# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid Godot 4.4 game project with both C# and Python components for a turn-based game featuring:
- Custom calendar system (360 days/year, 24 hours/day)
- CTB (Conditional Turn-Based) battle system
- Indexed time wheel for efficient event scheduling
- Dual implementation in both C# (Godot) and Python (prototyping)

## Architecture

The project has two main components:

### 1. Godot Game Engine (C#)
- **Location**: `scripts/csharp/core/` and `tests/csharp/core/`
- **Core Systems**:
  - `Calendar.cs` - Time management system starting from 2000 BC
  - `CTBManager.cs` - Event-based battle system using indexed time wheel
  - `IndexedTimeWheel.cs` - Circular buffer for efficient event scheduling
- **Game Scene**: `scenes/my_ctb_game.tscn`

### 2. Python Prototypes
- **Location**: `python_prototypes/`
- **Purpose**: Rapid prototyping and testing of game systems
- **Structure**:
  - `core/` - Core game logic modules (calendar, ctb_manager, indexed_time_wheel, game_world)
  - `examples/` - Web demos and usage examples
  - `tests/` - Comprehensive test suites with unittest framework

## Development Commands

### Python Prototype Development
```bash
cd python_prototypes

# Set up environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run tests
python3 run_tests.py

# Run web demos
python3 examples/start_web_demo.py

# Generate API documentation
python3 generate_docs.py
```

### Godot Development
- Open `project.godot` in Godot 4.4
- The project uses C# scripting with .NET support
- Main scene: `scenes/my_ctb_game.tscn`
- Core scripts located in `scripts/csharp/core/`

### Unified Testing Framework (GUT)
```bash
# Run tests in Godot editor
# Open test scene: tests/test_scene.tscn

# Run tests from command line
godot --headless --script run_gut_tests.gd

# Test both C# and GDScript implementations
# View results in unified test UI
```

### Code Synchronization
```bash
# Sync Python to C#
python3 sync_code.py py cs [--file=module] [--dry-run]

# Sync C# to Python
python3 sync_code.py cs py [--file=module] [--dry-run]

# Check mapping consistency
python3 sync_code.py --check-mapping

# Preview changes
python3 sync_code.py py cs --dry-run
```

## Key Systems

### Time Management
- **Custom Calendar**: 360-day years (12 months × 30 days), 24-hour days
- **Era System**: Supports custom era anchoring (e.g., "开元", "贞观")
- **Dual Display**: Gregorian (公元前/后) and era-based formatting
- **Time Flow**: Non-uniform time progression for turn-based gameplay

### CTB Battle System v2.0
- **Circular Buffer**: 180-day (4320-hour) event scheduling
- **Event Inheritance**: Character actions, season changes, festivals
- **Random Intervals**: 1-180 day action intervals (avg 90 days)
- **O(1) Time Complexity**: Efficient event processing

### Indexed Time Wheel
- **Fixed Memory**: Circular buffer prevents memory growth
- **Event Chaining**: Linked lists for simultaneous events
- **Dynamic Offset**: Avoids array shifting overhead
- **Generic Design**: Supports any event type

## Code Conventions

### Python Code
- Follow existing module structure in `game_system/`
- Use pytest for testing with descriptive test names
- Include type hints and docstrings
- Web demos use modern HTML5/CSS3/JavaScript

### C# Code
- Use PascalCase for public members
- Include XML documentation comments
- Follow Godot C# conventions
- Implement abstract Event base class for new event types

## Testing

### Python Tests
- **Location**: `python_prototypes/tests/`
- **Runner**: `python3 run_tests.py` (uses unittest)
- **Coverage**: 61 test cases covering all core functionality
- **Structure**: Mirrors `core/` module organization

### Unified Testing (GUT Framework)
- **Location**: `tests/test_scene.tscn` and `addons/gut/`
- **Purpose**: Test both C# and GDScript implementations in Godot environment
- **Features**:
  - Visual test runner with progress tracking
  - Migrated C# unit tests for full integration testing
  - Cross-language compatibility verification
  - Real-time result display with color coding
  - Comprehensive test coverage: Calendar, IndexedTimeWheel, CTBManager
  - Focus on integration rather than isolated unit testing

