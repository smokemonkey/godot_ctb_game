"""
CTB (Character Turn-Based) System

基于时间系统的回合制战斗模块，提供角色行动调度和管理功能。

主要组件:
- CTBManager: CTB系统管理器
- Character: 角色类
- ActionEvent: 行动事件类
- ActionType: 行动类型枚举
- CTBFormula: CTB公式计算类

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

__all__ = [
    "CTBManager",
    "Character",
    "ActionEvent", 
    "ActionType",
    "CTBFormula"
]

__version__ = "1.0.0" 