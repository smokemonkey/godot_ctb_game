# Run Python Prototype Tests

Execute the Python prototype test suite to verify core system functionality.

## Usage
- `/project:run-python-tests` - Run all Python tests
- `/project:run-python-tests [module]` - Run specific module tests

## Command
Please run Python prototype tests: $ARGUMENTS

Follow these steps:

1. **Setup Environment**:
   - Change to `python_prototypes/` directory
   - Verify virtual environment is activated (or activate it)
   - Check that dependencies are installed

2. **Identify Test Scope**:
   - If no arguments: run all tests via `run_tests.py`
   - If module specified: run specific test file
   - Available modules: calendar, indexed_time_wheel, ctb_manager, game_world

3. **Execute Tests**:
   - Run `python3 run_tests.py` for full test suite
   - Or run specific test file: `python3 -m pytest tests/test_[module].py`
   - Capture test output and results

4. **Analyze Results**:
   - Report test pass/fail statistics
   - Identify any failing tests and reasons
   - Check test coverage if available
   - Note performance of time-critical tests

5. **Compare with GDScript**:
   - Cross-reference results with GDScript implementation
   - Identify any behavioral differences
   - Suggest synchronization if APIs have diverged

6. **Generate Report**:
   - Summarize test outcomes
   - Report any issues or failures
   - Suggest fixes for failing tests
   - Update documentation if tests reveal API changes

## Test Commands
```bash
cd python_prototypes
python3 run_tests.py                    # All tests
python3 -m pytest tests/test_calendar.py           # Calendar only
python3 -m pytest tests/test_indexed_time_wheel.py # TimeWheel only
python3 -m pytest tests/test_ctb_manager.py        # CTB only
python3 -m pytest tests/test_game_world.py         # GameWorld only
```

## Test Coverage
- **Calendar**: 62 test cases covering time management and era system
- **IndexedTimeWheel**: Event scheduling, circular buffer, future events
- **CTBManager**: Character management, turn processing, event execution
- **GameWorld**: Unified coordination and integration testing