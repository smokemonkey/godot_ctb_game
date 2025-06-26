using System;
using Godot;
using Core;

public partial class TestIndexedTimeWheel : Node
{
    private IndexedTimeWheel<string> _timeWheel;
    private int _currentTime = 0;
    private Label _statusLabel;
    private VBoxContainer _eventsContainer;
    private Button _addEventButton;
    private Button _advanceTimeButton;
    private Button _popEventButton;
    private LineEdit _keyInput;
    private LineEdit _valueInput;
    private LineEdit _delayInput;

    public override void _Ready()
    {
        GD.Print("Initializing IndexedTimeWheel Test Scene");
        
        // Initialize the time wheel with a callback that returns our current time
        _timeWheel = new IndexedTimeWheel<string>(10, () => _currentTime);
        
        SetupUI();
        UpdateDisplay();
    }

    private void SetupUI()
    {
        // Find or create the main container
        var scrollContainer = GetNode<ScrollContainer>("ScrollContainer");
        var marginContainer = scrollContainer.GetNode<MarginContainer>("MarginContainer");
        
        // Create main container
        var vbox = new VBoxContainer();
        marginContainer.AddChild(vbox);

        // Status label
        _statusLabel = new Label();
        _statusLabel.Text = "IndexedTimeWheel Test - Ready";
        vbox.AddChild(_statusLabel);

        // Current time display
        var timeLabel = new Label();
        timeLabel.Text = $"Current Time: {_currentTime}";
        timeLabel.Name = "TimeLabel";
        vbox.AddChild(timeLabel);

        // Input section
        var inputContainer = new HBoxContainer();
        vbox.AddChild(inputContainer);

        inputContainer.AddChild(new Label { Text = "Key:" });
        _keyInput = new LineEdit();
        _keyInput.PlaceholderText = "event_key";
        _keyInput.CustomMinimumSize = new Vector2(100, 0);
        inputContainer.AddChild(_keyInput);

        inputContainer.AddChild(new Label { Text = "Value:" });
        _valueInput = new LineEdit();
        _valueInput.PlaceholderText = "event_data";
        _valueInput.CustomMinimumSize = new Vector2(100, 0);
        inputContainer.AddChild(_valueInput);

        inputContainer.AddChild(new Label { Text = "Delay:" });
        _delayInput = new LineEdit();
        _delayInput.PlaceholderText = "5";
        _delayInput.CustomMinimumSize = new Vector2(60, 0);
        inputContainer.AddChild(_delayInput);

        // Buttons
        var buttonContainer = new HBoxContainer();
        vbox.AddChild(buttonContainer);

        _addEventButton = new Button();
        _addEventButton.Text = "Add Event";
        _addEventButton.Pressed += OnAddEvent;
        buttonContainer.AddChild(_addEventButton);

        _advanceTimeButton = new Button();
        _advanceTimeButton.Text = "Advance Time";
        _advanceTimeButton.Pressed += OnAdvanceTime;
        buttonContainer.AddChild(_advanceTimeButton);

        _popEventButton = new Button();
        _popEventButton.Text = "Pop Due Event";
        _popEventButton.Pressed += OnPopEvent;
        buttonContainer.AddChild(_popEventButton);

        // Test buttons
        var testContainer = new HBoxContainer();
        vbox.AddChild(testContainer);

        var testBasicButton = new Button();
        testBasicButton.Text = "Test Basic Operations";
        testBasicButton.Pressed += OnTestBasic;
        testContainer.AddChild(testBasicButton);

        var testFutureButton = new Button();
        testFutureButton.Text = "Test Future Events";
        testFutureButton.Pressed += OnTestFuture;
        testContainer.AddChild(testFutureButton);

        var clearButton = new Button();
        clearButton.Text = "Clear All";
        clearButton.Pressed += OnClearAll;
        testContainer.AddChild(clearButton);

        var validateButton = new Button();
        validateButton.Text = "Run Validation Tests";
        validateButton.Pressed += OnRunValidation;
        testContainer.AddChild(validateButton);

        // Events display
        vbox.AddChild(new Label { Text = "Upcoming Events:" });
        _eventsContainer = new VBoxContainer();
        vbox.AddChild(_eventsContainer);
    }

    private void OnAddEvent()
    {
        try
        {
            string key = _keyInput.Text.Trim();
            string value = _valueInput.Text.Trim();
            int delay = int.Parse(_delayInput.Text.Trim());

            if (string.IsNullOrEmpty(key))
            {
                key = $"event_{DateTime.Now.Ticks}";
            }
            if (string.IsNullOrEmpty(value))
            {
                value = $"data_{key}";
            }

            _timeWheel.ScheduleWithDelay(key, value, delay);
            _statusLabel.Text = $"Added event '{key}' with delay {delay}";
            
            // Clear inputs
            _keyInput.Text = "";
            _valueInput.Text = "";
            _delayInput.Text = "";
            
            UpdateDisplay();
        }
        catch (Exception e)
        {
            _statusLabel.Text = $"Error adding event: {e.Message}";
            GD.PrintErr($"Error adding event: {e}");
        }
    }

    private void OnAdvanceTime()
    {
        try
        {
            if (!_timeWheel.IsCurrentSlotEmpty())
            {
                _statusLabel.Text = "Cannot advance: current slot is not empty. Pop events first.";
                return;
            }

            _currentTime++;
            _timeWheel.AdvanceWheel();
            _statusLabel.Text = $"Advanced time to {_currentTime}";
            UpdateDisplay();
        }
        catch (Exception e)
        {
            _statusLabel.Text = $"Error advancing time: {e.Message}";
            GD.PrintErr($"Error advancing time: {e}");
        }
    }

