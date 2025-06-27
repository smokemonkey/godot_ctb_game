extends RefCounted
class_name CTBManager

## 事件类型枚举
enum EventType {
	CHARACTER_ACTION,  # 角色行动
	SEASON_CHANGE,     # 季节变化
	WEATHER_CHANGE,    # 天气变化
	STORY_EVENT,       # 剧情事件
	CUSTOM             # 自定义事件
}

## 事件基类
## 在CTB系统中的事件都应该继承此类。
class Event:
	var id: String
	var name: String
	var event_type: EventType
	var trigger_time: int
	var description: String
	
	func _init(p_id: String, p_name: String, p_event_type: EventType, p_trigger_time: int, p_description: String = ""):
		id = p_id
		name = p_name
		event_type = p_event_type
		trigger_time = p_trigger_time
		description = p_description
	
	## 执行事件
	## 子类应该重写此方法实现具体的事件逻辑。
	func execute() -> Variant:
		push_error("Event.execute() must be overridden in subclass")
		return null
	
	func _to_string() -> String:
		return "%s (%s)" % [name, EventType.keys()[event_type]]

## 游戏角色
## 角色是一个特殊的事件，其Execute方法执行角色的行动。
class Character extends Event:
	var faction: String
	var is_active: bool
	
	func _init(p_id: String, p_name: String, p_faction: String = "中立"):
		super._init(p_id, p_name, EventType.CHARACTER_ACTION, 0, "%s的行动" % p_name)
		faction = p_faction
		is_active = true
	
	## 计算下次行动时间
	## 使用三角分布，在1-180天之间随机，峰值在90天
	## 峰值：90天，符合现实的分布。
	func calculate_next_action_time(current_time: int) -> int:
		# 使用三角分布（最小1天，最大180天，峰值90天）
		var days = _triangular_distribution(1, 180, 90)
		var hours = int(days * 24)
		return current_time + hours
	
	## 三角分布实现
	func _triangular_distribution(min_val: float, max_val: float, mode: float) -> float:
		var u = randf()
		var c = (mode - min_val) / (max_val - min_val)
		
		if u < c:
			return min_val + sqrt(u * (max_val - min_val) * (mode - min_val))
		else:
			return max_val - sqrt((1 - u) * (max_val - min_val) * (max_val - mode))
	
	## 执行角色行动
	func execute() -> Variant:
		# 这里可以添加角色行动的具体逻辑
		# 例如：发动战斗、使用技能、移动等
		return self

## CTB系统管理器
## 负责管理事件的调度和执行，通过回调函数处理时间管理。
var _get_time_callback: Callable
var _advance_time_callback: Callable
var _schedule_callback: Callable
var _remove_callback: Callable
var _peek_callback: Callable
var _pop_callback: Callable
var _is_slot_empty_callback: Callable

# 状态
var characters: Dictionary
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
	
	characters = {}
	is_initialized = false
	action_history = []

## 添加角色到系统
func add_character(character: Character) -> void:
	if characters.has(character.id):
		push_error("Character with ID %s already exists" % character.id)
		return
	
	characters[character.id] = character

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
		execute_event(due_event)
		return {
			"type": "EVENT_EXECUTED",
			"ticks_advanced": ticks_advanced,
			"event_id": due_event.id,
			"event_name": due_event.name,
			"event_type": EventType.keys()[due_event.event_type],
			"timestamp": _get_time_callback.call()
		}
	
	push_error("Inconsistent State: Slot was not empty, but no event could be popped.")
	return {}

## 从系统中移除角色
func remove_character(character_id: String) -> bool:
	if not characters.has(character_id):
		return false
	
	# 从时间轮中移除角色的事件
	_remove_callback.call(character_id)
	
	# 从角色字典中移除
	characters.erase(character_id)
	return true

## 获取角色
func get_character(character_id: String) -> Character:
	if characters.has(character_id):
		return characters[character_id]
	return null

## 初始化CTB系统
## 为所有角色排程初始行动时间。
func initialize_ctb() -> void:
	if characters.is_empty():
		push_error("Cannot initialize CTB without characters")
		return
	
	var current_time = _get_time_callback.call()
	
	# 为每个活跃角色排程初始行动
	for character in characters.values():
		if character.is_active:
			# 计算初始行动时间
			var next_time = character.calculate_next_action_time(current_time)
			character.trigger_time = next_time
			
			# 添加到时间轮
			var delay = next_time - current_time
			_schedule_callback.call(character.id, character, delay)
	
	is_initialized = true

