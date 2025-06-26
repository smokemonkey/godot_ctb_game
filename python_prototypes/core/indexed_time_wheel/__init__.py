"""
索引时间轮模块

提供带索引功能的时间轮数据结构，支持快速查找和删除事件。

主要组件:
- IndexedTimeWheel: 带索引的时间轮，支持O(1)查找和删除
"""

from .indexed_time_wheel import IndexedTimeWheel

__version__ = "1.0.0"
__author__ = "Indexed Time Wheel Team"

# 导出的公共API
__all__ = [
    "IndexedTimeWheel",
]