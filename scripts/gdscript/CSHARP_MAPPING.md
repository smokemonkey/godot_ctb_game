# GDScript → C# Mapping

This file documents the correspondence between GDScript and C# implementations.

## Core Systems Mapping

### Calendar System
- **GDScript**: `tests/gdscript/Calendar.gd`
- **C#**: `scripts/csharp/core/Calendar.cs`
- **Status**: Feature complete, GDScript is primary implementation
- **API Correspondence**:
  - `Calendar.new()` ↔ `new Calendar()`
  - `advance_time_tick()` ↔ `AdvanceTimeTick()`
  - `get_timestamp()` ↔ `GetTimestamp()`
  - `get_time_info()` ↔ `GetTimeInfo()`
  - `format_date_gregorian()` ↔ `FormatDateGregorian()`
  - `format_date_era()` ↔ `FormatDateEra()`
  - `anchor_era()` ↔ `AnchorEra()`
  - `start_new_era()` ↔ `StartNewEra()`
  - `reset()` ↔ `Reset()`

### IndexedTimeWheel System
- **GDScript**: `tests/gdscript/IndexedTimeWheel.gd`
- **C#**: `scripts/csharp/core/IndexedTimeWheel.cs`
- **Status**: Feature complete, thread safety model adapted
- **API Correspondence**:
  - `IndexedTimeWheel.new(size, callback)` ↔ `new IndexedTimeWheel<T>(size, callback)`
  - `schedule_with_delay()` ↔ `ScheduleWithDelay()`
  - `schedule_at_absolute_hour()` ↔ `ScheduleAtAbsoluteHour()`
  - `pop_due_event()` ↔ `PopDueEvent()`
  - `advance_wheel()` ↔ `AdvanceWheel()`
  - `remove()` ↔ `Remove()`
  - `peek_upcoming_events()` ↔ `PeekUpcomingEvents()`
  - `get_event()` ↔ `Get()`
  - `contains()` ↔ `Contains()`
  - `get_count()` ↔ `Count` (property)
  - `has_any_events()` ↔ `HasAnyEvents()`

### CTBManager System
- **GDScript**: `tests/gdscript/CTBManager.gd`
- **C#**: `scripts/csharp/core/CTBManager.cs`
- **Status**: Feature complete, event system adapted for GDScript signals
- **API Correspondence**:
  - `CTBManager.new()` ↔ `new CTBManager()`
  - `add_character()` ↔ `AddCharacter()`
  - `remove_character()` ↔ `RemoveCharacter()`
  - `get_character()` ↔ `GetCharacter()`
  - `initialize_ctb()` ↔ `InitializeCTB()`
  - `process_next_turn()` ↔ `ProcessNextTurn()`
  - `schedule_event()` ↔ `ScheduleEvent()`
  - `schedule_with_delay()` ↔ `ScheduleWithDelay()`
  - `execute_event()` ↔ `ExecuteEvent()`
  - `set_character_active()` ↔ `SetCharacterActive()`
  - `get_status_text()` ↔ `GetStatusText()`

### Unified Test Coordinator
- **GDScript**: `tests/gdscript/TestGameWorld.gd`
- **C#**: `scripts/csharp/tests/TestGameWorld.cs` (if existed)
- **Status**: GDScript implementation is the reference

## Event System Mapping

### Event Classes
- **GDScript**: `CTBManager.Event` (base class)
- **C#**: `Event` (abstract base class)
- **GDScript**: `CTBManager.Character` (extends Event)
- **C#**: `Character` (extends Event)

### Event Types
- **GDScript**: `CTBManager.EventType` enum
- **C#**: `EventType` enum
- **Values**: CHARACTER_ACTION, SEASON_CHANGE, WEATHER_CHANGE, STORY_EVENT, CUSTOM

## Testing Integration

### UI Test Interface
- **GDScript**: `tests/gdscript/IntegratedSystemTest.gd`
- **C#**: `scripts/csharp/tests/IntegratedSystemTest.cs` (legacy)
- **Scene**: `scenes/gdscript_integrated_test.tscn` (primary)
- **Legacy Scene**: `scenes/my_ctb_game.tscn` (C# version)

### Functional Tests
- **GDScript**: `tests/gdscript/test_gdscript_systems.gd`
- **C#**: GUT framework tests (legacy)

## Technical Differences

### Language-Specific Adaptations

1. **Thread Safety**:
   - **GDScript**: Uses `Mutex` class for thread synchronization
   - **C#**: Uses `lock` statements with `object _lock = new object()`

2. **Error Handling**:
   - **GDScript**: Uses `push_error()` for error reporting
   - **C#**: Uses `throw new ArgumentException()` for error handling

3. **Event System**:
   - **GDScript**: Uses Godot signals (`signal event_executed`, `emit()`)
   - **C#**: Uses `Action<T>` delegates and event callbacks

4. **Type System**:
   - **GDScript**: Uses `Variant` for flexible typing, class_name for strong typing
   - **C#**: Uses generic types `<T>` and strong static typing

5. **Memory Management**:
   - **GDScript**: Uses `RefCounted` base class for automatic reference counting
   - **C#**: Uses .NET garbage collection

6. **Naming Conventions**:
   - **GDScript**: snake_case for methods and variables
   - **C#**: PascalCase for public methods, camelCase for private fields

## Synchronization Notes

### API Compatibility
- Core functionality is preserved across implementations
- Method behavior is identical where possible
- Return types are consistent (Dictionary ↔ Dictionary<string, object>)
- Parameter semantics are maintained

### Feature Parity
- All time management features are implemented in both
- Event scheduling and CTB logic are identical
- Calendar system with era support is fully synchronized
- IndexedTimeWheel performance characteristics are preserved

### Differences by Design
- **Performance**: GDScript eliminates C# compilation overhead
- **Integration**: GDScript uses native Godot components
- **Development**: GDScript supports immediate execution
- **Threading**: GDScript uses Godot's threading model

## Migration Strategy

### Current Status
- **GDScript**: Primary implementation, actively developed
- **C#**: Legacy implementation, maintained for reference
- **Phase Out Plan**: C# code will be commented out, not deleted

### Code Commenting Strategy
```csharp
// [LEGACY - GDScript Primary] Original C# implementation
// This code is preserved for reference but not actively used
// See tests/gdscript/ for the primary GDScript implementation
```

### Mapping Maintenance
- This mapping file is updated when APIs change
- Both implementations are kept in sync for reference
- GDScript implementation leads, C# follows for compatibility

## Implementation Notes

### EventNode Internal Class
- **GDScript**: `EventNode` class within `IndexedTimeWheel`
- **C#**: `EventNode` internal class with generic typing
- **Key Difference**: GDScript uses `Variant` types, C# uses generics

### Callback Systems
- **GDScript**: Uses `Callable` type for function references
- **C#**: Uses `Func<T>` and `Action<T>` delegates
- **Behavior**: Functionally equivalent, syntax differs

### Collection Types
- **GDScript**: Uses `Array`, `Dictionary` native types
- **C#**: Uses `List<T>`, `Dictionary<K,V>` generic collections
- **Performance**: Both provide similar performance characteristics

## Migration Status

- ✅ **Calendar**: Complete migration with full parity
- ✅ **IndexedTimeWheel**: Complete with thread model adaptation
- ✅ **CTBManager**: Complete with signal system integration
- ✅ **TestGameWorld**: New unified coordinator in GDScript
- ✅ **Integration Tests**: Complete UI replacement
- ✅ **Code Organization**: Proper test directory structure

Last Updated: 2025-06-27