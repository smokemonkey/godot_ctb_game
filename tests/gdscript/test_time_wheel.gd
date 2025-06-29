extends GutTest

## IndexedTimeWheel系统单元测试
##
## 测试时间轮的事件调度和管理功能

const IndexedTimeWheel = preload("res://scripts/gdscript/core/IndexedTimeWheel.gd")
const EventExample = preload("res://scripts/gdscript/development/EventExample.gd")
const ConfigManagerMock = preload("res://tests/gdscript/mocks/ConfigManagerMock.gd")

var time_wheel: IndexedTimeWheel
var config_mock: ConfigManagerMock

func before_each():
    config_mock = ConfigManagerMock.new()
    # 创建IndexedTimeWheel用于测试
    time_wheel = IndexedTimeWheel.new(180, func(): return 0)

func after_each():
    # RefCounted对象会自动管理内存，不需要queue_free()
    time_wheel = null
    config_mock = null

func test_initial_state():
    var actor = EventExample.new("test1", "测试角色", "测试阵营")
    assert_not_null(actor, "EventExample应该能够创建")
    assert_eq(actor.id, "test1", "ID应该正确")
    # RefCounted对象自动管理内存

func test_schedulable_interface():
    var actor = EventExample.new("test1", "测试角色", "测试阵营")

    # 测试基本属性
    assert_eq(actor.faction, "测试阵营", "阵营应该正确设置")
    assert_false(actor.action_list.is_empty(), "动作列表不应该为空")

    # RefCounted对象自动管理内存

func test_advance_and_pop_events():
    var actor = EventExample.new("test1", "测试角色")
    time_wheel.schedule_with_delay("actor1", actor, 3)  # 3小时后

    # 推进2小时，事件还没有到期
    for i in range(2):
        var event = time_wheel.pop_due_event()  # 清空当前槽
        time_wheel.advance_wheel()
    
    var event = time_wheel.pop_due_event()
    assert_true(event.is_empty(), "2小时后不应该有到期事件")

    # 再推进1小时，事件应该到期（总共3小时）
    time_wheel.advance_wheel()
    event = time_wheel.pop_due_event()
    assert_false(event.is_empty(), "3小时后应该有1个到期事件")

    # RefCounted对象自动管理内存

func test_schedule_at_absolute_hour():
    var actor = EventExample.new("test1", "测试角色")
    time_wheel.schedule_at_absolute_hour("actor1", actor, 10)  # 绝对时间第10小时

    assert_eq(time_wheel.get_count(), 1, "调度绝对时间事件后应该有1个事件")

    # 推进到第10小时
    for i in range(10):
        var temp_event = time_wheel.pop_due_event()  # 清空当前槽
        time_wheel.advance_wheel()
    var event = time_wheel.pop_due_event()
    assert_false(event.is_empty(), "到达第10小时应该有1个到期事件")

    # RefCounted对象自动管理内存

func test_multiple_events():
    var actor1 = EventExample.new("actor1", "角色1")
    var actor2 = EventExample.new("actor2", "角色2")

    time_wheel.schedule_with_delay("actor1", actor1, 2)  # 2小时后
    time_wheel.schedule_with_delay("actor2", actor2, 5)  # 5小时后

    assert_eq(time_wheel.get_count(), 2, "调度两个事件后应该有2个事件")

    # 推进到第2小时
    for i in range(2):
        var temp_event = time_wheel.pop_due_event()  # 清空当前槽
        time_wheel.advance_wheel()
    var event = time_wheel.pop_due_event()
    assert_false(event.is_empty(), "第2小时应该有1个到期事件")
    assert_eq(time_wheel.get_count(), 1, "取出1个事件后应该还有1个事件")

    # 推进到第5小时
    for i in range(3):
        var temp_event = time_wheel.pop_due_event()  # 清空当前槽
        time_wheel.advance_wheel()
    event = time_wheel.pop_due_event()
    assert_false(event.is_empty(), "第5小时应该有1个到期事件")
    assert_eq(time_wheel.get_count(), 0, "取出所有事件后应该没有事件")

    # RefCounted objects are automatically managed, no need for queue_free()

func test_remove_event():
    var actor = EventExample.new("test1", "测试角色")
    time_wheel.schedule_with_delay("actor1", actor, 5)

    assert_eq(time_wheel.get_count(), 1, "调度事件后应该有1个事件")

    time_wheel.remove("actor1")
    assert_eq(time_wheel.get_count(), 0, "移除事件后应该没有事件")

    # RefCounted对象自动管理内存