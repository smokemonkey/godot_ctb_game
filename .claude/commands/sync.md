# Sync Code Between Implementations

Synchronize code changes between Python, C#, and GDScript implementations of the CTB game systems.

## Usage
- `/project:sync-code python gdscript [file]` - Sync Python changes to GDScript
- `/project:sync-code gdscript python [file]` - Sync GDScript changes to Python  
- `/project:sync-code csharp gdscript [file]` - Sync C# changes to GDScript
- `/project:sync-code gdscript csharp [file]` - Sync GDScript changes to C#

## Command
Please synchronize code between implementations: $ARGUMENTS

Follow these steps:

1. **Parse Arguments**: Extract source language, target language, and optional file specification
2. **Identify Files**: 
   - Use mapping files (`scripts/gdscript/PYTHON_MAPPING.md`, `scripts/gdscript/CSHARP_MAPPING.md`)
   - If file specified, sync only that module
   - If no file, sync all core systems (Calendar, IndexedTimeWheel, CTBManager)

3. **Read Source Implementation**: 
   - Read the source file(s) from the appropriate directory
   - Understand the current API and implementation

4. **Read Target Implementation**:
   - Read the target file(s) to understand current state
   - Identify differences and required changes

5. **Perform Synchronization**:
   - Update target implementation to match source changes
   - Maintain language-specific patterns and conventions
   - Preserve existing comments and documentation
   - Update API correspondence in mapping files

6. **Verify Synchronization**:
   - Check that all public APIs match between implementations
   - Ensure functionality is equivalent
   - Update mapping documentation if APIs changed

7. **Update Documentation**:
   - Update mapping files with any API changes
   - Update CLAUDE.md if significant architectural changes
   - Note synchronization in commit message

## Implementation Directories
- **Python**: `python_prototypes/core/`
- **C#**: `scripts/csharp/core/` (legacy)
- **GDScript**: `scripts/gdscript/` (primary)

## Core Systems
- `Calendar` - Time management system
- `IndexedTimeWheel` - Event scheduling time wheel
- `CTBManager` - CTB battle system manager
- `TestGameWorld` - Unified test coordinator

## Language-Specific Considerations
- **Python**: Dynamic typing, snake_case, exception handling
- **C#**: Static typing, PascalCase, lock statements, generics
- **GDScript**: Variant typing, snake_case, signals, Mutex threading

Maintain API compatibility while respecting each language's idioms and best practices.