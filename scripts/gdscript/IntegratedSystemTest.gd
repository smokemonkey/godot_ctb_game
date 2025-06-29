extends Control

## 静态UI版本的集成系统测试
## 使用预定义的场景节点而不是动态创建

# 预加载TestGameWorld类
const TestGameWorld = preload("res://tests/gdscript/TestGameWorld.gd")

# 统一测试协调器
var test_world

# UI组件引用 - 使用@onready连接到静态节点
@onready var ctb_title: Label = $MainContainer/LeftPanel/CTBTitle
@onready var ctb_scroll_container: ScrollContainer = $MainContainer/LeftPanel/CTBScrollContainer
@onready var ctb_events_list: VBoxContainer = $MainContainer/LeftPanel/CTBScrollContainer/CTBEventsList

@onready var current_time_label: Label = $MainContainer/CenterPanel/CurrentTimeLabel
@onready var calendar_status_label: Label = $MainContainer/CenterPanel/CalendarStatusLabel

@onready var time_wheel_title: Label = $MainContainer/RightPanel/TimeWheelTitle
@onready var wheel_events_list: VBoxContainer = $MainContainer/RightPanel/WheelScrollContainer/WheelEventsList
@onready var future_events_list: VBoxContainer = $MainContainer/RightPanel/FutureScrollContainer/FutureEventsList

# 按钮引用
@onready var add_action_button: Button = $MainContainer/LeftPanel/ButtonsContainer/AddActionButton
@onready var execute_current_button: Button = $MainContainer/LeftPanel/ButtonsContainer/ExecuteCurrentButton
@onready var advance_to_next_button: Button = $MainContainer/LeftPanel/ButtonsContainer/AdvanceToNextButton

@onready var advance_hour_button: Button = $MainContainer/CenterPanel/ControlsContainer/TimeGroup/TimeButtonRow1/AdvanceHourButton
@onready var advance_day_button: Button = $MainContainer/CenterPanel/ControlsContainer/TimeGroup/TimeButtonRow1/AdvanceDayButton
@onready var advance_week_button: Button = $MainContainer/CenterPanel/ControlsContainer/TimeGroup/TimeButtonRow2/AdvanceWeekButton
@onready var advance_month_button: Button = $MainContainer/CenterPanel/ControlsContainer/TimeGroup/TimeButtonRow2/AdvanceMonthButton

@onready var era_name_input: LineEdit = $MainContainer/CenterPanel/ControlsContainer/CalendarGroup/AnchorContainer/EraNameInput
@onready var anchor_year_input: LineEdit = $MainContainer/CenterPanel/ControlsContainer/CalendarGroup/AnchorContainer/AnchorYearInput
@onready var anchor_button: Button = $MainContainer/CenterPanel/ControlsContainer/CalendarGroup/AnchorContainer/AnchorButton
@onready var new_era_input: LineEdit = $MainContainer/CenterPanel/ControlsContainer/CalendarGroup/ChangeEraContainer/NewEraInput
@onready var change_era_button: Button = $MainContainer/CenterPanel/ControlsContainer/CalendarGroup/ChangeEraContainer/ChangeEraButton
@onready var reset_button: Button = $MainContainer/CenterPanel/ControlsContainer/CalendarGroup/ChangeEraContainer/ResetButton

@onready var basic_test_button: Button = $MainContainer/CenterPanel/ControlsContainer/TestGroup/TestButtonRow1/BasicTestButton
@onready var combat_test_button: Button = $MainContainer/CenterPanel/ControlsContainer/TestGroup/TestButtonRow1/CombatTestButton
@onready var long_term_test_button: Button = $MainContainer/CenterPanel/ControlsContainer/TestGroup/TestButtonRow2/LongTermTestButton
@onready var clear_all_button: Button = $MainContainer/CenterPanel/ControlsContainer/TestGroup/TestButtonRow2/ClearAllButton

# 测试数据
var character_names = ["张飞", "关羽", "刘备", "曹操", "孙权"]

func _ready():
    print("Initializing GDScript Integrated System Test (Static UI)")

    # 设置UI样式
    setup_ui_styling()

    # 初始化系统
    initialize_systems()

    # 连接按钮信号
    connect_signals()

    # 更新显示
    update_all_displays()

    # 添加初始测试事件（注释掉自动添加，改为手动添加）
    add_initial_test_events()

