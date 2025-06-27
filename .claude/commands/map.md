# Update Implementation Mappings

Update the correspondence documentation between Python, C#, and GDScript implementations.

## Usage
- `/project:update-mapping` - Update all mapping files
- `/project:update-mapping [language]` - Update specific language mapping (python, csharp)

## Command
Please update implementation mappings: $ARGUMENTS

Follow these steps:

1. **Identify Mapping Scope**:
   - If no arguments: update both Python and C# mappings
   - If language specified: update only that mapping
   - Target files: `scripts/gdscript/PYTHON_MAPPING.md`, `scripts/gdscript/CSHARP_MAPPING.md`

2. **Analyze Current Implementations**:
   - Read GDScript implementation files in `scripts/gdscript/`
   - Read Python implementation files in `python_prototypes/core/`
   - Read C# implementation files in `scripts/csharp/core/`

3. **Compare APIs**:
   - Extract public methods and properties from each implementation
   - Identify parameter types and return values
   - Note any language-specific adaptations or differences
   - Check for new methods or removed methods

4. **Update Python Mapping**:
   - Update `scripts/gdscript/PYTHON_MAPPING.md`
   - Document GDScript ↔ Python method correspondence
   - Note any API changes or additions
   - Update status and synchronization notes

5. **Update C# Mapping**:
   - Update `scripts/gdscript/CSHARP_MAPPING.md` 
   - Document GDScript ↔ C# method correspondence
   - Note language-specific differences (generics, typing, etc.)
   - Update legacy status and phase-out notes

6. **Verify Completeness**:
   - Ensure all public APIs are documented
   - Check that mappings are bidirectional
   - Verify technical differences are explained
   - Update last modified dates

7. **Update Project Documentation**:
   - Update CLAUDE.md if significant changes
   - Note any breaking changes or new features
   - Update development workflow if needed

## Mapping Files
- `scripts/gdscript/PYTHON_MAPPING.md` - GDScript ↔ Python correspondence
- `scripts/gdscript/CSHARP_MAPPING.md` - GDScript ↔ C# correspondence

## Systems to Map
- **Calendar**: Time management and era system
- **IndexedTimeWheel**: Event scheduling data structure  
- **CTBManager**: Battle system coordination
- **TestGameWorld**: Unified test coordinator
- **Event Classes**: Base Event and Character classes