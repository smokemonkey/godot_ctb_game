import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_system.game_time.time_system import TimeManager, Calendar
from game_system.game_time.time_unit import TimeUnit
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

    def test_era_anchor(self):
        """测试设置年号锚点"""
        self.time_manager.set_era_anchor("大汉", -140)
        self.time_manager.advance_time_to_year(-130)

        self.assertEqual(self.time_manager.get_current_era_name(), "大汉")
        self.assertEqual(self.time_manager.get_current_era_year(), 11)

    def test_era_before_anchor(self):
        """测试锚点前的年号"""
        self.time_manager.set_era_anchor("大汉", -140)
        self.time_manager.advance_time_to_year(-200)
        self.assertIsNone(self.time_manager.get_current_era_name())
        self.assertIsNone(self.time_manager.get_current_era_year())


class TestCalendarIntegration(unittest.TestCase):
    """测试日历集成"""

    def setUp(self):
        self.time_manager = TimeManager()
        self.calendar = Calendar(self.time_manager)

    def test_date_formatting(self):
        """测试日期格式化"""
        date_str = self.calendar.format_date_gregorian(show_hour=False)
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR)}年1月1日")

        date_str_with_hour = self.calendar.format_date_gregorian(show_hour=True)
        self.assertEqual(date_str_with_hour, f"公元前{abs(EPOCH_START_YEAR)}年1月1日0点")

    def test_date_formatting_after_advance(self):
        """测试时间推进后的日期格式化"""
        # 推进1000天 (2年又280天)
        self.time_manager.advance_time(1000, TimeUnit.DAY)
        expected_year = EPOCH_START_YEAR + 2
        self.assertEqual(self.time_manager.current_year, expected_year)

        date_str = self.calendar.format_date_gregorian(show_hour=False)
        self.assertIn(str(abs(expected_year)), date_str)

    def test_reset_and_format(self):
        """测试重置后格式化"""
        self.time_manager.advance_time(100, TimeUnit.DAY)
        self.time_manager.reset()
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, f"公元前{abs(EPOCH_START_YEAR)}年1月1日0点")


class TestTimeManagerWithDifferentStart(unittest.TestCase):
    """测试不同起始年份的时间管理器"""

    def test_start_from_ad_1(self):
        """测试从公元1年开始"""
        time_manager = TimeManager(start_year=1)
        self.assertEqual(time_manager.current_year, 1)
        time_manager.advance_time(365, TimeUnit.DAY)
        # 我们的年份是360天，所以365天后是2年第5天
        self.assertEqual(time_manager.current_year, 2)
        self.assertEqual(time_manager.current_day_in_year, 5)

    def test_start_from_bc_era(self):
        """测试从其他公元前年份开始"""
        time_manager = TimeManager(start_year=-100)
        self.assertEqual(time_manager.current_year, -100)
        time_manager.advance_time(360 * 100, TimeUnit.DAY) # 推进100年
        # 应该到达公元1年（没有公元0年）
        self.assertEqual(time_manager.current_year, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)