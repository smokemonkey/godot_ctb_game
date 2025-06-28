extends Control

@onready var run_all_button = $VBoxContainer/ButtonContainer/RunAllButton
@onready var run_csharp_button = $VBoxContainer/ButtonContainer/RunCSharpButton
@onready var run_gdscript_button = $VBoxContainer/ButtonContainer/RunGDScriptButton
@onready var clear_button = $VBoxContainer/ButtonContainer/ClearButton
@onready var progress_bar = $VBoxContainer/ProgressBar
@onready var status_label = $VBoxContainer/StatusLabel
@onready var results_text = $VBoxContainer/ScrollContainer/ResultsText

var gut
var total_tests = 0
var completed_tests = 0

func _ready():
    # 创建GUT实例
    gut = load("res://addons/gut/gut.gd").new()
    add_child(gut)

    # 配置GUT
    gut.add_directory("res://tests/gdscript/", "test_", ".gd")
    gut.include_subdirectories = true
    gut.log_level = gut.LOG_LEVEL_ALL_ASSERTS
    print("GUT配置：查找路径 res://tests/gdscript/ 下的 test_*.gd 文件")

    # 连接GUT的信号
    gut.start_run.connect(_on_start_run)
    gut.end_run.connect(_on_end_run)
    gut.start_script.connect(_on_start_script)
    gut.end_script.connect(_on_end_script)
    gut.start_test.connect(_on_start_test)
    gut.end_test.connect(_on_end_test)

    # 连接按钮信号
    run_all_button.connect("pressed", _on_run_all_pressed)
    run_csharp_button.connect("pressed", _on_run_csharp_pressed)
    run_gdscript_button.connect("pressed", _on_run_gdscript_pressed)
    clear_button.connect("pressed", _on_clear_pressed)

    _update_status("测试运行器已准备就绪")

func _on_run_all_pressed():
    if gut:
        clear_results()
        _update_status("运行所有测试...")
        progress_bar.value = 0
        gut.test_scripts(['test_calendar_csharp.gd', 'test_ctb_manager_csharp.gd', 'test_indexed_time_wheel_csharp.gd'])

func _on_run_csharp_pressed():
    if gut:
        clear_results()
        _update_status("运行C#测试...")
        progress_bar.value = 0
        gut.test_scripts(['test_calendar_csharp.gd', 'test_ctb_manager_csharp.gd', 'test_indexed_time_wheel_csharp.gd'])

func _on_run_gdscript_pressed():
    if gut:
        clear_results()
        _update_status("运行GDScript测试...")
        progress_bar.value = 0
        gut.run_tests()

func _on_clear_pressed():
    clear_results()
    _update_status("结果已清空")

func clear_results():
    results_text.text = ""
    progress_bar.value = 0
    completed_tests = 0
    total_tests = 0

func _update_status(message: String):
    status_label.text = message
    print("Status: " + message)

func _append_result(message: String, color: String = "white"):
    var formatted_message = "[color=" + color + "]" + message + "[/color]\n"
    results_text.text += formatted_message

    # 滚动到底部
    await get_tree().process_frame
    var scroll_container = $VBoxContainer/ScrollContainer
    scroll_container.ensure_control_visible(results_text)

func _on_start_run():
    _append_result("=== 开始运行测试 ===", "yellow")
    total_tests = 0
    completed_tests = 0

func _on_end_run():
    var passed = gut.get_pass_count()
    var failed = gut.get_fail_count()

    _append_result("\n=== 测试完成 ===", "white")
    _append_result("通过: " + str(passed), "green")
    _append_result("失败: " + str(failed), "red")

    if failed == 0:
        _update_status("🎉 所有测试通过!")
        _append_result("🎉 所有测试通过!", "green")
    else:
        _update_status("❌ 有 " + str(failed) + " 个测试失败")
        _append_result("❌ 有测试失败，请检查", "red")

    progress_bar.value = 100

func _on_start_script(test_script_obj):
    _append_result("运行测试脚本: " + str(test_script_obj), "yellow")

func _on_end_script():
    _append_result("测试脚本完成", "white")

func _on_start_test(test_name: String):
    _append_result("开始测试: " + test_name, "yellow")
    total_tests += 1

func _on_end_test():
    completed_tests += 1
    _update_progress()

    # 检查最后一个测试的结果
    var last_result = gut.get_current_test_object()
    if last_result and last_result.is_failing():
        _append_result("✗ 失败: " + str(last_result), "red")
    else:
        _append_result("✓ 通过", "green")

func _update_progress():
    if total_tests > 0:
        var percentage = (float(completed_tests) / float(total_tests)) * 100
        progress_bar.value = percentage
        _update_status("进度: " + str(completed_tests) + "/" + str(total_tests) + " (" + str(int(percentage)) + "%)")
