extends GutTest

## CTBManager系统单元测试
##
## 测试CTB管理器的核心功能：角色管理、调度、时间推进等

const EventExample = preload("res://scripts/gdscript/development/EventExample.gd")
const ConfigManagerMock = preload("res://tests/gdscript/mocks/ConfigManagerMock.gd")

var config_mock: ConfigManagerMock

func before_each():
    config_mock = ConfigManagerMock.new()

func after_each():
    # RefCounted objects are automatically managed, no need for queue_free()
    config_mock = null

func test_schedulable_creation():
    var actor = EventExample.new("test1", "测试角色", "测试阵营")
    assert_not_null(actor, "EventExample应该能够创建")
    assert_eq(actor.id, "test1", "ID应该正确")
    assert_eq(actor.name, "测试角色", "名称应该正确")
    # RefCounted objects are automatically managed, no need for queue_free()

func test_schedulable_interface():
    var actor = EventExample.new("test1", "测试角色", "测试阵营")
    
    # 测试接口方法
    assert_eq(actor.faction, "测试阵营", "阵营应该正确设置")
    assert_false(actor.action_list.is_empty(), "动作列表不应该为空")
    var next_time = actor.calculate_next_schedule_time(0)
    assert_true(next_time > 0, "下次调度时间应该大于0")
    
    # RefCounted objects are automatically managed, no need for queue_free()

func test_multiple_schedulables():
    var actor1 = EventExample.new("test1", "角色1", "阵营1")
    var actor2 = EventExample.new("test2", "角色2", "阵营2")
    
    assert_ne(actor1.id, actor2.id, "不同角色应该有不同ID")
    assert_ne(actor1.name, actor2.name, "不同角色应该有不同名称")
    
    # RefCounted objects are automatically managed, no need for queue_free()

func test_action_execution():
    var actor = EventExample.new("test1", "测试角色", "测试阵营")
    
    # 测试动作执行（应该不会崩溃）
    var result = actor.execute()
    assert_not_null(result, "execute()应该返回结果")
    assert_true(result.has("actor"), "结果应该包含actor字段")
    assert_true(result.has("action"), "结果应该包含action字段") 
    assert_true(result.has("success"), "结果应该包含success字段")
    
    # RefCounted objects are automatically managed, no need for queue_free()

func test_schedulable_state():
    var actor = EventExample.new("test1", "测试角色", "测试阵营")
    
    # 测试状态管理
    assert_true(actor.should_reschedule(), "角色应该默认允许重复调度")
    actor.reschedule_enabled = false
    assert_false(actor.should_reschedule(), "设置为不重复调度后应该返回false")
    actor.reschedule_enabled = true
    assert_true(actor.should_reschedule(), "重新启用重复调度后应该返回true")
    
    # RefCounted objects are automatically managed, no need for queue_free()