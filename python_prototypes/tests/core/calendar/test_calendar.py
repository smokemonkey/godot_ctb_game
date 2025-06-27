import unittest
import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.calendar.calendar import Calendar, TimeUnit
from core.config import EPOCH_START_YEAR


class TestTimeManager(unittest.TestCase):
    """测试时间管理器"""

    def setUp(self):
        """测试初始化"""
        self.calendar = Calendar()

    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.calendar.current_gregorian_year, EPOCH_START_YEAR)
        # 验证时间信息通过get_time_info获取
        info = self.calendar.get_time_info()
        self.assertEqual(info['month'], 1)
        self.assertEqual(info['day_in_month'], 1)

    def test_advance_one_year(self):
        """测试推进一整年"""
        # 推进360天 * 24小时 = 8640小时
        for _ in range(360 * 24):
            self.calendar.advance_time_tick()
        self.assertEqual(self.calendar.current_gregorian_year, EPOCH_START_YEAR + 1)
        # 验证时间信息通过get_time_info获取
        info = self.calendar.get_time_info()
        self.assertEqual(info['month'], 1)
        self.assertEqual(info['day_in_month'], 1)

    def test_get_time_info(self):
        """测试获取时间信息"""
        # 推进100天 * 24小时 = 2400小时
        for _ in range(100 * 24):
            self.calendar.advance_time_tick()
        # 推进5小时
        for _ in range(5):
            self.calendar.advance_time_tick()
        # 设置纪元锚点避免异常
        self.calendar.anchor_era("测试纪元", EPOCH_START_YEAR)
        info = self.calendar.get_time_info()

        self.assertEqual(info['gregorian_year'], EPOCH_START_YEAR)
        self.assertEqual(info['day_in_year'], 101)
        self.assertEqual(info['hour_in_day'], 5)
        # 设置了纪元锚点，纪元相关字段应该有值
        self.assertEqual(info['current_era_name'], "测试纪元")
        self.assertEqual(info['current_era_year'], 1)

    def test_reset(self):
        """测试重置功能"""
        # 推进100天 * 24小时 = 2400小时
        for _ in range(100 * 24):
            self.calendar.advance_time_tick()
        self.calendar.reset()
        self.assertEqual(self.calendar.current_gregorian_year, EPOCH_START_YEAR)
        # 验证时间信息通过get_time_info获取
        info = self.calendar.get_time_info()
        self.assertEqual(info['day_in_year'], 1)
        self.assertEqual(info['hour_in_day'], 0)


class TestEraSystem(unittest.TestCase):
    """测试年号系统"""

    def setUp(self):
        self.calendar = Calendar()
        # Set current year to -104 for testing
        # To get to year -104 from -2000, we need to advance -104 - (-2000) = 1896 years
        # 1896年 * 360天 * 24小时 = 16381440小时
        for _ in range(1896 * 360 * 24):
            self.calendar.advance_time_tick()
        self.assertEqual(self.calendar.current_gregorian_year, -104)

    def test_era_anchor(self):
        """测试设置年号锚点"""
        self.calendar.anchor_era("大汉", -140) # This is in the past, so it's valid
        info = self.calendar.get_time_info()
        self.assertEqual(info['current_era_name'], "大汉")
        self.assertEqual(info['current_era_year'], 37) # -104 - (-140) + 1

    def test_era_anchor_validation(self):
        """测试锚点年份验证"""
        # Current year is -104. Anchoring to a future year should fail.
        with self.assertRaises(ValueError):
            self.calendar.anchor_era("新纪元", -100) # -100 is after -104

    def test_reset_and_format(self):
        """测试重置后格式化"""
        # 推进100天 * 24小时 = 2400小时
        for _ in range(100 * 24):
            self.calendar.advance_time_tick()
        self.calendar.reset()
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR)}年1月1日")

    def test_format_with_era(self):
        """测试带年号的格式化"""
        # 推进2712年 * 360天 * 24小时 = 23431680小时，到达712年
        for _ in range(2712 * 360 * 24):
            self.calendar.advance_time_tick()
        self.calendar.start_new_era("开元") # Starts in 712
        # 推进365天 * 24小时 = 8760小时，到达713年
        for _ in range(365 * 24):
            self.calendar.advance_time_tick()
        # 推进5小时
        for _ in range(5):
            self.calendar.advance_time_tick()

        # Era is 开元, year is 2 (713 is the 2nd year of the era started in 712)
        date_str = self.calendar.format_date_era(show_hour=True)
        self.assertEqual(date_str, "开元2年1月6日5点")

    def test_start_from_bc_era(self):
        """测试从其他公元前年份开始"""
        calendar = Calendar(base_year=-100)
        self.assertEqual(calendar.current_gregorian_year, -100)
        # 推进100年 * 360天 * 24小时 = 864000小时
        for _ in range(100 * 360 * 24):
            calendar.advance_time_tick()
        # 从-100年推进100年，会到达公元0年 (我们的日历系统包含0年)
        self.assertEqual(calendar.current_gregorian_year, 0)


