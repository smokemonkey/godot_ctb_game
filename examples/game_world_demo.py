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

    # 4. 调度一些事件
    world.schedule_event("event_1", "第一个事件", 5)
    world.schedule_event("event_2", "第二个事件", 10)

    print(f"调度了 {len(world.get_upcoming_events(10))} 个事件")

    # 5. 演示tick推进
    print("演示tick() - 推进到下一个事件:")
    for i in range(3):
        result = world.tick()
        print(f"tick {result['tick_number']}: 推进了 {result['ticks_advanced']} 小时，"
              f"执行了 {result['events_executed']} 个事件")
        print(f"当前时间: {world.calendar.format_date_gregorian()}")

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
        print(f"事件: 事件 {data['event_id']} 已调度，延迟 {data['delay']} 小时")

    def on_tick_ended(data):
        print(f"事件: tick {data['tick_number']} 结束，"
              f"时间: {data['current_time']['year']}年{data['current_time']['month']}月")

    world.register_event_callback('event_scheduled', on_event_scheduled)
    world.register_event_callback('tick_ended', on_tick_ended)

    # 调度事件触发回调
    world.schedule_event("demo_event", "演示事件", 5)

    # 推进tick触发事件
    for i in range(2):
        world.tick()

    world.stop_game()


def demo_time_management():
    """演示时间管理"""
    print("\n=== 时间管理演示 ===")

    world = get_game_world()
    world.start_game()

    print(f"初始时间: {world.calendar.format_date_gregorian()}")

    # 手动推进时间
    world.advance_time(30, TimeUnit.DAY)
    print(f"推进30天后: {world.calendar.format_date_gregorian()}")

    # 开始新纪元
    world.start_new_era("开元")
    print(f"开始开元纪元: {world.calendar.format_date_era()}")

    # 推进几个回合
    for i in range(2):
        result = world.advance_turn()
        print(f"回合 {result['turn_number']}: {world.calendar.format_date_era()}")

    # 推进几个tick
    for i in range(2):
        result = world.tick()
        print(f"tick {result['tick_number']}: {world.calendar.format_date_era()}")

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

    # 调度事件并查看
    world.schedule_event("test_event", "测试事件", 5)

    # 查看即将发生的事件
    upcoming = world.get_upcoming_events(5)
    print(f"即将发生的事件: {len(upcoming)} 个")

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
        demo_singleton_behavior()

        print("\n" + "=" * 50)
        print("所有演示完成！")

    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()