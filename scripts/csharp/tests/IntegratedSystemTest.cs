using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using Core;
using Tests;

public partial class IntegratedSystemTest : Control
{
    // Unified test coordinator - replaces manual component management
    private TestGameWorld _testWorld;

    // UI Components - Left CTB Action Bar
    private VBoxContainer _ctbActionBar;
    private ScrollContainer _ctbScrollContainer;
    private Label _ctbTitle;
    private VBoxContainer _ctbEventsList;

    // UI Components - Right TimeWheel Inspector
    private VBoxContainer _timeWheelInspector;
    private ScrollContainer _timeWheelScrollContainer;
    private Label _timeWheelTitle;
    private VBoxContainer _wheelEventsList;
    private VBoxContainer _futureEventsList;

    // UI Components - Center Control Panel
    private VBoxContainer _centerPanel;
    private Label _currentTimeLabel;
    private Label _calendarStatusLabel;
    private VBoxContainer _controlsContainer;

    // Test data
    private List<string> _characterNames = new List<string> { "张飞", "关羽", "刘备", "曹操", "孙权" };
    private Random _random = new Random();

    public override void _Ready()
    {
        GD.Print("Initializing Integrated System Test");
        
        // 设置UI缩放和字体大小
        SetupUIScaling();
        
        InitializeSystems();
        SetupUI();
        UpdateAllDisplays();
        
        // Add some initial test events
        AddInitialTestEvents();
    }

    private void SetupUIScaling()
    {
        // 设置全局字体大小而不是整体缩放（避免按钮被裁剪）
        // 我们将在各个UI元素中单独设置字体大小
        GD.Print("UI scaling setup: using individual font sizes instead of global scaling");
    }

    private void InitializeSystems()
    {
        // Initialize unified test coordinator with 180-hour buffer
        _testWorld = new TestGameWorld(timeWheelSize: 180);
        
        // Subscribe to events for UI updates
        _testWorld.OnEventExecuted += (eventDesc) => {
            AddCTBLogEntry($"已执行: {eventDesc}", true);
        };
        
        _testWorld.OnTimeAdvanced += (hours) => {
            AddCTBLogEntry($"时间推进了 {hours} 小时", false);
        };
        
        _testWorld.OnSystemsUpdated += () => {
            CallDeferred(nameof(UpdateAllDisplays));
        };
        
        GD.Print($"TestGameWorld initialized - Calendar: {_testWorld.CurrentCalendarTime}");
    }

    private void SetupUI()
    {
        // Main layout: Left bar | Center panel | Right bar - Fill entire window
        var mainContainer = new HBoxContainer();
        mainContainer.AnchorLeft = 0;
        mainContainer.AnchorTop = 0;
        mainContainer.AnchorRight = 1;
        mainContainer.AnchorBottom = 1;
        mainContainer.OffsetLeft = 0;
        mainContainer.OffsetTop = 0;
        mainContainer.OffsetRight = 0;
        mainContainer.OffsetBottom = 0;
        mainContainer.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        mainContainer.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        AddChild(mainContainer);

        // === LEFT CTB ACTION BAR ===
        SetupCTBActionBar(mainContainer);
        
        // === CENTER CONTROL PANEL ===
        SetupCenterPanel(mainContainer);
        
        // === RIGHT TIMEWHEEL INSPECTOR ===
        SetupTimeWheelInspector(mainContainer);
    }

