# Character System CLAUDE.md

三层角色系统设计与实现文档

## ⚠️ 关键设计原则

1. **三层分离**: Template（模板）→ Instance（实例）→ Character（运行时）
2. **确定性生成**: 第二层避免随机性，使用哈希算法确保可重现性
3. **Jomini兼容**: 第一层支持P社游戏格式，AI辅助数据转换
4. **状态管理**: 第三层处理完整的动态游戏状态

## 系统架构

### 第一层：CharacterTemplate（静态模板）
**职责**: 游戏开始前就存在的历史人物数据，类似"史书记录"

**核心特征**:
- 历史身份信息（姓名、朝代、文化、宗教）
- 血缘关系网络（父母、配偶、子女）
- 能力范围而非确定值（diplomacy: [5,15]）
- 模糊信息支持（负数表示不确定）
- Jomini引擎格式兼容性

**使用场景**:
```gdscript
var template = CharacterTemplate.new("ragnar_001", "拉格纳·洛德布罗克")
template.ability_ranges = {"martial": [15, 20], "diplomacy": [8, 12]}
template.birth_year = 845
template.death_year = -1  # 史料不详
```

### 第二层：CharacterInstance（游戏实例）
**职责**: 游戏开始时根据模板生成的具体化人物

**核心特征**:
- 具体化的能力值（不再随机，基于哈希确定性生成）
- 预定的未来事件（结婚、死亡、重要决策）
- 初始装备和社会地位
- 潜在发展路径规划

**确定性算法**:
```gdscript
func _calculate_ability_value(min_val: int, max_val: int) -> int:
    var hash_seed = template.template_id.hash()
    return min_val + (hash_seed % (max_val - min_val + 1))
```

### 第三层：Character（运行时状态）
**职责**: 游戏进行中拥有完整动态状态的活跃人物

**核心特征**:
- 完整生命状态（健康、年龄、情绪、疾病）
- 动态社交关系和声誉系统
- 婚姻家庭状态管理
- 个人活动和技能发展
- 家族地位和继承权

**状态管理**:
```gdscript
func perform_activity(activity_type: String) -> Dictionary:
    # 返回详细的活动结果和状态变化
```

## 与回合制系统的关系

**明确分工**:
- **House**: 唯一的Schedulable实体，被CTB系统调度
- **Character**: House的成员，不直接参与回合制
- **活动执行**: House选择合适的Character执行活动

**集成模式**:
```gdscript
# House.gd中
func execute() -> Variant:
    var best_character = _select_character_for_activity(current_activity)
    return best_character.perform_activity(current_activity)
```

## Jomini引擎兼容性

### AI辅助实现方案
**文件格式支持**:
- CK3/EU4/Stellaris角色定义文件解析
- 复杂嵌套结构和特殊语法处理
- 多语言本地化文本支持
- 版本兼容性处理

**实现示例**:
```gdscript
# CharacterTemplate中
static func from_jomini_data(jomini_data: Dictionary) -> CharacterTemplate:
    var template = CharacterTemplate.new()
    template.jomini_id = jomini_data.get("id", -1)
    template.historical_name = jomini_data.get("first_name", "")
    # AI辅助实现复杂数据映射
    return template
```

**AI优势**:
- 理解P社mod格式的复杂语法规则
- 批量处理数千个角色定义文件  
- 处理格式不一致和缺失数据
- 多语言和特殊字符处理

## 开发工作流

### 使用Gemini CLI处理大量数据
```bash
# 分析mod文件格式
gemini --telemetry=false -p "@mod_files/ 分析这些CK3角色文件，生成GDScript解析器"

# 批量数据转换
gemini --telemetry=false --yolo -p "@character_data/ 将所有角色数据转换为CharacterTemplate格式"
```

### 测试策略
1. **模板验证**: 确保历史数据完整性
2. **实例生成**: 验证确定性算法的一致性
3. **运行时状态**: 测试复杂状态变化和事件处理
4. **集成测试**: 与House系统的协作

## 文件结构

```
entities/character/
├── CLAUDE.md              # 本文档
├── CharacterTemplate.gd   # 第一层：静态历史模板
├── CharacterInstance.gd   # 第二层：游戏开始实例  
└── Character.gd          # 第三层：运行时状态
```

## 与现有系统集成

**House系统集成**:
- House管理多个Character作为成员
- Character提供技能和能力支持House活动
- 家族地位影响Character的行为选择

