# C# 代码对应关系

本文档说明 Python 原型代码与 Godot C# 实现的对应关系。

## 开发流程

Python 原型 → C# 移植 → (未来可能) GDScript 移植

## 核心文件对应关系

| Python 原型文件 | C# 实现文件 | Python 测试 | C# 测试 | 状态 |
|----------------|-------------|----------|---------|------|
| `core/calendar/calendar.py` | `../../scripts/csharp/core/Calendar.cs` | `tests/core/calendar/test_calendar.py` | `../../tests/csharp/core/CalendarTests.cs` | ✅ 已同步 |
| `core/ctb_manager/ctb_manager.py` | `../../scripts/csharp/core/CTBManager.cs` | `tests/core/ctb_manager/test_ctb_manager.py` | `../../tests/csharp/core/CTBManagerTests.cs` | ✅ 已同步 |
| `core/indexed_time_wheel/indexed_time_wheel.py` | `../../scripts/csharp/core/IndexedTimeWheel.cs` | `tests/core/indexed_time_wheel/test_indexed_time_wheel.py` | `../../tests/csharp/core/IndexedTimeWheelTests.cs` | ✅ 已同步 |
| `core/game_world.py` | - | `tests/core/test_game_world.py` | - | ❌ 待移植 |
| `core/config.py` | - | - | - | ❌ 待移植 |

## 目录结构对应

```
Python 原型结构                     Godot 实现结构
python_prototypes/                  scripts/
├── core/                           ├── csharp/core/        (当前实现)
│   ├── calendar/                   │   ├── Calendar.cs
│   ├── ctb_manager/                │   ├── CTBManager.cs
│   └── indexed_time_wheel/         │   └── IndexedTimeWheel.cs
├── tests/                          └── gdscript/core/      (未来规划)
│   └── core/                           ├── calendar.gd
│       ├── calendar/                   ├── ctb_manager.gd
│       │   └── test_calendar.py        └── indexed_time_wheel.gd
│       ├── ctb_manager/
│       │   └── test_ctb_manager.py tests/
│       └── indexed_time_wheel/     ├── csharp/core/        (当前测试)
│           └── test_indexed_time_wheel.py │ ├── CalendarTests.cs  
└── examples/                       │   ├── CTBManagerTests.cs
                                    │   └── IndexedTimeWheelTests.cs
                                    └── gdscript/core/      (未来测试)
                                        ├── test_calendar.gd
                                        ├── test_ctb_manager.gd  
                                        └── test_indexed_time_wheel.gd
```

**多语言支持说明：**
- **当前**: Python原型 ↔ C#实现
- **未来**: Python原型 ↔ C#实现 ↔ GDScript实现
- **语言选择**: 根据性能需求和团队偏好选择C#或GDScript

## API 命名对应规则

| Python (snake_case) | C# (PascalCase) | 示例 |
|---------------------|-----------------|------|
| 类名 | 相同 | `CTBManager` |
| 方法名 | `snake_case` → `PascalCase` | `add_character()` → `AddCharacter()` |
| 变量/属性 | `snake_case` → `camelCase` | `current_time` → `currentTime` |
| 常量 | `UPPER_CASE` → `PascalCase` | `HOURS_PER_DAY` → `HoursPerDay` |
| 私有字段 | `_snake_case` → `_camelCase` | `_total_hours` → `_totalHours` |

## 移植时注意事项

1. **类型安全**: C# 需要明确类型声明
2. **内存管理**: C# 使用 `using` 语句管理资源
3. **异常处理**: C# 有编译期类型检查
4. **线程安全**: C# 版本添加了 `lock` 机制
5. **Godot 集成**: C# 版本需要考虑 Godot 生命周期

## 开发指南

### 修改 Python 原型后的同步步骤：
1. 在 Python 中实现和测试新功能
2. 运行 `python run_tests.py` 确保测试通过
3. 移植到对应的 C# 文件
4. 运行 Godot 中的 C# 测试
5. **⚠️ 重要：更新本文档的状态和对应关系**
6. **⚠️ 重要：同时更新 `../../scripts/csharp/PYTHON_MAPPING.md`**

### 添加新模块的步骤：
1. 在 `game_system/` 下创建新模块
2. 编写对应的测试文件
3. 在 `scripts/csharp/core/` 下创建 C# 版本
4. 在 `tests/core/` 下创建 C# 测试
5. **⚠️ 重要：更新本文档添加新的对应关系**
6. **⚠️ 重要：同时更新 `../../scripts/csharp/PYTHON_MAPPING.md`**

### 🔄 Mapping 文档维护提醒

**每次修改代码时必须检查和更新的文档：**
- 本文档 (`CSHARP_MAPPING.md`)
- C# 对应文档 (`../../scripts/csharp/PYTHON_MAPPING.md`)
- 主项目文档 (`../../CLAUDE.md`)

**⚠️ 强烈建议：** 在git commit前运行checklist确认所有mapping文档已更新！

## 工具和命令

```bash
# Python 测试
cd python_prototypes
python run_tests.py

# 生成 API 文档
python generate_docs.py

# 启动演示服务器
python examples/start_web_demo.py
```

## 版本同步状态

- **最后同步时间**: 2025-06-25
- **Python 版本**: 稳定版本 (v2.0)
- **C# 版本**: 与 Python 同步
- **待移植模块**: `game_world.py`, `config.py`