    private void SetupCTBActionBar(HBoxContainer parent)
    {
        _ctbActionBar = new VBoxContainer();
        _ctbActionBar.CustomMinimumSize = new Vector2(300, 0);
        _ctbActionBar.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _ctbActionBar.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        parent.AddChild(_ctbActionBar);

        // Title
        _ctbTitle = new Label();
        _ctbTitle.Text = "⚔️ CTB行动条";
        _ctbTitle.HorizontalAlignment = HorizontalAlignment.Center;
        _ctbTitle.AddThemeStyleboxOverride("normal", CreateColoredStyleBox(new Color(0.2f, 0.3f, 0.5f)));
        _ctbTitle.AddThemeColorOverride("font_color", Colors.White);
        _ctbTitle.AddThemeFontSizeOverride("font_size", 18);
        _ctbTitle.CustomMinimumSize = new Vector2(0, 50);
        _ctbActionBar.AddChild(_ctbTitle);

        // Scrollable events list - 修复文字显示
        _ctbScrollContainer = new ScrollContainer();
        _ctbScrollContainer.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        _ctbScrollContainer.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _ctbScrollContainer.HorizontalScrollMode = ScrollContainer.ScrollMode.Auto;
        _ctbScrollContainer.VerticalScrollMode = ScrollContainer.ScrollMode.Auto;
        _ctbActionBar.AddChild(_ctbScrollContainer);

        _ctbEventsList = new VBoxContainer();
        _ctbEventsList.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _ctbScrollContainer.AddChild(_ctbEventsList);

        // Action buttons
        var ctbButtonsContainer = new HBoxContainer();
        ctbButtonsContainer.CustomMinimumSize = new Vector2(0, 50);
        ctbButtonsContainer.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _ctbActionBar.AddChild(ctbButtonsContainer);

        var addActionButton = new Button();
        addActionButton.Text = "添加行动";
        addActionButton.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        addActionButton.AddThemeFontSizeOverride("font_size", 14);
        addActionButton.Pressed += OnAddRandomAction;
        ctbButtonsContainer.AddChild(addActionButton);

        var executeActionButton = new Button();
        executeActionButton.Text = "执行行动";
        executeActionButton.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        executeActionButton.AddThemeFontSizeOverride("font_size", 14);
        executeActionButton.Pressed += OnExecuteNextAction;
        ctbButtonsContainer.AddChild(executeActionButton);
    }

    private void SetupCenterPanel(HBoxContainer parent)
    {
        _centerPanel = new VBoxContainer();
        _centerPanel.CustomMinimumSize = new Vector2(450, 0);
        _centerPanel.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _centerPanel.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        parent.AddChild(_centerPanel);

        // Current time display
        _currentTimeLabel = new Label();
        _currentTimeLabel.Text = "当前时间: 初始化中...";
        _currentTimeLabel.HorizontalAlignment = HorizontalAlignment.Center;
        _currentTimeLabel.AddThemeStyleboxOverride("normal", CreateColoredStyleBox(new Color(0.1f, 0.5f, 0.2f)));
        _currentTimeLabel.AddThemeColorOverride("font_color", Colors.White);
        _currentTimeLabel.AddThemeFontSizeOverride("font_size", 16);
        _currentTimeLabel.CustomMinimumSize = new Vector2(0, 80);
        _centerPanel.AddChild(_currentTimeLabel);

        // Calendar status
        _calendarStatusLabel = new Label();
        _calendarStatusLabel.Text = "日历状态: 初始化中...";
        _calendarStatusLabel.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _calendarStatusLabel.AddThemeFontSizeOverride("font_size", 14);
        _centerPanel.AddChild(_calendarStatusLabel);

        // Controls
        _controlsContainer = new VBoxContainer();
        _centerPanel.AddChild(_controlsContainer);

        SetupTimeControls();
        SetupCalendarControls();
        SetupTestControls();
    }

    private void SetupTimeControls()
    {
        var timeGroup = CreateControlGroup("⏰ 时间控制");
        _controlsContainer.AddChild(timeGroup);

        var buttonRow1 = new HBoxContainer();
        timeGroup.AddChild(buttonRow1);

        var advanceHourButton = new Button();
        advanceHourButton.Text = "推进1小时";
        advanceHourButton.Pressed += () => AdvanceTime(1);
        buttonRow1.AddChild(advanceHourButton);

        var advanceDayButton = new Button();
        advanceDayButton.Text = "推进1天";
        advanceDayButton.Pressed += () => AdvanceTime(24);
        buttonRow1.AddChild(advanceDayButton);

        var buttonRow2 = new HBoxContainer();
        timeGroup.AddChild(buttonRow2);

        var advanceWeekButton = new Button();
        advanceWeekButton.Text = "推进7天";
        advanceWeekButton.Pressed += () => AdvanceTime(168);
        buttonRow2.AddChild(advanceWeekButton);

        var advanceMonthButton = new Button();
        advanceMonthButton.Text = "推进1月";
        advanceMonthButton.Pressed += () => AdvanceTime(720); // 30 days * 24 hours
        buttonRow2.AddChild(advanceMonthButton);
    }

