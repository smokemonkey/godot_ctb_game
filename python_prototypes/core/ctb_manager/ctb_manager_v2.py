#!/usr/bin/env python3
"""
CTB管理器 v2.0 - 基于可调度接口的重构版本

重构后的CTB系统，移除了对具体Character类的依赖，改为使用Schedulable接口。

核心改进:
- 解耦合: 不再依赖特定的角色或事件类型
- 统一接口: 所有可调度对象使用相同的Schedulable接口
- 灵活扩展: 任何实现Schedulable接口的对象都可以被调度
- 单一职责: CTB只负责调度，不关心具体对象类型
"""

from typing import Dict, List, Any, Callable, Optional
from ..schedulable import Schedulable, EventExample


class CTBManager:
    """
    CTB系统管理器

    负责管理可调度对象的调度和执行，通过回调函数处理时间管理。

    Attributes:
        scheduled_objects: 已注册的可调度对象字典
        is_initialized: 是否已初始化
        action_history: 行动历史记录
        on_event_executed: 事件执行回调函数
    """

    def __init__(self,
                 get_time_callback: Callable[[], int],
                 advance_time_callback: Callable[[], None],
                 schedule_callback: Callable[[str, Schedulable, int], bool],
                 remove_callback: Callable[[str], bool],
                 peek_callback: Callable[[int, int], List[Dict[str, Any]]],
                 pop_callback: Callable[[], Dict[str, Any]],
                 is_slot_empty_callback: Callable[[], bool]):
        """
        初始化CTB管理器

        Args:
            get_time_callback: 获取当前时间的回调函数
            advance_time_callback: 推进时间的回调函数
            schedule_callback: 调度事件的回调函数
            remove_callback: 移除事件的回调函数
            peek_callback: 查看即将到来事件的回调函数
            pop_callback: 弹出到期事件的回调函数
            is_slot_empty_callback: 检查当前时间槽是否为空的回调函数
        """
        # 时间管理回调
        self._get_time_callback = get_time_callback
        self._advance_time_callback = advance_time_callback
        self._schedule_callback = schedule_callback
        self._remove_callback = remove_callback
        self._peek_callback = peek_callback
        self._pop_callback = pop_callback
        self._is_slot_empty_callback = is_slot_empty_callback

        # 状态
        self.scheduled_objects: Dict[str, Schedulable] = {}
        self.is_initialized = False
        self.action_history: List[Dict[str, Any]] = []

        # 事件执行回调
        self.on_event_executed: Optional[Callable[[Schedulable], None]] = None

    def add_event(self, schedulable: Schedulable) -> None:
        """
        添加可调度对象到系统

        Args:
            schedulable: 要添加的可调度对象

        Raises:
            ValueError: 如果ID已存在
        """
        if schedulable.id in self.scheduled_objects:
            raise ValueError(f"Schedulable with ID {schedulable.id} already exists")

        self.scheduled_objects[schedulable.id] = schedulable
        print(f"已添加可调度对象: {schedulable.name}")

    def remove_event(self, schedulable_id: str) -> bool:
        """
        从系统中移除可调度对象

        Args:
            schedulable_id: 要移除的对象ID

        Returns:
            是否成功移除
        """
        if schedulable_id not in self.scheduled_objects:
            return False

        # 从时间轮中移除对象的事件
        self._remove_callback(schedulable_id)

        # 从对象字典中移除
        removed_obj = self.scheduled_objects.pop(schedulable_id)
        print(f"已移除可调度对象: {removed_obj.name}")
        return True

    def get_event(self, schedulable_id: str) -> Optional[Schedulable]:
        """
        获取可调度对象

        Args:
            schedulable_id: 对象ID

        Returns:
            可调度对象，如果不存在则返回None
        """
        return self.scheduled_objects.get(schedulable_id)

    def initialize_ctb(self) -> None:
        """
        初始化CTB系统

        为所有可调度对象排程初始调度时间。

        Raises:
            ValueError: 如果没有可调度对象
        """
        if not self.scheduled_objects:
            raise ValueError("Cannot initialize CTB without schedulable objects")

        current_time = self._get_time_callback()
        print(f"初始化CTB系统，当前时间: {current_time}")

        # 为每个可调度对象排程初始调度
        for obj in self.scheduled_objects.values():
            if obj.should_reschedule():
                # 计算初始调度时间
                next_time = obj.calculate_next_schedule_time(current_time)
                obj.trigger_time = next_time

                # 添加到时间轮
                delay = next_time - current_time
                self._schedule_callback(obj.id, obj, delay)
                print(f"已为 {obj.name} 安排初始调度，延迟: {delay} 小时")

        self.is_initialized = True
        print("CTB系统初始化完成")

    def process_next_turn(self) -> Dict[str, Any]:
        """
        处理下一个逻辑回合

        会推进时间直到找到下一个事件。这是CTB系统的核心"回合"处理。

        Returns:
            包含回合处理结果的字典
        """
        ticks_advanced = 0
        while self._is_slot_empty_callback():
            if ticks_advanced > 24 * 365:
                raise RuntimeError("CTBManager advanced time for over a year without finding any event.")
            self._advance_time_callback()
            ticks_advanced += 1

        due_event = self.get_due_event()
        if due_event is not None:
            self.execute_event(due_event)
            return {
                "type": "SCHEDULABLE_EXECUTED",
                "ticks_advanced": ticks_advanced,
                "schedulable_id": due_event.id,
                "schedulable_name": due_event.name,
                "schedulable_type": due_event.get_type_identifier(),
                "timestamp": self._get_time_callback()
            }

        raise RuntimeError("Inconsistent State: Slot was not empty, but no schedulable could be popped.")

    def schedule_event(self, schedulable: Schedulable, trigger_time: int) -> bool:
        """
        安排自定义可调度对象

        Args:
            schedulable: 要调度的对象
            trigger_time: 触发时间

        Returns:
            是否成功调度
        """
        current_time = self._get_time_callback()
        if trigger_time < current_time:
            return False  # 不能在过去安排事件

        delay = trigger_time - current_time
        return self.schedule_with_delay(schedulable.id, schedulable, delay)

    def schedule_with_delay(self, key: str, schedulable: Schedulable, delay: int) -> bool:
        """
        使用延迟时间安排可调度对象

        Args:
            key: 调度键
            schedulable: 可调度对象
            delay: 延迟时间

        Returns:
            是否成功调度
        """
        return self._schedule_callback(key, schedulable, delay)

    def get_due_event(self) -> Optional[Schedulable]:
        """
        获取当前时间到期的下一个可调度对象

        Returns:
            到期的可调度对象，如果没有则返回None
        """
        result = self._pop_callback()
        if not result:
            return None

        # Python版本返回元组(key, value)，GDScript版本返回字典{"key": key, "value": value}
        if isinstance(result, tuple) and len(result) == 2:
            return result[1]  # 返回value部分
        elif isinstance(result, dict) and "value" in result:
            return result["value"]
        else:
            return None

    def execute_events(self, schedulables: List[Schedulable]) -> None:
        """
        执行可调度对象列表

        Args:
            schedulables: 要执行的可调度对象列表
        """
        for schedulable in schedulables:
            self.execute_event(schedulable)

    def execute_event(self, schedulable: Schedulable) -> None:
        """
        执行单个可调度对象，包括更新内部逻辑、记录下次调度等

        Args:
            schedulable: 要执行的可调度对象
        """
        result = schedulable.execute()
        self.record_action(schedulable)

        if self.on_event_executed:
            self.on_event_executed(schedulable)

        # 如果需要重复调度，计算并调度下一次
        if schedulable.should_reschedule():
            current_time = self._get_time_callback()
            next_time = schedulable.calculate_next_schedule_time(current_time)
            schedulable.trigger_time = next_time
            delay = next_time - current_time
            self.schedule_with_delay(schedulable.id, schedulable, delay)

    def record_action(self, schedulable: Schedulable) -> None:
        """
        记录行动历史

        Args:
            schedulable: 执行的可调度对象
        """
        current_time = self._get_time_callback()
        record = {
            "schedulable_name": schedulable.name,
            "schedulable_type": schedulable.get_type_identifier(),
            "timestamp": current_time
        }
        self.action_history.append(record)

    def get_status_text(self) -> str:
        """
        获取系统当前状态的文本描述

        Returns:
            状态描述字符串
        """
        if not self.is_initialized:
            return "CTB系统未初始化"

        current_time = self._get_time_callback()
        active_count = sum(1 for obj in self.scheduled_objects.values() if obj.should_reschedule())

        status_lines = [
            "=== CTB系统状态 ===",
            f"  当前时间: {current_time} 小时",
            f"  对象总数: {len(self.scheduled_objects)}",
            f"  活跃对象: {active_count}"
        ]

        # 获取下一个对象
        next_events = self._peek_callback(1, 1)
        if next_events:
            next_event_data = next_events[0]
            next_obj = next_event_data["value"]
            delay = next_obj.trigger_time - current_time
            if delay <= 0:
                status_lines.append(f"  下个调度: 待执行 ({next_obj.name})")
            else:
                status_lines.append(f"  下个调度: {delay} 小时后 ({next_obj.name})")
        else:
            status_lines.append("  下个调度: (无)")

        return "\n".join(status_lines)

    def get_event_info(self) -> List[Dict[str, Any]]:
        """
        获取所有可调度对象信息

        Returns:
            包含对象信息的字典列表
        """
        info_list = []
        current_time = self._get_time_callback()

        for obj in self.scheduled_objects.values():
            info = {
                "id": obj.id,
                "name": obj.name,
                "type": obj.get_type_identifier(),
                "should_reschedule": obj.should_reschedule()
            }

            # 尝试从时间轮中获取下次调度时间
            events = self._peek_callback(1, 1)
            for event_data in events:
                if event_data["key"] == obj.id:
                    event = event_data["value"]
                    info["next_schedule_time"] = event.trigger_time
                    info["time_until_schedule"] = event.trigger_time - current_time
                    break

            # 如果是EventExample，添加额外信息
            if isinstance(obj, EventExample):
                info["faction"] = obj.faction
                info["is_active"] = obj.is_active

            info_list.append(info)

        return info_list

    def get_next_schedule_time_info(self) -> str:
        """
        获取下一个调度的时间信息

        Returns:
            时间信息字符串
        """
        next_events = self._peek_callback(1, 1)
        if not next_events:
            return "无"

        current_time = self._get_time_callback()
        next_event_data = next_events[0]
        next_obj = next_event_data["value"]
        delay = next_obj.trigger_time - current_time

        if delay <= 0:
            return "待执行"
        else:
            return f"{delay}小时后"


# 简单事件类 - 用于测试
class SimpleEvent(Schedulable):
    """简单事件类，用于测试和演示"""

    def __init__(self, id: str, description: str, trigger_time: int):
        super().__init__(id, description, description)
        self.trigger_time = trigger_time

    def execute(self) -> Any:
        print(f"执行事件: {self.description}")
        return self

    def calculate_next_schedule_time(self, current_time: int) -> int:
        return current_time  # 简单事件不重复

    def should_reschedule(self) -> bool:
        return False

    def get_type_identifier(self) -> str:
        return "SimpleEvent"