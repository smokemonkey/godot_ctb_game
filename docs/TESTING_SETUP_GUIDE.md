# Godot Testing Setup Guide

## Quick Start

**✅ RECOMMENDED: Use GUT Command Line**

GUT framework works best with direct command line execution. This provides detailed output and fast execution:

```bash
# Step 1: Import resources and cache classes
./godot.sh --path . --import

# Step 2: Run all tests
./godot.sh --path . --script addons/gut/gut_cmdln.gd -gdir=tests/gdscript

# Run specific test file
./godot.sh --path . --script addons/gut/gut_cmdln.gd -gtest_name=test_calendar.gd
```

**Performance**: All tests complete in ~0.08 seconds with detailed output.

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

**✅ Command Line Supported**

GUT command line mode works well for automated testing:

```bash
# CI/CD pipeline example
./godot.sh --path . --import
./godot.sh --path . --script addons/gut/gut_cmdln.gd -gdir=tests/gdscript
```

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

- ✅ **Calendar**: Direct ConfigManager access (works in all modes)
- ✅ **EventExample**: Handles configuration gracefully  
- ✅ **Tests**: Use `class_name` classes directly with GUT framework
- ✅ **Command Line**: Native GUT command line for fast execution
- ❌ **GUI Test Runner**: Removed in favor of command line efficiency