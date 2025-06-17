#!/usr/bin/env python3
"""
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


T = TypeVar('T')  # 泛型类型参数


class TimeWheel(Generic[T]):
    """
    一个泛型的时间轮数据结构，用于高效地调度和触发基于时间的事件。
    """
    def __init__(self, size: int):
        if size <= 0:
            raise ValueError("Time wheel size must be positive.")
        self.size = size
        self.slots: List[List[T]] = [[] for _ in range(size)]
        self.offset = 0

    def schedule(self, event: T, delay: int):
        """
        在相对于当前时间 `delay` 个单位后安排一个事件。

        Args:
            event: 要安排的事件。
            delay: 从现在开始的时间单位数。必须为非负数。
        """
        if delay < 0:
            raise ValueError("Delay must be non-negative.")

        index = (self.offset + delay) % self.size
        self.slots[index].append(event)

    def _is_current_slot_empty(self) -> bool:
        """检查当前时间槽是否为空。"""
        return not self.slots[self.offset]

    def pop_due_event(self) -> Optional[T]:
        """
        从当前时间槽中弹出一个到期的事件。

        Returns:
            如果当前时间槽有事件，则返回一个事件；否则返回 None。
        """
        if not self._is_current_slot_empty():
            return self.slots[self.offset].pop(0)
        return None

    def _tick(self):
        """
        将时间向前推进一个单位。

        Raises:
            RuntimeError: 如果当前时间槽中仍有未处理的事件。
        """
        if not self._is_current_slot_empty():
            raise RuntimeError("Cannot advance time: current time slot is not empty.")
        self.offset = (self.offset + 1) % self.size

    def tick_till_next_event(self) -> int:
        """
        推进时间直到下一个有事件的槽位，或完成一个完整的循环。

        Returns:
            推进的时间单位数。
        """
        ticks = 0
        for _ in range(self.size):
            if not self._is_current_slot_empty():
                return ticks
            self._tick()
            ticks += 1
        return ticks

    def _get_buffer_at_offset(self, delay: int) -> List[T]:
        """
        获取相对于当前时间 `delay` 处的事件列表（缓冲区）。

        Args:
            delay: 从当前时间开始的偏移量。

        Returns:
            该时间点的事件列表。
        """
        if delay < 0:
            raise ValueError("Delay must be non-negative.")
        index = (self.offset + delay) % self.size
        return self.slots[index]

    def peek_upcoming_events(self, count: int, max_events: Optional[int] = None) -> List[T]:
        """
        预览未来 `count` 个时间单位内即将发生的事件，用于UI显示等。

        Args:
            count: 要检查的未来时间单位数。
            max_events: 最多返回的事件数量。如果为 None，则返回所有找到的事件。

        Returns:
            一个扁平化的事件列表。
        """
        events = []
        for i in range(count):
            events.extend(self._get_buffer_at_offset(i))
            if max_events is not None and len(events) >= max_events:
                return events[:max_events]
        return events


class _EventNode(Generic[T]):
    """用于在 IndexedTimeWheel 中存储事件的内部节点。"""
    def __init__(self, key: Any, value: T, scheduled_at: int):
        self.key = key
        self.value = value
        self.scheduled_at = scheduled_at # Absolute position in the time wheel

    def __repr__(self) -> str:
        return f"_EventNode(key={self.key}, value={self.value}, scheduled_at={self.scheduled_at})"


class IndexedTimeWheel(Generic[T]):
    """
    一个带索引的时间轮，允许通过唯一的键来跟踪、更新和移除事件。
    此类通过包含一个 TimeWheel 实例来实现功能。
    """
    def __init__(self, size: int):
        self.time_wheel = TimeWheel[_EventNode[T]](size)
        self.index: Dict[Any, _EventNode[T]] = {}

    def schedule(self, key: Any, value: T, delay: int):
        """
        安排一个带有关联键的事件。

        Args:
            key: 与事件关联的唯一键。
            value: 事件本身。
            delay: 从现在开始的延迟时间。

        Raises:
            ValueError: 如果键已存在或延迟为负。
        """
        if key in self.index:
            raise ValueError(f"Key '{key}' already exists in the time wheel.")
        if delay < 0:
            raise ValueError("Delay must be non-negative.")

        scheduled_at = (self.time_wheel.offset + delay) % self.time_wheel.size
        node = _EventNode(key, value, scheduled_at)

        self.time_wheel.schedule(node, delay)
        self.index[key] = node

    def pop_due_event(self) -> Optional[Tuple[Any, T]]:
        """
        从当前时间槽中弹出一个到期的事件及其键。

        Returns:
            一个包含（键，事件值）的元组，如果当前槽为空则返回 None。
        """
        due_node = self.time_wheel.pop_due_event()
        if due_node:
            # 在从索引中删除之前进行健全性检查
            if due_node.key in self.index:
                 del self.index[due_node.key]
            return due_node.key, due_node.value
        return None

    def tick_till_next_event(self) -> int:
        """推进时间直到下一个事件。"""
        return self.time_wheel.tick_till_next_event()

    def peek_upcoming_events(self, count: int, max_events: Optional[int] = None) -> List[Tuple[Any, T]]:
        """预览即将发生的事件。"""
        nodes = self.time_wheel.peek_upcoming_events(count, max_events)
        return [(node.key, node.value) for node in nodes]

    def remove(self, key: Any) -> Optional[T]:
        """
        通过键移除一个已安排的事件。

        Args:
            key: 要移除的事件的键。

        Returns:
            如果找到并移除了事件，则返回事件的值，否则返回 None。
        """
        if key not in self.index:
            return None

        node_to_remove = self.index[key]

        # 计算节点应该在的相对延迟
        delay = (node_to_remove.scheduled_at - self.time_wheel.offset + self.time_wheel.size) % self.time_wheel.size

        # 获取对应的缓冲区并尝试移除
        buffer = self.time_wheel._get_buffer_at_offset(delay)

        try:
            buffer.remove(node_to_remove)
            del self.index[key]
            return node_to_remove.value
        except ValueError:
            # 如果事件不在预期的缓冲区中，这可能表示状态不一致。
            # 在这种情况下，我们清理索引并返回None。
            del self.index[key]
            return None

    def get(self, key: Any) -> Optional[T]:
        """
        通过键获取一个已安排的事件的值。
        """
        node = self.index.get(key)
        return node.value if node else None

    def __contains__(self, key: Any) -> bool:
        """检查一个键是否存在于时间轮中。"""
        return key in self.index

    def __len__(self) -> int:
        """返回已安排的事件总数。"""
        return len(self.index)