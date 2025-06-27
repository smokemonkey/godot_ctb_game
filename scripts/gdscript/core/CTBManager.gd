extends RefCounted
class_name CTBManager

## CTB系统管理器
## 负责管理可调度对象的调度和执行，通过回调函数处理时间管理。

# 时间管理回调
var _get_time_callback: Callable
var _advance_time_callback: Callable
var _schedule_callback: Callable
var _remove_callback: Callable
var _peek_callback: Callable
var _pop_callback: Callable
var _is_slot_empty_callback: Callable

# 状态
var scheduled_objects: Dictionary  # 替换原来的characters
var is_initialized: bool
var action_history: Array[Dictionary]

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
	
	scheduled_objects = {}
	is_initialized = false
	action_history = []

## 添加可调度对象到系统
func add_schedulable(schedulable: Schedulable) -> void:
	if scheduled_objects.has(schedulable.id):
		push_error("Schedulable with ID %s already exists" % schedulable.id)
		return
	
	scheduled_objects[schedulable.id] = schedulable
	print("已添加可调度对象: %s" % schedulable.name)

## 从系统中移除可调度对象
func remove_schedulable(schedulable_id: String) -> bool:
	if not scheduled_objects.has(schedulable_id):
		return false
	
	# 从时间轮中移除对象的事件
	_remove_callback.call(schedulable_id)
	
	# 从对象字典中移除
	var removed_obj = scheduled_objects[schedulable_id]
	scheduled_objects.erase(schedulable_id)
	print("已移除可调度对象: %s" % removed_obj.name)
	return true

## 获取可调度对象
func get_schedulable(schedulable_id: String) -> Schedulable:
	if scheduled_objects.has(schedulable_id):
		return scheduled_objects[schedulable_id]
	return null

## 初始化CTB系统
## 为所有可调度对象排程初始调度时间
func initialize_ctb() -> void:
	if scheduled_objects.is_empty():
		push_error("Cannot initialize CTB without schedulable objects")
		return
	
	var current_time = _get_time_callback.call()
	print("初始化CTB系统，当前时间: %d" % current_time)
	
	# 为每个可调度对象排程初始调度
	for obj in scheduled_objects.values():
		if obj.should_reschedule():
			# 计算初始调度时间
			var next_time = obj.calculate_next_schedule_time(current_time)
			obj.trigger_time = next_time
			
			# 添加到时间轮
			var delay = next_time - current_time
			_schedule_callback.call(obj.id, obj, delay)
			print("已为 %s 安排初始调度，延迟: %d 小时" % [obj.name, delay])
	
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
	
	var due_schedulable = get_due_schedulable()
	if due_schedulable != null:
		execute_schedulable(due_schedulable)
		return {
			"type": "SCHEDULABLE_EXECUTED",
			"ticks_advanced": ticks_advanced,
			"schedulable_id": due_schedulable.id,
			"schedulable_name": due_schedulable.name,
			"schedulable_type": due_schedulable.get_type_identifier(),
			"timestamp": _get_time_callback.call()
		}
	
	push_error("Inconsistent State: Slot was not empty, but no schedulable could be popped.")
	return {}

## 安排自定义可调度对象
func schedule_schedulable(schedulable: Schedulable, trigger_time: int) -> bool:
	var current_time = _get_time_callback.call()
	if trigger_time < current_time:
		return false  # 不能在过去安排事件
	
	var delay = trigger_time - current_time
	return schedule_with_delay(schedulable.id, schedulable, delay)

## 使用延迟时间安排可调度对象
func schedule_with_delay(key: String, schedulable: Schedulable, delay: int) -> bool:
	return _schedule_callback.call(key, schedulable, delay)

## 获取当前时间到期的下一个可调度对象
func get_due_schedulable() -> Schedulable:
	var result = _pop_callback.call()
	if result.is_empty():
		return null
	
	return result["value"]

## 执行可调度对象列表
func execute_schedulables(schedulables: Array[Schedulable]) -> void:
	for schedulable in schedulables:
		execute_schedulable(schedulable)

## 执行单个可调度对象，包括更新内部逻辑、记录下次调度等
func execute_schedulable(schedulable: Schedulable) -> void:
	var result = schedulable.execute()
	record_action(schedulable)
	
	if on_event_executed.is_valid():
		on_event_executed.call(schedulable)
	
	# 如果需要重复调度，计算并调度下一次
	if schedulable.should_reschedule():
		var current_time = _get_time_callback.call()
		var next_time = schedulable.calculate_next_schedule_time(current_time)
		schedulable.trigger_time = next_time
		var delay = next_time - current_time
		schedule_with_delay(schedulable.id, schedulable, delay)

## 记录行动历史
func record_action(schedulable: Schedulable) -> void:
	var current_time = _get_time_callback.call()
	var record = {
		"schedulable_name": schedulable.name,
		"schedulable_type": schedulable.get_type_identifier(),
		"timestamp": current_time
	}
	action_history.append(record)

## 设置可调度对象的活跃状态（仅对SchedulableExample有效）
func set_schedulable_active(schedulable_id: String, active: bool) -> bool:
	var schedulable = get_schedulable(schedulable_id)
	if schedulable == null:
		return false
	
	# 检查是否是SchedulableExample类型
	if schedulable is SchedulableExample:
		var combat_actor = schedulable as SchedulableExample
		combat_actor.set_active(active)
		
		# 如果设置为非活跃，从时间轮中移除其尚未执行的调度
		if not active:
			_remove_callback.call(schedulable_id)
		# 如果重新激活，需要手动为其安排下一次调度
		elif active:
			var current_time = _get_time_callback.call()
			var next_time = combat_actor.calculate_next_schedule_time(current_time)
			combat_actor.trigger_time = next_time
			var delay = next_time - current_time
			schedule_with_delay(combat_actor.id, combat_actor, delay)
		
		return true
	
	return false

## 获取系统当前状态的文本描述
func get_status_text() -> String:
	if not is_initialized:
		return "CTB系统未初始化"
	
	var current_time = _get_time_callback.call()
	var active_count = 0
	for obj in scheduled_objects.values():
		if obj.should_reschedule():
			active_count += 1
	
	var status_lines = [
		"=== CTB系统状态 ===",
		"  当前时间: %d 小时" % current_time,
		"  对象总数: %d" % scheduled_objects.size(),
		"  活跃对象: %d" % active_count
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

## 获取所有可调度对象信息
func get_schedulable_info() -> Array[Dictionary]:
	var info_list: Array[Dictionary] = []
	var current_time = _get_time_callback.call()
	
	for obj in scheduled_objects.values():
		var info = {
			"id": obj.id,
			"name": obj.name,
			"type": obj.get_type_identifier(),
			"should_reschedule": obj.should_reschedule()
		}
		
		# 尝试从时间轮中获取下次调度时间
		var events = _peek_callback.call(1, 1)
		for event_data in events:
			var key = event_data["key"]
			var event = event_data["value"]
			if key == obj.id:
				info["next_schedule_time"] = event.trigger_time
				info["time_until_schedule"] = event.trigger_time - current_time
				break
		
		# 如果是SchedulableExample，添加额外信息
		if obj is SchedulableExample:
			var combat_actor = obj as SchedulableExample
			info["faction"] = combat_actor.faction
			info["is_active"] = combat_actor.is_active
		
		info_list.append(info)
	
	return info_list

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