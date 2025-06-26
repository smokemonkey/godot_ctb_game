using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;

namespace Core
{
    /// <summary>
    /// The interface of this file is manually decided and finalized. Do not change without explicit instructions.
    ///
    /// A Time Wheel data structure - for event scheduling in a CTB (Conditional Turn-Based) system.
    ///
    /// Core Design:
    /// - Circular Buffer: Uses a fixed-size array for an efficient time window.
    /// - Linked List Slots: Each time slot uses a list to store events that trigger at the same time.
    ///   (Note: The original Python implementation uses a List, resulting in O(N) removal. A true LinkedList would be O(1)).
    /// - Dynamic Offset: An 'offset' pointer points to the current time slot (buffer design).
    /// - Generic Support: Can store any type of event object.
    ///
    /// Buffer Design Explanation:
    /// - The slot pointed to by 'offset' is the "action buffer for the current turn".
    /// - All events in this slot should be executed immediately.
    /// - Time advances only after all events in the current slot have been executed.
    /// - In the first turn of the game, the time wheel has not advanced at all.
    /// </summary>
    public class IndexedTimeWheel<T>
    {
        /// <summary>
        /// internal node to store events within the IndexedTimeWheel.
        /// </summary>
        internal class EventNode
        {
            public object Key { get; }
            public T Value { get; }

            // When SlotIndex == -1, it indicates the event is in the _futureEvents list.
            public int SlotIndex { get; set; }
            public int? AbsoluteHour { get; }

            public EventNode(object key, T value, int slotIndex, int? absoluteHour = null)
            {
                this.Key = key;
                this.Value = value;
                this.SlotIndex = slotIndex;
                this.AbsoluteHour = absoluteHour;
            }

            public override string ToString()
            {
                return $"EventNode(Key={Key}, Value={Value})";
            }
        }

        internal readonly int _bufferSize;
        internal readonly Func<int> _getTime;

        // Core circular buffer - each slot stores a list of events.
        internal readonly List<EventNode>[] _slots;
        internal int _offset;

        // Indexing and future events
        internal readonly Dictionary<object, EventNode> _index;
        internal readonly List<(int AbsoluteHour, EventNode Node)> _futureEvents;
        internal readonly object _lock = new object();

        /// <summary>
        /// An indexed, generic time wheel data structure with support for future events.
        /// internally uses a list for each slot, providing O(1) for add/pop but O(N) for removal by key.
        /// Tracks and removes events in O(1) from the index, but removal from the slot list is O(N) where N is the number of events in that slot.
        /// </summary>
        /// <param name="bufferSize">The size of the time wheel buffer. Must be positive.</param>
        /// <param name="getTimeCallback">A function that returns the current time (in hours).</param>
        public IndexedTimeWheel(int bufferSize, Func<int> getTimeCallback)
        {
            if (bufferSize <= 0)
            {
                throw new ArgumentOutOfRangeException(nameof(bufferSize), "Time wheel size must be positive.");
            }

            _bufferSize = bufferSize;
            _getTime = getTimeCallback;

            // Initialize slots
            _slots = new List<EventNode>[_bufferSize];
            for (int i = 0; i < _bufferSize; i++)
            {
                _slots[i] = new List<EventNode>();
            }
            _offset = 0;

            _index = new Dictionary<object, EventNode>();
            _futureEvents = new List<(int, EventNode)>();
        }

        /// <summary>
        /// [��] ˽�еġ��������ĺ��ĵ��ȷ�����
        /// ���й��������ڻ�ȡ������֤�����󣬶�Ӧ���ô˷�����ִ��ʵ�ʵĵ����߼���
        /// </summary>
        private void ScheduleInternal(object key, T value, int delay, int now)
        {
            // �˷����ٶ�:
            // 1. �Ѿ����� lock ���С�
            // 2. key ��Ψһ�Ժ� delay �ķǸ����Ѿ��ɵ�������֤��
            // 3. now �������ڸոջ�ȡ�ĵ�ǰʱ�䡣

            int absoluteHour = now + delay;

            if (delay >= _bufferSize)
            {
                // ����δ���¼���
                var node = new EventNode(key, value, -1, absoluteHour);
                InsertFutureEvent(absoluteHour, node);
                _index.Add(key, node);
            }
            else
            {
                // �������ȵ�ʱ����
                int targetIndex = (_offset + delay) % _bufferSize;
                var node = new EventNode(key, value, targetIndex, absoluteHour);
                InsertToWheel(node, targetIndex);
                _index.Add(key, node);
            }
        }

