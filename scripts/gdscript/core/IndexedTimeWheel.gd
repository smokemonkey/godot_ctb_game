extends RefCounted
class_name IndexedTimeWheel

## A Time Wheel data structure - for event scheduling in a CTB (Conditional Turn-Based) system.
##
## Core Design:
## - Circular Buffer: Uses a fixed-size array for an efficient time window.
## - Linked List Slots: Each time slot uses a list to store events that trigger at the same time.
## - Dynamic Offset: An 'offset' pointer points to the current time slot (buffer design).
## - Generic Support: Can store any type of event object.
##
## Buffer Design Explanation:
## - The slot pointed to by 'offset' is the "action buffer for the current turn".
## - All events in this slot should be executed immediately.
## - Time advances only after all events in the current slot have been executed.
## - In the first turn of the game, the time wheel has not advanced at all.

## Internal node to store events within the IndexedTimeWheel
class EventNode:
    var key: Variant
    var value: Variant
    var slot_index: int  # When slot_index == -1, it indicates the event is in the _future_events list
    var absolute_hour: int

    func _init(p_key: Variant, p_value: Variant, p_slot_index: int, p_absolute_hour: int = -1):
        key = p_key
        value = p_value
        slot_index = p_slot_index
        absolute_hour = p_absolute_hour

    func _to_string() -> String:
        return "EventNode(Key=%s, Value=%s)" % [key, value]

var _buffer_size: int
var _get_time_callback: Callable

# Core circular buffer - each slot stores a list of events
var _slots: Array[Array]
var _offset: int

# Indexing and future events
var _index: Dictionary
var _future_events: Array  # Array of [absolute_hour, EventNode]
var _lock: Mutex

## An indexed, generic time wheel data structure with support for future events.
## internally uses a list for each slot, providing O(1) for add/pop but O(N) for removal by key.
## Tracks and removes events in O(1) from the index, but removal from the slot list is O(N)
## where N is the number of events in that slot.
func _init(buffer_size: int, get_time_callback: Callable):
    if buffer_size <= 0:
        push_error("Time wheel size must be positive.")
        return

    _buffer_size = buffer_size
    _get_time_callback = get_time_callback

    # Initialize slots
    _slots = []
    _slots.resize(_buffer_size)
    for i in range(_buffer_size):
        _slots[i] = []
    _offset = 0

    _index = {}
    _future_events = []
    _lock = Mutex.new()

## 私有的调度内核的正确方法
## 需要在已获得锁且保证条件正确后，对应调用此方法来执行实际的调度逻辑
func _schedule_internal(key: Variant, value: Variant, delay: int, now: int) -> void:
    # 此方法假设:
    # 1. 已经持有 lock 锁内。
    # 2. key 的唯一性和 delay 的非负性已经由调用方保证。
    # 3. now 是当前刚刚获取的当前时间。

    var absolute_hour = now + delay

    if delay >= _buffer_size:
        # 存储到未来事件
        var node = EventNode.new(key, value, -1, absolute_hour)
        _insert_future_event(absolute_hour, node)
        _index[key] = node
    else:
        # 存储到时间轮
        var target_index = (_offset + delay) % _buffer_size
        var node = EventNode.new(key, value, target_index, absolute_hour)
        _insert_to_wheel(node, target_index)
        _index[key] = node

## 根据延迟后调度事件，这是一个线程安全的包装方法
func schedule_with_delay(key: Variant, value: Variant, delay: int) -> void:
    _lock.lock()

    if _index.has(key):
        _lock.unlock()
        push_error("Key '%s' already exists." % key)
        return
    if delay < 0:
        _lock.unlock()
        push_error("Delay must be non-negative.")
        return

    var now = _get_time_callback.call()
    _schedule_internal(key, value, delay, now)

    _lock.unlock()
    # TODO: Notify UI to re-render after data changes.

## 在指定的绝对时间点安排事件，修复了原有的静态方法命名错误。
func schedule_at_absolute_hour(key: Variant, value: Variant, absolute_hour: int) -> void:
    _lock.lock()

    var now = _get_time_callback.call()
    if absolute_hour < now:
        _lock.unlock()
        push_error("Cannot schedule in the past.")
        return
    if _index.has(key):
        _lock.unlock()
        push_error("Key '%s' already exists." % key)
        return

    var delay = absolute_hour - now
    _schedule_internal(key, value, delay, now)

    _lock.unlock()
    # TODO: Notify UI to re-render after data changes.

## Inserts an event node into the specified target index slot.
func _insert_to_wheel(event_node: EventNode, target_index: int) -> void:
    _slots[target_index].append(event_node)

## Inserts a future event into the list, finding the correct sorted position by iterating backwards.
func _insert_future_event(absolute_hour: int, node: EventNode) -> void:
    # Find insertion point from the end of the list.
    var insert_index = 0
    for i in range(_future_events.size() - 1, -1, -1):
        if _future_events[i][0] <= absolute_hour:
            insert_index = i + 1
            break

    # Insert at the correct position to maintain sort order.
    _future_events.insert(insert_index, [absolute_hour, node])

