# Test GDScript Implementation

Run comprehensive tests for the GDScript implementation of CTB game systems.

## Usage
- `/project:test-gdscript` - Run all GDScript tests
- `/project:test-gdscript [system]` - Test specific system (calendar, timewheel, ctb, integration)

## Command
Please test the GDScript implementation: $ARGUMENTS

Follow these steps:

1. **Identify Test Scope**:
   - If no arguments: test all systems
   - If system specified: focus on that system only
   - Available systems: calendar, timewheel, ctb, integration

2. **Run Functional Tests**:
   - Execute `tests/gdscript/test_gdscript_systems.gd`
   - Verify all core system functionality
   - Test Calendar time management and era system
   - Test IndexedTimeWheel event scheduling
   - Test CTBManager battle coordination

3. **Run Integration Tests**:
   - Test TestGameWorld unified coordinator
   - Test IntegratedSystemTest UI functionality
   - Verify signal-based event coordination
   - Test time advancement and event processing

4. **Verify API Compatibility**:
   - Check that GDScript APIs match Python/C# mappings
   - Ensure all documented methods are implemented
   - Verify return types and parameter handling

5. **Performance Testing**:
   - Test time wheel with large numbers of events
   - Verify memory management with RefCounted classes
   - Test thread safety with Mutex implementation

6. **Report Results**:
   - Summarize test outcomes
   - Report any failures or inconsistencies
   - Suggest fixes for any issues found
   - Update documentation if needed

## Test Files
- `tests/gdscript/test_gdscript_systems.gd` - Functional tests
- `tests/gdscript/test_calendar.gd` - Calendar unit tests (placeholder)
- `tests/gdscript/test_time_wheel.gd` - TimeWheel unit tests (placeholder)  
- `tests/gdscript/test_ctb_manager.gd` - CTB unit tests (placeholder)
- `tests/gdscript/test_config_system.gd` - Config unit tests (placeholder)
- `tests/gdscript/test_integration.gd` - Integration tests (placeholder)
- `scripts/gdscript/IntegratedSystemTest.gd` - UI integration tests
- `scenes/integrated_system_test.tscn` - Test scene

## Core Systems to Test
- **Calendar**: Time advancement, era management, formatting
- **IndexedTimeWheel**: Event scheduling, time wheel advancement, future events
- **CTBManager**: Character management, event execution, turn processing
- **TestGameWorld**: Unified coordination, signal integration