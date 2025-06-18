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


def clear_due_events(world):
    while True:
        event = world.time_wheel.pop_due_event()
        if event is None:
            break


def demo_basic_usage():
    """演示基本使用"""
    print("=== 游戏世界系统基本使用演示 ===")

    # 1. 获取游戏世界实例（单例）
    world = get_game_world()

    # 2. 配置游戏世界（仅在第一次创建时有效）
    config = GameWorldConfig(
        time_wheel_size=100,  # 较小的时间轮用于演示
        auto_save_interval=5
    )
    world = get_game_world(config)

    # 3. 开始游戏
    world.start_game()

    # 4. 通过CTB管理器调度一些事件
    world.ctb_manager.schedule_with_delay("event_1", "第一个事件", 5)
    world.ctb_manager.schedule_with_delay("event_2", "第二个事件", 10)

    print(f"调度了 {len(world.time_wheel.peek_upcoming_events(10, 100))} 个事件")

    # 5. 演示tick推进
    print("演示_advance_tick() - 推进到下一个事件:")
    for i in range(3):
        clear_due_events(world)
        world._advance_tick()
        print(f"tick {i+1}: 推进了 1 小时，当前时间: {world.calendar.format_date_gregorian()}")

    # 6. 查看游戏状态
    status = world.get_game_status()
    print(f"\n游戏状态: {status}")

    # 7. 停止游戏
    world.stop_game()


def demo_event_system():
    """演示事件系统"""
    print("\n=== 事件系统演示 ===")

    world = get_game_world()
    world.start_game()

    # 注册事件回调
    def on_event_scheduled(data):
        print(f"事件: 事件 {data.get('event_id', 'unknown')} 已调度")

    def on_tick_ended(data):
        print(f"事件: tick {data.get('tick_number', 0)} 结束，"
              f"时间: {data.get('current_time', {}).get('gregorian_year', 0)}年")

    world.register_event_callback('tick_ended', on_tick_ended)

    # 通过CTB管理器调度事件
    world.ctb_manager.schedule_with_delay("demo_event", "演示事件", 5)

    # 推进tick触发事件
    for i in range(2):
        clear_due_events(world)
        world._advance_tick()

    world.stop_game()


def demo_time_management():
    """演示时间管理"""
    print("\n=== 时间管理演示 ===")

    world = get_game_world()
    world.start_game()

    print(f"初始时间: {world.calendar.format_date_gregorian()}")

    # 手动推进时间（通过tick）
    for i in range(30 * 24):  # 30天 = 30 * 24小时
        clear_due_events(world)
        world._advance_tick()
    print(f"推进30天后: {world.calendar.format_date_gregorian()}")

    # 开始新纪元
    world.calendar.start_new_era("开元")
    print(f"开始开元纪元: {world.calendar.format_date_era()}")

    # 推进几个tick
    for i in range(2):
        clear_due_events(world)
        world._advance_tick()
        print(f"tick {i+1}: {world.calendar.format_date_era()}")

    world.stop_game()


def demo_component_access():
    """演示直接访问组件"""
    print("\n=== 组件访问演示 ===")

    world = get_game_world()
    world.start_game()

    # 直接访问日历系统
    calendar = world.calendar
    print(f"日历时间: {calendar.get_time_info()}")

    # 直接访问时间轮
    time_wheel = world.time_wheel
    print(f"时间轮大小: {time_wheel.buffer_size}")
    print(f"当前槽位事件数: {len(time_wheel)}")

    # 通过CTB管理器调度事件并查看
    world.ctb_manager.schedule_with_delay("test_event", "测试事件", 5)

    # 查看即将发生的事件
    upcoming = world.time_wheel.peek_upcoming_events(5, 100)
    print(f"即将发生的事件: {len(upcoming)} 个")

    world.stop_game()


def demo_ctb_system():
    """演示CTB系统"""
    print("\n=== CTB系统演示 ===")

    world = get_game_world()
    world.start_game()

    # 添加一些角色
    ctb = world.ctb_manager
    ctb.add_character(Character("zhangsan", "张三"))
    ctb.add_character(Character("lisi", "李四"))
    ctb.add_character(Character("wangwu", "王五"))

    print(f"添加了 {len(ctb.characters)} 个角色")

    # 初始化CTB系统
    ctb.initialize_ctb()
    print("CTB系统已初始化")

    # 查看角色信息
    char_info = world.get_characters_info()
    print(f"角色信息: {char_info}")

    # 推进几个tick看看行动顺序
    for i in range(3):
        clear_due_events(world)
        world._advance_tick()
        due_event = ctb.get_due_event()
        if due_event:
            print(f"tick {i+1}: {due_event['character']} 行动")
        else:
            print(f"tick {i+1}: 无行动")

    world.stop_game()


def demo_singleton_behavior():
    """演示单例行为"""
    print("\n=== 单例行为演示 ===")

    # 创建多个实例引用
    world1 = get_game_world()
    world2 = get_game_world()
    world3 = GameWorld()

    # 验证它们是同一个实例
    print(f"world1 is world2: {world1 is world2}")
    print(f"world1 is world3: {world1 is world3}")

    # 在一个实例上操作，另一个实例能看到变化
    world1.start_game()
    print(f"world2.is_running: {world2.is_running}")

    world1.stop_game()


def main():
    """主函数"""
    print("游戏世界系统演示程序")
    print("=" * 50)

    try:
        # 运行各种演示
        demo_basic_usage()
        demo_event_system()
        demo_time_management()
        demo_component_access()
        demo_ctb_system()
        demo_singleton_behavior()

        print("\n" + "=" * 50)
        print("所有演示完成！")

    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()