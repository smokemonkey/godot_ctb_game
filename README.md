# 回合制游戏时间系统

一个专为回合制游戏设计的完整时间管理系统，支持非匀速时间流逝、双纪年显示和精确时间控制。

## ✨ 特性

### 🕒 核心时间系统
- **360天/年，24小时/天** 的自定义时间体系
- **公元前1000年起始** 的完整时间线
- **小时级精度** 的时间控制
- **非匀速时间流逝** - 可按需推进时间

### 🏛️ 双纪年系统
- **公历显示**: 公元前/公元XX年XX月XX日
- **自定义纪年**: 支持添加历史纪年节点（如"开元"、"贞观"等）
- **灵活切换**: 同时显示两种纪年方式

### 🎮 用户界面
- **实时时间显示**: 当前时间状态面板
- **快捷控制**: +1天/+10天/+100天/+1年按钮
- **精确输入**: 支持输入指定天数/小时数推进
- **纪年管理**: 可添加自定义纪年节点

### 🎨 技术特性
- **自适应字体**: 根据控件大小自动调整字体
- **中文支持**: 自动检测并使用支持中文的系统字体
- **模块化设计**: 低耦合，易于集成到其他项目

## 🚀 快速开始

### 安装依赖
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装pygame
pip install pygame
```

### 运行演示
```bash
python main.py
```

### 运行测试
```bash
# 使用测试运行器
python run_tests.py

# 或直接运行测试文件
python test_time_system.py
```

## 📖 基础用法

### 1. 基本时间操作
```python
from time_system import TimeManager, Calendar

# 创建时间管理器
time_manager = TimeManager()

# 推进时间
time_manager.advance_time(30, TimeUnit.DAY)  # 推进30天
time_manager.advance_time(5, TimeUnit.HOUR)  # 推进5小时

# 获取当前时间信息
print(f"当前年份: {time_manager.current_year}")
print(f"当前月份: {time_manager.current_month}")
print(f"当前日期: {time_manager.current_day_in_month}")
```

### 2. 纪年管理
```python
# 添加纪年节点
time_manager.add_era_node("开元")  # 在当前年份添加"开元"纪年
time_manager.add_era_node("贞观", start_year=626)  # 在公元626年添加"贞观"纪年

# 获取当前纪年
current_era = time_manager.get_current_era()
if current_era:
    print(f"当前纪年: {current_era.name}")
```

### 3. 日期显示
```python
# 创建日历显示器
calendar = Calendar(time_manager)

# 公历格式
gregorian_date = calendar.format_date_gregorian()
print(gregorian_date)  # "公元前999年1月1日"

# 纪年格式
era_date = calendar.format_date_era()
print(era_date)  # "开元1年1月1日"

# 详细状态
status = calendar.get_time_status_text()
print(status)
```

## 🎯 适用场景

- **回合制策略游戏**: 文明建设、王朝兴衰模拟
- **历史模拟游戏**: 需要准确历法的历史重现
- **RPG游戏**: 长时间跨度的剧情发展
- **经营模拟**: 需要时间管理的经营类游戏

## 📁 项目结构

```
pygame-sample/
├── time_system.py        # 核心时间管理逻辑
├── ui_components.py      # UI组件库（Button, InputBox, TextDisplay）
├── font_manager.py       # 自适应字体管理器
├── main.py              # 主程序和测试界面
├── test_time_system.py  # 时间系统测试用例
├── run_tests.py         # 测试运行器
├── requirements.txt     # 依赖列表
└── README.md           # 项目文档
```

## 🔧 核心API

### TimeManager类
- `advance_time(amount, unit)`: 推进时间
- `set_time_to_day(day)`: 跳转到指定天
- `add_era_node(name, start_year)`: 添加纪年节点
- `current_year/month/day`: 当前时间属性

### Calendar类
- `format_date_gregorian(show_hour)`: 公历格式化
- `format_date_era(show_hour)`: 纪年格式化
- `get_time_status_text()`: 详细时间状态

## 🎨 自定义和扩展

### 修改时间体系
```python
# 在TimeManager类中修改常量
DAYS_PER_YEAR = 365  # 改为365天/年
HOURS_PER_DAY = 12   # 改为12小时/天
```

### 集成到游戏中
```python
# 在游戏主循环中
def game_update():
    # 处理游戏逻辑
    process_player_turn()
    
    # 推进时间
    if turn_completed:
        time_manager.advance_time(1, TimeUnit.DAY)
    
    # 更新UI显示
    update_time_display()
```

## 📋 开发要求来源

> **原始需求**: 制作一个回合制游戏，时间的流逝不是匀速的，最根本的组件是控制时间的流逝。需要一个控制历法与时间的模块，假定一年有360天，每天最多有24个单元，可以控制让时间流逝到XX天或者XX单元之后。默认以天为单位流逝。提供当前日期显示功能，真实计时从公元前1000年开始，真实日期显示为公元XX年XX月XX日XX点（通常不显示时间）。但是更多时候采用另一种显示方法：允许在日历中加入XX元年的节点，之后显示的日期就以XX元年为基准。保持低耦合设计。

## 📄 许可证

MIT License - 可自由用于商业和非商业项目。 