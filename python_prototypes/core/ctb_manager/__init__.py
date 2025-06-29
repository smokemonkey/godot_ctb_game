"""
CTB (Conditional Turn-Based) 战斗系统

一个灵活的回合制战斗系统，支持条件触发的行动顺序。

主要组件:
- TimeWheel: 通用时间轮数据结构，用于事件调度
- IndexedTimeWheel: 带索引的时间轮，支持快速查找
- Event: 事件基类，所有CTB事件的基础
- Character: 角色类，继承自Event
- CTBManager: CTB系统管理器，协调所有组件

使用示例:
    >>> from game_system.calendar import Calendar
    >>> from game_system.ctb_manager import CTBManager, Character
    >>>
    >>> # 创建日历和CTB管理器
    >>> calendar = Calendar()
    >>> ctb_mgr = CTBManager(
    ...     get_time_callback=lambda: calendar.get_timestamp(),
    ...     schedule_callback=lambda key, event, delay: True,
    ...     remove_callback=lambda key: True,
    ...     peek_callback=lambda count, max_events: [],
    ...     pop_callback=lambda: None
    ... )
    >>>
    >>> # 添加角色
    >>> hero = Character("hero", "英雄")
    >>> enemy = Character("enemy", "敌人", faction="敌方")
    >>> ctb_mgr.add_character(hero)
    >>> ctb_mgr.add_character(enemy)
    >>>
    >>> # 初始化战斗
    >>> ctb_mgr.initialize_ctb()
    >>>
    >>> # 执行下一个行动
    >>> next_action = ctb_mgr.get_due_event()
    >>> if next_action:
    ...     print(f"{next_action.name} 行动了！")

最后更新: 2024-12-17
"""

# 版本信息
__version__ = "2.0.0"
__author__ = "CTB Development Team"

# 导入核心组件
from .ctb_manager import (
    Character,
    CTBManager,
    Event,
    EventType,
)
from ..indexed_time_wheel import (
    IndexedTimeWheel,
)

# 公开接口
__all__ = [
    'Character',
    'CTBManager',
    'Event',
    'EventType',
    'IndexedTimeWheel',
]