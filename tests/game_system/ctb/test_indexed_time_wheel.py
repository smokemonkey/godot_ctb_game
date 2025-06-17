import unittest
import sys
import os
import threading
import random
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from game_system.ctb.indexed_time_wheel import IndexedTimeWheel

class TestIndexedTimeWheel(unittest.TestCase):
    """Tests for the unified IndexedTimeWheel class."""

    def test_schedule_and_remove_in_wheel(self):
        """Test scheduling with a key and removing by key from the main wheel."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay(key="A", value="Action A", delay=3)
        self.assertIn("A", i_wheel)
        self.assertEqual(len(i_wheel), 1)

        removed_value = i_wheel.remove("A")
        self.assertEqual(removed_value, "Action A")
        self.assertNotIn("A", i_wheel)
        self.assertEqual(len(i_wheel), 0)
        self.assertIsNone(i_wheel.remove("A"))

    def test_pop_due_event_updates_index(self):
        """Test that popping a due event also removes it from the index."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay(key="A", value="Action A", delay=0)

        self.assertIn("A", i_wheel)
        key, value = i_wheel.pop_due_event()
        self.assertEqual(key, "A")
        self.assertEqual(value, "Action A")
        self.assertNotIn("A", i_wheel)
        self.assertIsNone(i_wheel.get("A"))

    def test_duplicate_key_raises_error(self):
        """Test that scheduling with a duplicate key raises an AssertionError."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay(key="A", value="Action A", delay=1)
        with self.assertRaises(AssertionError):
            i_wheel.schedule_with_delay(key="A", value="Another Action", delay=2)
        with self.assertRaises(AssertionError):
            i_wheel.schedule_at_absolute_hour(key="A", value="Another Action", absolute_hour=3)

    def test_peek_upcoming_events_only_sees_wheel(self):
        """Test peeking at events only returns those in the wheel, not future bucket."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay("A", "Action A", 2)
        i_wheel.schedule_with_delay("B", "Action B", 5)
        i_wheel.schedule_with_delay("C", "Future C", 15) # This is a future event

        # Peek should only see A and B
        events = i_wheel.peek_upcoming_events(count=10)

        event_keys = [key for key, val in events]
        self.assertIn("A", event_keys)
        self.assertIn("B", event_keys)
        self.assertNotIn("C", event_keys)
        self.assertEqual(len(events), 2)

        # Test max_events
        events_limited = i_wheel.peek_upcoming_events(count=10, max_events=1)
        self.assertEqual(len(events_limited), 1)
        self.assertEqual(events_limited[0][0], "A")

    def test_complex_scenario(self):
        """Test a more complex sequence of operations."""
        i_wheel = IndexedTimeWheel[str](20)
        i_wheel.schedule_with_delay("A", "Action A", 5)
        i_wheel.schedule_with_delay("B", "Action B", 10)
        i_wheel.schedule_with_delay("C", "Action C", 10)

        ticks = i_wheel.tick_till_next_event()
        self.assertEqual(ticks, 5)

        key, value = i_wheel.pop_due_event()
        self.assertEqual(key, "A")

        self.assertIsNone(i_wheel.pop_due_event())

        removed = i_wheel.remove("C")
        self.assertEqual(removed, "Action C")

        ticks = i_wheel.tick_till_next_event()
        self.assertEqual(ticks, 5)

        key, value = i_wheel.pop_due_event()
        self.assertEqual(key, "B")
        self.assertEqual(len(i_wheel), 0)

        self.assertIsNone(i_wheel.pop_due_event())

    def test_fifo_for_indexed_wheel(self):
        """Test that events in the same slot are processed in FIFO order for the user."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay("first", "First Event", 2)
        i_wheel.schedule_with_delay("second", "Second Event", 2)

        i_wheel.tick_till_next_event()

        key1, val1 = i_wheel.pop_due_event()
        self.assertEqual(key1, "first")

        key2, val2 = i_wheel.pop_due_event()
        self.assertEqual(key2, "second")

        self.assertIsNone(i_wheel.pop_due_event())


class TestSchedulingMethods(unittest.TestCase):
    """Tests for different scheduling methods and their validation."""

    def test_schedule_at_absolute_hour(self):
        """Test scheduling at a specific absolute hour."""
        i_wheel = IndexedTimeWheel[str](100)

        # Manually tick internal state for test setup
        i_wheel.total_ticks = 2
        i_wheel.offset = 2

        i_wheel.schedule_at_absolute_hour("A", "Absolute Event", 10)
        self.assertIn("A", i_wheel)

        ticks = i_wheel.tick_till_next_event()
        self.assertEqual(ticks, 8)

        key, value = i_wheel.pop_due_event()
        self.assertEqual(key, "A")

    def test_absolute_and_delay_scheduling_coexist(self):
        """Test that both scheduling methods can be used together."""
        i_wheel = IndexedTimeWheel[str](20)
        # Advance time by 5 ticks
        i_wheel.total_ticks = 5
        i_wheel.offset = 5

        # Schedule an event 5 ticks from now (at absolute time 10)
        i_wheel.schedule_with_delay("delay_event", "Event via Delay", 5)
        # Schedule an event at absolute hour 12
        i_wheel.schedule_at_absolute_hour("abs_event", "Event via Absolute", 12)

        # The next event should be the delay_event at time 10
        ticks = i_wheel.tick_till_next_event()
        self.assertEqual(ticks, 5) # 10 - 5 = 5
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "delay_event")

        # The next one should be the absolute_event at time 12
        ticks = i_wheel.tick_till_next_event()
        self.assertEqual(ticks, 2) # 12 - 10 = 2
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "abs_event")

    def test_schedule_in_the_past_raises_error(self):
        """Test scheduling in the past raises an AssertionError."""
        i_wheel = IndexedTimeWheel[str](20)
        i_wheel.total_ticks = 10
        i_wheel.offset = 10

        # Try to schedule at time 9, which is in the past
        with self.assertRaises(AssertionError):
            i_wheel.schedule_at_absolute_hour("A", "Past Event", 9)


class TestFutureEvents(unittest.TestCase):
    """Tests for future event handling (scheduling beyond one cycle)."""

    def test_schedule_beyond_one_cycle(self):
        """Test scheduling an event far in the future places it in the future bucket."""
        i_wheel = IndexedTimeWheel[str](10)
        # current time is 0, size is 10. Scheduling at 15 should go to future_events.
        i_wheel.schedule_with_delay("A", "Future A", 15)

        self.assertIn("A", i_wheel)
        self.assertEqual(len(i_wheel.future_events), 1)
        self.assertEqual(i_wheel.future_events.peek()[0], 15) # Check absolute hour in heap
        self.assertEqual(i_wheel.index["A"].slot_index, -1)
        # The main wheel should be empty
        self.assertTrue(i_wheel._is_current_slot_empty())

    def test_remove_from_future_bucket(self):
        """Test removing an event from the future bucket uses lazy deletion."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay("A", "Future A", 15)

        node = i_wheel.index["A"]
        self.assertFalse(node.deleted)

        removed_value = i_wheel.remove("A")
        self.assertEqual(removed_value, "Future A")

        # The key is gone from the index, but the node in future_events is marked
        self.assertNotIn("A", i_wheel)
        self.assertTrue(node.deleted)
        # Heap itself is not modified yet
        self.assertEqual(len(i_wheel.future_events), 1)

    def test_reschedule_on_tick(self):
        """Test that future events are rescheduled when their time comes."""
        i_wheel = IndexedTimeWheel[str](10)
        # Schedule event at time 2. Should go into the wheel.
        i_wheel.schedule_with_delay("A", "Action A", 2)
        # Schedule another far-future event. Should go into the heap.
        i_wheel.schedule_with_delay("B", "Future B", 20)

        # Verify initial state: A is in wheel, B is in heap.
        self.assertEqual(len(i_wheel.future_events), 1)
        # Peek at the node in the tuple: (time, seq, node)
        self.assertEqual(i_wheel.future_events.peek()[2].key, "B")
        self.assertNotEqual(i_wheel.index["A"].slot_index, -1)
        self.assertEqual(i_wheel.index["B"].slot_index, -1)

        # Advance time by 2 ticks to where A is.
        ticks = i_wheel.tick_till_next_event()
        self.assertEqual(ticks, 2)

        # Now pop event A
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "A")

        # Now test the future event B. Current time is 2.
        # We need to advance 17 ticks to get to time 19.
        for _ in range(17):
            # Cannot use tick_till_next_event as it would skip to the end
            self.assertTrue(i_wheel._is_current_slot_empty())
            i_wheel._tick()
        self.assertEqual(i_wheel.total_ticks, 19)

        self.assertEqual(len(i_wheel.future_events), 1) # B is still in the heap
        i_wheel._tick() # This is tick 20. B should be popped from heap and put in wheel.
        self.assertEqual(i_wheel.total_ticks, 20)
        self.assertEqual(len(i_wheel.future_events), 0)

        self.assertFalse(i_wheel._is_current_slot_empty())
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "B")

    def test_deleted_future_event_is_not_rescheduled(self):
        """Test that a deleted future event is discarded during rescheduling."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay("A", "Future A", 12)
        i_wheel.schedule_with_delay("B", "Future B", 12)

        i_wheel.remove("A") # This one is lazily deleted

        # Advance time to trigger reschedule
        for _ in range(12):
            i_wheel._tick()

        self.assertEqual(len(i_wheel.future_events), 0)
        self.assertNotIn("A", i_wheel)
        self.assertIn("B", i_wheel) # B should be rescheduled

        # The next event should be B at time 12.
        self.assertFalse(i_wheel._is_current_slot_empty())
        key, _ = i_wheel.pop_due_event()
        self.assertEqual(key, "B")

    def test_absolute_hour_scheduling_is_now_allowed(self):
        """Test scheduling an absolute hour >= total_ticks + size is now allowed."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.total_ticks = 5
        i_wheel.offset = 5

        # This should now be fine and go to future_events
        i_wheel.schedule_with_delay("A", "Action A", 10) # total_ticks=5, delay=10 -> abs_hour=15
        self.assertIn("A", i_wheel.index)
        self.assertEqual(i_wheel.index["A"].slot_index, -1)

        i_wheel.schedule_with_delay("B", "Action B", 20) # total_ticks=5, delay=20 -> abs_hour=25
        self.assertIn("B", i_wheel.index)
        self.assertEqual(i_wheel.index["B"].slot_index, -1)
        self.assertEqual(len(i_wheel.future_events), 2)


