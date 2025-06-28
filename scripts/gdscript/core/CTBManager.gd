extends RefCounted
class_name CTBManager

## CTB系统管理器
## 负责管理可调度对象的调度和执行，通过回调函数处理时间管理。

# 预加载Schedulable接口
const Schedulable = preload("res://scripts/gdscript/shared/interfaces/Schedulable.gd")

# 时间管理回调
var _get_time_callback: Callable
var _advance_time_callback: Callable
var _schedule_callback: Callable
var _remove_callback: Callable
var _peek_callback: Callable
var _pop_callback: Callable
var _is_slot_empty_callback: Callable

# 状态
var is_initialized: bool

# 事件执行回调
var on_event_executed: Callable

## 初始化CTB管理器
func _init(
    get_time_callback: Callable,
    advance_time_callback: Callable,
    schedule_callback: Callable,
    remove_callback: Callable,
    peek_callback: Callable,
    pop_callback: Callable,
    is_slot_empty_callback: Callable
):
    _get_time_callback = get_time_callback
    _advance_time_callback = advance_time_callback
    _schedule_callback = schedule_callback
    _remove_callback = remove_callback
    _peek_callback = peek_callback
    _pop_callback = pop_callback
    _is_slot_empty_callback = is_slot_empty_callback

    is_initialized = false


## 从时间轮中移除对象
func remove_event(schedulable_id: String) -> bool:
    return _remove_callback.call(schedulable_id)


## 标记CTB系统为已初始化
func initialize_ctb() -> void:
    is_initialized = true
    print("CTB系统初始化完成")

## 处理下一个逻辑回合
## 会推进时间直到找到下一个事件。
## 这是CTB系统的核心"回合"处理。
func process_next_turn() -> Dictionary:
    var ticks_advanced = 0
    while _is_slot_empty_callback.call():
        if ticks_advanced > 24 * 365:
            push_error("CTBManager advanced time for over a year without finding any event.")
            return {}
        _advance_time_callback.call()
        ticks_advanced += 1

    var due_event = get_due_event()
    if due_event != null:
        _execute_event(due_event)
        return {
            "type": "SCHEDULABLE_EXECUTED",
            "ticks_advanced": ticks_advanced,
            "schedulable_id": due_event.id,
            "schedulable_name": due_event.name,
            "schedulable_type": due_event.get_type_identifier(),
            "timestamp": _get_time_callback.call()
        }

    push_error("Inconsistent State: Slot was not empty, but no schedulable could be popped.")
    return {}

## 安排自定义可调度对象
func schedule_event(schedulable: Schedulable, trigger_time: int) -> bool:
    var current_time = _get_time_callback.call()
    if trigger_time < current_time:
        return false  # 不能在过去安排事件

    var delay = trigger_time - current_time
    return schedule_with_delay(schedulable.id, schedulable, delay)

## 使用延迟时间安排可调度对象
func schedule_with_delay(key: String, schedulable: Schedulable, delay: int) -> bool:
    return _schedule_callback.call(key, schedulable, delay)

## 获取当前时间到期的下一个可调度对象
func get_due_event() -> Schedulable:
    var result = _pop_callback.call()
    if result.is_empty():
        return null

    return result["value"]

## 执行单个可调度对象，包括更新内部逻辑、记录下次调度等
# 私有方法：执行单个可调度对象
func _execute_event(schedulable: Schedulable) -> void:
    var result = schedulable.execute()

    if on_event_executed.is_valid():
        on_event_executed.call(schedulable)

    # 如果需要重复调度，计算并调度下一次
    if schedulable.should_reschedule():
        var current_time = _get_time_callback.call()
        var next_time = schedulable.calculate_next_schedule_time(current_time)
        schedulable.trigger_time = next_time
        var delay = next_time - current_time
        schedule_with_delay(schedulable.id, schedulable, delay)



## 获取系统当前状态的文本描述
func get_status_text() -> String:
    if not is_initialized:
        return "CTB系统未初始化"

    var current_time = _get_time_callback.call()
    var status_lines = [
        "=== CTB系统状态 ===",
        "  当前时间: %d 小时" % current_time
    ]

    # 获取下一个对象
    var next_events = _peek_callback.call(1, 1)
    if next_events.size() > 0:
        var next_event_data = next_events[0]
        var next_obj = next_event_data["value"]
        var delay = next_obj.trigger_time - current_time
        if delay <= 0:
            status_lines.append("  下个调度: 待执行 (%s)" % next_obj.name)
        else:
            status_lines.append("  下个调度: %d 小时后 (%s)" % [delay, next_obj.name])
    else:
        status_lines.append("  下个调度: (无)")

    return "\n".join(status_lines)


## 获取下一个调度的时间信息
func get_next_schedule_time_info() -> String:
    var next_events = _peek_callback.call(1, 1)
    if next_events.is_empty():
        return "无"

    var current_time = _get_time_callback.call()
    var next_event_data = next_events[0]
    var next_obj = next_event_data["value"]
    var delay = next_obj.trigger_time - current_time

    if delay <= 0:
        return "待执行"
    else:
        return "%d小时后" % delay
