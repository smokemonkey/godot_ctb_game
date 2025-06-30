## 第二层：游戏实例
## 游戏开始时根据模板生成的具体人物，包括预定的未来事件
class_name CharacterInstance  
extends Resource

const CharacterTemplate = preload("res://scripts/gdscript/entities/character/CharacterTemplate.gd")

# 模板引用
@export var template: CharacterTemplate
@export var instance_id: String

# 具体化的能力值（不再随机）
@export var abilities: Dictionary = {
    "diplomacy": 10,
    "martial": 10, 
    "stewardship": 10,
    "intrigue": 10,
    "learning": 10,
    "prowess": 10
}

# 确定的生卒时间（基于模板生成）
@export var actual_birth_year: int
@export var actual_death_year: int = -1  # -1表示尚未确定

# 预定的未来事件
@export var predetermined_events: Array[Dictionary] = []
# 事件格式: {"year": 1066, "type": "marriage", "target_id": "spouse_id", "probability": 0.8}

# 初始装备和资源
@export var starting_equipment: Array[String] = []
@export var starting_titles: Array[String] = []
@export var starting_relationships: Dictionary = {}

# 潜在发展路径
@export var potential_career_paths: Array[String] = []
@export var scripted_personality_traits: Array[String] = []

# 家族归属
@export var house_id: String = ""
@export var faction_id: String = ""
@export var initial_house_position: String = "member"  # leader, heir, member

func _init(template_ref: CharacterTemplate = null, id: String = ""):
    template = template_ref
    instance_id = id
    if template:
        _generate_from_template()

# 根据模板生成具体数据
func _generate_from_template():
    if not template:
        return
    
    # 处理互斥变体生成
    if template.is_variant_group and not _should_generate_variant():
        return  # 该变体未被选中，不生成
    
    # 生成能力值（支持扩展语法）
    _generate_abilities_from_template()
    
    # 处理多相位关系
    _resolve_relationship_phases()
    
    # 确定生卒年（基于历史记录或合理推算）
    actual_birth_year = template.birth_year if template.birth_year > 0 else _estimate_birth_year()
    if template.death_year > 0:
        actual_death_year = template.death_year
    
    # 生成预定事件
    _generate_predetermined_events()

# 计算能力值（确定性算法，避免随机）
func _calculate_ability_value(min_val: int, max_val: int) -> int:
    # 使用模板ID的哈希确保确定性
    var hash_seed = template.template_id.hash()
    return min_val + (hash_seed % (max_val - min_val + 1))

# 估算出生年（当模板不确定时）
func _estimate_birth_year() -> int:
    # 基于父母年龄、历史事件等推算
    return 1000  # TODO: 实现智能推算逻辑

# 添加预定事件
func add_predetermined_event(year: int, event_type: String, data: Dictionary = {}):
    predetermined_events.append({
        "year": year,
        "type": event_type,
        "data": data,
        "probability": data.get("probability", 1.0)
    })

# 获取指定年份的预定事件
func get_events_for_year(year: int) -> Array[Dictionary]:
    var events = []
    for event in predetermined_events:
        if event.year == year:
            events.append(event)
    return events

# 检查是否应该在指定年份出生
func should_be_born(current_year: int) -> bool:
    return current_year >= actual_birth_year

# 检查是否应该在指定年份死亡
func should_die(current_year: int) -> bool:
    return actual_death_year > 0 and current_year >= actual_death_year

# 获取在指定年份的年龄
func get_age_at_year(year: int) -> int:
    if year < actual_birth_year:
        return 0
    return year - actual_birth_year

# 验证实例数据
func validate() -> bool:
    return template != null and instance_id != "" and actual_birth_year > 0

# 生成能力值（支持扩展语法）
func _generate_abilities_from_template():
    for ability in template.abilities:
        var ability_def = template.parse_ability_value(ability)
        abilities[ability] = _generate_ability_value(ability_def)

# 根据能力定义生成具体值
func _generate_ability_value(ability_def: Dictionary) -> int:
    match ability_def.type:
        "fixed":
            return ability_def.value
        "normal_distribution":
            return _generate_normal_distribution(
                ability_def.center,
                ability_def.deviation,
                ability_def.min,
                ability_def.max
            )
        "random":
            return _generate_deterministic_random(ability_def.min, ability_def.max)
        "complex":
            return _generate_complex_ability(ability_def.params)
        _:
            return 10  # 默认值

