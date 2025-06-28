# Tests Directory

Comprehensive testing framework for the Godot CTB Game Project using GDScript and the new **Schedulable Architecture**.

## Directory Structure

```
tests/
├── README.md           # This file
├── gdscript/          # GDScript tests (primary)
│   ├── TestGameWorld.gd            # Unified test coordinator
│   ├── test_schedulable_system.gd  # New architecture tests
│   └── CSHARP_MAPPING.md          # Historical mapping (deprecated)
├── test_scene.tscn     # Visual GUT test runner scene (if used)
└── run_gut_tests.gd    # Project status checker
```

## Testing Strategy

This project uses **GDScript-first testing** with Python reference implementation:

- ✅ **GDScript Primary**: Main tests written in GDScript for native integration
- ✅ **Python Reference**: Algorithm validation and prototyping
- ✅ **Schedulable Testing**: Comprehensive tests for new architecture
- ✅ **Integration Tests**: Visual UI testing in Godot environment

## New Architecture Testing

### Schedulable System Tests
- **Location**: `gdscript/test_schedulable_system.gd`
- **Coverage**: Schedulable interface, CombatActor, CTBManager v2
- **Features**: Interface testing, character actions, mixed scheduling

### Key Test Cases
1. **Schedulable Interface**: Abstract methods, type identification
2. **CombatActor**: Creation, execution, active state management
3. **CTBManager**: Adding/removing schedulables, initialization, turn processing
4. **Mixed Scheduling**: Characters and events in same system

## Running Tests

### GDScript Tests (Primary)
```bash
# Run through Godot test scene
# Open scenes/integrated_system_test.tscn and press F6

# Or use GUT if available
godot --headless --script run_gut_tests.gd
```

### Python Reference Tests
```bash
cd python_prototypes
python3 tests/test_schedulable_system.py
# All 13 tests should pass ✅
```

### Visual Integration Test
1. Open `scenes/integrated_system_test.tscn`
2. Press F6 to run scene
3. Observe character actions: "角色张飞执行行动：攻击"
4. Test time advancement and CTB queue

## Adding Tests

### For New Schedulable Objects
```gdscript
extends "res://addons/gut/test.gd"  # If using GUT

func test_custom_schedulable():
    # Create custom schedulable
    var weather = WeatherEvent.new("weather", "天气系统")
    
    # Test interface implementation
    assert_not_null(weather.execute())
    assert_true(weather.should_reschedule())
    assert_eq(weather.get_type_identifier(), "WeatherEvent")
```

### For CTB Integration
```gdscript
func test_mixed_scheduling():
    var actor = CombatActor.new("test", "测试角色")
    var event = SimpleEvent.new("event", "测试事件")
    
    ctb_manager.add_schedulable(actor)
    ctb_manager.add_schedulable(event)
    
    assert_eq(ctb_manager.scheduled_objects.size(), 2)
```

## Test Organization

### Current Test Files
- `test_schedulable_system.gd` - New architecture comprehensive tests
- `TestGameWorld.gd` - Unified test coordinator for integration
- Python: `test_schedulable_system.py` - Reference implementation tests

### Test Categories
1. **Interface Tests**: Schedulable abstract methods
2. **Implementation Tests**: CombatActor specific functionality  
3. **System Tests**: CTBManager operations
4. **Integration Tests**: Multiple objects working together

## Python Reference Testing

Python tests serve as algorithmic reference:
- **Location**: `../python_prototypes/tests/test_schedulable_system.py`
- **Framework**: unittest
- **Status**: 13/13 tests passing ✅
- **Purpose**: Validate architecture before GDScript implementation

### Python Test Results
```
角色 测试战士 执行行动: 休息
已添加可调度对象: 战士1
已添加可调度对象: 战士2
初始化CTB系统，当前时间: 0
.............
----------------------------------------------------------------------
Ran 13 tests in 0.004s

OK
```

## Architecture Benefits

### Why Schedulable Interface?
1. **Decoupling**: CTB doesn't know about Character specifics
2. **Extensibility**: Any object can be scheduled (weather, events, etc.)
3. **Testability**: Easy to mock and test individual components
4. **Consistency**: Same interface for all scheduled objects

### Test Coverage
- ✅ Interface compliance testing
- ✅ Character action randomization
- ✅ Time calculation algorithms
- ✅ Mixed object scheduling
- ✅ State management (active/inactive)

## Development Workflow

1. **Python Validation**: Test algorithms in Python first
2. **GDScript Implementation**: Port to GDScript with tests
3. **Integration Testing**: Use visual test scene for UI validation
4. **Cross-Platform**: Ensure tests pass in both environments

## Related Documentation

- **Architecture**: [CLAUDE.md](../CLAUDE.md) - Full project overview
- **Implementation**: [scripts/README.md](../scripts/README.md) - Code structure
- **Status**: [docs/PROJECT_STATUS.md](../docs/PROJECT_STATUS.md) - Current progress

This testing approach ensures the new Schedulable architecture works correctly while maintaining reference compatibility with the Python implementation.
