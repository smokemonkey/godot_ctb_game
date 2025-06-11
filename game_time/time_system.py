from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TimeUnit(Enum):
    """时间单位枚举"""
    HOUR = "hour"
    DAY = "day"


@dataclass
class EraNode:
    """纪年节点"""
    name: str  # 纪年名称，如"开元"
    start_year: int  # 开始年份（公元年）
    
    
class TimeManager:
    """时间管理器 - 负责游戏时间的流逝和控制
    
    专为回合制游戏设计的时间系统，支持非匀速时间流逝、精确时间控制和纪年管理。
    
    Attributes:
        DAYS_PER_YEAR (int): 每年天数，默认360天
        HOURS_PER_DAY (int): 每天小时数，默认24小时  
        BASE_YEAR (int): 起始年份，默认公元前1000年
        
    Example:
        >>> time_manager = TimeManager()
        >>> time_manager.advance_time(30, TimeUnit.DAY)
        >>> print(f"当前年份: {time_manager.current_year}")
        >>> time_manager.add_era_node("开元")
    """
    
    DAYS_PER_YEAR = 360
    HOURS_PER_DAY = 24
    BASE_YEAR = -1000  # 公元前1000年
    
    def __init__(self):
        # 当前时间（以小时为最小单位）
        self._total_hours = 0
        # 纪年节点列表
        self._era_nodes: list[EraNode] = []
    
    @property
    def current_year(self) -> int:
        """当前年份（公元年）"""
        total_days = self._total_hours // self.HOURS_PER_DAY
        return self.BASE_YEAR + (total_days // self.DAYS_PER_YEAR)
    
    @property
    def current_day_in_year(self) -> int:
        """当前年中的第几天（1-360）"""
        total_days = self._total_hours // self.HOURS_PER_DAY
        return (total_days % self.DAYS_PER_YEAR) + 1
    
    @property
    def current_hour(self) -> int:
        """当前小时（0-23）"""
        return self._total_hours % self.HOURS_PER_DAY
    
    @property
    def current_month(self) -> int:
        """当前月份（1-12，每月30天）"""
        return ((self.current_day_in_year - 1) // 30) + 1
    
    @property
    def current_day_in_month(self) -> int:
        """当前月中的第几天（1-30）"""
        return ((self.current_day_in_year - 1) % 30) + 1
    
    def advance_time(self, amount: int, unit: TimeUnit = TimeUnit.DAY) -> None:
        """推进时间
        
        Args:
            amount (int): 推进的时间数量
            unit (TimeUnit): 时间单位，默认为天
            
        Example:
            >>> time_manager.advance_time(5, TimeUnit.DAY)   # 推进5天
            >>> time_manager.advance_time(3, TimeUnit.HOUR)  # 推进3小时
        """
        if unit == TimeUnit.DAY:
            self._total_hours += amount * self.HOURS_PER_DAY
        elif unit == TimeUnit.HOUR:
            self._total_hours += amount
    
    def set_time_to_day(self, target_day: int, from_current_year: bool = True) -> None:
        """设置时间到指定天数
        
        Args:
            target_day: 目标天数
            from_current_year: 是否从当前年开始计算
        """
        if from_current_year:
            current_year_start_hours = (self.current_year - self.BASE_YEAR) * self.DAYS_PER_YEAR * self.HOURS_PER_DAY
            self._total_hours = current_year_start_hours + (target_day - 1) * self.HOURS_PER_DAY
        else:
            self._total_hours = (target_day - 1) * self.HOURS_PER_DAY
    
    def set_time_to_hour(self, target_hour: int, from_current_day: bool = True) -> None:
        """设置时间到指定小时
        
        Args:
            target_hour: 目标小时（0-23）
            from_current_day: 是否从当前天开始计算
        """
        if from_current_day:
            current_day_start_hours = (self._total_hours // self.HOURS_PER_DAY) * self.HOURS_PER_DAY
            self._total_hours = current_day_start_hours + target_hour
        else:
            self._total_hours = target_hour
    
    def add_era_node(self, name: str, start_year: Optional[int] = None) -> None:
        """添加纪年节点
        
        Args:
            name: 纪年名称
            start_year: 开始年份，如果为None则使用当前年份
        """
        if start_year is None:
            start_year = self.current_year
        
        era_node = EraNode(name, start_year)
        # 按开始年份排序插入
        insert_index = 0
        for i, existing_era in enumerate(self._era_nodes):
            if existing_era.start_year <= start_year:
                insert_index = i + 1
            else:
                break
        
        self._era_nodes.insert(insert_index, era_node)
    
    def get_current_era(self) -> Optional[EraNode]:
        """获取当前纪年"""
        current_year = self.current_year
        for era in reversed(self._era_nodes):
            if era.start_year <= current_year:
                return era
        return None
    
    def get_time_info(self) -> dict:
        """获取当前时间信息"""
        return {
            'total_hours': self._total_hours,
            'year': self.current_year,
            'month': self.current_month,
            'day_in_month': self.current_day_in_month,
            'day_in_year': self.current_day_in_year,
            'hour': self.current_hour,
            'current_era': self.get_current_era()
        }


class Calendar:
    """日历显示器 - 负责时间的格式化显示"""
    
    def __init__(self, time_manager: TimeManager):
        self.time_manager = time_manager
    
    def format_date_gregorian(self, show_hour: bool = False) -> str:
        """格式化为公历日期显示
        
        Args:
            show_hour: 是否显示小时
        
        Returns:
            格式化的日期字符串
        """
        year = self.time_manager.current_year
        month = self.time_manager.current_month
        day = self.time_manager.current_day_in_month
        hour = self.time_manager.current_hour
        
        # 处理公元前年份
        if year < 0:
            year_str = f"公元前{abs(year)}年"
        else:
            year_str = f"公元{year}年"
        
        if show_hour:
            return f"{year_str}{month}月{day}日{hour}点"
        else:
            return f"{year_str}{month}月{day}日"
    
    def format_date_era(self, show_hour: bool = False) -> str:
        """格式化为纪年日期显示
        
        Args:
            show_hour: 是否显示小时
        
        Returns:
            格式化的日期字符串
        """
        current_era = self.time_manager.get_current_era()
        
        if current_era is None:
            return self.format_date_gregorian(show_hour)
        
        era_year = self.time_manager.current_year - current_era.start_year + 1
        month = self.time_manager.current_month
        day = self.time_manager.current_day_in_month
        hour = self.time_manager.current_hour
        
        if show_hour:
            return f"{current_era.name}{era_year}年{month}月{day}日{hour}点"
        else:
            return f"{current_era.name}{era_year}年{month}月{day}日"
    
    def get_time_status_text(self) -> str:
        """获取详细的时间状态文本"""
        info = self.time_manager.get_time_info()
        gregorian = self.format_date_gregorian(True)
        era = self.format_date_era(True)
        
        status_lines = [
            f"公历: {gregorian}",
            f"纪年: {era}",
            f"年内第{info['day_in_year']}天",
            f"总计: {info['total_hours']}小时"
        ]
        
        return "\n".join(status_lines) 