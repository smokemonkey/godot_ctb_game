# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid Godot 4.4 game project with C#, Python, and GDScript components for a turn-based game featuring:
- Custom calendar system (360 days/year, 24 hours/day)
- CTB (Conditional Turn-Based) battle system
- Indexed time wheel for efficient event scheduling
- Triple implementation in C# (Godot), Python (prototyping), and GDScript (primary)

## Architecture

The project has three main implementation layers:

### 1. GDScript Implementation (Primary)
- **Location**: `scripts/gdscript/core/` (core systems), `scripts/gdscript/` (UI), `tests/gdscript/` (tests)
- **Status**: Primary implementation, actively developed
- **Core Systems**:
  - `scripts/gdscript/core/Calendar.gd` - Time management system with configurable parameters
  - `scripts/gdscript/core/CTBManager.gd` - Event-based battle system using indexed time wheel
  - `scripts/gdscript/core/IndexedTimeWheel.gd` - Circular buffer for efficient event scheduling
  - `scripts/gdscript/core/GameConfig.gd` - Configuration resource system
  - `scripts/gdscript/core/ConfigManager.gd` - Autoload configuration manager
- **Test Coordination**: `tests/gdscript/TestGameWorld.gd` - Unified test coordinator
- **UI Interface**: `scripts/gdscript/IntegratedSystemTest.gd` - Complete UI test interface
- **Game Scene**: `scenes/integrated_system_test.tscn`

### 2. Godot Game Engine (C#)
- **Location**: `scripts/csharp/core/` and `tests/csharp/core/`
- **Status**: Legacy implementation, to be phased out
- **Core Systems**:
  - `Calendar.cs` - Time management system starting from 2000 BC
  - `CTBManager.cs` - Event-based battle system using indexed time wheel
  - `IndexedTimeWheel.cs` - Circular buffer for efficient event scheduling
- **Game Scene**: `scenes/my_ctb_game.tscn`

### 3. Python Prototypes
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

# Set up environment, actually not necessary anymore
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
- The project used C# scripting with .NET support but now we switch to GDscript for swift prototyping.
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
- Follow existing module structure in `core/`
- Use pytest for testing with descriptive test names
- Include type hints and docstrings
- Web demos use modern HTML5/CSS3/JavaScript

### GDScript Code
- **Private Methods**: Use `_` prefix for private/internal methods (e.g., `_calculate_delay()`, `_update_internal_state()`)
- **Public API**: Methods without `_` prefix are considered public interface
- **Documentation**: Use `##` for public method documentation, `#` for private method comments
- **Naming**: Use snake_case for all methods and variables
- **Indentation**: Always use 4 spaces, never tabs

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
6. **Confirm**: Ask for permission when you want to change interface or delete code/test file

## Development Notes

The Python prototypes serve as the reference implementation, with the C# version being a port for Godot integration. The project emphasizes stability - avoid major API changes to the core time management and CTB systems as they are considered feature-complete.

### Current Status
- **Core Systems**: Calendar, CTB Manager, and Indexed Time Wheel are fully synchronized
- **Test Coverage**: Both Python and C# have comprehensive test suites
- **Documentation**: Mapping files maintain correspondence between implementations
- **Unified Testing**: GUT framework provides cross-language testing in Godot
- **Automation**: sync_code.py enables automated code synchronization

## Latest Updates (2025-06-27)

### 🚀 Schedulable Architecture Implementation
1. **完整架构重构**: 成功实现基于Schedulable接口的新CTB系统
   - **创建**: `Schedulable.gd` - 统一的可调度接口基类
   - **创建**: `CombatActor.gd` - 实现Schedulable的战斗角色类
   - **重构**: `CTBManager.gd` - 移除Character依赖，使用Schedulable接口
   - **同步**: Python版本完全对应，API保持一致

2. **解耦合设计优势**:
   - **接口标准化**: 任何对象都可以实现Schedulable被调度
   - **类型无关**: CTB不再依赖具体的角色或事件类型
   - **易于扩展**: 天气、剧情、任何游戏对象都可以轻松添加
   - **测试友好**: 13个测试用例全部通过，覆盖所有核心功能

3. **CombatActor特性**:
   - **随机行动**: 从预定义列表中随机选择行动（"攻击", "防御", "技能"等）
   - **三角分布**: 使用配置参数计算下次行动时间
   - **状态管理**: 支持活跃/非活跃状态切换
   - **控制台输出**: "角色张飞执行行动：攻击"等友好显示

4. **技术实现**:
   - **双语言同步**: Python和GDScript版本API完全一致
   - **向后兼容**: 保持时间管理回调接口不变
   - **混合调度**: 角色和事件可以在同一系统中调度
   - **性能优化**: 保持O(1)时间复杂度的事件处理

5. **文档更新**:
   - **清理过时内容**: 移除Windows特定批处理文件引用
   - **架构文档**: 更新所有README文件反映新架构
   - **测试文档**: 详细说明新的测试体系和用例

### GDScript Implementation Migration
1. **Complete Code Translation**: Successfully migrated all core systems from C# to GDScript
   - **Converted**: `Calendar.cs` → `Calendar.gd` with full feature parity
   - **Converted**: `IndexedTimeWheel.cs` → `IndexedTimeWheel.gd` with thread safety via Mutex
   - **Converted**: `CTBManager.cs` → `CTBManager.gd` with event system integration
   - **Created**: `TestGameWorld.gd` - unified test coordinator replacing manual component management
   - **Created**: `IntegratedSystemTest.gd` - complete UI test interface in GDScript

2. **Architecture Simplification**:
   - **Primary Implementation**: GDScript is now the main development target
   - **C# Status**: Marked as legacy, to be phased out
   - **Unified Testing**: Single GDScript test scene replaces complex C#/GUT setup
   - **Reduced Complexity**: Eliminated C# compilation dependencies for core development

3. **Technical Improvements**:
   - **Signal System**: Proper Godot signal integration for event coordination
   - **Resource Management**: RefCounted-based classes for automatic memory management
   - **Type Safety**: Strong typing where possible while maintaining GDScript flexibility
   - **Performance**: Native GDScript performance without C# interop overhead

4. **Development Benefits**:
   - **Faster Iteration**: No compilation step required
   - **Better Integration**: Native Godot editor support and debugging
   - **Simplified Testing**: Direct script execution without build pipeline
   - **Easier Maintenance**: Single language for core game logic

5. **C# Legacy Code Management**:
   - **Status**: All C# files marked as legacy with header comments
   - **Project Config**: C# support disabled in project.godot for faster debugging
   - **Build System**: .csproj file renamed to .disabled to prevent compilation
   - **GUT Framework**: Re-enabled (supports both GDScript and C# testing)
   - **Preservation**: All C# code preserved for reference and future porting

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
   - Try to use Chinese in the updated part of document/commit but don't translate the whole file suddenly

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
   - Update this CLAUDE.md file to reflect any significant changes
   - Review and update PROJECT_STATUS.md if milestones completed
   - Clean outdated content from README files
   - Ensure Windows-specific instructions are in CLAUDE.local.md