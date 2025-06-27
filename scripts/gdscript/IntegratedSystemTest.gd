extends Control

## GDScript版本的集成系统测试
## 使用GDScript实现的Calendar、IndexedTimeWheel和CTBManager

# 预加载TestGameWorld类
const TestGameWorld = preload("res://tests/gdscript/TestGameWorld.gd")

# 统一测试协调器 - 替代手动组件管理
var test_world: TestGameWorld

# UI组件 - 左侧CTB行动条
var ctb_action_bar: VBoxContainer
var ctb_scroll_container: ScrollContainer
var ctb_title: Label
var ctb_events_list: VBoxContainer

# UI组件 - 右侧时间轮检查器
var time_wheel_inspector: VBoxContainer
var time_wheel_scroll_container: ScrollContainer
var time_wheel_title: Label
var wheel_events_list: VBoxContainer
var future_events_list: VBoxContainer

# UI组件 - 中央控制面板
var center_panel: VBoxContainer
var current_time_label: Label
var calendar_status_label: Label
var controls_container: VBoxContainer

# 测试数据
var character_names = ["张飞", "关羽", "刘备", "曹操", "孙权"]

func _ready():
	print("Initializing GDScript Integrated System Test")
	
	# 设置UI缩放和字体大小
	setup_ui_scaling()
	
	initialize_systems()
	setup_ui()
	update_all_displays()
	
	# 添加一些初始测试事件
	add_initial_test_events()

func setup_ui_scaling():
	# 设置全局字体大小而不是整体缩放（避免按钮被裁剪）
	print("UI scaling setup: using individual font sizes instead of global scaling")

func initialize_systems():
	# 使用配置中的默认缓冲区大小初始化统一测试协调器
	test_world = TestGameWorld.new()
	
	# 订阅事件以进行UI更新
	test_world.event_executed.connect(_on_event_executed)
	test_world.time_advanced.connect(_on_time_advanced)
	test_world.systems_updated.connect(_on_systems_updated)
	
	print("TestGameWorld initialized - Calendar: ", test_world.current_calendar_time)

func _on_event_executed(event_desc: String):
	add_ctb_log_entry("已执行: %s" % event_desc, true)

func _on_time_advanced(hours: int):
	add_ctb_log_entry("时间推进了 %d 小时" % hours, false)

func _on_systems_updated():
	call_deferred("update_all_displays")

func setup_ui():
	# 主布局：左栏 | 中央面板 | 右栏 - 填充整个窗口
	var main_container = HBoxContainer.new()
	main_container.anchor_left = 0
	main_container.anchor_top = 0
	main_container.anchor_right = 1
	main_container.anchor_bottom = 1
	main_container.offset_left = 0
	main_container.offset_top = 0
	main_container.offset_right = 0
	main_container.offset_bottom = 0
	main_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(main_container)
	
	# === 左侧CTB行动条 ===
	setup_ctb_action_bar(main_container)
	
	# === 中央控制面板 ===
	setup_center_panel(main_container)
	
	# === 右侧时间轮检查器 ===
	setup_time_wheel_inspector(main_container)

func setup_ctb_action_bar(parent: HBoxContainer):
	ctb_action_bar = VBoxContainer.new()
	ctb_action_bar.custom_minimum_size = Vector2(300, 0)
	ctb_action_bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ctb_action_bar.size_flags_vertical = Control.SIZE_EXPAND_FILL
	parent.add_child(ctb_action_bar)
	
	# 标题
	ctb_title = Label.new()
	ctb_title.text = "⚔️ CTB行动条"
	ctb_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ctb_title.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.2, 0.3, 0.5)))
	ctb_title.add_theme_color_override("font_color", Color.WHITE)
	ctb_title.add_theme_font_size_override("font_size", 18)
	ctb_title.custom_minimum_size = Vector2(0, 50)
	ctb_action_bar.add_child(ctb_title)
	
	# 可滚动事件列表
	ctb_scroll_container = ScrollContainer.new()
	ctb_scroll_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	ctb_scroll_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ctb_scroll_container.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	ctb_scroll_container.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	ctb_action_bar.add_child(ctb_scroll_container)
	
	ctb_events_list = VBoxContainer.new()
	ctb_events_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ctb_scroll_container.add_child(ctb_events_list)
	
	# 行动按钮
	var ctb_buttons_container = HBoxContainer.new()
	ctb_buttons_container.custom_minimum_size = Vector2(0, 50)
	ctb_buttons_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ctb_action_bar.add_child(ctb_buttons_container)
	
	var add_action_button = Button.new()
	add_action_button.text = "添加行动"
	add_action_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_action_button.add_theme_font_size_override("font_size", 14)
	add_action_button.pressed.connect(on_add_random_action)
	ctb_buttons_container.add_child(add_action_button)
	
	var execute_action_button = Button.new()
	execute_action_button.text = "执行行动"
	execute_action_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	execute_action_button.add_theme_font_size_override("font_size", 14)
	execute_action_button.pressed.connect(on_execute_next_action)
	ctb_buttons_container.add_child(execute_action_button)