**CTB系统集成**:
- Character不直接参与CTB调度
- 通过House间接影响回合制进程
- 个人活动在House回合内执行

## P社兼容性策略

### 开发优先级
1. **第一阶段**: 核心逻辑 - 让三层角色系统和CTB调度机制稳定运行
2. **第二阶段**: 数据明文化 - 硬编码数据转为明文配置文件
3. **第三阶段**: 格式兼容 - 添加Jomini语法解析器吸引P社mod作者

### Jomini语法支持
**什么是Jomini**: P社游戏引擎（CK3、EU4、HOI4、Stellaris）使用的数据格式

**标准Jomini角色定义**:
```
1234 = {
    first_name = "Ragnar"
    dynasty = 1337
    religion = norse_pagan
    culture = norwegian
    trait = brave
    trait = strong
    birth = 845.1.1
    father = 5678
    mother = 9012
    diplomacy = 8
    martial = 16
}
```

**多相位支持** (扩展语法):
```
mordred = {
    first_name = "Mordred"
    possible_fathers = {
        arthur = { weight = 50 trait = bastard }
        lot_of_orkney = { weight = 50 trait = legitimate }
    }
    if_father_arthur = {
        diplomacy = 12
        martial = 16
    }
}
```

## 远古历史游戏扩展语法

### 核心设计理念
远古历史游戏的特殊性在于**史料的不确定性**和**历史诠释的多样性**。CharacterTemplate层的设计正是为了处理这些现实问题。

### 1. 史料不确定性支持

**负数表示记载不详**:
```
# 标准P社语法（每局固定）
sun_wu = {
    martial = 20
    diplomacy = 8
}

# 扩展语法：史料真实性
sun_wu = {
    martial = 7          # 正数：史料明确记载
    diplomacy = -5       # 负数：以5为中心的正态分布
    stewardship = 0      # 零：史料完全缺失，纯随机
    intrigue = -12       # 负数：推测能力很高，但不确定
}
```

**数值解释**:
- **正数**: 历史明确记载的能力值
- **负数**: 史料模糊，以绝对值为中心的概率分布
- **零**: 史料完全缺失，1-20范围内随机

### 2. 多相位历史人物

**血缘关系的史学争议**:
```
mordred = {
    first_name = "Mordred"
    
    # 史学界争议的血缘关系
    possible_fathers = {
        arthur = { 
            weight = 60 
            trait = bastard
            martial_bonus = 2
            source = "geoffrey_of_monmouth"
        }
        lot_of_orkney = { 
            weight = 40 
            trait = legitimate
            diplomacy_bonus = 3
            source = "welsh_triads"
        }
    }
}
```

**人物身份的历史争议**:
```
homer = {
    # 荷马是否真实存在的争议
    existence_probability = 0.7
    
    possible_identities = {
        single_poet = { 
            weight = 30 
            trait = genius
            learning = 18
        }
        multiple_authors = { 
            weight = 70
            trait = collective_work
            learning = -8  # 不确定的平均水平
        }
    }
}
```

### 3. 共享UID互斥生成

**避免矛盾角色同时存在**:
```
# 方案A：条件互斥组
character_group_robin = {
    shared_uid = "robin_hood_001"
    exclusive_spawn = true
    
    robin_noble = {
        weight = 30
        first_name = "Robert"
        dynasty = huntingdon
        trait = noble
        backstory = "dispossessed_noble"
    }
    
    robin_outlaw = {
        weight = 70
        first_name = "Robin"
        culture = anglo_saxon
        trait = outlaw
        backstory = "peasant_rebel"
    }
}

# 方案B：历史分歧点
arthur_variants = {
    shared_uid = "arthur_pendragon"
    
    arthur_historical = {
        weight = 40
        birth = 485
        death = 537
        trait = warlord
        martial = 16
        source = "nennius_historia"
    }
    
    arthur_legendary = {
        weight = 60
        birth = 470
        death = -1  # 不死传说
        trait = mythical_king
        martial = 20
        source = "geoffrey_romance"
    }
}
```

### 4. 复杂历史背景处理

**时代背景的不确定性**:
```
# 特洛伊战争是否真实发生
trojan_war_characters = {
    historical_certainty = 0.3
    
    # 如果历史事件不发生，相关角色也不出现
    conditional_spawn = "trojan_war_happened"
    
    achilles = {
        martial = 20
        trait = legendary_warrior
        conditional_traits = {
            if_mythical = ["invulnerable"]
            if_historical = ["skilled_fighter"]
        }
    }
}
```