func setup_ui_styling():
    # 设置标题样式
    ctb_title.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.2, 0.3, 0.5)))
    ctb_title.add_theme_color_override("font_color", Color.WHITE)
    ctb_title.add_theme_font_size_override("font_size", 18)

    current_time_label.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.1, 0.5, 0.2)))
    current_time_label.add_theme_color_override("font_color", Color.WHITE)
    current_time_label.add_theme_font_size_override("font_size", 16)

    time_wheel_title.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.5, 0.2, 0.3)))
    time_wheel_title.add_theme_color_override("font_color", Color.WHITE)
    time_wheel_title.add_theme_font_size_override("font_size", 18)

func initialize_systems():
    # 初始化测试世界
    test_world = TestGameWorld.new()

    # 订阅事件
    test_world.event_executed.connect(_on_event_executed)
    test_world.time_advanced.connect(_on_time_advanced)
    test_world.systems_updated.connect(_on_systems_updated)

    print("TestGameWorld initialized - Calendar: ", test_world.current_calendar_time)

func connect_signals():
    # CTB按钮
    add_action_button.pressed.connect(on_add_random_action)
    execute_current_button.pressed.connect(on_execute_current_action)
    advance_to_next_button.pressed.connect(on_advance_to_next_action)

    # 时间控制按钮
    advance_hour_button.pressed.connect(func(): advance_time(1))
    advance_day_button.pressed.connect(func(): advance_time(24))
    advance_week_button.pressed.connect(func(): advance_time(168))
    advance_month_button.pressed.connect(func(): advance_time(720))

    # 日历控制按钮
    anchor_button.pressed.connect(on_anchor_era)
    change_era_button.pressed.connect(on_change_era)
    reset_button.pressed.connect(on_reset_calendar)

    # 测试按钮
    basic_test_button.pressed.connect(on_basic_test)
    combat_test_button.pressed.connect(on_combat_test)
    long_term_test_button.pressed.connect(on_long_term_test)
    clear_all_button.pressed.connect(on_clear_all)

func _on_event_executed(event_desc: String):
    add_ctb_log_entry("已执行: %s" % event_desc, true)

func _on_time_advanced(hours: int):
    add_ctb_log_entry("时间推进了 %d 小时" % hours, false)

func _on_systems_updated():
    call_deferred("update_all_displays")

func create_colored_style_box(color: Color) -> StyleBoxFlat:
    var style_box = StyleBoxFlat.new()
    style_box.bg_color = color
    style_box.border_width_top = 1
    style_box.border_width_bottom = 1
    style_box.border_width_left = 1
    style_box.border_width_right = 1
    style_box.border_color = color.darkened(0.3)
    style_box.corner_radius_top_left = 3
    style_box.corner_radius_top_right = 3
    style_box.corner_radius_bottom_left = 3
    style_box.corner_radius_bottom_right = 3
    style_box.content_margin_top = 8
    style_box.content_margin_bottom = 8
    style_box.content_margin_left = 12
    style_box.content_margin_right = 12
    return style_box

# 所有其他方法与原版相同，只是不需要创建UI
func add_initial_test_events():
    # for character_name in character_names:
    #     var actor = test_world.add_example_event(character_name, character_name, "测试阵营")
    #     # 禁用自动重调度，避免执行后自动重新出现
    #     actor.reschedule_enabled = false
    test_world.initialize_ctb()
    test_world.schedule_event("季节变化", "春季到来", 200)
    test_world.schedule_event("节日庆典", "中秋节庆典", 300)
    print("Initial test actors and events added via TestGameWorld")

func advance_time(hours: int):
    var result = test_world.advance_time(hours)
    print("Advanced time: ", result.summary)
    if result.stopped_for_event:
        add_ctb_log_entry("⚠️ %s" % result.summary, false)
    else:
        add_ctb_log_entry("⏰ %s" % result.summary, false)
    update_all_displays()  # 更新显示

