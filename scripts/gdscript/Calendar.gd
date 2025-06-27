extends RefCounted
class_name Calendar

## 时间单位枚举
enum TimeUnit {
	HOUR,
	DAY
}

## 游戏日历显示器 - 负责时间的格式化显示和时间管理
##
## 专为回合制游戏设计的时间系统，支持非匀速时间流逝、精确时间控制和纪年管理。
## 所有时间参数从ConfigManager配置系统读取，支持运行时配置。
##
## 配置参数:
##     时间系统通过ConfigManager.config访问以下参数：
##     - time_hours_per_day: 每天小时数
##     - time_days_per_year: 每年天数  
##     - time_epoch_start_year: 起始年份
##
## 示例:
##     var calendar = Calendar.new()  # 使用配置中的默认起始年
##     calendar.advance_time_tick()
##     print("当前年份: ", calendar.current_gregorian_year)
##     calendar.start_new_era("开元")
##     calendar.anchor_era("开元", 713)  # 开元元年=公元713年

## 每天小时数（从配置读取）
var hours_per_day: int:
	get: return ConfigManager.time_hours_per_day

## 每年天数（从配置读取）
var days_per_year: int:
	get: return ConfigManager.time_days_per_year

## 起始年份
var _base_year: int

## 当前时间（以小时为最小单位）
var _timestamp_hour: int = 0

## 当前锚定：[纪元名, 元年公元年份]
var _current_anchor: Array

## 构造函数
func _init(base_year: int = 0):
	# 如果传入0或没有传入参数，使用配置中的默认值
	if base_year == 0:
		_base_year = ConfigManager.time_epoch_start_year
	else:
		_base_year = base_year
	_current_anchor = ["uninitialized", _base_year]

## 当前年份（公元年）
var current_gregorian_year: int:
	get:
		var total_days = _timestamp_hour / hours_per_day
		return _base_year + (total_days / days_per_year)

## 锚定纪元
##
## 指定某个纪元的元年对应的公元年份，用于纪元显示计算。
## 不允许锚定到比当前时间还晚的时期。
##
## 参数:
##     era_name: 纪元名称，如"开元"
##     gregorian_year: 纪元元年对应的公元年份，如713（开元元年=公元713年）
##
## 异常:
##     当锚定年份晚于当前年份时抛出错误
##
## 示例:
##     calendar.anchor_era("开元", 713)  # 开元元年=公元713年
func anchor_era(era_name: String, gregorian_year: int) -> void:
	if era_name.strip_edges().is_empty():
		push_error("era_name cannot be empty or whitespace")
		return
	
	var current_year = current_gregorian_year
	if gregorian_year > current_year:
		push_error("不能锚定到未来时期：锚定年份%d晚于当前年份%d" % [gregorian_year, current_year])
		return
	
	# 存储为 [纪元名, 元年公元年份]
	_current_anchor = [era_name, gregorian_year]

## 改元 - 开始新纪元
##
## 从当前年份开始新的纪元。
##
## 参数:
##     name: 新纪元名称，如"永徽"、"开元"等
##
## 异常:
##     当纪元名称为空时抛出错误
##
## 示例:
##     calendar.start_new_era("永徽")  # 从当前年份开始永徽纪元
func start_new_era(name: String) -> void:
	if name.strip_edges().is_empty():
		push_error("name cannot be empty or whitespace")
		return
	
	# 改元就是锚定当前年份为新纪元的元年
	anchor_era(name, current_gregorian_year)

## 获取当前时间戳（小时数）
##
## 返回:
##     int: 从起始时间开始的总小时数
func get_timestamp() -> int:
	return _timestamp_hour

## 推进时间一个tick（1小时）
func advance_time_tick() -> void:
	_timestamp_hour += 1

## 获取当前时间信息
func get_time_info() -> Dictionary:
	var total_days = _timestamp_hour / hours_per_day
	var day_in_year = (total_days % days_per_year) + 1
	var hour_in_day = _timestamp_hour % hours_per_day
	var month = ((day_in_year - 1) / 30) + 1
	var day_in_month = ((day_in_year - 1) % 30) + 1
	
	# 获取纪元信息
	var era_name = null
	var era_year = null
	if _current_anchor.size() >= 2:
		var anchor_era_name = _current_anchor[0]
		var gregorian_year = _current_anchor[1]
		var current_year = current_gregorian_year
		if current_year >= gregorian_year:
			era_name = anchor_era_name
			era_year = current_year - gregorian_year + 1
	
	var info = {
		"timestamp": _timestamp_hour,
		"gregorian_year": current_gregorian_year,
		"month": month,
		"day_in_month": day_in_month,
		"day_in_year": day_in_year,
		"hour_in_day": hour_in_day,
		"current_era_name": era_name,
		"current_era_year": era_year,
		"current_anchor": _current_anchor
	}
	
	return info

## 重置时间到起始状态
func reset() -> void:
	_timestamp_hour = 0
	_current_anchor = ["uninitialized", _base_year]

## 格式化为公历日期显示
##
## 参数:
##     show_hour: 是否显示小时
##
## 返回:
##     格式化的日期字符串
func format_date_gregorian(show_hour: bool = false) -> String:
	var year = current_gregorian_year
	var total_days = _timestamp_hour / hours_per_day
	var day_in_year = (total_days % days_per_year) + 1
	var month = ((day_in_year - 1) / 30) + 1
	var day = ((day_in_year - 1) % 30) + 1
	var hour = _timestamp_hour % hours_per_day
	
	# 处理公元前年份
	var year_str: String
	if year < 0:
		year_str = "公元前%d年" % abs(year)
	else:
		year_str = "公元%d年" % year
	
	if show_hour:
		return "%s%d月%d日%d点" % [year_str, month, day, hour]
	else:
		return "%s%d月%d日" % [year_str, month, day]

## 格式化为纪年日期显示
##
## 参数:
##     show_hour: 是否显示小时
##
## 返回:
##     格式化的日期字符串
func format_date_era(show_hour: bool = false) -> String:
	# 获取纪元信息
	var era_name = null
	var era_year = null
	if _current_anchor.size() >= 2:
		var anchor_era_name = _current_anchor[0]
		var gregorian_year = _current_anchor[1]
		var current_year = current_gregorian_year
		if current_year >= gregorian_year:
			era_name = anchor_era_name
			era_year = current_year - gregorian_year + 1
	
	if era_name == null or era_year == null:
		return format_date_gregorian(show_hour)
	
	var total_days = _timestamp_hour / hours_per_day
	var day_in_year = (total_days % days_per_year) + 1
	var month = ((day_in_year - 1) / 30) + 1
	var day = ((day_in_year - 1) % 30) + 1
	var hour = _timestamp_hour % hours_per_day
	
	if show_hour:
		return "%s%d年%d月%d日%d点" % [era_name, era_year, month, day, hour]
	else:
		return "%s%d年%d月%d日" % [era_name, era_year, month, day]

## 获取详细的时间状态文本
func get_time_status_text() -> String:
	var info = get_time_info()
	var gregorian = format_date_gregorian(true)
	var era = format_date_era(true)
	
	var status_lines = [
		"公历: %s" % gregorian,
		"纪年: %s" % era,
		"年内第%d天" % info["day_in_year"],
		"总计: %d小时" % info["timestamp"]
	]
	
	# 显示锚定信息
	if info["current_anchor"] != null and info["current_anchor"].size() >= 2:
		var anchor = info["current_anchor"]
		var era_name = anchor[0]
		var gregorian_year = anchor[1]
		status_lines.append("锚定: %s元年 = 公元%d年" % [era_name, gregorian_year])
	
	return "\n".join(status_lines)