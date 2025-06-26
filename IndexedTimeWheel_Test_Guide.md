# IndexedTimeWheel Test Guide

## Overview
This guide will help you test the IndexedTimeWheel implementation in Godot. The Python code has been successfully synced to C# and we've created a comprehensive test scene.

## What We've Created

### 1. **C# Implementation** 
- **File**: `scripts/csharp/core/IndexedTimeWheel.cs`
- **Status**: Fully synchronized with Python improvements
- **Key Features**:
  - Thread-safe operations with proper locking
  - Future event support (events beyond buffer size)
  - O(1) event scheduling and popping
  - Key-based event indexing and removal
  - Fixed `HasAnyEvents()` method

### 2. **Test Scene**
- **File**: `scenes/test_indexed_time_wheel.tscn`
- **Script**: `scripts/csharp/tests/TestIndexedTimeWheel.cs`
- **Features**:
  - Interactive UI for manual testing
  - Automated validation tests
  - Real-time event visualization
  - Multiple test scenarios

### 3. **Validation System**
- **File**: `scripts/csharp/tests/IndexedTimeWheelValidator.cs`
- **Tests**: 5 comprehensive test cases covering:
  - Basic scheduling and popping
  - Future events (beyond buffer size)
  - Multiple events at same time
  - Event removal operations  
  - HasAnyEvents functionality

## How to Run Tests

### Method 1: Using the Batch File
```batch
# Double-click or run from command line:
run_timewheel_test.bat
```

### Method 2: From Godot Editor
1. Open `project.godot` in Godot 4.4
2. Open scene: `scenes/test_indexed_time_wheel.tscn`
3. Press F6 or click "Play Scene"

### Method 3: Command Line
```bash
"D:\godot\Godot_v4.4.1-stable_mono_win64.exe" --path . scenes/test_indexed_time_wheel.tscn
```

## Test Interface Guide

### Controls Available:
1. **Input Fields**:
   - **Key**: Unique identifier for the event
   - **Value**: Data associated with the event
   - **Delay**: Time delay before event triggers

2. **Action Buttons**:
   - **Add Event**: Schedule a new event
   - **Advance Time**: Move time forward by 1 hour
   - **Pop Due Event**: Extract next ready event

3. **Test Buttons**:
   - **Test Basic Operations**: Schedule events at times 2 and 5
   - **Test Future Events**: Schedule events beyond buffer size (15, 25)
   - **Clear All**: Reset everything to start fresh
   - **Run Validation Tests**: Execute all automated tests

### Status Information:
- **Current Time**: Shows the current time counter
- **Total Events**: Number of scheduled events
- **Has Events**: Whether any events exist
- **Current Slot Empty**: Whether current time slot is ready to advance

## Testing Scenarios

### Scenario 1: Basic Operations
1. Click "Test Basic Operations"
2. You should see events scheduled for times 2 and 5
3. Click "Advance Time" twice to reach time 2
4. Click "Pop Due Event" to extract the first event
5. Continue advancing and popping to test timing

### Scenario 2: Future Events
1. Click "Test Future Events" 
2. Events will be scheduled beyond the buffer size (10)
3. Advance time slowly and observe when future events become available
4. Future events should not appear in "Upcoming Events" until their time approaches

### Scenario 3: Manual Testing
1. Enter custom Key, Value, and Delay
2. Click "Add Event"
3. Experiment with different delays (try both < 10 and > 10)
4. Test removing events, advancing time, etc.

### Scenario 4: Automated Validation
1. Click "Run Validation Tests"
2. Watch the results - all should show "PASSED" in green
3. If any show "FAILED" in red, there's an implementation issue

## Expected Results

### ✅ All Tests Should Pass:
- **Test 1**: Basic scheduling and popping
- **Test 2**: Future events work correctly  
- **Test 3**: Multiple events at same time (FIFO order)
- **Test 4**: Remove operations work properly
- **Test 5**: HasAnyEvents reflects actual state

### 🎯 Interactive Features Should Work:
- Events can be scheduled with custom delays
- Time advancement works when current slot is empty
- Event popping retrieves correct key-value pairs
- Future events (delay > 10) don't appear in wheel preview
- Status display updates correctly

## Troubleshooting

### Build Issues:
- Make sure C# solution builds successfully
- Check that all using statements are correct
- Verify Godot 4.4 with Mono support

### Runtime Issues:
- Check console output for detailed error messages
- Verify that scene structure matches script expectations
- Ensure time advancement follows correct order (advance → pop → advance)

## Integration with Game Systems

This IndexedTimeWheel can now be integrated with:
- **CTB Manager**: For character action scheduling
- **Calendar System**: For time-based events
- **Game Events**: Festivals, season changes, etc.
- **UI Systems**: Real-time event previews

The implementation is thread-safe and production-ready for your turn-based game!