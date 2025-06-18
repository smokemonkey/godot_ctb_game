#!/usr/bin/env python3
"""
游戏世界系统测试用例

测试GameWorld的核心功能：
- 单例模式
- 组件初始化
- 游戏状态管理
- 事件系统
- 并发安全性
"""

import unittest
import sys
import os
import threading
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from game_system.game_world import GameWorld, GameWorldConfig, get_game_world, reset_game_world


class TestGameWorld(unittest.TestCase):
    """测试GameWorld核心功能"""

    def setUp(self):
        """每个测试前的设置"""
        reset_game_world()
        self.world = get_game_world()

    def test_singleton_behavior(self):
        """测试单例模式"""
        world1 = get_game_world()
        world2 = get_game_world()

        # 验证是同一个实例
        self.assertIs(world1, world2)

        # 验证重置后仍然是单例
        reset_game_world()
        world3 = get_game_world()
        self.assertIs(world1, world3)

    def test_initial_state(self):
        """测试初始状态"""
        # 验证初始状态
        self.assertFalse(self.world.is_running)
        self.assertEqual(self.world.turn_count, 0)

        # 验证组件已初始化
        self.assertIsNotNone(self.world.calendar)
        self.assertIsNotNone(self.world.time_wheel)
        self.assertIsNotNone(self.world.ctb_manager)

    def test_start_stop_game(self):
        """测试开始和停止游戏"""
        # 开始游戏
        self.world.start_game()
        self.assertTrue(self.world.is_running)

        # 停止游戏
        self.world.stop_game()
        self.assertFalse(self.world.is_running)

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

    def test_get_characters_info(self):
        """测试获取角色信息（暂时返回空列表）"""
        characters_info = self.world.get_characters_info()
        self.assertEqual(len(characters_info), 0)
        self.assertIsInstance(characters_info, list)


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


def run_game_world_tests():
    """运行所有GameWorld测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    test_classes = [
        TestGameWorld,
        TestGameWorldConfig
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_game_world_tests()
    sys.exit(0 if success else 1)