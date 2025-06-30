# Actionables 文件夹 CLAUDE.md

实现Schedulable接口的游戏实体类，用于CTB系统集成。

## ⚠️ 关键模式

1. **Schedulable实现**: 所有actionables都继承Schedulable基类
2. **实体层次**: 阵营 → 家族(Schedulable) → 角色  
3. **直接引用**: 使用 `const Class = preload("path")` 加载依赖
4. **CTB集成**: 家族被CTB系统调度执行家族活动

## 实体系统设计

### Faction（政治实体）
**用途**: 顶级政治组织
- 管理阵营间外交关系（盟友、敌对、中立）
- 控制资源（财富、军事、经济实力）
- 包含多个家族作为成员
- 提供政治背景和战略目标

**核心功能**:
- 外交关系管理
- 资源分配和管理
- 家族成员关系和领导权
- 领土和影响力追踪

### House（可调度家族单位）
**用途**: 唯一可被CTB调度的家族组织
- **继承Schedulable**: 回合制游戏中的行动单位
- 管理角色成员及家族层次（使用entities/character系统）
- 使用成员技能执行阵营活动
- 连接个体角色和政治阵营的桥梁

**核心功能**:
- 为CTB集成实现Schedulable接口
- 角色成员管理（族长、继承人、成员）
- 家族活动执行（外交、军事、经济、文化）
- 资源管理（威望、财富、土地、军事单位）
- 根据活动需求智能选择参与者

**与Character系统集成**:
- House管理多个Character作为成员
- Character提供技能支持House活动
- Character不直接参与CTB调度，通过House间接影响游戏进程

## 实现模式

### Schedulable集成
```gdscript
extends Schedulable
class_name House

# 必需的Schedulable方法
func execute() -> Variant:
    # 选择并执行家族活动
    var action = _select_house_action()
    return _execute_house_action(action)

func calculate_next_schedule_time(current_time: int) -> int:
    return current_time + activity_cooldown

func should_reschedule() -> bool:
    return reschedule_enabled and members.size() > 0
```

### 依赖加载
```gdscript
# 在每个文件顶部
const Character = preload("res://scripts/gdscript/entities/character/Character.gd")
const Faction = preload("res://scripts/gdscript/actionables/Faction.gd")

# 使用方式
var character = Character.new(character_instance, "runtime_id")
var faction = Faction.new("faction_id", "faction_name")
```

### 活动系统
家族执行活动的流程：
1. 根据重点/优先级选择合适的行动
2. 为活动选择最适合的角色
3. 根据参与者技能计算成功率
4. 对家族资源/状态应用效果
5. 为CTB系统返回详细结果

## CTB系统集成

### 家族在CTB中的工作方式
1. **调度**: 家族像其他Schedulable一样被添加到CTB系统
2. **执行**: 触发时，House.execute()运行家族活动
3. **重调度**: 家族根据活动冷却时间自动重调度
4. **结果**: 活动返回结构化数据用于游戏状态更新

### 活动类型
- **外交谈判**: 使用外交技能高的角色
- **军事训练**: 使用武艺技能高的角色  
- **经济发展**: 使用经济技能高的角色
- **文化活动**: 使用魅力高的角色
- **情报收集**: 混合技能需求
- **联姻策划**: 战略关系建设

## 使用示例

### 创建完整的政治结构
```gdscript
# 创建阵营
var faction = Faction.new("kingdom_north", "北方王国")

# 创建家族
var house = House.new("house_stark", "史塔克家族", faction.id)
faction.add_house(house.id)

# 从entities/character系统创建角色
var ned_template = CharacterTemplate.new("ned_stark", "奈德·史塔克")
var ned_instance = CharacterInstance.new(ned_template, "ned_game_001")
var leader = Character.new(ned_instance, "ned_runtime")

var robb_template = CharacterTemplate.new("robb_stark", "罗柏·史塔克") 
var robb_instance = CharacterInstance.new(robb_template, "robb_game_001")
var heir = Character.new(robb_instance, "robb_runtime")

# 设置家族结构
house.add_member(leader)
house.add_member(heir)
house.set_leader(leader.character_id)
house.set_heir(heir.character_id)

# 添加到CTB系统
ctb_manager.schedule_with_delay(house.id, house, initial_delay)
```

### 活动执行流程
```gdscript
# CTB系统调用house.execute()
var result = house.execute()
# 返回:
{
    "house": house_reference,
    "action": "外交谈判",
    "success": true,
    "result": "外交谈判成功，家族威望提升",
    "effects": {"prestige": 5},
    "participants": [character1, character2]
}
```

## 文件组织

```
actionables/
├── CLAUDE.md          # 本文档
├── Faction.gd         # 政治实体类
└── House.gd          # 可调度家族单位类

# Character系统已移至:
entities/character/
├── CharacterTemplate.gd    # 第一层：历史模板
├── CharacterInstance.gd    # 第二层：游戏实例
└── Character.gd           # 第三层：运行时状态
```

## 最近更新 (2025-06-30)

**系统重构**
- Character系统移出actionables目录，移至entities/character/
- actionables现在只包含Schedulable实体（Faction, House）
- 更新文档反映新的系统架构
- House系统与新的三层Character系统集成

## 之前实现 (2025-06-29)

**完整实体系统**
- Faction: 400+行，包含完整的外交和资源系统
- House: 450+行，包含完整Schedulable实现和活动系统

**关键设计决策**
- 家族作为唯一Schedulable实体（而非角色或阵营）
- 基于家族重点和角色技能的活动选择
- 自动族长继承和继承人管理
- 成功/失败活动的资源效果

## 测试策略

家族应该测试：
1. 空成员列表（应优雅处理）
2. 不同活动类型和技能组合
3. 族长/继承人继承场景
4. CTB集成与各种调度模式
5. 资源管理和效果计算

## 未来增强

- 家族间联姻系统
- 阵营间战争机制
- 经济贸易路线和合约
- 角色老化和世代变化
- 基于关系的动态事件生成