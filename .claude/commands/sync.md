# Sync Code Between Implementations

Synchronize code changes between Python, C#, and GDScript implementations of the CTB game systems.

## Usage
- `/project:sync python gdscript [file]` - Sync Python changes to GDScript
- `/project:sync gdscript python [file]` - Sync GDScript changes to Python  
- `/project:sync csharp gdscript [file]` - Sync C# changes to GDScript
- `/project:sync gdscript csharp [file]` - Sync GDScript changes to C#
- `/project:sync check` - Check mapping consistency without syncing code

## Command
Please synchronize code between implementations: $ARGUMENTS

Follow these steps:

1. **Parse Arguments**: 
   - If first argument is "check": perform mapping consistency check only
   - Otherwise: Extract source language, target language, and optional file specification
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

7. **Update Mapping Documentation**:
   - Automatically update `scripts/gdscript/PYTHON_MAPPING.md` if syncing with Python
   - Automatically update `scripts/gdscript/CSHARP_MAPPING.md` if syncing with C#
   - Document any API changes or additions in mapping files
   - Verify method correspondence is accurate and complete
   - Update implementation status and synchronization notes

8. **Update Project Documentation**:
   - Update CLAUDE.md if significant architectural changes
   - Note synchronization and mapping updates in commit message
   - Update last modified dates in mapping files

## Check Mode (when first argument is "check")
If the first argument is "check", skip code synchronization and only verify mapping consistency:

1. **Load Mapping Files**: Read both PYTHON_MAPPING.md and CSHARP_MAPPING.md
2. **Scan Implementations**: Extract actual APIs from all implementation files
3. **Compare Documentation vs Reality**: Check if documented methods exist and match
4. **Report Discrepancies**: List any missing, outdated, or incorrect mappings
5. **Suggest Updates**: Recommend what needs to be fixed in mapping files

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