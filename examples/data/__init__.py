"""
演示数据包

包含用于演示和测试的示例数据：
- ctb_characters: CTB系统的角色数据
"""

from .ctb_characters import get_characters, get_ctb_config, print_character_info

__all__ = [
    "get_characters",
    "get_ctb_config", 
    "print_character_info"
] 