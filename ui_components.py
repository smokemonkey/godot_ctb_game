import pygame
from typing import Callable, Optional
from font_manager import font_manager


class Button:
    """简单的按钮组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 font: Optional[pygame.font.Font] = None, callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font or font_manager.get_button_font(width, height, text)
        self.callback = callback
        self.is_pressed = False
        self.is_hovered = False
        
        # 颜色配置
        self.bg_color = (200, 200, 200)
        self.bg_color_hover = (220, 220, 220)
        self.bg_color_pressed = (180, 180, 180)
        self.text_color = (0, 0, 0)
        self.border_color = (100, 100, 100)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件，返回是否处理了事件"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return self.is_hovered
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.is_pressed and self.rect.collidepoint(event.pos):
                    if self.callback:
                        self.callback()
                    self.is_pressed = False
                    return True
                self.is_pressed = False
        
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """绘制按钮"""
        # 选择背景颜色
        if self.is_pressed:
            bg_color = self.bg_color_pressed
        elif self.is_hovered:
            bg_color = self.bg_color_hover
        else:
            bg_color = self.bg_color
        
        # 绘制按钮背景
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # 绘制文本
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class TextDisplay:
    """文本显示组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, font: Optional[pygame.font.Font] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font or font_manager.get_display_font(width, height)
        self.text_lines: list[str] = []
        self.line_height = self.font.get_height() + 2
        
        # 颜色配置
        self.bg_color = (240, 240, 240)
        self.text_color = (0, 0, 0)
        self.border_color = (150, 150, 150)
    
    def set_text(self, text: str) -> None:
        """设置显示文本"""
        self.text_lines = text.split('\n')
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件（TextDisplay不需要处理事件，返回False）"""
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """绘制文本显示区域"""
        # 绘制背景
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # 绘制文本
        y_offset = self.rect.y + 5
        for line in self.text_lines:
            if y_offset + self.line_height > self.rect.bottom:
                break  # 超出显示区域
            
            text_surface = self.font.render(line, True, self.text_color)
            screen.blit(text_surface, (self.rect.x + 5, y_offset))
            y_offset += self.line_height


class InputBox:
    """简单的输入框组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, font: Optional[pygame.font.Font] = None, 
                 input_type: str = "number"):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font or font_manager.get_input_font(width, height)
        self.text = ""
        self.is_active = False
        self.input_type = input_type  # "number" 或 "text"
        self.composition = ""  # 中文输入法组合字符
        
        # 颜色配置
        self.bg_color = (255, 255, 255)
        self.bg_color_active = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.border_color = (100, 100, 100)
        self.border_color_active = (0, 100, 200)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.is_active = self.rect.collidepoint(event.pos)
                return self.is_active
        
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                if self.text:
                    self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif self.input_type == "number":
                # 数字输入模式 - 严格限制
                if event.unicode.isdigit() or event.unicode in ['-', '+']:
                    self.text += event.unicode
            elif self.input_type == "text":
                # 文本输入模式 - 宽松策略，支持所有字符
                if event.unicode and len(event.unicode) == 1 and len(self.text) < 20:
                    # 接受所有单字符输入，包括中文
                    self.text += event.unicode
            return True
        
        # 尝试处理文本输入事件（对中文输入法更友好）
        elif event.type == pygame.TEXTINPUT and self.is_active and self.input_type == "text":
            if len(self.text) < 20:
                self.text += event.text
            return True
        
        return False
    
    def get_value(self) -> int:
        """获取输入的数值"""
        try:
            return int(self.text) if self.text else 0
        except ValueError:
            return 0
    
    def get_text(self) -> str:
        """获取输入的文本"""
        return self.text.strip()
    
    def clear(self) -> None:
        """清空输入"""
        self.text = ""
    
    def draw(self, screen: pygame.Surface) -> None:
        """绘制输入框"""
        # 选择颜色
        bg_color = self.bg_color_active if self.is_active else self.bg_color
        border_color = self.border_color_active if self.is_active else self.border_color
        
        # 绘制背景
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # 绘制文本
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        # 绘制光标
        if self.is_active:
            cursor_x = self.rect.x + 5
            if self.text:
                text_surface = self.font.render(self.text, True, self.text_color)
                cursor_x += text_surface.get_width()
            
            pygame.draw.line(screen, self.text_color, 
                           (cursor_x, self.rect.y + 5), 
                           (cursor_x, self.rect.bottom - 5), 2) 