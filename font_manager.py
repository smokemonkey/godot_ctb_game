import pygame
from typing import Dict, Tuple, Optional

class FontManager:
    """字体管理器 - 提供自适应字体功能"""
    
    def __init__(self):
        self.font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}
        self.chinese_font_name = self._find_chinese_font()
        
    def _find_chinese_font(self) -> str:
        """寻找支持中文的字体"""
        chinese_fonts = [
            "arialunicode",
            "stheitimedium", 
            "stheitilight",
        ]
        
        def test_chinese_font(font_name: str, test_char: str = "中") -> bool:
            try:
                test_font = pygame.font.SysFont(font_name, 20)
                surface = test_font.render(test_char, True, (0, 0, 0))
                # 更宽松的检测条件 - 只要能渲染就认为支持
                return surface.get_width() > 5
            except Exception as e:
                print(f"字体 {font_name} 测试失败: {e}")
                return False
        
        # 先测试一下有哪些字体可用
        available_fonts = pygame.font.get_fonts()
        print(f"系统可用字体数量: {len(available_fonts)}")
        
        for font_name in chinese_fonts:
            print(f"测试字体: {font_name}")
            if font_name in available_fonts:
                print(f"  - 字体存在于系统中")
                if test_chinese_font(font_name):
                    print(f"  - 支持中文渲染")
                    print(f"使用 {font_name} 字体 - 支持中文显示")
                    return font_name
                else:
                    print(f"  - 不支持中文渲染")
            else:
                print(f"  - 字体不存在于系统中")
        
        # 如果都不行，直接使用arialunicode，不再测试
        print("强制使用 arialunicode 字体")
        return "arialunicode"
    
    def get_font(self, size: int) -> pygame.font.Font:
        """获取指定大小的字体"""
        cache_key = (self.chinese_font_name, size)
        
        if cache_key not in self.font_cache:
            try:
                font = pygame.font.SysFont(self.chinese_font_name, size)
                self.font_cache[cache_key] = font
            except:
                font = pygame.font.Font(None, size)
                self.font_cache[cache_key] = font
                
        return self.font_cache[cache_key]
    
    def get_adaptive_font(self, rect_width: int, rect_height: int, 
                         text: str = "测试文字Ag", scale_factor: float = 0.6) -> pygame.font.Font:
        """获取自适应大小的字体
        
        Args:
            rect_width: 控件宽度
            rect_height: 控件高度  
            text: 用于测试的文本
            scale_factor: 缩放因子，控制字体相对于控件的大小
        """
        # 从控件高度估算字体大小
        estimated_size = int(rect_height * scale_factor)
        
        # 限制字体大小范围
        min_size, max_size = 10, 48
        estimated_size = max(min_size, min(max_size, estimated_size))
        
        # 获取字体
        font = self.get_font(estimated_size)
        
        # 检查文本是否适合控件宽度，如果不适合则缩小
        text_width = font.size(text)[0]
        target_width = int(rect_width * 0.9)  # 留10%边距
        
        while text_width > target_width and estimated_size > min_size:
            estimated_size -= 1
            font = self.get_font(estimated_size)
            text_width = font.size(text)[0]
            
        return font
    
    def get_button_font(self, button_width: int, button_height: int, text: str) -> pygame.font.Font:
        """获取适合按钮的字体"""
        return self.get_adaptive_font(button_width, button_height, text, 0.4)
    
    def get_label_font(self, label_width: int, label_height: int, text: str) -> pygame.font.Font:
        """获取适合标签的字体"""
        return self.get_adaptive_font(label_width, label_height, text, 0.7)
    
    def get_input_font(self, input_width: int, input_height: int) -> pygame.font.Font:
        """获取适合输入框的字体"""
        return self.get_adaptive_font(input_width, input_height, "输入文字123", 0.5)
    
    def get_display_font(self, display_width: int, display_height: int) -> pygame.font.Font:
        """获取适合显示区域的字体"""
        return self.get_adaptive_font(display_width, display_height, "显示文字", 0.08)

# 全局字体管理器实例
font_manager = FontManager() 