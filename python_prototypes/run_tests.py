#!/usr/bin/env python3
"""
项目根目录的测试运行器
调用unittest来发现并运行所有测试
"""

import sys
import unittest
import os

if __name__ == "__main__":
    # 添加当前目录到Python路径
    sys.path.insert(0, os.path.abspath('.'))
    
    # 运行各个模块的测试
    test_modules = [
        'tests.core.calendar.test_calendar',
        'tests.core.indexed_time_wheel.test_indexed_time_wheel', 
        'tests.core.ctb_manager.test_ctb_manager',
        'tests.core.test_game_world'
    ]
    
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            # 导入模块并添加到测试套件
            module = __import__(module_name, fromlist=[''])
            loader = unittest.TestLoader()
            module_suite = loader.loadTestsFromModule(module)
            suite.addTests(module_suite)
            print(f"✓ 成功加载: {module_name}")
        except ImportError as e:
            print(f"✗ 导入失败: {module_name} - {e}")
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回适当的退出代码
    sys.exit(0 if result.wasSuccessful() else 1)