#!/usr/bin/env python3
"""
CTB系统测试用例

测试CTB系统的核心功能：
- 角色管理
- 行动队列
- 时间推进
- 公式计算
- 状态管理
"""

import unittest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_time import TimeManager
from ctb import CTBManager, Character, ActionEvent, ActionType, CTBFormula

class TestCTBFormula(unittest.TestCase):
    """测试CTB公式计算"""
    
    def test_calculate_action_interval(self):
        """测试行动间隔计算"""
        # 基础测试
        self.assertEqual(CTBFormula.calculate_action_interval(5, 100), 20.0)
        self.assertEqual(CTBFormula.calculate_action_interval(10, 100), 10.0)
        self.assertEqual(CTBFormula.calculate_action_interval(1, 100), 100.0)
        
        # 不同基础因子
        self.assertEqual(CTBFormula.calculate_action_interval(5, 50), 10.0)
        self.assertEqual(CTBFormula.calculate_action_interval(10, 200), 20.0)
        
    def test_calculate_action_interval_edge_cases(self):
        """测试边界情况"""
        # 速度为0应该抛出异常
        with self.assertRaises(ValueError):
            CTBFormula.calculate_action_interval(0, 100)
        
        # 负速度应该抛出异常
        with self.assertRaises(ValueError):
            CTBFormula.calculate_action_interval(-5, 100)
    
    def test_calculate_next_action_time(self):
        """测试下次行动时间计算"""
        # 基础测试：速度5，基础因子100，间隔20天=480小时
        next_time = CTBFormula.calculate_next_action_time(0, 5, 100)
        self.assertEqual(next_time, 480)
        
        # 从非零时间开始
        next_time = CTBFormula.calculate_next_action_time(100, 10, 100)
        self.assertEqual(next_time, 340)  # 100 + 240 (10天*24小时)


class TestCharacter(unittest.TestCase):
    """测试角色类"""
    
    def test_character_creation(self):
        """测试角色创建"""
        char = Character("test1", "测试角色", 5, "测试阵营")
        self.assertEqual(char.id, "test1")
        self.assertEqual(char.name, "测试角色")
        self.assertEqual(char.speed, 5)
        self.assertEqual(char.faction, "测试阵营")
        self.assertTrue(char.is_active)
    
    def test_character_defaults(self):
        """测试角色默认值"""
        char = Character("test2", "简单角色", 10)
        self.assertEqual(char.faction, "中立")
        self.assertTrue(char.is_active)
    
    def test_invalid_speed(self):
        """测试无效速度"""
        with self.assertRaises(ValueError):
            Character("test3", "无效角色", 0)
        
        with self.assertRaises(ValueError):
            Character("test4", "负速度角色", -5)


