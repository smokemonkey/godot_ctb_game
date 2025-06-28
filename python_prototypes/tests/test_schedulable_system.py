#!/usr/bin/env python3
"""
新架构的可调度系统单元测试

测试Schedulable接口、EventExample和重构后的CTBManager
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.schedulable import Schedulable, EventExample
from core.ctb_manager.ctb_manager_v2 import CTBManager, SimpleEvent
from core.indexed_time_wheel import IndexedTimeWheel


class MockCalendar:
    """模拟日历类"""
    def __init__(self):
        self.current_time = 0

    def get_timestamp(self):
        return self.current_time

    def advance_time_tick(self):
        self.current_time += 1


class TestSchedulableSystem(unittest.TestCase):
    """可调度系统测试类"""

    def setUp(self):
        """测试前置设置"""
        self.mock_calendar = MockCalendar()
        self.time_wheel = IndexedTimeWheel(180, self.mock_calendar.get_timestamp)
        self.ctb_manager = CTBManager(
            get_time_callback=self.mock_calendar.get_timestamp,
            advance_time_callback=self._advance_time_callback,
            schedule_callback=self._schedule_callback,
            remove_callback=self._remove_callback,
            peek_callback=self._peek_callback,
            pop_callback=self._pop_callback,
            is_slot_empty_callback=self._is_slot_empty_callback
        )

    def _advance_time_callback(self):
        """时间推进回调"""
        self.mock_calendar.advance_time_tick()
        self.time_wheel.advance_wheel()

    def _schedule_callback(self, key, schedulable, delay):
        """调度回调"""
        self.time_wheel.schedule_with_delay(key, schedulable, delay)
        return True

    def _remove_callback(self, key):
        """移除回调"""
        removed = self.time_wheel.remove(key)
        return removed is not None

    def _peek_callback(self, count, max_events):
        """查看回调"""
        upcoming = self.time_wheel.peek_upcoming_events(count, max_events)
        result = []
        for event_tuple in upcoming:
            # Python版本返回元组(key, value)
            if isinstance(event_tuple, tuple) and len(event_tuple) == 2:
                result.append({"key": event_tuple[0], "value": event_tuple[1]})
            else:
                # 如果已经是字典格式，直接添加
                result.append(event_tuple)
        return result

    def _pop_callback(self):
        """弹出回调"""
        return self.time_wheel.pop_due_event()

    def _is_slot_empty_callback(self):
        """检查当前槽是否为空的回调"""
        return self.time_wheel._is_current_slot_empty()

    def test_combat_actor_creation(self):
        """测试EventExample创建"""
        actor = EventExample("test_actor", "测试战士", "测试阵营")

        self.assertEqual(actor.id, "test_actor")
        self.assertEqual(actor.name, "测试战士")
        self.assertEqual(actor.faction, "测试阵营")
        self.assertTrue(actor.is_active)
        self.assertEqual(actor.get_type_identifier(), "EventExample")

    def test_combat_actor_execute(self):
        """测试EventExample执行行动"""
        actor = EventExample("test_actor", "测试战士")

        # 测试执行行动
        result = actor.execute()
        self.assertIsNotNone(result)
        self.assertIn("actor", result)
        self.assertIn("action", result)
        self.assertIn("success", result)
        self.assertEqual(result["actor"], actor)
        self.assertTrue(result["success"])

    def test_combat_actor_inactive(self):
        """测试EventExample非活跃状态"""
        actor = EventExample("test_actor", "测试战士")
        actor.set_active(False)

        self.assertFalse(actor.is_active)
        self.assertFalse(actor.should_reschedule())

        result = actor.execute()
        self.assertIsNone(result)

    def test_combat_actor_schedule_time(self):
        """测试EventExample调度时间计算"""
        actor = EventExample("test_actor", "测试战士")
        current_time = 100

        next_time = actor.calculate_next_schedule_time(current_time)
        self.assertGreater(next_time, current_time)

        # 测试多次计算，应该有随机性
        times = [actor.calculate_next_schedule_time(current_time) for _ in range(10)]

        # 检查是否有变化（不是所有时间都相同）
        all_same = len(set(times)) == 1
        self.assertFalse(all_same, "Schedule times should have randomness")

    def test_ctb_manager_add_event(self):
        """测试CTBManager添加可调度对象"""
        actor = EventExample("test_actor", "测试战士")

        self.ctb_manager.add_event(actor)
        self.assertIn("test_actor", self.ctb_manager.scheduled_objects)

        retrieved = self.ctb_manager.get_event("test_actor")
        self.assertEqual(retrieved, actor)

    def test_ctb_manager_remove_event(self):
        """测试CTBManager移除可调度对象"""
        actor = EventExample("test_actor", "测试战士")

        self.ctb_manager.add_event(actor)
        self.assertIn("test_actor", self.ctb_manager.scheduled_objects)

        removed = self.ctb_manager.remove_event("test_actor")
        self.assertTrue(removed)
        self.assertNotIn("test_actor", self.ctb_manager.scheduled_objects)

        retrieved = self.ctb_manager.get_event("test_actor")
        self.assertIsNone(retrieved)

    def test_ctb_manager_initialization(self):
        """测试CTBManager初始化"""
        actor1 = EventExample("actor1", "战士1")
        actor2 = EventExample("actor2", "战士2")

        self.ctb_manager.add_event(actor1)
        self.ctb_manager.add_event(actor2)

        self.assertFalse(self.ctb_manager.is_initialized)

        self.ctb_manager.initialize_ctb()
        self.assertTrue(self.ctb_manager.is_initialized)

        # 检查是否有事件被安排 - 直接检查index，因为事件可能在远期事件池中
        self.assertGreater(len(self.time_wheel.index), 0)

        # 也可以检查总事件数
        self.assertTrue(self.time_wheel.has_any_events())

    def test_ctb_manager_execute_event(self):
        """测试CTBManager执行可调度对象"""
        actor = EventExample("test_actor", "测试战士")
        executed_count = 0

        # 设置执行回调
        def on_executed(schedulable):
            nonlocal executed_count
            executed_count += 1

        self.ctb_manager.on_event_executed = on_executed

        self.ctb_manager.execute_event(actor)

        self.assertEqual(executed_count, 1)
        self.assertEqual(len(self.ctb_manager.action_history), 1)

        history_entry = self.ctb_manager.action_history[0]
        self.assertEqual(history_entry["schedulable_name"], "测试战士")
        self.assertEqual(history_entry["schedulable_type"], "EventExample")

    def test_ctb_manager_process_turn(self):
        """测试CTBManager回合处理"""
        actor = EventExample("test_actor", "测试战士")

        self.ctb_manager.add_event(actor)
        self.ctb_manager.initialize_ctb()

        # 推进时间直到有事件可执行
        result = self.ctb_manager.process_next_turn()

        self.assertIn("type", result)
        self.assertEqual(result["type"], "SCHEDULABLE_EXECUTED")
        self.assertIn("schedulable_name", result)
        self.assertIn("ticks_advanced", result)

    def test_ctb_manager_status_info(self):
        """测试CTBManager状态信息"""
        actor1 = EventExample("actor1", "战士1")
        actor2 = EventExample("actor2", "战士2")

        self.ctb_manager.add_event(actor1)
        self.ctb_manager.add_event(actor2)
        self.ctb_manager.initialize_ctb()

        status_text = self.ctb_manager.get_status_text()
        self.assertIn("CTB系统状态", status_text)
        self.assertIn("对象总数: 2", status_text)

        info_list = self.ctb_manager.get_event_info()
        self.assertEqual(len(info_list), 2)

        for info in info_list:
            self.assertIn("id", info)
            self.assertIn("name", info)
            self.assertIn("type", info)
            self.assertEqual(info["type"], "EventExample")

    def test_simple_event(self):
        """测试简单事件类"""
        event = SimpleEvent("test_event", "测试事件", 100)

        self.assertEqual(event.id, "test_event")
        self.assertEqual(event.description, "测试事件")
        self.assertEqual(event.trigger_time, 100)
        self.assertEqual(event.get_type_identifier(), "SimpleEvent")
        self.assertFalse(event.should_reschedule())

        result = event.execute()
        self.assertEqual(result, event)

    def test_mixed_scheduling_system(self):
        """测试混合调度系统"""
        actor = EventExample("test_actor", "测试战士")
        event = SimpleEvent("test_event", "测试事件", self.mock_calendar.current_time + 5)

        self.ctb_manager.add_event(actor)
        self.ctb_manager.schedule_with_delay("test_event", event, 5)
        self.ctb_manager.initialize_ctb()

        # 应该能同时处理角色和事件
        processed_count = 0
        while processed_count < 3 and self.mock_calendar.current_time < 200:
            if not self.time_wheel._is_current_slot_empty():
                due = self.ctb_manager.get_due_event()
                if due is not None:
                    self.ctb_manager.execute_event(due)
                    processed_count += 1
            else:
                self.mock_calendar.advance_time_tick()
                self.time_wheel.advance_wheel()

        self.assertGreater(processed_count, 0)
        self.assertGreater(len(self.ctb_manager.action_history), 0)


if __name__ == '__main__':
    unittest.main()