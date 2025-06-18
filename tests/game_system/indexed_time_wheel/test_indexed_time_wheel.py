import unittest
import sys
import os
import threading
import random
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from game_system.indexed_time_wheel import IndexedTimeWheel

class TestIndexedTimeWheel(unittest.TestCase):
    """Tests for the unified IndexedTimeWheel class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock time callback that returns a simple counter
        self.time_counter = 0
        self.get_time_callback = lambda: self.time_counter

    def create_wheel(self, size):
        """Helper method to create a test wheel with mock time callback."""
        return IndexedTimeWheel[str](size, self.get_time_callback)

    def test_schedule_and_remove_in_wheel(self):
        """Test scheduling with a key and removing by key from the main wheel."""
        i_wheel = self.create_wheel(10)
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
        i_wheel = self.create_wheel(10)
        i_wheel.schedule_with_delay(key="A", value="Action A", delay=0)

        self.assertIn("A", i_wheel)
        key, value = i_wheel.pop_due_event()
        self.assertEqual(key, "A")
        self.assertEqual(value, "Action A")
        self.assertNotIn("A", i_wheel)
        self.assertIsNone(i_wheel.get("A"))

    def test_duplicate_key_raises_error(self):
        """Test that scheduling with a duplicate key raises an AssertionError."""
        i_wheel = self.create_wheel(10)
        i_wheel.schedule_with_delay(key="A", value="Action A", delay=1)
        with self.assertRaises(AssertionError):
            i_wheel.schedule_with_delay(key="A", value="Another Action", delay=2)
        with self.assertRaises(AssertionError):
            i_wheel.schedule_at_absolute_hour(key="A", value="Another Action", absolute_hour=3)

    def test_peek_upcoming_events_only_sees_wheel(self):
        """Test peeking at events only returns those in the wheel, not future bucket."""
        i_wheel = self.create_wheel(10)
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
        i_wheel = self.create_wheel(20)
        i_wheel.schedule_with_delay("A", "Action A", 5)
        i_wheel.schedule_with_delay("B", "Action B", 10)
        i_wheel.schedule_with_delay("C", "Action C", 10)

        # Advance time to first event
        self.time_counter = 5
        i_wheel.update_wheel()

        # Pop the first event
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "A")

        # Advance time to next event
        self.time_counter = 10
        i_wheel.update_wheel()

        # Pop the second event
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "B")

        # Pop the third event (same time slot)
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "C")

        # No more events
        self.assertIsNone(i_wheel.pop_due_event())

    def test_fifo_for_indexed_wheel(self):
        """Test that events in the same slot are processed in FIFO order for the user."""
        i_wheel = self.create_wheel(10)
        i_wheel.schedule_with_delay("first", "First Event", 2)
        i_wheel.schedule_with_delay("second", "Second Event", 2)

        # Advance time to the events
        self.time_counter = 2
        i_wheel.update_wheel()

        key1, val1 = i_wheel.pop_due_event()
        self.assertEqual(key1, "first")

        key2, val2 = i_wheel.pop_due_event()
        self.assertEqual(key2, "second")

        self.assertIsNone(i_wheel.pop_due_event())


class TestSchedulingMethods(unittest.TestCase):
    """Tests for different scheduling methods and their validation."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock time callback that returns a simple counter
        self.time_counter = 0
        self.get_time_callback = lambda: self.time_counter

    def create_wheel(self, size):
        """Helper method to create a test wheel with mock time callback."""
        return IndexedTimeWheel[str](size, self.get_time_callback)

    def test_schedule_at_absolute_hour(self):
        """Test scheduling at a specific absolute hour."""
        i_wheel = self.create_wheel(100)

        # Manually tick internal state for test setup
        self.time_counter = 2
        i_wheel.total_ticks = 2
        i_wheel.offset = 2

        i_wheel.schedule_at_absolute_hour("A", "Absolute Event", 10)
        self.assertIn("A", i_wheel)

        # Advance time to the event
        self.time_counter = 10
        i_wheel.update_wheel()

        key, value = i_wheel.pop_due_event()
        self.assertEqual(key, "A")

    def test_absolute_and_delay_scheduling_coexist(self):
        """Test that both scheduling methods can be used together."""
        i_wheel = self.create_wheel(20)
        # Advance time by 5 ticks
        self.time_counter = 5
        i_wheel.total_ticks = 5
        i_wheel.offset = 5

        # Schedule an event 5 ticks from now (at absolute time 10)
        i_wheel.schedule_with_delay("delay_event", "Event via Delay", 5)
        # Schedule an event at absolute hour 12
        i_wheel.schedule_at_absolute_hour("abs_event", "Event via Absolute", 12)

        # Advance time to first event
        self.time_counter = 10
        i_wheel.update_wheel()
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "delay_event")

        # Advance time to second event
        self.time_counter = 12
        i_wheel.update_wheel()
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "abs_event")

    def test_schedule_in_the_past_raises_error(self):
        """Test scheduling in the past raises an AssertionError."""
        i_wheel = self.create_wheel(20)
        self.time_counter = 10
        i_wheel.total_ticks = 10
        i_wheel.offset = 10

        # Try to schedule at time 9, which is in the past
        with self.assertRaises(AssertionError):
            i_wheel.schedule_at_absolute_hour("A", "Past Event", 9)


