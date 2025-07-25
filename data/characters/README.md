# 春秋角色数据库

按势力组织的明文角色模板文件。

## 目录结构

### 主要诸侯国
- `zheng_state/` - 郑国（小霸主）
- `qi_state/` - 齐国（大国，霸主候选）
- `jin_state/` - 晋国（大国，霸主候选） 
- `chu_state/` - 楚国（南方强国）
- `song_state/` - 宋国（殷商后裔）
- `lu_state/` - 鲁国（周公后裔，礼乐中心）

### 特殊势力
- `zhou_royal/` - 周王室（名义共主）
- `legendary_ancestors/` - 传说祖先（仅用于家族树）

## 文件命名规范

### 按人物重要性
- 主要君主：`{state}_{title}.txt` (如 `zheng_zhuang_gong.txt`)
- 重要大臣：`{state}_{name}.txt` (如 `qi_guan_zhong.txt`)
- 家族成员：包含在主要人物文件中

### 模板ID规范
- 格式：`{faction}_{name}_{version}`
- 示例：`zheng_zhuang_001`, `qi_huan_gong_001`

## 扩展语法特性

### 史料可靠性支持
```
abilities = {
    martial = 18,       # 正数：史料确定
    diplomacy = -12,    # 负数：以12为中心的不确定分布
    intrigue = 0        # 零：完全随机
}
```

### 多相位关系
```
possible_relationship_interpretations = {
    version_a = { weight = 70, source = "zuo_zhuan" }
    version_b = { weight = 30, source = "shi_ji" }
}
```

### 游戏可用性标记
- `genealogy_only = true` - 仅用于家族树
- `playable_character = true` - 可在游戏中操作
- `faction_affiliation = "state_name"` - 所属势力

## 历史时期设定

**时间范围**: 春秋时期 (770-476 BCE)
**核心特色**: 
- 礼崩乐坏的动荡时代
- 诸侯争霸的政治格局
- 史料相对可靠但仍有争议

## 数据质量分级

### 存在可能性
- `1.0` - 历史确定存在
- `0.7-0.9` - 很可能存在，史料较可靠
- `0.3-0.6` - 可能存在，传说成分较多
- `0.1-0.2` - 极可能是神话人物

### 史料可靠性
- `0.9+` - 《左传》等核心史料
- `0.7-0.8` - 《史记》等较可靠史料
- `0.5-0.6` - 后世整理，可能有误
- `0.3-` - 传说或推测

## 创建新角色指南

1. **确定所属势力**：选择合适的目录
2. **史料研究**：确定能力值和可靠性
3. **关系网络**：建立与现有角色的联系
4. **游戏定位**：决定是否可玩和重要性
5. **扩展语法**：利用不确定性和多相位特性

## 势力间关系

### 传统大国
- **齐国**: 东方霸主，管仲改革
- **晋国**: 北方强国，内政复杂
- **楚国**: 南方蛮夷，挑战周制

### 中小诸侯
- **郑国**: 小霸主，外交活跃
- **宋国**: 殷商遗民，文化保守  
- **鲁国**: 周公后裔，礼制中心

### 周王室
- **周王**: 名义共主，实力衰微
- **王室大臣**: 朝政参与者

此结构为mod作者提供清晰的春秋政治格局参考。