func setup_center_panel(parent: HBoxContainer):
	center_panel = VBoxContainer.new()
	center_panel.custom_minimum_size = Vector2(450, 0)
	center_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	parent.add_child(center_panel)
	
	# 当前时间显示
	current_time_label = Label.new()
	current_time_label.text = "当前时间: 初始化中..."
	current_time_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	current_time_label.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.1, 0.5, 0.2)))
	current_time_label.add_theme_color_override("font_color", Color.WHITE)
	current_time_label.add_theme_font_size_override("font_size", 16)
	current_time_label.custom_minimum_size = Vector2(0, 80)
	center_panel.add_child(current_time_label)
	
	# 日历状态
	calendar_status_label = Label.new()
	calendar_status_label.text = "日历状态: 初始化中..."
	calendar_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	calendar_status_label.add_theme_font_size_override("font_size", 14)
	center_panel.add_child(calendar_status_label)
	
	# 控制
	controls_container = VBoxContainer.new()
	center_panel.add_child(controls_container)
	
	setup_time_controls()
	setup_calendar_controls()
	setup_test_controls()

func setup_time_controls():
	var time_group = create_control_group("⏰ 时间控制")
	controls_container.add_child(time_group)
	
	var button_row1 = HBoxContainer.new()
	time_group.add_child(button_row1)
	
	var advance_hour_button = Button.new()
	advance_hour_button.text = "推进1小时"
	advance_hour_button.pressed.connect(func(): advance_time(1))
	button_row1.add_child(advance_hour_button)
	
	var advance_day_button = Button.new()
	advance_day_button.text = "推进1天"
	advance_day_button.pressed.connect(func(): advance_time(24))
	button_row1.add_child(advance_day_button)
	
	var button_row2 = HBoxContainer.new()
	time_group.add_child(button_row2)
	
	var advance_week_button = Button.new()
	advance_week_button.text = "推进7天"
	advance_week_button.pressed.connect(func(): advance_time(168))
	button_row2.add_child(advance_week_button)
	
	var advance_month_button = Button.new()
	advance_month_button.text = "推进1月"
	advance_month_button.pressed.connect(func(): advance_time(720))  # 30 days * 24 hours
	button_row2.add_child(advance_month_button)

func setup_calendar_controls():
	var calendar_group = create_control_group("📅 日历控制")
	controls_container.add_child(calendar_group)
	
	# 纪元锚定
	var anchor_container = HBoxContainer.new()
	calendar_group.add_child(anchor_container)
	
	var era_name_input = LineEdit.new()
	era_name_input.placeholder_text = "纪元名 (如: 开元)"
	era_name_input.name = "EraNameInput"
	anchor_container.add_child(era_name_input)
	
	var anchor_year_input = LineEdit.new()
	anchor_year_input.placeholder_text = "元年 (如: 713)"
	anchor_year_input.name = "AnchorYearInput"
	anchor_container.add_child(anchor_year_input)
	
	var anchor_button = Button.new()
	anchor_button.text = "锚定"
	anchor_button.pressed.connect(on_anchor_era)
	anchor_container.add_child(anchor_button)
	
	# 改元
	var change_era_container = HBoxContainer.new()
	calendar_group.add_child(change_era_container)
	
	var new_era_input = LineEdit.new()
	new_era_input.placeholder_text = "新纪元名"
	new_era_input.name = "NewEraInput"
	change_era_container.add_child(new_era_input)
	
	var change_era_button = Button.new()
	change_era_button.text = "改元"
	change_era_button.pressed.connect(on_change_era)
	change_era_container.add_child(change_era_button)
	
	var reset_button = Button.new()
	reset_button.text = "重置日历"
	reset_button.pressed.connect(on_reset_calendar)
	change_era_container.add_child(reset_button)

