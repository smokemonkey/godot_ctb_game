#!/usr/bin/env python3
"""
时间轮与时间系统集成测试

重点测试：
1. 时间轮的基本功能
2. 与时间系统的同步
3. 边界条件和off-by-one错误
4. 索引功能的正确性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from game_time import TimeManager, TimeUnit
from ctb import CTBManager, Character, Event, EventType, TimeWheel, IndexedTimeWheel


class TestTimeWheel(unittest.TestCase):
    """时间轮基础功能测试"""

    def test_basic_operations(self):
        """测试基本的添加和推进操作"""
        wheel = TimeWheel[str](24)

        # 添加事件
        self.assertTrue(wheel.add("event1", 0))  # 当前时间
        self.assertTrue(wheel.add("event2", 5))  # 5小时后
        self.assertTrue(wheel.add("event3", 23)) # 23小时后
        self.assertFalse(wheel.add("event4", 24)) # 超出范围

        # 测试总事件数
        self.assertEqual(wheel.total_events(), 3)

        # 推进0小时，不应该触发任何事件
        events = wheel.advance(0)
        self.assertEqual(events, [])

        # 推进1小时，应该触发第一个事件（在槽位0）
        events = wheel.advance(1)
        self.assertEqual(events, ["event1"])
        self.assertEqual(wheel.total_events(), 2)

        # 推进5小时，应该触发第二个事件
        events = wheel.advance(5)
        self.assertEqual(events, ["event2"])

        # 推进18小时到达并触发event3
        events = wheel.advance(18)
        self.assertEqual(events, ["event3"])

        # 确认时间轮为空
        self.assertTrue(wheel.is_empty())

    def test_multiple_events_same_slot(self):
        """测试同一时间槽的多个事件"""
        wheel = TimeWheel[str](10)

        # 在同一时间添加多个事件
        wheel.add("A", 5)
        wheel.add("B", 5)
        wheel.add("C", 5)

        # 推进到该时间
        events = wheel.advance(6)  # 推进6个单位来触发位置5的事件

        # 应该包含所有三个事件（顺序可能不同）
        self.assertEqual(len(events), 3)
        self.assertIn("A", events)
        self.assertIn("B", events)
        self.assertIn("C", events)

    def test_circular_behavior(self):
        """测试环形行为"""
        wheel = TimeWheel[int](10)

        # 添加事件
        for i in range(10):
            wheel.add(i, i)

        # 推进5个单位
        events = wheel.advance(5)
        self.assertEqual(sorted(events), [0, 1, 2, 3, 4])

        # 当前offset应该是5
        self.assertEqual(wheel.current_offset, 5)

        # 在位置0添加新事件（实际是槽位5）
        wheel.add(100, 0)

        # 立即推进应该触发
        events = wheel.advance(1)
        self.assertEqual(events, [100, 5])  # 100是新添加的，5是原来的

    def test_peek_functionality(self):
        """测试peek功能"""
        wheel = TimeWheel[str](20)

        wheel.add("A", 1)
        wheel.add("B", 5)
        wheel.add("C", 10)

        # Peek不应该移除事件
        peeked = wheel.peek(0, 6)
        self.assertEqual(len(peeked), 2)  # A和B

        # 事件仍然存在
        self.assertEqual(wheel.total_events(), 3)

        # Peek特定范围
        peeked = wheel.peek(5, 6)
        self.assertEqual(peeked, ["B", "C"])

    def test_next_event_delay(self):
        """测试获取下一个事件延迟"""
        wheel = TimeWheel[str](100)

        # 空轮
        self.assertIsNone(wheel.get_next_event_delay())

        # 添加事件
        wheel.add("A", 10)
        wheel.add("B", 20)

        self.assertEqual(wheel.get_next_event_delay(), 10)

        # 推进后
        wheel.advance(15)
        self.assertEqual(wheel.get_next_event_delay(), 5)  # B在20，已推进15


class TestIndexedTimeWheel(unittest.TestCase):
    """带索引的时间轮测试"""

    def test_indexed_operations(self):
        """测试索引功能"""
        # 使用字典作为事件，按id索引
        wheel = IndexedTimeWheel[dict](50, key_func=lambda x: x['id'])

        event1 = {'id': 'player1', 'action': 'attack'}
        event2 = {'id': 'player1', 'action': 'defend'}
        event3 = {'id': 'player2', 'action': 'heal'}

        wheel.add(event1, 10)
        wheel.add(event2, 20)
        wheel.add(event3, 15)

        # 测试按键获取
        player1_events = wheel.get_events_by_key('player1')
        self.assertEqual(len(player1_events), 2)
        self.assertEqual(player1_events[0][1], 10)  # 第一个事件延迟10
        self.assertEqual(player1_events[1][1], 20)  # 第二个事件延迟20

        # 测试按键删除
        removed = wheel.remove_by_key('player1')
        self.assertEqual(removed, 2)
        self.assertEqual(wheel.total_events(), 1)

        # 确认只剩player2的事件
        events = wheel.advance(16)  # 推进16来触发位置15的事件
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['id'], 'player2')

    def test_index_update_on_advance(self):
        """测试推进时索引的更新"""
        wheel = IndexedTimeWheel[str](20, key_func=lambda x: x[0])  # 按首字母索引

        wheel.add("A1", 5)
        wheel.add("A2", 10)
        wheel.add("B1", 5)

        # 推进6个单位来触发位置5的事件
        events = wheel.advance(6)
        self.assertEqual(len(events), 2)  # A1和B1

        # 检查索引是否正确更新
        a_events = wheel.get_events_by_key('A')
        self.assertEqual(len(a_events), 1)  # 只剩A2
        self.assertEqual(a_events[0][1], 4)  # 延迟从10变成4（10-6）


class TestCTBTimeWheelIntegration(unittest.TestCase):
    """CTB系统与时间轮集成测试"""

    def setUp(self):
        """初始化测试环境"""
        self.time_manager = TimeManager()
        self.ctb = CTBManager(self.time_manager)

    def test_basic_integration(self):
        """测试基本集成功能"""
        # 添加角色
        hero = Character("hero", "英雄")
        enemy = Character("enemy", "敌人")

        self.ctb.add_character(hero)
        self.ctb.add_character(enemy)

        # 初始化
        self.ctb.initialize_ctb()

        # 应该有2个事件在时间轮中
        self.assertEqual(self.ctb.time_wheel.total_events(), 2)

        # 获取下一个事件的延迟
        next_delay = self.ctb.time_wheel.get_next_event_delay()
        self.assertIsNotNone(next_delay)

        # 执行第一个行动
        event = self.ctb.execute_next_action()
        self.assertIsNotNone(event)
        self.assertIsInstance(event, Character)

        # 该角色应该安排了下一次行动，所以还是2个事件
        self.assertEqual(self.ctb.time_wheel.total_events(), 2)

    def test_time_sync_accuracy(self):
        """测试时间同步的准确性"""
        # 添加一个角色
        hero = Character("hero", "英雄")
        self.ctb.add_character(hero)

        # 手动注册一个事件在10小时后
        current_time = self.time_manager._total_hours
        self.ctb.register_event(hero, current_time + 10)
        self.ctb._last_sync_time = current_time  # 确保同步

        # 记录初始状态
        initial_time = self.time_manager._total_hours

        # 推进11小时来触发延迟10的事件
        events = self.ctb.advance_time(11)
        self.assertEqual(len(events), 1)
        self.assertEqual(self.time_manager._total_hours, initial_time + 11)
        self.assertEqual(len(self.ctb.action_history), 1)

    def test_off_by_one_scenarios(self):
        """测试各种off-by-one场景"""
        # 场景1：在延迟0注册事件（当前槽位）
        hero = Character("hero", "英雄")
        self.ctb.add_character(hero)

        current_time = self.time_manager._total_hours
        self.ctb.register_event(hero, current_time)  # 当前时间
        self.ctb._last_sync_time = current_time  # 确保同步

        # 延迟0意味着事件在当前槽位，需要推进1才能触发
        events = self.ctb.advance_time(1)
        self.assertEqual(len(events), 1)

        # 场景2：在延迟1注册事件
        self.ctb.time_wheel.clear()
        current_time = self.time_manager._total_hours
        self.ctb._last_sync_time = current_time  # 重新同步
        self.ctb.register_event(hero, current_time + 1)

        # 推进2小时来触发延迟1的事件
        events = self.ctb.advance_time(2)
        self.assertEqual(len(events), 1)

        # 场景3：边界测试
        self.ctb.time_wheel.clear()
        self.ctb._last_sync_time = self.time_manager._total_hours  # 重新同步
        current_time = self.time_manager._total_hours
        max_delay = CTBManager.TIME_WHEEL_SIZE - 1

        # 注册在最大延迟
        result = self.ctb.register_event(hero, current_time + max_delay)
        self.assertTrue(result)

        # 注册超出最大延迟
        result = self.ctb.register_event(hero, current_time + max_delay + 1)
        self.assertFalse(result)

    def test_character_removal_sync(self):
        """测试角色移除时的同步"""
        # 添加多个角色
        chars = []
        for i in range(5):
            char = Character(f"char{i}", f"角色{i}")
            chars.append(char)
            self.ctb.add_character(char)

        self.ctb.initialize_ctb()

        # 移除一个角色
        self.ctb.remove_character("char2")

        # 检查时间轮中的事件
        char2_events = self.ctb.time_wheel.get_events_by_key("char2")
        self.assertEqual(len(char2_events), 0)

        # 其他角色的事件应该还在
        self.assertEqual(self.ctb.time_wheel.total_events(), 4)

    def test_multiple_advances(self):
        """测试多次推进的准确性"""
        hero = Character("hero", "英雄")
        self.ctb.add_character(hero)

        # 在特定时间注册多个事件
        base_time = self.time_manager._total_hours
        for i in [10, 20, 30, 40, 50]:
            event = Event(f"event{i}", f"事件{i}", EventType.CUSTOM, base_time + i)
            self.ctb.register_event(event, base_time + i)

        # 分多次推进
        self.ctb.advance_time(15)  # 应该触发10
        self.assertEqual(len(self.ctb.action_history), 1)

        self.ctb.advance_time(10)  # 应该触发20
        self.assertEqual(len(self.ctb.action_history), 2)

        self.ctb.advance_time(30)  # 应该触发30, 40, 50
        self.assertEqual(len(self.ctb.action_history), 5)

        # 验证时间的准确性
        self.assertEqual(self.time_manager._total_hours, base_time + 55)


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_empty_wheel_operations(self):
        """测试空时间轮的操作"""
        wheel = TimeWheel[str](100)

        # 空轮推进
        events = wheel.advance(50)
        self.assertEqual(events, [])

        # 空轮peek
        peeked = wheel.peek(0, 100)
        self.assertEqual(peeked, [])

        # 空轮的下一个事件延迟
        self.assertIsNone(wheel.get_next_event_delay())

    def test_large_advance(self):
        """测试大幅度推进"""
        wheel = TimeWheel[int](100)

        # 添加一些事件
        for i in range(10):
            wheel.add(i, i * 10)

        # 推进超过轮子大小的时间
        events = wheel.advance(200)

        # 应该触发所有事件
        self.assertEqual(len(events), 10)
        self.assertTrue(wheel.is_empty())

    def test_negative_values(self):
        """测试负值处理"""
        wheel = TimeWheel[str](50)

        # 负延迟应该抛出异常
        with self.assertRaises(ValueError):
            wheel.add("event", -1)

        # 负推进应该抛出异常
        with self.assertRaises(ValueError):
            wheel.advance(-1)

        # 负起始peek应该抛出异常
        with self.assertRaises(ValueError):
            wheel.peek(-1, 10)


def run_tests():
    """运行所有测试"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()