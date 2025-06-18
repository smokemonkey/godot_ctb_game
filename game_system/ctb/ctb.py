#!/usr/bin/env python3
"""
CTB (Conditional Turn-Based) 战斗系统核心模块

基于时间轮的事件调度系统，支持角色行动和各种游戏事件的精确时间管理。

核心特性:
- 事件驱动: 所有游戏行为都是事件，包括角色行动
- 时间轮调度: 使用环形缓冲区高效管理未来180天的事件
- 随机间隔: 角色行动间隔在1-180天之间随机分布
- 灵活扩展: 支持自定义事件类型和执行逻辑

Buffer设计:
- 时间轮的当前槽位作为"当前回合的行动buffer"
- 所有当前槽位的事件立即执行，无需额外维护执行列表
- 执行完当前槽位所有事件后，时间才会推进
"""

from typing import List, Optional, Dict, Any, Callable
from enum import Enum, auto
import random
from dataclasses import dataclass

# 导入时间系统
from ..calendar.calendar import Calendar, TimeUnit

# 导入时间轮
from ..indexed_time_wheel import IndexedTimeWheel


class EventType(Enum):
    """事件类型枚举"""
    CHARACTER_ACTION = auto()  # 角色行动
    SEASON_CHANGE = auto()     # 季节变化
    WEATHER_CHANGE = auto()    # 天气变化
    STORY_EVENT = auto()       # 剧情事件
    CUSTOM = auto()           # 自定义事件


class Event:
    """
    事件基类

    所有CTB系统中的事件都应继承此类。

    Attributes:
        id: 事件的唯一标识符
        name: 事件名称
        event_type: 事件类型
        trigger_time: 触发时间（绝对时间，小时）
        description: 事件描述
    """

    def __init__(self, id: str, name: str, event_type: EventType,
                 trigger_time: int, description: str = ""):
        self.id = id
        self.name = name
        self.event_type = event_type
        self.trigger_time = trigger_time
        self.description = description

    def execute(self) -> Any:
        """
        执行事件

       子类应重写此方法实现具体的事件逻辑。

        Returns:
            Any: 执行结果，具体类型由子类决定
        """
        raise NotImplementedError("子类必须实现execute方法")

    def __str__(self):
        return f"{self.name} ({self.event_type.name})"


class Character(Event):
    """
    游戏角色

    角色是一种特殊的事件，其execute方法执行角色的行动。

    Attributes:
        faction: 角色所属阵营
        is_active: 角色是否活跃（可以行动）
    """

    def __init__(self, id: str, name: str, faction: str = "中立"):
        super().__init__(
            id=id,
            name=name,
            event_type=EventType.CHARACTER_ACTION,
            trigger_time=0,
            description=f"{name}的行动"
        )
        self.faction = faction
        self.is_active = True

    def calculate_next_action_time(self, current_time: int) -> int:
        """
        计算下次行动时间

        使用三角分布生成1-180天之间的随机间隔，
        峰值在90天，产生更自然的分布。

        Args:
            current_time: 当前时间（小时）

        Returns:
            int: 下次行动的绝对时间（小时）
        """
        # 使用三角分布：最小1天，最大180天，众数90天
        days = random.triangular(1, 180, 90)
        hours = int(days * 24)
        return current_time + hours

    def execute(self) -> 'Character':
        """
        执行角色行动

        Returns:
            Character: 返回自身，便于链式调用
        """
        # 这里可以添加角色行动的具体逻辑
        # 例如：触发战斗、使用技能、移动等
        return self