    private void SetupCalendarControls()
    {
        var calendarGroup = CreateControlGroup("📅 日历控制");
        _controlsContainer.AddChild(calendarGroup);

        // Era anchoring
        var anchorContainer = new HBoxContainer();
        calendarGroup.AddChild(anchorContainer);

        var eraNameInput = new LineEdit();
        eraNameInput.PlaceholderText = "纪元名 (如: 开元)";
        eraNameInput.Name = "EraNameInput";
        anchorContainer.AddChild(eraNameInput);

        var anchorYearInput = new LineEdit();
        anchorYearInput.PlaceholderText = "元年 (如: 713)";
        anchorYearInput.Name = "AnchorYearInput";
        anchorContainer.AddChild(anchorYearInput);

        var anchorButton = new Button();
        anchorButton.Text = "锚定";
        anchorButton.Pressed += OnAnchorEra;
        anchorContainer.AddChild(anchorButton);

        // Change era
        var changeEraContainer = new HBoxContainer();
        calendarGroup.AddChild(changeEraContainer);

        var newEraInput = new LineEdit();
        newEraInput.PlaceholderText = "新纪元名";
        newEraInput.Name = "NewEraInput";
        changeEraContainer.AddChild(newEraInput);

        var changeEraButton = new Button();
        changeEraButton.Text = "改元";
        changeEraButton.Pressed += OnChangeEra;
        changeEraContainer.AddChild(changeEraButton);

        var resetButton = new Button();
        resetButton.Text = "重置日历";
        resetButton.Pressed += OnResetCalendar;
        changeEraContainer.AddChild(resetButton);
    }

    private void SetupTestControls()
    {
        var testGroup = CreateControlGroup("🧪 测试场景");
        _controlsContainer.AddChild(testGroup);

        var testButtonRow1 = new HBoxContainer();
        testGroup.AddChild(testButtonRow1);

        var basicTestButton = new Button();
        basicTestButton.Text = "基础测试";
        basicTestButton.Pressed += OnBasicTest;
        testButtonRow1.AddChild(basicTestButton);

        var combatTestButton = new Button();
        combatTestButton.Text = "战斗测试";
        combatTestButton.Pressed += OnCombatTest;
        testButtonRow1.AddChild(combatTestButton);

        var testButtonRow2 = new HBoxContainer();
        testGroup.AddChild(testButtonRow2);

        var longTermTestButton = new Button();
        longTermTestButton.Text = "长期事件";
        longTermTestButton.Pressed += OnLongTermTest;
        testButtonRow2.AddChild(longTermTestButton);

        var clearAllButton = new Button();
        clearAllButton.Text = "清空所有";
        clearAllButton.Pressed += OnClearAll;
        testButtonRow2.AddChild(clearAllButton);
    }

    private void SetupTimeWheelInspector(HBoxContainer parent)
    {
        _timeWheelInspector = new VBoxContainer();
        _timeWheelInspector.CustomMinimumSize = new Vector2(350, 0);
        _timeWheelInspector.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _timeWheelInspector.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        parent.AddChild(_timeWheelInspector);

        // Title
        _timeWheelTitle = new Label();
        _timeWheelTitle.Text = "⚙️ 时间轮检查器";
        _timeWheelTitle.HorizontalAlignment = HorizontalAlignment.Center;
        _timeWheelTitle.AddThemeStyleboxOverride("normal", CreateColoredStyleBox(new Color(0.5f, 0.2f, 0.3f)));
        _timeWheelTitle.AddThemeColorOverride("font_color", Colors.White);
        _timeWheelTitle.AddThemeFontSizeOverride("font_size", 18);
        _timeWheelTitle.CustomMinimumSize = new Vector2(0, 50);
        _timeWheelInspector.AddChild(_timeWheelTitle);

        // Wheel events (current buffer)
        var wheelLabel = new Label();
        wheelLabel.Text = "🎯 主时间轮事件:";
        wheelLabel.AddThemeFontSizeOverride("font_size", 14);
        _timeWheelInspector.AddChild(wheelLabel);

        var wheelScrollContainer = new ScrollContainer();
        wheelScrollContainer.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        wheelScrollContainer.CustomMinimumSize = new Vector2(0, 200);
        _timeWheelInspector.AddChild(wheelScrollContainer);

        _wheelEventsList = new VBoxContainer();
        wheelScrollContainer.AddChild(_wheelEventsList);

        // Future events
        var futureLabel = new Label();
        futureLabel.Text = "🔮 远期事件池:";
        futureLabel.AddThemeFontSizeOverride("font_size", 14);
        _timeWheelInspector.AddChild(futureLabel);

        var futureScrollContainer = new ScrollContainer();
        futureScrollContainer.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        futureScrollContainer.CustomMinimumSize = new Vector2(0, 200);
        _timeWheelInspector.AddChild(futureScrollContainer);

        _futureEventsList = new VBoxContainer();
        futureScrollContainer.AddChild(_futureEventsList);
    }

