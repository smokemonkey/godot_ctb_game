# CLAUDE.md

Claude Code (claude.ai/code) guidance for this repository.

## ⚠️ CRITICAL RULES - MUST FOLLOW

1. **Godot Commands**: Use console version ONLY - NEVER add `--headless` parameter
2. **Resource References**: Use direct `const ClassName = preload("path")` - NO central References.gd system
3. **Static Scenes**: UI is now static in Godot editor, use `@onready` references
4. **Testing**: Use MockConfig in tests, not real GameConfig resources
5. **Indentation**: Always 4 spaces, never tabs
6. **Follow Documentation**: Respect ⚠️ CRITICAL warnings in all CLAUDE.md files

## Project Overview

Godot 4.4 turn-based game with GDScript (primary), legacy C#, and Python prototypes:
- Custom calendar (360 days/year, 24 hours/day)  
- CTB battle system with indexed time wheel
- Static UI scenes for editor visibility

## Architecture

**GDScript (Primary)**
- Core: `scripts/gdscript/core/` - Calendar, CTBManager, IndexedTimeWheel
- UI: `scenes/integrated_system_test.tscn` - Static scene with full UI
- Tests: `tests/gdscript/` - Uses MockConfig, not real resources

**Legacy C#** 
- Location: `scripts/csharp/` - To be phased out
- Status: Disabled in project.godot

**Python Prototypes**
- Location: `python_prototypes/` - For rapid prototyping only

## Development Commands

**Godot Testing**
```bash
# ⚠️ CRITICAL: Console version ONLY, NO --headless parameter
# Integrated test (main scene)
"/mnt/d/Godot/Godot_v4.4.1-stable_mono_win64_console.exe" --path . res://scenes/integrated_system_test.tscn

# Unit tests  
./run_tests.sh

# Direct script test
"/mnt/d/Godot/Godot_v4.4.1-stable_mono_win64_console.exe" --path . --script tests/run_tests.gd

# NEVER use aliases - Claude Code requires full paths
# NEVER add --headless to console version
```

**Python Tests**
```bash
cd python_prototypes && python3 run_tests.py
```

## Code Conventions

**GDScript**
- Private methods: `_method_name()` prefix
- Public API: no underscore prefix  
- Documentation: `##` for public, `#` for private
- Resource loading: `const Class = preload("res://path/Class.gd")`
- Type hints: Use direct class names, not `Refs.ClassName`

**Testing**
- Location: `tests/gdscript/` with MockConfig
- Inheritance: `extends GutTest`
- Naming: `test_method_name()`
- Setup: Use `before_each()` for initialization

## Key Files

- `scenes/integrated_system_test.tscn` - Main test interface (static)
- `run_tests.sh` - Quick test execution script
- `tests/gdscript/mocks/ConfigManagerMock.gd` - Mock for tests
- `scripts/gdscript/IntegratedSystemTest.gd` - Main test controller
- `addons/gut/gut_cmdln.gd` - GUT command line runner

## Recent Changes (2025-06-28)

**Static Scene Conversion**
- Converted dynamic UI to static Godot scenes
- IntegratedSystemTest now uses `@onready` node references
- Test scenes visible and editable in Godot editor

**References.gd Removal**
- Abandoned central reference system due to GDScript limitations
- `extends Refs.ClassName` syntax not supported
- `func method(param: Refs.ClassName)` type hints don't work
- Back to direct preload approach: `const Class = preload("path")`

**Testing Improvements**  
- Migrated to GUT command line for better performance (6.7s → 0.08s)
- Removed custom test runner GUI in favor of native GUT
- MockConfig usage in tests to avoid resource loading issues
- Enhanced test execution with detailed output and CI/CD support

## Sub-folder Documentation

**ALWAYS update sub-folder CLAUDE.md files when making changes:**

- `scripts/CLAUDE.md` - Resource reference patterns, GDScript conventions
- `tests/CLAUDE.md` - Testing approaches, MockConfig usage patterns  
- `scenes/CLAUDE.md` - Scene structure, static UI patterns
- `python_prototypes/CLAUDE.md` - Python testing and prototyping

## Documentation Maintenance

Update this file AND relevant sub-folder CLAUDE.md when:
- Architecture changes
- New testing approaches  
- Development workflow changes
- Critical rules discovered

Keep it concise and actionable!