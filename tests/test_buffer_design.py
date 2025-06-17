#!/usr/bin/env python3
"""
测试CTB系统的buffer设计

验证时间轮的当前槽位作为"当前回合行动buffer"的设计是否正确工作。

测试要点：
1. 游戏开始时，时间轮未转动
2. 当前槽位的事件立即执行
3. 执行完当前槽位所有事件后，时间才推进
4. 多个事件在同一时间触发时的处理

最后更新: 2024-12-17
"""

import unittest
import sys
import os
import random

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_time import TimeManager
from ctb import CTBManager, Character, Event, EventType


class TestEvent(Event):
    """测试用的事件类"""
    def execute(self):
        """简单的执行方法"""
        return self


class TestCharacter(Character):
    """测试用的角色类，使用固定的行动间隔"""
    def __init__(self, id: str, name: str, faction: str = "中立", interval_days: int = 10):
        super().__init__(id, name, faction)
        self.interval_days = interval_days

    def calculate_next_action_time(self, current_time: int) -> int:
        """使用固定间隔而不是随机"""
        hours = self.interval_days * 24
        return current_time + hours


class TestBufferDesign(unittest.TestCase):
    """测试buffer设计的核心功能"""

    def setUp(self):
        """测试初始化"""
        self.time_manager = TimeManager()
        self.ctb_manager = CTBManager(self.time_manager)

        # 创建测试角色（使用固定间隔）
        self.char1 = TestCharacter("char1", "角色1", interval_days=5)
        self.char2 = TestCharacter("char2", "角色2", interval_days=5)
        self.char3 = TestCharacter("char3", "角色3", interval_days=5)

    def test_initial_state_no_rotation(self):
        """测试初始状态：时间轮未转动"""
        # 添加角色但不初始化
        self.ctb_manager.add_character(self.char1)

        # 检查时间轮偏移
        self.assertEqual(self.ctb_manager.time_wheel.offset, 0)
        self.assertEqual(self.time_manager._total_hours, 0)

        # 初始化CTB
        self.ctb_manager.initialize_ctb()

        # 时间轮仍然应该在位置0
        self.assertEqual(self.ctb_manager.time_wheel.offset, 0)
        self.assertEqual(self.time_manager._total_hours, 0)

    def test_current_buffer_immediate_execution(self):
        """测试当前buffer中的事件立即执行"""
        # 创建一个立即执行的事件
        immediate_event = TestEvent("evt1", "立即事件", EventType.CUSTOM, 0)

        # 注册到当前时间（delay=0）
        current_time = self.time_manager._total_hours
        self.ctb_manager.register_event(immediate_event, current_time)

        # 检查当前buffer
        current_buffer = self.ctb_manager.time_wheel.get_current_buffer()
        self.assertEqual(len(current_buffer), 1)
        self.assertEqual(current_buffer[0].id, "evt1")

        # 执行下一个行动应该立即执行这个事件
        self.ctb_manager.is_initialized = True  # 手动设置为已初始化
        executed = self.ctb_manager.execute_next_action()

        self.assertIsNotNone(executed)
        self.assertEqual(executed.id, "evt1")

        # 时间不应该推进
        self.assertEqual(self.time_manager._total_hours, 0)

    def test_multiple_events_same_slot(self):
        """测试同一槽位多个事件的处理"""
        self.ctb_manager.is_initialized = True

        # 创建多个在同一时间触发的事件
        events = []
        for i in range(3):
            event = TestEvent(f"evt{i}", f"事件{i}", EventType.CUSTOM, 100)
            events.append(event)
            self.ctb_manager.register_event(event, 100)

        # 推进到事件触发时间
        initial_time = self.time_manager._total_hours

        # 执行第一个事件
        executed1 = self.ctb_manager.execute_next_action()
        self.assertIsNotNone(executed1)
        self.assertIn(executed1.id, ["evt0", "evt1", "evt2"])

        # 时间应该已经推进到100
        self.assertEqual(self.time_manager._total_hours, 100)

        # 其余事件应该在当前buffer中
        current_buffer = self.ctb_manager.time_wheel.get_current_buffer()
        self.assertEqual(len(current_buffer), 2)

        # 执行剩余事件时，时间不应该再推进
        executed2 = self.ctb_manager.execute_next_action()
        self.assertIsNotNone(executed2)
        self.assertEqual(self.time_manager._total_hours, 100)  # 时间保持不变

        executed3 = self.ctb_manager.execute_next_action()
        self.assertIsNotNone(executed3)
        self.assertEqual(self.time_manager._total_hours, 100)  # 时间仍然保持不变

    def test_time_advances_after_buffer_empty(self):
        """测试只有在buffer清空后时间才推进"""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()

        # 记录初始时间
        initial_time = self.time_manager._total_hours

        # 第一次执行
        executed1 = self.ctb_manager.execute_next_action()
        self.assertIsNotNone(executed1)

        # 时间应该推进了（5天 = 120小时）
        time_after_first = self.time_manager._total_hours
        self.assertEqual(time_after_first, 120)

        # 角色会自动安排下次行动
        # 再次执行应该推进到下一个事件
        executed2 = self.ctb_manager.execute_next_action()
        self.assertIsNotNone(executed2)

        time_after_second = self.time_manager._total_hours
        self.assertEqual(time_after_second, 240)  # 又推进了5天

    def test_buffer_design_with_characters(self):
        """测试角色行动的buffer设计"""
        # 创建有不同间隔的角色
        char_a = TestCharacter("a", "角色A", interval_days=10)
        char_b = TestCharacter("b", "角色B", interval_days=10)  # 同样10天
        char_c = TestCharacter("c", "角色C", interval_days=15)

        self.ctb_manager.add_character(char_a)
        self.ctb_manager.add_character(char_b)
        self.ctb_manager.add_character(char_c)

        # 初始化
        self.ctb_manager.initialize_ctb()

        # 记录每次执行的时间
        execution_times = []

        # 执行10个行动
        for i in range(10):
            current_time = self.time_manager._total_hours
            action = self.ctb_manager.execute_next_action()

            if action:
                execution_times.append({
                    'action': action.name,
                    'time': current_time,
                    'time_advanced': self.time_manager._total_hours - current_time
                })

        # 验证时间推进模式
        same_time_count = 0
        for i, record in enumerate(execution_times):
            if i > 0:
                # 如果时间与前一个事件相同，说明是从buffer中执行的
                if record['time'] == execution_times[i-1]['time']:
                    same_time_count += 1

        # char_a和char_b应该在同一时间（240小时）第一次相遇
        # 所以应该至少有一次同时间执行
        self.assertGreater(same_time_count, 0)

    def test_get_next_event_delay_with_buffer(self):
        """测试get_next_event_delay在buffer设计下的行为"""
        # 添加一个立即执行的事件
        immediate_event = TestEvent("now", "现在", EventType.CUSTOM, 0)
        self.ctb_manager.register_event(immediate_event, 0)

        # get_next_event_delay应该返回0
        delay = self.ctb_manager.time_wheel.get_next_event_delay()
        self.assertEqual(delay, 0)

        # 清空当前buffer
        self.ctb_manager.time_wheel.clear_current_buffer()

        # 添加一个未来的事件
        future_event = TestEvent("future", "未来", EventType.CUSTOM, 100)
        self.ctb_manager.register_event(future_event, 100)

        # get_next_event_delay应该返回100
        delay = self.ctb_manager.time_wheel.get_next_event_delay()
        self.assertEqual(delay, 100)


