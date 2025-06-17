# 回合制游戏时间系统

一个专为回合制游戏设计的完整时间管理系统，支持非匀速时间流逝、双纪年显示和精确时间控制。

## ✨ 特性

### 🕒 核心时间系统
- **360天/年，24小时/天** 的自定义时间体系
- **公元前722年起始** 的完整时间线（鲁隐公元年，春秋开始）
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
- **高级输入框**: 支持光标移动、文本选择、中文输入法

### 🎨 技术特性
- **自适应字体**: 根据控件大小自动调整字体
- **中文支持**: 自动检测并使用支持中文的系统字体
- **高级输入**: 光标移动、文本滚动、输入法组合状态显示
- **模块化设计**: 低耦合，易于集成到其他项目
- **自动文档**: 内置API文档生成器

## 🚀 快速开始

### 方式1: 直接使用（推荐）
```bash
# 克隆仓库
git clone <repository-url>
cd pygame-sample

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 方式2: 包安装模式
```bash
# 开发模式安装（可编辑）
pip install -e .

# 或正式安装
pip install .
```

### 运行演示
```bash
# 方式1: 直接运行演示
cd examples && python demo.py

# 方式2: 使用包导入方式
python -c "from examples.demo import main; main()"
```

### 运行测试
```bash
# 使用根目录测试运行器（推荐）
python run_tests.py

# 或使用tests目录的运行器
cd tests && python run_tests.py

# 或直接运行测试文件
cd tests && python test_time_system.py
```

### 生成API文档
```bash
# 自动生成API文档
python generate_docs.py

# 将在根目录生成 API_DOCS.md 文件
```

## 📖 基础用法

### 1. 基本时间操作
```python
from game_time import TimeManager, Calendar, TimeUnit

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
print(gregorian_date)  # "公元前722年1月1日"

# 纪年格式
era_date = calendar.format_date_era()
print(era_date)  # "开元1年1月1日"

# 详细状态
status = calendar.get_time_status_text()
print(status)
```

## ⌨️ 输入框功能

游戏提供了功能强大的输入框组件：

### 光标操作
- **左右箭头键**: 移动光标位置
- **Home键**: 光标移到开头
- **End键**: 光标移到末尾
- **Backspace**: 删除光标前的字符
- **Delete**: 删除光标后的字符

### 中文输入支持
- **输入法组合**: 支持拼音等输入法的组合状态显示
- **组合预览**: 实时显示输入法组合字符（带下划线）
- **自动确认**: Enter键确认组合，Escape键取消组合

### 文本滚动
- **自动滚动**: 当文本超出输入框宽度时自动滚动
- **光标跟随**: 滚动时始终保持光标可见

## 🎯 适用场景

- **回合制策略游戏**: 文明建设、王朝兴衰模拟
- **历史模拟游戏**: 需要准确历法的历史重现
- **RPG游戏**: 长时间跨度的剧情发展
- **经营模拟**: 需要时间管理的经营类游戏

## 📁 项目结构

```
pygame-sample/
├── game_time/              # 核心时间系统包
│   ├── __init__.py        # 包初始化和API导出
│   ├── time_system.py     # 时间管理核心逻辑
│   ├── ui_components.py   # UI组件库
│   └── font_manager.py    # 自适应字体管理器
├── tests/                 # 测试目录
│   ├── test_time_system.py # 时间系统测试用例
│   └── run_tests.py       # 测试运行器
├── examples/              # 示例代码
│   └── demo.py           # 演示程序
├── setup.py              # 包安装配置
├── run_tests.py          # 根目录测试运行器
├── requirements.txt      # 依赖列表
└── README.md            # 项目文档
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

## 📋 开发需求来源

> **核心需求**: 为回合制游戏开发一个支持非匀速时间流逝的时间管理系统。该系统的核心功能是精确控制游戏时间的推进过程。
>
> **技术规格**:
> - **时间体系**: 采用360天/年、24小时/天的自定义历法系统
> - **时间控制**: 支持按天或小时为单位推进时间，可精确跳转到指定时间点
> - **起始时间**: 以公元前722年（鲁隐公元年，春秋时代开始）作为时间起点
> - **显示系统**:
>   - **标准格式**: 公元XX年XX月XX日XX点（可选显示小时）
>   - **纪年格式**: 支持添加自定义纪年节点（如"开元"、"贞观"等），并以此为基准显示日期
> - **架构要求**: 采用低耦合的模块化设计，便于集成到不同的游戏项目中

## 📄 许可证

MIT License - 可自由用于商业和非商业项目。

## 核心功能

### 1. 游戏时间系统 (game_time)
- 360天年历系统（12个月，每月30天）
- 支持公元纪年和自定义纪元
- 精确到小时的时间控制
- 纪元锚定和改元功能

### 2. CTB战斗系统 (ctb) - v2.0 环形缓冲区版本
- **全新设计**: 基于环形缓冲区的高效事件调度
- **统一事件模型**: 角色行动、季节变化、节日等统一处理
- **随机行动间隔**: 1-180天随机间隔（平均90天）
- **链表时间槽**: 支持同时间多事件
- **角色索引**: O(1)的角色事件查找

### 3. Web演示界面
- 实时显示时间流逝
- 可视化行动队列
- 交互式控制面板

## 最新更新 (v2.0)

### CTB系统重大升级
- 移除了基于速度的简单除法计算
- 实现了180天（4320小时）的环形缓冲区
- Character现在继承自Event基类
- 支持自定义事件类型（季节、节日等）
- 更高效的内存使用和时间复杂度

### 设计亮点
1. **环形缓冲区**: 固定内存占用，O(1)时间推进
2. **事件继承体系**: 易于扩展新的事件类型
3. **链表槽位**: 优雅处理同时触发的事件
4. **动态offset**: 避免数组整体移动的开销