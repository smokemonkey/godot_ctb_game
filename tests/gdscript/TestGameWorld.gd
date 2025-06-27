extends RefCounted
class_name TestGameWorld

## 简单事件类 - 用于测试
class SimpleEvent extends Schedulable:
	func _init(p_id: String, p_description: String, p_trigger_time: int):
		super._init(p_id, p_description, p_description)
		trigger_time = p_trigger_time
	
	func execute() -> Variant:
		print("执行事件: %s" % description)
		return self
	
	func calculate_next_schedule_time(current_time: int) -> int:
		return current_time  # 简单事件不重复
	
	func should_reschedule() -> bool:
		return false
	
	func get_type_identifier() -> String:
		return "SimpleEvent"

## 统一的游戏世界测试协调器 - GDScript版本
## 
## 这个类将Calendar、IndexedTimeWheel和CTBManager整合为一个
## 统一的测试接口，简化了集成测试。

# 核心系统组件
var calendar: Calendar
var time_wheel: IndexedTimeWheel
var ctb_manager: CTBManager

# 事件回调信号
signal event_executed(event_description: String)
signal time_advanced(hours: int)
signal systems_updated()

## 初始化测试世界
func _init(time_wheel_size: int = 0):
	# 如果没有指定大小，使用配置中的默认值
	var actual_size = time_wheel_size if time_wheel_size > 0 else ConfigManager.ctb_time_wheel_buffer_size
	
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

## 推进时间
func advance_time(hours: int) -> Dictionary:
	var initial_time = current_time
	
	for i in range(hours):
		calendar.advance_time_tick()
		
		# 检查是否有事件需要从future pool移动到主时间轮
		if not time_wheel._is_current_slot_empty():
			# 处理当前时间槽的所有事件
			while not time_wheel._is_current_slot_empty():
				var event_data = time_wheel.pop_due_event()
				if not event_data.is_empty():
					var event = event_data["value"]
					ctb_manager.execute_schedulable(event)
		
		# 推进时间轮
		time_wheel.advance_wheel()
	
	var hours_advanced = current_time - initial_time
	time_advanced.emit(hours_advanced)
	systems_updated.emit()
	
	return {
		"hours_advanced": hours_advanced,
		"current_time": current_time,
		"summary": "推进了%d小时" % hours_advanced
	}

## 推进到下一个事件
func advance_to_next_event(max_hours: int = 100) -> Dictionary:
	var initial_time = current_time
	var events_executed = []
	var hours_advanced = 0
	
	# 最多推进max_hours小时寻找事件
	while hours_advanced < max_hours:
		if not time_wheel._is_current_slot_empty():
			# 执行当前槽的所有事件
			while not time_wheel._is_current_slot_empty():
				var event_data = time_wheel.pop_due_event()
				if not event_data.is_empty():
					var event = event_data["value"]
					ctb_manager.execute_schedulable(event)
					events_executed.append(str(event))
			break
		
		# 推进一小时
		calendar.advance_time_tick()
		time_wheel.advance_wheel()
		hours_advanced += 1
	
	if events_executed.size() > 0:
		time_advanced.emit(hours_advanced)
		systems_updated.emit()
	
	return {
		"hours_advanced": hours_advanced,
		"events_executed": events_executed,
		"current_time": current_time
	}

## 安排事件
func schedule_event(key: String, description: String, delay_hours: int) -> void:
	# 创建一个简单的可调度对象
	var event = SimpleEvent.new(key, description, current_time + delay_hours)
	time_wheel.schedule_with_delay(key, event, delay_hours)
	systems_updated.emit()

## 添加战斗角色
func add_combat_actor(id: String, name: String, faction: String = "中立") -> CombatActor:
	var actor = CombatActor.new(id, name, faction)
	ctb_manager.add_schedulable(actor)
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
func get_upcoming_events(hours: int, max_events: int = -1) -> Array:
	var upcoming = time_wheel.peek_upcoming_events(hours, max_events)
	var result = []
	for event_dict in upcoming:
		result.append([event_dict["key"], event_dict["value"]])
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