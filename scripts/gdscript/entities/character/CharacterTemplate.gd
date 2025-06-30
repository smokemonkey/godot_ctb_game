## 第一层：静态角色模板
## 游戏开始前就存在的历史人物数据，类似"史书记录"
class_name CharacterTemplate
extends Resource

# 基础身份信息
@export var template_id: String
@export var historical_name: String
@export var dynasty_id: String
@export var culture: String
@export var religion: String

# 历史时间信息
@export var birth_year: int = -1  # 负数表示不确定
@export var death_year: int = -1  # 负数表示不确定
@export var historical_events: Array[String] = []

# 血缘关系（支持多相位）
@export var father_id: String = ""
@export var mother_id: String = ""
@export var spouse_ids: Array[String] = []
@export var children_ids: Array[String] = []

# 多相位关系支持（史学争议）
@export var possible_fathers: Dictionary = {}
# 格式: {"father_id": {"weight": 50, "trait": "bastard", "source": "geoffrey"}}
@export var possible_mothers: Dictionary = {}
@export var relationship_uncertainty: bool = false

# 共享UID互斥生成
@export var shared_uid: String = ""           # 共享的唯一标识
@export var exclusive_variants: Dictionary = {} # 互斥的变体定义
@export var is_variant_group: bool = false    # 是否为变体组
@export var variant_weight: int = 50          # 在变体组中的权重

# 固定特质（历史确定的）
@export var confirmed_traits: Array[String] = []
@export var legendary_titles: Array[String] = []

# 能力值定义（支持扩展语法）
@export var abilities: Dictionary = {
    "diplomacy": 10,     # 正数：确定值
    "martial": -15,      # 负数：以15为中心的正态分布
    "stewardship": 0,    # 零：完全随机
    "intrigue": 8,
    "learning": -5,
    "prowess": 12
}

# 能力值的史料可靠性元数据
@export var ability_reliability: Dictionary = {
    "diplomacy": {"source": "plutarch", "confidence": 0.8},
    "martial": {"source": "speculation", "confidence": 0.3},
    "stewardship": {"source": "unknown", "confidence": 0.0}
}

# 传统能力范围（向后兼容）
@export var ability_ranges: Dictionary = {}

# 史料不确定性元数据
@export var historical_uncertainty: Dictionary = {
    "existence_probability": 1.0,      # 人物存在的概率
    "source_reliability": 0.7,         # 主要史料的可靠性
    "anachronism_risk": 0.2,          # 时代错误的风险
    "mythologization_degree": 0.1      # 神话化程度
}

# Jomini引擎兼容性支持
@export var jomini_id: int = -1
@export var jomini_source_mod: String = ""
@export var jomini_raw_data: Dictionary = {}

func _init(id: String = "", name: String = ""):
    template_id = id
    historical_name = name

# 从Jomini格式创建模板（AI辅助实现）
static func from_jomini_data(jomini_data: Dictionary) -> CharacterTemplate:
    var template = CharacterTemplate.new()
    # TODO: AI辅助实现Jomini数据解析
    return template

# 验证模板数据完整性
func validate() -> bool:
    return template_id != "" and historical_name != ""

# 获取能力值范围
func get_ability_range(ability: String) -> Array:
    return ability_ranges.get(ability, [1, 20])

# 检查是否有确定的历史记录
func has_confirmed_data(data_type: String) -> bool:
    match data_type:
        "birth": return birth_year > 0
        "death": return death_year > 0
        "father": return father_id != "" and not relationship_uncertainty
        "mother": return mother_id != "" and not relationship_uncertainty
        _: return false

# 解析能力值类型（扩展语法支持）
func parse_ability_value(ability: String) -> Dictionary:
    var value = abilities.get(ability, 0)
    
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
    else:
        return {"type": "random", "min": 1, "max": 20}

# 获取史料可靠性
func get_source_reliability(data_type: String) -> float:
    match data_type:
        "ability":
            var total_confidence = 0.0
            var count = 0
            for ability in ability_reliability:
                total_confidence += ability_reliability[ability].get("confidence", 0.5)
                count += 1
            return total_confidence / max(count, 1)
        "existence":
            return historical_uncertainty.get("existence_probability", 1.0)
        "relationships":
            return 1.0 if not relationship_uncertainty else 0.5
        _:
            return historical_uncertainty.get("source_reliability", 0.7)

# 设置多相位父亲关系
func add_possible_father(father_id: String, weight: int, additional_data: Dictionary = {}):
    possible_fathers[father_id] = {
        "weight": weight,
        "data": additional_data
    }
    relationship_uncertainty = true

# 设置多相位母亲关系
func add_possible_mother(mother_id: String, weight: int, additional_data: Dictionary = {}):
    possible_mothers[mother_id] = {
        "weight": weight,
        "data": additional_data
    }
    relationship_uncertainty = true

# 创建变体组（互斥生成）
func create_variant_group(uid: String, variants: Dictionary):
    shared_uid = uid
    exclusive_variants = variants
    is_variant_group = true

# 检查是否为史料不详的能力
func is_ability_uncertain(ability: String) -> bool:
    var value = abilities.get(ability, 0)
    return value <= 0  # 负数或零都表示不确定

# 获取能力值的史料来源
func get_ability_source(ability: String) -> String:
    return ability_reliability.get(ability, {}).get("source", "unknown")

# 检查是否存在史学争议
func has_historical_controversy() -> bool:
    return relationship_uncertainty or possible_fathers.size() > 0 or possible_mothers.size() > 0

# 生成史料摘要
func generate_historical_summary() -> Dictionary:
    return {
        "template_id": template_id,
        "historical_name": historical_name,
        "source_reliability": get_source_reliability("existence"),
        "has_controversy": has_historical_controversy(),
        "uncertain_abilities": _get_uncertain_abilities(),
        "variant_group": shared_uid if is_variant_group else "",
        "anachronism_risk": historical_uncertainty.get("anachronism_risk", 0.0)
    }

# 获取不确定的能力列表
func _get_uncertain_abilities() -> Array[String]:
    var uncertain = []
    for ability in abilities:
        if is_ability_uncertain(ability):
            uncertain.append(ability)
    return uncertain