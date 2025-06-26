using System;
using System.Collections.Generic;

namespace Core
{
    /// <summary>
    /// 时间单位枚举
    /// </summary>
    public enum TimeUnit
    {
        Hour,
        Day
    }

    /// <summary>
    /// 游戏日历显示器 - 负责时间的格式化显示和时间管理
    ///
    /// 专为回合制游戏设计的时间系统，支持非匀速时间流逝、精确时间控制和纪年管理。
    ///
    /// Attributes:
    ///     DAYS_PER_YEAR (int): 每年天数，默认360天
    ///     HOURS_PER_DAY (int): 每天小时数，默认24小时
    ///     BASE_YEAR (int): 起始年份，默认公元前2000年
    ///
    /// Example:
    ///     var calendar = new GameCalendar();
    ///     calendar.AdvanceTime(30, TimeUnit.Day);
    ///     Console.WriteLine($"当前年份: {calendar.CurrentGregorianYear}");
    ///     calendar.StartNewEra("开元");
    ///     calendar.AnchorEra("开元", 713);  // 开元元年=公元713年
    /// </summary>
    public class Calendar
    {
        /// <summary>
        /// 每天小时数
        /// </summary>
        public const int HOURS_PER_DAY = 24;

        /// <summary>
        /// 每年天数
        /// </summary>
        public const int DAYS_PER_YEAR = 360;  // 简化为12个月，每月30天

        /// <summary>
        /// 起始年份
        /// </summary>
        private readonly int _baseYear;

        /// <summary>
        /// 当前时间（以小时为最小单位）
        /// </summary>
        private int _timestampHour = 0;

        /// <summary>
        /// 当前锚定：(纪元名, 元年公元年份)
        /// </summary>
        private Tuple<string, int> _currentAnchor;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="baseYear">基准年份，默认为-2000</param>
        public Calendar(int baseYear = -2000)
        {
            _baseYear = baseYear;
            _currentAnchor = new Tuple<string, int>("uninitialized", _baseYear);
        }

        /// <summary>
        /// 当前年份（公元年）
        /// </summary>
        public int CurrentGregorianYear
        {
            get
            {
                int totalDays = _timestampHour / HOURS_PER_DAY;
                return _baseYear + (totalDays / DAYS_PER_YEAR);
            }
        }

        /// <summary>
        /// 当前年中的第几天（1-360）
        /// </summary>
        public int CurrentDayInYear
        {
            get
            {
                int totalDays = _timestampHour / HOURS_PER_DAY;
                return (totalDays % DAYS_PER_YEAR) + 1;
            }
        }

        /// <summary>
        /// 当前小时（0-23）
        /// </summary>
        public int CurrentHourInDay
        {
            get
            {
                return _timestampHour % HOURS_PER_DAY;
            }
        }

        /// <summary>
        /// 当前月份（1-12，每月30天）
        /// </summary>
        public int CurrentMonth
        {
            get
            {
                return ((CurrentDayInYear - 1) / 30) + 1;
            }
        }

        /// <summary>
        /// 当前月中的第几天（1-30）
        /// </summary>
        public int CurrentDayInMonth
        {
            get
            {
                return ((CurrentDayInYear - 1) % 30) + 1;
            }
        }

        /// <summary>
        /// 锚定纪元
        ///
        /// 指定某个纪元的元年对应的公元年份，用于纪元显示计算。
        /// 不允许锚定到比当前时间还晚的时期。
        ///
        /// Args:
        ///     eraName: 纪元名称，如"开元"
        ///     gregorianYear: 纪元元年对应的公元年份，如713（开元元年=公元713年）
        ///
        /// Raises:
        ///     ArgumentException: 当锚定年份晚于当前年份时
        ///
        /// Example:
        ///     calendar.AnchorEra("开元", 713);  // 开元元年=公元713年
        /// </summary>
        /// <param name="eraName">纪元名称</param>
        /// <param name="gregorianYear">纪元元年对应的公元年份</param>
        public void AnchorEra(string eraName, int gregorianYear)
        {
            if (string.IsNullOrWhiteSpace(eraName))
            {
                throw new ArgumentException("eraName cannot be empty or whitespace");
            }

            int currentYear = CurrentGregorianYear;
            if (gregorianYear > currentYear)
            {
                throw new ArgumentException($"不能锚定到未来时期：锚定年份{gregorianYear}晚于当前年份{currentYear}");
            }

            // 存储为 (纪元名, 元年公元年份)
            _currentAnchor = new Tuple<string, int>(eraName, gregorianYear);
        }

        /// <summary>
        /// 改元 - 开始新纪元
        ///
        /// 从当前年份开始新的纪元。
        ///
        /// Args:
        ///     name: 新纪元名称，如"永徽"、"开元"等
        ///
        /// Raises:
        ///     ArgumentException: 当纪元名称为空时
        ///
        /// Example:
        ///     calendar.StartNewEra("永徽");  // 从当前年份开始永徽纪元
        /// </summary>
        /// <param name="name">新纪元名称</param>
        public void StartNewEra(string name)
        {
            if (string.IsNullOrWhiteSpace(name))
            {
                throw new ArgumentException("name cannot be empty or whitespace");
            }

            // 改元就是锚定当前年份为新纪元的元年
            AnchorEra(name, CurrentGregorianYear);
        }

