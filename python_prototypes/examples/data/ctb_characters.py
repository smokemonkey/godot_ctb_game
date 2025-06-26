"""
CTB系统测试数据

包含各种类型的角色数据，用于测试CTB系统功能。
这些数据与代码分离，便于修改和扩展。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from game_system.ctb_manager.ctb_manager import Character

# 基础测试角色数据
BASIC_CHARACTERS = [
    Character(
        id="char_zhang",
        name="张三",
        speed=5,
        faction="蜀国",
        is_active=True
    ),
    Character(
        id="char_li",
        name="李四",
        speed=7,
        faction="魏国",
        is_active=True
    ),
    Character(
        id="char_wang",
        name="王五",
        speed=10,
        faction="吴国",
        is_active=True
    )
]

# 扩展测试角色数据（更多角色用于复杂测试）
EXTENDED_CHARACTERS = [
    Character(
        id="char_zhao",
        name="赵六",
        speed=3,
        faction="蜀国",
        is_active=True
    ),
    Character(
        id="char_sun",
        name="孙七",
        speed=8,
        faction="吴国",
        is_active=True
    ),
    Character(
        id="char_zhou",
        name="周八",
        speed=12,
        faction="魏国",
        is_active=True
    ),
    Character(
        id="char_wu",
        name="吴九",
        speed=6,
        faction="中立",
        is_active=False  # 初始为非活跃状态
    )
]

# 速度极值测试数据
EXTREME_SPEED_CHARACTERS = [
    Character(
        id="char_slow",
        name="龟速者",
        speed=1,
        faction="慢速军团",
        is_active=True
    ),
    Character(
        id="char_fast",
        name="闪电侠",
        speed=50,
        faction="速度军团",
        is_active=True
    ),
    Character(
        id="char_medium",
        name="平衡者",
        speed=10,
        faction="中庸派",
        is_active=True
    )
]

# 按难度级别组织的角色组
CHARACTER_GROUPS = {
    "basic": BASIC_CHARACTERS,
    "extended": BASIC_CHARACTERS + EXTENDED_CHARACTERS,
    "extreme": EXTREME_SPEED_CHARACTERS,
    "all": BASIC_CHARACTERS + EXTENDED_CHARACTERS + EXTREME_SPEED_CHARACTERS
}

# CTB系统配置参数
CTB_CONFIGS = {
    "default": {
        "base_factor": 100,
        "description": "默认配置，标准速度计算"
    },
    "fast_pace": {
        "base_factor": 50,
        "description": "快节奏配置，行动更频繁"
    },
    "slow_pace": {
        "base_factor": 200,
        "description": "慢节奏配置，行动间隔更长"
    },
    "ultra_fast": {
        "base_factor": 20,
        "description": "超快节奏，适合快速测试"
    }
}

def get_characters(group_name: str = "basic"):
    """
    获取指定组的角色列表

    Args:
        group_name: 角色组名称 ("basic", "extended", "extreme", "all")

    Returns:
        角色列表的深拷贝
    """
    if group_name not in CHARACTER_GROUPS:
        raise ValueError(f"未知的角色组: {group_name}. 可用组: {list(CHARACTER_GROUPS.keys())}")

    # 返回深拷贝，避免修改原始数据
    import copy
    return copy.deepcopy(CHARACTER_GROUPS[group_name])

def get_ctb_config(config_name: str = "default"):
    """
    获取CTB配置参数

    Args:
        config_name: 配置名称

    Returns:
        配置字典
    """
    if config_name not in CTB_CONFIGS:
        raise ValueError(f"未知的配置: {config_name}. 可用配置: {list(CTB_CONFIGS.keys())}")

    return CTB_CONFIGS[config_name].copy()

def print_character_info(characters=None):
    """打印角色信息，用于调试"""
    if characters is None:
        characters = BASIC_CHARACTERS

    print("=== 角色信息 ===")
    for char in characters:
        active_status = "活跃" if char.is_active else "非活跃"
        print(f"ID: {char.id}")
        print(f"姓名: {char.name}")
        print(f"速度: {char.speed}")
        print(f"阵营: {char.faction}")
        print(f"状态: {active_status}")
        print(f"行动间隔: {100/char.speed:.1f}天")
        print("-" * 20)

if __name__ == "__main__":
    # 运行此文件时显示所有角色信息
    print("基础角色组:")
    print_character_info(get_characters("basic"))

    print("\n扩展角色组:")
    print_character_info(get_characters("extended"))

    print("\n极值速度角色组:")
    print_character_info(get_characters("extreme"))