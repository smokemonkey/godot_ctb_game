#!/usr/bin/env python3
"""
可调度示例模块

这是一个开发用的示例类，展示如何实现Schedulable接口。
适合作为学习参考，不是最终的游戏角色实现。
"""

import random
import math
from typing import Dict, List, Any
from .schedulable import Schedulable


class EventExample(Schedulable):
    """
    Schedulable接口的示例实现类

    这是一个开发用的示例类，展示如何实现Schedulable接口。

    Attributes:
        faction: 阵营
        is_active: 是否活跃
        action_list: 可执行的行动列表
    """

    def __init__(self, id: str, name: str, faction: str = "中立"):
        """
        初始化示例对象

        Args:
            id: 对象唯一标识符
            name: 对象名称
            faction: 阵营
        """
        super().__init__(id, name, f"{name}的战斗行动")
        self.faction = faction
        self.is_active = True

        # 预定义行动列表
        self.action_list = [
            "攻击",
            "防御",
            "使用技能",
            "移动",
            "观察",
            "休息",
            "准备反击",
            "蓄力"
        ]

    def execute(self) -> Any:
        """
        执行角色行动

        Returns:
            行动结果字典，包含actor、action、success等信息
        """
        if not self.is_active:
            print(f"角色 {self.name} 处于非活跃状态，跳过行动")
            return None

        # 随机选择一个行动
        random_action = random.choice(self.action_list)
        print(f"角色 {self.name} 执行行动: {random_action}")

        return {
            "actor": self,
            "action": random_action,
            "success": True
        }

    def calculate_next_schedule_time(self, current_time: int) -> int:
        """
        计算下次行动时间

        使用三角分布生成行动间隔。

        Args:
            current_time: 当前时间

        Returns:
            下次行动的绝对时间
        """
        # 使用配置中的三角分布参数（模拟ConfigManager）
        min_days = 1    # ConfigManager.ctb_action_delay_min_days
        max_days = 180  # ConfigManager.ctb_action_delay_max_days
        peak_days = 90  # ConfigManager.ctb_action_delay_peak_days

        days = self._triangular_distribution(min_days, max_days, peak_days)
        hours = int(days * 24)  # 24小时每天
        return current_time + hours

    def should_reschedule(self) -> bool:
        """
        是否需要重复调度

        Returns:
            True如果角色活跃，False如果非活跃
        """
        return self.is_active

    def set_active(self, active: bool) -> None:
        """
        设置活跃状态

        Args:
            active: 是否活跃
        """
        self.is_active = active
        if not active:
            print(f"角色 {self.name} 已设置为非活跃状态")
        else:
            print(f"角色 {self.name} 已激活")

    def _triangular_distribution(self, min_val: float, max_val: float, mode: float) -> float:
        """
        三角分布实现

        Args:
            min_val: 最小值
            max_val: 最大值
            mode: 众数（峰值）

        Returns:
            三角分布的随机值
        """
        u = random.random()
        c = (mode - min_val) / (max_val - min_val)

        if u < c:
            return min_val + math.sqrt(u * (max_val - min_val) * (mode - min_val))
        else:
            return max_val - math.sqrt((1 - u) * (max_val - min_val) * (max_val - mode))

    def get_character_info(self) -> Dict[str, Any]:
        """
        获取角色信息

        Returns:
            包含角色详细信息的字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "faction": self.faction,
            "is_active": self.is_active,
            "trigger_time": self.trigger_time,
            "description": self.description
        }

    def get_type_identifier(self) -> str:
        """获取类型标识符"""
        return "EventExample"