func on_add_random_action():
    var character = character_names[randi() % character_names.size()]
    var actions = ["攻击", "防御", "技能", "移动", "休息"]
    var action = actions[randi() % actions.size()]
    var delay = randi_range(1, 50)

    var event_key = "%s_%s_%d" % [character, action, Time.get_ticks_msec()]
    var event_value = "%s执行%s" % [character, action]

    test_world.schedule_event(event_key, event_value, delay)
    add_ctb_log_entry("已安排: %s (延迟%d小时)" % [event_value, delay], false)
    update_all_displays()  # 更新显示

func on_execute_current_action():
    # 执行当前到期事件，不推进时间（一次只执行一个事件）
    var result = test_world.execute_due_event()
    if result.found_event:
        add_ctb_log_entry("已执行: %s" % result.event_executed, true)
        update_all_displays()  # 更新显示
    else:
        add_ctb_log_entry("当前没有到期事件", false)

func on_advance_to_next_action():
    # 推进到下一个事件但不执行
    var result = test_world.advance_to_next_event(10000)
    if result.hours_advanced > 0:
        add_ctb_log_entry("推进了 %d 小时到达下一个事件" % result.hours_advanced, false)
        update_all_displays()  # 更新显示
    elif result.found_event:
        add_ctb_log_entry("当前就有到期事件", false)
    else:
        add_ctb_log_entry("在 %d 小时内没有找到任何事件" % 10000, false)

func on_anchor_era():
    if era_name_input.text.strip_edges() != "" and anchor_year_input.text.is_valid_int():
        var era_name = era_name_input.text.strip_edges()
        var year = anchor_year_input.text.to_int()
        test_world.anchor_era(era_name, year)
        add_ctb_log_entry("锚定纪元: %s元年 = 公元%d年" % [era_name, year], false)
        era_name_input.text = ""
        anchor_year_input.text = ""
        update_all_displays()  # 更新显示

func on_change_era():
    if new_era_input.text.strip_edges() != "":
        var era_name = new_era_input.text.strip_edges()
        test_world.start_new_era(era_name)
        add_ctb_log_entry("改元: %s元年 = 当前年份" % era_name, false)
        new_era_input.text = ""
        update_all_displays()  # 更新显示

func on_reset_calendar():
    test_world.reset()
    add_ctb_log_entry("游戏世界已重置", false)
    update_all_displays()  # 更新显示

func on_basic_test():
    add_ctb_log_entry("开始基础测试...", false)
    test_world.schedule_event("基础测试1", "基础事件1", 2)
    test_world.schedule_event("基础测试2", "基础事件2", 5)
    test_world.schedule_event("基础测试3", "基础事件3", 2)
    add_ctb_log_entry("基础测试事件已安排", false)
    update_all_displays()  # 更新显示

func on_combat_test():
    add_ctb_log_entry("开始战斗测试...", false)
    for i in range(3):
        var character = character_names[i]
        var delay = randi_range(1, 20)
        test_world.schedule_event("%s_combat" % character, "%s战斗行动" % character, delay)
    add_ctb_log_entry("战斗测试场景已创建", false)
    update_all_displays()  # 更新显示

func on_long_term_test():
    add_ctb_log_entry("开始长期事件测试...", false)
    test_world.schedule_event("春节", "春节庆典", 250)
    test_world.schedule_event("收获节", "秋收庆典", 400)
    test_world.schedule_event("年终", "年终总结", 500)
    add_ctb_log_entry("长期事件已安排到远期池", false)
    update_all_displays()  # 更新显示

func on_clear_all():
    test_world.clear_all_events()
    add_ctb_log_entry("所有事件已清空", false)
    update_all_displays()  # 更新显示

