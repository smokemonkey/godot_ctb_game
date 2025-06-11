#!/usr/bin/env python
"""
时间系统测试运行器
运行所有时间系统相关的测试用例
"""

import unittest
import sys
import os

def run_tests():
    """运行所有测试"""
    # 确保当前目录在Python路径中
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = current_dir
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 配置测试运行器
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print("=" * 60)
    print("🧪 运行时间系统测试套件")
    print("=" * 60)
    
    # 运行测试
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, trace in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, trace in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  存在失败的测试，请检查代码。")
        return 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code) 