        /// <summary>
        /// [���ع�] ������ӳٺ����¼���������һ���̰߳�ȫ�İ�װ����
        /// </summary>
        public void ScheduleWithDelay(object key, T value, int delay)
        {
            lock (_lock)
            {
                if (_index.ContainsKey(key))
                {
                    throw new ArgumentException($"Key '{key}' already exists.", nameof(key));
                }
                if (delay < 0)
                {
                    throw new ArgumentOutOfRangeException(nameof(delay), "Delay must be non-negative.");
                }

                int now = _getTime();
                ScheduleInternal(key, value, delay, now);
            }
            // TODO: Notify UI to re-render after data changes.
        }

        /// <summary>
        /// [���ع�] ��ָ���ľ���ʱ��㰲���¼����޸���ԭ�еľ�̬�������⡣
        /// </summary>
        public void ScheduleAtAbsoluteHour(object key, T value, int absoluteHour)
        {
            lock (_lock)
            {
                int now = _getTime();
                if (absoluteHour < now)
                {
                    throw new ArgumentOutOfRangeException(nameof(absoluteHour), "Cannot schedule in the past.");
                }
                if (_index.ContainsKey(key))
                {
                    throw new ArgumentException($"Key '{key}' already exists.", nameof(key));
                }

                int delay = absoluteHour - now;
                ScheduleInternal(key, value, delay, now);
            }
            // TODO: Notify UI to re-render after data changes.
        }

        /// <summary>
        /// Inserts an event node into the specified target index slot.
        /// </summary>
        internal void InsertToWheel(EventNode eventNode, int targetIndex)
        {
            _slots[targetIndex].Add(eventNode);
        }

        /// <summary>
        /// Inserts a future event into the list, finding the correct sorted position by iterating backwards.
        /// </summary>
        internal void InsertFutureEvent(int absoluteHour, EventNode node)
        {
            // Find insertion point from the end of the list.
            int insertIndex = 0;
            for (int i = _futureEvents.Count - 1; i >= 0; i--)
            {
                if (_futureEvents[i].AbsoluteHour <= absoluteHour)
                {
                    insertIndex = i + 1;
                    break;
                }
            }

            // Insert at the correct position to maintain sort order.
            _futureEvents.Insert(insertIndex, (absoluteHour, node));
        }

        /// <summary>
        /// Checks if the current time slot is empty.
        /// </summary>
        internal bool IsCurrentSlotEmpty() => _slots[_offset].Count == 0;

        /// <summary>
        /// Pops a due event from the head of the current time slot.
        /// </summary>
        /// <returns>A tuple containing the key and value of the event, or null if the current slot is empty.</returns>
        public (object Key, T Value)? PopDueEvent()
        {
            lock (_lock)
            {
                if (IsCurrentSlotEmpty())
                {
                    return null;
                }

                EventNode nodeToPop = _slots[_offset][0];
                _slots[_offset].RemoveAt(0);

                _index.Remove(nodeToPop.Key);

                // TODO: Notify UI to re-render after data changes.
                return (nodeToPop.Key, nodeToPop.Value);
            }
        }

