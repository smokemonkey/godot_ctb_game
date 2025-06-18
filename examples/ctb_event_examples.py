#!/usr/bin/env python3
"""
CTB系统事件示例

展示如何创建和使用不同类型的事件，包括：
- 角色行动事件
- 季节变化事件
- 自定义事件
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_system.calendar import TimeManager
from game_system.ctb import CTBManager, Character, Event, EventType


class SeasonChangeEvent(Event):
    """季节变化事件"""

    def __init__(self, season_name: str, next_season_days: int = 90):
        """
        初始化季节变化事件

        Args:
            season_name: 季节名称
            next_season_days: 下一个季节的天数后
        """
        super().__init__(
            id=f"season_{season_name}",
            name=f"{season_name}季到来",
            event_type=EventType.SEASON_CHANGE,
            trigger_time=0,  # 将在注册时设置
            description=f"季节变化：进入{season_name}季"
        )
        self.season_name = season_name
        self.next_season_days = next_season_days

    def execute(self, ctb_manager: CTBManager) -> None:
        """执行季节变化"""
        print(f"\n🌸 季节变化：{self.season_name}季到来了！")

        # 计算下一个季节
        season_cycle = ["春", "夏", "秋", "冬"]
        current_index = season_cycle.index(self.season_name)
        next_season = season_cycle[(current_index + 1) % 4]

        # 注册下一个季节变化事件
        next_event = SeasonChangeEvent(next_season, 90)
        next_time = ctb_manager.time_manager._total_hours + (90 * 24)
        ctb_manager.register_event(next_event, next_time)


class CustomEvent(Event):
    """自定义事件示例 - 节日"""

    def __init__(self, festival_name: str, callback=None):
        super().__init__(
            id=f"festival_{festival_name}",
            name=f"{festival_name}节",
            event_type=EventType.CUSTOM,
            trigger_time=0,
            description=f"节日庆典：{festival_name}节"
        )
        self.festival_name = festival_name
        self.callback = callback

    def execute(self, ctb_manager: CTBManager) -> None:
        """执行节日事件"""
        print(f"\n🎉 节日：{self.festival_name}节到了！全民欢庆！")
        if self.callback:
            self.callback(self, ctb_manager)


def main():
    """演示不同类型的事件"""
    print("=== CTB系统事件类型演示 ===\n")

    # 初始化系统
    time_manager = TimeManager()
    ctb = CTBManager(time_manager)

    # 添加角色
    characters = [
        Character("warrior", "战士", faction="王国"),
        Character("mage", "法师", faction="魔法学院"),
        Character("rogue", "盗贼", faction="盗贼公会")
    ]

    for char in characters:
        ctb.add_character(char)
        print(f"添加角色：{char.name} ({char.faction})")

    # 注册季节变化事件（从春季开始）
    spring_event = SeasonChangeEvent("春")
    ctb.register_event(spring_event, time_manager._total_hours + 24)  # 1天后春季到来
    print("\n注册季节变化事件：春季将在1天后到来")

    # 注册一些节日
    festivals = [
        ("春节", 30),    # 30天后
        ("中秋", 120),   # 120天后
        ("冬至", 270)    # 270天后
    ]

    for festival_name, days in festivals:
        festival_event = CustomEvent(festival_name)
        ctb.register_event(festival_event, time_manager._total_hours + days * 24)
        print(f"注册节日事件：{festival_name}节将在{days}天后到来")

    # 初始化CTB系统
    print("\n初始化CTB系统...")
    ctb.initialize_ctb()

    # 显示未来的事件
    print("\n=== 未来30个事件预览 ===")
    action_list = ctb.get_action_list(30)

    for i, action in enumerate(action_list[:15]):
        hours_total = action['time_until']
        days = hours_total // 24
        hours = hours_total % 24
        event_type = action.get('type', '')
        event_name = action.get('name', '')
        print(f"{i+1:2d}. [{event_type:8s}] {event_name:12s} - {days:3d}天{hours:2d}小时后")

    if len(action_list) > 15:
        print(f"... (共{len(action_list)}个事件)")

    # 执行一些事件
    print("\n=== 执行前10个事件 ===")
    for i in range(10):
        event = ctb.execute_next_action()
        if event:
            time_info = time_manager.get_time_info()
            print(f"\n时间：{time_info['year']}年{time_info['month']}月{time_info['day_in_month']}日")
            print(f"事件：{event.name} ({event.event_type.value})")
        else:
            break

    # 显示系统状态
    print("\n" + ctb.get_status_text())

    print("\n演示完成！")


if __name__ == "__main__":
    main()