#!/usr/bin/env python3
"""
游戏世界系统测试

测试GameWorld单例类的各种功能。
"""

import unittest
import sys
import os
import threading
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from game_system.game_world import GameWorld, get_game_world, GameWorldConfig, reset_game_world
from game_system.calendar.calendar import TimeUnit


class TestGameWorld(unittest.TestCase):
    """测试GameWorld类的基本功能"""

    def setUp(self):
        """每个测试前的设置"""
        # 重置游戏世界到初始状态
        reset_game_world()
        self.world = get_game_world()

    def test_singleton_behavior(self):
        """测试单例模式行为"""
        world1 = get_game_world()
        world2 = get_game_world()
        world3 = GameWorld()

        # 验证所有实例都是同一个对象
        self.assertIs(world1, world2)
        self.assertIs(world1, world3)
        self.assertIs(world2, world3)

    def test_initial_state(self):
        """测试初始状态"""
        self.assertFalse(self.world.is_running)
        self.assertEqual(self.world.turn_count, 0)
        self.assertIsNotNone(self.world.calendar)
        self.assertIsNotNone(self.world.time_wheel)

    def test_start_stop_game(self):
        """测试开始和停止游戏"""
        # 初始状态
        self.assertFalse(self.world.is_running)

        # 开始游戏
        self.world.start_game()
        self.assertTrue(self.world.is_running)
        self.assertEqual(self.world.turn_count, 0)

        # 再次开始游戏（应该无效果）
        self.world.start_game()
        self.assertTrue(self.world.is_running)

        # 停止游戏
        self.world.stop_game()
        self.assertFalse(self.world.is_running)

    def test_schedule_remove_event(self):
        """测试调度和移除事件"""
        self.world.start_game()

        # 调度事件
        success = self.world.schedule_event("test_event", "test_data", 5)
        self.assertTrue(success)

        # 验证事件已添加
        upcoming_events = self.world.get_upcoming_events(10)
        self.assertEqual(len(upcoming_events), 1)
        self.assertEqual(upcoming_events[0][0], "test_event")

        # 移除事件
        removed_data = self.world.remove_event("test_event")
        self.assertEqual(removed_data, "test_data")

        # 验证事件已移除
        upcoming_events = self.world.get_upcoming_events(10)
        self.assertEqual(len(upcoming_events), 0)

        # 移除不存在的事件
        removed_data = self.world.remove_event("nonexistent")
        self.assertIsNone(removed_data)

    def test_time_management(self):
        """测试时间管理功能"""
        self.world.start_game()

        # 获取初始时间
        initial_time = self.world.calendar.get_time_info()

        # 手动推进时间 - 使用_advance_tick替代advance_time
        for _ in range(10 * 24):  # 推进10天 = 240小时
            self.world._advance_tick()

        # 验证时间已推进
        new_time = self.world.calendar.get_time_info()
        self.assertGreater(new_time['total_hours'], initial_time['total_hours'])

    def test_era_management(self):
        """测试纪元管理"""
        self.world.start_game()

        # 开始新纪元
        self.world.start_new_era("测试纪元")

        # 验证纪元信息
        era_name = self.world.calendar.get_current_era_name()
        era_year = self.world.calendar.get_current_era_year()

        self.assertEqual(era_name, "测试纪元")
        self.assertEqual(era_year, 1)

    def test_get_game_status(self):
        """测试获取游戏状态"""
        self.world.start_game()

        status = self.world.get_game_status()

        # 验证状态信息包含所有必要字段
        required_fields = ['is_running', 'turn_count', 'current_time',
                          'character_count', 'pending_events', 'future_events']
        for field in required_fields:
            self.assertIn(field, status)

        # 验证character_count为0（暂时）
        self.assertEqual(status['character_count'], 0)

    def test_event_system(self):
        """测试事件系统"""
        self.world.start_game()

        events_triggered = []

        def on_event_scheduled(data):
            events_triggered.append(('event_scheduled', data))

        def on_tick_ended(data):
            events_triggered.append(('tick_ended', data))

        # 注册事件回调
        self.world.register_event_callback('event_scheduled', on_event_scheduled)
        self.world.register_event_callback('tick_ended', on_tick_ended)

        # 触发事件
        self.world.schedule_event("test_event", "test_data", 5)

        # 推进tick触发事件 - 使用_advance_tick替代tick
        self.world._advance_tick()

        # 验证事件被触发
        self.assertGreater(len(events_triggered), 0)

        # 验证事件类型
        event_types = [event[0] for event in events_triggered]
        self.assertIn('event_scheduled', event_types)
        self.assertIn('tick_ended', event_types)

    def test_component_access(self):
        """测试组件访问"""
        # 验证可以直接访问各个组件
        self.assertIsNotNone(self.world.calendar)
        self.assertIsNotNone(self.world.time_wheel)

        # 验证组件类型
        from game_system.calendar.calendar import Calendar
        from game_system.indexed_time_wheel.indexed_time_wheel import IndexedTimeWheel

        self.assertIsInstance(self.world.calendar, Calendar)
        self.assertIsInstance(self.world.time_wheel, IndexedTimeWheel)

        # 添加事件并查看
        self.world.start_game()
        # 使用延迟1小时，确保在时间轮范围内
        self.world.schedule_event("test_event", "test_data", 1)

        # 查看即将发生的事件
        upcoming = self.world.get_upcoming_events(5)
        self.assertEqual(len(upcoming), 1)

    def test_reset_functionality(self):
        """测试重置功能"""
        self.world.start_game()

        # 添加事件
        self.world.schedule_event("test_event", "test_data", 5)

        # 推进几个tick - 使用_advance_tick替代tick
        for _ in range(3):
            self.world._advance_tick()

        # 验证状态已改变
        self.assertTrue(self.world.is_running)
        self.assertEqual(self.world.turn_count, 3)
        self.assertGreater(len(self.world.get_upcoming_events(10)), 0)

        # 重置
        self.world.reset()

        # 验证已重置到初始状态
        self.assertFalse(self.world.is_running)
        self.assertEqual(self.world.turn_count, 0)
        self.assertEqual(len(self.world.get_upcoming_events(10)), 0)

    def test_get_characters_info(self):
        """测试获取角色信息（暂时返回空列表）"""
        characters_info = self.world.get_characters_info()
        self.assertEqual(len(characters_info), 0)
        self.assertIsInstance(characters_info, list)


