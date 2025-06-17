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

最后更新: 2024-12-17 - 采用buffer设计思路
"""

from typing import List, Optional, Dict, Any, Callable
from enum import Enum, auto
import random
from dataclasses import dataclass

# 导入时间系统
from game_time import TimeManager, TimeUnit

# 导入时间轮
from .time_wheel import IndexedTimeWheel


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
        time_manager: 时间管理器
        time_wheel: 时间轮调度器
        characters: 角色字典
        is_initialized: 系统是否已初始化
        action_history: 行动历史记录
    """

    # 时间轮大小：180天 * 24小时
    TIME_WHEEL_SIZE = 180 * 24

    def __init__(self, time_manager: TimeManager):
        """
        初始化CTB管理器

        Args:
            time_manager: 游戏时间管理器
        """
        self.time_manager = time_manager
        self.time_wheel = IndexedTimeWheel[Event](
            self.TIME_WHEEL_SIZE,
            key_func=lambda e: e.id
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
        self.time_wheel.remove_by_key(character_id)

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

        current_time = self.time_manager._total_hours

        # 为每个活跃角色安排初始行动
        for character in self.characters.values():
            if character.is_active:
                # 计算初始行动时间
                next_time = character.calculate_next_action_time(current_time)
                character.trigger_time = next_time

                # 添加到时间轮（使用buffer设计，delay=0表示立即执行）
                delay = next_time - current_time
                self.time_wheel.add(character, delay)

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
        current_time = self.time_manager._total_hours
        delay = trigger_time - current_time

        if delay < 0:
            return False  # 不能注册过去的事件

        event.trigger_time = trigger_time
        return self.time_wheel.add(event, delay)

    def execute_next_action(self) -> Optional[Event]:
        """
        执行下一个行动

        使用buffer设计：
        1. 检查当前槽位是否有事件
        2. 如果有，执行第一个事件
        3. 如果没有，推进时间直到找到事件

        Returns:
            Optional[Event]: 执行的事件，如果没有事件返回None
        """
        if not self.is_initialized:
            return None

        # 检查当前buffer
        current_buffer = self.time_wheel.get_current_buffer()

        if current_buffer:
            # 执行buffer中的第一个事件
            event = current_buffer[0]
            self.time_wheel.remove(event, 0)  # 从当前槽位移除

            # 执行事件
            self._execute_event(event)
            return event

        # 如果当前buffer为空，推进时间
        next_delay = self.time_wheel.get_next_event_delay()
        if next_delay is None:
            return None

        # 推进时间（以小时为单位）
        self.time_manager.advance_time(next_delay, TimeUnit.HOUR)

        # 推进时间轮
        self.time_wheel.advance(next_delay)

        # 推进后，事件应该在新的当前buffer中
        current_buffer = self.time_wheel.get_current_buffer()

        if current_buffer:
            # 执行第一个事件
            event = current_buffer[0]
            self.time_wheel.remove(event, 0)

            # 执行事件
            self._execute_event(event)
            return event

        return None

    def _execute_event(self, event: Event) -> None:
        """
        执行事件的内部方法

        Args:
            event: 要执行的事件
        """
        # 执行事件
        event.execute()

        # 记录历史
        self._record_action(event)

        # 如果是角色行动，安排下次行动
        if isinstance(event, Character) and event.is_active:
            current_time = self.time_manager._total_hours
            next_time = event.calculate_next_action_time(current_time)
            event.trigger_time = next_time

            delay = next_time - current_time
            self.time_wheel.add(event, delay)

        # 触发回调
        if self.on_event_executed:
            self.on_event_executed(event)

    def _record_action(self, event: Event) -> None:
        """
        记录行动历史

        Args:
            event: 执行的事件
        """
        record = {
            'event_name': event.name,
            'event_type': event.event_type.name,
            'timestamp': self.time_manager._total_hours,
            'year': self.time_manager.current_year,
            'month': self.time_manager.current_month,
            'day': self.time_manager.current_day_in_month,
            'hour': self.time_manager.current_hour
        }
        self.action_history.append(record)

    def set_character_active(self, character_id: str, active: bool) -> bool:
        """
        设置角色的活跃状态

        Args:
            character_id: 角色ID
            active: 是否活跃

        Returns:
            bool: 如果成功设置返回True
        """
        character = self.get_character(character_id)
        if not character:
            return False

        character.is_active = active

        if not active:
            # 如果设为非活跃，从时间轮中移除
            self.time_wheel.remove_by_key(character_id)
        else:
            # 如果设为活跃，重新安排行动
            current_time = self.time_manager._total_hours
            next_time = character.calculate_next_action_time(current_time)
            character.trigger_time = next_time

            delay = next_time - current_time
            self.time_wheel.add(character, delay)

        return True

    def get_action_list(self, count: int) -> List[Dict[str, Any]]:
        """
        获取未来的行动列表

        Args:
            count: 要获取的行动数量

        Returns:
            List[Dict[str, Any]]: 行动信息列表
        """
        all_events = self.time_wheel.get_all_events()
        current_time = self.time_manager._total_hours

        # 按延迟时间排序
        all_events.sort(key=lambda x: x[0])

        action_list = []
        for delay, event in all_events[:count]:
            action_info = {
                'event_name': event.name,
                'event_type': event.event_type.name,
                'hours_from_now': delay,
                'days_from_now': delay / 24,
                'trigger_time': current_time + delay
            }
            action_list.append(action_info)

        return action_list

    def get_status_text(self) -> str:
        """
        获取CTB系统状态文本

        Returns:
            str: 格式化的状态文本
        """
        if not self.is_initialized:
            return "CTB系统未初始化"

        lines = [
            "=== CTB系统状态 ===",
            f"时间轮大小: {self.TIME_WHEEL_SIZE} 小时",
            f"当前偏移: {self.time_wheel.offset}",
            f"总事件数: {self.time_wheel.total_events()}",
            f"活跃角色: {sum(1 for c in self.characters.values() if c.is_active)}",
        ]

        # 添加下一个行动信息
        next_delay = self.time_wheel.get_next_event_delay()
        if next_delay is not None:
            if next_delay == 0:
                lines.append("下个行动: 立即执行（当前buffer）")
            else:
                lines.append(f"下个行动: {next_delay} 小时后")

        return "\n".join(lines)

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
            event = self.time_wheel.get_by_key(character.id)
            if event:
                current_time = self.time_manager._total_hours
                info['next_action_time'] = event.trigger_time
                info['time_until_action'] = event.trigger_time - current_time

            info_list.append(info)

        return info_list