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

最后更新: 2024-12-17 - 采用buffer设计思路
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any, Callable, Tuple
from collections import defaultdict
from threading import Lock


T = TypeVar('T')  # 泛型类型参数


class _EventNode(Generic[T]):
    """用于在 IndexedTimeWheel 中存储事件的双向链表节点。"""
    def __init__(self, key: Any, value: T, slot_index: int):
        self.key = key
        self.value = value
        self.slot_index = slot_index  # 存储预定槽位的绝对索引
        self.prev: Optional['_EventNode[T]'] = None
        self.next: Optional['_EventNode[T]'] = None

    def __repr__(self) -> str:
        return f"_EventNode(key={self.key}, value={self.value})"


class TimeWheel(Generic[T]):
    """
    一个泛型的时间轮数据结构，内部为每个槽位使用双向链表以实现 O(1) 的添加/弹出/删除。
    泛型类型 T 应为 _EventNode 或具有 prev/next 指针的类似结构。
    """
    def __init__(self, buffer_size: int):
        if buffer_size <= 0:
            raise ValueError("Time wheel size must be positive.")
        self.buffer_size = buffer_size
        # 每个槽位存储一个 (head, tail) 元组，代表一个双向链表
        self.slots: List[Tuple[Optional[T], Optional[T]]] = [(None, None) for _ in range(buffer_size)]
        self.offset = 0  # 当前在环形数组中的指针位置
        self.total_ticks = 0 # 从开始到现在的总节拍数

    def _schedule(self, event_node: T, target_index: int):
        """将事件节点插入到指定的目标索引槽位中。"""
        head, tail = self.slots[target_index]

        if tail is None:  # 链表为空
            self.slots[target_index] = (event_node, event_node)
        else:  # 追加到链表末尾
            tail.next = event_node
            event_node.prev = tail
            self.slots[target_index] = (head, event_node)

    def schedule_with_delay(self, event_node: T, delay: int):
        """在相对延迟后安排一个事件节点。延迟必须小于时间轮的大小。"""
        if delay < 0:
            raise ValueError("Delay must be non-negative.")
        if delay >= self.buffer_size:
            raise ValueError(f"Delay ({delay}) must be less than the time wheel size ({self.buffer_size}).")

        target_index = (self.offset + delay) % self.buffer_size
        event_node.slot_index = target_index
        self._schedule(event_node, target_index)

    def schedule_at_absolute_hour(self, event_node: T, absolute_hour: int):
        """在指定的绝对时间点安排一个事件节点。时间点不能在过去，也不能超过一个完整的轮次。"""
        if absolute_hour < self.total_ticks:
            raise ValueError(f"Cannot schedule in the past. Absolute hour ({absolute_hour}) "
                             f"is less than current time ({self.total_ticks}).")
        if absolute_hour >= self.total_ticks + self.buffer_size:
            raise ValueError(f"Cannot schedule at absolute_hour ({absolute_hour}) more than one wheel cycle "
                             f"(current_time={self.total_ticks}, size={self.buffer_size}) in the future.")

        delay = absolute_hour - self.total_ticks
        target_index = (self.offset + delay) % self.buffer_size

        event_node.slot_index = target_index
        self._schedule(event_node, target_index)

    def _is_current_slot_empty(self) -> bool:
        """检查当前时间槽是否为空。"""
        return self.slots[self.offset][0] is None

    def pop_due_event(self) -> Optional[T]:
        """从当前时间槽的头部弹出一个到期的事件。"""
        head, tail = self.slots[self.offset]
        if head is None:
            return None

        node_to_pop = head
        new_head = head.next

        if new_head is None:  # 链表变为空
            self.slots[self.offset] = (None, None)
        else:
            new_head.prev = None
            self.slots[self.offset] = (new_head, tail)

        # 清理弹出节点的指针
        node_to_pop.next = None
        node_to_pop.prev = None

        return node_to_pop

    def _tick(self):
        """将时间向前推进一个单位。"""
        if not self._is_current_slot_empty():
            raise RuntimeError("Cannot advance time: current time slot is not empty.")
        self.total_ticks += 1
        self.offset = self.total_ticks % self.buffer_size

    def tick_till_next_event(self) -> int:
        """推进时间直到下一个有事件的槽位。"""
        ticks = 0
        for _ in range(self.buffer_size):
            if not self._is_current_slot_empty():
                return ticks
            self._tick()
            ticks += 1
        return ticks

    def _get_buffer_at_offset(self, delay: int) -> List[T]:
        """通过遍历链表，获取相对延迟处的事件列表。"""
        if delay < 0:
            raise ValueError("Delay must be non-negative.")
        index = (self.offset + delay) % self.buffer_size

        events = []
        current_node, _ = self.slots[index]
        while current_node:
            events.append(current_node)
            current_node = current_node.next
        return events

    def peek_upcoming_events(self, count: int, max_events: Optional[int] = None) -> List[T]:
        """预览即将发生的事件。"""
        events = []
        for i in range(count):
            events.extend(self._get_buffer_at_offset(i))
            if max_events is not None and len(events) >= max_events:
                return events[:max_events]
        return events


