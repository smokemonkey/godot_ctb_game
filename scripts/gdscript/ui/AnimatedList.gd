@tool
extends Container
class_name AnimatedList

## 管理整个动画列表的组件
## 支持根据数据自动排序和分配动画目标位置

## 预加载AnimatedListItem类
const AnimatedListItem = preload("res://scripts/gdscript/ui/AnimatedListItem.gd")

## 列表中的所有动画项
var items: Array[AnimatedListItem] = []
## 每个项目的高度（用于计算位置）
@export var item_height: float = 40.0
## 项目之间的间距
@export var item_spacing: float = 2.0
## 动画速度（像素/秒）
@export var animation_speed: float = 300.0

## 列表项被点击的信号
signal item_clicked(item: AnimatedListItem, data: Variant)
## 列表项动画完成的信号
signal item_animation_finished(item: AnimatedListItem)
## 所有动画完成的信号
signal all_animations_finished()

func _ready():
    # 设置容器的布局模式 - 禁用自动布局，使用手动定位
    if not Engine.is_editor_hint():
        # 确保容器不会自动排列子节点
        pass

## 设置项目高度和间距
func set_item_layout(height: float, spacing: float = 2.0):
    item_height = height
    item_spacing = spacing
    update_target_positions_by_trigger_time()

## 设置全局动画速度
func set_animation_speed(speed: float):
    animation_speed = speed
    for item in items:
        item.set_animation_speed(speed)

## 添加一个新的动画项
func add_animated_item(data: Variant, control_node: Control = null) -> AnimatedListItem:
    var item: AnimatedListItem
    
    if control_node:
        # 如果提供了控件节点，将其包装为AnimatedListItem
        item = AnimatedListItem.new()
        item.add_child(control_node)
        item.set_data(data)
        item.size = control_node.size
        # 设置控件的大小以匹配容器宽度
        control_node.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        control_node.anchors_preset = Control.PRESET_FULL_RECT
    else:
        # 创建基础的AnimatedListItem
        item = AnimatedListItem.new()
        item.set_data(data)
        item.custom_minimum_size = Vector2(0, item_height)
    
    # 设置项目的大小
    item.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    item.custom_minimum_size.y = item_height
    item.set_animation_speed(animation_speed)
    item.animation_finished.connect(_on_item_animation_finished)
    
    add_child(item)
    items.append(item)
    
    # 设置初始位置为列表底部
    var initial_y = (items.size() - 1) * (item_height + item_spacing)  # 修正索引计算
    item.position = Vector2(0, initial_y)
    item.current_position = Vector2(0, initial_y)
    item.target_position = Vector2(0, initial_y)
    
    # 调试信息
    if not Engine.is_editor_hint():
        print("Added item at position: ", initial_y, " with size: ", item.size)
    
    return item

## 移除动画项
func remove_animated_item(item: AnimatedListItem):
    if item in items:
        items.erase(item)
        remove_child(item)
        item.queue_free()
        update_target_positions_by_trigger_time()

## 清空所有项目
func clear_all_items():
    for item in items:
        remove_child(item)
        item.queue_free()
    items.clear()

## 根据trigger_time排序并更新所有项目的目标位置
func update_target_positions_by_trigger_time():
    if items.size() == 0:
        return
    
    # 按trigger_time排序（从data中获取）
    items.sort_custom(_compare_by_trigger_time)
    
    # 为每个项目分配新的目标位置
    for i in range(items.size()):
        var new_y = i * (item_height + item_spacing)
        var new_target = Vector2(0, new_y)
        items[i].set_target_position(new_target)
        
        # 确保项目的大小正确
        var container_width = get_rect().size.x if get_rect().size.x > 0 else 280
        items[i].size.x = container_width
        items[i].size.y = item_height
        
        # 调试信息
        if not Engine.is_editor_hint():
            print("Updated item %d size to: %s" % [i, items[i].size])

## 比较函数：按trigger_time排序
func _compare_by_trigger_time(a: AnimatedListItem, b: AnimatedListItem) -> bool:
    var data_a = a.get_data()
    var data_b = b.get_data()
    
    # 确保数据包含trigger_time字段
    if typeof(data_a) == TYPE_DICTIONARY and typeof(data_b) == TYPE_DICTIONARY:
        if "trigger_time" in data_a and "trigger_time" in data_b:
            return data_a.trigger_time < data_b.trigger_time
    
    # 备用排序方式：按添加顺序
    return items.find(a) < items.find(b)

## 修改指定项目的trigger_time并更新位置（用于技能预览）
func modify_item_trigger_time(item: AnimatedListItem, new_trigger_time: int):
    var data = item.get_data()
    if typeof(data) == TYPE_DICTIONARY and "trigger_time" in data:
        data.trigger_time = new_trigger_time
        update_target_positions_by_trigger_time()

## 恢复指定项目的原始trigger_time
func restore_item_original_trigger_time(item: AnimatedListItem):
    var data = item.get_data()
    if typeof(data) == TYPE_DICTIONARY and "original_trigger_time" in data:
        data.trigger_time = data.original_trigger_time
        update_target_positions_by_trigger_time()

## 恢复所有项目的原始trigger_time（取消技能预览）
func restore_all_original_trigger_times():
    var needs_update = false
    for item in items:
        var data = item.get_data()
        if typeof(data) == TYPE_DICTIONARY and "original_trigger_time" in data:
            if data.trigger_time != data.original_trigger_time:
                data.trigger_time = data.original_trigger_time
                needs_update = true
    
    if needs_update:
        update_target_positions_by_trigger_time()

## 检查是否有任何项目正在动画中
func has_animating_items() -> bool:
    for item in items:
        if item.is_animating():
            return true
    return false

## 让所有项目立即跳转到目标位置
func snap_all_to_targets():
    for item in items:
        item.snap_to_target()

## 获取指定数据的项目
func find_item_by_data(target_data: Variant) -> AnimatedListItem:
    for item in items:
        if item.get_data() == target_data:
            return item
    return null

## 项目动画完成的回调
func _on_item_animation_finished(item: AnimatedListItem):
    item_animation_finished.emit(item)
    
    # 检查是否所有动画都完成了
    if not has_animating_items():
        all_animations_finished.emit()

## 获取所有项目的数据列表
func get_all_data() -> Array:
    var data_list = []
    for item in items:
        data_list.append(item.get_data())
    return data_list

## 更新现有项目的数据（保持动画状态）
func update_items_from_data(data_array: Array):
    # 移除不再存在的项目
    var items_to_remove = []
    for item in items:
        var found = false
        for data in data_array:
            if _data_matches(item.get_data(), data):
                found = true
                break
        if not found:
            items_to_remove.append(item)
    
    for item in items_to_remove:
        remove_animated_item(item)
    
    # 添加新项目或更新现有项目
    for data in data_array:
        var existing_item = _find_item_by_matching_data(data)
        if existing_item:
            # 更新现有项目的数据
            existing_item.set_data(data)
        else:
            # 添加新项目
            add_animated_item(data)
    
    # 更新位置
    update_target_positions_by_trigger_time()

## 检查两个数据是否匹配（通过key字段）
func _data_matches(data1: Variant, data2: Variant) -> bool:
    if typeof(data1) == TYPE_DICTIONARY and typeof(data2) == TYPE_DICTIONARY:
        if "key" in data1 and "key" in data2:
            return data1.key == data2.key
    return data1 == data2

## 通过匹配数据查找项目
func _find_item_by_matching_data(target_data: Variant) -> AnimatedListItem:
    for item in items:
        if _data_matches(item.get_data(), target_data):
            return item
    return null

