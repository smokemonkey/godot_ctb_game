extends Schedulable
class_name SchedulableExample

## Schedulable接口的示例实现类
## 
## 这是一个开发用的示例类，展示如何实现Schedulable接口。
## 适合作为学习参考，不是最终的游戏角色实现。
## 
## 主要功能：
## - 演示Schedulable接口的所有方法实现
## - 提供随机行动系统作为测试用途
## - 展示时间计算和状态管理的基本模式

var faction: String
var is_active: bool
var action_list: Array[String]

func _init(p_id: String, p_name: String, p_faction: String = "中立"):
    super._init(p_id, p_name, "%s的战斗行动" % p_name)
    faction = p_faction
    is_active = true
    
    # 预定义行动列表
    action_list = [
        "攻击",
        "防御", 
        "使用技能",
        "移动",
        "观察",
        "休息",
        "准备反击",
        "蓄力"
    ]

## 执行角色行动
func execute() -> Variant:
    if not is_active:
        print("角色 %s 处于非活跃状态，跳过行动" % name)
        return null
    
    # 随机选择一个行动
    var random_action = action_list[randi() % action_list.size()]
    print("角色 %s 执行行动: %s" % [name, random_action])
    
    return {
        "actor": self,
        "action": random_action,
        "success": true
    }

## 计算下次行动时间
func calculate_next_schedule_time(current_time: int) -> int:
    # 使用配置中的三角分布参数
    var min_days = ConfigManager.ctb_action_delay_min_days
    var max_days = ConfigManager.ctb_action_delay_max_days  
    var peak_days = ConfigManager.ctb_action_delay_peak_days
    var days = _triangular_distribution(min_days, max_days, peak_days)
    var hours = int(days * ConfigManager.time_hours_per_day)
    return current_time + hours

## 是否需要重复调度
func should_reschedule() -> bool:
    return is_active

## 设置活跃状态
func set_active(active: bool) -> void:
    is_active = active
    if not active:
        print("角色 %s 已设置为非活跃状态" % name)
    else:
        print("角色 %s 已激活" % name)

## 三角分布实现
func _triangular_distribution(min_val: float, max_val: float, mode: float) -> float:
    var u = randf()
    var c = (mode - min_val) / (max_val - min_val)
    
    if u < c:
        return min_val + sqrt(u * (max_val - min_val) * (mode - min_val))
    else:
        return max_val - sqrt((1 - u) * (max_val - min_val) * (max_val - mode))

## 获取角色信息
func get_character_info() -> Dictionary:
    return {
        "id": id,
        "name": name,
        "faction": faction,
        "is_active": is_active,
        "trigger_time": trigger_time,
        "description": description
    }

func get_type_identifier() -> String:
    return "SchedulableExample"