extends "res://addons/gut/test.gd"

## 新架构的可调度系统单元测试
## 测试Schedulable接口、SchedulableExample和重构后的CTBManager

var time_wheel: IndexedTimeWheel
var ctb_manager: CTBManager
var mock_calendar: MockCalendar
var executed_count: int = 0

# 模拟日历类
class MockCalendar:
    var current_time: int = 0
    
    func get_timestamp() -> int:
        return current_time
    
    func advance_time_tick() -> void:
        current_time += 1

func before_each():
    executed_count = 0  # 重置计数器
    mock_calendar = MockCalendar.new()
    time_wheel = IndexedTimeWheel.new(4320, mock_calendar.get_timestamp)  # 180天 * 24小时
    ctb_manager = CTBManager.new(
        mock_calendar.get_timestamp,
        _advance_time_callback,
        _schedule_callback,
        _remove_callback,
        _peek_callback,
        _pop_callback,
        _is_slot_empty_callback
    )

func _advance_time_callback() -> void:
    mock_calendar.advance_time_tick()
    time_wheel.advance_wheel()

func _schedule_callback(key: String, schedulable: Schedulable, delay: int) -> bool:
    time_wheel.schedule_with_delay(key, schedulable, delay)
    return true

func _remove_callback(key: String) -> bool:
    var removed = time_wheel.remove(key)
    return removed != null

func _peek_callback(count: int, max_events: int) -> Array:
    var upcoming = time_wheel.peek_upcoming_events(count, max_events)
    var result = []
    for event_dict in upcoming:
        result.append({"key": event_dict["key"], "value": event_dict["value"]})
    return result

func _pop_callback() -> Dictionary:
    return time_wheel.pop_due_event()

func _is_slot_empty_callback() -> bool:
    return time_wheel._is_current_slot_empty()

func _test_execute_callback(schedulable):
    executed_count += 1

## 测试SchedulableExample基本功能
func test_schedulable_example_creation():
    var actor = SchedulableExample.new("test_actor", "测试战士", "测试阵营")
    
    assert_eq(actor.id, "test_actor", "Actor ID should be set correctly")
    assert_eq(actor.name, "测试战士", "Actor name should be set correctly")
    assert_eq(actor.faction, "测试阵营", "Actor faction should be set correctly")
    assert_true(actor.is_active, "Actor should be active by default")
    assert_eq(actor.get_type_identifier(), "SchedulableExample", "Type identifier should be correct")

## 测试SchedulableExample执行行动
func test_schedulable_example_execute():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    
    # 测试执行行动
    var result = actor.execute()
    assert_not_null(result, "Execute should return a result")
    assert_true(result.has("actor"), "Result should contain actor")
    assert_true(result.has("action"), "Result should contain action")
    assert_true(result.has("success"), "Result should contain success flag")
    assert_eq(result["actor"], actor, "Result actor should be the same")
    assert_true(result["success"], "Action should be successful")

## 测试SchedulableExample非活跃状态
func test_schedulable_example_inactive():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    actor.set_active(false)
    
    assert_false(actor.is_active, "Actor should be inactive")
    assert_false(actor.should_reschedule(), "Inactive actor should not reschedule")
    
    var result = actor.execute()
    assert_null(result, "Inactive actor should not execute")

## 测试SchedulableExample调度时间计算
func test_schedulable_example_schedule_time():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    var current_time = 100
    
    var next_time = actor.calculate_next_schedule_time(current_time)
    assert_gt(next_time, current_time, "Next schedule time should be in the future")
    
    # 测试多次计算，应该有随机性
    var times = []
    for i in range(10):
        times.append(actor.calculate_next_schedule_time(current_time))
    
    # 检查是否有变化（不是所有时间都相同）
    var all_same = true
    for i in range(1, times.size()):
        if times[i] != times[0]:
            all_same = false
            break
    assert_false(all_same, "Schedule times should have randomness")

## 测试CTBManager添加可调度对象
func test_ctb_manager_add_schedulable():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    
    ctb_manager.add_schedulable(actor)
    assert_true(ctb_manager.scheduled_objects.has("test_actor"), "Actor should be added to CTB manager")
    
    var retrieved = ctb_manager.get_schedulable("test_actor")
    assert_eq(retrieved, actor, "Retrieved actor should be the same")

## 测试CTBManager移除可调度对象
func test_ctb_manager_remove_schedulable():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    
    ctb_manager.add_schedulable(actor)
    assert_true(ctb_manager.scheduled_objects.has("test_actor"), "Actor should be added")
    
    var removed = ctb_manager.remove_schedulable("test_actor")
    assert_true(removed, "Remove should return true")
    assert_false(ctb_manager.scheduled_objects.has("test_actor"), "Actor should be removed")
    
    var retrieved = ctb_manager.get_schedulable("test_actor")
    assert_null(retrieved, "Retrieved actor should be null after removal")

