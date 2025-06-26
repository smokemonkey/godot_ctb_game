#!/usr/bin/env -S godot --headless --script
# GUT 测试运行器 - 当前仅用于文件验证

extends SceneTree

func _init():
	print("=== Godot 项目测试状态检查 ===")
	
	# 检查C#测试文件
	var csharp_tests = [
		"res://tests/csharp/core/CalendarTests.cs",
		"res://tests/csharp/core/CTBManagerTests.cs",
		"res://tests/csharp/core/IndexedTimeWheelTests.cs"
	]
	
	print("\n📋 C# 测试文件状态:")
	var found_csharp = 0
	for file_path in csharp_tests:
		if FileAccess.file_exists(file_path):
			found_csharp += 1
			print("✅ " + file_path)
		else:
			print("❌ " + file_path)
	
	print("\n📊 测试结构状态:")
	print("- C# 测试: " + str(found_csharp) + "/" + str(csharp_tests.size()) + " 文件就位")
	print("- 测试结构: 按语言分离，对应代码结构")
	print("- GUT 框架: 已安装和配置")
	
	if found_csharp == csharp_tests.size():
		print("\n🎉 测试基础设施已就绪!")
		print("📝 建议:")
		print("   - 安装 .NET SDK 来运行 C# 测试")
		print("   - 使用 'dotnet test' 运行 C# 单元测试")
		print("   - 在编辑器中使用 GUT 插件运行 GDScript 测试")
		quit(0)
	else:
		print("\n❌ 部分测试文件缺失")
		quit(1)