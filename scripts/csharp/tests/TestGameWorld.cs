using System;
using System.Collections.Generic;
using System.Linq;
using Core;

namespace Tests
{
    /// <summary>
    /// 专门用于集成测试的游戏世界协调器
    /// 
    /// 设计目标：
    /// - 统一时间源：Calendar是唯一的时间源
    /// - 自动同步：组件间通过回调自动保持同步
    /// - 简化接口：专注于测试需求，不包含完整游戏逻辑
    /// - 事件驱动：模拟基本的事件调度机制
    /// </summary>
    public class TestGameWorld
    {
        // Core components - Calendar是唯一时间源
        private Calendar _calendar;
        private IndexedTimeWheel<string> _timeWheel;
        
        // Simple event system for testing
        public event Action<string> OnEventExecuted;
        public event Action<int> OnTimeAdvanced;
        public event Action OnSystemsUpdated;
        
        // Configuration
        private readonly int _timeWheelSize;
        
        public TestGameWorld(int timeWheelSize = 180)
        {
            _timeWheelSize = timeWheelSize;
            InitializeComponents();
        }
        
        private void InitializeComponents()
        {
            // 1. Initialize Calendar as the single source of time
            _calendar = new Calendar();
            
            // 2. Initialize TimeWheel with callback to Calendar
            _timeWheel = new IndexedTimeWheel<string>(
                bufferSize: _timeWheelSize,
                getTimeCallback: () => _calendar.GetTimestamp()
            );
        }
        
        // ==================== Public API ====================
        
        /// <summary>
        /// 推进时间指定小时数
        /// 这是唯一的时间推进方法，确保所有组件同步
        /// </summary>
        public TimeAdvanceResult AdvanceTime(int hours)
        {
            if (hours <= 0) 
                throw new ArgumentException("Hours must be positive");
                
            var result = new TimeAdvanceResult
            {
                HoursAdvanced = hours,
                EventsExecuted = new List<string>(),
                StartTime = _calendar.GetTimestamp(),
                StartCalendarTime = _calendar.FormatDateGregorian(true)
            };
            
            // Advance time hour by hour to process events
            for (int i = 0; i < hours; i++)
            {
                // 1. Advance Calendar (single source of time)
                _calendar.AdvanceTimeTick();
                
                // 2. Process any events that become due
                ProcessDueEventsAtCurrentTime(result.EventsExecuted);
                
                // 3. Advance TimeWheel to next slot
                _timeWheel.AdvanceWheel();
            }
            
            result.EndTime = _calendar.GetTimestamp();
            result.EndCalendarTime = _calendar.FormatDateGregorian(true);
            
            // Notify listeners
            OnTimeAdvanced?.Invoke(hours);
            OnSystemsUpdated?.Invoke();
            
            return result;
        }
        
        /// <summary>
        /// 推进时间直到下一个事件被执行
        /// </summary>
        public TimeAdvanceResult AdvanceToNextEvent(int maxHours = 100)
        {
            int hoursAdvanced = 0;
            var executedEvents = new List<string>();
            var startTime = _calendar.GetTimestamp();
            var startCalendarTime = _calendar.FormatDateGregorian(true);
            
            for (int i = 0; i < maxHours; i++)
            {
                // Check if current slot has events
                if (!_timeWheel.IsCurrentSlotEmpty())
                {
                    // Process events at current time
                    ProcessDueEventsAtCurrentTime(executedEvents);
                    break;
                }
                
                // Advance time if no events
                _calendar.AdvanceTimeTick();
                _timeWheel.AdvanceWheel();
                hoursAdvanced++;
            }
            
            var result = new TimeAdvanceResult
            {
                HoursAdvanced = hoursAdvanced,
                EventsExecuted = executedEvents,
                StartTime = startTime,
                EndTime = _calendar.GetTimestamp(),
                StartCalendarTime = startCalendarTime,
                EndCalendarTime = _calendar.FormatDateGregorian(true)
            };
            
            if (hoursAdvanced > 0)
            {
                OnTimeAdvanced?.Invoke(hoursAdvanced);
                OnSystemsUpdated?.Invoke();
            }
            
            return result;
        }
        
        /// <summary>
        /// 调度事件
        /// </summary>
        public void ScheduleEvent(string key, string eventDescription, int delayHours)
        {
            _timeWheel.ScheduleWithDelay(key, eventDescription, delayHours);
            OnSystemsUpdated?.Invoke();
        }
        