        /// <summary>
        /// 获取当前纪元名称
        /// </summary>
        /// <returns>当前纪元名称</returns>
        public string GetCurrentEraName()
        {
            if (_currentAnchor != null)
            {
                string eraName = _currentAnchor.Item1;
                int gregorianYear = _currentAnchor.Item2;
                int currentYear = CurrentGregorianYear;

                // 如果当前年份在纪元范围内
                if (currentYear >= gregorianYear)
                {
                    return eraName;
                }
            }

            throw new InvalidOperationException("current year earlier than anchor year");
        }

        /// <summary>
        /// 获取当前纪元年份
        /// </summary>
        /// <returns>当前纪元年份</returns>
        public int GetCurrentEraYear()
        {
            if (_currentAnchor != null)
            {
                string eraName = _currentAnchor.Item1;
                int gregorianYear = _currentAnchor.Item2;
                int currentYear = CurrentGregorianYear;

                // 如果当前年份在纪元范围内
                if (currentYear >= gregorianYear)
                {
                    return currentYear - gregorianYear + 1;
                }
            }

            throw new InvalidOperationException("current year earlier than anchor year");
        }

        /// <summary>
        /// 获取当前时间戳（小时数）
        ///
        /// Returns:
        ///     int: 从起始时间开始的总小时数
        /// </summary>
        /// <returns>当前时间戳</returns>
        public int GetTimestamp()
        {
            return _timestampHour;
        }

        /// <summary>
        /// 推进时间一个tick（1小时）
        /// </summary>
        public void AdvanceTimeTick()
        {
            _timestampHour += 1;
        }

        /// <summary>
        /// 获取当前时间信息
        /// </summary>
        /// <returns>时间信息字典</returns>
        public Dictionary<string, object> GetTimeInfo()
        {
            var info = new Dictionary<string, object>
            {
                ["timestamp"] = _timestampHour,
                ["gregorian_year"] = CurrentGregorianYear,
                ["month"] = CurrentMonth,
                ["day_in_month"] = CurrentDayInMonth,
                ["day_in_year"] = CurrentDayInYear,
                ["hour_in_day"] = CurrentHourInDay,
                ["current_anchor"] = _currentAnchor
            };

            try
            {
                info["current_era_name"] = GetCurrentEraName();
                info["current_era_year"] = GetCurrentEraYear();
            }
            catch (InvalidOperationException)
            {
                info["current_era_name"] = null;
                info["current_era_year"] = null;
            }

            return info;
        }

        /// <summary>
        /// 重置时间到起始状态
        /// </summary>
        public void Reset()
        {
            _timestampHour = 0;
            _currentAnchor = new Tuple<string, int>("uninitialized", _baseYear);
        }

        /// <summary>
        /// 格式化为公历日期显示
        ///
        /// Args:
        ///     showHour: 是否显示小时
        ///
        /// Returns:
        ///     格式化的日期字符串
        /// </summary>
        /// <param name="showHour">是否显示小时</param>
        /// <returns>格式化的日期字符串</returns>
        public string FormatDateGregorian(bool showHour = false)
        {
            int year = CurrentGregorianYear;
            int month = CurrentMonth;
            int day = CurrentDayInMonth;
            int hour = CurrentHourInDay;

            // 处理公元前年份
            string yearStr;
            if (year < 0)
            {
                yearStr = $"公元前{Math.Abs(year)}年";
            }
            else
            {
                yearStr = $"公元{year}年";
            }

            if (showHour)
            {
                return $"{yearStr}{month}月{day}日{hour}点";
            }
            else
            {
                return $"{yearStr}{month}月{day}日";
            }
        }

        /// <summary>
        /// 格式化为纪年日期显示
        ///
        /// Args:
        ///     showHour: 是否显示小时
        ///
        /// Returns:
        ///     格式化的日期字符串
        /// </summary>
        /// <param name="showHour">是否显示小时</param>
        /// <returns>格式化的日期字符串</returns>
        public string FormatDateEra(bool showHour = false)
        {
            try
            {
                string eraName = GetCurrentEraName();
                int eraYear = GetCurrentEraYear();

                if (eraName == null)
                {
                    // 如果纪元未设置或当前年份早于锚定年份，回退到公历显示
                    return FormatDateGregorian(showHour);
                }

                int month = CurrentMonth;
                int day = CurrentDayInMonth;
                int hour = CurrentHourInDay;

                if (showHour)
                {
                    return $"{eraName}{eraYear}年{month}月{day}日{hour}点";
                }
                else
                {
                    return $"{eraName}{eraYear}年{month}月{day}日";
                }
            }
            catch (InvalidOperationException)
            {
                // 如果纪元未设置或当前年份早于锚定年份，回退到公历显示
                return FormatDateGregorian(showHour);
            }
        }

        /// <summary>
        /// 获取详细的时间状态文本
        /// </summary>
        /// <returns>时间状态文本</returns>
        public string GetTimeStatusText()
        {
            var info = GetTimeInfo();
            string gregorian = FormatDateGregorian(true);
            string era = FormatDateEra(true);

            var statusLines = new List<string>
            {
                $"公历: {gregorian}",
                $"纪年: {era}",
                $"年内第{info["day_in_year"]}天",
                $"总计: {info["timestamp"]}小时"
            };

            // 显示锚定信息
            if (info["current_anchor"] != null)
            {
                var anchor = (Tuple<string, int>)info["current_anchor"];
                string eraName = anchor.Item1;
                int gregorianYear = anchor.Item2;
                statusLines.Add($"锚定: {eraName}元年 = 公元{gregorianYear}年");
            }

            return string.Join("\n", statusLines);
        }
    }
}