# Python 原型对应关系

本文档说明 Godot C# 实现与 Python 原型代码的对应关系。

## 开发流程

**原型开发** (Python) → **生产实现** (C#) → **游戏集成** (Godot)

## 核心文件对应关系

| C# 实现文件 | Python 原型文件 | Python 测试文件 | C# 测试文件 | 同步状态 |
|-------------|----------------|-----------------|-------------|----------|
| `core/Calendar.cs` | `../../python_prototypes/core/calendar/calendar.py` | `../../python_prototypes/tests/core/calendar/test_calendar.py` | `../../tests/csharp/core/CalendarTests.cs` | ✅ 已同步 |
| `core/CTBManager.cs` | `../../python_prototypes/core/ctb_manager/ctb_manager.py` | `../../python_prototypes/tests/core/ctb_manager/test_ctb_manager.py` | `../../tests/csharp/core/CTBManagerTests.cs` | ✅ 已同步 |
| `core/IndexedTimeWheel.cs` | `../../python_prototypes/core/indexed_time_wheel/indexed_time_wheel.py` | `../../python_prototypes/tests/core/indexed_time_wheel/test_indexed_time_wheel.py` | `../../tests/csharp/core/IndexedTimeWheelTests.cs` | ✅ 已同步 |

## 对应的测试文件

| C# 测试文件 | Python 测试文件 | 说明 |
|-------------|----------------|------|
| `../../tests/csharp/core/CalendarTests.cs` | `../../python_prototypes/tests/core/calendar/test_calendar.py` | 测试用例基本对应 |
| `../../tests/csharp/core/CTBManagerTests.cs` | `../../python_prototypes/tests/core/ctb_manager/test_ctb_manager.py` | 测试用例基本对应 |
| `../../tests/csharp/core/IndexedTimeWheelTests.cs` | `../../python_prototypes/tests/core/indexed_time_wheel/test_indexed_time_wheel.py` | 测试用例基本对应 |

## 从 Python 移植到 C# 的注意事项

### 命名转换规则
- **类名**: 保持相同 (PascalCase)
- **方法名**: `snake_case` → `PascalCase`
- **参数和变量**: `snake_case` → `camelCase`  
- **常量**: `UPPER_SNAKE_CASE` → `PascalCase`
- **私有字段**: `_snake_case` → `_camelCase`

### 语言特性差异

| 特性 | Python | C# | 移植注意事项 |
|------|--------|----|--------------| 
| **类型系统** | 动态类型 + 类型提示 | 静态类型 | 需要明确所有类型声明 |
| **属性访问** | 直接访问或 `@property` | Properties | 使用 C# property 语法 |
| **集合初始化** | `[]`, `{}` | `new List<>()`, `new Dictionary<>()` | 使用 C# 集合初始化器 |
| **异常处理** | `try/except` | `try/catch` | 异常类型可能不同 |
| **字符串格式化** | f-string | string interpolation | `f"{var}"` → `$"{var}"` |
| **None 值** | `None` | `null` | 需要考虑可空类型 |

### C# 特有的增强功能

1. **线程安全**: 添加了 `lock` 语句保护共享资源
2. **类型安全**: 编译期类型检查避免运行时错误
3. **内存管理**: 自动垃圾回收 + 确定性资源释放
4. **Godot 集成**: 
   - `.uid` 文件用于 Godot 资源管理
   - 支持 Godot 的序列化系统
   - 可以在 Godot 编辑器中直接调试

## 修改 C# 代码后的同步指南

### 如果修改了 C# 代码:
1. 考虑是否需要同步回 Python 原型
2. 如果是 Godot 特有功能，在 Python 中添加注释说明
3. 更新对应的测试用例
4. 更新文档和注释

### 如果 Python 原型有新功能:
1. 首先在 Python 中完善实现和测试
2. 参考本文档进行 C# 移植
3. 适配 Godot 特有的约定和限制
4. 添加 C# 特有的类型安全检查
5. **⚠️ 重要：更新本文档的同步状态**
6. **⚠️ 重要：同时更新 `../../python_prototypes/CSHARP_MAPPING.md`**

### 🔄 Mapping 文档维护提醒

**每次修改代码时必须检查和更新的文档：**
- 本文档 (`scripts/csharp/PYTHON_MAPPING.md`)
- Python 对应文档 (`../../python_prototypes/CSHARP_MAPPING.md`)
- 主项目文档 (`../../CLAUDE.md`)

**⚠️ 强烈建议：** 建立开发checklist，确保mapping文档与代码同步更新！

## 开发工具和命令

### Python 原型测试
```bash
cd ../../python_prototypes
python run_tests.py
```

### C# 测试 (在 Godot 中)
- 打开 Godot 项目
- 在项目设置中启用 C# 测试
- 或在命令行使用 dotnet test (如果有 .csproj)

### 查看 Python 文档和演示
```bash
cd ../../python_prototypes
python generate_docs.py
python examples/start_web_demo.py
```

## Godot C# 特有约定

1. **文件命名**: 每个类一个 `.cs` 文件，文件名与类名相同
2. **命名空间**: 使用 `Core` 作为根命名空间
3. **Godot 生命周期**: 考虑 `_Ready()`, `_Process()` 等方法
4. **序列化**: 使用 Godot 的 `[Export]` 特性而非 .NET 的序列化
5. **资源管理**: 使用 Godot 的资源系统

## 版本同步记录

- **最后同步时间**: 2025-06-25
- **Python 原型版本**: v2.0 (稳定版本)
- **C# 实现版本**: 与 Python 同步
- **主要差异**: C# 版本添加了线程安全和 Godot 集成功能

## 未来规划

1. **考虑 GDScript 移植**: 如果性能要求不高，可能移植到 GDScript
2. **自动化同步**: 考虑建立自动化脚本来同步常见的修改
3. **文档生成**: 建立从 Python 文档自动生成 C# 文档的工具