class IndexedTimeWheel(Generic[T]):
    """
    带索引的时间轮，允许通过唯一的键以 O(1) 的时间复杂度来跟踪和移除事件。
    """
    def __init__(self, size: int):
        self.time_wheel = TimeWheel[_EventNode[T]](size)

        # TODO: make index one to multiple events.
        self.index: Dict[Any, _EventNode[T]] = {}
        self._lock = Lock()

    def _get_current_absolute_hour(self):
        """这是一个简化的示例，现实中可能需要更复杂的逻辑来跟踪总轮数。"""
        return self.time_wheel.total_ticks

    def schedule_with_delay(self, key: Any, value: T, delay: int):
        """在相对延迟后安排一个带有关联键的事件。"""
        with self._lock:
            if key in self.index:
                raise ValueError(f"Key '{key}' already exists in the time wheel.")
            # 基础时间轮会进行验证，但在这里也进行一次检查可以更快地失败
            if delay < 0:
                raise ValueError("Delay must be non-negative.")
            if delay >= self.time_wheel.buffer_size:
                raise ValueError(f"Delay ({delay}) must be less than the time wheel size ({self.time_wheel.buffer_size}).")

            # _EventNode需要知道它将被插入哪个槽位索引
            slot_index = (self.time_wheel.offset + delay) % self.time_wheel.buffer_size
            node = _EventNode(key, value, slot_index)

            self.time_wheel.schedule_with_delay(node, delay)
            self.index[key] = node
            # TODO: 数据改变后通知UI重新渲染

    def schedule_at_absolute_hour(self, key: Any, value: T, absolute_hour: int):
        """在指定的绝对时间点安排一个带有关联键的事件。"""
        with self._lock:
            if key in self.index:
                raise ValueError(f"Key '{key}' already exists in the time wheel.")

            # 基础时间轮会进行验证，我们在这里仅计算索引以创建节点
            # 验证: 不能在过去安排
            if absolute_hour < self.time_wheel.total_ticks:
                raise ValueError(f"Cannot schedule in the past. Absolute hour ({absolute_hour}) "
                                 f"is less than current time ({self.time_wheel.total_ticks}).")
            # 验证: 不能安排超过一个轮次
            if absolute_hour >= self.time_wheel.total_ticks + self.time_wheel.buffer_size:
                raise ValueError(f"Cannot schedule at absolute_hour ({absolute_hour}) more than one wheel cycle.")

            delay = absolute_hour - self.time_wheel.total_ticks
            slot_index = (self.time_wheel.offset + delay) % self.time_wheel.buffer_size
            node = _EventNode(key, value, slot_index)

            self.time_wheel.schedule_at_absolute_hour(node, absolute_hour)
            self.index[key] = node
            # TODO: 数据改变后通知UI重新渲染

    def pop_due_event(self) -> Optional[Tuple[Any, T]]:
        """从当前时间槽中弹出一个到期的事件及其键。"""
        with self._lock:
            due_node = self.time_wheel.pop_due_event()
            if due_node:
                if due_node.key in self.index:
                     del self.index[due_node.key]
                # TODO: 数据改变后通知UI重新渲染
                return due_node.key, due_node.value
            return None

    def tick_till_next_event(self) -> int:
        """推进时间直到下一个事件。"""
        with self._lock:
            ticks = self.time_wheel.tick_till_next_event()
            if ticks > 0:
                # TODO: 时间推进，数据已改变，通知UI重新渲染
                pass
            return ticks

    def peek_upcoming_events(self, count: int, max_events: Optional[int] = None) -> List[Tuple[Any, T]]:
        """预览即将发生的事件。"""
        with self._lock:
            nodes = self.time_wheel.peek_upcoming_events(count, max_events)
            return [(node.key, node.value) for node in nodes]

    def remove(self, key: Any) -> Optional[T]:
        """通过键以 O(1) 时间复杂度移除一个已安排的事件。"""
        with self._lock:
            if key not in self.index:
                return None

            node_to_remove = self.index[key]

            # O(1) 链表移除
            prev_node = node_to_remove.prev
            next_node = node_to_remove.next

            if prev_node:
                prev_node.next = next_node
            if next_node:
                next_node.prev = prev_node

            # 更新 TimeWheel 槽位中的 head/tail 指针
            index = node_to_remove.slot_index
            head, tail = self.time_wheel.slots[index]

            new_head, new_tail = head, tail

            if node_to_remove == head:
                new_head = next_node
            if node_to_remove == tail:
                new_tail = prev_node

            self.time_wheel.slots[index] = (new_head, new_tail)

            del self.index[key]

            # 清理移除节点的指针
            node_to_remove.prev = None
            node_to_remove.next = None

            # TODO: 数据改变后通知UI重新渲染
            return node_to_remove.value

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