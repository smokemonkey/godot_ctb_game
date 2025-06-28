# Godot Testing Setup Guide

## Quick Start

**⚠️ CRITICAL: GUT Tests Must Run in GUI Mode**

GUT framework does not work properly in console/headless mode due to autoload compilation issues. Always run tests in GUI mode:

```bash
# Step 1: Import resources and cache classes (console mode OK)
./godot.sh --path . --import

# Step 2: Run tests in GUI mode (REQUIRED)
./godot.sh --path . res://tests/test_scene.tscn
```

**Note**: Console/headless mode causes `ConfigManager` autoload compilation errors. GUI mode works perfectly.

## Why Two Steps?

Godot needs to cache `class_name` classes before they can be used. The `--import` flag:
- ✅ Creates `.godot/global_script_class_cache.cfg`
- ✅ Imports all resources
- ✅ Caches all custom classes (Calendar, CTBManager, GutTest, etc.)
- ✅ Fast and reliable (Godot 4.3+ feature)

## Test Results

After running the import + test workflow:

### ✅ Working Tests
- **Calendar System**: All basic functionality working
- **IndexedTimeWheel**: Event scheduling and time wheel operations
- **CTBManager**: Schedulable object management
- **GUT Framework**: Now loads and initializes correctly

### 📝 Test Output Example
```
=== 测试Calendar系统 ===
初始时间: 0
推进1小时后: 1
Calendar测试完成 ✓

=== 测试IndexedTimeWheel系统 ===
调度了2个事件
事件总数: 2
IndexedTimeWheel测试完成 ✓

=== 测试CTBManager系统 ===
添加角色: 英雄1
CTBManager测试完成 ✓

---  GUT  ---
Godot version:  4.4.1
GUT version:  9.4.0
```

## For CI/CD

**❌ Headless/Console Mode Not Supported**

Due to GUT framework limitations with autoload in console mode, automated CI/CD testing is not currently feasible. Tests must be run manually in GUI mode.

## Troubleshooting

**❌ If you see "class not found" errors:**
```
ERROR: Cannot get class 'GameConfig'
SCRIPT ERROR: Could not resolve class "GutTest"
```

**✅ Solution:** Run `--import` first!

**❌ If you skip the import step:**
- Classes won't be cached
- Tests will fail with compilation errors
- GUT framework won't work

## Key Lessons Learned

1. **`--import` is mandatory** for `class_name` classes to work
2. **Two-step process** is required - cannot combine import with execution
3. **Always import first** in scripts and CI pipelines
4. **References.gd pattern abandoned** - use direct `class_name` or `preload()`

## Updated Architecture

- ✅ **Calendar**: Uses fallback ConfigManager access
- ✅ **SchedulableExample**: Handles missing ConfigManager gracefully  
- ✅ **Tests**: Use `class_name` classes directly
- ❌ **References.gd**: Abandoned due to GDScript syntax limitations