    private VBoxContainer CreateControlGroup(string title)
    {
        var group = new VBoxContainer();
        group.AddThemeStyleboxOverride("normal", CreateColoredStyleBox(new Color(0.9f, 0.9f, 0.9f)));

        var titleLabel = new Label();
        titleLabel.Text = title;
        titleLabel.AddThemeColorOverride("font_color", new Color(0.2f, 0.2f, 0.2f));
        group.AddChild(titleLabel);

        return group;
    }

    private StyleBoxFlat CreateColoredStyleBox(Color color)
    {
        var styleBox = new StyleBoxFlat();
        styleBox.BgColor = color;
        styleBox.BorderWidthTop = styleBox.BorderWidthBottom = styleBox.BorderWidthLeft = styleBox.BorderWidthRight = 1;
        styleBox.BorderColor = color.Darkened(0.3f);
        styleBox.CornerRadiusTopLeft = styleBox.CornerRadiusTopRight = 
            styleBox.CornerRadiusBottomLeft = styleBox.CornerRadiusBottomRight = 3;
        styleBox.ContentMarginTop = styleBox.ContentMarginBottom = 8;
        styleBox.ContentMarginLeft = styleBox.ContentMarginRight = 12;
        return styleBox;
    }

    private void AddInitialTestEvents()
    {
        try
        {
            // Add some character actions using TestGameWorld API
            _testWorld.ScheduleEvent("张飞_攻击", "张飞发动攻击", 5);
            _testWorld.ScheduleEvent("关羽_防御", "关羽进入防御状态", 8);
            _testWorld.ScheduleEvent("刘备_治疗", "刘备使用治疗技能", 12);
            
            // Add some future events
            _testWorld.ScheduleEvent("季节变化", "春季到来", 200);
            _testWorld.ScheduleEvent("节日庆典", "中秋节庆典", 300);
            
            GD.Print("Initial test events added via TestGameWorld");
        }
        catch (Exception e)
        {
            GD.PrintErr($"Error adding initial events: {e.Message}");
        }
    }

    private void AdvanceTime(int hours)
    {
        try
        {
            // Use TestGameWorld's unified time advancement - no manual sync needed!
            var result = _testWorld.AdvanceTime(hours);
            
            GD.Print($"Advanced time: {result.Summary}");
            
            // UI update is handled automatically via OnSystemsUpdated event
        }
        catch (Exception e)
        {
            GD.PrintErr($"Error advancing time: {e.Message}");
        }
    }

    // This method is no longer needed - TestGameWorld handles event processing automatically
    // Keeping it as a stub for compatibility
    private void ProcessDueEventsUntilSlotEmpty()
    {
        // Event processing is now handled automatically by TestGameWorld
        // This method exists for backwards compatibility but does nothing
        GD.Print("ProcessDueEventsUntilSlotEmpty called - now handled by TestGameWorld");
    }

    private void OnAddRandomAction()
    {
        try
        {
            var character = _characterNames[_random.Next(_characterNames.Count)];
            var actions = new[] { "攻击", "防御", "技能", "移动", "休息" };
            var action = actions[_random.Next(actions.Length)];
            var delay = _random.Next(1, 50);
            
            var eventKey = $"{character}_{action}_{DateTime.Now.Ticks}";
            var eventValue = $"{character}执行{action}";
            
            _testWorld.ScheduleEvent(eventKey, eventValue, delay);
            AddCTBLogEntry($"已安排: {eventValue} (延迟{delay}小时)", false);
            
            // UI update is handled automatically via OnSystemsUpdated event
        }
        catch (Exception e)
        {
            GD.PrintErr($"Error adding random action: {e.Message}");
        }
    }

