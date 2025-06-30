# Core 文件夹 CLAUDE.md

## ⚠️ 关键警告

**这部分的设计被认为是最终确定和测试完成的，没有我的明确请求或许可，不要更改。**

## 核心系统组件

这个文件夹包含游戏的核心系统组件，经过充分测试和验证：

### Calendar.gd - 日历系统
**用途**: 游戏时间管理和纪年系统
- 自定义日历（360天/年，24小时/天）
- 纪年锚定和纪元管理
- 公历和游戏内纪年转换
- 时间推进和格式化显示

**核心功能**:
- 时间戳管理和推进
- 纪元锚定系统
- 多种时间格式显示
- 线程安全的时间操作

### IndexedTimeWheel.gd - 索引时间轮
**用途**: 高效的事件调度数据结构
- 循环缓冲区用于近期事件
- 未来事件列表用于远期事件
- O(1) 调度和检索性能
- 支持绝对时间和相对延迟调度

**核心功能**:
- 高效事件调度和检索
- 未来事件自动迁移
- 时间轮推进和事件弹出
- 事件计数和状态查询

### CTBManager.gd - CTB战斗管理器
**用途**: 条件回合制战斗系统管理
- 回调模式与时间轮集成
- 自动重调度机制
- 事件执行和生命周期管理
- 状态查询和调试支持

**核心功能**:
- Schedulable对象调度管理
- 回合处理和时间推进
- 事件执行和回调触发
- 系统状态监控

## 系统架构

```
CTBManager (调度管理)
    ↓ uses
IndexedTimeWheel (事件存储)
    ↓ uses  
Calendar (时间系统)
```

### 集成模式
1. **Calendar** 提供统一的时间基础
2. **IndexedTimeWheel** 管理事件的时间调度
3. **CTBManager** 协调整个调度流程

### 回调系统
CTBManager使用回调模式实现与具体数据结构的解耦：
- `get_time_callback`: 获取当前时间
- `advance_time_callback`: 推进时间
- `schedule_callback`: 调度事件
- `remove_callback`: 移除事件
- `peek_callback`: 查看即将到来的事件
- `pop_callback`: 弹出到期事件
- `is_slot_empty_callback`: 检查当前时间槽

## 设计原则

### 1. 性能优化
- IndexedTimeWheel使用O(1)调度操作
- 循环缓冲区减少内存分配
- 未来事件分离避免影响热路径

### 2. 模块化设计
- 各组件职责清晰分离
- 回调接口实现松耦合
- 可独立测试和验证

### 3. 可扩展性
- 支持任意Schedulable对象
- 灵活的时间配置
- 可配置的缓冲区大小

## 测试覆盖

所有核心组件都有完整的单元测试：
- `tests/gdscript/test_calendar.gd`
- `tests/gdscript/test_time_wheel.gd`
- `tests/gdscript/test_ctb_manager.gd`

测试覆盖包括：
- 基本功能验证
- 边界条件处理
- 性能特征验证
- 错误条件测试

## 使用模式

### 典型初始化流程
```gdscript
# 1. 创建日历
var calendar = Calendar.new()

# 2. 创建时间轮
var time_wheel = IndexedTimeWheel.new(180, calendar.get_timestamp)

# 3. 创建CTB管理器
var ctb_manager = CTBManager.new(
    calendar.get_timestamp,          # get_time
    _advance_time_callback,          # advance_time
    _schedule_callback,              # schedule
    _remove_callback,                # remove
    _peek_callback,                  # peek
    _pop_callback,                   # pop
    _is_slot_empty_callback          # is_empty
)
```

### 事件调度流程
```gdscript
# 调度可调度对象
var house = House.new("house_id", "家族名称")
ctb_manager.schedule_with_delay("house_id", house, 24)

# 处理下一个回合
var result = ctb_manager.process_next_turn()
```

## 配置参数

核心系统使用ConfigManager进行配置：
- `time_hours_per_day`: 每天小时数 (默认24)
- `time_days_per_year`: 每年天数 (默认360)
- `time_epoch_start_year`: 纪元起始年 (默认-2000)
- `ctb_time_wheel_buffer_size`: 时间轮缓冲区大小 (默认4320)

## 性能特征

### 时间复杂度
- 事件调度: O(1)
- 事件检索: O(1)
- 时间推进: O(k) 其中k是当前槽事件数
- 未来事件迁移: O(m) 其中m是需要迁移的事件数

### 内存使用
- 主缓冲区: O(buffer_size)
- 未来事件列表: O(future_events_count)
- 键值映射: O(total_events)

## 维护注意事项

1. **不要修改核心算法** - 除非有明确的性能问题
2. **保持测试覆盖** - 任何更改都需要对应的测试更新
3. **向后兼容** - 公共API变更需要仔细考虑影响
4. **性能监控** - 关键路径的性能变化需要测量验证

## 扩展指南

如果需要扩展核心系统：
1. 首先评估是否真的需要修改核心组件
2. 考虑通过组合而非修改来实现新功能
3. 确保有完整的测试覆盖
4. 保持与现有系统的兼容性