"""
可调度系统模块

提供CTB系统的可调度接口和相关实现。
"""

from .schedulable import Schedulable
from .schedulable_example import SchedulableExample

__all__ = ['Schedulable', 'SchedulableExample']