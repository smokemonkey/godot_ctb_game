import unittest
import sys
import os

# 添加父目录到Python路径，以便导入game_time包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_time import TimeManager, Calendar, TimeUnit


class TestTimeManager(unittest.TestCase):
    """TimeManager类的测试用例"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.time_manager = TimeManager()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.time_manager.current_year, -722)
        self.assertEqual(self.time_manager.current_month, 1)
        self.assertEqual(self.time_manager.current_day_in_month, 1)
        self.assertEqual(self.time_manager.current_day_in_year, 1)
        self.assertEqual(self.time_manager.current_hour, 0)
    
    def test_advance_days(self):
        """测试按天推进时间"""
        # 推进1天
        self.time_manager.advance_time(1, TimeUnit.DAY)
        self.assertEqual(self.time_manager.current_day_in_year, 2)
        self.assertEqual(self.time_manager.current_hour, 0)
        
        # 推进30天（跨月）
        self.time_manager.advance_time(30, TimeUnit.DAY)
        self.assertEqual(self.time_manager.current_day_in_year, 32)
        self.assertEqual(self.time_manager.current_month, 2)
        self.assertEqual(self.time_manager.current_day_in_month, 2)
    
    def test_advance_hours(self):
        """测试按小时推进时间"""
        # 推进5小时
        self.time_manager.advance_time(5, TimeUnit.HOUR)
        self.assertEqual(self.time_manager.current_hour, 5)
        self.assertEqual(self.time_manager.current_day_in_year, 1)
        
        # 推进20小时（跨天）
        self.time_manager.advance_time(20, TimeUnit.HOUR)
        self.assertEqual(self.time_manager.current_hour, 1)  # 5 + 20 = 25 -> 1
        self.assertEqual(self.time_manager.current_day_in_year, 2)
    
    def test_advance_full_year(self):
        """测试推进一整年"""
        self.time_manager.advance_time(360, TimeUnit.DAY)
        self.assertEqual(self.time_manager.current_year, -721)
        self.assertEqual(self.time_manager.current_day_in_year, 1)
        self.assertEqual(self.time_manager.current_month, 1)
    
    def test_month_calculation(self):
        """测试月份计算"""
        # 测试各月份边界
        test_cases = [
            (1, 1, 1),    # 第1天 -> 1月1日
            (30, 1, 30),  # 第30天 -> 1月30日  
            (31, 2, 1),   # 第31天 -> 2月1日
            (60, 2, 30),  # 第60天 -> 2月30日
            (61, 3, 1),   # 第61天 -> 3月1日
            (360, 12, 30) # 第360天 -> 12月30日
        ]
        
        for day_in_year, expected_month, expected_day_in_month in test_cases:
            with self.subTest(day=day_in_year):
                self.time_manager._total_hours = (day_in_year - 1) * 24
                self.assertEqual(self.time_manager.current_month, expected_month)
                self.assertEqual(self.time_manager.current_day_in_month, expected_day_in_month)
    
    def test_anchor_era(self):
        """测试纪元锚定功能"""
        # 推进到公元713年
        target_year = 713
        years_to_advance = target_year - self.time_manager.current_year
        self.time_manager.advance_time(years_to_advance * 360, TimeUnit.DAY)
        
        # 锚定开元纪元
        self.time_manager.anchor_era("开元", 713)
        
        # 检查锚定是否生效
        self.assertEqual(self.time_manager.get_current_era_name(), "开元")
        self.assertEqual(self.time_manager.get_current_era_year(), 1)  # 开元元年
        
        # 推进时间，检查纪元年份计算
        self.time_manager.advance_time(360, TimeUnit.DAY)  # 推进1年
        self.assertEqual(self.time_manager.get_current_era_year(), 2)  # 开元二年
    
    def test_anchor_era_future_restriction(self):
        """测试锚定未来时期的限制"""
        current_year = self.time_manager.current_year
        future_year = current_year + 100
        
        # 尝试锚定到未来年份，应该抛出异常
        with self.assertRaises(ValueError) as context:
            self.time_manager.anchor_era("未来纪元", future_year)
        
        self.assertIn("不能锚定到未来时期", str(context.exception))
    
    def test_start_new_era(self):
        """测试改元功能"""
        # 推进一些时间
        self.time_manager.advance_time(1000, TimeUnit.DAY)
        current_year = self.time_manager.current_year
        
        # 开始新纪元
        self.time_manager.start_new_era("永徽")
        
        # 检查改元是否成功
        self.assertEqual(self.time_manager.get_current_era_name(), "永徽")
        self.assertEqual(self.time_manager.get_current_era_year(), 1)  # 永徽元年
        
        # 检查锚定信息
        info = self.time_manager.get_time_info()
        self.assertEqual(info['current_anchor'], ("永徽", current_year))
    
    def test_era_without_anchor(self):
        """测试无锚定时的纪元状态"""
        # 初始状态下没有锚定
        self.assertIsNone(self.time_manager.get_current_era_name())
        self.assertIsNone(self.time_manager.get_current_era_year())
    
    def test_get_time_info(self):
        """测试获取时间信息"""
        self.time_manager.advance_time(100, TimeUnit.DAY)
        self.time_manager.advance_time(5, TimeUnit.HOUR)
        
        info = self.time_manager.get_time_info()
        
        self.assertEqual(info['year'], -722)
        self.assertEqual(info['day_in_year'], 101)
        self.assertEqual(info['hour'], 5)
        self.assertEqual(info['total_hours'], 100 * 24 + 5)
        self.assertIsNone(info['current_anchor'])  # 初始无锚定
    
    def test_reset(self):
        """测试重置功能"""
        # 推进时间并设置锚定
        self.time_manager.advance_time(1000, TimeUnit.DAY)
        self.time_manager.start_new_era("测试纪元")
        
        # 重置
        self.time_manager.reset()
        
        # 检查是否完全重置
        self.assertEqual(self.time_manager.current_year, -722)
        self.assertEqual(self.time_manager.current_day_in_year, 1)
        self.assertEqual(self.time_manager.current_hour, 0)
        self.assertIsNone(self.time_manager.get_current_era_name())
        self.assertIsNone(self.time_manager._current_anchor)


class TestCalendar(unittest.TestCase):
    """Calendar类的测试用例"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.time_manager = TimeManager()
        self.calendar = Calendar(self.time_manager)
    
    def test_gregorian_format_bc(self):
        """测试公元前日期格式化"""
        # 默认公元前722年（鲁隐公元年）
        date_str = self.calendar.format_date_gregorian()
        self.assertEqual(date_str, "公元前722年1月1日")
        
        # 带小时显示
        date_str_with_hour = self.calendar.format_date_gregorian(show_hour=True)
        self.assertEqual(date_str_with_hour, "公元前722年1月1日0点")
    
    def test_gregorian_format_ad(self):
        """测试公元后日期格式化"""
        # 推进到公元后
        self.time_manager.advance_time(360000, TimeUnit.DAY)  # 推进1000年
        
        date_str = self.calendar.format_date_gregorian()
        expected_year = -722 + (360000 // 360)
        self.assertIn(f"公元{expected_year}年", date_str)
    
    def test_era_format_without_era(self):
        """测试无纪年时的格式化"""
        date_str = self.calendar.format_date_era()
        # 无纪年时应该回退到公历格式
        self.assertEqual(date_str, "公元前722年1月1日")
    
    def test_era_format_with_era(self):
        """测试有纪年时的格式化"""
        # 推进到公元713年并锚定开元
        target_year = 713
        years_to_advance = target_year - self.time_manager.current_year
        self.time_manager.advance_time(years_to_advance * 360, TimeUnit.DAY)
        self.time_manager.anchor_era("开元", 713)
        
        # 推进1年多
        self.time_manager.advance_time(365, TimeUnit.DAY)
        
        date_str = self.calendar.format_date_era()
        self.assertIn("开元", date_str)
        self.assertIn("2年", date_str)  # 开元第2年
    
    def test_time_status_text(self):
        """测试详细时间状态文本"""
        self.time_manager.advance_time(50, TimeUnit.DAY)
        self.time_manager.advance_time(10, TimeUnit.HOUR)
        self.time_manager.start_new_era("测试元年")
        
        status = self.calendar.get_time_status_text()
        
        # 检查是否包含关键信息
        self.assertIn("公历:", status)
        self.assertIn("纪年:", status)
        self.assertIn("年内第51天", status)
        self.assertIn("总计:", status)
        self.assertIn("锚定:", status)  # 应该显示锚定信息


class TestIntegration(unittest.TestCase):
    """集成测试用例"""
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        time_manager = TimeManager()
        calendar = Calendar(time_manager)
        
        # 1. 初始状态检查
        self.assertEqual(time_manager.current_year, -722)
        
        # 2. 推进到唐朝开元年间
        target_year = 713
        years_to_advance = target_year - time_manager.current_year
        time_manager.advance_time(years_to_advance * 360, TimeUnit.DAY)
        self.assertEqual(time_manager.current_year, 713)
        
        # 3. 锚定开元纪年
        time_manager.anchor_era("开元", 713)
        
        # 4. 继续推进几年
        time_manager.advance_time(5 * 360, TimeUnit.DAY)  # 推进5年
        self.assertEqual(time_manager.current_year, 718)
        
        # 5. 检查当前纪年
        self.assertEqual(time_manager.get_current_era_name(), "开元")
        self.assertEqual(time_manager.get_current_era_year(), 6)  # 开元六年
        
        # 6. 改元到天宝
        time_manager.start_new_era("天宝")
        
        # 7. 检查改元结果
        self.assertEqual(time_manager.get_current_era_name(), "天宝")
        self.assertEqual(time_manager.get_current_era_year(), 1)  # 天宝元年
        
        # 8. 测试格式化显示
        era_date = calendar.format_date_era()
        self.assertIn("天宝", era_date)
        self.assertIn("1年", era_date)
        
        gregorian_date = calendar.format_date_gregorian()
        self.assertIn("公元718年", gregorian_date)
    
    def test_edge_cases(self):
        """测试边界情况"""
        time_manager = TimeManager()
        
        # 测试推进0时间
        original_hour = time_manager.current_hour
        time_manager.advance_time(0, TimeUnit.DAY)
        self.assertEqual(time_manager.current_hour, original_hour)
        
        # 测试大量时间推进
        time_manager.advance_time(1000000, TimeUnit.DAY)
        self.assertGreater(time_manager.current_year, 1000)  # 应该到达公元后很久
        
        # 测试锚定过去年份
        current_year = time_manager.current_year
        past_year = current_year - 100
        time_manager.anchor_era("过去纪元", past_year)
        
        # 当前年份应该显示为该纪元的很多年后
        era_year = time_manager.get_current_era_year()
        self.assertGreater(era_year, 100)
    
    def test_anchor_replacement(self):
        """测试锚定替换"""
        time_manager = TimeManager()
        
        # 推进到某个年份
        time_manager.advance_time(1000 * 360, TimeUnit.DAY)
        current_year = time_manager.current_year
        
        # 设置第一个锚定
        time_manager.anchor_era("第一纪元", current_year - 50)
        self.assertEqual(time_manager.get_current_era_name(), "第一纪元")
        self.assertEqual(time_manager.get_current_era_year(), 51)
        
        # 设置第二个锚定，应该替换第一个
        time_manager.anchor_era("第二纪元", current_year - 20)
        self.assertEqual(time_manager.get_current_era_name(), "第二纪元")
        self.assertEqual(time_manager.get_current_era_year(), 21)


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2) 