        /// <summary>
        /// 移除事件
        /// </summary>
        public bool RemoveEvent(string key)
        {
            var removedEvent = _timeWheel.Remove(key);
            bool removed = removedEvent != null;
            if (removed)
            {
                OnSystemsUpdated?.Invoke();
            }
            return removed;
        }
        
        /// <summary>
        /// 获取即将到来的事件
        /// </summary>
        public List<(string Key, string Value)> GetUpcomingEvents(int maxLookAhead = 50, int maxEvents = 20)
        {
            var events = _timeWheel.PeekUpcomingEvents(maxLookAhead, maxEvents);
            return events.Select(e => (e.Key.ToString(), e.Value)).ToList();
        }
        
        /// <summary>
        /// 清空所有事件
        /// </summary>
        public void ClearAllEvents()
        {
            _timeWheel = new IndexedTimeWheel<string>(
                bufferSize: _timeWheelSize,
                getTimeCallback: () => _calendar.GetTimestamp()
            );
            OnSystemsUpdated?.Invoke();
        }
        
        /// <summary>
        /// 重置到初始状态
        /// </summary>
        public void Reset()
        {
            _calendar.Reset();
            ClearAllEvents();
            OnSystemsUpdated?.Invoke();
        }
        
        // ==================== Properties ====================
        
        public Calendar Calendar => _calendar;
        public IndexedTimeWheel<string> TimeWheel => _timeWheel;
        
        public int CurrentTime => _calendar.GetTimestamp();
        public string CurrentCalendarTime => _calendar.FormatDateGregorian(true);
        public string CurrentEraTime => _calendar.FormatDateEra(true);
        
        public int EventCount => _timeWheel.Count;
        public bool HasAnyEvents => _timeWheel.HasAnyEvents();
        public bool IsCurrentSlotEmpty => _timeWheel.IsCurrentSlotEmpty();
        
        // ==================== Calendar Operations ====================
        
        public void AnchorEra(string eraName, int gregorianYear)
        {
            _calendar.AnchorEra(eraName, gregorianYear);
            OnSystemsUpdated?.Invoke();
        }
        
        public void StartNewEra(string eraName)
        {
            _calendar.StartNewEra(eraName);
            OnSystemsUpdated?.Invoke();
        }
        
        public Dictionary<string, object> GetCalendarInfo()
        {
            return _calendar.GetTimeInfo();
        }
        
        // ==================== Private Methods ====================
        
        private void ProcessDueEventsAtCurrentTime(List<string> executedEvents)
        {
            while (!_timeWheel.IsCurrentSlotEmpty())
            {
                var dueEvent = _timeWheel.PopDueEvent();
                if (dueEvent.HasValue)
                {
                    var eventDescription = dueEvent.Value.Value;
                    executedEvents.Add(eventDescription);
                    OnEventExecuted?.Invoke(eventDescription);
                }
                else
                {
                    break; // No more events
                }
            }
        }
        
        // ==================== Test Utilities ====================
        
        /// <summary>
        /// 添加测试事件的便捷方法
        /// </summary>
        public void AddTestEvents()
        {
            var characters = new[] { "张飞", "关羽", "刘备", "曹操", "孙权" };
            var actions = new[] { "攻击", "防御", "技能", "移动", "休息" };
            var random = new Random();
            
            foreach (var character in characters)
            {
                var action = actions[random.Next(actions.Length)];
                var delay = random.Next(1, 50);
                ScheduleEvent($"{character}_{action}", $"{character}执行{action}", delay);
            }
            
            // Add some long-term events
            ScheduleEvent("春节", "春节庆典", 200);
            ScheduleEvent("中秋", "中秋节庆典", 300);
        }
        
        /// <summary>
        /// 获取系统状态摘要
        /// </summary>
        public string GetStatusSummary()
        {
            return $"时间: {CurrentTime}h | 事件: {EventCount} | 日历: {CurrentCalendarTime}";
        }
    }
    
    /// <summary>
    /// 时间推进结果
    /// </summary>
    public class TimeAdvanceResult
    {
        public int HoursAdvanced { get; set; }
        public List<string> EventsExecuted { get; set; } = new List<string>();
        public int StartTime { get; set; }
        public int EndTime { get; set; }
        public string StartCalendarTime { get; set; }
        public string EndCalendarTime { get; set; }
        
        public string Summary => 
            $"推进{HoursAdvanced}小时，执行{EventsExecuted.Count}个事件，从{StartCalendarTime}到{EndCalendarTime}";
    }
}