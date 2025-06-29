extends Resource
class_name GameConfig

## 游戏配置资源类
## 包含所有可配置的游戏参数，支持编辑器可视化编辑

@export_group("Time System", "time_")
## 每天小时数
@export var time_hours_per_day: int = 24
## 每年天数（简化历法：12个月 × 30天）
@export var time_days_per_year: int = 360
## 游戏起始年份（公元年）
@export var time_epoch_start_year: int = -2000

@export_group("CTB System", "ctb_")
## 时间轮缓冲区大小（小时）
@export var ctb_time_wheel_buffer_size: int = 180 * 24
## 角色行动间隔最小值（天）
@export var ctb_action_delay_min_days: int = 1
## 角色行动间隔最大值（天）
@export var ctb_action_delay_max_days: int = 180
## 角色行动间隔峰值（天，用于三角分布）
@export var ctb_action_delay_peak_days: int = 90

@export_group("Calendar Display", "display_")
## 默认显示格式是否包含小时
@export var display_show_hour_by_default: bool = false
## 月份名称（用于显示，按1-12月顺序）
@export var display_month_names: Array[String] = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月"
]

@export_group("Debug Settings", "debug_")
## 是否启用调试输出
@export var debug_enable_logging: bool = false
## 时间推进时是否打印日志
@export var debug_log_time_advancement: bool = false
## 事件执行时是否打印日志
@export var debug_log_event_execution: bool = false

## 验证配置的合理性
func validate() -> bool:
    if time_hours_per_day <= 0:
        push_error("time_hours_per_day must be positive")
        return false
    if time_days_per_year <= 0:
        push_error("time_days_per_year must be positive")
        return false
    if ctb_time_wheel_buffer_size <= 0:
        push_error("ctb_time_wheel_buffer_size must be positive")
        return false
    if ctb_action_delay_min_days < 0:
        push_error("ctb_action_delay_min_days must be non-negative")
        return false
    if ctb_action_delay_max_days < ctb_action_delay_min_days:
        push_error("ctb_action_delay_max_days must be >= ctb_action_delay_min_days")
        return false
    if ctb_action_delay_peak_days < ctb_action_delay_min_days or ctb_action_delay_peak_days > ctb_action_delay_max_days:
        push_error("ctb_action_delay_peak_days must be between min and max")
        return false
    if display_month_names.size() != 12:
        push_error("display_month_names must contain exactly 12 month names")
        return false

    return true

## 获取配置摘要文本
func get_summary() -> String:
    var lines = [
        "=== 游戏配置摘要 ===",
        "时间系统:",
        "  每天%d小时，每年%d天" % [time_hours_per_day, time_days_per_year],
        "  起始年份: 公元%d年" % time_epoch_start_year,
        "CTB系统:",
        "  时间轮缓冲区: %d小时" % ctb_time_wheel_buffer_size,
        "  行动间隔: %d-%d天 (峰值%d天)" % [ctb_action_delay_min_days, ctb_action_delay_max_days, ctb_action_delay_peak_days],
        "调试设置:",
        "  日志输出: %s" % ("启用" if debug_enable_logging else "禁用")
    ]
    return "\n".join(lines)