class TestIndexedTimeWheelConcurrency(unittest.TestCase):
    """Tests for thread safety in IndexedTimeWheel."""

    def test_concurrent_read_write(self):
        """
        Tests that concurrent reads and writes do not corrupt the
        TimeWheel's state or raise exceptions.
        """
        wheel_size = 100
        i_wheel = IndexedTimeWheel[int](wheel_size)
        exceptions = []

        def writer():
            """Continuously schedules and removes events."""
            for i in range(200):
                try:
                    key = f"w_event_{threading.get_ident()}_{i}"
                    delay = random.randint(0, wheel_size + 50) # Test future events too
                    i_wheel.schedule_with_delay(key, i, delay)
                    time.sleep(random.uniform(0, 0.001))
                    if random.random() > 0.5:
                        i_wheel.remove(key)
                except ValueError:
                    pass
                except Exception as e:
                    exceptions.append(e)

        def reader():
            """Continuously reads data from the time wheel."""
            for _ in range(200):
                try:
                    i_wheel.peek_upcoming_events(count=20)
                    len(i_wheel)
                    time.sleep(random.uniform(0, 0.001))
                except Exception as e:
                    exceptions.append(e)

        threads = []
        for _ in range(2):
            threads.append(threading.Thread(target=writer))
        for _ in range(2):
            threads.append(threading.Thread(target=reader))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(exceptions), 0, f"Caught exceptions in threads: {exceptions}")

if __name__ == '__main__':
    unittest.main(verbosity=2)