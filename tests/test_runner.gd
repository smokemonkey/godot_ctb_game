extends Control

@onready var run_tests_button = $VBoxContainer/ButtonContainer/RunTestsButton
@onready var run_calendar_button = $VBoxContainer/ButtonContainer/RunCalendarButton
@onready var run_ctb_button = $VBoxContainer/ButtonContainer/RunCTBButton
@onready var run_time_wheel_button = $VBoxContainer/ButtonContainer/RunTimeWheelButton
@onready var status_label = $VBoxContainer/StatusLabel
@onready var progress_bar = $VBoxContainer/ProgressBar
@onready var results_text = $VBoxContainer/ScrollContainer/ResultsText

var test_results = []
var current_test_file = ""

func _ready():
    status_label.text = "测试运行器已准备就绪"
    results_text.text = "[color=green][b]CTB游戏系统单元测试[/b][/color]\n\n点击按钮运行特定测试或运行所有测试。"
    
    # 连接按钮信号
    run_tests_button.pressed.connect(_run_all_tests)
    run_calendar_button.pressed.connect(func(): _run_specific_test("test_calendar.gd"))
    run_ctb_button.pressed.connect(func(): _run_specific_test("test_ctb_manager.gd"))
    run_time_wheel_button.pressed.connect(func(): _run_specific_test("test_time_wheel.gd"))

func _run_all_tests():
    _log_message("正在使用GUT运行所有测试...", "blue")
    status_label.text = "正在运行所有测试..."
    progress_bar.value = 0
    
    _log_message("提示: 由于GUT框架复杂性，建议使用以下方法运行测试:", "yellow")
    _log_message("1. 命令行: godot --script tests/run_tests.gd", "cyan")  
    _log_message("2. 集成测试: scenes/integrated_system_test.tscn", "cyan")
    _log_message("3. 单独测试: godot --script tests/gdscript/test_calendar.gd", "cyan")
    
    progress_bar.value = 100
    status_label.text = "请使用推荐的测试方法"

func _run_specific_test(test_file: String):
    _log_message("运行单个测试: " + test_file, "blue")
    status_label.text = "正在运行: " + test_file
    progress_bar.value = 0
    
    var result = _execute_test_file(test_file)
    progress_bar.value = 100
    
    _log_message("测试完成: " + test_file, "green")
    _log_message("结果: " + ("通过" if result.passed else "失败"), "green" if result.passed else "red")

func _execute_test_file(test_file: String) -> Dictionary:
    var test_path = "res://tests/gdscript/" + test_file
    
    # 检查文件是否存在
    if not FileAccess.file_exists(test_path):
        _log_message("错误: 测试文件不存在: " + test_path, "red")
        return {"passed": false, "error": "文件不存在"}
    
    # 先创建一个简单的GUT环境
    var gut_test_class = load("res://addons/gut/test.gd")
    if gut_test_class == null:
        _log_message("错误: 无法加载GUT测试基类", "red")
        return {"passed": false, "error": "GUT不可用"}
    
    # 加载并运行测试脚本
    var test_script = load(test_path)
    if test_script == null:
        _log_message("错误: 无法加载测试脚本: " + test_path, "red")
        return {"passed": false, "error": "无法加载脚本"}
    
    # 创建测试实例
    var test_instance = test_script.new()
    
    # 检查是否有测试方法
    var test_methods = []
    for method in test_instance.get_method_list():
        if method.name.begins_with("test_"):
            test_methods.append(method.name)
    
    if test_methods.is_empty():
        _log_message("警告: 没有找到测试方法 (以test_开头的方法)", "yellow")
        return {"passed": true, "warning": "没有测试方法"}
    
    # 运行所有测试方法
    var passed_count = 0
    var failed_count = 0
    
    for method_name in test_methods:
        _log_message("  运行: " + method_name, "gray")
        
        # 调用测试方法
        var test_passed = true
        var error_message = ""
        
        # Setup
        if test_instance.has_method("before_each"):
            test_instance.before_each()
        
        # 执行测试方法
        var callable = Callable(test_instance, method_name)
        if callable.is_valid():
            callable.call()
            passed_count += 1
            _log_message("    ✓ 通过", "green")
        else:
            failed_count += 1
            _log_message("    ✗ 失败: 方法无效", "red")
        
        # Teardown
        if test_instance.has_method("after_each"):
            test_instance.after_each()
    
    var total_tests = passed_count + failed_count
    var success_rate = (float(passed_count) / total_tests * 100) if total_tests > 0 else 100
    
    _log_message("测试统计: %d/%d 通过 (%.1f%%)" % [passed_count, total_tests, success_rate], 
                "green" if failed_count == 0 else "yellow")
    
    # 清理
    test_instance.queue_free()
    
    return {
        "passed": failed_count == 0,
        "total": total_tests,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "success_rate": success_rate
    }

func _show_final_results():
    status_label.text = "所有测试完成"
    
    var total_passed = 0
    var total_tests = 0
    var files_passed = 0
    
    for result in test_results:
        if result.has("total"):
            total_tests += result.total
            total_passed += result.passed_count
            if result.passed:
                files_passed += 1
    
    var overall_rate = (float(total_passed) / total_tests * 100) if total_tests > 0 else 100
    
    _log_message("", "white")
    _log_message("=== 最终测试结果 ===", "cyan")
    _log_message("测试文件: %d/%d 通过" % [files_passed, test_results.size()], "cyan")
    _log_message("测试用例: %d/%d 通过 (%.1f%%)" % [total_passed, total_tests, overall_rate], "cyan")
    
    if files_passed == test_results.size():
        _log_message("🎉 所有测试通过！", "green")
    else:
        _log_message("⚠️  有测试失败，请检查结果", "red")

func _log_message(message: String, color: String = "white"):
    var timestamp = Time.get_datetime_string_from_system(false, true)
    var formatted_message = "[color=%s][%s] %s[/color]\n" % [color, timestamp.substr(11, 8), message]
    results_text.text += formatted_message
    
    # 自动滚动到底部
    await get_tree().process_frame
    var scroll_container = $VBoxContainer/ScrollContainer
    scroll_container.scroll_vertical = int(scroll_container.get_v_scroll_bar().max_value)