class TestCalendarIntegration(unittest.TestCase):
    """测试日历和时间管理器的集成"""

    def setUp(self):
        # Reset BASE_YEAR before each test in this class to ensure isolation
        Calendar.BASE_YEAR = EPOCH_START_YEAR
        self.calendar = Calendar()

    def test_initial_date(self):
        """测试初始日期"""
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR)}年1月1日")

    def test_advancing_time_and_format(self):
        """测试推进时间后的格式化"""
        # 推进365天 * 24小时 = 8760小时
        for _ in range(365 * 24):
            self.calendar.advance_time_tick()
        # After 365 days from start of -2000, it's year -1999, day 6
        self.assertEqual(self.calendar.current_gregorian_year, EPOCH_START_YEAR + 1)
        # 验证时间信息通过get_time_info获取
        info = self.calendar.get_time_info()
        self.assertEqual(info['day_in_year'], 6)
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR) - 1}年1月6日")

    def test_reset_and_format(self):
        """测试重置后格式化"""
        # 推进100天 * 24小时 = 2400小时
        for _ in range(100 * 24):
            self.calendar.advance_time_tick()
        self.calendar.reset()
        self.assertEqual(self.calendar.current_gregorian_year, EPOCH_START_YEAR)
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR)}年1月1日")

    def test_format_with_era(self):
        """测试带年号的格式化"""
        # Go to year 713 AD
        target_year = 713
        initial_year = self.calendar.current_gregorian_year
        # 推进(target_year - initial_year)年 * 360天 * 24小时
        for _ in range((target_year - initial_year) * 360 * 24):
            self.calendar.advance_time_tick()
        self.assertEqual(self.calendar.current_gregorian_year, target_year)

        self.calendar.anchor_era("开元", 713)
        # 推进5天 * 24小时 + 5小时 = 125小时
        for _ in range(5 * 24 + 5):
            self.calendar.advance_time_tick()

        # Year is 713, which is the 1st year of the Kaiyuan era
        date_str = self.calendar.format_date_era(show_hour=True)
        self.assertEqual(date_str, "开元1年1月6日5点")


class TestTimeManagerWithDifferentStart(unittest.TestCase):
    """测试不同起始年份的时间管理器"""

    def test_start_from_ad_1(self):
        """测试从公元1年开始"""
        calendar = Calendar(base_year=1)
        self.assertEqual(calendar.current_gregorian_year, 1)
        # 推进365天 * 24小时 = 8760小时
        for _ in range(365 * 24):
            calendar.advance_time_tick()
        # 我们的年份是360天，所以365天后是2年第6天 (day 1 to 5 are in year 2)
        self.assertEqual(calendar.current_gregorian_year, 2)
        info = calendar.get_time_info()
        self.assertEqual(info['day_in_year'], 6)

    def test_start_from_bc_era(self):
        """测试从其他公元前年份开始"""
        calendar = Calendar(base_year=-100)
        self.assertEqual(calendar.current_gregorian_year, -100)
        # 推进100年 * 360天 * 24小时 = 864000小时
        for _ in range(100 * 360 * 24):
            calendar.advance_time_tick()
        # 从-100年推进100年，会到达公元0年 (我们的日历系统包含0年)
        self.assertEqual(calendar.current_gregorian_year, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)