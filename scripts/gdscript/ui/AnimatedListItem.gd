@tool
extends Control
class_name AnimatedListItem

## 通用的动画列表项组件
## 支持平滑动画移动到目标位置，适用于CTB队列等需要动态重排的UI元素

## 当前显示位置（可能正在动画中）
var current_position: Vector2
## 目标位置（动画的终点）
var target_position: Vector2
## 动画速度（像素/秒）
@export var animation_speed: float = 300.0
## 到达目标的容差距离
@export var arrival_threshold: float = 1.0
## 关联的数据对象（通常是事件数据）
var data: Variant

## 动画完成信号
signal animation_finished(item: AnimatedListItem)

func _ready():
    # 初始化位置为当前Control位置
    current_position = position
    target_position = position
    
    # 确保能够填满父容器的宽度
    if not Engine.is_editor_hint():
        size_flags_horizontal = Control.SIZE_EXPAND_FILL

## 设置新的目标位置，开始动画
func set_target_position(new_target: Vector2):
    target_position = new_target
    
## 立即跳转到目标位置，不播放动画
func snap_to_target():
    current_position = target_position
    position = current_position
    animation_finished.emit(self)

## 检查是否正在动画中
func is_animating() -> bool:
    return current_position.distance_to(target_position) > arrival_threshold

## 设置动画速度
func set_animation_speed(speed: float):
    animation_speed = max(speed, 0.1)  # 防止速度过小

## 设置关联数据
func set_data(new_data: Variant):
    data = new_data

## 获取关联数据
func get_data() -> Variant:
    return data

func _process(delta):
    if not Engine.is_editor_hint() and is_animating():
        # 向目标位置移动
        current_position = current_position.move_toward(target_position, animation_speed * delta)
        position = current_position
        
        # 检查是否到达目标
        if not is_animating():
            animation_finished.emit(self)


## 设置到达容差
func set_arrival_threshold(threshold: float):
    arrival_threshold = max(threshold, 0.1)

## 获取到目标位置的距离
func get_distance_to_target() -> float:
    return current_position.distance_to(target_position)