## 安排自定义事件
func schedule_event(event: Event, trigger_time: int) -> bool:
	var current_time = _get_time_callback.call()
	if trigger_time < current_time:
		return false  # 不能在过去安排事件
	
	var delay = trigger_time - current_time
	return schedule_with_delay(event.id, event, delay)

## 使用延迟时间安排事件
func schedule_with_delay(key: String, event: Event, delay: int) -> bool:
	return _schedule_callback.call(key, event, delay)

## 获取当前时间到期的下一个事件
func get_due_event() -> Event:
	var result = _pop_callback.call()
	if result.is_empty():
		return null
	
	return result["value"]

## 执行事件列表
func execute_events(events: Array[Event]) -> void:
	for event in events:
		execute_event(event)

## 执行单个事件，包括更新内部逻辑、记录下次调度等
func execute_event(event: Event) -> void:
	var result = event.execute()
	record_action(event)
	
	if on_event_executed.is_valid():
		on_event_executed.call(event)
	
	# 如果是角色行动，计算并调度下一次行动
	if event.event_type == EventType.CHARACTER_ACTION and event is Character:
		var character = event as Character
		if character.is_active:
			var current_time = _get_time_callback.call()
			var next_time = character.calculate_next_action_time(current_time)
			character.trigger_time = next_time
			var delay = next_time - current_time
			schedule_with_delay(character.id, character, delay)

## 记录行动历史
func record_action(event: Event) -> void:
	var current_time = _get_time_callback.call()
	var record = {
		"event_name": event.name,
		"event_type": EventType.keys()[event.event_type],
		"timestamp": current_time
	}
	action_history.append(record)

## 设置角色的活跃状态
## 当一个角色被设置为非活跃时，其尚未执行的行动会被取消。
## 如果当前队列中有行动，行动会被取消。
func set_character_active(character_id: String, active: bool) -> bool:
	var character = get_character(character_id)
	if character == null:
		return false
	
	character.is_active = active
	
	# 如果角色被设置为非活跃，从时间轮中移除其尚未执行的行动
	if not active:
		_remove_callback.call(character_id)
	# 如果角色重新激活，需要手动为其安排下一次行动
	elif active:
		var current_time = _get_time_callback.call()
		var next_time = character.calculate_next_action_time(current_time)
		character.trigger_time = next_time
		var delay = next_time - current_time
		schedule_with_delay(character.id, character, delay)
	
	return true

## 获取系统当前状态的文本描述
func get_status_text() -> String:
	if not is_initialized:
		return "CTB系统未初始化"
	
	var current_time = _get_time_callback.call()
	var active_characters = 0
	for character in characters.values():
		if character.is_active:
			active_characters += 1
	
	var status_lines = [
		"=== CTB系统状态 ===",
		"  当前时间: %d 小时" % current_time,
		"  角色总数: %d" % characters.size(),
		"  活跃角色: %d" % active_characters
	]
	
	# 获取下一个事件
	var next_events = _peek_callback.call(1, 1)
	if next_events.size() > 0:
		var next_event_data = next_events[0]
		var next_event = next_event_data["value"]
		var delay = next_event.trigger_time - current_time
		if delay <= 0:
			status_lines.append("  下个行动: 待执行 (%s)" % next_event.name)
		else:
			status_lines.append("  下个行动: %d 小时后 (%s)" % [delay, next_event.name])
	else:
		status_lines.append("  下个行动: (无)")
	
	return "\n".join(status_lines)

## 获取所有角色信息
func get_character_info() -> Array[Dictionary]:
	var info_list: Array[Dictionary] = []
	var current_time = _get_time_callback.call()
	
	for character in characters.values():
		var info = {
			"id": character.id,
			"name": character.name,
			"faction": character.faction,
			"is_active": character.is_active
		}
		
		# 尝试从时间轮中获取下次行动时间
		var events = _peek_callback.call(1, 1)
		for event_data in events:
			var key = event_data["key"]
			var event = event_data["value"]
			if key == character.id:
				info["next_action_time"] = event.trigger_time
				info["time_until_action"] = event.trigger_time - current_time
				break
		
		info_list.append(info)
	
	return info_list

## 获取下一个行动的时间信息
func get_next_action_time_info() -> String:
	var next_events = _peek_callback.call(1, 1)
	if next_events.is_empty():
		return "无"
	
	var current_time = _get_time_callback.call()
	var next_event_data = next_events[0]
	var next_event = next_event_data["value"]
	var delay = next_event.trigger_time - current_time
	
	if delay <= 0:
		return "待执行"
	else:
		return "%d小时后" % delay