## 测试CTBManager初始化
func test_ctb_manager_initialization():
    var actor1 = SchedulableExample.new("actor1", "战士1")
    var actor2 = SchedulableExample.new("actor2", "战士2")
    
    ctb_manager.add_schedulable(actor1)
    ctb_manager.add_schedulable(actor2)
    
    assert_false(ctb_manager.is_initialized, "CTB should not be initialized yet")
    
    ctb_manager.initialize_ctb()
    assert_true(ctb_manager.is_initialized, "CTB should be initialized")
    
    # 检查是否有事件被安排
    var count = time_wheel.get_count()
    assert_gt(count, 0, "Should have scheduled events after initialization")

## 测试CTBManager执行可调度对象
func test_ctb_manager_execute_schedulable():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    
    # 设置执行回调
    ctb_manager.on_event_executed = Callable(self, "_test_execute_callback")
    
    ctb_manager.execute_schedulable(actor)
    
    assert_eq(executed_count, 1, "Execute callback should be called once")
    assert_eq(ctb_manager.action_history.size(), 1, "Action should be recorded in history")
    
    var history_entry = ctb_manager.action_history[0]
    assert_eq(history_entry["schedulable_name"], "测试战士", "History should record correct name")
    assert_eq(history_entry["schedulable_type"], "SchedulableExample", "History should record correct type")

## 测试CTBManager回合处理
func test_ctb_manager_process_turn():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    
    ctb_manager.add_schedulable(actor)
    ctb_manager.initialize_ctb()
    
    # 推进时间直到有事件可执行
    var result = ctb_manager.process_next_turn()
    
    assert_true(result.has("type"), "Result should have type")
    assert_eq(result["type"], "SCHEDULABLE_EXECUTED", "Type should be SCHEDULABLE_EXECUTED")
    assert_true(result.has("schedulable_name"), "Result should have schedulable name")
    assert_true(result.has("ticks_advanced"), "Result should have ticks advanced")

## 测试CTBManager活跃状态设置
func test_ctb_manager_set_active():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    
    ctb_manager.add_schedulable(actor)
    assert_true(actor.is_active, "Actor should be active initially")
    
    var result = ctb_manager.set_schedulable_active("test_actor", false)
    assert_true(result, "Set active should return true")
    assert_false(actor.is_active, "Actor should be inactive")
    
    result = ctb_manager.set_schedulable_active("test_actor", true)
    assert_true(result, "Set active should return true")
    assert_true(actor.is_active, "Actor should be active again")

## 测试CTBManager状态信息
func test_ctb_manager_status_info():
    var actor1 = SchedulableExample.new("actor1", "战士1")
    var actor2 = SchedulableExample.new("actor2", "战士2")
    
    ctb_manager.add_schedulable(actor1)
    ctb_manager.add_schedulable(actor2)
    ctb_manager.initialize_ctb()
    
    var status_text = ctb_manager.get_status_text()
    assert_true(status_text.contains("CTB系统状态"), "Status should contain system status")
    assert_true(status_text.contains("对象总数: 2"), "Status should show correct object count")
    
    var info_list = ctb_manager.get_schedulable_info()
    assert_eq(info_list.size(), 2, "Info list should contain 2 objects")
    
    for info in info_list:
        assert_true(info.has("id"), "Info should have id")
        assert_true(info.has("name"), "Info should have name")
        assert_true(info.has("type"), "Info should have type")
        assert_eq(info["type"], "SchedulableExample", "Type should be SchedulableExample")

## 测试简单事件类
func test_simple_event():
    var event = TestGameWorld.SimpleEvent.new("test_event", "测试事件", 100)
    
    assert_eq(event.id, "test_event", "Event ID should be correct")
    assert_eq(event.description, "测试事件", "Event description should be correct")
    assert_eq(event.trigger_time, 100, "Trigger time should be correct")
    assert_eq(event.get_type_identifier(), "SimpleEvent", "Type identifier should be correct")
    assert_false(event.should_reschedule(), "Simple event should not reschedule")
    
    var result = event.execute()
    assert_eq(result, event, "Execute should return the event itself")

## 测试混合调度系统
func test_mixed_scheduling_system():
    var actor = SchedulableExample.new("test_actor", "测试战士")
    var event = TestGameWorld.SimpleEvent.new("test_event", "测试事件", mock_calendar.current_time + 5)
    
    ctb_manager.add_schedulable(actor)
    ctb_manager.schedule_with_delay("test_event", event, 5)
    ctb_manager.initialize_ctb()
    
    # 应该能同时处理角色和事件
    var processed_count = 0
    while processed_count < 3 and mock_calendar.current_time < 200:
        if not time_wheel._is_current_slot_empty():
            var due = ctb_manager.get_due_schedulable()
            if due != null:
                ctb_manager.execute_schedulable(due)
                processed_count += 1
        else:
            mock_calendar.advance_time_tick()
            time_wheel.advance_wheel()
    
    assert_gt(processed_count, 0, "Should have processed some schedulables")
    assert_gt(ctb_manager.action_history.size(), 0, "Should have action history")