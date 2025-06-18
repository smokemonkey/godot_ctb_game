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
from typing import List, Tuple, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from game_system.calendar import Calendar
from game_system.ctb_manager.ctb_manager import CTBManager, Character, Event, EventType


class TestEventBase(unittest.TestCase):
    """测试事件基类"""

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

    def test_event_execute_not_implemented(self):
        """测试基类execute方法抛出NotImplementedError"""
        event = Event("evt1", "测试事件", EventType.CUSTOM, 0)
        with self.assertRaises(NotImplementedError):
            event.execute()


class MockEvent(Event):
    """测试用事件类"""

    def __init__(self, event_id: str, name: str, event_type: EventType = EventType.CUSTOM):
        super().__init__(event_id, name, event_type, 0)

    def execute(self):
        return f"执行了{self.name}"


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


class MockTimeWheel:
    """模拟时间轮用于测试"""

    def __init__(self):
        self.events = {}
        self.due_events = []

    def schedule_with_delay(self, key: str, event: Event, delay: int) -> bool:
        event.trigger_time = self.get_time() + delay
        self.events[key] = event
        return True

    def remove(self, key: str) -> bool:
        return self.events.pop(key, None) is not None

    def peek_upcoming_events(self, count: int, max_events: int) -> List[Tuple[str, Event]]:
        sorted_events = sorted(self.events.items(), key=lambda x: x[1].trigger_time)
        return sorted_events[:max_events]

    def pop_due_event(self) -> Optional[Tuple[str, Event]]:
        if self.due_events:
            return self.due_events.pop(0)
        return None

    def get_time(self) -> int:
        return 0

    def __len__(self):
        return len(self.events)


class TestCTBManager(unittest.TestCase):
    """Tests for the CTBManager."""

    def setUp(self):
        """Set up a new CTBManager and characters for each test."""
        self.calendar = Calendar()
        self.mock_time_wheel = MockTimeWheel()

        # 创建CTB管理器，使用模拟的回调函数
        self.ctb_manager = CTBManager(
            get_time_callback=lambda: self.calendar.get_timestamp(),
            schedule_callback=lambda key, event, delay: self.mock_time_wheel.schedule_with_delay(key, event, delay),
            remove_callback=lambda key: self.mock_time_wheel.remove(key),
            peek_callback=lambda count, max_events: self.mock_time_wheel.peek_upcoming_events(count, max_events),
            pop_callback=lambda: self.mock_time_wheel.pop_due_event()
        )

        self.char1 = Character("char1", "Hero")
        self.char2 = Character("char2", "Sidekick")
        # Mock the random time calculation for predictable testing
        self.char1.calculate_next_action_time = lambda t: t + 100
        self.char2.calculate_next_action_time = lambda t: t + 200

    def test_initial_state(self):
        """Test the initial state of the CTBManager."""
        self.assertEqual(len(self.ctb_manager.characters), 0)
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
        self.assertEqual(len(self.mock_time_wheel), 2)
        self.assertIn("char1", self.mock_time_wheel.events)
        self.assertIn("char2", self.mock_time_wheel.events)

    def test_schedule_event(self):
        """Test scheduling custom events."""
        event = MockEvent("evt1", "A Special Thing", EventType.CUSTOM)
        result = self.ctb_manager.schedule_event(event, 100)
        self.assertTrue(result)
        self.assertEqual(len(self.mock_time_wheel), 1)

        # Scheduling an event in the past should fail
        event3 = MockEvent("evt3", "Past Thing", EventType.CUSTOM)
        result = self.ctb_manager.schedule_event(event3, -50)
        self.assertFalse(result)

    def test_get_due_event(self):
        """Test getting due events."""
        # 添加一个到期事件到模拟时间轮
        event = MockEvent("evt1", "Due Event", EventType.CUSTOM)
        self.mock_time_wheel.due_events.append(("evt1", event))

        due_event = self.ctb_manager.get_due_event()
        self.assertIsNotNone(due_event)
        self.assertEqual(due_event.id, "evt1")

        # 没有更多到期事件
        due_event = self.ctb_manager.get_due_event()
        self.assertIsNone(due_event)

    def test_execute_events(self):
        """Test executing events."""
        event = MockEvent("evt1", "Test Event", EventType.CUSTOM)
        events = [event]

        # 添加事件到模拟时间轮以便重新调度
        self.mock_time_wheel.events["evt1"] = event

        self.ctb_manager.execute_events(events)

        # 应该记录了行动历史
        self.assertEqual(len(self.ctb_manager.action_history), 1)
        self.assertEqual(self.ctb_manager.action_history[0]['event_name'], "Test Event")

    def test_character_active_state(self):
        """Test activating and deactivating characters."""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()
        self.assertEqual(len(self.mock_time_wheel), 1)

        # Deactivating the character should remove them from the time wheel
        self.ctb_manager.set_character_active("char1", False)
        self.assertEqual(len(self.mock_time_wheel), 0)

        # Activating them again should reschedule them
        self.ctb_manager.set_character_active("char1", True)
        self.assertEqual(len(self.mock_time_wheel), 1)