class TestFutureEvents(unittest.TestCase):
    """Tests for future event handling (scheduling beyond one cycle)."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock time callback that returns a simple counter
        self.time_counter = 0
        self.get_time_callback = lambda: self.time_counter

    def create_wheel(self, size):
        """Helper method to create a test wheel with mock time callback."""
        return IndexedTimeWheel[str](size, self.get_time_callback)

    def test_schedule_beyond_one_cycle(self):
        """Test scheduling an event far in the future places it in the future bucket."""
        i_wheel = self.create_wheel(10)
        # current time is 0, size is 10. Scheduling at 15 should go to future_events.
        i_wheel.schedule_with_delay("A", "Future A", 15)

        self.assertIn("A", i_wheel)
        self.assertEqual(len(i_wheel.future_events), 1)
        self.assertEqual(i_wheel.future_events[0][0], 15) # Check absolute hour in heap
        self.assertEqual(i_wheel.index["A"].slot_index, -1)
        # The main wheel should be empty
        self.assertTrue(i_wheel._is_current_slot_empty())

    def test_remove_from_future_bucket(self):
        """Test removing an event from the future bucket uses direct deletion."""
        i_wheel = self.create_wheel(10)
        i_wheel.schedule_with_delay("A", "Future A", 15)

        removed_value = i_wheel.remove("A")
        self.assertEqual(removed_value, "Future A")

        # The key is gone from the index
        self.assertNotIn("A", i_wheel)
        # Future events list is now empty
        self.assertEqual(len(i_wheel.future_events), 0)

    def test_reschedule_on_tick(self):
        """Test that future events are rescheduled when their time comes."""
        i_wheel = self.create_wheel(10)
        # Schedule event at time 2. Should go into the wheel.
        i_wheel.schedule_with_delay("A", "Action A", 2)
        # Schedule another far-future event. Should go into the heap.
        i_wheel.schedule_with_delay("B", "Future B", 20)

        # Verify initial state: A is in wheel, B is in heap.
        self.assertEqual(len(i_wheel.future_events), 1)
        # Peek at the node in the tuple: (time, node)
        self.assertEqual(i_wheel.future_events[0][1].key, "B")
        self.assertNotEqual(i_wheel.index["A"].slot_index, -1)
        self.assertEqual(i_wheel.index["B"].slot_index, -1)

        # Advance time by 2 ticks to where A is.
        self.time_counter = 2
        i_wheel.update_wheel()

        # Now pop event A
        key, val = i_wheel.pop_due_event()
        self.assertEqual(key, "A")

        # Now test the future event B. Current time is 2.
        # Advance time to 20 to trigger the future event
        self.time_counter = 20
        i_wheel.update_wheel()

        self.assertEqual(len(i_wheel.future_events), 0) # B should be moved to wheel

        # B should be in the wheel but at the far end slot, not the current slot
        self.assertTrue(i_wheel._is_current_slot_empty())
        # But B should still be in the wheel
        self.assertIn("B", i_wheel)

    def test_deleted_future_event_is_not_rescheduled(self):
        """Test that a deleted future event is not rescheduled."""
        i_wheel = self.create_wheel(10)
        i_wheel.schedule_with_delay("A", "Future A", 12)
        i_wheel.schedule_with_delay("B", "Future B", 12)

        i_wheel.remove("A") # This one is immediately deleted

        # Advance time to trigger reschedule
        self.time_counter = 12
        i_wheel.update_wheel()

        self.assertEqual(len(i_wheel.future_events), 0)
        self.assertNotIn("A", i_wheel)
        self.assertIn("B", i_wheel) # B should be rescheduled

        # B should be in the wheel but at the far end slot, not the current slot
        self.assertTrue(i_wheel._is_current_slot_empty())
        # But B should still be in the wheel
        self.assertIn("B", i_wheel)

    def test_absolute_hour_scheduling_is_now_allowed(self):
        """Test scheduling an absolute hour >= total_ticks + size is now allowed."""
        i_wheel = self.create_wheel(10)
        self.time_counter = 5
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

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock time callback that returns a simple counter
        self.time_counter = 0
        self.get_time_callback = lambda: self.time_counter

    def create_wheel(self, size):
        """Helper method to create a test wheel with mock time callback."""
        return IndexedTimeWheel[int](size, self.get_time_callback)

    def test_concurrent_read_write(self):
        """
        Tests that concurrent reads and writes do not corrupt the
        TimeWheel's state or raise exceptions.
        """
        wheel_size = 100
        i_wheel = self.create_wheel(wheel_size)
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

class TestIndexedTimeWheelFeatures(unittest.TestCase):
    """Test new features like removal and far-future event scheduling."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock time callback that returns a simple counter
        self.time_counter = 0
        self.get_time_callback = lambda: self.time_counter
        self.tw = IndexedTimeWheel(100, self.get_time_callback) # Wheel with size 100

    def test_remove_scheduled_event_from_wheel(self):
        """Test removing an event that is currently in the wheel."""
        self.tw.schedule_with_delay("key1", "event1", 10)
        self.assertIn("key1", self.tw)

        removed = self.tw.remove("key1")
        self.assertTrue(removed)
        self.assertNotIn("key1", self.tw)
        self.assertIsNone(self.tw.pop_due_event())

    def test_remove_scheduled_event_from_future_heap(self):
        """Test removing an event that is in the future heap."""
        self.tw.schedule_with_delay("key2", "event2", 200) # delay > size
        self.assertIn("key2", self.tw) # __contains__ should check both

        removed = self.tw.remove("key2")
        self.assertTrue(removed)
        self.assertNotIn("key2", self.tw)

    def test_remove_nonexistent_event(self):
        """Test that removing a non-existent key returns False."""
        removed = self.tw.remove("nonexistent")
        self.assertFalse(removed)

    def test_schedule_far_future_event(self):
        """Test that events with long delays go to the future heap."""
        self.tw.schedule_with_delay("future_event", "data", 150) # delay > size
        self.assertIn("future_event", self.tw.index)
        self.assertEqual(len(self.tw.future_events), 1)

        # Verify it's not in the upcoming events from the wheel itself
        upcoming = self.tw.peek_upcoming_events(count=100)
        self.assertEqual(len(upcoming), 0)

    def test_tick_moves_future_event_to_wheel(self):
        """Test that ticking the wheel correctly moves an event from the future heap."""
        # This event will go to the future heap.
        self.tw.schedule_with_delay("future_event", "data", 110)

        # This event is on the wheel and will force the clock to advance.
        self.tw.schedule_with_delay("dummy_event", "dummy_data", 10)

        # Advance time until the dummy event.
        self.time_counter = 10
        self.tw.update_wheel()

        # Pop the dummy event
        event = self.tw.pop_due_event()
        self.assertEqual(event[0], "dummy_event")

        # At this point, total_ticks = 10, future_event is still in the heap
        self.assertEqual(len(self.tw.future_events), 1)
        self.assertEqual(self.tw.future_events[0][1].key, "future_event")

        # Advance time to 110 to trigger the future event
        self.time_counter = 110
        self.tw.update_wheel()

        # Now the future_event should have been moved into the wheel at the far end
        self.assertEqual(len(self.tw.future_events), 0)

        # It should be in the wheel but not immediately available
        # The event should be in the wheel's far end slot
        self.assertIn("future_event", self.tw)

if __name__ == '__main__':
    unittest.main(verbosity=2)