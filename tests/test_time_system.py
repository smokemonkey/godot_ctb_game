import unittest
import sys
import os

# 添加父目录到Python路径，以便导入game_time包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_time import TimeManager, Calendar, TimeUnit, EraNode


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
    
    def test_set_time_to_day(self):
        """测试跳转到指定天数"""
        # 跳转到当前年第100天
        self.time_manager.set_time_to_day(100)
        self.assertEqual(self.time_manager.current_day_in_year, 100)
        self.assertEqual(self.time_manager.current_year, -722)
        
        # 推进到下一年，再跳转
        self.time_manager.advance_time(365, TimeUnit.DAY)
        self.time_manager.set_time_to_day(50)
        self.assertEqual(self.time_manager.current_day_in_year, 50)
        self.assertEqual(self.time_manager.current_year, -721)
    
    def test_set_time_to_hour(self):
        """测试跳转到指定小时"""
        self.time_manager.set_time_to_hour(15)
        self.assertEqual(self.time_manager.current_hour, 15)
        self.assertEqual(self.time_manager.current_day_in_year, 1)
    
    def test_era_management(self):
        """测试纪年管理"""
        # 添加纪年节点
        self.time_manager.add_era_node("开元")
        
        # 检查纪年是否正确添加
        current_era = self.time_manager.get_current_era()
        self.assertIsNotNone(current_era)
        self.assertEqual(current_era.name, "开元")
        self.assertEqual(current_era.start_year, -722)
        
        # 推进时间后添加新纪年
        self.time_manager.advance_time(3650, TimeUnit.DAY)  # 约10年
        self.time_manager.add_era_node("贞观")
        
        # 检查当前纪年是否为新纪年
        current_era = self.time_manager.get_current_era()
        self.assertEqual(current_era.name, "贞观")
        
        # 检查纪年节点总数
        self.assertEqual(len(self.time_manager._era_nodes), 2)
    
    def test_era_ordering(self):
        """测试纪年节点排序"""
        # 添加多个纪年节点（不按时间顺序）
        self.time_manager.add_era_node("晚期", -900)
        self.time_manager.add_era_node("早期", -950)
        self.time_manager.add_era_node("中期", -925)
        
        # 检查排序是否正确
        eras = self.time_manager._era_nodes
        self.assertEqual(len(eras), 3)
        self.assertEqual(eras[0].name, "早期")
        self.assertEqual(eras[1].name, "中期") 
        self.assertEqual(eras[2].name, "晚期")
    
    def test_get_time_info(self):
        """测试获取时间信息"""
        self.time_manager.advance_time(100, TimeUnit.DAY)
        self.time_manager.advance_time(5, TimeUnit.HOUR)
        
        info = self.time_manager.get_time_info()
        
        self.assertEqual(info['year'], -722)
        self.assertEqual(info['day_in_year'], 101)
        self.assertEqual(info['hour'], 5)
        self.assertEqual(info['total_hours'], 100 * 24 + 5)


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
        # 添加纪年并推进时间
        self.time_manager.add_era_node("开元")
        self.time_manager.advance_time(365, TimeUnit.DAY)  # 推进1年多
        
        date_str = self.calendar.format_date_era()
        self.assertIn("开元", date_str)
        self.assertIn("2年", date_str)  # 开元第2年
    
    def test_time_status_text(self):
        """测试详细时间状态文本"""
        self.time_manager.advance_time(50, TimeUnit.DAY)
        self.time_manager.advance_time(10, TimeUnit.HOUR)
        self.time_manager.add_era_node("测试元年")
        
        status = self.calendar.get_time_status_text()
        
        # 检查是否包含关键信息
        self.assertIn("公历:", status)
        self.assertIn("纪年:", status)
        self.assertIn("年内第51天", status)
        self.assertIn("总计:", status)


class TestEraNode(unittest.TestCase):
    """EraNode数据类的测试用例"""
    
    def test_era_node_creation(self):
        """测试纪年节点创建"""
        era = EraNode("开元", 713)
        self.assertEqual(era.name, "开元")
        self.assertEqual(era.start_year, 713)


class TestIntegration(unittest.TestCase):
    """集成测试用例"""
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        time_manager = TimeManager()
        calendar = Calendar(time_manager)
        
        # 1. 初始状态检查
        self.assertEqual(time_manager.current_year, -722)
        
        # 2. 推进到春秋时期
        time_manager.advance_time(200 * 360, TimeUnit.DAY)  # 推进200年
        self.assertEqual(time_manager.current_year, -522)
        
        # 3. 添加春秋纪年
        time_manager.add_era_node("春秋元年")
        
        # 4. 继续推进到战国
        time_manager.advance_time(300 * 360, TimeUnit.DAY)  # 再推进300年
        self.assertEqual(time_manager.current_year, -222)
        
        # 5. 添加战国纪年
        time_manager.add_era_node("战国元年")
        
        # 6. 检查当前纪年
        current_era = time_manager.get_current_era()
        self.assertEqual(current_era.name, "战国元年")
        
        # 7. 测试格式化显示
        era_date = calendar.format_date_era()
        self.assertIn("战国元年", era_date)
        
        gregorian_date = calendar.format_date_gregorian()
        self.assertIn("公元前222年", gregorian_date)
    
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
        
        # 测试在同一年添加多个纪年
        current_year = time_manager.current_year
        time_manager.add_era_node("纪年A", current_year)
        time_manager.add_era_node("纪年B", current_year)
        
        # 最后添加的应该是当前纪年
        current_era = time_manager.get_current_era()
        self.assertEqual(current_era.name, "纪年B")


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2) 