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

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_time import TimeManager
from ctb import CTBManager, Character, Event, EventType


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
    """测试CTB管理器"""

    def setUp(self):
        """测试初始化"""
        self.time_manager = TimeManager()
        self.ctb_manager = CTBManager(self.time_manager)

        # 创建测试角色
        self.char1 = Character("char1", "张三")
        self.char2 = Character("char2", "李四")
        self.char3 = Character("char3", "王五")

    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(len(self.ctb_manager.characters), 0)
        self.assertEqual(self.ctb_manager.time_wheel.total_events(), 0)
        self.assertFalse(self.ctb_manager.is_initialized)

    def test_add_character(self):
        """测试添加角色"""
        self.ctb_manager.add_character(self.char1)
        self.assertEqual(len(self.ctb_manager.characters), 1)

        # 添加重复ID应该抛出异常
        with self.assertRaises(ValueError):
            self.ctb_manager.add_character(self.char1)

    def test_remove_character(self):
        """测试移除角色"""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.add_character(self.char2)

        # 移除存在的角色
        result = self.ctb_manager.remove_character("char1")
        self.assertTrue(result)
        self.assertEqual(len(self.ctb_manager.characters), 1)

        # 移除不存在的角色
        result = self.ctb_manager.remove_character("nonexistent")
        self.assertFalse(result)

    def test_get_character(self):
        """测试获取角色"""
        self.ctb_manager.add_character(self.char1)

        char = self.ctb_manager.get_character("char1")
        self.assertIsNotNone(char)
        self.assertEqual(char.name, "张三")

        char = self.ctb_manager.get_character("nonexistent")
        self.assertIsNone(char)

    def test_initialize_ctb(self):
        """测试CTB初始化"""
        # 没有角色时初始化应该失败
        with self.assertRaises(ValueError):
            self.ctb_manager.initialize_ctb()

        # 添加角色后初始化
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.add_character(self.char2)
        self.ctb_manager.initialize_ctb()

        self.assertTrue(self.ctb_manager.is_initialized)
        self.assertEqual(self.ctb_manager.time_wheel.total_events(), 2)

    def test_register_event(self):
        """测试事件注册"""
        # 注册一个自定义事件
        event = Event("evt1", "测试事件", EventType.CUSTOM, 100)
        result = self.ctb_manager.register_event(event, 100)
        self.assertTrue(result)

        # 注册超出范围的事件
        far_event = Event("evt2", "远期事件", EventType.CUSTOM, 10000)
        result = self.ctb_manager.register_event(far_event, 10000)
        self.assertFalse(result)

    def test_execute_next_action(self):
        """测试执行下一个行动"""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()

        # 记录初始时间
        initial_time = self.time_manager._total_hours

        # 执行行动
        action = self.ctb_manager.execute_next_action()
        self.assertIsNotNone(action)
        self.assertEqual(action.name, "张三")

        # 时间应该已推进
        self.assertGreater(self.time_manager._total_hours, initial_time)

        # 应该有新的行动安排（角色会自动安排下次行动）
        self.assertEqual(self.ctb_manager.time_wheel.total_events(), 1)

    def test_character_active_state(self):
        """测试角色活跃状态"""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.add_character(self.char2)
        self.ctb_manager.initialize_ctb()

        # 初始状态：2个活跃角色，2个行动
        self.assertEqual(self.ctb_manager.time_wheel.total_events(), 2)

        # 停用一个角色
        result = self.ctb_manager.set_character_active("char1", False)
        self.assertTrue(result)
        self.assertEqual(self.ctb_manager.time_wheel.total_events(), 1)

        # 重新激活角色
        result = self.ctb_manager.set_character_active("char1", True)
        self.assertTrue(result)
        self.assertEqual(self.ctb_manager.time_wheel.total_events(), 2)

        # 操作不存在的角色
        result = self.ctb_manager.set_character_active("nonexistent", False)
        self.assertFalse(result)

    def test_action_history(self):
        """测试行动历史"""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()

        # 执行几个行动
        for _ in range(3):
            self.ctb_manager.execute_next_action()

        # 检查历史记录
        history = self.ctb_manager.action_history
        self.assertEqual(len(history), 3)

        # 验证历史记录内容
        for record in history:
            self.assertIn('event_name', record)
            self.assertIn('timestamp', record)
            self.assertIn('year', record)

    def test_get_action_list(self):
        """测试获取行动列表"""
        # 添加多个角色和事件
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.add_character(self.char2)

        # 注册一些自定义事件
        for i in range(5):
            event = Event(f"evt{i}", f"事件{i}", EventType.CUSTOM, i * 100)
            self.ctb_manager.register_event(event, i * 100)

        self.ctb_manager.initialize_ctb()

        # 获取行动列表
        action_list = self.ctb_manager.get_action_list(10)
        self.assertGreater(len(action_list), 0)

        # 验证列表内容
        for action in action_list:
            self.assertIn('event_name', action)
            self.assertIn('event_type', action)
            self.assertIn('hours_from_now', action)
            self.assertIn('days_from_now', action)

    def test_get_status_info(self):
        """测试状态信息获取"""
        # 未初始化状态
        status = self.ctb_manager.get_status_text()
        self.assertIn("未初始化", status)

        # 初始化后状态
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()

        status = self.ctb_manager.get_status_text()
        self.assertIn("时间轮大小", status)
        self.assertIn("活跃角色", status)

        # 角色信息
        char_info = self.ctb_manager.get_character_info()
        self.assertEqual(len(char_info), 1)
        self.assertEqual(char_info[0]['name'], "张三")


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
            action = self.ctb_manager.execute_next_action()
            if action:
                action_names.append(action.name)

        # 应该有10个行动
        self.assertEqual(len(action_names), 10)

        # 每个角色都应该行动过
        unique_names = set(action_names)
        self.assertIn("角色1", unique_names)
        self.assertIn("角色2", unique_names)
        self.assertIn("角色3", unique_names)

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
            event = self.ctb_manager.execute_next_action()
            if event:
                event_types.append(event.event_type)

        # 应该有两种类型的事件
        unique_types = set(event_types)
        self.assertIn(EventType.CHARACTER_ACTION, unique_types)
        self.assertIn(EventType.CUSTOM, unique_types)


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