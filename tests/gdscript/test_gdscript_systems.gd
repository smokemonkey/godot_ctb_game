extends SceneTree

## GDScript系统功能测试脚本
## 用于验证Calendar、IndexedTimeWheel和CTBManager的基本功能

func _init():
    print("开始GDScript系统测试...")
    
    # 测试Calendar
    test_calendar()
    
    # 测试IndexedTimeWheel
    test_indexed_time_wheel()
    
    # 测试CTBManager
    test_ctb_manager()
    
    # 测试TestGameWorld集成
    test_integrated_system()
    
    print("所有测试完成！")
    quit()

func test_calendar():
    print("\n=== 测试Calendar系统 ===")
    
    var calendar = Calendar.new()
    
    # 测试基本时间推进
    print("初始时间: ", calendar.get_timestamp())
    calendar.advance_time_tick()
    print("推进1小时后: ", calendar.get_timestamp())
    
    # 测试时间信息
    var info = calendar.get_time_info()
    print("时间信息: ", info)
    
    # 测试格式化显示
    print("公历格式: ", calendar.format_date_gregorian(true))
    print("纪年格式: ", calendar.format_date_era(true))
    
    # 测试纪元锚定
    calendar.anchor_era("开元", 713)
    print("锚定开元后 - 纪年格式: ", calendar.format_date_era(true))
    
    # 测试改元
    calendar.start_new_era("永徽")
    print("改元永徽后 - 纪年格式: ", calendar.format_date_era(true))
    
    print("Calendar测试完成 ✓")

func test_indexed_time_wheel():
    print("\n=== 测试IndexedTimeWheel系统 ===")
    
    var current_time = [0]  # 使用数组来模拟可变引用
    var get_time_func = func(): return current_time[0]
    
    var wheel = IndexedTimeWheel.new(10, get_time_func)
    
    # 测试基本调度
    wheel.schedule_with_delay("test1", "测试事件1", 2)
    wheel.schedule_with_delay("test2", "测试事件2", 5)
    print("调度了2个事件")
    
    # 测试事件计数
    print("事件总数: ", wheel.get_count())
    print("有任何事件: ", wheel.has_any_events())
    
    # 测试查看即将到来的事件
    var upcoming = wheel.peek_upcoming_events(10, 5)
    print("即将到来的事件数量: ", upcoming.size())
    
    # 模拟时间推进
    current_time[0] = 2
    var popped = wheel.pop_due_event()
    if not popped.is_empty():
        print("弹出事件: ", popped)
    
    # 测试时间轮推进
    wheel.advance_wheel()
    current_time[0] = 3
    
    print("IndexedTimeWheel测试完成 ✓")

func test_ctb_manager():
    print("\n=== 测试CTBManager系统 ===")
    
    var current_time = [0]
    var get_time_func = func(): return current_time[0]
    var advance_time_func = func(): current_time[0] += 1
    
    # 创建时间轮以支持CTBManager
    var wheel = IndexedTimeWheel.new(10, get_time_func)
    
    # 创建CTB管理器
    var ctb = CTBManager.new(
        get_time_func,
        advance_time_func,
        func(key, event, delay): wheel.schedule_with_delay(key, event, delay); return true,
        func(key): return wheel.remove(key) != null,
        func(count, max_events): return wheel.peek_upcoming_events(count, max_events),
        func(): return wheel.pop_due_event(),
        func(): return wheel._is_current_slot_empty()
    )
    
    # 测试角色添加
    var character = CTBManager.Character.new("hero1", "英雄1")
    ctb.add_character(character)
    print("添加角色: ", character.name)
    
    # 测试事件安排
    var event = CTBManager.Event.new("event1", "测试事件", CTBManager.EventType.CUSTOM, 0)
    var scheduled = ctb.schedule_event(event, current_time[0] + 3)
    print("事件安排结果: ", scheduled)
    
    print("CTBManager测试完成 ✓")

func test_integrated_system():
    print("\n=== 测试TestGameWorld集成系统 ===")
    
    var test_world = TestGameWorld.new(20)
    
    # 测试基本功能
    print("初始时间: ", test_world.current_time)
    print("日历时间: ", test_world.current_calendar_time)
    
    # 测试事件安排
    test_world.schedule_event("test1", "集成测试事件1", 2)
    test_world.schedule_event("test2", "集成测试事件2", 5)
    print("安排了2个测试事件")
    
    # 测试时间推进
    var result = test_world.advance_time(3)
    print("时间推进结果: ", result)
    
    # 测试下一个事件
    var next_result = test_world.advance_to_next_event(10)
    print("下一个事件结果: ", next_result)
    
    # 测试纪元功能
    test_world.anchor_era("测试", 100)
    print("锚定纪元后 - 纪年时间: ", test_world.current_era_time)
    
    # 测试状态信息
    print("系统状态: ", test_world.get_status_summary())
    
    print("TestGameWorld集成测试完成 ✓")