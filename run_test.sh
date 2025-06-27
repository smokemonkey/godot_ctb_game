#!/bin/bash
# 跨平台测试运行脚本

# 检测操作系统并找到Godot可执行文件
GODOT_EXEC=""

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    GODOT_PATHS=(
        "/usr/bin/godot"
        "/usr/local/bin/godot"
        "/opt/godot/godot"
        "./godot"
        "../godot/godot"
    )
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    GODOT_PATHS=(
        "/Applications/Godot.app/Contents/MacOS/Godot"
        "/Applications/Godot_mono.app/Contents/MacOS/Godot"
        "/usr/local/bin/godot"
        "./godot"
    )
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash/MSYS2)
    GODOT_PATHS=(
        "/mnt/d/godot/Godot_v4.4.1-stable_mono_win64.exe"
        "/c/godot/Godot_v4.4.1-stable_mono_win64.exe"
        "./Godot.exe"
        "./godot.exe"
        "C:/Godot/Godot.exe"
    )
fi

# 寻找Godot可执行文件
for path in "${GODOT_PATHS[@]}"; do
    if [[ -f "$path" ]]; then
        GODOT_EXEC="$path"
        break
    fi
done

if [[ -z "$GODOT_EXEC" ]]; then
    echo "❌ 未找到Godot可执行文件"
    echo "请将Godot安装路径添加到PATH环境变量，或修改此脚本"
    echo "常见安装位置:"
    for path in "${GODOT_PATHS[@]}"; do
        echo "  - $path"
    done
    exit 1
fi

echo "🎮 使用Godot: $GODOT_EXEC"
echo "🚀 启动集成系统测试..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 运行Godot项目
"$GODOT_EXEC" --path "$(pwd)"