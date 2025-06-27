# Integrated System Test Guide

## Overview
这是一个综合集成测试，将**Calendar**、**CTB (Conditional Turn-Based)**和**IndexedTimeWheel**系统结合在一个交互式场景中。现在使用全新的**Schedulable架构**，提供更灵活的事件调度系统。

## What's Integrated

### 🗓️ **Calendar System**
- **Time Management**: 360-day years, 24-hour days
- **Era System**: Anchoring and changing eras
- **Date Formatting**: Both Gregorian and era-based display
- **Real-time Updates**: Synchronized with time advancement

### ⚙️ **IndexedTimeWheel** 
- **Event Scheduling**: Short-term (main wheel) and long-term (future pool)
- **Visual Inspector**: Shows wheel contents and future events
- **Real-time Processing**: Events execute as time advances
- **Thread-safe Operations**: Handles concurrent access

### ⚔️ **New Schedulable CTB System**
- **CombatActor**: War characters with random actions like "攻击", "防御", "技能"
- **Schedulable Interface**: Any object can implement scheduling behavior
- **Mixed Events**: Characters, weather, story events all use same system
- **Decoupled Design**: CTB only knows about Schedulable interface

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

### Left: CTB Action Bar (Game Ready)
- **Combat Actions**: Shows character actions like "角色张飞执行行动：攻击"
- **Queue Display**: Next action highlighted, others in order
- **Real-time Updates**: Shows action queue like in actual CTB games
- **Auto-scroll**: Always shows latest activity

### Center: Control Panel
- **Time Display**: Current time in both era and Gregorian formats
- **Calendar Status**: Year, month, day, era information
- **Time Controls**: Advance by hour, day, week, month
- **Era Controls**: Anchor eras, change eras
- **Test Scenarios**: Pre-built test cases

### Right: TimeWheel Inspector
- **Wheel Events**: Shows events in main time wheel buffer
- **Future Events**: Shows events beyond buffer size
- **Statistics**: Total events, wheel status
- **Real-time Monitoring**: Updates as events move/execute

## How to Run

### Quick Launch (Cross-platform)
```bash
python3 run_test.py
# or
./run_test.py
# or
make run
```

### Godot Editor
1. Open project in Godot 4.4
2. Navigate to `scenes/integrated_system_test.tscn`
3. Press F6 to run scene

## Testing Scenarios

### 🧪 **Basic Test**
- Schedules simple events at different times
- Tests basic scheduling and execution
- Verifies time advancement works

### ⚔️ **Combat Test** 
- Creates combat scenario with CombatActor characters
- Characters perform random actions ("攻击", "防御", "技能", etc.)
- Demonstrates new Schedulable architecture
- Shows how CTB action bar would work in-game

### 🔮 **Long-term Test**
- Schedules events beyond buffer size (250+ hours)
- Tests future event system
- Shows seasonal/festival events
- Demonstrates calendar integration

### 📅 **Calendar Features**
- **Era Anchoring**: `开元` era → year 713 AD
- **Era Changes**: Start new era at current year
- **Time Display**: Both Gregorian and era formats
- **Reset Function**: Clear and restart

## Key Features Demonstrated

### ✅ **New Schedulable Architecture**
1. **Interface-based**: Any object can implement Schedulable
2. **CombatActor**: Characters with random combat actions
3. **Mixed Scheduling**: Characters and events use same system
4. **Decoupled Design**: CTB doesn't know about specific object types
5. **Easy Extension**: Add weather, story events easily

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

## Expected Behavior

### When System Starts:
- 5 characters (张飞, 关羽, 刘备, 曹操, 孙权) are created as CombatActors
- Each character schedules initial actions with random delays
- Actions appear like "角色张飞执行行动：攻击"

### When Adding Actions:
- Action appears in CTB bar
- Shows up in TimeWheel inspector
- Time display shows scheduling

### When Advancing Time:
- Due actions execute automatically
- Character actions print to console
- Action bar updates
- Calendar updates
- TimeWheel inspector refreshes

### When Testing Era Functions:
- Anchoring works like web demo
- Era names display correctly
- Date formats switch properly
- Status shows anchor information

## Game Integration Ready

This test scene demonstrates production-ready integration:

1. **New CTB Architecture**: Schedulable interface ready for any game object
2. **CombatActor**: Ready-to-use character action system
3. **Time Management**: Calendar system ready for game events
4. **Event Scheduling**: TimeWheel handles all game timing
5. **Performance**: Thread-safe, optimized for real-time use

The three systems work together seamlessly with the new Schedulable architecture, providing a complete and flexible time management solution for your turn-based game!