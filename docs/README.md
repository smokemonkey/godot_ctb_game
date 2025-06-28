# 项目文档

本目录包含项目的核心文档。

## 文档说明

### 📊 项目状态
- **PROJECT_STATUS.md** - 当前项目状态和里程碑
  - 新Schedulable架构状态
  - 功能完成度
  - 重要提醒和约定

### 📚 API文档
- **API_DOCS.md** - 自动生成的API参考文档
  - Python原型的完整API
  - 由 `python_prototypes/generate_docs.py` 生成
  - 包含所有类和方法的详细说明

### 📝 开发记录
- **DEVELOPMENT_NOTES.md** - 开发历程和重要决策
  - 设计演进过程
  - 重要的架构决定
  - 经验教训

## 架构文档

### 新Schedulable架构
- **重构完成**: CTB系统已重构为基于Schedulable接口
- **双语言实现**: Python和GDScript版本完全对应

### 代码对应关系 (历史参考)
- `../python_prototypes/CSHARP_MAPPING.md` - Python → C# 对应关系 (已弃用)
- `../scripts/csharp/PYTHON_MAPPING.md` - C# → Python 对应关系 (已弃用)

## 文档更新

- **API_DOCS.md** 通过 `python generate_docs.py` 自动生成
- 其他文档需要手动维护
- 修改代码时记得同步更新相关文档