## Checks if the current time slot is empty.
func _is_current_slot_empty() -> bool:
    return _slots[_offset].size() == 0

## Pops a due event from the head of the current time slot.
## Returns a Dictionary with 'key' and 'value', or null if the current slot is empty.
func pop_due_event() -> Dictionary:
    _lock.lock()

    if _is_current_slot_empty():
        _lock.unlock()
        return {}

    var node_to_pop: EventNode = _slots[_offset][0]
    _slots[_offset].pop_front()

    _index.erase(node_to_pop.key)

    _lock.unlock()
    # TODO: Notify UI to re-render after data changes.
    return {"key": node_to_pop.key, "value": node_to_pop.value}

## Advances the time wheel state: updates the offset and moves upcoming future events into the main wheel.
func advance_wheel() -> void:
    _lock.lock()

    if not _is_current_slot_empty():
        _lock.unlock()
        push_error("Cannot advance wheel: current slot is not empty.")
        return

    # Advance the offset by one position
    _offset = (_offset + 1) % _buffer_size

    # Check if any future events need to be moved to the main wheel
    # Since the list is sorted by absolute_hour, we only need to check the first element
    # Only move events when they are within the range of current_time + buffer_size - 1
    var time_threshold = _get_time_callback.call() + _buffer_size - 1
    while _future_events.size() > 0 and _future_events[0][0] <= time_threshold:
        var future_event = _future_events.pop_front()
        var absolute_hour = future_event[0]
        var node: EventNode = future_event[1]

        assert(absolute_hour == time_threshold, "This event should have been handled earlier.")

        # Insert the due future event into the farthest slot of the time wheel (offset - 1)
        # This way, the event will be triggered at the correct time as the wheel turns
        var target_index = (_offset - 1 + _buffer_size) % _buffer_size
        node.slot_index = target_index
        _insert_to_wheel(node, target_index)

    assert(_future_events.size() == 0 or _future_events[0][0] > _get_time_callback.call(),
           "Future events are not correctly ordered.")

    _lock.unlock()

## Removes an event from the time wheel or the future events list.
## Returns the value of the removed event, or null if the key is not found.
func remove(key: Variant) -> Variant:
    _lock.lock()

    if not _index.has(key):
        _lock.unlock()
        return null

    var node_to_remove: EventNode = _index[key]

    # Case 1: Event is in the future pool, remove it directly from the list
    if node_to_remove.slot_index == -1:
        # Remove from the future events list
        for i in range(_future_events.size() - 1, -1, -1):
            if _future_events[i][1].key == key:
                _future_events.remove_at(i)
                break
    # Case 2: Event is in the time wheel, remove it from the corresponding slot's list
    else:
        var slot_events = _slots[node_to_remove.slot_index]
        for i in range(slot_events.size() - 1, -1, -1):
            if slot_events[i].key == key:
                slot_events.remove_at(i)
                break

    _index.erase(key)

    _lock.unlock()
    # TODO: Notify UI to re-render after data changes.
    return node_to_remove.value

## [For UI Rendering Only] Previews upcoming events within the next 'count' hours.
##
## Important: This method is designed for UI display or debugging and should not be used for core game loop logic.
## It may return imprecise or incomplete event data for UI convenience.
## The game loop should use advance_wheel() and pop_due_event().
##
## Returns up to 'count' upcoming events within 'max_hours' time range
## Parameters:
##   count: Maximum number of events to return
##   max_hours: Maximum hours to search (-1 for all available slots)
func peek_upcoming_events(count: int, max_hours: int = -1) -> Array[Dictionary]:
    if count <= 0:
        return []

    _lock.lock()

    var events: Array[Dictionary] = []
    var hours_to_search = max_hours if max_hours > 0 else _buffer_size

    # 遍历指定小时数的槽位
    for i in range(hours_to_search):
        var index = (_offset + i) % _buffer_size
        var current_nodes = _slots[index]

        for node in current_nodes:
            events.append({"key": node.key, "value": node.value})
            # 达到指定事件数量就返回
            if events.size() >= count:
                var result = events.slice(0, count)
                _lock.unlock()
                return result

    _lock.unlock()
    return events

## Gets the value of a scheduled event by its key.
## Returns the value of the event, or null if not found.
func get_event(key: Variant) -> Variant:
    _lock.lock()

    if _index.has(key):
        var result = _index[key].value
        _lock.unlock()
        return result

    _lock.unlock()
    return null

## Checks if a key exists in the time wheel.
func contains(key: Variant) -> bool:
    _lock.lock()
    var result = _index.has(key)
    _lock.unlock()
    return result

## Returns the total number of scheduled events.
func get_count() -> int:
    _lock.lock()
    var result = _index.size()
    _lock.unlock()
    return result

## Checks if there are any events in the time wheel or in the future events list.
func has_any_events() -> bool:
    _lock.lock()
    var result = _index.size() > 0
    _lock.unlock()
    return result
