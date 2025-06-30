## 第三层：运行时角色
## 游戏进行中拥有完整状态的活跃人物
class_name Character
extends Node

const CharacterInstance = preload("res://scripts/gdscript/entities/character/CharacterInstance.gd")

# 实例引用
@export var instance: CharacterInstance
@export var character_id: String

# 当前状态
@export var current_health: int = 100
@export var current_age: int = 0
@export var is_alive: bool = true

# 动态属性（会随游戏进行变化）
@export var current_mood: String = "neutral"  # happy, sad, angry, neutral
@export var stress_level: int = 0
@export var energy_level: int = 100

# 疾病和状态效果
@export var diseases: Array[String] = []
@export var temporary_traits: Array[String] = []
@export var status_effects: Array[Dictionary] = []

# 社交关系（动态变化）
@export var relationships: Dictionary = {}  # character_id -> relationship_data
@export var reputation: Dictionary = {}     # faction_id -> reputation_value

# 婚姻和家庭状态
@export var current_spouse_id: String = ""
@export var children_ids: Array[String] = []
@export var is_married: bool = false
@export var marriage_satisfaction: int = 50

# 位置和活动
@export var current_location: String = ""
@export var current_activity: String = "idle"
@export var activity_progress: float = 0.0

# 技能经验和发展
@export var skill_experience: Dictionary = {}
@export var skill_modifiers: Dictionary = {}  # 临时加成/减成
@export var learning_focus: String = ""

# 装备和财产
@export var equipment: Array[String] = []
@export var personal_wealth: int = 0
@export var owned_titles: Array[String] = []

# 在家族中的地位
@export var house_position: String = "member"  # leader, heir, member
@export var house_loyalty: int = 100
@export var succession_order: int = -1

func _init(instance_ref: CharacterInstance = null, id: String = ""):
    instance = instance_ref  
    character_id = id
    if instance:
        _initialize_from_instance()

func _ready():
    if instance:
        _initialize_from_instance()

# 从实例初始化运行时状态
func _initialize_from_instance():
    if not instance:
        return
    
    character_id = instance.instance_id
    
    # 复制基础能力值
    for ability in instance.abilities:
        skill_experience[ability] = instance.abilities[ability] * 100
    
    # 设置初始装备
    equipment = instance.starting_equipment.duplicate()
    
    # 设置家族地位
    house_position = instance.initial_house_position

# 更新年龄（每年调用）
func update_age(current_year: int):
    if not instance:
        return
    
    current_age = instance.get_age_at_year(current_year)
    
    # 检查是否应该死亡
    if instance.should_die(current_year):
        die("natural_death")

# 角色死亡
func die(cause: String = "unknown"):
    is_alive = false
    current_health = 0
    # TODO: 触发死亡事件，处理继承等

# 获取当前有效能力值（基础+修正）
func get_effective_ability(ability: String) -> int:
    var base = get_base_ability(ability)
    var modifier = skill_modifiers.get(ability, 0)
    return max(1, base + modifier)

# 获取基础能力值
func get_base_ability(ability: String) -> int:
    var experience = skill_experience.get(ability, 0)
    return experience / 100  # 简单的经验转能力算法

# 处理关系变化
func modify_relationship(target_id: String, change: int, reason: String = ""):
    if not relationships.has(target_id):
        relationships[target_id] = {"value": 0, "history": []}
    
    relationships[target_id].value += change
    relationships[target_id].history.append({
        "change": change,
        "reason": reason,
        "timestamp": Time.get_unix_time_from_system()
    })

# 获取与指定角色的关系值
func get_relationship_value(target_id: String) -> int:
    return relationships.get(target_id, {"value": 0}).value

# 执行个人活动
func perform_activity(activity_type: String, duration: float = 1.0) -> Dictionary:
    current_activity = activity_type
    activity_progress = 0.0
    
    var result = {
        "success": true,
        "activity": activity_type,
        "character": self,
        "effects": {}
    }
    
    # 根据活动类型处理不同效果
    match activity_type:
        "study":
            _handle_study_activity(result)
        "socialize":
            _handle_social_activity(result)
        "rest":
            _handle_rest_activity(result)
        "work":
            _handle_work_activity(result)
    
    return result

# 处理学习活动
func _handle_study_activity(result: Dictionary):
    var focus_skill = learning_focus if learning_focus != "" else "learning"
    skill_experience[focus_skill] = skill_experience.get(focus_skill, 0) + 10
    result.effects[focus_skill + "_exp"] = 10

# 处理社交活动
func _handle_social_activity(result: Dictionary):
    energy_level = max(0, energy_level - 10)
    current_mood = "happy"
    result.effects["mood"] = "improved"

# 处理休息活动  
func _handle_rest_activity(result: Dictionary):
    energy_level = min(100, energy_level + 20)
    stress_level = max(0, stress_level - 5)
    result.effects["energy"] = 20

# 处理工作活动
func _handle_work_activity(result: Dictionary):
    energy_level = max(0, energy_level - 15)
    var work_skill = "stewardship"  # 默认工作技能
    skill_experience[work_skill] = skill_experience.get(work_skill, 0) + 5
    result.effects["productivity"] = true

# 检查是否可以执行特定活动
func can_perform_activity(activity_type: String) -> bool:
    if not is_alive:
        return false
    
    match activity_type:
        "study": return energy_level >= 20
        "socialize": return current_mood != "sick"
        "work": return energy_level >= 15
        _: return true

# 获取角色状态摘要
func get_status_summary() -> Dictionary:
    return {
        "id": character_id,
        "name": instance.template.historical_name if instance else "Unknown",
        "age": current_age,
        "alive": is_alive,
        "health": current_health,
        "mood": current_mood,
        "activity": current_activity,
        "house_position": house_position
    }