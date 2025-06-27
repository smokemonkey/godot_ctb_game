# Godot项目跨平台启动器
# 使用方法: make run 或 make test

# 检测操作系统
UNAME_S := $(shell uname -s)

# 根据操作系统设置Godot路径
ifeq ($(UNAME_S),Linux)
    GODOT ?= $(shell which godot || echo "/usr/bin/godot")
    PLATFORM = linux
endif
ifeq ($(UNAME_S),Darwin)
    GODOT ?= $(shell which godot || echo "/Applications/Godot.app/Contents/MacOS/Godot")
    PLATFORM = macos
endif
ifeq ($(OS),Windows_NT)
    GODOT ?= D:/godot/Godot_v4.4.1-stable_mono_win64.exe
    PLATFORM = windows
endif

# 默认目标
.PHONY: help
help:
	@echo "Godot集成系统测试 - 跨平台启动器"
	@echo ""
	@echo "使用方法:"
	@echo "  make run       - 启动集成系统测试"
	@echo "  make test      - 同上"
	@echo "  make editor    - 打开Godot编辑器"
	@echo "  make build     - 构建C#项目"
	@echo "  make clean     - 清理临时文件"
	@echo "  make info      - 显示系统信息"
	@echo ""
	@echo "当前平台: $(PLATFORM)"
	@echo "Godot路径: $(GODOT)"

.PHONY: run test
run test:
	@echo "🎮 启动集成系统测试..."
	@echo "📍 平台: $(PLATFORM)"
	@echo "🔧 Godot: $(GODOT)"
	@if [ ! -f "$(GODOT)" ]; then \
		echo "❌ 错误: 未找到Godot可执行文件: $(GODOT)"; \
		echo "请设置GODOT环境变量或修改Makefile"; \
		exit 1; \
	fi
	@if [ ! -f "project.godot" ]; then \
		echo "❌ 错误: 未找到project.godot文件"; \
		exit 1; \
	fi
	"$(GODOT)" --path "$(shell pwd)"

.PHONY: editor
editor:
	@echo "🔧 打开Godot编辑器..."
	"$(GODOT)" --path "$(shell pwd)" --editor

.PHONY: build
build:
	@echo "🔨 构建C#项目..."
	"$(GODOT)" --headless --build-solutions --quit

.PHONY: clean
clean:
	@echo "🧹 清理临时文件..."
	@find . -name "*.tmp" -delete 2>/dev/null || true
	@find . -name ".godot" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

.PHONY: info
info:
	@echo "📊 系统信息:"
	@echo "  操作系统: $(shell uname -s) $(shell uname -r)"
	@echo "  平台: $(PLATFORM)"
	@echo "  Godot路径: $(GODOT)"
	@echo "  Godot存在: $(shell [ -f "$(GODOT)" ] && echo "✅" || echo "❌")"
	@echo "  项目文件: $(shell [ -f "project.godot" ] && echo "✅" || echo "❌")"
	@echo "  当前目录: $(shell pwd)"