class TestCTBIntegration(unittest.TestCase):
    """CTB系统集成测试"""

    def setUp(self):
        """测试初始化"""
        self.calendar = Calendar()
        self.mock_time_wheel = MockTimeWheel()

        self.ctb_manager = CTBManager(
            get_time_callback=lambda: self.calendar.get_timestamp(),
            schedule_callback=lambda key, event, delay: self.mock_time_wheel.schedule_with_delay(key, event, delay),
            remove_callback=lambda key: self.mock_time_wheel.remove(key),
            peek_callback=lambda count, max_events: self.mock_time_wheel.peek_upcoming_events(count, max_events),
            pop_callback=lambda: self.mock_time_wheel.pop_due_event()
        )

        # 添加多个角色
        self.ctb_manager.add_character(Character("char1", "角色1"))
        self.ctb_manager.add_character(Character("char2", "角色2"))
        self.ctb_manager.add_character(Character("char3", "角色3"))

    def test_multiple_actions_sequence(self):
        """测试多个行动的执行序列"""
        self.ctb_manager.initialize_ctb()

        # 模拟一些到期事件
        events = [
            MockEvent("evt1", "事件1", EventType.CUSTOM),
            MockEvent("evt2", "事件2", EventType.CUSTOM),
            MockEvent("evt3", "事件3", EventType.CUSTOM)
        ]

        for event in events:
            self.mock_time_wheel.due_events.append((event.id, event))

        # 获取并执行到期事件
        due_event = self.ctb_manager.get_due_event()
        self.assertIsNotNone(due_event)

        self.ctb_manager.execute_events([due_event])
        self.assertEqual(len(self.ctb_manager.action_history), 1)

    def test_schedule_with_delay(self):
        """测试使用延迟时间调度事件"""
        event = MockEvent("evt1", "Delayed Event", EventType.CUSTOM)
        result = self.ctb_manager.schedule_with_delay("evt1", event, 50)
        self.assertTrue(result)
        self.assertEqual(len(self.mock_time_wheel), 1)
        self.assertIn("evt1", self.mock_time_wheel.events)


class SeasonChangeEvent(Event):
    """季节变化事件"""

    def __init__(self, season_name: str, next_season_days: int = 90):
        """
        初始化季节变化事件

        Args:
            season_name: 季节名称
            next_season_days: 下一个季节的天数后
        """
        super().__init__(
            id=f"season_{season_name}",
            name=f"{season_name}季到来",
            event_type=EventType.SEASON_CHANGE,
            trigger_time=0,  # 将在注册时设置
            description=f"季节变化：进入{season_name}季"
        )
        self.season_name = season_name
        self.next_season_days = next_season_days

    def execute(self) -> None:
        """执行季节变化"""
        # 在测试中不打印，只返回执行结果
        return f"季节变化：{self.season_name}季到来了！"