    private void OnExecuteNextAction()
    {
        try
        {
            // Use TestGameWorld's advance-to-next-event functionality
            var result = _testWorld.AdvanceToNextEvent(maxHours: 10);
            
            if (result.EventsExecuted.Count > 0)
            {
                AddCTBLogEntry($"执行了 {result.EventsExecuted.Count} 个事件", false);
            }
            else if (result.HoursAdvanced > 0)
            {
                AddCTBLogEntry($"推进了 {result.HoursAdvanced} 小时寻找事件", false);
            }
            else
            {
                AddCTBLogEntry("没有找到任何事件", false);
            }
            
            // UI update is handled automatically via OnSystemsUpdated event
        }
        catch (Exception e)
        {
            GD.PrintErr($"Error executing next action: {e.Message}");
        }
    }

    private void OnAnchorEra()
    {
        try
        {
            var eraName = FindChild("EraNameInput", true) as LineEdit;
            var anchorYear = FindChild("AnchorYearInput", true) as LineEdit;
            
            if (eraName?.Text?.Trim() != "" && int.TryParse(anchorYear?.Text, out int year))
            {
                _testWorld.AnchorEra(eraName.Text.Trim(), year);
                AddCTBLogEntry($"锚定纪元: {eraName.Text}元年 = 公元{year}年", false);
                eraName.Text = "";
                anchorYear.Text = "";
                // UI update is handled automatically via OnSystemsUpdated event
            }
        }
        catch (Exception e)
        {
            GD.PrintErr($"Error anchoring era: {e.Message}");
            AddCTBLogEntry($"锚定失败: {e.Message}", false);
        }
    }

    private void OnChangeEra()
    {
        try
        {
            var newEraInput = FindChild("NewEraInput", true) as LineEdit;
            
            if (newEraInput?.Text?.Trim() != "")
            {
                _testWorld.StartNewEra(newEraInput.Text.Trim());
                AddCTBLogEntry($"改元: {newEraInput.Text}元年 = 当前年份", false);
                newEraInput.Text = "";
                // UI update is handled automatically via OnSystemsUpdated event
            }
        }
        catch (Exception e)
        {
            GD.PrintErr($"Error changing era: {e.Message}");
            AddCTBLogEntry($"改元失败: {e.Message}", false);
        }
    }

    private void OnResetCalendar()
    {
        _testWorld.Reset();
        AddCTBLogEntry("游戏世界已重置", false);
        // UI update is handled automatically via OnSystemsUpdated event
    }

    private void OnBasicTest()
    {
        AddCTBLogEntry("开始基础测试...", false);
        
        // Add basic events using TestGameWorld API
        _testWorld.ScheduleEvent("基础测试1", "基础事件1", 2);
        _testWorld.ScheduleEvent("基础测试2", "基础事件2", 5);
        _testWorld.ScheduleEvent("基础测试3", "基础事件3", 2);
        
        AddCTBLogEntry("基础测试事件已安排", false);
        // UI update is handled automatically via OnSystemsUpdated event
    }

    private void OnCombatTest()
    {
        AddCTBLogEntry("开始战斗测试...", false);
        
        // Simulate combat scenario
        foreach (var character in _characterNames.Take(3))
        {
            var delay = _random.Next(1, 20);
            _testWorld.ScheduleEvent($"{character}_combat", $"{character}战斗行动", delay);
        }
        
        AddCTBLogEntry("战斗测试场景已创建", false);
        // UI update is handled automatically via OnSystemsUpdated event
    }

    private void OnLongTermTest()
    {
        AddCTBLogEntry("开始长期事件测试...", false);
        
        // Add future events beyond buffer
        _testWorld.ScheduleEvent("春节", "春节庆典", 250);
        _testWorld.ScheduleEvent("收获节", "秋收庆典", 400);
        _testWorld.ScheduleEvent("年终", "年终总结", 500);
        
        AddCTBLogEntry("长期事件已安排到远期池", false);
        // UI update is handled automatically via OnSystemsUpdated event
    }