class TestCTBManager(unittest.TestCase):
    """测试CTB管理器"""
    
    def setUp(self):
        """测试初始化"""
        self.time_manager = TimeManager()
        self.ctb_manager = CTBManager(self.time_manager, base_factor=100)
        
        # 创建测试角色
        self.char1 = Character("char1", "张三", 5)
        self.char2 = Character("char2", "李四", 10)
        self.char3 = Character("char3", "王五", 20)
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.ctb_manager.base_factor, 100)
        self.assertEqual(len(self.ctb_manager.characters), 0)
        self.assertEqual(len(self.ctb_manager.action_queue), 0)
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
        self.assertEqual(len(self.ctb_manager.action_queue), 2)
    
    def test_action_queue_order(self):
        """测试行动队列顺序"""
        self.ctb_manager.add_character(self.char1)  # 速度5, 间隔20天
        self.ctb_manager.add_character(self.char2)  # 速度10, 间隔10天
        self.ctb_manager.add_character(self.char3)  # 速度20, 间隔5天
        
        self.ctb_manager.initialize_ctb()
        
        # 下一个行动应该是速度最快的角色
        next_action = self.ctb_manager.get_next_action()
        self.assertIsNotNone(next_action)
        self.assertEqual(next_action.character.name, "王五")  # 速度20，最快
    
    def test_execute_next_action(self):
        """测试执行下一个行动"""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()
        
        # 记录初始时间
        initial_time = self.time_manager._total_hours
        
        # 执行行动
        action = self.ctb_manager.execute_next_action()
        self.assertIsNotNone(action)
        self.assertEqual(action.character.name, "张三")
        
        # 时间应该已推进
        self.assertGreater(self.time_manager._total_hours, initial_time)
        
        # 应该有新的行动安排
        self.assertEqual(len(self.ctb_manager.action_queue), 1)
    
    def test_set_base_factor(self):
        """测试设置基础因子"""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()
        
        # 获取初始行动时间
        initial_action = self.ctb_manager.get_next_action()
        initial_time = initial_action.trigger_time
        
        # 修改基础因子
        self.ctb_manager.set_base_factor(50)
        self.assertEqual(self.ctb_manager.base_factor, 50)
        
        # 行动时间应该重新计算
        new_action = self.ctb_manager.get_next_action()
        new_time = new_action.trigger_time
        self.assertNotEqual(initial_time, new_time)
    
    def test_character_active_state(self):
        """测试角色活跃状态"""
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.add_character(self.char2)
        self.ctb_manager.initialize_ctb()
        
        # 初始状态：2个活跃角色，2个行动
        self.assertEqual(len(self.ctb_manager.action_queue), 2)
        
        # 停用一个角色
        result = self.ctb_manager.set_character_active("char1", False)
        self.assertTrue(result)
        self.assertEqual(len(self.ctb_manager.action_queue), 1)
        
        # 重新激活角色
        result = self.ctb_manager.set_character_active("char1", True)
        self.assertTrue(result)
        self.assertEqual(len(self.ctb_manager.action_queue), 2)
        
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
        history = self.ctb_manager.get_recent_actions()
        self.assertEqual(len(history), 3)
        
        # 验证历史记录内容
        for record in history:
            self.assertIn('character_name', record)
            self.assertIn('timestamp', record)
            self.assertIn('year', record)
    
    def test_get_status_info(self):
        """测试状态信息获取"""
        # 未初始化状态
        status = self.ctb_manager.get_status_text()
        self.assertIn("未初始化", status)
        
        # 初始化后状态
        self.ctb_manager.add_character(self.char1)
        self.ctb_manager.initialize_ctb()
        
        status = self.ctb_manager.get_status_text()
        self.assertIn("基础因子", status)
        self.assertIn("活跃角色", status)
        
        # 角色信息
        char_info = self.ctb_manager.get_character_info()
        self.assertEqual(len(char_info), 1)
        self.assertEqual(char_info[0]['name'], "张三")
        self.assertEqual(char_info[0]['speed'], 5)
        
        # 队列信息
        queue_info = self.ctb_manager.get_action_queue_info()
        self.assertEqual(len(queue_info), 1)
        self.assertEqual(queue_info[0]['character_name'], "张三")


class TestCTBIntegration(unittest.TestCase):
    """CTB系统集成测试"""
    
    def setUp(self):
        """测试初始化"""
        self.time_manager = TimeManager()
        self.ctb_manager = CTBManager(self.time_manager, base_factor=20)  # 快速测试
        
        # 添加多个角色
        self.ctb_manager.add_character(Character("fast", "快速角色", 10))
        self.ctb_manager.add_character(Character("slow", "慢速角色", 5))
        self.ctb_manager.add_character(Character("medium", "中速角色", 8))
    
    def test_multiple_actions_sequence(self):
        """测试多个行动的执行序列"""
        self.ctb_manager.initialize_ctb()
        
        action_sequence = []
        for _ in range(6):
            action = self.ctb_manager.execute_next_action()
            if action:
                action_sequence.append(action.character.name)
        
        # 验证执行序列（快速角色应该更频繁行动）
        fast_count = action_sequence.count("快速角色")
        slow_count = action_sequence.count("慢速角色")
        
        # 快速角色行动次数应该更多
        self.assertGreaterEqual(fast_count, slow_count)
    
    def test_time_progression(self):
        """测试时间推进"""
        self.ctb_manager.initialize_ctb()
        
        initial_time = self.time_manager._total_hours
        
        # 执行多个行动
        for _ in range(5):
            self.ctb_manager.execute_next_action()
        
        final_time = self.time_manager._total_hours
        
        # 时间应该有显著推进
        self.assertGreater(final_time - initial_time, 100)  # 至少推进100小时


def run_ctb_tests():
    """运行所有CTB测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [
        TestCTBFormula,
        TestCharacter,
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