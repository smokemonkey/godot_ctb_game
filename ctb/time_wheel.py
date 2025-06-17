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

from typing import TypeVar, Generic, List, Optional, Dict, Any, Callable
from collections import defaultdict


T = TypeVar('T')  # 泛型类型参数


class TimeWheel(Generic[T]):
    """
    通用时间轮数据结构

    使用环形缓冲区实现的事件调度器，支持高效的时间窗口管理。

    Attributes:
        size: 时间轮的槽位数量
        offset: 当前时间槽位的偏移量（buffer设计）
        slots: 存储事件的槽位数组
    """

    def __init__(self, size: int):
        """
        初始化时间轮

        Args:
            size: 时间轮的大小（槽位数量）

        Raises:
            ValueError: 如果size <= 0
        """
        if size <= 0:
            raise ValueError("时间轮大小必须为正数")

        self.size = size
        self.offset = 0  # 指向当前时间槽（buffer）
        self.slots: List[List[T]] = [[] for _ in range(size)]

    def add(self, event: T, delay: int) -> bool:
        """
        添加事件到时间轮

        Args:
            event: 要添加的事件
            delay: 延迟时间（0表示当前槽位，立即执行）

        Returns:
            bool: 如果成功添加返回True，如果延迟超出范围返回False
        """
        if delay < 0 or delay >= self.size:
            return False

        # Buffer设计：delay=0放入当前槽位（立即执行）
        slot_index = (self.offset + delay) % self.size
        self.slots[slot_index].append(event)
        return True

    def advance(self, hours: int = 1) -> List[List[T]]:
        """
        推进时间轮

        Args:
            hours: 要推进的时间单位数

        Returns:
            List[List[T]]: 每个时间单位触发的事件列表
        """
        triggered_events = []

        for _ in range(hours):
            # 获取当前槽位的事件（buffer）
            current_events = self.slots[self.offset]
            if current_events:
                triggered_events.append(current_events[:])
                self.slots[self.offset] = []  # 清空当前槽位
            else:
                triggered_events.append([])

            # 推进到下一个槽位
            self.offset = (self.offset + 1) % self.size

        return triggered_events

    def get_current_buffer(self) -> List[T]:
        """
        获取当前槽位的事件（不移除）

        Returns:
            List[T]: 当前槽位中的所有事件
        """
        return self.slots[self.offset][:]

    def clear_current_buffer(self) -> List[T]:
        """
        清空并返回当前槽位的事件

        Returns:
            List[T]: 被清空的事件列表
        """
        events = self.slots[self.offset][:]
        self.slots[self.offset] = []
        return events

    def peek(self, hours_ahead: int) -> List[T]:
        """
        查看未来某个时间点的事件（不移除）

        Args:
            hours_ahead: 要查看的未来时间点

        Returns:
            List[T]: 该时间点的事件列表
        """
        if hours_ahead < 0 or hours_ahead >= self.size:
            return []

        slot_index = (self.offset + hours_ahead) % self.size
        return self.slots[slot_index][:]

    def remove(self, event: T, hours_ahead: int) -> bool:
        """
        从指定时间槽移除事件

        Args:
            event: 要移除的事件
            hours_ahead: 事件所在的时间槽（相对于当前时间）

        Returns:
            bool: 如果成功移除返回True
        """
        if hours_ahead < 0 or hours_ahead >= self.size:
            return False

        slot_index = (self.offset + hours_ahead) % self.size
        try:
            self.slots[slot_index].remove(event)
            return True
        except ValueError:
            return False

    def get_next_event_delay(self) -> Optional[int]:
        """
        获取下一个事件的延迟时间

        Returns:
            Optional[int]: 如果有事件返回延迟时间，否则返回None
        """
        # Buffer设计：先检查当前槽位
        if self.slots[self.offset]:
            return 0

        # 检查后续槽位
        for i in range(1, self.size):
            slot_index = (self.offset + i) % self.size
            if self.slots[slot_index]:
                return i

        return None

    def total_events(self) -> int:
        """
        获取时间轮中的事件总数

        Returns:
            int: 所有槽位中的事件总数
        """
        return sum(len(slot) for slot in self.slots)

    def get_all_events(self) -> List[tuple[int, T]]:
        """
        获取所有事件及其触发时间

        Returns:
            List[tuple[int, T]]: (延迟时间, 事件) 的列表
        """
        events = []
        for i in range(self.size):
            slot_index = (self.offset + i) % self.size
            for event in self.slots[slot_index]:
                events.append((i, event))
        return events


class IndexedTimeWheel(TimeWheel[T]):
    """
    带索引的时间轮

    Attributes:
        index: 事件索引，key -> (delay, event)
        key_func: 从事件中提取键的函数
    """

    def __init__(self, size: int, key_func: Callable[[T], Any]):
        """
        初始化带索引的时间轮

        Args:
            size: 时间轮的大小
            key_func: 从事件中提取键的函数
        """
        super().__init__(size)
        self.index: Dict[Any, tuple[int, T]] = {}
        self.key_func = key_func

    def add(self, event: T, delay: int) -> bool:
        """
        添加事件到时间轮（带索引）

        Args:
            event: 要添加的事件
            delay: 延迟时间

        Returns:
            bool: 如果成功添加返回True
        """
        if not super().add(event, delay):
            return False

        # 更新索引
        key = self.key_func(event)
        self.index[key] = (delay, event)
        return True

    def remove_by_key(self, key: Any) -> bool:
        """
        通过键移除事件

        Args:
            key: 事件的键

        Returns:
            bool: 如果成功移除返回True
        """
        if key not in self.index:
            return False

        delay, event = self.index[key]

        # 计算当前的相对延迟
        # 需要考虑时间已经推进的情况
        current_delay = delay

        if self.remove(event, current_delay):
            del self.index[key]
            return True

        return False

    def get_by_key(self, key: Any) -> Optional[T]:
        """
        通过键获取事件

        Args:
            key: 事件的键

        Returns:
            Optional[T]: 如果找到返回事件，否则返回None
        """
        if key in self.index:
            _, event = self.index[key]
            return event
        return None

    def advance(self, hours: int = 1) -> List[List[T]]:
        """
        推进时间轮（需要更新索引）

        Args:
            hours: 要推进的时间单位数

        Returns:
            List[List[T]]: 每个时间单位触发的事件列表
        """
        triggered_events = super().advance(hours)

        # 更新索引中的延迟时间
        new_index = {}
        for key, (delay, event) in self.index.items():
            new_delay = delay - hours
            if new_delay >= 0:
                new_index[key] = (new_delay, event)

        self.index = new_index

        return triggered_events

    def clear_current_buffer(self) -> List[T]:
        """
        清空当前槽位并更新索引

        Returns:
            List[T]: 被清空的事件列表
        """
        events = super().clear_current_buffer()

        # 从索引中移除这些事件
        for event in events:
            key = self.key_func(event)
            if key in self.index:
                del self.index[key]

        return events