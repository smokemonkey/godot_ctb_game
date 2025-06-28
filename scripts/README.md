# Scripts 目录说明

本目录包含游戏的脚本实现，现在主要使用GDScript开发。

## 目录结构

```
scripts/
├── gdscript/                    # GDScript 实现 (主要开发语言)
│   ├── core/                   # 核心游戏系统
│   │   ├── Calendar.gd         # 日历系统
│   │   ├── CTBManager.gd       # CTB管理器
│   │   └── IndexedTimeWheel.gd # 时间轮实现
│   ├── shared/                 # 共享组件
│   │   └── interfaces/
│   │       └── Schedulable.gd  # 可调度接口基类
│   ├── development/            # 开发示例
│   │   └── SchedulableExample.gd # 可调度对象示例
│   ├── managers/               # 系统管理器
│   │   ├── ConfigManager.gd    # 配置管理
│   │   ├── AudioManager.gd     # 音频管理
│   │   └── SceneManager.gd     # 场景管理
│   ├── resources/              # 资源类
│   │   └── GameConfig.gd       # 游戏配置资源
│   └── IntegratedSystemTest.gd # UI集成测试
├── csharp/                     # C# 实现 (已弃用，保留作参考)
│   ├── core/                   # 原C#核心系统
│   │   ├── Calendar.cs         # 日历系统 (过时)
│   │   ├── CTBManager.cs       # CTB管理器 (过时)
│   │   └── IndexedTimeWheel.cs # 时间轮实现 (过时)
│   └── PYTHON_MAPPING.md       # 历史对应关系文档
├── CLAUDE.md                   # 开发指导文档
└── README.md                   # 本文件
```

## 语言架构现状

### GDScript (主要开发语言) ✅
- **优势**: 与Godot深度集成、无编译步骤、快速迭代
- **适用**: 所有游戏逻辑、UI交互、核心系统
- **当前状态**: ✅ 全面实现，包括新Schedulable架构

### Python (原型验证) ✅
- **用途**: 算法验证、单元测试、Web演示
- **位置**: `../python_prototypes/`
- **状态**: ✅ 与GDScript版本保持同步

### C# (已弃用) ❌
- **状态**: 已标记为legacy，不再维护
- **原因**: 编译复杂度、开发效率问题
- **保留**: 作为参考实现，文件已标记为过时

## 新架构特性

### Schedulable系统
- **接口统一**: 任何对象都可以实现Schedulable接口被调度
- **解耦设计**: CTB系统不再依赖具体的角色类型
- **灵活扩展**: 角色、事件、天气等都使用相同的调度机制

### 实现对应关系

| 系统模块 | Python 原型 | GDScript 实现 | 文件位置 |
|----------|-------------|---------------|----------|
| 可调度接口 | `schedulable.py` | `Schedulable.gd` | `shared/interfaces/` |
| 战斗角色 | `combat_actor.py` | `SchedulableExample.gd` | `development/` |
| CTB管理器 | `ctb_manager_v2.py` | `CTBManager.gd` | `core/` |
| 日历系统 | `calendar.py` | `Calendar.gd` | `core/` |
| 时间轮 | `indexed_time_wheel.py` | `IndexedTimeWheel.gd` | `core/` |
| 配置管理 | N/A | `ConfigManager.gd` | `managers/` |
| 游戏配置 | N/A | `GameConfig.gd` | `resources/` |

## 开发流程

### 当前推荐流程
1. **Python验证**: 在Python中验证新算法和逻辑
2. **GDScript实现**: 直接在GDScript中实现功能
3. **同步测试**: 确保Python和GDScript版本一致

### 特性开发
1. 优先考虑在GDScript中直接开发
2. 复杂算法可先用Python验证
3. 保持两个版本的API一致

### 架构扩展示例
```gdscript
# 创建新的可调度对象
class WeatherEvent extends Schedulable:
    func execute() -> Variant:
        print("天气变化: 开始下雨")
        return self

    func should_reschedule() -> bool:
        return true

# 添加到CTB系统
var weather = WeatherEvent.new("weather", "天气系统")
ctb_manager.add_event(weather)
```

## 测试体系

### GDScript测试
- `../tests/gdscript/test_event_system.gd` - 新架构测试
- `../tests/gdscript/TestGameWorld.gd` - 统一测试协调器

### Python测试
- `../python_prototypes/tests/test_event_system.py` - 对应测试

### 集成测试
- `../scenes/integrated_system_test.tscn` - 可视化集成测试

## 注意事项

- **主要开发**: 现在专注于GDScript开发
- **Python同步**: 保持Python版本作为算法参考
- **C#过时**: 不再维护C#版本，文件已标记legacy
- **接口稳定**: Schedulable架构已确定，避免大改