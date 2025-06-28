extends Node

## 配置管理器 - Autoload单例
## 提供全局配置访问和热重载功能

# 预加载GameConfig类
const GameConfig = preload("res://scripts/gdscript/resources/GameConfig.gd")

signal config_changed()

## 当前配置实例
var config: GameConfig

## 默认配置文件路径
const DEFAULT_CONFIG_PATH = "res://config/game_config.tres"

func _ready():
    load_config()

## 加载配置文件
func load_config(path: String = DEFAULT_CONFIG_PATH) -> bool:
    if not FileAccess.file_exists(path):
        print("配置文件不存在，创建默认配置: ", path)
        create_default_config(path)
    
    var loaded_config = load(path) as GameConfig
    if loaded_config == null:
        push_error("无法加载配置文件: " + path)
        # 如果加载失败，使用默认配置
        config = GameConfig.new()
        return false
    
    config = loaded_config
    
    # 验证配置
    if not config.validate():
        push_error("配置文件验证失败，使用默认配置")
        config = GameConfig.new()
        return false
    
    print("配置加载成功: ", path)
    if config.debug_enable_logging:
        print(config.get_summary())
    
    config_changed.emit()
    return true

## 创建默认配置文件
func create_default_config(path: String) -> void:
    # 确保目录存在
    var dir = path.get_base_dir()
    if not DirAccess.dir_exists_absolute(dir):
        DirAccess.open("res://").make_dir_recursive(dir.trim_prefix("res://"))
    
    var default_config = GameConfig.new()
    var error = ResourceSaver.save(default_config, path)
    if error != OK:
        push_error("无法创建默认配置文件: " + path)
    else:
        print("已创建默认配置文件: ", path)

## 保存当前配置
func save_config(path: String = DEFAULT_CONFIG_PATH) -> bool:
    if config == null:
        push_error("没有配置可保存")
        return false
    
    var error = ResourceSaver.save(config, path)
    if error != OK:
        push_error("保存配置失败: " + path)
        return false
    
    print("配置已保存: ", path)
    return true

## 重新加载配置（热重载）
func reload_config() -> bool:
    print("重新加载配置...")
    return load_config()

## 内部方法：获取配置值，带fallback逻辑
func _get_config_value(property: String, default_value: Variant) -> Variant:
    # 首先尝试使用实例的config
    if config != null:
        return config.get(property)
    # 如果没有配置实例，尝试静态加载
    return _get_config_value_static(property, default_value)

## 获取时间系统配置的便捷访问器
var time_hours_per_day: int:
    get: return _get_config_value("time_hours_per_day", 24)

var time_days_per_year: int:
    get: return _get_config_value("time_days_per_year", 360)

var time_epoch_start_year: int:
    get: return _get_config_value("time_epoch_start_year", -2000)

## 获取CTB系统配置的便捷访问器
var ctb_time_wheel_buffer_size: int:
    get: return _get_config_value("ctb_time_wheel_buffer_size", 4320)

var ctb_action_delay_min_days: int:
    get: return _get_config_value("ctb_action_delay_min_days", 1)

var ctb_action_delay_max_days: int:
    get: return _get_config_value("ctb_action_delay_max_days", 180)

var ctb_action_delay_peak_days: int:
    get: return _get_config_value("ctb_action_delay_peak_days", 90)

## 获取显示配置的便捷访问器
var display_show_hour_by_default: bool:
    get: return _get_config_value("display_show_hour_by_default", false)

var display_month_names: Array[String]:
    get: return _get_config_value("display_month_names", [])

## 获取调试配置的便捷访问器
var debug_enable_logging: bool:
    get: return _get_config_value("debug_enable_logging", false)

var debug_log_time_advancement: bool:
    get: return _get_config_value("debug_log_time_advancement", false)

var debug_log_event_execution: bool:
    get: return _get_config_value("debug_log_event_execution", false)

## 静态fallback方法：用于非autoload环境
static func _get_config_value_static(property: String, default_value: Variant) -> Variant:
    var config_path = "res://config/game_config.tres"
    # 使用try-catch机制处理加载失败
    var loaded_config = load(config_path)
    if loaded_config != null and loaded_config.has_method("get"):
        return loaded_config.get(property)
    # 如果加载失败（例如在headless模式下），返回默认值
    return default_value

## 开发者命令：在运行时更新配置
func dev_update_config(property: String, value: Variant) -> bool:
    if config == null:
        return false
    
    if not config.has_method("set"):
        return false
    
    config.set(property, value)
    
    if config.validate():
        config_changed.emit()
        print("配置已更新: %s = %s" % [property, value])
        return true
    else:
        push_error("配置更新失败，值无效")
        return false