class CustomEvent(Event):
    """自定义事件示例 - 节日"""

    def __init__(self, festival_name: str, callback=None):
        super().__init__(
            id=f"festival_{festival_name}",
            name=f"{festival_name}节",
            event_type=EventType.CUSTOM,
            trigger_time=0,
            description=f"节日庆典：{festival_name}节"
        )
        self.festival_name = festival_name
        self.callback = callback

    def execute(self) -> None:
        """执行节日事件"""
        result = f"节日：{self.festival_name}节到了！全民欢庆！"
        if self.callback:
            self.callback(self)
        return result


class TestCTBEventExamples(unittest.TestCase):
    """测试CTB系统事件示例功能"""

    def setUp(self):
        """测试初始化"""
        self.calendar = Calendar()
        self.mock_time_wheel = MockTimeWheel()

        self.ctb_manager = CTBManager(
            get_time_callback=lambda: self.calendar.get_timestamp(),
            schedule_callback=lambda key, event, delay: self.mock_time_wheel.schedule_with_delay(key, event, delay),
            remove_callback=lambda key: self.mock_time_wheel.remove(key),
            peek_callback=lambda count, max_events: self.mock_time_wheel.peek_upcoming_events(count, max_events),
            pop_callback=lambda: self.mock_time_wheel.pop_due_event()
        )

    def test_season_change_event(self):
        """测试季节变化事件"""
        # 创建季节变化事件
        spring_event = SeasonChangeEvent("春")
        self.assertEqual(spring_event.season_name, "春")
        self.assertEqual(spring_event.event_type, EventType.SEASON_CHANGE)

        # 测试执行
        result = spring_event.execute()
        self.assertIn("春季到来了", result)

    def test_custom_festival_event(self):
        """测试自定义节日事件"""
        # 创建节日事件
        festival_event = CustomEvent("春节")
        self.assertEqual(festival_event.festival_name, "春节")
        self.assertEqual(festival_event.event_type, EventType.CUSTOM)

        # 测试执行
        result = festival_event.execute()
        self.assertIn("春节节到了", result)

    def test_complex_event_integration(self):
        """测试复杂事件集成场景"""
        # 添加角色
        characters = [
            Character("warrior", "战士", faction="王国"),
            Character("mage", "法师", faction="魔法学院"),
            Character("rogue", "盗贼", faction="盗贼公会")
        ]

        for char in characters:
            self.ctb_manager.add_character(char)

        # 注册季节变化事件
        spring_event = SeasonChangeEvent("春")
        self.ctb_manager.schedule_event(spring_event, self.calendar.get_timestamp() + 24)

        # 注册节日事件
        festival_event = CustomEvent("春节")
        self.ctb_manager.schedule_event(festival_event, self.calendar.get_timestamp() + 30 * 24)

        # 初始化CTB系统
        self.ctb_manager.initialize_ctb()

        # 验证事件总数
        self.assertEqual(len(self.mock_time_wheel), 5)  # 3个角色 + 2个自定义事件

        # 模拟执行事件
        test_event = MockEvent("test", "Test", EventType.CUSTOM)
        self.ctb_manager.execute_events([test_event])

        # 验证时间推进
        self.assertGreater(len(self.ctb_manager.action_history), 0)

    def test_event_execution_sequence(self):
        """测试事件执行序列"""
        # 添加角色
        char = Character("test_char", "测试角色")
        self.ctb_manager.add_character(char)

        # 注册自定义事件
        event1 = CustomEvent("事件1")
        event2 = CustomEvent("事件2")

        # 注册事件，确保执行顺序
        self.ctb_manager.schedule_event(event1, self.calendar.get_timestamp() + 10)
        self.ctb_manager.schedule_event(event2, self.calendar.get_timestamp() + 20)

        self.ctb_manager.initialize_ctb()

        # 执行事件并验证
        test_event = MockEvent("test", "Test", EventType.CUSTOM)
        self.ctb_manager.execute_events([test_event])

        # 验证事件历史记录
        self.assertGreater(len(self.ctb_manager.action_history), 0)


def run_ctb_tests():
    """运行所有CTB测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    test_classes = [
        TestCharacter,
        TestEventBase,
        TestCTBManager,
        TestCTBIntegration,
        TestCTBEventExamples
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_ctb_tests()
    sys.exit(0 if success else 1)