extends RefCounted
class_name Schedulable

## 可调度接口基类
## 任何可以被CTB系统调度的对象都应该继承此类

var id: String
var name: String  
var trigger_time: int
var description: String

func _init(p_id: String, p_name: String, p_description: String = ""):
    id = p_id
    name = p_name
    description = p_description
    trigger_time = 0

## 抽象方法：执行调度逻辑
## 子类必须重写此方法实现具体的执行逻辑
func execute() -> Variant:
    push_error("Schedulable.execute() must be overridden in subclass")
    return null

## 抽象方法：计算下次调度时间  
## 子类必须重写此方法实现下次调度时间的计算
func calculate_next_schedule_time(current_time: int) -> int:
    push_error("Schedulable.calculate_next_schedule_time() must be overridden in subclass")
    return current_time

## 抽象方法：是否需要重复调度
## 子类可以重写此方法控制是否继续调度
func should_reschedule() -> bool:
    return false

## 获取类型标识符（用于调试和日志）
func get_type_identifier() -> String:
    return get_script().get_global_name() if get_script() else "Schedulable"

func _to_string() -> String:
    return "%s [%s]" % [name, get_type_identifier()]