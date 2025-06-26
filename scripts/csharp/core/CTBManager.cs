using System;
using System.Collections.Generic;
using System.Linq;

namespace Core
{
    /// <summary>
    /// 事件类型枚举
    /// </summary>
    public enum EventType
    {
        CharacterAction,  // 角色行动
        SeasonChange,     // 季节变化
        WeatherChange,    // 天气变化
        StoryEvent,       // 剧情事件
        Custom            // 自定义事件
    }

    /// <summary>
    /// 事件基类
    /// 所有CTB系统中的事件都应继承此类。
    /// </summary>
    public abstract class Event
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public EventType EventType { get; set; }
        public int TriggerTime { get; set; }
        public string Description { get; set; }

        protected Event(string id, string name, EventType eventType, int triggerTime, string description = "")
        {
            Id = id;
            Name = name;
            EventType = eventType;
            TriggerTime = triggerTime;
            Description = description;
        }

        /// <summary>
        /// 执行事件
        /// 子类应重写此方法实现具体的事件逻辑。
        /// </summary>
        /// <returns>执行结果，具体类型由子类决定</returns>
        public abstract object Execute();

        public override string ToString()
        {
            return $"{Name} ({EventType})";
        }
    }

    /// <summary>
    /// 游戏角色
    /// 角色是一种特殊的事件，其Execute方法执行角色的行动。
    /// </summary>
    public class Character : Event
    {
        public string Faction { get; set; }
        public bool IsActive { get; set; }

        public Character(string id, string name, string faction = "中立")
            : base(id, name, EventType.CharacterAction, 0, $"{name}的行动")
        {
            Faction = faction;
            IsActive = true;
        }

        /// <summary>
        /// 计算下次行动时间
        /// 使用三角分布生成1-180天之间的随机间隔，
        /// 峰值在90天，产生更自然的分布。
        /// </summary>
        /// <param name="currentTime">当前时间（小时）</param>
        /// <returns>下次行动的绝对时间（小时）</returns>
        public int CalculateNextActionTime(int currentTime)
        {
            // 使用三角分布：最小1天，最大180天，众数90天
            var random = new Random();
            double days = TriangularDistribution(random, 1, 180, 90);
            int hours = (int)(days * 24);
            return currentTime + hours;
        }

        /// <summary>
        /// 三角分布实现
        /// </summary>
        private double TriangularDistribution(Random random, double min, double max, double mode)
        {
            double u = random.NextDouble();
            double c = (mode - min) / (max - min);

            if (u < c)
            {
                return min + Math.Sqrt(u * (max - min) * (mode - min));
            }
            else
            {
                return max - Math.Sqrt((1 - u) * (max - min) * (max - mode));
            }
        }

        /// <summary>
        /// 执行角色行动
        /// </summary>
        /// <returns>返回自身，便于链式调用</returns>
        public override object Execute()
        {
            // 这里可以添加角色行动的具体逻辑
            // 例如：触发战斗、使用技能、移动等
            return this;
        }
    }

    /// <summary>
    /// CTB系统管理器
    /// 负责管理所有事件的调度和执行，通过回调函数访问时间轮。
    /// </summary>
    public class CTBManager
    {
        // 回调函数
        private readonly Func<int> _getTimeCallback;
        private readonly Action _advanceTimeCallback;
        private readonly Func<string, Event, int, bool> _scheduleCallback;
        private readonly Func<string, bool> _removeCallback;
        private readonly Func<int, int, List<Tuple<string, Event>>> _peekCallback;
        private readonly Func<Tuple<string, Event>> _popCallback;
        private readonly Func<bool> _isSlotEmptyCallback;

        // 状态
        public Dictionary<string, Character> Characters { get; private set; }
        public bool IsInitialized { get; private set; }
        public List<Dictionary<string, object>> ActionHistory { get; private set; }

        // 事件执行回调
        public Action<Event> OnEventExecuted { get; set; }

        /// <summary>
        /// 初始化CTB管理器
        /// </summary>
        /// <param name="getTimeCallback">获取当前时间的回调函数</param>
        /// <param name="advanceTimeCallback">推进时间的回调函数</param>
        /// <param name="scheduleCallback">调度事件的回调函数 (key, event, delay) -> bool</param>
        /// <param name="removeCallback">移除事件的回调函数 (key) -> bool</param>
        /// <param name="peekCallback">预览事件的回调函数 (count, max_events) -> List<Tuple<string, Event>></param>
        /// <param name="popCallback">弹出到期事件的回调函数 () -> Tuple<string, Event></param>
        /// <param name="isSlotEmptyCallback">检查时间槽是否为空</param>
        public CTBManager(
            Func<int> getTimeCallback,
            Action advanceTimeCallback,
            Func<string, Event, int, bool> scheduleCallback,
            Func<string, bool> removeCallback,
            Func<int, int, List<Tuple<string, Event>>> peekCallback,
            Func<Tuple<string, Event>> popCallback,
            Func<bool> isSlotEmptyCallback)
        {
            _getTimeCallback = getTimeCallback;
            _advanceTimeCallback = advanceTimeCallback;
            _scheduleCallback = scheduleCallback;
            _removeCallback = removeCallback;
            _peekCallback = peekCallback;
            _popCallback = popCallback;
            _isSlotEmptyCallback = isSlotEmptyCallback;

            Characters = new Dictionary<string, Character>();
            IsInitialized = false;
            ActionHistory = new List<Dictionary<string, object>>();
        }

        /// <summary>
        /// 添加角色到系统
        /// </summary>
        /// <param name="character">要添加的角色</param>
        /// <exception cref="ArgumentException">如果角色ID已存在</exception>
        public void AddCharacter(Character character)
        {
            if (Characters.ContainsKey(character.Id))
            {
                throw new ArgumentException($"Character with ID {character.Id} already exists");
            }

            Characters[character.Id] = character;
        }

        /// <summary>
        /// 处理下一个逻辑回合
        /// 这会驱动时间前进，直到找到并处理完一个事件。
        /// 这是CTB系统的核心"引擎"方法。
        /// </summary>
        /// <returns>包含已执行事件信息的字典</returns>
        public Dictionary<string, object> ProcessNextTurn()
        {
            int ticksAdvanced = 0;
            while (_isSlotEmptyCallback())
            {
                if (ticksAdvanced > 24 * 365)
                {
                    throw new InvalidOperationException("CTBManager advanced time for over a year without finding any event.");
                }
                _advanceTimeCallback();
                ticksAdvanced++;
            }

            var dueEvent = GetDueEvent();
            if (dueEvent != null)
            {
                ExecuteEvent(dueEvent);
                return new Dictionary<string, object>
                {
                    ["type"] = "EVENT_EXECUTED",
                    ["ticks_advanced"] = ticksAdvanced,
                    ["event_id"] = dueEvent.Id,
                    ["event_name"] = dueEvent.Name,
                    ["event_type"] = dueEvent.EventType.ToString(),
                    ["timestamp"] = _getTimeCallback()
                };
            }

            throw new InvalidOperationException("Inconsistent State: Slot was not empty, but no event could be popped.");
        }

        /// <summary>
        /// 从系统中移除角色
        /// </summary>
        /// <param name="characterId">要移除的角色ID</param>
        /// <returns>如果成功移除返回True，否则返回False</returns>
        public bool RemoveCharacter(string characterId)
        {
            if (!Characters.ContainsKey(characterId))
            {
                return false;
            }

            // 从时间轮中移除角色的事件
            _removeCallback(characterId);

            // 从角色字典中移除
            Characters.Remove(characterId);
            return true;
        }

        /// <summary>
        /// 获取角色
        /// </summary>
        /// <param name="characterId">角色ID</param>
        /// <returns>如果找到返回角色，否则返回null</returns>
        public Character GetCharacter(string characterId)
        {
            return Characters.TryGetValue(characterId, out var character) ? character : null;
        }

        /// <summary>
        /// 初始化CTB系统
        /// 为所有角色安排初始行动时间。
        /// </summary>
        /// <exception cref="InvalidOperationException">如果没有角色</exception>
        public void InitializeCTB()
        {
            if (!Characters.Any())
            {
                throw new InvalidOperationException("Cannot initialize CTB without characters");
            }

            int currentTime = _getTimeCallback();

            // 为每个活跃角色安排初始行动
            foreach (var character in Characters.Values)
            {
                if (character.IsActive)
                {
                    // 计算初始行动时间
                    int nextTime = character.CalculateNextActionTime(currentTime);
                    character.TriggerTime = nextTime;

                    // 添加到时间轮
                    int delay = nextTime - currentTime;
                    _scheduleCallback(character.Id, character, delay);
                }
            }

            IsInitialized = true;
        }

        /// <summary>
        /// 调度自定义事件
        /// </summary>
        /// <param name="event">要调度的事件</param>
        /// <param name="triggerTime">触发时间（绝对时间）</param>
        /// <returns>如果成功调度返回True，否则返回False</returns>
        public bool ScheduleEvent(Event @event, int triggerTime)
        {
            int currentTime = _getTimeCallback();
            if (triggerTime < currentTime)
            {
                return false; // 不能在过去调度事件
            }

            int delay = triggerTime - currentTime;
            return ScheduleWithDelay(@event.Id, @event, delay);
        }

        /// <summary>
        /// 使用延迟时间调度事件
        /// </summary>
        /// <param name="key">事件键值</param>
        /// <param name="event">要调度的事件</param>
        /// <param name="delay">延迟时间（小时）</param>
        /// <returns>如果成功调度返回True，否则返回False</returns>
        public bool ScheduleWithDelay(string key, Event @event, int delay)
        {
            return _scheduleCallback(key, @event, delay);
        }

        /// <summary>
        /// 获取当前时间到期的下一个事件
        /// </summary>
        /// <returns>到期的事件，如果没有则返回null</returns>
        public Event GetDueEvent()
        {
            var eventTuple = _popCallback();
            if (eventTuple == null)
            {
                return null;
            }

            var (key, @event) = eventTuple;
            return @event;
        }

        /// <summary>
        /// 执行事件列表
        /// </summary>
        /// <param name="events">要执行的事件列表</param>
        public void ExecuteEvents(List<Event> events)
        {
            foreach (var @event in events)
            {
                ExecuteEvent(@event);
            }
        }

        /// <summary>
        /// 执行单个事件，并处理后续逻辑（如重新调度）。
        /// </summary>
        /// <param name="event">要执行的事件</param>
        private void ExecuteEvent(Event @event)
        {
            var result = @event.Execute();
            RecordAction(@event);

            OnEventExecuted?.Invoke(@event);

            // 如果是角色行动，计算并安排下一次行动
            if (@event.EventType == EventType.CharacterAction && @event is Character character)
            {
                if (character.IsActive)
                {
                    int currentTime = _getTimeCallback();
                    int nextTime = character.CalculateNextActionTime(currentTime);
                    character.TriggerTime = nextTime;
                    int delay = nextTime - currentTime;
                    ScheduleWithDelay(character.Id, character, delay);
                }
            }
        }

        /// <summary>
        /// 记录行动历史
        /// </summary>
        /// <param name="event">执行的事件</param>
        private void RecordAction(Event @event)
        {
            int currentTime = _getTimeCallback();
            var record = new Dictionary<string, object>
            {
                ["event_name"] = @event.Name,
                ["event_type"] = @event.EventType.ToString(),
                ["timestamp"] = currentTime
            };
            ActionHistory.Add(record);
        }

        /// <summary>
        /// 设置角色的活跃状态
        /// 如果一个角色被设置为不活跃，它将不会被安排下一次行动。
        /// 如果它当前被安排了行动，该行动会被取消。
        /// </summary>
        /// <param name="characterId">角色ID</param>
        /// <param name="active">是否活跃</param>
        /// <returns>操作是否成功</returns>
        public bool SetCharacterActive(string characterId, bool active)
        {
            var character = GetCharacter(characterId);
            if (character == null)
            {
                return false;
            }

            character.IsActive = active;

            // 如果角色被设置为不活跃，从时间轮中移除其未来的行动
            if (!active)
            {
                _removeCallback(characterId);
            }
            // 如果角色被重新激活，需要手动为他安排下一次行动
            else if (active)
            {
                int currentTime = _getTimeCallback();
                int nextTime = character.CalculateNextActionTime(currentTime);
                character.TriggerTime = nextTime;
                int delay = nextTime - currentTime;
                ScheduleWithDelay(character.Id, character, delay);
            }

            return true;
        }

        /// <summary>
        /// 获取系统当前状态的文本描述
        /// </summary>
        /// <returns>状态描述文本</returns>
        public string GetStatusText()
        {
            if (!IsInitialized)
            {
                return "CTB系统未初始化";
            }

            int currentTime = _getTimeCallback();
            int activeCharacters = Characters.Values.Count(c => c.IsActive);

            var statusLines = new List<string>
            {
                "=== CTB系统状态 ===",
                $"  当前时间: {currentTime} 小时",
                $"  角色数量: {Characters.Count}",
                $"  活跃角色: {activeCharacters}"
            };

            // 获取下一个事件
            var nextEvents = _peekCallback(1, 1);
            if (nextEvents.Any())
            {
                var (key, nextEvent) = nextEvents[0];
                int delay = nextEvent.TriggerTime - currentTime;
                if (delay <= 0)
                {
                    statusLines.Add($"  下个行动: 立即执行 ({nextEvent.Name})");
                }
                else
                {
                    statusLines.Add($"  下个行动: {delay} 小时后 ({nextEvent.Name})");
                }
            }
            else
            {
                statusLines.Add("  下个行动: (无)");
            }

            return string.Join("\n", statusLines);
        }

        /// <summary>
        /// 获取所有角色信息
        /// </summary>
        /// <returns>角色信息列表</returns>
        public List<Dictionary<string, object>> GetCharacterInfo()
        {
            var infoList = new List<Dictionary<string, object>>();
            int currentTime = _getTimeCallback();

            foreach (var character in Characters.Values)
            {
                var info = new Dictionary<string, object>
                {
                    ["id"] = character.Id,
                    ["name"] = character.Name,
                    ["faction"] = character.Faction,
                    ["is_active"] = character.IsActive
                };

                // 尝试从时间轮中获取下次行动时间
                var events = _peekCallback(1, 1);
                foreach (var (key, @event) in events)
                {
                    if (key == character.Id)
                    {
                        info["next_action_time"] = @event.TriggerTime;
                        info["time_until_action"] = @event.TriggerTime - currentTime;
                        break;
                    }
                }

                infoList.Add(info);
            }

            return infoList;
        }

        /// <summary>
        /// 获取下一个行动的时间信息
        /// </summary>
        /// <returns>时间信息文本</returns>
        public string GetNextActionTimeInfo()
        {
            var nextEvents = _peekCallback(1, 1);
            if (!nextEvents.Any())
            {
                return "无";
            }

            int currentTime = _getTimeCallback();
            var (key, nextEvent) = nextEvents[0];
            int delay = nextEvent.TriggerTime - currentTime;

            if (delay <= 0)
            {
                return "立即执行";
            }
            else
            {
                return $"{delay}小时后";
            }
        }
    }
}