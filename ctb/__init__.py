"""
CTB (Conditional Turn-Based) 战斗系统

基于时间系统的回合制战斗模块，提供角色行动调度和管理功能。
专为回合制游戏设计，支持基于速度的行动排序和精确的时间推进。

主要组件:
- CTBManager: CTB系统管理器，核心控制类
- Character: 角色数据类，包含速度等属性
- ActionEvent: 行动事件类，表示单次行动
- ActionType: 行动类型枚举，定义行动种类
- CTBFormula: CTB公式计算类，隔离计算逻辑

核心特性:
- 速度驱动的行动顺序
- 与时间系统无缝集成
- 灵活的角色管理
- 完整的行动历史记录

示例用法:
    >>> from ctb import CTBManager, Character
    >>> from game_time import TimeManager
    >>> 
    >>> time_manager = TimeManager()
    >>> ctb = CTBManager(time_manager)
    >>> 
    >>> hero = Character("hero", "英雄", speed=100)
    >>> ctb.add_character(hero)
    >>> ctb.initialize_ctb()

依赖:
- game_time: 核心时间管理系统
"""

from .ctb_system import (
    CTBManager,
    Character, 
    ActionEvent,
    ActionType,
    CTBFormula
)

__version__ = "1.0.0"
__author__ = "CTB System"

# 导出的公共API
__all__ = [
    "CTBManager",
    "Character",
    "ActionEvent", 
    "ActionType",
    "CTBFormula"
] 