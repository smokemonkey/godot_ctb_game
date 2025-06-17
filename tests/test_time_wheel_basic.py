#!/usr/bin/env python3
"""
时间轮基础功能测试

这些测试用于验证时间轮的核心行为，特别是：
- 槽位和offset的关系
- 事件触发时机
- 环形缓冲区行为
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from ctb import TimeWheel


class TestTimeWheelBasics(unittest.TestCase):
    """时间轮基础行为测试"""

    def test_slot_and_offset_relationship(self):
        """测试槽位和offset的关系"""
        wheel = TimeWheel[str](10)

        # 添加事件到延迟5（槽位5）
        wheel.add("E", 5)

        # 验证初始状态
        self.assertEqual(wheel.current_offset, 0)
        self.assertEqual(wheel.get_next_event_delay(), 5)

        # 逐步推进，观察延迟变化
        for expected_delay in [4, 3, 2, 1, 0]:
            wheel.advance(1)
            if expected_delay > 0:
                self.assertEqual(wheel.get_next_event_delay(), expected_delay)

        # 在延迟为0时，再推进1应该触发事件
        events = wheel.advance(1)
        self.assertEqual(events, ["E"])
        self.assertIsNone(wheel.get_next_event_delay())

    def test_event_trigger_timing(self):
        """测试事件触发时机"""
        wheel = TimeWheel[str](24)
        wheel.add("event", 23)

        # offset=0，事件在槽位23
        # 推进23会让offset=23，但还没处理槽位23
        events = wheel.advance(23)
        self.assertEqual(events, [])
        self.assertEqual(wheel.current_offset, 23)

        # 需要再推进1才能处理槽位23
        events = wheel.advance(1)
        self.assertEqual(events, ["event"])
        self.assertEqual(wheel.current_offset, 0)  # 环形回到0

    def test_circular_wraparound(self):
        """测试环形缓冲区的回绕行为"""
        wheel = TimeWheel[int](5)

        # 在每个槽位添加事件
        for i in range(5):
            wheel.add(i, i)

        # 推进超过轮子大小
        events = wheel.advance(7)  # 推进7，应该触发所有事件
        self.assertEqual(sorted(events), [0, 1, 2, 3, 4])
        self.assertEqual(wheel.current_offset, 2)  # 7 % 5 = 2

        # 再次添加事件
        wheel.add(100, 0)  # 在当前位置（槽位2）
        wheel.add(200, 3)  # 在槽位 (2+3)%5 = 0

        # 验证事件位置
        self.assertEqual(wheel.get_next_event_delay(), 0)
        events = wheel.advance(1)
        self.assertEqual(events, [100])

        events = wheel.advance(3)
        self.assertEqual(events, [200])

    def test_boundary_conditions(self):
        """测试边界条件"""
        wheel = TimeWheel[str](100)

        # 测试最大延迟
        self.assertTrue(wheel.add("A", 99))   # 最大有效延迟
        self.assertFalse(wheel.add("B", 100)) # 超出范围

        # 测试延迟0
        self.assertTrue(wheel.add("C", 0))    # 当前槽位

        # 验证事件数量
        self.assertEqual(wheel.total_events(), 2)

        # 测试get_next_event_delay
        self.assertEqual(wheel.get_next_event_delay(), 0)  # "C"在当前位置

        # 触发"C"
        events = wheel.advance(1)
        self.assertEqual(events, ["C"])

        # 现在下一个事件是"A"，在99-1=98的位置
        self.assertEqual(wheel.get_next_event_delay(), 98)

    def test_multiple_advances_accuracy(self):
        """测试多次推进的准确性"""
        wheel = TimeWheel[str](50)

        # 添加多个事件
        test_events = [
            ("E1", 10),
            ("E2", 20),
            ("E3", 30),
            ("E4", 40)
        ]

        for name, delay in test_events:
            wheel.add(name, delay)

        # 分步推进
        all_triggered = []

        # 推进15，应该触发E1
        events = wheel.advance(15)
        all_triggered.extend(events)
        self.assertEqual(events, ["E1"])

        # 推进10，应该触发E2
        events = wheel.advance(10)
        all_triggered.extend(events)
        self.assertEqual(events, ["E2"])

        # 推进20，应该触发E3和E4
        events = wheel.advance(20)
        all_triggered.extend(events)
        self.assertEqual(sorted(events), ["E3", "E4"])

        # 验证所有事件都被触发
        self.assertEqual(sorted(all_triggered), ["E1", "E2", "E3", "E4"])
        self.assertTrue(wheel.is_empty())


class TestTimeWheelEdgeCases(unittest.TestCase):
    """时间轮边缘情况测试"""

    def test_advance_zero(self):
        """测试推进0的行为"""
        wheel = TimeWheel[str](10)
        wheel.add("A", 0)
        wheel.add("B", 1)

        # 推进0不应该触发任何事件
        events = wheel.advance(0)
        self.assertEqual(events, [])
        self.assertEqual(wheel.total_events(), 2)

        # offset也不应该改变
        self.assertEqual(wheel.current_offset, 0)

    def test_large_advance(self):
        """测试大幅度推进"""
        wheel = TimeWheel[int](10)

        # 添加事件
        for i in range(5):
            wheel.add(i, i * 2)  # 0在0，1在2，2在4，3在6，4在8

        # 推进超过轮子大小的两倍
        events = wheel.advance(25)

        # 所有事件都应该被触发
        self.assertEqual(sorted(events), [0, 1, 2, 3, 4])
        self.assertTrue(wheel.is_empty())
        self.assertEqual(wheel.current_offset, 5)  # 25 % 10 = 5

    def test_single_slot_multiple_events_order(self):
        """测试单个槽位多个事件的顺序"""
        wheel = TimeWheel[str](10)

        # 在同一槽位添加多个事件
        # 由于是链表头插入，后添加的会先被触发
        wheel.add("First", 5)
        wheel.add("Second", 5)
        wheel.add("Third", 5)

        events = wheel.advance(6)

        # 验证所有事件都被触发
        self.assertEqual(len(events), 3)
        self.assertIn("First", events)
        self.assertIn("Second", events)
        self.assertIn("Third", events)

        # 注意：由于链表实现，顺序是反的
        self.assertEqual(events[0], "Third")   # 最后添加的先触发
        self.assertEqual(events[1], "Second")
        self.assertEqual(events[2], "First")


def run_tests():
    """运行所有测试"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()