## Important Files

- `docs/PROJECT_STATUS.md` - Current project status and milestones
- `docs/API_DOCS.md` - Generated API documentation
- `docs/DEVELOPMENT_NOTES.md` - Development history and decisions
- `python_prototypes/CSHARP_MAPPING.md` - Python → C# correspondence
- `scripts/csharp/PYTHON_MAPPING.md` - C# → Python correspondence
- `project.godot` - Godot project configuration
- `sync_code.py` - Code synchronization tool between languages
- `addons/gut/` - Unified testing framework for Godot
- `tests/test_scene.tscn` - Visual test runner scene

## Development Workflow

### Standard Development Flow
**Python Prototype → C# Port → (Future) GDScript Migration**

This project follows a hybrid development approach where Python serves as the rapid prototyping environment and C# provides the production-ready Godot implementation.

#### Phase 1: Python Prototyping
1. **Rapid Development**: Implement new features in Python first
2. **Testing**: Write comprehensive unit tests using pytest
3. **Documentation**: Update API documentation and examples
4. **Validation**: Use web demos to validate functionality

#### Phase 2: C# Production Port
1. **Code Translation**: Port Python code to C# following naming conventions
2. **Godot Integration**: Adapt for Godot-specific requirements
3. **Type Safety**: Add static typing and error handling
4. **Performance**: Optimize for production use

#### Phase 3: Future GDScript Migration (Planned)
- Consider GDScript for simpler systems if C# performance isn't critical
- Maintain same API structure for consistency

### Code Correspondence System

The project maintains strict correspondence between Python and C# implementations:

- **Mapping Files**:
  - `python_prototypes/CSHARP_MAPPING.md` - Python → C# correspondence
  - `scripts/csharp/PYTHON_MAPPING.md` - C# → Python correspondence
- **Synchronized APIs**: Method signatures and functionality remain consistent
- **Test Parity**: Both implementations have equivalent test coverage

### Making Changes

#### When Adding New Features:
1. **Start with Python**: Implement and test in `python_prototypes/game_system/`
2. **Add Tests**: Create corresponding test file in `python_prototypes/tests/`
3. **Document**: Update API docs and mapping files
4. **Port to C#**: Implement in `scripts/csharp/core/`
5. **Add C# Tests**: Create test in `tests/core/`
6. **Update Mappings**: Update both mapping documentation files

#### When Modifying Existing Code:
1. **Determine Lead**: Decide if Python or C# is the authoritative version
2. **Make Changes**: Implement in the lead version first
3. **Test Thoroughly**: Ensure all tests pass
4. **Sync**: Update the corresponding implementation
5. **Verify**: Run both test suites to ensure compatibility

## Development Notes

The Python prototypes serve as the reference implementation, with the C# version being a port for Godot integration. The project emphasizes stability - avoid major API changes to the core time management and CTB systems as they are considered feature-complete.

### Current Status
- **Core Systems**: Calendar, CTB Manager, and Indexed Time Wheel are fully synchronized
- **Test Coverage**: Both Python and C# have comprehensive test suites
- **Documentation**: Mapping files maintain correspondence between implementations
- **Unified Testing**: GUT framework provides cross-language testing in Godot
- **Automation**: sync_code.py enables automated code synchronization

## Latest Updates (2025-06-27)

### Calendar System Streamlining
1. **Method Reduction**: Removed redundant Calendar methods to focus on core functionality
   - **Deleted**: All computed properties (`current_month`, `current_day_in_month`, etc.)
   - **Deleted**: Separate era query methods (`get_current_era_name`, `get_current_era_year`)
   - **Inlined**: Time calculations directly into display and info methods
   - **Preserved**: Core functionality (timestamp, time advancement, era anchoring, formatting)

