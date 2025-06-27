# 如何运行集成系统测试

这个项目现在有**跨平台启动方案**，支持Windows、macOS、Linux。

## 🚀 快速启动（推荐）

### 方法1: Python启动器（推荐）
```bash
python3 run_test.py
```
或
```bash
./run_test.py
```

### 方法2: Shell脚本（Linux/macOS）
```bash
./run_test.sh
```

### 方法3: Makefile（所有平台）
```bash
make run
# 或
make test
```

### 方法4: 手动启动
```bash
# 找到你的Godot安装路径，然后：
/path/to/godot --path /path/to/this/project
```

## 📋 其他可用命令

### 打开Godot编辑器
```bash
make editor
```


### 查看系统信息
```bash
make info
```

### 清理临时文件
```bash
make clean
```

## 🔧 配置Godot路径

如果自动检测失败，可以手动设置：

### 环境变量方式
```bash
export GODOT=/path/to/your/godot
python3 run_test.py
```

### Makefile方式
```bash
make run GODOT=/path/to/your/godot
```

## 🎮 使用说明

启动后你会看到三栏界面：

- **左侧**: CTB行动条（可复用到实际游戏）
- **中间**: 控制面板（时间推进、纪元管理）  
- **右侧**: 时间轮检查器（事件监控）

## ✨ 最新功能

### UI改进
- 字号优化：标题18px，内容14-16px，确保清晰可读
- 按钮修复：确保"添加行动"和"执行行动"按钮正常显示
- 更好的布局：所有UI元素正确填充窗口空间

### CTB队列系统（重新设计）
- **真正的事件队列**：显示即将执行的行动，而非日志
- **队列排序**：按执行顺序显示，下一个执行的高亮显示
- **位置编号**：每个事件显示队列位置（01, 02, 03...）
- **颜色系统**：
  - 🟡 黄色高亮：下一个要执行的事件
  - 🔵 蓝色渐变：排队等待的事件（越靠后越淡）
- **底部日志**：简短的操作日志（限制5条）

### 跨平台支持
- 移除了Windows专用的.bat文件
- 添加了Linux/macOS shell脚本
- Python启动器支持所有平台
- Makefile提供统一的命令接口

现在无论在什么平台开发，都能轻松启动测试！