class TestBufferEdgeCases(unittest.TestCase):
    """测试buffer设计的边界情况"""

    def setUp(self):
        """测试初始化"""
        self.time_manager = TimeManager()
        self.ctb_manager = CTBManager(self.time_manager)

    def test_empty_buffer_behavior(self):
        """测试空buffer的行为"""
        self.ctb_manager.is_initialized = True

        # 没有任何事件时执行
        result = self.ctb_manager.execute_next_action()
        self.assertIsNone(result)

        # 时间不应该推进
        self.assertEqual(self.time_manager._total_hours, 0)

    def test_buffer_overflow_handling(self):
        """测试大量事件在同一时间的处理"""
        self.ctb_manager.is_initialized = True

        # 创建100个同时触发的事件
        event_count = 100
        for i in range(event_count):
            event = TestEvent(f"evt{i}", f"事件{i}", EventType.CUSTOM, 1000)
            self.ctb_manager.register_event(event, 1000)

        # 执行所有事件
        executed_count = 0
        last_time = self.time_manager._total_hours

        while True:
            action = self.ctb_manager.execute_next_action()
            if not action:
                break

            executed_count += 1

            # 前100个事件执行时，时间应该保持在1000
            if executed_count <= event_count:
                if self.time_manager._total_hours >= 1000:
                    # 确保我们在正确的时间点
                    self.assertEqual(self.time_manager._total_hours, 1000)

            # 防止无限循环
            if executed_count > event_count + 10:
                break

        # 应该执行了所有事件
        self.assertEqual(executed_count, event_count)


def run_buffer_tests():
    """运行所有buffer设计测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestBufferDesign,
        TestBufferEdgeCases
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 50)
    print("CTB Buffer设计测试")
    print("=" * 50)

    success = run_buffer_tests()

    if success:
        print("\n✅ 所有Buffer设计测试通过！")
    else:
        print("\n❌ 部分Buffer设计测试失败")

    exit(0 if success else 1)