# Tests Directory

Comprehensive testing framework for the Godot CTB Game Project using GUT (Godot Unit Testing) framework.

## Directory Structure

```
tests/
├── README.md           # This file
├── test_scene.tscn     # Visual GUT test runner scene
├── test_runner_ui.gd   # GUT test runner UI logic
└── run_gut_tests.gd    # Project status checker
```

## Testing Strategy

This project uses **GUT (Godot Unit Testing)** framework for testing within the Godot environment. This approach provides:

- ✅ **Native Godot Integration**: Tests run in actual Godot environment
- ✅ **GDScript Support**: Native support for GDScript testing
- ✅ **Visual Test Runner**: Interactive UI for test development
- ✅ **C# Integration**: Can test C# classes through GDScript wrappers when needed

## Why GUT Instead of Traditional C# Testing?

1. **Godot-Specific**: Tests run in the actual game environment
2. **Unified Framework**: Single testing approach for all scripts
3. **Visual Debugging**: Can test UI, scenes, and gameplay mechanics
4. **No External Dependencies**: No need for NUnit, MSTest, or other frameworks

## Running Tests

### Visual Test Runner (Recommended)
1. Open Godot editor
2. Open `test_scene.tscn`
3. Run scene (F6)
4. Use UI to run tests interactively

### GUT Editor Plugin
1. Enable GUT plugin in Project Settings > Plugins
2. Use GUT dock panel in editor
3. Configure and run tests directly

### Command Line Status Check
```bash
# Check project structure and test setup
godot --headless --script run_gut_tests.gd
```

## Adding Tests

### For Core Systems
Create test files that extend `GutTest`:

```gdscript
extends GutTest

func test_your_functionality():
    # Arrange
    var instance = YourClass.new()
    
    # Act
    var result = instance.your_method()
    
    # Assert
    assert_eq(result, expected_value, "Description of what should happen")
```

### For C# Integration
When needed, create GDScript wrapper classes to test C# functionality:

1. Create a GDScript wrapper that extends Node
2. Instantiate and call C# classes from the wrapper
3. Test the wrapper with GUT framework

## Test Organization

Tests should be organized by system:
- `test_calendar.gd` - Calendar system tests
- `test_ctb_manager.gd` - CTB Manager tests  
- `test_indexed_time_wheel.gd` - Time wheel tests
- `test_game_mechanics.gd` - Gameplay logic tests

## Python Reference Tests

Python prototype tests serve as reference implementation:
- **Location**: `../python_prototypes/tests/core/`
- **Framework**: unittest
- **Run**: `cd python_prototypes && python run_tests.py`
- **Status**: 61/61 tests passing ✅
- **Purpose**: Validate logic before implementing in Godot

## Related Documentation

- **Project Structure**: [CLAUDE.md](../CLAUDE.md)
- **Python Reference**: [python_prototypes/tests/](../python_prototypes/tests/)
- **GUT Framework**: [Official Documentation](https://github.com/bitwes/Gut)

## Development Workflow

1. **Python Prototype**: Validate logic in reference implementation
2. **Godot Implementation**: Port to C# or GDScript  
3. **GUT Testing**: Test integration in Godot environment
4. **Iterate**: Refine based on test results

This approach ensures code quality while maintaining the benefits of Godot's integrated development environment.