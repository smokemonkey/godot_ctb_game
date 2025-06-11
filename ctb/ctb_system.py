"""
CTB (Conditional Turn-Based) 系统模块

提供基于速度的回合制战斗系统，角色根据速度属性计算行动间隔。
与时间系统集成，支持精确的时间推进和行动调度。
"""

from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import heapq
from game_time import TimeManager, TimeUnit


class ActionType(Enum):
    """行动类型枚举"""
    MOVE = "移动"
    ATTACK = "攻击" 
    SKILL = "技能"
    WAIT = "等待"
    CUSTOM = "自定义"


@dataclass
class Character:
    """角色数据类"""
    id: str
    name: str
    speed: int
    faction: str = "中立"
    is_active: bool = True
    
    def __post_init__(self):
        """初始化后验证"""
        if self.speed <= 0:
            raise ValueError(f"角色 {self.name} 的速度必须大于0，当前值: {self.speed}")


@dataclass
class ActionEvent:
    """行动事件数据类"""
    trigger_time: int  # 触发的绝对时间（小时）
    character: Character
    action_type: ActionType = ActionType.CUSTOM
    description: str = ""
    
    def __lt__(self, other):
        """用于堆排序的比较方法"""
        return self.trigger_time < other.trigger_time


class CTBFormula:
    """CTB公式配置类 - 隔离计算逻辑便于修改"""
    
    @staticmethod
    def calculate_action_interval(speed: int, base_factor: int = 100) -> float:
        """
        计算行动间隔
        
        Args:
            speed: 角色速度
            base_factor: 基础因子，默认100
            
        Returns:
            行动间隔（天数）
            
        Formula:
            interval_days = base_factor / speed
        """
        if speed <= 0:
            raise ValueError("速度必须大于0")
        return base_factor / speed
    
    @staticmethod
    def calculate_next_action_time(current_time: int, speed: int, base_factor: int = 100) -> int:
        """
        计算下次行动时间
        
        Args:
            current_time: 当前时间（小时）
            speed: 角色速度
            base_factor: 基础因子
            
        Returns:
            下次行动时间（小时）
        """
        interval_days = CTBFormula.calculate_action_interval(speed, base_factor)
        interval_hours = int(interval_days * 24)  # 转换为小时
        return current_time + interval_hours


