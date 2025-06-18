#!/usr/bin/env python3
"""
项目根目录的测试运行器
调用pytest来发现并运行所有测试
"""

import sys
import pytest

if __name__ == "__main__":
    # 直接调用pytest的主函数
    # pytest会自动发现tests/目录下的所有测试文件
    retcode = pytest.main()
    sys.exit(retcode)