    private void OnClearAll()
    {
        // Use TestGameWorld's clear functionality
        _testWorld.ClearAllEvents();
        
        AddCTBLogEntry("所有事件已清空", false);
        // UI update is handled automatically via OnSystemsUpdated event
    }

    private void UpdateCTBQueue()
    {
        // 清空现有显示
        foreach (Node child in _ctbEventsList.GetChildren())
        {
            child.QueueFree();
        }
        
        // 获取即将到来的事件（作为队列显示）
        var upcomingEvents = _testWorld.GetUpcomingEvents(20, 15);
        
        if (upcomingEvents.Count == 0)
        {
            var noEventsLabel = new Label();
            noEventsLabel.Text = "暂无待执行行动";
            noEventsLabel.HorizontalAlignment = HorizontalAlignment.Center;
            noEventsLabel.AddThemeFontSizeOverride("font_size", 14);
            noEventsLabel.Modulate = new Color(0.7f, 0.7f, 0.7f);
            _ctbEventsList.AddChild(noEventsLabel);
            return;
        }
        
        // 按时间排序显示队列
        for (int i = 0; i < upcomingEvents.Count; i++)
        {
            var (key, value) = upcomingEvents[i];
            
            var eventContainer = new HBoxContainer();
            eventContainer.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            eventContainer.CustomMinimumSize = new Vector2(0, 40);
            
            // 队列位置显示
            var positionLabel = new Label();
            positionLabel.Text = $"{i + 1:D2}";
            positionLabel.CustomMinimumSize = new Vector2(30, 0);
            positionLabel.HorizontalAlignment = HorizontalAlignment.Center;
            positionLabel.VerticalAlignment = VerticalAlignment.Center;
            positionLabel.AddThemeFontSizeOverride("font_size", 12);
            positionLabel.AddThemeStyleboxOverride("normal", CreateColoredStyleBox(new Color(0.4f, 0.4f, 0.4f, 0.8f)));
            positionLabel.AddThemeColorOverride("font_color", Colors.White);
            eventContainer.AddChild(positionLabel);
            
            // 事件内容
            var eventLabel = new Label();
            eventLabel.Text = value.ToString();
            eventLabel.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            eventLabel.VerticalAlignment = VerticalAlignment.Center;
            eventLabel.AutowrapMode = TextServer.AutowrapMode.WordSmart;
            eventLabel.AddThemeFontSizeOverride("font_size", 14);
            
            // 根据队列位置设置颜色（即将执行的更亮）
            var intensity = 1.0f - (i * 0.1f);
            if (intensity < 0.4f) intensity = 0.4f;
            
            if (i == 0)
            {
                // 下一个要执行的 - 高亮显示
                eventLabel.AddThemeStyleboxOverride("normal", CreateColoredStyleBox(new Color(1.0f, 0.7f, 0, 0.6f)));
                eventLabel.AddThemeColorOverride("font_color", Colors.Black);
            }
            else
            {
                // 排队等待的事件
                eventLabel.AddThemeStyleboxOverride("normal", CreateColoredStyleBox(new Color(0.3f, 0.5f, 0.8f, intensity * 0.4f)));
                eventLabel.AddThemeColorOverride("font_color", new Color(1, 1, 1, intensity));
            }
            
            eventContainer.AddChild(eventLabel);
            _ctbEventsList.AddChild(eventContainer);
        }
    }
    
    private void AddCTBLogEntry(string message, bool isExecuted)
    {
        // 这个方法现在只用于添加日志条目到队列显示的底部
        var logLabel = new Label();
        logLabel.Text = $"📝 {message}";
        logLabel.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        logLabel.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        logLabel.CustomMinimumSize = new Vector2(0, 25);
        logLabel.VerticalAlignment = VerticalAlignment.Center;
        logLabel.AddThemeFontSizeOverride("font_size", 12);
        
        if (isExecuted)
        {
            logLabel.Modulate = new Color(0, 0.8f, 0); // Green for executed
        }
        else
        {
            logLabel.Modulate = new Color(0.8f, 0.8f, 0.8f); // Gray for info
        }
        
        _ctbEventsList.AddChild(logLabel);
        
        // 限制日志条目数量
        var logEntries = 0;
        foreach (Node child in _ctbEventsList.GetChildren())
        {
            if (child is Label label && label.Text.StartsWith("📝"))
            {
                logEntries++;
            }
        }
        
        if (logEntries > 5)
        {
            // 删除最老的日志条目
            foreach (Node child in _ctbEventsList.GetChildren())
            {
                if (child is Label label && label.Text.StartsWith("📝"))
                {
                    child.QueueFree();
                    break;
                }
            }
        }
        
        CallDeferred(nameof(ScrollCTBToBottom));
    }

