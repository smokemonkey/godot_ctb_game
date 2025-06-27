#!/usr/bin/env python3
"""
可调度接口模块

定义了CTB系统中可调度对象的基础接口。任何可以被CTB系统调度的对象都应该实现此接口。

核心概念:
- 解耦合: CTB不再依赖具体的角色或事件类型
- 统一接口: 所有可调度对象使用相同的调度接口
- 灵活扩展: 任何对象都可以实现此接口被调度
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class Schedulable(ABC):
    """
    可调度接口基类
    
    任何可以被CTB系统调度的对象都应该继承此类。
    
    Attributes:
        id: 唯一标识符
        name: 显示名称
        trigger_time: 触发时间
        description: 描述信息
    """
    
    def __init__(self, id: str, name: str, description: str = ""):
        """
        初始化可调度对象
        
        Args:
            id: 唯一标识符
            name: 显示名称
            description: 描述信息
        """
        self.id = id
        self.name = name
        self.description = description
        self.trigger_time = 0
    
    @abstractmethod
    def execute(self) -> Any:
        """
        执行调度逻辑
        
        子类必须重写此方法实现具体的执行逻辑。
        
        Returns:
            执行结果（具体类型由子类定义）
        """
        pass
    
    @abstractmethod
    def calculate_next_schedule_time(self, current_time: int) -> int:
        """
        计算下次调度时间
        
        子类必须重写此方法实现下次调度时间的计算。
        
        Args:
            current_time: 当前时间
            
        Returns:
            下次调度的绝对时间
        """
        pass
    
    @abstractmethod
    def should_reschedule(self) -> bool:
        """
        是否需要重复调度
        
        子类可以重写此方法控制是否继续调度。
        
        Returns:
            True表示需要重复调度，False表示一次性事件
        """
        return False
    
    def get_type_identifier(self) -> str:
        """
        获取类型标识符
        
        用于调试和日志记录。
        
        Returns:
            类型标识符字符串
        """
        return self.__class__.__name__
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name} [{self.get_type_identifier()}]"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"{self.__class__.__name__}(id='{self.id}', name='{self.name}')"