**文化融合的渐进性**:
```
alexander_successors = {
    # 继业者的希腊化程度随时间变化
    time_based_evolution = true
    
    seleucus = {
        culture_blend = {
            macedonian = 0.7
            persian = 0.2
            babylonian = 0.1
        }
        # 能力值随文化融合程度变化
        diplomacy = { base = 12, cultural_bonus = 2 }
    }
}
```

### 5. 扩展语法解析

**JominiParser增强**:
```gdscript
static func parse_ability_value(value: Variant) -> Dictionary:
    if value is int:
        if value > 0:
            return {"type": "fixed", "value": value}
        elif value < 0:
            return {
                "type": "normal_distribution", 
                "center": abs(value), 
                "deviation": 2,
                "min": 1, 
                "max": 20
            }
        else:  # value == 0
            return {"type": "random", "min": 1, "max": 20}
    elif value is Dictionary:
        return {"type": "complex", "params": value}

static func parse_exclusive_group(group_data: Dictionary) -> Array:
    # 处理共享UID和互斥生成逻辑
    var variants = []
    for variant_name in group_data.variants:
        variants.append({
            "name": variant_name,
            "weight": group_data.variants[variant_name].weight,
            "data": group_data.variants[variant_name]
        })
    return variants
```

### P社明文化设计

**剧本系统**:
- 所有历史数据、人物、国家、事件都是纯文本文件
- Mod通过覆盖同名文件实现内容替换
- 零学习成本，P社mod作者可直接参与

**存档格式**:
```
# P社存档也是明文（压缩存储）
characters={
    1234={
        first_name="William"
        relations={
            5678={
                opinion_modifier={
                    murdered_my_brother={ value=-50 date="1066.10.14" }
                }
                total_opinion=-30
            }
        }
    }
}
```

**关系存储**:
- 角色间关系（仇恨值、好感度）直接存储在角色对象内
- 双向关系分别存储，带时间戳和原因
- 复杂查询通过遍历实现，简单直观

### 工具链生态

**现成编辑器**:
- **CWTools**: VS Code插件，语法高亮、错误检查
- **PDX Script**: 轻量级语法支持
- **在线角色编辑器**: 可视化创建角色

**推荐配置**:
- 开发者: VS Code + CWTools
- Mod作者: VS Code + PDX Script  
- 普通用户: 在线编辑器

### 实现计划

**JominiParser.gd**:
```gdscript
static func parse_character_definition(text: String) -> CharacterTemplate:
    # 解析 first_name = "Name" 语法
    # 解析 trait = value 数组语法
    # 转换为 CharacterTemplate 对象
```

**数据流向**:
```
Jomini文本文件 → JominiParser → CharacterTemplate → CharacterInstance → Character
```

**扩展语法优势**:
- **史料真实性**: 负数系统反映远古历史的不确定性
- **历史诠释多样性**: 多相位人物支持不同史学观点
- **互斥生成**: 避免逻辑矛盾的历史人物同时存在
- **时代特色**: 专门针对远古历史游戏的独特需求

**vs P社标准语法**:
- P社：每局游戏完全固定，适合中世纪有详细记录的时期
- 扩展：每局不同，适合远古时期史料稀缺、争议众多的特点

**生态兼容性**:
- 借用P社成熟工具链
- 巨大的现成内容库作为基础
- 活跃的mod社区
- 完全自由的后台逻辑设计
- 向下兼容标准P社语法

## 未来扩展

**数据层增强**:
- 更复杂的血缘关系网络
- 基于AI的性格生成系统
- 历史事件的连锁反应机制
- P社mod内容的批量导入工具

**游戏性增强**:
- 角色间复杂外交互动
- 基于关系的动态事件生成
- 跨世代的家族传承系统
- 多相位历史的动态选择机制

## 最近实现 (2025-06-30)

**三层系统创建**:
- CharacterTemplate: 200+行，包含Jomini兼容性和历史数据管理
- CharacterInstance: 150+行，确定性生成和事件预设系统
- Character: 250+行，完整运行时状态和活动系统

**关键设计决策**:
- 从actionables目录分离出独立的entities/character结构
- 确定性算法避免随机性破坏游戏平衡
- AI辅助的Jomini格式兼容性设计
- 与现有House/CTB系统的清晰集成界面