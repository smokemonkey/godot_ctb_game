# 游戏时间系统开发笔记

## 重要提醒 ⚠️

**现在的接口不要大改了！** (2025-06-12)

当前API已经稳定，经过多次迭代和用户反馈，已达到最终形态：
- 核心接口：`anchor_era()`, `start_new_era()`, `advance_time()`
- 查询接口：`get_current_era_name()`, `get_current_era_year()`
- 时间属性：`current_year`, `current_month`, `current_day_in_month`, `current_hour`

未来可能的小幅调整：
- 可能增加按小时数流逝时间的功能
- 但核心架构和主要接口保持不变

## 开发历程

### 第一阶段：过度工程化 (被拒绝)
- 创建了复杂的EraSystem数据类
- 多重era系统管理
- 用户反馈："太复杂了"，"你改的太大了"

### 第二阶段：重置和最小化实现 (成功)
- 完全重置，回到原始代码
- 只添加最小必要功能：
  - `anchor_era(era_name, gregorian_year)` - 锚定纪元
  - `start_new_era(name)` - 改元（内部调用anchor_era）
  - `get_current_era_name()` - 获取纪元名
  - `get_current_era_year()` - 获取纪元年份

### 第三阶段：用户细化需求
- 简化anchor参数（移除era_year）
- 添加未来时期限制
- 移除演示文件

### 第四阶段：向后兼容清理 (2025-06-12)
- 用户明确表示开发刚开始，不需要向后兼容
- 移除了EraNode类和_era_nodes列表
- 移除了add_era_node()方法
- 简化为纯锚定系统
- 更新了所有测试和Web界面

## 核心设计原则

1. **纯锚定系统**：只使用锚定机制，不维护纪元节点列表
2. **时间只能前进**：移除了时间跳转功能
3. **锚定vs改元**：
   - 锚定：可指定任意年份为纪元起始
   - 改元：只能将当前年份设为新纪元起始
4. **未来限制**：不允许锚定到未来时期

## 最终API

### TimeManager类
```python
# 时间推进
advance_time(amount: int, unit: TimeUnit = TimeUnit.DAY)

# 锚定功能
anchor_era(era_name: str, gregorian_year: int)
start_new_era(name: str)  # 改元，锚定当前年份

# 查询功能
get_current_era_name() -> Optional[str]
get_current_era_year() -> Optional[int]
get_time_info() -> dict

# 时间属性
current_year: int
current_month: int
current_day_in_month: int
current_hour: int
```

### Calendar类
```python
format_date_gregorian(show_hour: bool = False) -> str
format_date_era(show_hour: bool = False) -> str
get_time_status_text() -> str
```

## 测试覆盖

- ✅ 19个测试用例全部通过
- ✅ 基础时间推进功能
- ✅ 锚定功能和限制
- ✅ 改元功能
- ✅ 日历格式化
- ✅ Web界面功能

## 经验教训

1. **听用户的**：用户说"太复杂"就是太复杂
2. **最小化原则**：先实现最小功能，再根据需求扩展
3. **不要过度设计**：YAGNI原则很重要
4. **接口稳定性**：一旦用户满意，就不要再大改

## 未来扩展方向

- 可能增加按小时流逝的时间推进功能
- 保持现有接口不变
- 只做小幅度的功能增强

## 最新更新记录

### 2025-06-12 - CTB系统文档完善
- 为 `ctb/ctb.py` 添加详细的模块说明文档
- 更新 `ctb/__init__.py` 的文档风格，保持与时间系统一致
- 包含完整的功能说明、核心设计、使用场景和示例代码
- 所有38个测试用例继续通过，确保文档更新没有影响功能