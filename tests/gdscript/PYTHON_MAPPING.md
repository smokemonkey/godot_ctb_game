# GDScript → Python Mapping

This file documents the correspondence between GDScript and Python implementations.

## Core Systems Mapping

### Calendar System
- **GDScript**: `tests/gdscript/Calendar.gd`
- **Python**: `python_prototypes/core/calendar.py`
- **Status**: Feature complete, fully synchronized
- **API Correspondence**:
  - `Calendar.new()` ↔ `Calendar()`
  - `advance_time_tick()` ↔ `advance_time_tick()`
  - `get_timestamp()` ↔ `get_timestamp()`
  - `get_time_info()` ↔ `get_time_info()`
  - `format_date_gregorian()` ↔ `format_date_gregorian()`
  - `format_date_era()` ↔ `format_date_era()`
  - `anchor_era()` ↔ `anchor_era()`
  - `start_new_era()` ↔ `start_new_era()`
  - `reset()` ↔ `reset()`

### IndexedTimeWheel System
- **GDScript**: `tests/gdscript/IndexedTimeWheel.gd`
- **Python**: `python_prototypes/core/indexed_time_wheel.py`
- **Status**: Feature complete, thread safety adapted for GDScript
- **API Correspondence**:
  - `IndexedTimeWheel.new(size, callback)` ↔ `IndexedTimeWheel(size, callback)`
  - `schedule_with_delay()` ↔ `schedule_with_delay()`
  - `schedule_at_absolute_hour()` ↔ `schedule_at_absolute_hour()`
  - `pop_due_event()` ↔ `pop_due_event()`
  - `advance_wheel()` ↔ `advance_wheel()`
  - `remove()` ↔ `remove()`
  - `peek_upcoming_events()` ↔ `peek_upcoming_events()`
  - `get_event()` ↔ `get()`
  - `contains()` ↔ `contains()`
  - `get_count()` ↔ `count` (property)
  - `has_any_events()` ↔ `has_any_events()`

### CTBManager System
- **GDScript**: `tests/gdscript/CTBManager.gd`
- **Python**: `python_prototypes/core/ctb_manager.py`
- **Status**: Feature complete, event system adapted for GDScript signals
- **API Correspondence**:
  - `CTBManager.new()` ↔ `CTBManager()`
  - `add_character()` ↔ `add_character()`
  - `remove_character()` ↔ `remove_character()`
  - `get_character()` ↔ `get_character()`
  - `initialize_ctb()` ↔ `initialize_ctb()`
  - `process_next_turn()` ↔ `process_next_turn()`
  - `schedule_event()` ↔ `schedule_event()`
  - `schedule_with_delay()` ↔ `schedule_with_delay()`
  - `execute_event()` ↔ `execute_event()`
  - `set_character_active()` ↔ `set_character_active()`
  - `get_status_text()` ↔ `get_status_text()`

### Unified Test Coordinator
- **GDScript**: `tests/gdscript/TestGameWorld.gd`
- **Python**: `python_prototypes/core/game_world.py`
- **Status**: Feature complete, signal-based event system
- **API Correspondence**:
  - `TestGameWorld.new()` ↔ `GameWorld()`
  - `current_time` ↔ `current_time`
  - `current_calendar_time` ↔ `current_calendar_time`
  - `advance_time()` ↔ `advance_time()`
  - `schedule_event()` ↔ `schedule_event()`
  - `anchor_era()` ↔ `anchor_era()`
  - `start_new_era()` ↔ `start_new_era()`
  - `reset()` ↔ `reset()`
  - `get_status_summary()` ↔ `get_status_summary()`

## Event System Mapping

### Event Classes
- **GDScript**: `CTBManager.Event` (base class)
- **Python**: `Event` (base class)
- **GDScript**: `CTBManager.Character` (extends Event)
- **Python**: `Character` (extends Event)

### Event Types
- **GDScript**: `CTBManager.EventType` enum
- **Python**: `EventType` enum
- **Values**: CHARACTER_ACTION, SEASON_CHANGE, WEATHER_CHANGE, STORY_EVENT, CUSTOM

## Testing Integration

### UI Test Interface
- **GDScript**: `tests/gdscript/IntegratedSystemTest.gd`
- **Python**: N/A (web-based demos in `examples/`)
- **Scene**: `scenes/gdscript_integrated_test.tscn`

### Functional Tests
- **GDScript**: `tests/gdscript/test_gdscript_systems.gd`
- **Python**: `python_prototypes/tests/` (unittest framework)

## Technical Differences

### Language-Specific Adaptations

1. **Thread Safety**:
   - **GDScript**: Uses `Mutex` class for thread synchronization
   - **Python**: Uses `threading.Lock()` for thread synchronization

2. **Error Handling**:
   - **GDScript**: Uses `push_error()` for error reporting
   - **Python**: Uses `raise Exception()` for error handling

3. **Event System**:
   - **GDScript**: Uses Godot signals (`signal event_executed`, `emit()`)
   - **Python**: Uses callback functions and direct method calls

4. **Type System**:
   - **GDScript**: Uses `Variant` for flexible typing, strong typing where possible
   - **Python**: Uses dynamic typing with type hints

5. **Memory Management**:
   - **GDScript**: Uses `RefCounted` base class for automatic reference counting
   - **Python**: Uses automatic garbage collection

## Synchronization Notes

### API Compatibility
- Method signatures are kept as similar as possible
- Return types are consistent (Dictionary for complex data, basic types for simple data)
- Parameter names and order are maintained across implementations

### Feature Parity
- All core functionality is implemented in both languages
- Time management, event scheduling, and CTB logic are identical
- Calendar system with era support is fully synchronized
- IndexedTimeWheel performance characteristics are preserved

### Differences by Design
- **UI Integration**: GDScript version uses native Godot UI components
- **Performance**: GDScript version eliminates C# interop overhead
- **Development**: GDScript version supports immediate execution without compilation
- **Debugging**: GDScript version integrates with Godot's native debugging tools

## Migration Status

- ✅ **Calendar**: Complete feature parity
- ✅ **IndexedTimeWheel**: Complete with thread safety adaptation
- ✅ **CTBManager**: Complete with signal system integration
- ✅ **TestGameWorld**: Complete with unified coordination
- ✅ **Integration Tests**: Complete UI test interface
- ✅ **Functional Tests**: Basic test coverage implemented

Last Updated: 2025-06-27