class TestGameWorldConcurrency(unittest.TestCase):
    """测试GameWorld的并发安全性"""

    def setUp(self):
        """每个测试前的设置"""
        reset_game_world()
        self.world = get_game_world()

    def test_concurrent_access(self):
        """测试并发访问"""
        self.world.start_game()

        exceptions = []

        def worker():
            """工作线程函数"""
            try:
                for _ in range(10):
                    # 调度事件
                    self.world.schedule_event(f"event_{threading.get_ident()}_{_}",
                                            f"data_{_}", _)

                    # 推进tick - 使用_advance_tick替代tick
                    self.world._advance_tick()

                    # 获取状态
                    self.world.get_game_status()

                time.sleep(0.001)  # 短暂休眠
            except Exception as e:
                exceptions.append(e)

        # 创建多个线程
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有异常
        self.assertEqual(len(exceptions), 0, f"并发访问出现异常: {exceptions}")


class TestGameWorldConfig(unittest.TestCase):
    """测试GameWorldConfig配置类"""

    def test_default_config(self):
        """测试默认配置"""
        config = GameWorldConfig()

        self.assertEqual(config.time_wheel_size, 180 * 24)
        self.assertTrue(config.enable_threading)
        self.assertEqual(config.auto_save_interval, 1000)

    def test_custom_config(self):
        """测试自定义配置"""
        config = GameWorldConfig(
            time_wheel_size=100,
            enable_threading=False,
            auto_save_interval=50
        )

        self.assertEqual(config.time_wheel_size, 100)
        self.assertFalse(config.enable_threading)
        self.assertEqual(config.auto_save_interval, 50)


if __name__ == '__main__':
    unittest.main(verbosity=2)