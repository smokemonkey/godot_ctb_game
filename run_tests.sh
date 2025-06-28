#!/bin/bash

# 简化的测试运行脚本
# 使用GUT命令行直接运行测试

GODOT_PATH="/mnt/d/Godot/Godot_v4.4.1-stable_mono_win64.exe"

echo "正在导入资源并缓存类..."
"$GODOT_PATH" --path . --import

echo "运行所有测试..."
"$GODOT_PATH" --path . --script addons/gut/gut_cmdln.gd -gdir=tests/gdscript