        /// <summary>
        /// Advances the time wheel state: updates the offset and moves upcoming future events into the main wheel.
        /// </summary>
        public void AdvanceWheel()
        {
            lock (_lock)
            {

                if (!IsCurrentSlotEmpty())
                {
                    throw new InvalidOperationException("Cannot advance wheel: current slot is not empty.");
                }

                // Advance the offset by one position.
                _offset = (_offset + 1) % _bufferSize;

                // Check if any future events need to be moved to the main wheel.
                // Since the list is sorted by absolute_hour, we only need to check the first element.
                // Only move events when they are within the range of current_time + buffer_size - 1.
                int timeThreshold = _getTime() + _bufferSize - 1;
                while (_futureEvents.Count > 0 && _futureEvents[0].AbsoluteHour <= timeThreshold)
                {
                    var (absoluteHour, node) = _futureEvents[0];
                    _futureEvents.RemoveAt(0);

                    Debug.Assert(absoluteHour == timeThreshold, "This event should have been handled earlier.");

                    // Insert the due future event into the farthest slot of the time wheel (offset - 1).
                    // This way, the event will be triggered at the correct time as the wheel turns.
                    int targetIndex = (_offset - 1 + _bufferSize) % _bufferSize;
                    node.SlotIndex = targetIndex;
                    InsertToWheel(node, targetIndex);
                }

                Debug.Assert(_futureEvents.Count == 0 || _futureEvents[0].AbsoluteHour > _getTime(), "Future events are not correctly ordered.");
            }
        }

        /// <summary>
        /// Removes an event from the time wheel or the future events list.
        /// </summary>
        /// <param name="key">The key of the event to remove.</param>
        /// <returns>The value of the removed event, or the default value of T if the key is not found.</returns>
        public T Remove(object key)
        {
            lock (_lock)
            {
                if (!_index.TryGetValue(key, out EventNode nodeToRemove))
                {
                    return default;
                }

                // Case 1: Event is in the future pool, remove it directly from the list.
                if (nodeToRemove.SlotIndex == -1)
                {
                    // Remove from the future events list.
                    _futureEvents.RemoveAll(tuple => tuple.Node.Key.Equals(key));
                }
                // Case 2: Event is in the time wheel, remove it from the corresponding slot's list.
                else
                {
                    _slots[nodeToRemove.SlotIndex].RemoveAll(node => node.Key.Equals(key));
                }

                _index.Remove(key);
                // TODO: Notify UI to re-render after data changes.
                return nodeToRemove.Value;
            }
        }

        /// <summary>
        /// [For UI Rendering Only] Previews upcoming events within the next 'count' hours.
        ///
        /// Important: This method is designed for UI display or debugging and should not be used for core game loop logic.
        /// It may return imprecise or incomplete event data for UI convenience.
        /// The game loop should use AdvanceWheel() and PopDueEvent().
        /// </summary>
        /// <param name="count">The number of hours to preview.</param>
        /// <param name="maxEvents">The maximum number of events to return.</param>
        /// <returns>A list of tuples, each containing the key and value of an upcoming event.</returns>
        public List<(object Key, T Value)> PeekUpcomingEvents(int count, int? maxEvents = null)
        {
            lock (_lock)
            {
                var events = new List<(object, T)>();
                for (int i = 0; i < count; i++)
                {
                    int index = (_offset + i) % _bufferSize;
                    List<EventNode> currentNodes = _slots[index];
                    foreach (var node in currentNodes)
                    {
                        events.Add((node.Key, node.Value));
                    }

                    if (maxEvents.HasValue && events.Count >= maxEvents.Value)
                    {
                        return events.Take(maxEvents.Value).ToList();
                    }
                }

                // TODO: In extreme cases, read events from _futureEvents as well.
                return events;
            }
        }

        /// <summary>
        /// Gets the value of a scheduled event by its key.
        /// </summary>
        /// <param name="key">The key of the event.</param>
        /// <returns>The value of the event, or the default value of T if not found.</returns>
        public T Get(object key)
        {
            lock (_lock)
            {
                if (_index.TryGetValue(key, out EventNode node))
                {
                    return node.Value;
                }
                return default;
            }
        }

        /// <summary>
        /// Checks if a key exists in the time wheel.
        /// </summary>
        public bool Contains(object key)
        {
            lock (_lock)
            {
                return _index.ContainsKey(key);
            }
        }

        /// <summary>
        /// Returns the total number of scheduled events.
        /// </summary>
        public int Count
        {
            get
            {
                lock (_lock)
                {
                    return _index.Count;
                }
            }
        }

        /// <summary>
        /// Checks if there are any events in the time wheel or in the future events list.
        /// </summary>
        /// <returns>True if there are any events, otherwise false.</returns>
        public bool HasAnyEvents()
        {
            lock (_lock)
            {
                return _index.Count > 0;
            }
        }
    }
}