#!/usr/bin/env python3
"""
游戏世界系统 - 全局单例管理器

负责协调和管理游戏系统的三个核心组件：
- Calendar: 时间管理系统
- IndexedTimeWheel: 事件调度系统
- CTBManager: 战斗系统管理器

设计原则：
- 单例模式：确保全局唯一实例
- 组件协作：三个组件各司其职，相互配合
- 统一接口：提供简洁的游戏世界操作接口
- 线程安全：支持多线程环境下的安全访问
"""

import threading
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .calendar.calendar import Calendar, TimeUnit
from .indexed_time_wheel.indexed_time_wheel import IndexedTimeWheel
from .ctb.ctb import CTBManager


@dataclass
class GameWorldConfig:
    """游戏世界配置"""
    time_wheel_size: int = 180 * 24  # 180天 * 24小时
    enable_threading: bool = True
    auto_save_interval: int = 1000  # 自动保存间隔（回合数）


class GameWorld:
    """
    游戏世界单例类

    管理游戏的核心组件，提供统一的游戏世界操作接口。
    使用单例模式确保全局唯一实例。
    """

    _instance: Optional['GameWorld'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: Optional[GameWorldConfig] = None):
        """初始化游戏世界（仅在第一次创建时执行）"""
        if hasattr(self, '_initialized'):
            return

        self.config = config or GameWorldConfig()
        self._initialized = True

        # 初始化核心组件
        self._calendar: Optional[Calendar] = None
        self._time_wheel: Optional[IndexedTimeWheel] = None
        self._ctb_manager: Optional[CTBManager] = None

        # 游戏状态
        self._game_running = False
        self._auto_save_counter = 0

        # 事件回调
        self._event_callbacks: Dict[str, List[callable]] = {}

        # 线程安全锁
        self._lock = threading.Lock()

        # 初始化组件
        self._initialize_components()

    def _initialize_components(self):
        """初始化所有核心组件"""
        # 1. 初始化时间系统
        self._calendar = Calendar()

        # 2. 初始化时间轮，传入全局时间戳回调
        self._time_wheel = IndexedTimeWheel(
            self.config.time_wheel_size,
            get_time_callback=lambda: self._calendar.get_timestamp()
        )

        # 3. 初始化CTB管理器，传入时间轮的回调函数
        self._ctb_manager = CTBManager(
            get_time_callback=lambda: self._calendar.get_timestamp(),
            schedule_callback=lambda key, event, delay: self._time_wheel.schedule_with_delay(key, event, delay),
            remove_callback=lambda key: self._time_wheel.remove(key),
            peek_callback=lambda count, max_events: self._time_wheel.peek_upcoming_events(count, max_events),
            pop_callback=lambda: self._time_wheel.pop_due_event()
        )

        # 4. 设置组件间的协作关系
        self._setup_component_collaboration()

    def _setup_component_collaboration(self):
        """设置组件间的协作关系"""
        # 注册时间推进事件
        self.register_event_callback('time_advanced', self._on_time_advanced)
        self.register_event_callback('tick_started', self._on_tick_started)
        self.register_event_callback('tick_ended', self._on_tick_ended)

    # ==================== 公共接口 ====================

    def start_game(self) -> None:
        """开始游戏"""
        if self._game_running:
            return

        self._game_running = True
        self._auto_save_counter = 0

        self._trigger_event('game_started')
        print(f"游戏世界已启动 - 当前时间: {self._calendar.format_date_gregorian()}")

    def stop_game(self) -> None:
        """停止游戏"""
        if not self._game_running:
            return

        self._game_running = False
        self._trigger_event('game_stopped')
        print(f"游戏世界已停止 - 当前时间: {self._calendar.format_date_gregorian()}")

    # ==================== 查询接口 ====================

    @property
    def calendar(self) -> Calendar:
        """获取日历系统"""
        return self._calendar

    @property
    def time_wheel(self) -> IndexedTimeWheel:
        """获取时间轮系统"""
        return self._time_wheel

    @property
    def ctb_manager(self) -> CTBManager:
        """获取CTB管理器"""
        return self._ctb_manager

    @property
    def is_running(self) -> bool:
        """游戏是否正在运行"""
        return self._game_running

    @property
    def turn_count(self) -> int:
        """当前回合数（基于calendar的total_hours）"""
        return self._calendar.get_timestamp()

    def get_game_status(self) -> Dict[str, Any]:
        """获取游戏状态信息"""
        return {
            'is_running': self._game_running,
            'turn_count': self._calendar.get_timestamp(),
            'current_time': self._calendar.get_time_info(),
            'character_count': len(self._ctb_manager.characters) if self._ctb_manager else 0,
            'pending_events': len(self._time_wheel),
            'future_events': len(self._time_wheel.future_events)
        }

    def get_characters_info(self) -> List[Dict[str, Any]]:
        """获取所有角色信息"""
        if self._ctb_manager:
            return self._ctb_manager.get_character_info()
        return []

    # ==================== 事件系统 ====================

    def register_event_callback(self, event_type: str, callback: callable) -> None:
        """注册事件回调"""
        if event_type not in self._event_callbacks:
            self._event_callbacks[event_type] = []
        self._event_callbacks[event_type].append(callback)

    def unregister_event_callback(self, event_type: str, callback: callable) -> None:
        """注销事件回调"""
        if event_type in self._event_callbacks:
            try:
                self._event_callbacks[event_type].remove(callback)
            except ValueError:
                pass

    def _trigger_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """触发事件"""
        if event_type in self._event_callbacks:
            for callback in self._event_callbacks[event_type]:
                try:
                    callback(data or {})
                except Exception as e:
                    print(f"事件回调执行错误: {e}")

    # ==================== 内部方法 ====================

    def _on_time_advanced(self, data: Dict[str, Any]) -> None:
        """时间推进回调"""
        pass  # 可以在这里添加时间相关的逻辑

    def _on_tick_started(self, data: Dict[str, Any]) -> None:
        """tick开始回调"""
        pass  # 可以在这里添加tick开始时的逻辑

    def _on_tick_ended(self, data: Dict[str, Any]) -> None:
        """tick结束回调"""
        pass  # 可以在这里添加tick结束时的逻辑

    def _auto_save(self) -> None:
        """自动保存游戏状态"""
        # TODO: 实现自动保存逻辑
        self._trigger_event('auto_save', {'turn': self._calendar.get_timestamp()})

    def _advance_tick(self) -> None:
        # 1. 原子推进 - 所有时间相关操作都在锁内
        with self._lock:
            # 只通过Calendar推进时间，Calendar是唯一的时间源
            self._calendar.advance_time_tick()
            # 时间轮从Calendar获取当前时间并更新
            self._time_wheel.advance_wheel()

        # 2. 外围操作（锁外）
        self._auto_save_counter += 1
        if self._auto_save_counter >= self.config.auto_save_interval:
            self._auto_save()
            self._auto_save_counter = 0
        self._trigger_event('tick_ended', {
            'tick_number': self._calendar.get_timestamp(),
            'ticks_advanced': 1,
            'events_executed': 0,
            'current_time': self._calendar.get_time_info(),
            'next_actions': []
        })

    def advance_to_next_event(self) -> int:
        """
        推进时间直到下一个有事件的槽位（public方法，循环调用_advance_tick）
        Returns: int: 时间推进的小时数
        """
        ticks = 0
        for _ in range(self._time_wheel.buffer_size):
            if not self._time_wheel._is_current_slot_empty():
                break
            self._advance_tick()
            ticks += 1
        else:
            raise RuntimeError("advance_to_next_event completed a full cycle without finding any event in the wheel.")
        return ticks

    # ==================== 重置和清理 ====================

    def reset(self) -> None:
        """重置游戏世界到初始状态"""
        self.stop_game()

        # 重置所有组件
        self._calendar.reset()
        self._time_wheel = IndexedTimeWheel(
            self.config.time_wheel_size,
            get_time_callback=lambda: self._calendar.get_timestamp()
        )

        # 重新设置协作关系
        self._setup_component_collaboration()

        # 重置状态
        self._auto_save_counter = 0

        self._trigger_event('world_reset')

    def cleanup(self) -> None:
        """清理游戏世界资源"""
        self.stop_game()
        self._event_callbacks.clear()
        self._trigger_event('world_cleanup')


# ==================== 便捷函数 ====================

def get_game_world(config: Optional[GameWorldConfig] = None) -> GameWorld:
    """
    获取游戏世界实例的便捷函数

    Args:
        config: 游戏世界配置，仅在第一次创建时有效

    Returns:
        GameWorld: 游戏世界单例实例
    """
    return GameWorld(config)


def reset_game_world() -> None:
    """重置游戏世界"""
    world = get_game_world()
    world.reset()


def cleanup_game_world() -> None:
    """清理游戏世界"""
    world = get_game_world()
    world.cleanup()