# 生成正态分布值（史料不详的能力）
func _generate_normal_distribution(center: int, deviation: float, min_val: int, max_val: int) -> int:
    # 使用Box-Muller变换生成正态分布，但保持确定性
    var hash_seed = (template.template_id + str(center)).hash()
    var u1 = float(hash_seed % 10000) / 10000.0
    var u2 = float((hash_seed / 10000) % 10000) / 10000.0
    
    var z = sqrt(-2.0 * log(u1)) * cos(2.0 * PI * u2)
    var result = int(center + z * deviation)
    
    return clamp(result, min_val, max_val)

# 生成确定性随机值
func _generate_deterministic_random(min_val: int, max_val: int) -> int:
    var hash_seed = template.template_id.hash()
    return min_val + (hash_seed % (max_val - min_val + 1))

# 生成复杂能力值
func _generate_complex_ability(params: Dictionary) -> int:
    # 处理复杂的能力定义，如文化融合等
    var base = params.get("base", 10)
    var bonus = params.get("cultural_bonus", 0)
    return base + bonus

# 解析多相位关系
func _resolve_relationship_phases():
    # 处理多相位父亲关系
    if template.possible_fathers.size() > 0:
        var selected_father = _select_weighted_option(template.possible_fathers)
        if selected_father != "":
            # 更新实际父亲ID和相关特质
            var father_data = template.possible_fathers[selected_father]
            # TODO: 应用父亲选择的影响（特质、能力加成等）
    
    # 处理多相位母亲关系
    if template.possible_mothers.size() > 0:
        var selected_mother = _select_weighted_option(template.possible_mothers)
        if selected_mother != "":
            # 更新实际母亲ID和相关特质
            var mother_data = template.possible_mothers[selected_mother]

# 权重选择算法
func _select_weighted_option(options: Dictionary) -> String:
    if options.size() == 0:
        return ""
    
    var total_weight = 0
    for option in options:
        total_weight += options[option].weight
    
    # 使用确定性随机选择
    var hash_seed = template.template_id.hash()
    var random_value = hash_seed % total_weight
    
    var current_weight = 0
    for option in options:
        current_weight += options[option].weight
        if random_value < current_weight:
            return option
    
    # 回退：返回第一个选项
    return options.keys()[0]

# 检查是否应该生成该变体
func _should_generate_variant() -> bool:
    if not template.is_variant_group:
        return true
    
    # 使用共享UID的哈希来决定生成哪个变体
    var hash_seed = template.shared_uid.hash()
    var selected_weight = hash_seed % 100
    
    return selected_weight < template.variant_weight

# 生成预定事件（基于史料和推测）
func _generate_predetermined_events():
    # 基于历史不确定性生成事件
    var uncertainty = template.historical_uncertainty
    
    # 如果存在神话化程度，可能添加传奇事件
    var mythical_degree = uncertainty.get("mythologization_degree", 0.0)
    if mythical_degree > 0.5:
        add_predetermined_event(actual_birth_year + 20, "legendary_deed", {
            "probability": mythical_degree
        })
    
    # 基于史料可靠性添加历史事件
    var reliability = uncertainty.get("source_reliability", 0.7)
    if reliability > 0.8:
        # 高可靠性史料，添加确定事件
        for event in template.historical_events:
            add_predetermined_event(actual_birth_year + 25, "historical_event", {
                "event": event,
                "probability": 1.0
            })

# 获取生成摘要
func get_generation_summary() -> Dictionary:
    return {
        "instance_id": instance_id,
        "template_source": template.template_id if template else "unknown",
        "generation_method": "extended_syntax",
        "ability_uncertainties": _get_ability_uncertainties(),
        "relationship_phases": _get_relationship_phase_summary(),
        "variant_selection": template.shared_uid if template and template.is_variant_group else "",
        "historical_reliability": template.get_source_reliability("existence") if template else 0.0
    }

# 获取能力不确定性摘要
func _get_ability_uncertainties() -> Dictionary:
    var uncertainties = {}
    for ability in abilities:
        if template and template.is_ability_uncertain(ability):
            uncertainties[ability] = {
                "method": "distribution" if template.abilities[ability] < 0 else "random",
                "source": template.get_ability_source(ability)
            }
    return uncertainties

# 获取关系相位摘要
func _get_relationship_phase_summary() -> Dictionary:
    var summary = {}
    if template and template.possible_fathers.size() > 0:
        summary["father_options"] = template.possible_fathers.size()
    if template and template.possible_mothers.size() > 0:
        summary["mother_options"] = template.possible_mothers.size()
    return summary