func setup_test_controls():
	var test_group = create_control_group("🧪 测试场景")
	controls_container.add_child(test_group)
	
	var test_button_row1 = HBoxContainer.new()
	test_group.add_child(test_button_row1)
	
	var basic_test_button = Button.new()
	basic_test_button.text = "基础测试"
	basic_test_button.pressed.connect(on_basic_test)
	test_button_row1.add_child(basic_test_button)
	
	var combat_test_button = Button.new()
	combat_test_button.text = "战斗测试"
	combat_test_button.pressed.connect(on_combat_test)
	test_button_row1.add_child(combat_test_button)
	
	var test_button_row2 = HBoxContainer.new()
	test_group.add_child(test_button_row2)
	
	var long_term_test_button = Button.new()
	long_term_test_button.text = "长期事件"
	long_term_test_button.pressed.connect(on_long_term_test)
	test_button_row2.add_child(long_term_test_button)
	
	var clear_all_button = Button.new()
	clear_all_button.text = "清空所有"
	clear_all_button.pressed.connect(on_clear_all)
	test_button_row2.add_child(clear_all_button)

func setup_time_wheel_inspector(parent: HBoxContainer):
	time_wheel_inspector = VBoxContainer.new()
	time_wheel_inspector.custom_minimum_size = Vector2(350, 0)
	time_wheel_inspector.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	time_wheel_inspector.size_flags_vertical = Control.SIZE_EXPAND_FILL
	parent.add_child(time_wheel_inspector)
	
	# 标题
	time_wheel_title = Label.new()
	time_wheel_title.text = "⚙️ 时间轮检查器"
	time_wheel_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	time_wheel_title.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.5, 0.2, 0.3)))
	time_wheel_title.add_theme_color_override("font_color", Color.WHITE)
	time_wheel_title.add_theme_font_size_override("font_size", 18)
	time_wheel_title.custom_minimum_size = Vector2(0, 50)
	time_wheel_inspector.add_child(time_wheel_title)
	
	# 时间轮事件（当前缓冲区）
	var wheel_label = Label.new()
	wheel_label.text = "🎯 主时间轮事件:"
	wheel_label.add_theme_font_size_override("font_size", 14)
	time_wheel_inspector.add_child(wheel_label)
	
	var wheel_scroll_container = ScrollContainer.new()
	wheel_scroll_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	wheel_scroll_container.custom_minimum_size = Vector2(0, 200)
	time_wheel_inspector.add_child(wheel_scroll_container)
	
	wheel_events_list = VBoxContainer.new()
	wheel_scroll_container.add_child(wheel_events_list)
	
	# 远期事件
	var future_label = Label.new()
	future_label.text = "🔮 远期事件池:"
	future_label.add_theme_font_size_override("font_size", 14)
	time_wheel_inspector.add_child(future_label)
	
	var future_scroll_container = ScrollContainer.new()
	future_scroll_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	future_scroll_container.custom_minimum_size = Vector2(0, 200)
	time_wheel_inspector.add_child(future_scroll_container)
	
	future_events_list = VBoxContainer.new()
	future_scroll_container.add_child(future_events_list)

func create_control_group(title: String) -> VBoxContainer:
	var group = VBoxContainer.new()
	group.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.9, 0.9, 0.9)))
	
	var title_label = Label.new()
	title_label.text = title
	title_label.add_theme_color_override("font_color", Color(0.2, 0.2, 0.2))
	group.add_child(title_label)
	
	return group

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

