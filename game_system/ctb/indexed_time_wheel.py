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
import copy


T = TypeVar('T')  # 泛型类型参数


class _EventNode(Generic[T]):
    """用于在 IndexedTimeWheel 中存储事件。"""
    def __init__(self, key: Any, value: T, slot_index: int, absolute_hour: Optional[int] = None):
        self.key = key
        self.value = value
        # 当 slot_index == -1 时，表示事件在 future_events 列表中
        self.slot_index = slot_index
        self.absolute_hour = absolute_hour

    def __repr__(self) -> str:
        return f"_EventNode(key={self.key}, value={self.value})"


class IndexedTimeWheel(Generic[T]):
    """
    一个带索引和远期事件支持的泛型时间轮数据结构。
    内部为每个槽位使用双向链表以实现 O(1) 的添加/弹出/删除。
    通过唯一的键以 O(1) 的时间复杂度来跟踪和移除事件。
    """
    def __init__(self, buffer_size: int):
        assert buffer_size > 0, "Time wheel size must be positive."
        self.buffer_size = buffer_size
        # 核心环形缓冲区 - 每个槽位存储事件列表
        self.slots: List[List[_EventNode[T]]] = [[] for _ in range(self.buffer_size)]
        self.offset = 0
        self.total_ticks = 0

        # 索引和远期事件
        self.index: Dict[Any, _EventNode[T]] = {}
        self.future_events = []
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
                self._insert_future_event(absolute_hour, node)
                self.index[key] = node
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
        self.slots[target_index].append(event_node)

    def _insert_future_event(self, absolute_hour: int, node: _EventNode[T]):
        """将远期事件插入到列表中，从后往前找到正确位置直接插入。"""
        # 从后往前找到插入位置
        insert_index = len(self.future_events)
        for i in range(len(self.future_events) - 1, -1, -1):
            if self.future_events[i][0] <= absolute_hour:
                insert_index = i + 1
                break
            insert_index = i

        # 在正确位置插入
        self.future_events.insert(insert_index, (absolute_hour, node))

    def _is_current_slot_empty(self) -> bool:
        """检查当前时间槽是否为空。"""
        return not self.slots[self.offset]

    def pop_due_event(self) -> Optional[Tuple[Any, T]]:
        """从当前时间槽的头部弹出一个到期的事件。"""
        with self._lock:
            if not self.slots[self.offset]:
                return None

            node_to_pop = self.slots[self.offset][0]
            self.slots[self.offset] = self.slots[self.offset][1:]

            if node_to_pop.key in self.index:
                del self.index[node_to_pop.key]

            # TODO: 数据改变后通知UI重新渲染
            return node_to_pop.key, node_to_pop.value

    def _tick(self):
        """推进时间轮一小时，并移动接近的远期事件到主轮。"""
        self.total_ticks += 1
        self.offset = self.total_ticks % self.buffer_size

        # 检查是否有远期事件需要移动到主轮
        # 由于列表已按absolute_hour排序，只需要检查第一个元素
        while self.future_events and self.future_events[0][0] <= self.total_ticks:
            absolute_hour, node = self.future_events.pop(0)

            # 将到期的远期事件插入时间轮的最远端槽位 (offset-1)
            # 这样事件会在时间轮中正确的时间点被触发
            target_index = (self.offset - 1) % self.buffer_size
            node.slot_index = target_index
            self._schedule(node, target_index)

        assert not self.future_events or self.future_events[0][0] > self.total_ticks

    def advance_to_next_event(self) -> int:
        """
        [核心逻辑] 推进时间直到下一个有事件的槽位。
        这是游戏循环的主要驱动方法。

        Raises:
            RuntimeError: 如果遍历一整圈后仍未找到任何事件。

        Returns:
            int: 时间推进的小时数。
        """
        with self._lock:
            ticks = 0
            # 最多检查 buffer_size 次，防止无限循环
            for _ in range(self.buffer_size):
                if not self._is_current_slot_empty():
                    # TODO: 时间推进，数据已改变，通知UI重新渲染
                    return ticks
                self._tick()
                ticks += 1

            # TODO: 这种情况可能意味着所有剩余的事件都在远期事件堆中，
            # 且它们的触发时间超出了当前时间轮的一整圈。
            # 未来的版本需要更完善的逻辑来处理这种情况, 但目前，这被视为一个异常状态。
            raise RuntimeError("advance_to_next_event completed a full cycle without finding any event in the wheel.")

    def remove(self, key: Any) -> Optional[T]:
        """从时间轮或远期事件列表中移除一个事件。"""
        with self._lock:
            if key not in self.index:
                return None

            node_to_remove = self.index[key]

            # case 1: 事件在远期池中, 直接从列表中删除
            if node_to_remove.slot_index == -1:
                # 从远期事件列表中删除
                for i, (_, node) in enumerate(self.future_events):
                    if node.key == key:
                        self.future_events.pop(i)
                        break
            # case 2: 事件在时间轮中, O(1) 链表移除
            else:
                self.slots[node_to_remove.slot_index] = [node for node in self.slots[node_to_remove.slot_index] if node.key != key]

            del self.index[key]
            # TODO: 数据改变后通知UI重新渲染
            return node_to_remove.value

    # TODO 最极端情况下从future_event中读取事件。
    def peek_upcoming_events(self, count: int, max_events: Optional[int] = None) -> List[Tuple[Any, T]]:
        """
        [仅供UI渲染使用] 预览接下来`count`个小时内即将发生的事件。

        重要提示: 此方法为UI显示或调试而设计, 不应用于核心游戏循环逻辑。
        它可能会为了UI的便利而返回不精确或不完整的事件数据。
        游戏循环应使用 advance_to_next_event() 和 pop_due_event()。

        Args:
            count: 要预览的小时数。
            max_events: 最多返回的事件数量。

        Returns:
            一个元组列表，每个元组包含(key, value)。
        """
        with self._lock:
            events = []
            for i in range(count):
                index = (self.offset + i) % self.buffer_size
                current_nodes = self.slots[index]
                for node in current_nodes:
                    events.append((node.key, node.value))

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

    # TODO confirm the copy&delete is not effecting the original list
    def deepcopy(self) -> 'IndexedTimeWheel[T]':
        """创建当前时间轮的深拷贝，用于技能效果预测。"""
        with self._lock:
            new_wheel = IndexedTimeWheel[T](self.buffer_size)
            new_wheel.offset = self.offset
            new_wheel.total_ticks = self.total_ticks

            # 深拷贝slots
            for i, slot in enumerate(self.slots):
                new_wheel.slots[i] = [copy.deepcopy(node) for node in slot]

            # 深拷贝future_events
            new_wheel.future_events = [(hour, copy.deepcopy(node)) for hour, node in self.future_events]

            # 重建index
            new_wheel.index = {}
            for slot in new_wheel.slots:
                for node in slot:
                    new_wheel.index[node.key] = node
            for _, node in new_wheel.future_events:
                new_wheel.index[node.key] = node

            return new_wheel

    def delay_key(self, key: Any, delay_hours: int) -> bool:
        """
        延后指定key的事件N小时。只能在拷贝的时间轮上使用。

        Args:
            key: 要延后的事件key
            delay_hours: 延后的小时数（必须为正数）

        Returns:
            bool: 是否成功延后
        """
        with self._lock:
            if key not in self.index:
                return False
            if delay_hours <= 0:
                return False

            node = self.index[key]
            old_absolute_hour = node.absolute_hour
            new_absolute_hour = old_absolute_hour + delay_hours

            # 从原位置移除
            if node.slot_index == -1:
                # 在future_events中
                for i, (hour, future_node) in enumerate(self.future_events):
                    if future_node.key == key:
                        self.future_events.pop(i)
                        break
            else:
                # 在时间轮中
                self.slots[node.slot_index] = [n for n in self.slots[node.slot_index] if n.key != key]

            # 重新调度到新位置
            node.absolute_hour = new_absolute_hour
            delay = new_absolute_hour - self.total_ticks

            if delay >= self.buffer_size:
                # 重新放入future_events
                node.slot_index = -1
                self._insert_future_event(new_absolute_hour, node)
            else:
                # 重新放入时间轮
                target_index = (self.offset + delay) % self.buffer_size
                node.slot_index = target_index
                self._schedule(node, target_index)

            return True