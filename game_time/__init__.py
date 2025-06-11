"""
回合制游戏时间系统

一个专为回合制游戏设计的完整时间管理系统，支持非匀速时间流逝、双纪年显示和精确时间控制。

主要组件:
- TimeManager: 时间管理器
- Calendar: 日历显示器
- TimeUnit: 时间单位枚举
- EraNode: 纪年节点数据类

示例用法:
    >>> from game_time import TimeManager, Calendar, TimeUnit
    >>> time_manager = TimeManager()
    >>> time_manager.advance_time(30, TimeUnit.DAY)
    >>> calendar = Calendar(time_manager)
    >>> print(calendar.format_date_gregorian())
"""

from .time_system import TimeManager, Calendar, TimeUnit, EraNode
from .font_manager import FontManager, font_manager
from .ui_components import Button, TextDisplay, InputBox

__version__ = "1.0.0"
__author__ = "Game Time System"

# 导出的公共API
__all__ = [
    "TimeManager",
    "Calendar", 
    "TimeUnit",
    "EraNode",
    "FontManager",
    "font_manager",
    "Button",
    "TextDisplay", 
    "InputBox"
] 