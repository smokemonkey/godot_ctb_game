#!/usr/bin/env python
"""
项目根目录的测试运行器
简单调用tests目录中的测试运行器
"""

import subprocess
import sys
import os

def main():
    """运行测试"""
    # 切换到tests目录运行测试
    tests_dir = os.path.join(os.path.dirname(__file__), "tests")
    test_runner = os.path.join(tests_dir, "run_tests.py")
    
    if not os.path.exists(test_runner):
        print("❌ 找不到测试运行器")
        return 1
    
    try:
        # 运行测试
        result = subprocess.run([sys.executable, test_runner], 
                              cwd=tests_dir,
                              capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 