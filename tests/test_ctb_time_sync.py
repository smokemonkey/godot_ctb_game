#!/usr/bin/env python3
"""
CTB系统与时间管理器同步测试

专门测试CTB系统与时间管理器的同步机制，确保：
- 时间推进的准确性
- 事件触发时机的正确性
- 同步状态的一致性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from game_time import TimeManager, TimeUnit
from ctb import CTBManager, Character, Event, EventType


class TestCTBTimeSync(unittest.TestCase):
    """CTB时间同步测试"""

    def setUp(self):
        """初始化测试环境"""
        self.time_manager = TimeManager()
        self.ctb = CTBManager(self.time_manager)

    def test_manual_event_registration_and_sync(self):
        """测试手动事件注册和同步"""
        hero = Character("hero", "英雄")
        self.ctb.add_character(hero)

        # 记录初始时间
        initial_time = self.time_manager._total_hours
        self.assertEqual(initial_time, 0)

        # 手动注册事件在10小时后
        self.ctb.register_event(hero, initial_time + 10)
        self.ctb._last_sync_time = initial_time

        # 验证事件已注册
        self.assertEqual(self.ctb.time_wheel.total_events(), 1)
        self.assertEqual(self.ctb.time_wheel.get_next_event_delay(), 10)

        # 推进11小时来触发延迟10的事件
        events = self.ctb.advance_time(11)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "英雄")
        self.assertEqual(self.time_manager._total_hours, 11)
        self.assertEqual(len(self.ctb.action_history), 1)

    def test_initialize_and_execute_flow(self):
        """测试初始化和执行流程"""
        # 添加多个角色
        hero = Character("hero", "英雄")
        enemy = Character("enemy", "敌人")

        self.ctb.add_character(hero)
        self.ctb.add_character(enemy)

        # 初始化CTB
        self.ctb.initialize_ctb()

        # 验证初始状态
        self.assertEqual(self.ctb.time_wheel.total_events(), 2)
        self.assertTrue(self.ctb.is_initialized)
        self.assertEqual(self.ctb._last_sync_time, 0)

        # 获取第一个事件的延迟
        first_delay = self.ctb.time_wheel.get_next_event_delay()
        self.assertIsNotNone(first_delay)
        self.assertGreater(first_delay, 0)  # 应该是正数

        # 执行第一个行动
        event = self.ctb.execute_next_action()
        self.assertIsNotNone(event)
        self.assertIsInstance(event, Character)

        # 验证时间推进了（需要多推进1来触发）
        self.assertEqual(self.time_manager._total_hours, first_delay + 1)

        # 验证事件被记录
        self.assertEqual(len(self.ctb.action_history), 1)

        # 角色应该安排了下次行动，所以还是2个事件
        self.assertEqual(self.ctb.time_wheel.total_events(), 2)

    def test_sync_after_manual_time_advance(self):
        """测试手动推进时间后的同步"""
        hero = Character("hero", "英雄")
        self.ctb.add_character(hero)

        # 在时间10注册事件
        self.ctb.register_event(hero, 10)
        self.ctb._last_sync_time = 0

        # 手动推进时间管理器（模拟外部时间推进）
        self.time_manager.advance_time(5, TimeUnit.HOUR)

        # CTB应该能同步这个变化
        events = self.ctb._sync_with_time_manager()
        self.assertEqual(len(events), 0)  # 还没到时间10
        self.assertEqual(self.ctb._last_sync_time, 5)

        # 再推进6小时（总共11小时）来触发
        self.time_manager.advance_time(6, TimeUnit.HOUR)
        events = self.ctb._sync_with_time_manager()
        self.assertEqual(len(events), 1)  # 现在应该触发了
        self.assertEqual(self.ctb._last_sync_time, 11)

    def test_multiple_events_at_same_time(self):
        """测试同时触发的多个事件"""
        # 创建多个事件在同一时间
        events_to_add = []
        for i in range(3):
            event = Event(
                id=f"event{i}",
                name=f"事件{i}",
                event_type=EventType.CUSTOM,
                trigger_time=100
            )
            events_to_add.append(event)

        # 注册所有事件
        for event in events_to_add:
            self.ctb.register_event(event, 100)

        self.ctb._last_sync_time = 0

        # 推进到触发时间（需要101来触发延迟100的事件）
        triggered = self.ctb.advance_time(101)

        # 验证所有事件都被触发
        self.assertEqual(len(triggered), 3)
        self.assertEqual(len(self.ctb.action_history), 3)

        # 验证事件名称
        triggered_names = {e.name for e in triggered}
        expected_names = {"事件0", "事件1", "事件2"}
        self.assertEqual(triggered_names, expected_names)

    def test_time_wheel_offset_consistency(self):
        """测试时间轮offset的一致性"""
        # 添加一个角色
        hero = Character("hero", "英雄")
        self.ctb.add_character(hero)

        # 在特定时间注册多个事件
        for hour in [24, 48, 72]:
            event = Event(f"e{hour}", f"事件{hour}", EventType.CUSTOM, hour)
            self.ctb.register_event(event, hour)

        self.ctb._last_sync_time = 0
        initial_offset = self.ctb.time_wheel.current_offset

        # 推进25小时来触发第一个事件
        self.ctb.advance_time(25)

        # offset应该增加25
        expected_offset = (initial_offset + 25) % self.ctb.TIME_WHEEL_SIZE
        self.assertEqual(self.ctb.time_wheel.current_offset, expected_offset)

        # 验证第一个事件被触发
        self.assertEqual(len(self.ctb.action_history), 1)
        self.assertEqual(self.ctb.action_history[0]['event_name'], "事件24")

    def test_edge_case_zero_delay_event(self):
        """测试延迟0的事件"""
        hero = Character("hero", "英雄")
        self.ctb.add_character(hero)

        current_time = self.time_manager._total_hours

        # 注册一个当前时间的事件
        self.ctb.register_event(hero, current_time)
        self.ctb._last_sync_time = current_time

        # 延迟0的事件需要推进1小时才能触发
        events = self.ctb.advance_time(1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "英雄")


class TestCTBTimeBoundaries(unittest.TestCase):
    """CTB时间边界测试"""

    def setUp(self):
        self.time_manager = TimeManager()
        self.ctb = CTBManager(self.time_manager)

    def test_max_time_wheel_capacity(self):
        """测试时间轮最大容量"""
        hero = Character("hero", "英雄")
        self.ctb.add_character(hero)

        current_time = self.time_manager._total_hours
        max_valid_time = current_time + self.ctb.TIME_WHEEL_SIZE - 1

        # 最大有效延迟
        result = self.ctb.register_event(hero, max_valid_time)
        self.assertTrue(result)

        # 超出容量
        result = self.ctb.register_event(hero, max_valid_time + 1)
        self.assertFalse(result)

    def test_rapid_time_advances(self):
        """测试快速时间推进"""
        # 添加事件在不同时间
        for i in range(5):
            event = Event(f"e{i}", f"事件{i}", EventType.CUSTOM, i * 100)
            self.ctb.register_event(event, i * 100)

        self.ctb._last_sync_time = 0

        # 快速推进
        total_triggered = 0
        for _ in range(5):
            events = self.ctb.advance_time(100)
            total_triggered += len(events)

        # 应该触发所有5个事件
        self.assertEqual(total_triggered, 5)
        self.assertEqual(self.time_manager._total_hours, 500)


def run_tests():
    """运行所有测试"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()