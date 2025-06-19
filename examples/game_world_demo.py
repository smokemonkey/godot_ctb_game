#!/usr/bin/env python3
"""
游戏世界系统使用示例

演示如何使用GameWorld单例来管理游戏的核心组件。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_system.game_world import get_game_world, GameWorldConfig, GameWorld
from game_system.calendar.calendar import TimeUnit
from game_system.ctb_manager.ctb_manager import CTBManager, Character

def run_demo():
    world = get_game_world()

    # 添加角色
    world.ctb_manager.add_character(Character(id="player", name="勇者"))
    world.ctb_manager.add_character(Character(id="npc_01", name="商人A"))
    world.ctb_manager.add_character(Character(id="monster_01", name="哥布林"))

    # 开始游戏（这会为角色安排初始行动）
    world.start_game()

    # 模拟玩家点击“下一步”按钮20次
    for i in range(20):
        print(f"\n--- [第 {i+1} 次操作：推进游戏] ---")
        result = world.step_forward()
        if result:
            print(f"步骤结果: {result}")
        else:
            print("游戏已结束。")
            break

        # 打印状态信息
        print(world.ctb_manager.get_status_text())

if __name__ == "__main__":
    run_demo()