class CTBManager:
    """CTB系统管理器"""
    
    def __init__(self, time_manager: TimeManager, base_factor: int = 100):
        """
        初始化CTB管理器
        
        Args:
            time_manager: 时间管理器实例
            base_factor: 速度计算的基础因子
        """
        self.time_manager = time_manager
        self.base_factor = base_factor
        self.characters: List[Character] = []
        self.action_queue: List[ActionEvent] = []  # 使用堆队列管理行动顺序
        self.action_history: List[Dict[str, Any]] = []
        self.is_initialized = False
        
        # 回调函数
        self.on_character_action: Optional[Callable[[ActionEvent], None]] = None
    
    def set_base_factor(self, factor: int) -> None:
        """设置基础因子"""
        if factor <= 0:
            raise ValueError("基础因子必须大于0")
        self.base_factor = factor
        if self.is_initialized:
            self._rebuild_action_queue()
    
    def add_character(self, character: Character) -> None:
        """添加角色"""
        if any(c.id == character.id for c in self.characters):
            raise ValueError(f"角色ID '{character.id}' 已存在")
        
        self.characters.append(character)
        
        # 如果系统已初始化，立即为新角色安排行动
        if self.is_initialized:
            self._schedule_character_action(character)
    
    def remove_character(self, character_id: str) -> bool:
        """移除角色"""
        character = self.get_character(character_id)
        if not character:
            return False
        
        # 从角色列表中移除
        self.characters = [c for c in self.characters if c.id != character_id]
        
        # 从行动队列中移除相关事件
        self.action_queue = [event for event in self.action_queue 
                           if event.character.id != character_id]
        heapq.heapify(self.action_queue)
        
        return True
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """获取角色"""
        return next((c for c in self.characters if c.id == character_id), None)
    
    def initialize_ctb(self) -> None:
        """初始化CTB系统，为所有角色安排首次行动"""
        if not self.characters:
            raise ValueError("没有角色可以初始化CTB系统")
        
        self.action_queue.clear()
        current_time = self.time_manager._total_hours
        
        # 为每个角色安排首次行动
        for character in self.characters:
            if character.is_active:
                self._schedule_character_action(character, current_time)
        
        self.is_initialized = True
    
    def _schedule_character_action(self, character: Character, from_time: Optional[int] = None) -> None:
        """为角色安排下次行动"""
        if not character.is_active:
            return
        
        current_time = from_time if from_time is not None else self.time_manager._total_hours
        next_action_time = CTBFormula.calculate_next_action_time(
            current_time, character.speed, self.base_factor
        )
        
        action_event = ActionEvent(
            trigger_time=next_action_time,
            character=character,
            action_type=ActionType.CUSTOM,
            description=f"{character.name} 准备行动"
        )
        
        heapq.heappush(self.action_queue, action_event)
    
    def _rebuild_action_queue(self) -> None:
        """重建行动队列（当基础因子改变时）"""
        if not self.is_initialized:
            return
        
        # 保存当前时间
        current_time = self.time_manager._total_hours
        
        # 清空队列并重新安排所有角色
        self.action_queue.clear()
        for character in self.characters:
            if character.is_active:
                self._schedule_character_action(character, current_time)
    
    def get_next_action(self) -> Optional[ActionEvent]:
        """获取下一个行动事件（不执行）"""
        if not self.action_queue:
            return None
        return self.action_queue[0]
    
    def execute_next_action(self) -> Optional[ActionEvent]:
        """执行下一个行动"""
        if not self.action_queue:
            return None
        
        # 获取下一个行动事件
        next_action = heapq.heappop(self.action_queue)
        
        # 推进时间到行动时间
        target_time = next_action.trigger_time
        current_time = self.time_manager._total_hours
        
        if target_time > current_time:
            time_diff = target_time - current_time
            self.time_manager.advance_time(time_diff, TimeUnit.HOUR)
        
        # 执行行动
        self._perform_action(next_action)
        
        # 为该角色安排下次行动
        self._schedule_character_action(next_action.character)
        
        return next_action
    
    def _perform_action(self, action: ActionEvent) -> None:
        """执行具体行动"""
        # 记录行动历史
        action_record = {
            'timestamp': self.time_manager._total_hours,
            'year': self.time_manager.current_year,
            'month': self.time_manager.current_month,
            'day': self.time_manager.current_day_in_month,
            'hour': self.time_manager.current_hour,
            'character_id': action.character.id,
            'character_name': action.character.name,
            'action_type': action.action_type.value,
            'description': action.description
        }
        self.action_history.append(action_record)
        
        # 触发回调
        if self.on_character_action:
            self.on_character_action(action)
    
    def get_action_queue_info(self) -> List[Dict[str, Any]]:
        """获取行动队列信息"""
        queue_info = []
        for event in sorted(self.action_queue):
            queue_info.append({
                'character_name': event.character.name,
                'trigger_time': event.trigger_time,
                'time_until_action': event.trigger_time - self.time_manager._total_hours,
                'action_type': event.action_type.value,
                'description': event.description
            })
        return queue_info
    
    def get_character_info(self) -> List[Dict[str, Any]]:
        """获取角色信息"""
        info = []
        for char in self.characters:
            interval = CTBFormula.calculate_action_interval(char.speed, self.base_factor)
            info.append({
                'id': char.id,
                'name': char.name,
                'speed': char.speed,
                'faction': char.faction,
                'is_active': char.is_active,
                'action_interval_days': round(interval, 2),
                'action_interval_hours': round(interval * 24, 1)
            })
        return info
    
    def get_recent_actions(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近的行动记录"""
        return self.action_history[-count:] if self.action_history else []
    
    def set_character_active(self, character_id: str, is_active: bool) -> bool:
        """设置角色活跃状态"""
        character = self.get_character(character_id)
        if not character:
            return False
        
        character.is_active = is_active
        
        if not is_active:
            # 移除该角色的所有行动事件
            self.action_queue = [event for event in self.action_queue 
                               if event.character.id != character_id]
            heapq.heapify(self.action_queue)
        elif self.is_initialized:
            # 如果重新激活，安排行动
            self._schedule_character_action(character)
        
        return True
    
    def get_status_text(self) -> str:
        """获取CTB系统状态文本"""
        if not self.is_initialized:
            return "CTB系统未初始化"
        
        lines = []
        lines.append(f"=== CTB系统状态 ===")
        lines.append(f"基础因子: {self.base_factor}")
        lines.append(f"活跃角色: {len([c for c in self.characters if c.is_active])}/{len(self.characters)}")
        lines.append(f"待执行行动: {len(self.action_queue)}")
        
        if self.action_queue:
            next_action = self.action_queue[0]
            time_until = next_action.trigger_time - self.time_manager._total_hours
            lines.append(f"下个行动: {next_action.character.name}")
            lines.append(f"剩余时间: {time_until}小时 ({time_until//24}天{time_until%24}小时)")
        
        return "\n".join(lines) 