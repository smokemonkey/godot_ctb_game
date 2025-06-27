# Integrated System Test Guide

## Overview
This is a comprehensive integration test that combines **Calendar**, **CTB (Conditional Turn-Based)**, and **IndexedTimeWheel** systems in a single interactive scene. It provides visual feedback similar to the Python web demos but within Godot.

## What's Integrated

### 🗓️ **Calendar System**
- **Time Management**: 360-day years, 24-hour days
- **Era System**: Anchoring and changing eras (like the web demo)
- **Date Formatting**: Both Gregorian and era-based display
- **Real-time Updates**: Synchronized with time advancement

### ⚙️ **IndexedTimeWheel** 
- **Event Scheduling**: Short-term (main wheel) and long-term (future pool)
- **Visual Inspector**: Shows wheel contents and future events
- **Real-time Processing**: Events execute as time advances
- **Thread-safe Operations**: Handles concurrent access

### ⚔️ **CTB Action System**
- **Character Actions**: Simulated combat actions with delays
- **Action Queue**: Visual representation like a game's action bar
- **Event Execution**: Actions trigger when their time comes
- **Combat Simulation**: Multiple characters with random timing

## UI Layout

```
┌─────────────┬─────────────────┬──────────────┐
│  CTB Action │   Control Panel │  TimeWheel   │
│     Bar     │                 │  Inspector   │
│             │                 │              │
│ ⚔️ Actions  │ 📅 Time Display │ 🎯 Wheel     │
│ Scrolling   │ 🏛️ Era Controls │ 🔮 Future    │
│ Up/Down     │ 🧪 Test Buttons │ Events       │
│             │                 │              │
└─────────────┴─────────────────┴──────────────┘
```

### Left: CTB Action Bar (Reusable for Game)
- **Scrolls Bottom→Top**: New actions at bottom, executed actions scroll up
- **Color Coding**: 
  - 🔵 Blue = Scheduled actions
  - 🟢 Green = Executed actions
- **Real-time Updates**: Shows action queue like in actual CTB games
- **Auto-scroll**: Always shows latest activity

### Center: Control Panel
- **Time Display**: Current time in both era and Gregorian formats
- **Calendar Status**: Year, month, day, era information
- **Time Controls**: Advance by hour, day, week, month
- **Era Controls**: Anchor eras, change eras (like web demo)
- **Test Scenarios**: Pre-built test cases

### Right: TimeWheel Inspector
- **Wheel Events**: Shows events in main time wheel buffer
- **Future Events**: Shows events beyond buffer size
- **Statistics**: Total events, wheel status
- **Real-time Monitoring**: Updates as events move/execute

## How to Run

### Method 1: Quick Launch
```batch
# Double-click:
run_timewheel_test.bat
```

### Method 2: Godot Editor
1. Open `open_godot_editor.bat`
2. Navigate to `scenes/integrated_system_test.tscn`
3. Press F6 to run scene

### Method 3: Alternative Test
```batch
# For simple timewheel-only test:
run_simple_timewheel_test.bat
```

## Testing Scenarios

### 🧪 **Basic Test**
- Schedules events at different times
- Tests basic scheduling and execution
- Verifies time advancement works

### ⚔️ **Combat Test** 
- Creates combat scenario with multiple characters
- Random action timing (1-20 hours)
- Simulates turn-based battle system
- Shows how CTB action bar would work in-game

### 🔮 **Long-term Test**
- Schedules events beyond buffer size (250+ hours)
- Tests future event system
- Shows seasonal/festival events
- Demonstrates calendar integration

### 📅 **Calendar Features** (Like Web Demo)
- **Era Anchoring**: `开元` era → year 713 AD
- **Era Changes**: Start new era at current year
- **Time Display**: Both Gregorian and era formats
- **Reset Function**: Clear and restart

## Key Features Demonstrated

### ✅ **Time Wheel Functionality**
1. **Event Scheduling**: Both immediate and future events
2. **Buffer Management**: 180-hour circular buffer
3. **Future Pool**: Events beyond buffer automatically handled
4. **Thread Safety**: Locks prevent data corruption
5. **Event Execution**: FIFO processing of due events

### ✅ **Calendar Integration**
1. **Era System**: Full anchoring and change functionality
2. **Date Formatting**: Matches Python web demo exactly
3. **Time Advancement**: Tick-based progression
4. **Status Display**: Comprehensive time information

### ✅ **CTB Simulation**
1. **Action Queue**: Visual representation of pending actions
2. **Character Management**: Multiple entities with actions
3. **Combat Flow**: Turn-based action execution
4. **UI Reusability**: Action bar design suitable for actual game

## Expected Behavior

### When Adding Actions:
- Action appears in CTB bar (blue)
- Shows up in TimeWheel inspector
- Time display shows scheduling

### When Advancing Time:
- Due actions execute automatically (turn green)
- Action bar scrolls up
- Calendar updates
- TimeWheel inspector refreshes

### When Testing Era Functions:
- Anchoring works like web demo
- Era names display correctly
- Date formats switch properly
- Status shows anchor information

## Game Integration Ready

This test scene demonstrates production-ready integration:

1. **CTB Action Bar**: Can be directly used in your game UI
2. **Time Management**: Calendar system ready for game events
3. **Event Scheduling**: TimeWheel handles all game timing
4. **Performance**: Thread-safe, optimized for real-time use

The three systems work together seamlessly, providing a complete time management solution for your turn-based game!