import unittest
import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from game_system.calendar.calendar import TimeManager, TimeUnit, Calendar
from game_system.config import EPOCH_START_YEAR


class TestTimeManager(unittest.TestCase):
    """测试时间管理器"""

    def setUp(self):
        """测试初始化"""
        # TimeManager 默认使用 config 中的年份
        self.time_manager = TimeManager()

    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.time_manager.current_year, EPOCH_START_YEAR)
        self.assertEqual(self.time_manager.current_month, 1)
        self.assertEqual(self.time_manager.current_day_in_month, 1)

    def test_advance_time(self):
        """测试时间推进"""
        self.time_manager.advance_time(1, TimeUnit.DAY)
        self.assertEqual(self.time_manager.current_year, EPOCH_START_YEAR)
        self.assertEqual(self.time_manager.current_month, 1)
        self.assertEqual(self.time_manager.current_day_in_month, 2)

    def test_advance_one_year(self):
        """测试推进一整年"""
        self.time_manager.advance_time(360, TimeUnit.DAY)
        self.assertEqual(self.time_manager.current_year, EPOCH_START_YEAR + 1)
        self.assertEqual(self.time_manager.current_month, 1)
        self.assertEqual(self.time_manager.current_day_in_month, 1)

    def test_get_time_info(self):
        """测试获取时间信息"""
        self.time_manager.advance_time(100, TimeUnit.DAY)
        self.time_manager.advance_time(5, TimeUnit.HOUR)
        info = self.time_manager.get_time_info()

        self.assertEqual(info['year'], EPOCH_START_YEAR)
        self.assertEqual(info['day_in_year'], 101)
        self.assertEqual(info['hour'], 5)

    def test_reset(self):
        """测试重置功能"""
        self.time_manager.advance_time(100, TimeUnit.DAY)
        self.time_manager.reset()
        self.assertEqual(self.time_manager.current_year, EPOCH_START_YEAR)
        self.assertEqual(self.time_manager.current_day_in_year, 1)
        self.assertEqual(self.time_manager.current_hour, 0)


class TestEraSystem(unittest.TestCase):
    """测试年号系统"""

    def setUp(self):
        self.time_manager = TimeManager()
        self.calendar = Calendar(self.time_manager)
        # Set current year to -104 for testing
        # To get to year -104 from -2000, we need to advance -104 - (-2000) = 1896 years
        self.time_manager.advance_time(1896 * 360, TimeUnit.DAY)
        self.assertEqual(self.time_manager.current_year, -104)

    def test_era_anchor(self):
        """测试设置年号锚点"""
        self.time_manager.anchor_era("大汉", -140) # This is in the past, so it's valid
        self.assertEqual(self.time_manager.get_current_era_name(), "大汉")
        self.assertEqual(self.time_manager.get_current_era_year(), 37) # -104 - (-140) + 1

    def test_era_anchor_validation(self):
        """测试锚点年份验证"""
        # Current year is -104. Anchoring to a future year should fail.
        with self.assertRaises(ValueError):
            self.time_manager.anchor_era("新纪元", -100) # -100 is after -104

    def test_reset_and_format(self):
        """测试重置后格式化"""
        self.time_manager.advance_time(100, TimeUnit.DAY)
        self.time_manager.reset()
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR)}年1月1日")

    def test_format_with_era(self):
        """测试带年号的格式化"""
        self.time_manager.advance_time(2712 * 360, TimeUnit.DAY) # Go to year 712
        self.time_manager.start_new_era("开元") # Starts in 712
        self.time_manager.advance_time(365, TimeUnit.DAY) # Go to year 713, day 6
        self.time_manager.advance_time(5, TimeUnit.HOUR)

        # Era is 开元, year is 2 (713 is the 2nd year of the era started in 712)
        date_str = self.calendar.format_date_era(show_hour=True)
        self.assertEqual(date_str, "开元2年1月6日5点")

    def test_start_from_bc_era(self):
        """测试从其他公元前年份开始"""
        TimeManager.BASE_YEAR = -100
        time_manager = TimeManager()
        self.assertEqual(time_manager.current_year, -100)
        time_manager.advance_time(360 * 100, TimeUnit.DAY) # 推进100年
        # 从-100年推进100年，会到达公元0年 (我们的日历系统包含0年)
        self.assertEqual(time_manager.current_year, 0)


class TestCalendarIntegration(unittest.TestCase):
    """测试日历和时间管理器的集成"""

    def setUp(self):
        # Reset BASE_YEAR before each test in this class to ensure isolation
        TimeManager.BASE_YEAR = EPOCH_START_YEAR
        self.time_manager = TimeManager()
        self.calendar = Calendar(self.time_manager)

    def test_initial_date(self):
        """测试初始日期"""
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR)}年1月1日")

    def test_advancing_time_and_format(self):
        """测试推进时间后的格式化"""
        self.time_manager.advance_time(365, TimeUnit.DAY)
        # After 365 days from start of -2000, it's year -1999, day 6
        self.assertEqual(self.time_manager.current_year, EPOCH_START_YEAR + 1)
        self.assertEqual(self.time_manager.current_day_in_year, 6)
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR) - 1}年1月6日")

    def test_reset_and_format(self):
        """测试重置后格式化"""
        self.time_manager.advance_time(100, TimeUnit.DAY)
        self.time_manager.reset()
        self.assertEqual(self.time_manager.current_year, EPOCH_START_YEAR)
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR)}年1月1日")

    def test_format_with_era(self):
        """测试带年号的格式化"""
        # Go to year 713 AD
        target_year = 713
        initial_year = self.time_manager.current_year
        self.time_manager.advance_time((target_year - initial_year) * 360, TimeUnit.DAY)
        self.assertEqual(self.time_manager.current_year, target_year)

        self.time_manager.anchor_era("开元", 713)
        self.time_manager.advance_time(5 * 24 + 5, TimeUnit.HOUR) # day 6, 5:00

        # Year is 713, which is the 1st year of the Kaiyuan era
        date_str = self.calendar.format_date_era(show_hour=True)
        self.assertEqual(date_str, "开元1年1月6日5点")


class TestTimeManagerWithDifferentStart(unittest.TestCase):
    """测试不同起始年份的时间管理器"""

    def setUp(self):
        # Save the original BASE_YEAR
        self.original_base_year = TimeManager.BASE_YEAR

    def tearDown(self):
        # Restore the original BASE_YEAR after each test
        TimeManager.BASE_YEAR = self.original_base_year

    def test_start_from_ad_1(self):
        """测试从公元1年开始"""
        TimeManager.BASE_YEAR = 1
        time_manager = TimeManager()
        self.assertEqual(time_manager.current_year, 1)
        time_manager.advance_time(365, TimeUnit.DAY)
        # 我们的年份是360天，所以365天后是2年第6天 (day 1 to 5 are in year 2)
        self.assertEqual(time_manager.current_year, 2)
        self.assertEqual(time_manager.current_day_in_year, 6)

    def test_start_from_bc_era(self):
        """测试从其他公元前年份开始"""
        TimeManager.BASE_YEAR = -100
        time_manager = TimeManager()
        self.assertEqual(time_manager.current_year, -100)
        time_manager.advance_time(360 * 100, TimeUnit.DAY) # 推进100年
        # 从-100年推进100年，会到达公元0年 (我们的日历系统包含0年)
        self.assertEqual(time_manager.current_year, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)