func update_ctb_queue():
    for child in ctb_events_list.get_children():
        ctb_events_list.remove_child(child)
        child.queue_free()

    var upcoming_events = test_world.get_upcoming_events(15, 180*24)
    if upcoming_events.size() == 0:
        var no_events_label = Label.new()
        no_events_label.text = "暂无待执行行动"
        no_events_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        no_events_label.add_theme_font_size_override("font_size", 14)
        no_events_label.modulate = Color(0.7, 0.7, 0.7)
        ctb_events_list.add_child(no_events_label)
        return

    for i in range(upcoming_events.size()):
        var event_tuple = upcoming_events[i]
        var key = event_tuple[0]
        var value = event_tuple[1]

        var event_container = HBoxContainer.new()
        var position_label = Label.new()
        position_label.text = "%02d" % (i + 1)
        position_label.custom_minimum_size = Vector2(30, 0)

        var event_label = Label.new()
        event_label.text = str(value)
        event_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL

        if i == 0:
            event_label.add_theme_stylebox_override("normal", create_colored_style_box(Color(1.0, 0.7, 0, 0.6)))
            event_label.add_theme_color_override("font_color", Color.BLACK)
        else:
            var intensity = 1.0 - (i * 0.1)
            if intensity < 0.4: intensity = 0.4
            event_label.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.3, 0.5, 0.8, intensity * 0.4)))
            event_label.add_theme_color_override("font_color", Color(1, 1, 1, intensity))

        event_container.add_child(position_label)
        event_container.add_child(event_label)
        ctb_events_list.add_child(event_container)

func add_ctb_log_entry(message: String, is_executed: bool):
    var log_label = Label.new()
    log_label.text = "📝 %s" % message
    log_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    log_label.add_theme_font_size_override("font_size", 12)

    if is_executed:
        log_label.modulate = Color(0, 0.8, 0)
    else:
        log_label.modulate = Color(0.8, 0.8, 0.8)

    ctb_events_list.add_child(log_label)

    # 限制日志条目数量
    var log_entries = 0
    for child in ctb_events_list.get_children():
        if child is Label and child.text.begins_with("📝"):
            log_entries += 1

    if log_entries > 5:
        for child in ctb_events_list.get_children():
            if child is Label and child.text.begins_with("📝"):
                child.queue_free()
                break

    call_deferred("scroll_ctb_to_bottom")

func scroll_ctb_to_bottom():
    ctb_scroll_container.scroll_vertical = int(ctb_scroll_container.get_v_scroll_bar().max_value)

func update_all_displays():
    update_time_display()
    update_calendar_status()
    update_time_wheel_inspector()
    update_ctb_queue()

func update_time_display():
    var gregorian_time = test_world.current_calendar_time
    var era_time = test_world.current_era_time
    var current_time = test_world.current_time
    current_time_label.text = "📅 %s\n🌍 %s\n⏰ 总计: %d小时" % [era_time, gregorian_time, current_time]

func update_calendar_status():
    var time_info = test_world.get_calendar_info()
    var status_text = "公历年份: %s\n" % time_info["gregorian_year"]
    status_text += "月份: %s, 日期: %s\n" % [time_info["month"], time_info["day_in_month"]]
    status_text += "年内第 %s 天\n" % time_info["day_in_year"]
    status_text += "当前纪年: %s\n" % (time_info["current_era_name"] if time_info["current_era_name"] else "无")

    if time_info.has("current_anchor") and time_info["current_anchor"] != null:
        var anchor = time_info["current_anchor"]
        if anchor.size() >= 2:
            status_text += "锚定: %s元年 = 公元%s年" % [anchor[0], anchor[1]]

    calendar_status_label.text = status_text

func update_time_wheel_inspector():
    for child in wheel_events_list.get_children():
        wheel_events_list.remove_child(child)
        child.queue_free()
    for child in future_events_list.get_children():
        future_events_list.remove_child(child)
        child.queue_free()

    var stats_label = Label.new()
    stats_label.text = "总事件: %d | 有事件: %s | 当前槽空: %s" % [
        test_world.event_count,
        "是" if test_world.has_any_events else "否",
        "是" if test_world.is_current_slot_empty else "否"
    ]
    wheel_events_list.add_child(stats_label)

    var upcoming_events = test_world.get_upcoming_events(30, 50)
    if upcoming_events.size() > 0:
        for event_tuple in upcoming_events:
            var key = event_tuple[0]
            var value = event_tuple[1]
            var event_label = Label.new()
            event_label.text = "🎯 %s: %s" % [key, value]
            event_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
            wheel_events_list.add_child(event_label)
    else:
        var no_events_label = Label.new()
        no_events_label.text = "暂无即将到来的事件"
        wheel_events_list.add_child(no_events_label)

    var future_info_label = Label.new()
    future_info_label.text = "系统状态: %s" % test_world.get_status_summary()
    future_events_list.add_child(future_info_label)
