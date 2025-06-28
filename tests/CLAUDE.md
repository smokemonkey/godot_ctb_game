# Tests Folder CLAUDE.md

Testing-specific guidance for this project.

## ⚠️ CRITICAL TESTING RULES

1. **Use MockConfig**: NEVER use real GameConfig resources in tests
2. **Static Scenes**: Test UI is now static, visible in Godot editor
3. **GUT Framework**: Use `extends GutTest` for unit tests
4. **Console Commands**: Use console version for test execution

## Test Structure

**gdscript/** - GDScript unit tests
- `test_calendar.gd` - Calendar system tests
- `test_ctb_manager.gd` - CTB battle system tests  
- `test_time_wheel.gd` - IndexedTimeWheel tests
- `mocks/ConfigManagerMock.gd` - Mock configuration for tests

**Scenes**
- `test_scene.tscn` - Static test runner UI
- `test_runner.gd` - Test execution controller

## MockConfig Usage

**✅ CORRECT - Use Mock in Tests**
```gdscript
extends GutTest

const ConfigManagerMock = preload("res://tests/gdscript/mocks/ConfigManagerMock.gd")

var calendar: Calendar
var config_mock: ConfigManagerMock

func before_each():
    config_mock = ConfigManagerMock.new()
    calendar = Calendar.new()
```

**❌ WRONG - Don't use real GameConfig**
```gdscript
# This will fail with resource loading errors
var config = GameConfig.new()  # Resource loading issues
```

## Test Execution Commands

**Unit Tests via Scene**
```bash
"/mnt/d/Godot/Godot_v4.4.1-stable_mono_win64_console.exe" --path . res://tests/test_scene.tscn
```

**Direct GUT Script**
```bash
"/mnt/d/Godot/Godot_v4.4.1-stable_mono_win64_console.exe" --path . --script tests/run_tests.gd
```

**Individual Test File**
```bash
"/mnt/d/Godot/Godot_v4.4.1-stable_mono_win64_console.exe" --path . --script tests/gdscript/test_calendar.gd
```

## Test Runner Features

**Static UI Components**
- Test selection buttons (Calendar, CTB, Time Wheel)
- Progress bar and status display
- Color-coded results with scrollable output
- Real-time test execution feedback

**Simplified Test Mode**
- Validates script loading and basic functionality
- Lists available test methods
- Shows compilation status without full GUT execution

## Recent Changes (2025-06-28)

**Static Scene Conversion**
- `test_scene.tscn` now has static UI layout
- `test_runner.gd` uses `@onready` node references
- Test interface visible and editable in Godot editor

**MockConfig Integration**
- All tests use ConfigManagerMock instead of real resources
- Avoids GameConfig class loading issues
- Provides consistent test environment

**Simplified Test Execution**
- Added basic script validation mode
- Better error handling for resource issues
- Cleaner test output with color coding

## Testing Best Practices

1. **Always use MockConfig** for configuration values
2. **Test compilation** before running full test suites
3. **Use before_each()** for test setup and cleanup
4. **Keep tests isolated** - no shared state between tests
5. **Test both success and failure cases**

## Troubleshooting

**Resource Loading Errors**
- Use MockConfig instead of GameConfig
- Check that class_name classes are properly compiled
- Verify preload paths are correct

**GUT Framework Issues**
- Try simplified test mode first
- Check GUT addon is properly installed
- Use direct script execution as fallback

## Documentation Updates

When modifying tests:
1. Update this file if test patterns change
2. Update MockConfig when new config values needed
3. Update main CLAUDE.md if testing approach changes
4. Document any new testing utilities or helpers