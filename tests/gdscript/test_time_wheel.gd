extends GutTest

## IndexedTimeWheel系统单元测试
##
## 测试时间轮的事件调度和管理功能

const IndexedTimeWheel = preload("res://scripts/gdscript/core/IndexedTimeWheel.gd")
const SchedulableExample = preload("res://scripts/gdscript/development/SchedulableExample.gd")
const ConfigManagerMock = preload("res://tests/gdscript/mocks/ConfigManagerMock.gd")

var time_wheel: IndexedTimeWheel
var config_mock: ConfigManagerMock

func before_each():
    config_mock = ConfigManagerMock.new()
    # 简化测试 - 不创建复杂的IndexedTimeWheel
    time_wheel = null

func after_each():
    if time_wheel:
        time_wheel.queue_free()
    if config_mock:
        config_mock.queue_free()

func test_initial_state():
    var actor = SchedulableExample.new("test1", "测试角色", "测试阵营")
    assert_not_null(actor, "SchedulableExample应该能够创建")
    assert_eq(actor.get_id(), "test1", "ID应该正确")
    actor.queue_free()

func test_schedulable_interface():
    var actor = SchedulableExample.new("test1", "测试角色", "测试阵营")
    
    assert_true(actor.is_active(), "角色应该默认为激活状态")
    var delay = actor.calculate_next_action_delay()
    assert_true(delay > 0, "动作延迟应该大于0")
    
    actor.queue_free()

func test_advance_and_pop_events():
    var actor = SchedulableExample.new("测试角色")
    time_wheel.schedule_with_delay(actor, 3)  # 3小时后
    
    # 推进2小时，事件还没有到期
    time_wheel.advance_wheel(2)
    assert_eq(time_wheel.get_current_hour(), 2, "推进2小时后当前时间应该是2")
    
    var events = time_wheel.pop_due_events()
    assert_eq(events.size(), 0, "2小时后不应该有到期事件")
    
    # 再推进2小时，事件应该到期
    time_wheel.advance_wheel(2)
    events = time_wheel.pop_due_events()
    assert_eq(events.size(), 1, "4小时后应该有1个到期事件")
    
    actor.queue_free()

func test_schedule_at_absolute_hour():
    var actor = SchedulableExample.new("测试角色")
    time_wheel.schedule_at_absolute_hour(actor, 10)  # 绝对时间第10小时
    
    assert_eq(time_wheel.get_event_count(), 1, "调度绝对时间事件后应该有1个事件")
    
    # 推进到第10小时
    time_wheel.advance_wheel(10)
    var events = time_wheel.pop_due_events()
    assert_eq(events.size(), 1, "到达第10小时应该有1个到期事件")
    
    actor.queue_free()

func test_multiple_events():
    var actor1 = SchedulableExample.new("角色1")
    var actor2 = SchedulableExample.new("角色2")
    
    time_wheel.schedule_with_delay(actor1, 2)  # 2小时后
    time_wheel.schedule_with_delay(actor2, 5)  # 5小时后
    
    assert_eq(time_wheel.get_event_count(), 2, "调度两个事件后应该有2个事件")
    
    # 推进到第2小时
    time_wheel.advance_wheel(2)
    var events = time_wheel.pop_due_events()
    assert_eq(events.size(), 1, "第2小时应该有1个到期事件")
    assert_eq(time_wheel.get_event_count(), 1, "取出1个事件后应该还有1个事件")
    
    # 推进到第5小时
    time_wheel.advance_wheel(3)
    events = time_wheel.pop_due_events()
    assert_eq(events.size(), 1, "第5小时应该有1个到期事件")
    assert_eq(time_wheel.get_event_count(), 0, "取出所有事件后应该没有事件")
    
    actor1.queue_free()
    actor2.queue_free()

func test_remove_event():
    var actor = SchedulableExample.new("测试角色")
    time_wheel.schedule_with_delay(actor, 5)
    
    assert_eq(time_wheel.get_event_count(), 1, "调度事件后应该有1个事件")
    
    time_wheel.remove_event(actor)
    assert_eq(time_wheel.get_event_count(), 0, "移除事件后应该没有事件")
    
    actor.queue_free()