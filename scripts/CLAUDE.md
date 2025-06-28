# Scripts Folder CLAUDE.md

Specific guidance for working with scripts in this project.

## ⚠️ CRITICAL RULES FOR SCRIPTS

1. **Resource References**: NEVER use central References.gd system
2. **Direct Preload**: Always use `const ClassName = preload("res://path/Class.gd")`
3. **Type Hints**: Use direct class names, not `Refs.ClassName`
4. **Extensions**: `extends "res://path/Class.gd"` for inheritance

## Resource Reference Patterns

**✅ CORRECT - Direct Preload**
```gdscript
const Calendar = preload("res://scripts/gdscript/core/Calendar.gd")
const Schedulable = preload("res://scripts/gdscript/shared/interfaces/Schedulable.gd")

var calendar = Calendar.new()
extends "res://scripts/gdscript/shared/interfaces/Schedulable.gd"
```

**❌ WRONG - Central Reference System**
```gdscript
const Refs = preload("res://scripts/gdscript/References.gd")
var calendar = Refs.Calendar.new()  # Doesn't work
extends Refs.Schedulable            # Syntax error
```

## GDScript Limitations Learned

1. **extends Syntax**: Cannot use `extends Refs.ClassName`
2. **Type Declarations**: Cannot use `func method(param: Refs.ClassName)`
3. **class_name Classes**: Are global, but only when files compile successfully
4. **Compilation Order**: Failed compilation prevents class_name registration

## Folder Structure

**gdscript/** (Primary Implementation)
- `core/` - Core game systems (Calendar, CTBManager, IndexedTimeWheel)
- `resources/` - Resource classes (GameConfig)
- `shared/interfaces/` - Interface definitions (Schedulable)
- `development/` - Development examples (EventExample)
- `managers/` - Autoload managers (ConfigManager)

**csharp/** (Legacy - To be phased out)
- Status: Disabled in project.godot
- Will be removed in future cleanup

## Recent Changes (2025-06-28)

**References.gd Abandoned**
- Attempted central reference system failed due to GDScript syntax limitations
- Reverted to direct preload approach for reliability
- All files updated to remove References.gd dependencies

**Static Scene Conversion**
- UI scripts now use `@onready` for static scene nodes
- Better editor integration and visual development
- Removed dynamic UI creation patterns

## Best Practices

1. **Keep preloads at top** of each file that needs them
2. **Group related preloads** with comments
3. **Use full paths** for clarity and IDE support
4. **Prefer class_name** when available, but have preload fallback
5. **Test compilation** after making reference changes

## Documentation Updates

When modifying scripts:
1. Update this file if reference patterns change
2. Update main CLAUDE.md if architecture changes
3. Update test documentation if test patterns change
4. Keep examples current with actual usage patterns