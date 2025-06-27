// [LEGACY - GDScript Primary] Original C# implementation
// This code is preserved for reference but not actively used
// See scripts/gdscript/CTBManager.gd for the primary GDScript implementation

using System;
using System.Collections.Generic;
using System.Linq;

namespace Core
{
    /// <summary>
    /// �¼�����ö��
    /// </summary>
    public enum EventType
    {
        CharacterAction,  // ��ɫ�ж�
        SeasonChange,     // ���ڱ仯
        WeatherChange,    // �����仯
        StoryEvent,       // �����¼�
        Custom            // �Զ����¼�
    }

    /// <summary>
    /// �¼�����
    /// ����CTBϵͳ�е��¼���Ӧ�̳д��ࡣ
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
        /// ִ���¼�
        /// ����Ӧ��д�˷���ʵ�־�����¼��߼���
        /// </summary>
        /// <returns>ִ�н���������������������</returns>
        public abstract object Execute();

        public override string ToString()
        {
            return $"{Name} ({EventType})";
        }
    }

    /// <summary>
    /// ��Ϸ��ɫ
    /// ��ɫ��һ��������¼�����Execute����ִ�н�ɫ���ж���
    /// </summary>
    public class Character : Event
    {
        public string Faction { get; set; }
        public bool IsActive { get; set; }

        public Character(string id, string name, string faction = "����")
            : base(id, name, EventType.CharacterAction, 0, $"{name}���ж�")
        {
            Faction = faction;
            IsActive = true;
        }

        /// <summary>
        /// �����´��ж�ʱ��
        /// ʹ�����Ƿֲ�����1-180��֮�����������
        /// ��ֵ��90�죬��������Ȼ�ķֲ���
        /// </summary>
        /// <param name="currentTime">��ǰʱ�䣨Сʱ��</param>
        /// <returns>�´��ж��ľ���ʱ�䣨Сʱ��</returns>
        public int CalculateNextActionTime(int currentTime)
        {
            // ʹ�����Ƿֲ�����С1�죬���180�죬����90��
            var random = new Random();
            double days = TriangularDistribution(random, 1, 180, 90);
            int hours = (int)(days * 24);
            return currentTime + hours;
        }

        /// <summary>
        /// ���Ƿֲ�ʵ��
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
        /// ִ�н�ɫ�ж�
        /// </summary>
        /// <returns>����������������ʽ����</returns>
        public override object Execute()
        {
            // ����������ӽ�ɫ�ж��ľ����߼�
            // ���磺����ս����ʹ�ü��ܡ��ƶ���
            return this;
        }
    }

    /// <summary>
    /// CTBϵͳ������
    /// ������������¼��ĵ��Ⱥ�ִ�У�ͨ���ص���������ʱ���֡�
    /// </summary>
    public class CTBManager
    {
        // �ص�����
        private readonly Func<int> _getTimeCallback;
        private readonly Action _advanceTimeCallback;
        private readonly Func<string, Event, int, bool> _scheduleCallback;
        private readonly Func<string, bool> _removeCallback;
        private readonly Func<int, int, List<Tuple<string, Event>>> _peekCallback;
        private readonly Func<Tuple<string, Event>> _popCallback;
        private readonly Func<bool> _isSlotEmptyCallback;

        // ״̬
        public Dictionary<string, Character> Characters { get; private set; }
        public bool IsInitialized { get; private set; }
        public List<Dictionary<string, object>> ActionHistory { get; private set; }

        // �¼�ִ�лص�
        public Action<Event> OnEventExecuted { get; set; }

        /// <summary>
        /// ��ʼ��CTB������
        /// </summary>
        /// <param name="getTimeCallback">��ȡ��ǰʱ��Ļص�����</param>
        /// <param name="advanceTimeCallback">�ƽ�ʱ��Ļص�����</param>
        /// <param name="scheduleCallback">�����¼��Ļص����� (key, event, delay) -> bool</param>
        /// <param name="removeCallback">�Ƴ��¼��Ļص����� (key) -> bool</param>
        /// <param name="peekCallback">Ԥ���¼��Ļص����� (count, max_events) -> List<Tuple<string, Event>></param>
        /// <param name="popCallback">���������¼��Ļص����� () -> Tuple<string, Event></param>
        /// <param name="isSlotEmptyCallback">���ʱ����Ƿ�Ϊ��</param>
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
        /// ���ӽ�ɫ��ϵͳ
        /// </summary>
        /// <param name="character">Ҫ���ӵĽ�ɫ</param>
        /// <exception cref="ArgumentException">�����ɫID�Ѵ���</exception>
        public void AddCharacter(Character character)
        {
            if (Characters.ContainsKey(character.Id))
            {
                throw new ArgumentException($"Character with ID {character.Id} already exists");
            }

            Characters[character.Id] = character;
        }

        /// <summary>
        /// ������һ���߼��غ�
        /// �������ʱ��ǰ����ֱ���ҵ���������һ���¼���
        /// ����CTBϵͳ�ĺ���"����"������
        /// </summary>
        /// <returns>������ִ���¼���Ϣ���ֵ�</returns>
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
        /// ��ϵͳ���Ƴ���ɫ
        /// </summary>
        /// <param name="characterId">Ҫ�Ƴ��Ľ�ɫID</param>
        /// <returns>����ɹ��Ƴ�����True�����򷵻�False</returns>
        public bool RemoveCharacter(string characterId)
        {
            if (!Characters.ContainsKey(characterId))
            {
                return false;
            }

            // ��ʱ�������Ƴ���ɫ���¼�
            _removeCallback(characterId);

            // �ӽ�ɫ�ֵ����Ƴ�
            Characters.Remove(characterId);
            return true;
        }

        /// <summary>
        /// ��ȡ��ɫ
        /// </summary>
        /// <param name="characterId">��ɫID</param>
        /// <returns>����ҵ����ؽ�ɫ�����򷵻�null</returns>
        public Character GetCharacter(string characterId)
        {
            return Characters.TryGetValue(characterId, out var character) ? character : null;
        }

        /// <summary>
        /// ��ʼ��CTBϵͳ
        /// Ϊ���н�ɫ���ų�ʼ�ж�ʱ�䡣
        /// </summary>
        /// <exception cref="InvalidOperationException">���û�н�ɫ</exception>
        public void InitializeCTB()
        {
            if (!Characters.Any())
            {
                throw new InvalidOperationException("Cannot initialize CTB without characters");
            }

            int currentTime = _getTimeCallback();

            // Ϊÿ����Ծ��ɫ���ų�ʼ�ж�
            foreach (var character in Characters.Values)
            {
                if (character.IsActive)
                {
                    // �����ʼ�ж�ʱ��
                    int nextTime = character.CalculateNextActionTime(currentTime);
                    character.TriggerTime = nextTime;

                    // ���ӵ�ʱ����
                    int delay = nextTime - currentTime;
                    _scheduleCallback(character.Id, character, delay);
                }
            }

            IsInitialized = true;
        }

        /// <summary>
        /// �����Զ����¼�
        /// </summary>
        /// <param name="event">Ҫ���ȵ��¼�</param>
        /// <param name="triggerTime">����ʱ�䣨����ʱ�䣩</param>
        /// <returns>����ɹ����ȷ���True�����򷵻�False</returns>
        public bool ScheduleEvent(Event @event, int triggerTime)
        {
            int currentTime = _getTimeCallback();
            if (triggerTime < currentTime)
            {
                return false; // �����ڹ�ȥ�����¼�
            }

            int delay = triggerTime - currentTime;
            return ScheduleWithDelay(@event.Id, @event, delay);
        }

        /// <summary>
        /// ʹ���ӳ�ʱ������¼�
        /// </summary>
        /// <param name="key">�¼���ֵ</param>
        /// <param name="event">Ҫ���ȵ��¼�</param>
        /// <param name="delay">�ӳ�ʱ�䣨Сʱ��</param>
        /// <returns>����ɹ����ȷ���True�����򷵻�False</returns>
        public bool ScheduleWithDelay(string key, Event @event, int delay)
        {
            return _scheduleCallback(key, @event, delay);
        }

        /// <summary>
        /// ��ȡ��ǰʱ�䵽�ڵ���һ���¼�
        /// </summary>
        /// <returns>���ڵ��¼������û���򷵻�null</returns>
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
        /// ִ���¼��б�
        /// </summary>
        /// <param name="events">Ҫִ�е��¼��б�</param>
        public void ExecuteEvents(List<Event> events)
        {
            foreach (var @event in events)
            {
                ExecuteEvent(@event);
            }
        }

        /// <summary>
        /// ִ�е����¼��������������߼��������µ��ȣ���
        /// </summary>
        /// <param name="event">Ҫִ�е��¼�</param>
        private void ExecuteEvent(Event @event)
        {
            var result = @event.Execute();
            RecordAction(@event);

            OnEventExecuted?.Invoke(@event);

            // ����ǽ�ɫ�ж������㲢������һ���ж�
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
        /// ��¼�ж���ʷ
        /// </summary>
        /// <param name="event">ִ�е��¼�</param>
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
        /// ���ý�ɫ�Ļ�Ծ״̬
        /// ���һ����ɫ������Ϊ����Ծ���������ᱻ������һ���ж���
        /// �������ǰ���������ж������ж��ᱻȡ����
        /// </summary>
        /// <param name="characterId">��ɫID</param>
        /// <param name="active">�Ƿ��Ծ</param>
        /// <returns>�����Ƿ�ɹ�</returns>
        public bool SetCharacterActive(string characterId, bool active)
        {
            var character = GetCharacter(characterId);
            if (character == null)
            {
                return false;
            }

            character.IsActive = active;

            // �����ɫ������Ϊ����Ծ����ʱ�������Ƴ���δ�����ж�
            if (!active)
            {
                _removeCallback(characterId);
            }
            // �����ɫ�����¼����Ҫ�ֶ�Ϊ��������һ���ж�
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
        /// ��ȡϵͳ��ǰ״̬���ı�����
        /// </summary>
        /// <returns>״̬�����ı�</returns>
        public string GetStatusText()
        {
            if (!IsInitialized)
            {
                return "CTBϵͳδ��ʼ��";
            }

            int currentTime = _getTimeCallback();
            int activeCharacters = Characters.Values.Count(c => c.IsActive);

            var statusLines = new List<string>
            {
                "=== CTBϵͳ״̬ ===",
                $"  ��ǰʱ��: {currentTime} Сʱ",
                $"  ��ɫ����: {Characters.Count}",
                $"  ��Ծ��ɫ: {activeCharacters}"
            };

            // ��ȡ��һ���¼�
            var nextEvents = _peekCallback(1, 1);
            if (nextEvents.Any())
            {
                var (key, nextEvent) = nextEvents[0];
                int delay = nextEvent.TriggerTime - currentTime;
                if (delay <= 0)
                {
                    statusLines.Add($"  �¸��ж�: ����ִ�� ({nextEvent.Name})");
                }
                else
                {
                    statusLines.Add($"  �¸��ж�: {delay} Сʱ�� ({nextEvent.Name})");
                }
            }
            else
            {
                statusLines.Add("  �¸��ж�: (��)");
            }

            return string.Join("\n", statusLines);
        }

        /// <summary>
        /// ��ȡ���н�ɫ��Ϣ
        /// </summary>
        /// <returns>��ɫ��Ϣ�б�</returns>
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

                // ���Դ�ʱ�����л�ȡ�´��ж�ʱ��
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
        /// ��ȡ��һ���ж���ʱ����Ϣ
        /// </summary>
        /// <returns>ʱ����Ϣ�ı�</returns>
        public string GetNextActionTimeInfo()
        {
            var nextEvents = _peekCallback(1, 1);
            if (!nextEvents.Any())
            {
                return "��";
            }

            int currentTime = _getTimeCallback();
            var (key, nextEvent) = nextEvents[0];
            int delay = nextEvent.TriggerTime - currentTime;

            if (delay <= 0)
            {
                return "����ִ��";
            }
            else
            {
                return $"{delay}Сʱ��";
            }
        }
    }
}