    private void OnPopEvent()
    {
        try
        {
            var result = _timeWheel.PopDueEvent();
            if (result.HasValue)
            {
                _statusLabel.Text = $"Popped event: Key='{result.Value.Key}', Value='{result.Value.Value}'";
            }
            else
            {
                _statusLabel.Text = "No events to pop in current slot.";
            }
            UpdateDisplay();
        }
        catch (Exception e)
        {
            _statusLabel.Text = $"Error popping event: {e.Message}";
            GD.PrintErr($"Error popping event: {e}");
        }
    }

    private void OnTestBasic()
    {
        try
        {
            _statusLabel.Text = "Running basic operations test...";
            
            // Clear everything first
            OnClearAll();
            
            // Test basic scheduling
            _timeWheel.ScheduleWithDelay("test1", "First Event", 2);
            _timeWheel.ScheduleWithDelay("test2", "Second Event", 5);
            _timeWheel.ScheduleWithDelay("test3", "Third Event", 2); // Same time as test1
            
            _statusLabel.Text = "Basic test completed. Events scheduled for times 2 and 5.";
            UpdateDisplay();
        }
        catch (Exception e)
        {
            _statusLabel.Text = $"Error in basic test: {e.Message}";
            GD.PrintErr($"Error in basic test: {e}");
        }
    }

    private void OnTestFuture()
    {
        try
        {
            _statusLabel.Text = "Running future events test...";
            
            // Clear everything first
            OnClearAll();
            
            // Test future event scheduling (beyond buffer size of 10)
            _timeWheel.ScheduleWithDelay("future1", "Future Event 1", 15);
            _timeWheel.ScheduleWithDelay("future2", "Future Event 2", 25);
            _timeWheel.ScheduleWithDelay("near1", "Near Event", 3);
            
            _statusLabel.Text = "Future test completed. Events scheduled beyond buffer size.";
            UpdateDisplay();
        }
        catch (Exception e)
        {
            _statusLabel.Text = $"Error in future test: {e.Message}";
            GD.PrintErr($"Error in future test: {e}");
        }
    }

    private void OnClearAll()
    {
        // Recreate the time wheel to clear it
        _currentTime = 0;
        _timeWheel = new IndexedTimeWheel<string>(10, () => _currentTime);
        _statusLabel.Text = "Cleared all events and reset time to 0";
        UpdateDisplay();
    }

    private void OnRunValidation()
    {
        try
        {
            _statusLabel.Text = "Running validation tests...";
            var results = IndexedTimeWheelValidator.RunAllTests();
            
            // Clear events container and show test results
            foreach (Node child in _eventsContainer.GetChildren())
            {
                child.QueueFree();
            }
            
            var header = new Label();
            header.Text = "Validation Test Results:";
            header.AddThemeStyleboxOverride("normal", new StyleBoxFlat());
            _eventsContainer.AddChild(header);
            
            foreach (var result in results)
            {
                var resultLabel = new Label();
                resultLabel.Text = result;
                if (result.Contains("PASSED"))
                {
                    resultLabel.Modulate = new Color(0, 1, 0); // Green
                }
                else if (result.Contains("FAILED"))
                {
                    resultLabel.Modulate = new Color(1, 0, 0); // Red
                }
                _eventsContainer.AddChild(resultLabel);
            }
            
            _statusLabel.Text = "Validation tests completed. Check results below.";
        }
        catch (Exception e)
        {
            _statusLabel.Text = $"Error running validation: {e.Message}";
            GD.PrintErr($"Error running validation: {e}");
        }
    }

    private void UpdateDisplay()
    {
        // Update time label
        var timeLabel = FindChild("TimeLabel") as Label;
        if (timeLabel != null)
        {
            timeLabel.Text = $"Current Time: {_currentTime}";
        }

        // Clear events container
        foreach (Node child in _eventsContainer.GetChildren())
        {
            child.QueueFree();
        }

        // Display wheel status
        var statusInfo = new Label();
        statusInfo.Text = $"Total Events: {_timeWheel.Count} | Has Events: {_timeWheel.HasAnyEvents()} | Current Slot Empty: {_timeWheel.IsCurrentSlotEmpty()}";
        _eventsContainer.AddChild(statusInfo);

        // Display upcoming events
        try
        {
            var upcomingEvents = _timeWheel.PeekUpcomingEvents(10, 20);
            if (upcomingEvents.Count > 0)
            {
                var header = new Label();
                header.Text = "Upcoming Events in Wheel:";
                header.AddThemeStyleboxOverride("normal", new StyleBoxFlat());
                _eventsContainer.AddChild(header);

                foreach (var (key, value) in upcomingEvents)
                {
                    var eventLabel = new Label();
                    eventLabel.Text = $"  • Key: '{key}', Value: '{value}'";
                    _eventsContainer.AddChild(eventLabel);
                }
            }
            else
            {
                var noEvents = new Label();
                noEvents.Text = "No upcoming events in wheel.";
                _eventsContainer.AddChild(noEvents);
            }
        }
        catch (Exception e)
        {
            var errorLabel = new Label();
            errorLabel.Text = $"Error displaying events: {e.Message}";
            _eventsContainer.AddChild(errorLabel);
        }
    }
}