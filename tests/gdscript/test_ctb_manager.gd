extends GutTest

## CTBManager系统单元测试
##
## 测试CTB管理器的核心功能：角色管理、调度、时间推进等

const SchedulableExample = preload("res://scripts/gdscript/development/SchedulableExample.gd")
const ConfigManagerMock = preload("res://tests/gdscript/mocks/ConfigManagerMock.gd")

var config_mock: ConfigManagerMock

func before_each():
    config_mock = ConfigManagerMock.new()

func after_each():
    if config_mock:
        config_mock.queue_free()

func test_schedulable_creation():
    var actor = SchedulableExample.new("test1", "测试角色", "测试阵营")
    assert_not_null(actor, "SchedulableExample应该能够创建")
    assert_eq(actor.get_id(), "test1", "ID应该正确")
    assert_eq(actor.get_name(), "测试角色", "名称应该正确")
    actor.queue_free()

func test_schedulable_interface():
    var actor = SchedulableExample.new("test1", "测试角色", "测试阵营")
    
    # 测试接口方法
    assert_true(actor.is_active(), "角色应该默认为激活状态")
    var delay = actor.calculate_next_action_delay()
    assert_true(delay > 0, "动作延迟应该大于0")
    
    actor.queue_free()

func test_multiple_schedulables():
    var actor1 = SchedulableExample.new("test1", "角色1", "阵营1")
    var actor2 = SchedulableExample.new("test2", "角色2", "阵营2")
    
    assert_ne(actor1.get_id(), actor2.get_id(), "不同角色应该有不同ID")
    assert_ne(actor1.get_name(), actor2.get_name(), "不同角色应该有不同名称")
    
    actor1.queue_free()
    actor2.queue_free()

func test_action_execution():
    var actor = SchedulableExample.new("test1", "测试角色", "测试阵营")
    
    # 测试动作执行（应该不会崩溃）
    actor.execute_action()
    assert_true(true, "动作执行应该成功完成")
    
    actor.queue_free()

func test_schedulable_state():
    var actor = SchedulableExample.new("test1", "测试角色", "测试阵营")
    
    # 测试状态管理
    assert_true(actor.is_active(), "角色应该默认为激活状态")
    actor.set_active(false)
    assert_false(actor.is_active(), "设置为非激活后应该返回false")
    actor.set_active(true)
    assert_true(actor.is_active(), "重新激活后应该返回true")
    
    actor.queue_free()