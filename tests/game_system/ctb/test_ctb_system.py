#!/usr/bin/env python3
"""
CTB系统测试用例

测试CTB系统的核心功能：
- 角色管理
- 事件系统
- 时间推进
- 随机行动间隔
- 状态管理
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from game_system.game_time import TimeManager
from game_system.ctb.ctb_system import CTBManager, Character, Event, EventType


class TestCharacter(unittest.TestCase):
    """测试角色类"""

    def test_character_creation(self):
        """测试角色创建"""
        char = Character("test1", "测试角色", "测试阵营")
        self.assertEqual(char.id, "test1")
        self.assertEqual(char.name, "测试角色")
        self.assertEqual(char.faction, "测试阵营")
        self.assertTrue(char.is_active)
        self.assertEqual(char.event_type, EventType.CHARACTER_ACTION)

    def test_character_defaults(self):
        """测试角色默认值"""
        char = Character("test2", "简单角色")
        self.assertEqual(char.faction, "中立")
        self.assertTrue(char.is_active)

    def test_calculate_next_action_time(self):
        """测试下次行动时间计算"""
        char = Character("test3", "测试角色")
        current_time = 1000

        # 测试多次计算，应该得到不同的随机值
        times = set()
        for _ in range(10):
            next_time = char.calculate_next_action_time(current_time)
            times.add(next_time - current_time)

        # 应该有多个不同的间隔
        self.assertGreater(len(times), 1)

        # 所有间隔应该在1-180天之间
        for interval in times:
            self.assertGreaterEqual(interval, 24)  # 至少1天
            self.assertLessEqual(interval, 180 * 24)  # 最多180天


class TestEvent(unittest.TestCase):
    """测试事件系统"""

    def test_event_creation(self):
        """测试事件创建"""
        event = Event("evt1", "测试事件", EventType.CUSTOM, 100, "这是一个测试事件")
        self.assertEqual(event.id, "evt1")
        self.assertEqual(event.name, "测试事件")
        self.assertEqual(event.event_type, EventType.CUSTOM)
        self.assertEqual(event.trigger_time, 100)
        self.assertEqual(event.description, "这是一个测试事件")

    def test_event_types(self):
        """测试事件类型"""
        # 角色事件
        char = Character("char1", "角色1")
        self.assertEqual(char.event_type, EventType.CHARACTER_ACTION)

        # 季节变化事件
        season = Event("season1", "春季", EventType.SEASON_CHANGE, 0)
        self.assertEqual(season.event_type, EventType.SEASON_CHANGE)

        # 自定义事件
        custom = Event("custom1", "节日", EventType.CUSTOM, 0)
        self.assertEqual(custom.event_type, EventType.CUSTOM)


class TestCTBManager(unittest.TestCase):
    """Tests for the CTBManager."""

    def setUp(self):
        """Set up a new CTBManager and characters for each test."""
        self.time_manager = TimeManager()
        self.ctb_manager = CTBManager(self.time_manager)
        self.char1 = Character("char1", "Hero")
        self.char2 = Character("char2", "Sidekick")
        # Mock the random time calculation for predictable testing
        self.char1.calculate_next_action_time = lambda t: t + 100
        self.char2.calculate_next_action_time = lambda t: t + 200

    def test_initial_state(self):
        """Test the initial state of the CTBManager."""
        self.assertEqual(len(self.ctb_manager.characters), 0)
        self.assertEqual(len(self.ctb_manager.time_wheel), 0)
        self.assertFalse(self.ctb_manager.is_initialized)

    def test_add_and_remove_character(self):
        """Test adding and removing characters."""
        self.ctb_manager.add_character(self.char1)
        self.assertIn("char1", self.ctb_manager.characters)
        self.assertEqual(len(self.ctb_manager.characters), 1)

        with self.assertRaises(ValueError):
            self.ctb_manager.add_character(self.char1)

        result = self.ctb_manager.remove_character("char1")
        self.assertTrue(result)
        self.assertNotIn("char1", self.ctb_manager.characters)
        self.assertFalse(self.ctb_manager.remove_character("nonexistent"))

    def test_initialize_ctb(self):
        """Test the initialization of the CTB system."""
        with self.assertRaises(ValueError):
            self.ctb_manager.initialize_ctb()

        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.add_character(self.char2)
        self.ctb_manager.initialize_ctb()

        self.assertTrue(self.ctb_manager.is_initialized)
        self.assertEqual(len(self.ctb_manager.time_wheel), 2)
        self.assertIn("char1", self.ctb_manager.time_wheel)
        self.assertIn("char2", self.ctb_manager.time_wheel)

    def test_register_event(self):
        """Test registering custom events."""
        event = Event("evt1", "A Special Thing", EventType.CUSTOM, 100)
        result = self.ctb_manager.register_event(event, 100)
        self.assertTrue(result)
        self.assertEqual(len(self.ctb_manager.time_wheel), 1)

        # Registering an event with a duplicate ID should fail
        event2 = Event("evt1", "Another Thing", EventType.CUSTOM, 200)
        result = self.ctb_manager.register_event(event2, 200)
        self.assertFalse(result)

        # Registering an event in the past should fail
        event3 = Event("evt3", "Past Thing", EventType.CUSTOM, -50)
        result = self.ctb_manager.register_event(event3, -50)
        self.assertFalse(result)

    def test_execute_next_action_single_event(self):
        """Test executing the next action when only one event is due."""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb() # Schedules char1 at t=100

        initial_time = self.time_manager._total_hours
        executed_events = self.ctb_manager.execute_next_action()
        self.assertEqual(len(executed_events), 1)
        self.assertEqual(executed_events[0].id, "char1")

        # Time should have advanced to 100, processed, then ticked to 101
        self.assertEqual(self.time_manager._total_hours, initial_time + 101)
        # char1 should have been rescheduled
        self.assertEqual(len(self.ctb_manager.time_wheel), 1)

    def test_execute_next_action_multiple_events_at_same_time(self):
        """Test executing actions when multiple events are due at the same time."""
        # Make both characters act at the same time
        self.char2.calculate_next_action_time = lambda t: t + 100
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.add_character(self.char2)
        self.ctb_manager.initialize_ctb() # Schedules both at t=100

        self.assertEqual(len(self.ctb_manager.time_wheel), 2)

        executed_events = self.ctb_manager.execute_next_action()

        # Should process both events in one call
        self.assertEqual(len(executed_events), 2)
        executed_ids = {e.id for e in executed_events}
        self.assertEqual(executed_ids, {"char1", "char2"})

        # Both characters should have been rescheduled
        self.assertEqual(len(self.ctb_manager.time_wheel), 2)

    def test_character_active_state(self):
        """Test activating and deactivating characters."""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()
        self.assertEqual(len(self.ctb_manager.time_wheel), 1)

        # Deactivating the character should remove them from the time wheel
        self.ctb_manager.set_character_active("char1", False)
        self.assertEqual(len(self.ctb_manager.time_wheel), 0)

        # Activating them again should reschedule them
        self.ctb_manager.set_character_active("char1", True)
        self.assertEqual(len(self.ctb_manager.time_wheel), 1)

    def test_get_action_list(self):
        """Test the structure of the data returned by get_action_list."""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()

        action_list = self.ctb_manager.get_action_list(5)
        self.assertEqual(len(action_list), 1)
        action = action_list[0]

        self.assertIn("id", action)
        self.assertIn("name", action)
        self.assertIn("type", action)
        self.assertIn("time_until", action)
        self.assertIn("trigger_time", action)
        self.assertEqual(action['id'], 'char1')
        self.assertEqual(action['time_until'], 100)


class TestCTBIntegration(unittest.TestCase):
    """CTB系统集成测试"""

    def setUp(self):
        """测试初始化"""
        self.time_manager = TimeManager()
        self.ctb_manager = CTBManager(self.time_manager)

        # 添加多个角色
        self.ctb_manager.add_character(Character("char1", "角色1"))
        self.ctb_manager.add_character(Character("char2", "角色2"))
        self.ctb_manager.add_character(Character("char3", "角色3"))

    def test_multiple_actions_sequence(self):
        """测试多个行动的执行序列"""
        self.ctb_manager.initialize_ctb()

        action_names = []
        for _ in range(10):
            actions = self.ctb_manager.execute_next_action()
            if actions:
                for action in actions:
                    action_names.append(action.name)
            else:
                break

        # We should have executed actions for both characters, but the exact order can vary.
        self.assertIn("角色1", action_names)
        self.assertIn("角色2", action_names)
        self.assertIn("角色3", action_names)

    def test_time_progression(self):
        """测试时间推进"""
        self.ctb_manager.initialize_ctb()

        initial_time = self.time_manager._total_hours

        # 执行多个行动
        for _ in range(5):
            self.ctb_manager.execute_next_action()

        final_time = self.time_manager._total_hours

        # 时间应该有显著推进
        self.assertGreater(final_time, initial_time)

    def test_mixed_events(self):
        """测试混合事件类型"""
        # 添加角色
        self.ctb_manager.initialize_ctb()

        # 创建一个测试事件类
        class TestEvent(Event):
            def execute(self):
                return self

        # 添加自定义事件
        current_time = self.time_manager._total_hours
        for i in range(3):
            event = TestEvent(f"custom{i}", f"自定义事件{i}", EventType.CUSTOM, 0)
            self.ctb_manager.register_event(event, current_time + (i + 1) * 50)

        # 执行一些行动，应该包含角色和自定义事件
        event_types = []
        for _ in range(10):
            events = self.ctb_manager.execute_next_action()
            if events:
                for event in events:
                    event_types.append(event.event_type)
            else:
                break

        self.assertIn(EventType.CHARACTER_ACTION, event_types)
        self.assertIn(EventType.CUSTOM, event_types)


def run_ctb_tests():
    """运行所有CTB测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    test_classes = [
        TestCharacter,
        TestEvent,
        TestCTBManager,
        TestCTBIntegration
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 50)
    print("CTB系统测试")
    print("=" * 50)

    success = run_ctb_tests()

    if success:
        print("\n✅ 所有CTB测试通过！")
    else:
        print("\n❌ 部分CTB测试失败")

    exit(0 if success else 1)