class CTBManager:
    """
    CTB系统管理器

    负责管理所有事件的调度和执行。

    Attributes:
        calendar: 时间管理器
        time_wheel: 时间轮调度器
        characters: 角色字典
        is_initialized: 系统是否已初始化
        action_history: 行动历史记录
    """

    # 时间轮大小：180天 * 24小时
    TIME_WHEEL_SIZE = 180 * 24

    def __init__(self, calendar: Calendar, time_wheel_size: int = TIME_WHEEL_SIZE):
        """
        初始化CTB管理器

        Args:
            calendar: 游戏时间管理器（Calendar实例）
        """
        self.calendar = calendar
        self.TIME_WHEEL_SIZE = time_wheel_size
        self.time_wheel = IndexedTimeWheel[Event](
            self.TIME_WHEEL_SIZE,
            get_time_callback=lambda: self.calendar.get_timestamp()
        )
        self.characters: Dict[str, Character] = {}
        self.is_initialized = False
        self.action_history: List[Dict[str, Any]] = []

        # 事件执行回调
        self.on_event_executed: Optional[Callable[[Event], None]] = None

    def add_character(self, character: Character) -> None:
        """
        添加角色到系统

        Args:
            character: 要添加的角色

        Raises:
            ValueError: 如果角色ID已存在
        """
        if character.id in self.characters:
            raise ValueError(f"Character with ID {character.id} already exists")

        self.characters[character.id] = character

    def remove_character(self, character_id: str) -> bool:
        """
        从系统中移除角色

        Args:
            character_id: 要移除的角色ID

        Returns:
            bool: 如果成功移除返回True，否则返回False
        """
        if character_id not in self.characters:
            return False

        # 从时间轮中移除角色的事件
        self.time_wheel.remove(character_id)

        # 从角色字典中移除
        del self.characters[character_id]
        return True

    def get_character(self, character_id: str) -> Optional[Character]:
        """
        获取角色

        Args:
            character_id: 角色ID

        Returns:
            Optional[Character]: 如果找到返回角色，否则返回None
        """
        return self.characters.get(character_id)

    def initialize_ctb(self) -> None:
        """
        初始化CTB系统

        为所有角色安排初始行动时间。

        Raises:
            ValueError: 如果没有角色
        """
        if not self.characters:
            raise ValueError("Cannot initialize CTB without characters")

        current_time = self.calendar.get_timestamp()

        # 为每个活跃角色安排初始行动
        for character in self.characters.values():
            if character.is_active:
                # 计算初始行动时间
                next_time = character.calculate_next_action_time(current_time)
                character.trigger_time = next_time

                # 添加到时间轮
                delay = next_time - current_time
                self.time_wheel.schedule_with_delay(character.id, character, delay)

        self.is_initialized = True

    def register_event(self, event: Event, trigger_time: int) -> bool:
        """
        注册自定义事件

        Args:
            event: 要注册的事件
            trigger_time: 触发时间（绝对时间）

        Returns:
            bool: 如果成功注册返回True，否则返回False
        """
        current_time = self.calendar.get_timestamp()
        if trigger_time < current_time:
            return False  # 不能在过去注册事件

        delay = trigger_time - current_time
        try:
            self.time_wheel.schedule_with_delay(event.id, event, delay)
            return True
        except (ValueError, AssertionError):
            # 例如，如果事件ID已经存在
            return False

    def execute_next_action(self) -> List[Event]:
        """
        推进时间直到下一个事件发生，并执行该时间点的所有事件。

        此方法是游戏主循环的核心驱动力。它会高效地跳过空闲时间。

        Returns:
            List[Event]: 在当前时间点执行的所有事件的列表。如果没有更多事件，则返回空列表。
        """
        # 1. 推进时间轮和游戏时间到下一个有事件的时间点
        ticks_advanced = self.time_wheel.advance_to_next_event()

        # 如果advance_to_next_event跑完一整圈都没找到事件，说明没有事件了
        if ticks_advanced >= self.time_wheel.buffer_size and self.time_wheel.pop_due_event() is None:
            return []

        # 2. 与游戏时间同步
        if ticks_advanced > 0:
            self.calendar.advance_time(ticks_advanced, TimeUnit.HOUR)

        # 3. 获取并执行当前时间槽的所有事件
        processed_events: List[Event] = []
        while True:
            event_tuple = self.time_wheel.pop_due_event()
            if event_tuple is None:
                break

            _key, event = event_tuple
            processed_events.append(event)

            # 执行事件并记录历史
            self._execute_event(event)

        # 4. 如果处理了事件，推进时间 (一个象征性的tick，防止无限循环)
        if processed_events:
            self.calendar.advance_time(1, TimeUnit.HOUR)

        return processed_events

    def _execute_event(self, event: Event) -> None:
        """
        执行单个事件，并处理后续逻辑（如重新调度）。
        """
        result = event.execute()
        self._record_action(event)

        if self.on_event_executed:
            self.on_event_executed(event)

        # 如果是角色行动，计算并安排下一次行动
        if event.event_type == EventType.CHARACTER_ACTION and isinstance(event, Character):
            character = event
            if character.is_active:
                current_time = self.calendar.get_timestamp()
                next_time = character.calculate_next_action_time(current_time)
                character.trigger_time = next_time
                delay = next_time - current_time
                self.time_wheel.schedule_with_delay(character.id, character, delay)

    def _record_action(self, event: Event) -> None:
        """
        记录行动历史

        Args:
            event: 执行的事件
        """
        record = {
            'event_name': event.name,
            'event_type': event.event_type.name,
            'timestamp': self.calendar.get_timestamp(),
            'gregorian_year': self.calendar.current_gregorian_year,
            'month': self.calendar.current_month,
            'day': self.calendar.current_day_in_month,
            'hour_in_day': self.calendar.current_hour_in_day
        }
        self.action_history.append(record)

    def set_character_active(self, character_id: str, active: bool) -> bool:
        """
        设置角色的活跃状态

        如果一个角色被设置为不活跃，它将不会被安排下一次行动。
        如果它当前被安排了行动，该行动会被取消。
        """
        character = self.get_character(character_id)
        if not character:
            return False

        character.is_active = active

        # 如果角色被设置为不活跃，从时间轮中移除其未来的行动
        if not active:
            self.time_wheel.remove(character_id)

        # 如果角色被重新激活，需要手动为他安排下一次行动
        # 否则他会等到自然触发的execute才被重新调度
        elif active and character_id not in self.time_wheel:
            current_time = self.calendar.get_timestamp()
            next_time = character.calculate_next_action_time(current_time)
            character.trigger_time = next_time
            delay = next_time - current_time
            self.time_wheel.schedule_with_delay(character.id, character, delay)

        return True

    def get_action_list(self, count: int) -> List[Dict[str, Any]]:
        """
        获取未来的行动列表，用于UI显示

        Args:
            count: 要获取的行动数量

        Returns:
            一个包含行动信息的字典列表
        """
        # 预览未来的所有事件
        events_tuples = self.time_wheel.peek_upcoming_events(
            count=self.TIME_WHEEL_SIZE,
            max_events=count
        )

        action_list = []
        current_time = self.calendar.get_timestamp()

        for key, event in events_tuples:
            if isinstance(event, Character):
                remaining_time = event.trigger_time - current_time
                action_list.append({
                    "id": event.id,
                    "name": event.name,
                    "type": event.event_type.name,
                    "time_until": remaining_time,
                    "trigger_time": event.trigger_time
                })

        return action_list

    def get_status_text(self) -> str:
        """获取系统当前状态的文本描述"""
        if not self.is_initialized:
            return "CTB系统未初始化"

        status_lines = [
            "=== CTB系统状态 ===",
            f"  时间轮大小: {self.time_wheel.buffer_size} 小时",
            f"  当前偏移: {self.time_wheel.offset}",
            f"  事件总数: {len(self.time_wheel)}",
            f"  角色数量: {len(self.characters)}",
            f"  活跃角色: {sum(1 for c in self.characters.values() if c.is_active)}",
        ]

        # 使用 peek_upcoming_events 安全地获取下一个事件
        next_events = self.time_wheel.peek_upcoming_events(count=self.time_wheel.buffer_size, max_events=1)
        if next_events:
            _key, next_event = next_events[0]
            current_time = self.calendar.get_timestamp()
            delay = next_event.trigger_time - current_time
            if delay <= 0:
                status_lines.append(f"  下个行动: 立即执行 ({next_event.name})")
            else:
                status_lines.append(f"  下个行动: {delay} 小时后 ({next_event.name})")
        else:
            status_lines.append("  下个行动: (无)")

        return "\n".join(status_lines)

    def get_character_info(self) -> List[Dict[str, Any]]:
        """
        获取所有角色信息

        Returns:
            List[Dict[str, Any]]: 角色信息列表
        """
        info_list = []

        for character in self.characters.values():
            info = {
                'id': character.id,
                'name': character.name,
                'faction': character.faction,
                'is_active': character.is_active
            }

            # 尝试从时间轮中获取下次行动时间
            event = self.time_wheel.get(character.id)
            if event:
                current_time = self.calendar.get_timestamp()
                info['next_action_time'] = event.trigger_time
                info['time_until_action'] = event.trigger_time - current_time

            info_list.append(info)

        return info_list

    def get_next_action_time_info(self) -> str:
        """获取下一个行动的时间信息"""
        # 使用 peek_upcoming_events 安全地获取下一个事件
        next_events = self.time_wheel.peek_upcoming_events(count=self.time_wheel.buffer_size, max_events=1)
        if next_events:
            _key, next_event = next_events[0]
            current_time = self.calendar.get_timestamp()
            delay = next_event.trigger_time - current_time
            if delay <= 0:
                # 如果有事件已经到期（或即将到期），返回格式化的时间
                return self.calendar.format_date_era()
            else:
                # 否则，返回剩余的小时数
                return f"{delay}小时后"
        return "无"