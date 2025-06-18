#!/usr/bin/env python3
"""
CTB (Conditional Turn-Based) 战斗系统核心模块

基于事件调度系统，支持角色行动和各种游戏事件的精确时间管理。

核心特性:
- 事件驱动: 所有游戏行为都是事件，包括角色行动
- 时间调度: 使用回调函数访问时间轮，不直接管理时间
- 随机间隔: 角色行动间隔在1-180天之间随机分布
- 灵活扩展: 支持自定义事件类型和执行逻辑

设计原则:
- CTB只负责事件的调度和执行
- 不直接管理时间轮或日历
- 通过回调函数访问时间轮功能
- 事件执行后返回下次执行时间
"""

from typing import List, Optional, Dict, Any, Callable, Tuple
from enum import Enum, auto
import random
from dataclasses import dataclass

# 导入时间系统


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

    负责管理所有事件的调度和执行，通过回调函数访问时间轮。

    Attributes:
        get_time_callback: 获取当前时间的回调函数
        schedule_callback: 调度事件的回调函数
        remove_callback: 移除事件的回调函数
        peek_callback: 预览事件的回调函数
        pop_callback: 弹出到期事件的回调函数
        characters: 角色字典
        is_initialized: 系统是否已初始化
        action_history: 行动历史记录
    """

    def __init__(self,
                 get_time_callback: Callable[[], int],
                 schedule_callback: Callable[[str, Event, int], bool],
                 remove_callback: Callable[[str], bool],
                 peek_callback: Callable[[int, int], List[Tuple[str, Event]]],
                 pop_callback: Callable[[], Optional[Tuple[str, Event]]]):
        """
        初始化CTB管理器

        Args:
            get_time_callback: 获取当前时间的回调函数
            schedule_callback: 调度事件的回调函数 (key, event, delay) -> bool
            remove_callback: 移除事件的回调函数 (key) -> bool
            peek_callback: 预览事件的回调函数 (count, max_events) -> List[Tuple[str, Event]]
            pop_callback: 弹出到期事件的回调函数 () -> Optional[Tuple[str, Event]]
        """
        self.get_time_callback = get_time_callback
        self.schedule_callback = schedule_callback
        self.remove_callback = remove_callback
        self.peek_callback = peek_callback
        self.pop_callback = pop_callback

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
        self.remove_callback(character_id)

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

        current_time = self.get_time_callback()

        # 为每个活跃角色安排初始行动
        for character in self.characters.values():
            if character.is_active:
                # 计算初始行动时间
                next_time = character.calculate_next_action_time(current_time)
                character.trigger_time = next_time

                # 添加到时间轮
                delay = next_time - current_time
                self.schedule_callback(character.id, character, delay)

        self.is_initialized = True

    def schedule_event(self, event: Event, trigger_time: int) -> bool:
        """
        调度自定义事件

        Args:
            event: 要调度的事件
            trigger_time: 触发时间（绝对时间）

        Returns:
            bool: 如果成功调度返回True，否则返回False
        """
        current_time = self.get_time_callback()
        if trigger_time < current_time:
            return False  # 不能在过去调度事件

        delay = trigger_time - current_time
        return self.schedule_with_delay(event.id, event, delay)

    def schedule_with_delay(self, key: str, event: Event, delay: int) -> bool:
        """
        使用延迟时间调度事件

        Args:
            key: 事件键值
            event: 要调度的事件
            delay: 延迟时间（小时）

        Returns:
            bool: 如果成功调度返回True，否则返回False
        """
        return self.schedule_callback(key, event, delay)

    def get_due_event(self) -> Optional[Event]:
        """
        获取当前时间到期的下一个事件

        Returns:
            Optional[Event]: 到期的事件，如果没有则返回None
        """
        event_tuple = self.pop_callback()
        if event_tuple is None:
            return None

        _key, event = event_tuple
        return event

    def execute_events(self, events: List[Event]) -> None:
        """
        执行事件列表

        Args:
            events: 要执行的事件列表
        """
        for event in events:
            self._execute_event(event)

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
                current_time = self.get_time_callback()
                next_time = character.calculate_next_action_time(current_time)
                character.trigger_time = next_time
                delay = next_time - current_time
                self.schedule_with_delay(character.id, character, delay)

    def _record_action(self, event: Event) -> None:
        """
        记录行动历史

        Args:
            event: 执行的事件
        """
        current_time = self.get_time_callback()
        record = {
            'event_name': event.name,
            'event_type': event.event_type.name,
            'timestamp': current_time,
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
            self.remove_callback(character_id)

        # 如果角色被重新激活，需要手动为他安排下一次行动
        elif active:
            current_time = self.get_time_callback()
            next_time = character.calculate_next_action_time(current_time)
            character.trigger_time = next_time
            delay = next_time - current_time
            self.schedule_with_delay(character.id, character, delay)

        return True

    def get_status_text(self) -> str:
        """获取系统当前状态的文本描述"""
        if not self.is_initialized:
            return "CTB系统未初始化"

        current_time = self.get_time_callback()
        active_characters = sum(1 for c in self.characters.values() if c.is_active)

        status_lines = [
            "=== CTB系统状态 ===",
            f"  当前时间: {current_time} 小时",
            f"  角色数量: {len(self.characters)}",
            f"  活跃角色: {active_characters}",
        ]

        # 获取下一个事件
        next_events = self.peek_callback(count=1, max_events=1)
        if next_events:
            _key, next_event = next_events[0]
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
        current_time = self.get_time_callback()

        for character in self.characters.values():
            info = {
                'id': character.id,
                'name': character.name,
                'faction': character.faction,
                'is_active': character.is_active
            }

            # 尝试从时间轮中获取下次行动时间
            events = self.peek_callback(count=1, max_events=1)
            for key, event in events:
                if key == character.id:
                    info['next_action_time'] = event.trigger_time
                    info['time_until_action'] = event.trigger_time - current_time
                    break

            info_list.append(info)

        return info_list

    def get_next_action_time_info(self) -> str:
        """获取下一个行动的时间信息"""
        next_events = self.peek_callback(count=1, max_events=1)
        if not next_events:
            return "无"

        current_time = self.get_time_callback()
        _key, next_event = next_events[0]
        delay = next_event.trigger_time - current_time

        if delay <= 0:
            return "立即执行"
        else:
            return f"{delay}小时后"