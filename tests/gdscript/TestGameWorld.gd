extends RefCounted
class_name TestGameWorld

# 预加载需要的类
const Schedulable = preload("res://scripts/gdscript/shared/interfaces/Schedulable.gd")
const Calendar = preload("res://scripts/gdscript/core/Calendar.gd")
const IndexedTimeWheel = preload("res://scripts/gdscript/core/IndexedTimeWheel.gd")
const CTBManager = preload("res://scripts/gdscript/core/CTBManager.gd")
const EventExample = preload("res://scripts/gdscript/development/EventExample.gd")

## 简单事件创建函数 - 使用EventExample替代SimpleEvent
static func create_simple_event(p_id: String, p_description: String) -> EventExample:
    var event = EventExample.new(p_id, p_description, "事件")
    # 设置为不重复调度的事件
    event.reschedule_enabled = false
    return event

## 统一的游戏世界测试协调器 - GDScript版本
##
## 这个类将Calendar、IndexedTimeWheel和CTBManager整合为一个
## 统一的测试接口，简化了集成测试。

# 核心系统组件
var calendar
var time_wheel
var ctb_manager

# 事件回调信号
signal event_executed(event_description: String)
signal time_advanced(hours: int)
signal systems_updated()

## 初始化测试世界
func _init(time_wheel_size: int = 0):
    # 如果没有指定大小，使用配置中的默认值
    var default_size = 180 * 24 # 默认缓冲区大小
    if ConfigManager != null and ConfigManager.config != null:
        default_size = ConfigManager.ctb_time_wheel_buffer_size
    var actual_size = time_wheel_size if time_wheel_size > 0 else default_size

    # 初始化日历
    calendar = Calendar.new()

    # 初始化时间轮，使用日历的获取时间方法
    time_wheel = IndexedTimeWheel.new(actual_size, calendar.get_timestamp)

    # 初始化CTB管理器，连接到时间轮
    ctb_manager = CTBManager.new(
        calendar.get_timestamp,          # get_time_callback
        _advance_time_callback,          # advance_time_callback
        _schedule_callback,              # schedule_callback
        _remove_callback,                # remove_callback
        _peek_callback,                  # peek_callback
        _pop_callback,                   # pop_callback
        _is_slot_empty_callback          # is_slot_empty_callback
    )

    # 连接CTB管理器的事件执行回调
    ctb_manager.on_event_executed = _on_event_executed

## 时间轮回调实现
func _advance_time_callback() -> void:
    calendar.advance_time_tick()
    time_wheel.advance_wheel()

func _schedule_callback(key: String, event: Variant, delay: int) -> bool:
    time_wheel.schedule_with_delay(key, event, delay)
    return true

func _remove_callback(key: String) -> bool:
    var removed = time_wheel.remove(key)
    return removed != null

func _peek_callback(count: int, max_hours: int) -> Array:
    var upcoming = time_wheel.peek_upcoming_events(count, max_hours)
    var result = []
    for event_dict in upcoming:
        result.append({"key": event_dict["key"], "value": event_dict["value"]})
    return result

func _pop_callback() -> Dictionary:
    return time_wheel.pop_due_event()

func _is_slot_empty_callback() -> bool:
    return time_wheel._is_current_slot_empty()

## 事件执行回调
func _on_event_executed(event) -> void:
    var description = ""
    if event.has_method("_to_string"):
        description = event._to_string()
    else:
        description = str(event)

    event_executed.emit(description)
    systems_updated.emit()

## 公共API方法

## 获取当前时间
var current_time: int:
    get:
        return calendar.get_timestamp()

## 获取当前日历时间（公历格式）
var current_calendar_time: String:
    get:
        return calendar.format_date_gregorian(true)

## 获取当前纪年时间
var current_era_time: String:
    get:
        return calendar.format_date_era(true)

## 推进时间（遇到事件时停下）
func advance_time(hours: int) -> Dictionary:
    var initial_time = current_time
    var hours_advanced = 0
    var stopped_for_event = false

    for i in range(hours):
        # 先检查当前槽是否有事件
        if not time_wheel._is_current_slot_empty():
            stopped_for_event = true
            break

        # 推进一小时
        calendar.advance_time_tick()
        time_wheel.advance_wheel()
        hours_advanced += 1

        # 推进后再次检查是否有新事件到期
        if not time_wheel._is_current_slot_empty():
            stopped_for_event = true
            break

    if hours_advanced > 0:
        time_advanced.emit(hours_advanced)
        systems_updated.emit()

    var summary = ""
    if stopped_for_event:
        summary = "推进了%d小时后遇到事件，已停止" % hours_advanced
    else:
        summary = "推进了%d小时" % hours_advanced

    return {
        "hours_advanced": hours_advanced,
        "current_time": current_time,
        "stopped_for_event": stopped_for_event,
        "summary": summary
    }