func add_initial_test_events():
	# 使用TestGameWorld API添加一些角色行动
	test_world.schedule_event("张飞_攻击", "张飞发动攻击", 5)
	test_world.schedule_event("关羽_防御", "关羽进入防御状态", 8)
	test_world.schedule_event("刘备_治疗", "刘备使用治疗技能", 12)
	
	# 添加一些远期事件
	test_world.schedule_event("季节变化", "春季到来", 200)
	test_world.schedule_event("节日庆典", "中秋节庆典", 300)
	
	print("Initial test events added via TestGameWorld")

func advance_time(hours: int):
	# 使用TestGameWorld的统一时间推进 - 无需手动同步！
	var result = test_world.advance_time(hours)
	print("Advanced time: ", result.summary)

func on_add_random_action():
	var character = character_names[randi() % character_names.size()]
	var actions = ["攻击", "防御", "技能", "移动", "休息"]
	var action = actions[randi() % actions.size()]
	var delay = randi_range(1, 50)
	
	var event_key = "%s_%s_%d" % [character, action, Time.get_ticks_msec()]
	var event_value = "%s执行%s" % [character, action]
	
	test_world.schedule_event(event_key, event_value, delay)
	add_ctb_log_entry("已安排: %s (延迟%d小时)" % [event_value, delay], false)

func on_execute_next_action():
	# 使用TestGameWorld的推进到下一事件功能
	var result = test_world.advance_to_next_event(10)
	
	if result.events_executed.size() > 0:
		add_ctb_log_entry("执行了 %d 个事件" % result.events_executed.size(), false)
	elif result.hours_advanced > 0:
		add_ctb_log_entry("推进了 %d 小时寻找事件" % result.hours_advanced, false)
	else:
		add_ctb_log_entry("没有找到任何事件", false)

func on_anchor_era():
	var era_name_input = find_child("EraNameInput", true) as LineEdit
	var anchor_year_input = find_child("AnchorYearInput", true) as LineEdit
	
	if era_name_input and anchor_year_input and era_name_input.text.strip_edges() != "" and anchor_year_input.text.is_valid_int():
		var era_name = era_name_input.text.strip_edges()
		var year = anchor_year_input.text.to_int()
		test_world.anchor_era(era_name, year)
		add_ctb_log_entry("锚定纪元: %s元年 = 公元%d年" % [era_name, year], false)
		era_name_input.text = ""
		anchor_year_input.text = ""

func on_change_era():
	var new_era_input = find_child("NewEraInput", true) as LineEdit
	
	if new_era_input and new_era_input.text.strip_edges() != "":
		var era_name = new_era_input.text.strip_edges()
		test_world.start_new_era(era_name)
		add_ctb_log_entry("改元: %s元年 = 当前年份" % era_name, false)
		new_era_input.text = ""

func on_reset_calendar():
	test_world.reset()
	add_ctb_log_entry("游戏世界已重置", false)

func on_basic_test():
	add_ctb_log_entry("开始基础测试...", false)
	
	# 使用TestGameWorld API添加基础事件
	test_world.schedule_event("基础测试1", "基础事件1", 2)
	test_world.schedule_event("基础测试2", "基础事件2", 5)
	test_world.schedule_event("基础测试3", "基础事件3", 2)
	
	add_ctb_log_entry("基础测试事件已安排", false)

func on_combat_test():
	add_ctb_log_entry("开始战斗测试...", false)
	
	# 模拟战斗场景
	for i in range(3):
		var character = character_names[i]
		var delay = randi_range(1, 20)
		test_world.schedule_event("%s_combat" % character, "%s战斗行动" % character, delay)
	
	add_ctb_log_entry("战斗测试场景已创建", false)

func on_long_term_test():
	add_ctb_log_entry("开始长期事件测试...", false)
	
	# 添加超出缓冲区的远期事件
	test_world.schedule_event("春节", "春节庆典", 250)
	test_world.schedule_event("收获节", "秋收庆典", 400)
	test_world.schedule_event("年终", "年终总结", 500)
	
	add_ctb_log_entry("长期事件已安排到远期池", false)