    private void ScrollCTBToBottom()
    {
        _ctbScrollContainer.ScrollVertical = (int)_ctbScrollContainer.GetVScrollBar().MaxValue;
    }

    private void UpdateAllDisplays()
    {
        UpdateTimeDisplay();
        UpdateCalendarStatus();
        UpdateTimeWheelInspector();
        UpdateCTBQueue(); // 更新CTB队列显示
    }

    private void UpdateTimeDisplay()
    {
        try
        {
            var gregorianTime = _testWorld.CurrentCalendarTime;
            var eraTime = _testWorld.CurrentEraTime;
            var currentTime = _testWorld.CurrentTime;
            
            _currentTimeLabel.Text = $"📅 {eraTime}\n🌍 {gregorianTime}\n⏰ 总计: {currentTime}小时";
        }
        catch (Exception e)
        {
            _currentTimeLabel.Text = $"时间显示错误: {e.Message}";
        }
    }

    private void UpdateCalendarStatus()
    {
        try
        {
            var timeInfo = _testWorld.GetCalendarInfo();
            var statusText = $"公历年份: {timeInfo["gregorian_year"]}\n";
            statusText += $"月份: {timeInfo["month"]}, 日期: {timeInfo["day_in_month"]}\n";
            statusText += $"年内第 {timeInfo["day_in_year"]} 天\n";
            statusText += $"当前纪年: {timeInfo["current_era_name"] ?? "无"}\n";
            
            if (timeInfo.ContainsKey("current_anchor") && timeInfo["current_anchor"] != null)
            {
                var anchor = timeInfo["current_anchor"] as Tuple<string, int>;
                if (anchor != null)
                {
                    statusText += $"锚定: {anchor.Item1}元年 = 公元{anchor.Item2}年";
                }
            }
            
            _calendarStatusLabel.Text = statusText;
        }
        catch (Exception e)
        {
            _calendarStatusLabel.Text = $"日历状态错误: {e.Message}";
        }
    }

    private void UpdateTimeWheelInspector()
    {
        // Clear existing lists
        foreach (Node child in _wheelEventsList.GetChildren())
        {
            child.QueueFree();
        }
        foreach (Node child in _futureEventsList.GetChildren())
        {
            child.QueueFree();
        }

        try
        {
            // Show wheel statistics using TestGameWorld properties
            var statsLabel = new Label();
            statsLabel.Text = $"总事件: {_testWorld.EventCount} | 有事件: {_testWorld.HasAnyEvents} | 当前槽空: {_testWorld.IsCurrentSlotEmpty}";
            _wheelEventsList.AddChild(statsLabel);

            // Show upcoming events in wheel
            var upcomingEvents = _testWorld.GetUpcomingEvents(50, 30);
            if (upcomingEvents.Count > 0)
            {
                foreach (var (key, value) in upcomingEvents)
                {
                    var eventLabel = new Label();
                    eventLabel.Text = $"🎯 {key}: {value}";
                    eventLabel.AutowrapMode = TextServer.AutowrapMode.WordSmart;
                    _wheelEventsList.AddChild(eventLabel);
                }
            }
            else
            {
                var noEventsLabel = new Label();
                noEventsLabel.Text = "暂无即将到来的事件";
                _wheelEventsList.AddChild(noEventsLabel);
            }

            // Show future events status
            var futureInfoLabel = new Label();
            futureInfoLabel.Text = $"系统状态: {_testWorld.GetStatusSummary()}";
            _futureEventsList.AddChild(futureInfoLabel);

        }
        catch (Exception e)
        {
            var errorLabel = new Label();
            errorLabel.Text = $"检查器错误: {e.Message}";
            _wheelEventsList.AddChild(errorLabel);
        }
    }
}