## 推进到下一个事件（不执行事件）
func advance_to_next_event(max_hours: int = 100) -> Dictionary:
    var initial_time = current_time
    var hours_advanced = 0
    var found_event = false

    # 最多推进max_hours小时寻找事件
    while hours_advanced < max_hours:
        if not time_wheel._is_current_slot_empty():
            # 找到事件，停止推进，不执行事件
            found_event = true
            break

        # 推进一小时
        calendar.advance_time_tick()
        time_wheel.advance_wheel()
        hours_advanced += 1

    if hours_advanced > 0:
        time_advanced.emit(hours_advanced)
        systems_updated.emit()

    return {
        "hours_advanced": hours_advanced,
        "found_event": found_event,
        "current_time": current_time
    }

## 执行当前到期事件（不推进时间，一次只执行一个事件）
func execute_due_event() -> Dictionary:
    var event_executed = ""
    var current_time = calendar.get_timestamp()
    var found_event = false

    # 只执行当前槽的一个事件
    if not time_wheel._is_current_slot_empty():
        var event_data = time_wheel.pop_due_event()
        if not event_data.is_empty():
            var event = event_data["value"]
            ctb_manager._execute_event(event)
            event_executed = str(event)
            found_event = true
            systems_updated.emit()

    return {
        "event_executed": event_executed,
        "found_event": found_event,
        "current_time": current_time
    }

## 安排事件
func schedule_event(key: String, description: String, delay_hours: int) -> void:
    # 创建一个简单的可调度对象
    var event = create_simple_event(key, description)
    # 手动设置触发时间
    event.trigger_time = current_time + delay_hours
    time_wheel.schedule_with_delay(key, event, delay_hours)
    systems_updated.emit()

## 添加示例角色（开发用）
func add_example_event(id: String, name: String, faction: String = "中立") -> EventExample:
    var actor = EventExample.new(id, name, faction)
    var current_time = calendar.get_timestamp()
    var delay = actor.calculate_next_schedule_time(current_time) - current_time
    ctb_manager.schedule_with_delay(id, actor, delay)
    return actor

## 初始化CTB系统（为角色安排初始行动）
func initialize_ctb() -> void:
    ctb_manager.initialize_ctb()
    systems_updated.emit()

## 锚定纪元
func anchor_era(era_name: String, gregorian_year: int) -> void:
    calendar.anchor_era(era_name, gregorian_year)
    systems_updated.emit()

## 开始新纪元
func start_new_era(era_name: String) -> void:
    calendar.start_new_era(era_name)
    systems_updated.emit()

## 重置系统
func reset() -> void:
    calendar.reset()
    # 重新初始化时间轮
    var buffer_size = time_wheel._buffer_size
    time_wheel = IndexedTimeWheel.new(buffer_size, calendar.get_timestamp)

    # 重新初始化CTB管理器
    ctb_manager = CTBManager.new(
        calendar.get_timestamp,
        _advance_time_callback,
        _schedule_callback,
        _remove_callback,
        _peek_callback,
        _pop_callback,
        _is_slot_empty_callback
    )
    ctb_manager.on_event_executed = _on_event_executed

    systems_updated.emit()

## 清空所有事件
func clear_all_events() -> void:
    # 重新创建时间轮以清空所有事件
    var buffer_size = time_wheel._buffer_size
    time_wheel = IndexedTimeWheel.new(buffer_size, calendar.get_timestamp)

    # 重新连接CTB管理器
    ctb_manager._schedule_callback = _schedule_callback
    ctb_manager._remove_callback = _remove_callback
    ctb_manager._peek_callback = _peek_callback
    ctb_manager._pop_callback = _pop_callback
    ctb_manager._is_slot_empty_callback = _is_slot_empty_callback

    systems_updated.emit()

## 获取即将到来的事件
## 参数：
##   count: 最多返回多少个事件
##   max_hours: 查看多少小时内的事件（-1表示查看所有槽位）
func get_upcoming_events(count: int, max_hours: int = -1) -> Array:
    var upcoming = time_wheel.peek_upcoming_events(count, max_hours)
    var result = []
    var current_time = calendar.get_timestamp()
    for event_dict in upcoming:
        var delay_hours = event_dict["trigger_time"] - current_time
        result.append([event_dict["key"], event_dict["value"], delay_hours])
    return result

## 获取日历信息
func get_calendar_info() -> Dictionary:
    return calendar.get_time_info()

## 获取状态摘要
func get_status_summary() -> String:
    var info = [
        "时间: %d小时" % current_time,
        "事件数: %d" % event_count,
        "有事件: %s" % ("是" if has_any_events else "否"),
        "当前槽空: %s" % ("是" if is_current_slot_empty else "否")
    ]
    return " | ".join(info)

## 属性访问器
var event_count: int:
    get:
        return time_wheel.get_count()

var has_any_events: bool:
    get:
        return time_wheel.has_any_events()

var is_current_slot_empty: bool:
    get:
        return time_wheel._is_current_slot_empty()
