extends RefCounted
class_name ConfigManagerMock

## ConfigManager的Mock类，用于单元测试
## 提供固定的配置值，避免依赖真实的配置文件

## 模拟的配置值
var time_hours_per_day: int = 24
var time_days_per_year: int = 360
var time_epoch_start_year: int = -2000

var ctb_time_wheel_buffer_size: int = 4320
var ctb_action_delay_min_days: int = 1
var ctb_action_delay_max_days: int = 180
var ctb_action_delay_peak_days: int = 90

var display_show_hour_by_default: bool = false
var display_month_names: Array[String] = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月"
]

var debug_enable_logging: bool = false
var debug_log_time_advancement: bool = false
var debug_log_event_execution: bool = false

## 模拟_get_config_value方法
func _get_config_value(property: String, default_value: Variant) -> Variant:
    if has_method("get"):
        return get(property)
    return default_value

## 静态方法兼容
static func _get_config_value_static(property: String, default_value: Variant) -> Variant:
    # 返回默认配置值
    match property:
        "time_hours_per_day": return 24
        "time_days_per_year": return 360
        "time_epoch_start_year": return -2000
        "ctb_time_wheel_buffer_size": return 4320
        "ctb_action_delay_min_days": return 1
        "ctb_action_delay_max_days": return 180
        "ctb_action_delay_peak_days": return 90
        "display_show_hour_by_default": return false
        "debug_enable_logging": return false
        "debug_log_time_advancement": return false
        "debug_log_event_execution": return false
        _: return default_value