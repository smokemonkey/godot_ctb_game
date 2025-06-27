# 项目结构说明

## GDScript 目录组织

```
scripts/gdscript/
├── core/                     # 核心游戏逻辑
│   ├── Calendar.gd          # 时间管理系统
│   ├── CTBManager.gd        # 战斗回合管理
│   └── IndexedTimeWheel.gd  # 时间轮数据结构
├── managers/                 # 管理器和自动加载单例
│   ├── ConfigManager.gd     # 配置管理器 (Autoload)
│   ├── AudioManager.gd      # 音频管理器 (占位符)
│   └── SceneManager.gd      # 场景管理器 (占位符)
├── resources/               # 配置和数据资源
│   └── GameConfig.gd        # 游戏配置资源
├── shared/                  # 共享组件
│   └── interfaces/
│       └── Schedulable.gd   # 可调度接口
├── development/             # 开发用临时代码
│   └── SchedulableExample.gd  # 可调度接口示例
└── gameplay/                # 游戏玩法相关
    └── actors/              # 角色和实体 (预留)
```

## 设计原则

### Core 目录
- **用途**: 存放游戏的核心逻辑系统
- **内容**: 算法、数据结构、业务逻辑核心
- **不应包含**: 管理器、UI、工具类、配置

### Managers 目录  
- **用途**: 系统管理器和自动加载单例
- **内容**: ConfigManager、AudioManager、SceneManager等
- **特点**: 通常作为Autoload全局访问

### Resources 目录
- **用途**: 配置资源和数据定义
- **内容**: GameConfig等Resource类
- **特点**: 可序列化的数据结构

### Shared 目录
- **用途**: 多个模块共享的组件
- **内容**: 接口、抽象类、通用工具
- **特点**: 被多个系统复用

### Development 目录
- **用途**: 临时开发用代码
- **内容**: 示例、测试、脚手架代码
- **特点**: 不是最终产品的一部分

### Gameplay 目录
- **用途**: 具体的游戏玩法实现
- **内容**: 角色、技能、物品等游戏对象
- **特点**: 面向最终游戏内容

## 优势

1. **清晰分离**: 核心逻辑与管理器分离
2. **易于维护**: 相关功能聚集在一起
3. **便于扩展**: 新功能有明确的归属目录
4. **减少耦合**: 不同职责的代码物理隔离