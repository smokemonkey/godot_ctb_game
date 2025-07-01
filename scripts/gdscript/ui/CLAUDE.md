# UI组件 CLAUDE.md

基于动画的UI组件，提供流畅的用户界面过渡效果。

## ⚠️ 关键规则 - UI组件

1. **工具注解**: 所有UI组件使用`@tool`实现编辑器集成
2. **数据驱动动画**: 位置动画由数据属性驱动，而非硬编码位置
3. **浅拷贝模式**: 数据数组创建指向原始对象的新列表，确保安全操作
4. **进程管理**: 谨慎管理_process方法以避免性能问题

## 组件概览

### AnimatedListItem.gd
**用途**: 具有平滑位置过渡的单个动画列表项
- 支持以可配置速度平滑移动到目标位置（默认200px/s）
- 到达目标时发出animation_finished信号
- 使用`_process`进行逐帧移动，配合move_toward()
- 可配置到达阈值和动画速度

**核心特性**:
- `current_position`和`target_position`实现平滑插值
- 关联数据存储用于列表管理
- 自动扩展填满父容器宽度
- 编辑器提示检测避免不必要的处理

**使用模式**:
```gdscript
var item = AnimatedListItem.new()
item.set_data(some_data)
item.set_target_position(Vector2(0, new_y))
item.set_animation_speed(300.0)
```

### AnimatedList.gd  
**用途**: 管理多个AnimatedListItem的容器，具有自动排序和定位功能
- 基于关联数据的trigger_time自动排序
- 可配置项目高度和间距
- 批量位置更新与目标位置计算
- 支持数据驱动更新而不丢失动画状态

**核心特性**:
- `update_target_positions_by_trigger_time()` - 核心排序和定位逻辑
- `update_items_from_data()` - 智能数据同步，保留现有项目
- 支持异构数据（事件、日志、特殊项目）
- 自动尺寸管理适配容器宽度

**数据结构要求**:
项目必须包含以下字典数据：
- `trigger_time`: 用于排序位置
- `key`: 项目匹配的唯一标识符
- `original_trigger_time`: 用于预览/回滚功能

## 与CTB系统集成

### 当前实现
- **IntegratedSystemTest.gd** 使用AnimatedList显示CTB队列
- 事件按trigger_time排序，具有平滑位置过渡
- 剩余时间显示的实时更新（+Xh格式）
- 到期事件的智能高亮系统

### 数据流程
1. **数据源**: IndexedTimeWheel.peek_upcoming_events()返回包含original_trigger_time的数据
2. **处理**: IntegratedSystemTest转换为AnimatedList格式
3. **显示**: AnimatedList管理定位和动画
4. **更新**: 时间显示和颜色的实时刷新

## 动画系统设计

### 位置动画
- **触发**: 数据变化（新事件、时间推进、事件执行）
- **计算**: update_target_positions_by_trigger_time()分配新的Y坐标
- **执行**: 每个AnimatedListItem平滑移动到目标位置
- **完成**: animation_finished信号协调完成状态

### 更新循环保护
- 使用`_updating_ctb`标志防止无限更新循环
- 对防止UI->数据->UI反馈循环至关重要
- 应用于数据更新和UI刷新循环

## 已知问题和限制

### 性能考虑
- 每个AnimatedListItem在动画时运行_process()
- 多个项目同时动画可能影响性能
- 未来优化：考虑使用Tween节点提高性能

### GUI vs 命令行差异  
- **命令行**: 正常退出行为
- **GUI模式**: 退出挂起，可能原因：
  - 关闭期间活动的_process方法
  - 信号连接未正确断开
  - 应用程序终止时的动画帧请求

### 已准备的未来增强功能
- **技能预览系统**: original_trigger_time支持临时位置变化
- **高级动画**: 基础设施支持复杂动画模式
- **撤销/重做**: 数据结构支持状态回滚

## 开发指南

### 添加新的动画组件
1. 扩展AnimatedListItem用于自定义项目类型
2. 使用@tool注解实现编辑器集成
3. 实现数据驱动的位置计算
4. 遵循浅拷贝数据模式

### 性能最佳实践
1. 最小化_process使用 - 仅在实际动画时使用
2. 使用animation_finished信号检测完成
3. 批量位置更新而非单独变更
4. 考虑Tween替代方案用于复杂动画

### 测试集成
- 测试GUI和命令行模式
- 验证多项目动画性能
- 检查扩展动画序列的内存使用
- 测试数据同步边缘情况

## 架构未来规划

### 技能预览集成
系统已为技能预览功能做好准备：
- `original_trigger_time`存储用于回滚
- `modify_item_trigger_time()`和`restore_original_trigger_times()`方法已就绪
- 浅拷贝模式允许安全操作而不影响核心数据

### 组件可复用性
- AnimatedList设计用于CTB队列之外的复用
- 通用数据驱动方法支持各种列表类型
- 通过控件节点组合实现可定制样式

该系统为丰富的动画界面提供基础，同时保持数据完整性和性能。