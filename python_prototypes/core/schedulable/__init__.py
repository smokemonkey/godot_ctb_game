"""
可调度系统模块

提供CTB系统的可调度接口和相关实现。
"""

from .schedulable import Schedulable
from .combat_actor import CombatActor

__all__ = ['Schedulable', 'CombatActor']