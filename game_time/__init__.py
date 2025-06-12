"""
回合制游戏时间系统

一个专为回合制游戏设计的核心时间管理系统，支持非匀速时间流逝、纪元锚定和精确时间控制。

主要组件:
- TimeManager: 时间管理器，支持锚定功能
- Calendar: 日历显示器  
- TimeUnit: 时间单位枚举

示例用法:
    >>> from game_time import TimeManager, Calendar, TimeUnit
    >>> time_manager = TimeManager()
    >>> calendar = Calendar(time_manager)
    >>> time_manager.advance_time(10, TimeUnit.DAY)
    >>> time_manager.anchor_era("开元", 713)  # 锚定开元元年=公元713年
"""

from .time_system import TimeManager, Calendar, TimeUnit

__version__ = "1.0.0"
__author__ = "Game Time System"

# 导出的公共API
__all__ = [
    # 核心时间系统
    "TimeManager",
    "Calendar", 
    "TimeUnit"
] 