2. **Test Updates**: Updated all test files to use `get_time_info()` for computed values
   - Python tests: 62 test cases, 100% pass rate maintained
   - Removed direct property access in favor of info dictionary access

3. **Documentation Maintenance**: 
   - Added critical reminder to update documentation before commits
   - Regenerated API documentation to reflect streamlined Calendar interface
   - Updated both Python and C# implementations consistently

### Previous Updates (2024-06-26)

### New Features Added
1. **GUT Testing Framework**:
   - Unified test runner for C# and GDScript in Godot
   - Visual test interface with progress tracking
   - Command-line test execution support
   - **Migrated all C# unit tests to GUT framework for integration testing**

2. **Code Synchronization Tool**:
   - `sync_code.py` for automated Python ↔ C# synchronization
   - Mapping file auto-generation and updates
   - Dry-run mode for safe preview of changes

3. **Project Structure Optimization**:
   - Cleaned up Python prototype directory structure
   - Consolidated testing framework to use unittest
   - Removed unnecessary files and empty directories
   - **Eliminated duplicate C# unit test files in favor of GUT integration tests**

4. **Enhanced Development Commands**:
   - `/sync` command for code synchronization
   - `/test` command for unified testing
   - Improved command-line workflow

### Testing Framework Migration
- **Migrated C# Tests**: All Calendar, IndexedTimeWheel, and CTBManager tests now run in GUT
- **Focus on Integration**: Tests now validate Godot-C# integration rather than isolated units
- **Comprehensive Coverage**:
  - Calendar: Basic functionality, time advancement, era system, reset, formatting
  - IndexedTimeWheel: Basic operations, scheduling methods, future events, complex scenarios
  - CTBManager: Basic functionality, character management, event handling
- **Removed**: `tests/csharp/` directory (tests migrated to GUT framework)

### Configuration Updates
- Updated `project.godot` with TestRunner autoload
- Enhanced global CLAUDE.md with command-line features
- Fixed Alt+Enter line break support for Windows environment

## 🚨 Critical Development Notes

### Encoding Issues Warning
- **File Encoding**: All files must use UTF-8 encoding
- **Chinese Comments**: Ensure Chinese text is properly encoded, especially when working in WSL
- **C# Files**: Found encoding issues in C# files with corrupted Chinese comments (lines 97-105 in IndexedTimeWheel.cs)
- **Python Files**: Maintain UTF-8 encoding for all Chinese documentation and comments
- **WSL Environment**: Extra attention needed when editing files from WSL to maintain encoding consistency

### Recent Code Improvements (IndexedTimeWheel)
- **Thread Safety**: Extracted private `_schedule_internal` method to optimize lock usage
- **Performance**: Reduced redundant `get_time()` calls
- **Debugging**: Added runtime assertions for better error detection
- **Code Quality**: Improved error messages and parameter validation
- **Status**: C# improvements successfully back-ported to Python (2024-06-26)

## Documentation Maintenance Rules

**Important**: This CLAUDE.md file should be updated whenever significant changes are made to:
- Project structure or architecture
- Development workflow or commands
- Testing frameworks or tools
- Code synchronization processes
- New features or major bug fixes
- **Encoding or internationalization issues**

**Update Triggers**:
- After implementing new tools or frameworks
- When changing development workflows
- After major refactoring or restructuring
- When adding new development commands
- Following significant bug fixes or optimizations
- **After discovering and fixing encoding problems**

**Maintenance Process**:
1. Document changes immediately after implementation
2. Update relevant sections with new information
3. Add entries to "Latest Updates" section with dates
4. Review and update file paths if changed
5. Ensure commands and examples are current and tested
6. **Verify encoding consistency across all edited files**
7. **⚠️ CRITICAL: Always update documentation files before committing:**
   - Regenerate API documentation: `python3 python_prototypes/generate_docs.py`
   - Update mapping files if code structure changed
   - Update this CLAUDE.md file to reflect any significant changes
   - Review and update PROJECT_STATUS.md if milestones completed