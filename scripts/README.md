# Scripts 目录说明

本目录包含游戏的脚本实现，支持多种编程语言。

## 目录结构

```
scripts/
├── csharp/              # C# 实现 (当前使用)
│   ├── core/           # 核心游戏系统
│   └── PYTHON_MAPPING.md  # Python 对应关系文档
├── gdscript/           # GDScript 实现 (未来规划)
│   ├── core/           # 核心游戏系统
│   └── PYTHON_MAPPING.md  # Python 对应关系文档  
└── README.md           # 本文件
```

## 语言选择指南

### C# (推荐用于复杂逻辑)
- **优势**: 静态类型、高性能、完整的.NET生态
- **适用**: 复杂算法、数据处理、高频计算
- **当前状态**: ✅ 已实现核心系统

### GDScript (推荐用于游戏逻辑)  
- **优势**: 与Godot深度集成、语法简洁、快速开发
- **适用**: 游戏逻辑、UI交互、场景管理
- **当前状态**: ⏳ 未来规划

## 开发流程

1. **原型阶段**: Python快速开发 (`../python_prototypes/`)
2. **生产阶段**: 选择C#或GDScript进行实现
3. **维护阶段**: 保持多语言版本同步

## 文件对应关系

所有实现都与Python原型保持严格对应：

| 系统模块 | Python 原型 | C# 实现 | GDScript 实现 |
|----------|-------------|---------|---------------|
| 日历系统 | `calendar.py` | `Calendar.cs` | `calendar.gd` (规划中) |
| CTB系统 | `ctb_manager.py` | `CTBManager.cs` | `ctb_manager.gd` (规划中) |
| 时间轮 | `indexed_time_wheel.py` | `IndexedTimeWheel.cs` | `indexed_time_wheel.gd` (规划中) |

## 使用建议

### 新功能开发
1. 先在Python中验证逻辑
2. 根据性能需求选择C#或GDScript
3. 保持API接口一致

### 现有功能修改
1. 确定主导版本(通常是Python原型)
2. 同步更新所有语言实现  
3. 更新对应的mapping文档

## 注意事项

- 每个语言目录都有独立的`PYTHON_MAPPING.md`文档
- 修改代码时必须同步更新mapping文档
- 建议在git commit前检查所有文档的一致性