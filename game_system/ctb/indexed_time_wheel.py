#!/usr/bin/env python3
"""
这个文件的接口是人工决定,已经finalize,没有明确指示绝不可以更改.

时间轮数据结构 - 用于CTB系统的事件调度

核心设计:
- 环形缓冲区: 使用固定大小的数组实现高效的时间窗口
- 链表槽位: 每个时间槽使用链表存储同时触发的事件
- 动态偏移: offset指针指向当前时间槽（buffer设计）
- 泛型支持: 可存储任意类型的事件对象

Buffer设计说明:
- offset指向的槽位是"当前回合的行动buffer"
- 该槽位中的所有事件应该立即执行
- 执行完当前槽位的所有事件后，时间才会推进
- 游戏开始的第一回合，时间轮完全没有转动过
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any, Callable, Tuple
from collections import defaultdict
from threading import Lock
import heapq


T = TypeVar('T')  # 泛型类型参数


class _EventNode(Generic[T]):
    """用于在 IndexedTimeWheel 中存储事件的双向链表节点。"""
    def __init__(self, key: Any, value: T, slot_index: int, absolute_hour: Optional[int] = None):
        self.key = key
        self.value = value
        # 当 slot_index == -1 时，表示事件在 future_events 堆中
        self.slot_index = slot_index
        self.absolute_hour = absolute_hour
        self.deleted = False
        self.prev: Optional['_EventNode[T]'] = None
        self.next: Optional['_EventNode[T]'] = None

    def __repr__(self) -> str:
        return f"_EventNode(key={self.key}, value={self.value})"


class MinHeap(Generic[T]):
    """一个显式的最小堆实现，用于存储远期事件。"""
    def __init__(self):
        self._heap: List[Tuple[int, int, _EventNode[T]]] = []

    def push(self, absolute_hour: int, seq: int, node: _EventNode[T]):
        """将一个事件节点推入堆中。"""
        heapq.heappush(self._heap, (absolute_hour, seq, node))

    def pop(self) -> Tuple[int, int, _EventNode[T]]:
        """从堆中弹出并返回最小的事件节点。"""
        return heapq.heappop(self._heap)

    def peek(self) -> Optional[Tuple[int, int, _EventNode[T]]]:
        """查看堆顶的最小事件节点，不弹出。"""
        return self._heap[0] if self._heap else None

    def __len__(self) -> int:
        return len(self._heap)


class IndexedTimeWheel(Generic[T]):
    """
    一个带索引和远期事件支持的泛型时间轮数据结构。
    内部为每个槽位使用双向链表以实现 O(1) 的添加/弹出/删除。
    通过唯一的键以 O(1) 的时间复杂度来跟踪和移除事件。
    """
    def __init__(self, buffer_size: int):
        assert buffer_size > 0, "Time wheel size must be positive."
        self.buffer_size = buffer_size
        # 核心环形缓冲区
        self.slots: List[Tuple[Optional[_EventNode[T]], Optional[_EventNode[T]]]] = [(None, None) for _ in range(self.buffer_size)]
        self.offset = 0
        self.total_ticks = 0

        # 索引和远期事件
        self.index: Dict[Any, _EventNode[T]] = {}
        self.future_events = MinHeap[_EventNode[T]]()
        self._seq = 0
        self._lock = Lock()


    def schedule_with_delay(self, key: Any, value: T, delay: int):
        """在相对延迟后安排一个带有关联键的事件。这是核心调度方法。"""
        with self._lock:
            assert key not in self.index, f"Key '{key}' already exists."
            assert delay >= 0, "Delay must be non-negative."

            # 如果延迟超出了当前轮次，则放入远期事件池
            if delay >= self.buffer_size:
                absolute_hour = self.total_ticks + delay
                # slot_index = -1 表示在远期池中
                node = _EventNode(key, value, slot_index=-1, absolute_hour=absolute_hour)
                self.future_events.push(absolute_hour, self._seq, node)
                self.index[key] = node
                self._seq += 1
            else:
                # 正常调度到时间轮
                target_index = (self.offset + delay) % self.buffer_size
                absolute_hour = self.total_ticks + delay
                node = _EventNode(key, value, target_index, absolute_hour=absolute_hour)
                self._schedule(node, target_index)
                self.index[key] = node

            # TODO: 数据改变后通知UI重新渲染

    def schedule_at_absolute_hour(self, key: Any, value: T, absolute_hour: int):
        """在指定的绝对时间点安排一个带有关联键的事件 (便利封装)。"""
        assert absolute_hour >= self.total_ticks, "Cannot schedule in the past."

        delay = absolute_hour - self.total_ticks
        self.schedule_with_delay(key, value, delay)

    def _schedule(self, event_node: _EventNode[T], target_index: int):
        """将事件节点插入到指定的目标索引槽位中。"""
        head, tail = self.slots[target_index]
        if tail is None:
            self.slots[target_index] = (event_node, event_node)
        else:
            tail.next = event_node
            event_node.prev = tail
            self.slots[target_index] = (head, event_node)

    def _is_current_slot_empty(self) -> bool:
        """检查当前时间槽是否为空。"""
        return self.slots[self.offset][0] is None

    def pop_due_event(self) -> Optional[Tuple[Any, T]]:
        """从当前时间槽的头部弹出一个到期的事件。"""
        with self._lock:
            head, tail = self.slots[self.offset]
            if head is None:
                return None

            node_to_pop = head
            new_head = head.next

            if new_head is None:
                self.slots[self.offset] = (None, None)
            else:
                new_head.prev = None
                self.slots[self.offset] = (new_head, tail)

            # 清理弹出节点的指针
            node_to_pop.next = None
            node_to_pop.prev = None

            if node_to_pop.key in self.index:
                del self.index[node_to_pop.key]

            # TODO: 数据改变后通知UI重新渲染
            return node_to_pop.key, node_to_pop.value

    def _tick(self):
        """(私有) 将时间向前推进一个单位，并处理到期的远期事件。"""
        assert self._is_current_slot_empty(), "Cannot advance time: current time slot is not empty."

        self.total_ticks += 1
        self.offset = self.total_ticks % self.buffer_size

        # 检查并处理所有在当前时间点到期的远期事件
        while self.future_events and self.future_events.peek()[0] == self.total_ticks:
            absolute_hour, seq, node = self.future_events.pop()

            if node.deleted:
                # key 已经在 remove() 时从 index 中删除
                continue

            # 将到期的远期事件插入主时间轮的当前槽位 (delay=0)
            node.slot_index = self.offset
            self._schedule(node, self.offset)

        assert not self.future_events or self.future_events.peek()[0] > self.total_ticks

    def tick_till_next_event(self) -> int:
        """推进时间直到下一个有事件的槽位。"""
        with self._lock:
            ticks = 0
            # 最多检查 buffer_size 次，防止无限循环
            for _ in range(self.buffer_size):
                if not self._is_current_slot_empty():
                    # TODO: 时间推进，数据已改变，通知UI重新渲染
                    return ticks
                self._tick()
                ticks += 1
            # TODO: 时间推进，数据已改变，通知UI重新渲染
            return ticks

    def remove(self, key: Any) -> Optional[T]:
        """通过键以 O(1) 时间复杂度移除一个已安排的事件。"""
        with self._lock:
            if key not in self.index:
                return None

            node_to_remove = self.index[key]

            # case 1: 事件在远期池中, 懒惰删除
            if node_to_remove.slot_index == -1:
                node_to_remove.deleted = True
            # case 2: 事件在时间轮中, O(1) 链表移除
            else:
                prev_node = node_to_remove.prev
                next_node = node_to_remove.next

                if prev_node:
                    prev_node.next = next_node
                if next_node:
                    next_node.prev = prev_node

                index = node_to_remove.slot_index
                head, tail = self.slots[index]
                new_head, new_tail = head, tail

                if node_to_remove == head:
                    new_head = next_node
                if node_to_remove == tail:
                    new_tail = prev_node

                self.slots[index] = (new_head, new_tail)

                node_to_remove.prev = None
                node_to_remove.next = None

            del self.index[key]
            # TODO: 数据改变后通知UI重新渲染
            return node_to_remove.value

    def peek_upcoming_events(self, count: int, max_events: Optional[int] = None) -> List[Tuple[Any, T]]:
        """预览即将发生在主时间轮内的事件 (不包括远期事件)。"""
        with self._lock:
            events = []
            for i in range(count):
                index = (self.offset + i) % self.buffer_size
                current_node, _ = self.slots[index]
                while current_node:
                    # 在主轮中不应该遇到已删除的节点，这是一个内部逻辑错误
                    assert not current_node.deleted, "Bug: Found a deleted node in the main wheel."
                    events.append((current_node.key, current_node.value))
                    current_node = current_node.next

                if max_events is not None and len(events) >= max_events:
                    return events[:max_events]
            return events

    def get(self, key: Any) -> Optional[T]:
        """通过键获取一个已安排的事件的值。"""
        with self._lock:
            node = self.index.get(key)
            return node.value if node else None

    def __contains__(self, key: Any) -> bool:
        """检查一个键是否存在于时间轮中。"""
        with self._lock:
            return key in self.index

    def __len__(self) -> int:
        """返回已安排的事件总数。"""
        with self._lock:
            return len(self.index)