func on_clear_all():
	# 使用TestGameWorld的清空功能
	test_world.clear_all_events()
	add_ctb_log_entry("所有事件已清空", false)

func update_ctb_queue():
	# 清空现有显示
	for child in ctb_events_list.get_children():
		child.queue_free()
	
	# 获取即将到来的事件（作为队列显示）
	var upcoming_events = test_world.get_upcoming_events(20, 15)
	
	if upcoming_events.size() == 0:
		var no_events_label = Label.new()
		no_events_label.text = "暂无待执行行动"
		no_events_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		no_events_label.add_theme_font_size_override("font_size", 14)
		no_events_label.modulate = Color(0.7, 0.7, 0.7)
		ctb_events_list.add_child(no_events_label)
		return
	
	# 按时间排序显示队列
	for i in range(upcoming_events.size()):
		var event_tuple = upcoming_events[i]
		var key = event_tuple[0]
		var value = event_tuple[1]
		
		var event_container = HBoxContainer.new()
		event_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		event_container.custom_minimum_size = Vector2(0, 40)
		
		# 队列位置显示
		var position_label = Label.new()
		position_label.text = "%02d" % (i + 1)
		position_label.custom_minimum_size = Vector2(30, 0)
		position_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		position_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		position_label.add_theme_font_size_override("font_size", 12)
		position_label.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.4, 0.4, 0.4, 0.8)))
		position_label.add_theme_color_override("font_color", Color.WHITE)
		event_container.add_child(position_label)
		
		# 事件内容
		var event_label = Label.new()
		event_label.text = str(value)
		event_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		event_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		event_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		event_label.add_theme_font_size_override("font_size", 14)
		
		# 根据队列位置设置颜色（即将执行的更亮）
		var intensity = 1.0 - (i * 0.1)
		if intensity < 0.4:
			intensity = 0.4
		
		if i == 0:
			# 下一个要执行的 - 高亮显示
			event_label.add_theme_stylebox_override("normal", create_colored_style_box(Color(1.0, 0.7, 0, 0.6)))
			event_label.add_theme_color_override("font_color", Color.BLACK)
		else:
			# 排队等待的事件
			event_label.add_theme_stylebox_override("normal", create_colored_style_box(Color(0.3, 0.5, 0.8, intensity * 0.4)))
			event_label.add_theme_color_override("font_color", Color(1, 1, 1, intensity))
		
		event_container.add_child(event_label)
		ctb_events_list.add_child(event_container)

func add_ctb_log_entry(message: String, is_executed: bool):
	# 这个方法现在只用于添加日志条目到队列显示的底部
	var log_label = Label.new()
	log_label.text = "📝 %s" % message
	log_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	log_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	log_label.custom_minimum_size = Vector2(0, 25)
	log_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	log_label.add_theme_font_size_override("font_size", 12)
	
	if is_executed:
		log_label.modulate = Color(0, 0.8, 0)  # Green for executed
	else:
		log_label.modulate = Color(0.8, 0.8, 0.8)  # Gray for info
	
	ctb_events_list.add_child(log_label)
	
	# 限制日志条目数量
	var log_entries = 0
	for child in ctb_events_list.get_children():
		if child is Label and child.text.begins_with("📝"):
			log_entries += 1
	
	if log_entries > 5:
		# 删除最老的日志条目
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
	# 清空现有列表
	for child in wheel_events_list.get_children():
		child.queue_free()
	for child in future_events_list.get_children():
		child.queue_free()
	
	# 显示时间轮统计信息
	var stats_label = Label.new()
	stats_label.text = "总事件: %d | 有事件: %s | 当前槽空: %s" % [
		test_world.event_count, 
		"是" if test_world.has_any_events else "否",
		"是" if test_world.is_current_slot_empty else "否"
	]
	wheel_events_list.add_child(stats_label)
	
	# 显示时间轮中即将到来的事件
	var upcoming_events = test_world.get_upcoming_events(50, 30)
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
	
	# 显示远期事件状态
	var future_info_label = Label.new()
	future_info_label.text = "系统状态: %s" % test_world.get_status_summary()
	future_events_list.add_child(future_info_label)