using System;
using System.Collections.Generic;
using Godot;
using Core;

public static class IndexedTimeWheelValidator
{
    public static List<string> RunAllTests()
    {
        var results = new List<string>();
        int testsPassed = 0;
        int testsTotal = 0;

        // Test 1: Basic scheduling and popping
        testsTotal++;
        try
        {
            var timeCounter = 0;
            var wheel = new IndexedTimeWheel<string>(10, () => timeCounter);
            
            wheel.ScheduleWithDelay("test1", "First Event", 2);
            
            if (!wheel.Contains("test1"))
                throw new Exception("Event not found after scheduling");
                
            if (wheel.Count != 1)
                throw new Exception($"Expected count 1, got {wheel.Count}");
                
            // Advance time to event
            timeCounter = 1;
            wheel.AdvanceWheel();
            timeCounter = 2;
            wheel.AdvanceWheel();
            
            var result = wheel.PopDueEvent();
            if (!result.HasValue || result.Value.Key.ToString() != "test1")
                throw new Exception("Failed to pop correct event");
                
            results.Add("✓ Test 1 PASSED: Basic scheduling and popping");
            testsPassed++;
        }
        catch (Exception e)
        {
            results.Add($"✗ Test 1 FAILED: {e.Message}");
        }

        // Test 2: Future events
        testsTotal++;
        try
        {
            var timeCounter = 0;
            var wheel = new IndexedTimeWheel<string>(5, () => timeCounter);
            
            // Schedule beyond buffer size
            wheel.ScheduleWithDelay("future", "Future Event", 10);
            
            if (!wheel.Contains("future"))
                throw new Exception("Future event not found");
                
            if (wheel.Count != 1)
                throw new Exception($"Expected count 1, got {wheel.Count}");
                
            // Advance time partially (future event should not be available yet)
            for (int i = 0; i < 5; i++)
            {
                timeCounter++;
                if (!wheel.IsCurrentSlotEmpty())
                    wheel.AdvanceWheel();
                else
                    wheel.AdvanceWheel();
            }
            
            var prematureResult = wheel.PopDueEvent();
            if (prematureResult.HasValue)
                throw new Exception("Future event was available too early");
                
            results.Add("✓ Test 2 PASSED: Future events");
            testsPassed++;
        }
        catch (Exception e)
        {
            results.Add($"✗ Test 2 FAILED: {e.Message}");
        }

        // Test 3: Multiple events same time
        testsTotal++;
        try
        {
            var timeCounter = 0;
            var wheel = new IndexedTimeWheel<string>(10, () => timeCounter);
            
            wheel.ScheduleWithDelay("event1", "First", 3);
            wheel.ScheduleWithDelay("event2", "Second", 3);
            
            if (wheel.Count != 2)
                throw new Exception($"Expected count 2, got {wheel.Count}");
                
            // Advance to events
            for (int i = 0; i < 3; i++)
            {
                timeCounter++;
                wheel.AdvanceWheel();
            }
            
            var first = wheel.PopDueEvent();
            var second = wheel.PopDueEvent();
            var third = wheel.PopDueEvent();
            
            if (!first.HasValue || !second.HasValue || third.HasValue)
                throw new Exception("Expected exactly 2 events");
                
            results.Add("✓ Test 3 PASSED: Multiple events same time");
            testsPassed++;
        }
        catch (Exception e)
        {
            results.Add($"✗ Test 3 FAILED: {e.Message}");
        }

        // Test 4: Remove operations
        testsTotal++;
        try
        {
            var timeCounter = 0;
            var wheel = new IndexedTimeWheel<string>(10, () => timeCounter);
            
            wheel.ScheduleWithDelay("remove_me", "Data", 5);
            wheel.ScheduleWithDelay("keep_me", "Keep", 5);
            
            if (wheel.Count != 2)
                throw new Exception($"Expected count 2, got {wheel.Count}");
                
            var removed = wheel.Remove("remove_me");
            if (removed != "Data")
                throw new Exception("Remove returned wrong value");
                
            if (wheel.Count != 1)
                throw new Exception($"Expected count 1 after removal, got {wheel.Count}");
                
            if (wheel.Contains("remove_me"))
                throw new Exception("Removed event still found");
                
            results.Add("✓ Test 4 PASSED: Remove operations");
            testsPassed++;
        }
        catch (Exception e)
        {
            results.Add($"✗ Test 4 FAILED: {e.Message}");
        }

        // Test 5: HasAnyEvents functionality
        testsTotal++;
        try
        {
            var timeCounter = 0;
            var wheel = new IndexedTimeWheel<string>(10, () => timeCounter);
            
            if (wheel.HasAnyEvents())
                throw new Exception("Empty wheel should have no events");
                
            wheel.ScheduleWithDelay("test", "data", 5);
            
            if (!wheel.HasAnyEvents())
                throw new Exception("Wheel with events should return true");
                
            wheel.Remove("test");
            
            if (wheel.HasAnyEvents())
                throw new Exception("Wheel should be empty after removing all events");
                
            results.Add("✓ Test 5 PASSED: HasAnyEvents functionality");
            testsPassed++;
        }
        catch (Exception e)
        {
            results.Add($"✗ Test 5 FAILED: {e.Message}");
        }

        // Summary
        results.Add("");
        results.Add($"Test Summary: {testsPassed}/{testsTotal} tests passed");
        
        if (testsPassed == testsTotal)
        {
            results.Add("🎉 All tests PASSED! IndexedTimeWheel is working correctly.");
        }
        else
        {
            results.Add("❌ Some tests FAILED. Check implementation.");
        }

        return results;
    }
}