extends GutTest

## Calendar系统单元测试
## 基于Python版本test_calendar.py移植

const ConfigManagerMock = preload("res://tests/gdscript/mocks/ConfigManagerMock.gd")

var calendar: Calendar
var config_mock: ConfigManagerMock

func before_each():
    config_mock = ConfigManagerMock.new()
    calendar = Calendar.new()

## 测试初始状态
func test_initial_state():
    assert_not_null(calendar, "Calendar应该能够创建")
    assert_eq(calendar.get_timestamp(), 0, "初始时间戳应该为0")
    assert_eq(calendar.current_gregorian_year, config_mock.time_epoch_start_year, "初始年份应该是epoch start year")
    
    var info = calendar.get_time_info()
    assert_eq(info["month"], 1, "初始月份应该是1")
    assert_eq(info["day_in_month"], 1, "初始日期应该是1日")

## 测试推进一整年
func test_advance_one_year():
    var initial_year = calendar.current_gregorian_year
    # 推进360天 * 24小时 = 8640小时
    for i in range(360 * 24):
        calendar.advance_time_tick()
    
    assert_eq(calendar.current_gregorian_year, initial_year + 1, "推进一年后年份应该增加1")
    var info = calendar.get_time_info()
    assert_eq(info["month"], 1, "新年应该是1月")
    assert_eq(info["day_in_month"], 1, "新年应该是1日")

## 测试获取时间信息
func test_get_time_info():
    # 推进100天 * 24小时 = 2400小时
    for i in range(100 * 24):
        calendar.advance_time_tick()
    # 推进5小时
    for i in range(5):
        calendar.advance_time_tick()
    
    # 设置纪元锚点避免异常
    calendar.anchor_era("测试纪元", config_mock.time_epoch_start_year)
    var info = calendar.get_time_info()
    
    assert_eq(info["gregorian_year"], config_mock.time_epoch_start_year, "公历年份应该正确")
    assert_eq(info["day_in_year"], 101, "年内第101天")
    assert_eq(info["hour_in_day"], 5, "日内第5小时")
    assert_eq(info["current_era_name"], "测试纪元", "纪元名称应该正确")
    assert_eq(info["current_era_year"], 1, "纪元年应该是1年")

## 测试重置功能
func test_reset():
    # 推进100天 * 24小时 = 2400小时
    for i in range(100 * 24):
        calendar.advance_time_tick()
    
    calendar.reset()
    assert_eq(calendar.current_gregorian_year, config_mock.time_epoch_start_year, "重置后年份应该恢复")
    
    var info = calendar.get_time_info()
    assert_eq(info["day_in_year"], 1, "重置后应该是第1天")
    assert_eq(info["hour_in_day"], 0, "重置后应该是第0小时")

## 测试纪元锚点设置
func test_era_anchor():
    # 简单推进几天测试锚定逻辑
    for i in range(100):
        calendar.advance_time_tick()
    
    # 设置锚点到当前时间之前的年份
    var current_year = calendar.current_gregorian_year
    var anchor_year = current_year - 10  # 10年前
    calendar.anchor_era("测试纪元", anchor_year)
    var info = calendar.get_time_info()
    
    assert_eq(info["current_era_name"], "测试纪元", "纪元名称应该正确")
    assert_eq(info["current_era_year"], 11, "纪元年应该是11年") # current_year - anchor_year + 1

## 测试纪元锚点验证
func test_era_anchor_validation():
    # 推进几天
    for i in range(100):
        calendar.advance_time_tick()
    
    # 测试锚定到未来年份应该失败（产生push_error）
    var current_year = calendar.current_gregorian_year
    var future_year = current_year + 10  # 未来年份
    
    # 尝试锚定到未来年份（应该失败并产生错误）
    calendar.anchor_era("未来纪元", future_year)
    
    # 验证锚定没有生效（应该保持原始状态）
    var info = calendar.get_time_info()
    assert_true(info["current_era_name"] == null or info["current_era_name"] == "uninitialized", "未来年份的锚定应该失败")

## 测试公历格式化
func test_format_gregorian():
    calendar.reset()
    var date_str = calendar.format_date_gregorian()
    var expected = "公元前%d年1月1日" % abs(config_mock.time_epoch_start_year)
    assert_eq(date_str, expected, "初始日期格式化应该正确")

## 测试纪年格式化
func test_format_with_era():
    # 推进5天 * 24小时 + 5小时 = 125小时
    for i in range(5 * 24 + 5):
        calendar.advance_time_tick()
    
    # 设置锚点为当前年份（这样就是纪元元年）
    var current_year = calendar.current_gregorian_year
    calendar.anchor_era("开元", current_year)
    
    var date_str = calendar.format_date_era(true)
    assert_eq(date_str, "开元1年1月6日5点", "纪年格式化应该正确")

## 测试不同起始年份
func test_different_start_year():
    var calendar_ad = Calendar.new(1)
    assert_eq(calendar_ad.current_gregorian_year, 1, "应该从公元1年开始")
    
    # 推进365天 * 24小时 = 8760小时
    for i in range(365 * 24):
        calendar_ad.advance_time_tick()
    
    # 我们的年份是360天，所以365天后是2年第6天
    assert_eq(calendar_ad.current_gregorian_year, 2, "推进365天后应该是第2年")
    var info = calendar_ad.get_time_info()
    assert_eq(info["day_in_year"], 6, "应该是第6天")
