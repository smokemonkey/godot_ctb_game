"""
回合制游戏时间系统

一个专为回合制游戏设计的核心时间管理系统，支持非匀速时间流逝、纪元锚定和精确时间控制。

主要组件:
- Calendar: 日历显示器和时间管理器，支持锚定功能
- TimeUnit: 时间单位枚举

示例用法:
    >>> from game_system.calendar import Calendar, TimeUnit
    >>> calendar = Calendar()
    >>> calendar.advance_time(10, TimeUnit.DAY)
    >>> calendar.anchor_era("开元", 713)  # 锚定开元元年=公元713年
"""

from .calendar import Calendar, TimeUnit

__version__ = "1.0.0"
__author__ = "Game Time System"

# 导出的公共API
__all__ = [
    "Calendar",
    "TimeUnit"
]