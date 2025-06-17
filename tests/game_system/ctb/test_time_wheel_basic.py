import unittest
import sys
import os
import threading
import random
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from game_system.ctb.time_wheel import TimeWheel, IndexedTimeWheel

class TestTimeWheel(unittest.TestCase):
    """Tests for the base TimeWheel class."""

    def test_schedule_and_pop_due_event(self):
        """Test scheduling events and popping them when they are due."""
        wheel = TimeWheel[object](10)
        class SimpleNode:
            def __init__(self, value):
                self.value = value
                self.prev = None
                self.next = None
            def __repr__(self): return f"Node({self.value})"
            def __eq__(self, other): return isinstance(other, SimpleNode) and self.value == other.value

        node_a = SimpleNode("A")
        node_b = SimpleNode("B")
        node_c = SimpleNode("C")

        wheel.schedule_with_delay(node_a, 0)
        wheel.schedule_with_delay(node_b, 0)
        wheel.schedule_with_delay(node_c, 5)

        self.assertFalse(wheel._is_current_slot_empty())
        self.assertEqual(wheel.pop_due_event(), node_a)
        self.assertEqual(wheel.pop_due_event(), node_b)
        self.assertTrue(wheel._is_current_slot_empty())
        self.assertIsNone(wheel.pop_due_event())

    def test_tick_and_time_advancement(self):
        """Test that tick advances time and respects the non-empty slot rule."""
        wheel = TimeWheel(10)
        class SimpleNode:
            def __init__(self, value):
                self.value = value
                self.prev = None
                self.next = None

        node_a = SimpleNode("A")
        wheel.schedule_with_delay(node_a, 1)

        self.assertTrue(wheel._is_current_slot_empty())
        wheel._tick() # Advance to slot 1

        self.assertFalse(wheel._is_current_slot_empty())
        with self.assertRaises(RuntimeError):
            wheel._tick()

        self.assertIsNotNone(wheel.pop_due_event())
        self.assertTrue(wheel._is_current_slot_empty())

        wheel._tick()
        self.assertEqual(wheel.offset, 2)

    def test_tick_till_next_event(self):
        """Test skipping empty slots to the next event."""
        # This is better tested with IndexedTimeWheel as it's more user-facing.
        # We will rely on the IndexedTimeWheel tests for this.
        pass

    def test_peek_upcoming_events(self):
        """Test peeking at future events without altering the wheel's state."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay("A", "Action A", 0)
        i_wheel.schedule_with_delay("B", "Action B", 2)
        i_wheel.schedule_with_delay("C", "Action C", 2)
        i_wheel.schedule_with_delay("D", "Action D", 5)

        events = i_wheel.peek_upcoming_events(count=3)
        self.assertEqual([val for key, val in events], ["Action A", "Action B", "Action C"])

        events = i_wheel.peek_upcoming_events(count=10, max_events=2)
        self.assertEqual([val for key, val in events], ["Action A", "Action B"])

        key, val = i_wheel.pop_due_event()
        self.assertEqual(val, "Action A")

class TestIndexedTimeWheel(unittest.TestCase):
    """Tests for the IndexedTimeWheel wrapper."""

    def test_schedule_and_remove(self):
        """Test scheduling with a key and removing by key."""
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
        """Test that scheduling with a duplicate key raises a ValueError."""
        i_wheel = IndexedTimeWheel[str](10)
        i_wheel.schedule_with_delay(key="A", value="Action A", delay=1)
        with self.assertRaises(ValueError):
            i_wheel.schedule_with_delay(key="A", value="Another Action", delay=2)
        with self.assertRaises(ValueError):
            i_wheel.schedule_at_absolute_hour(key="A", value="Another Action", absolute_hour=3)

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

        i_wheel.time_wheel._tick()
        i_wheel.time_wheel._tick()
        self.assertEqual(i_wheel.time_wheel.offset, 2)

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
        for _ in range(5):
            i_wheel.time_wheel._tick()
        self.assertEqual(i_wheel.time_wheel.total_ticks, 5)

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

    def test_delay_greater_than_size_raises_error(self):
        """Test scheduling with a delay >= size raises ValueError."""
        i_wheel = IndexedTimeWheel[str](10)
        with self.assertRaisesRegex(ValueError, "must be less than the time wheel size"):
            i_wheel.schedule_with_delay("A", "Action A", 10)
        with self.assertRaisesRegex(ValueError, "must be less than the time wheel size"):
            i_wheel.schedule_with_delay("B", "Action B", 11)

    def test_absolute_hour_too_far_raises_error(self):
        """Test scheduling an absolute hour >= total_ticks + size raises ValueError."""
        i_wheel = IndexedTimeWheel[str](10)
        for _ in range(5):
            i_wheel.time_wheel._tick()
        self.assertEqual(i_wheel.time_wheel.total_ticks, 5)

        # This should be fine, current time is 5, size is 10. Can schedule up to time 14.
        i_wheel.schedule_at_absolute_hour("A", "Action A", 14)

        # This should fail
        with self.assertRaisesRegex(ValueError, "more than one wheel cycle"):
            i_wheel.schedule_at_absolute_hour("B", "Action B", 15) # 5 + 10
        with self.assertRaisesRegex(ValueError, "more than one wheel cycle"):
            i_wheel.schedule_at_absolute_hour("C", "Action C", 16)

    def test_schedule_in_the_past_raises_error(self):
        """Test scheduling in the past raises ValueError."""
        i_wheel = IndexedTimeWheel[str](20)
        for _ in range(10):
            i_wheel.time_wheel._tick()
        self.assertEqual(i_wheel.time_wheel.total_ticks, 10)

        # Try to schedule at time 9, which is in the past
        with self.assertRaisesRegex(ValueError, "Cannot schedule in the past"):
            i_wheel.schedule_at_absolute_hour("A", "Past Event", 9)


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
                    delay = random.randint(0, wheel_size - 1)
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