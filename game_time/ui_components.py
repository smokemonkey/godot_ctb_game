import pygame
from typing import Callable, Optional
from .font_manager import font_manager


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
        self.composition = ""  # 输入法组合状态
        self.composing = False  # 是否正在使用输入法组合
        self.max_length = 20 if input_type == "text" else 10
        self.cursor_pos = 0  # 光标位置
        self.text_offset = 0  # 文本滚动偏移量
        
        # 颜色配置
        self.bg_color = (255, 255, 255)
        self.bg_color_active = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.composition_color = (100, 100, 100)  # 组合字符颜色
        self.border_color = (100, 100, 100)
        self.border_color_active = (0, 100, 200)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                was_active = self.is_active
                self.is_active = self.rect.collidepoint(event.pos)
                # 如果从激活状态变为非激活状态，停止输入法组合
                if was_active and not self.is_active:
                    self.composition = ""
                    self.composing = False
                return self.is_active
        
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                if self.composing and self.composition:
                    # 如果正在组合，删除组合字符
                    self.composition = self.composition[:-1]
                elif self.cursor_pos > 0:
                    # 在光标位置删除字符
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                    self._update_text_offset()
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    # 删除光标右边的字符
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                    self._update_text_offset()
            elif event.key == pygame.K_LEFT:
                # 光标左移
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    self._update_text_offset()
            elif event.key == pygame.K_RIGHT:
                # 光标右移
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                    self._update_text_offset()
            elif event.key == pygame.K_HOME:
                # 光标移到开始
                self.cursor_pos = 0
                self._update_text_offset()
            elif event.key == pygame.K_END:
                # 光标移到末尾
                self.cursor_pos = len(self.text)
                self._update_text_offset()
            elif event.key == pygame.K_RETURN:
                # 确认输入，结束组合状态
                if self.composing and self.composition:
                    self._insert_text(self.composition)
                    self.composition = ""
                    self.composing = False
                return True
            elif event.key == pygame.K_ESCAPE:
                # 取消输入法组合
                self.composition = ""
                self.composing = False
            elif self.input_type == "number" and not self.composing:
                # 数字输入模式 - 严格限制，不使用输入法
                if event.unicode.isdigit() or event.unicode in ['-', '+']:
                    if len(self.text) < self.max_length:
                        self._insert_text(event.unicode)
            return True
        
        # 处理文本输入事件（中文输入法支持）
        elif event.type == pygame.TEXTINPUT and self.is_active and self.input_type == "text":
            if len(self.text) + len(event.text) <= self.max_length:
                self._insert_text(event.text)
                # 结束组合状态
                self.composition = ""
                self.composing = False
            return True
        
        # 处理输入法组合事件
        elif event.type == pygame.TEXTEDITING and self.is_active and self.input_type == "text":
            self.composition = event.text
            self.composing = bool(event.text)
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
        self.cursor_pos = 0
        self.text_offset = 0
    
    def _insert_text(self, text: str) -> None:
        """在光标位置插入文本"""
        if len(self.text) + len(text) <= self.max_length:
            self.text = self.text[:self.cursor_pos] + text + self.text[self.cursor_pos:]
            self.cursor_pos += len(text)
            self._update_text_offset()
    
    def _update_text_offset(self) -> None:
        """更新文本滚动偏移量，确保光标可见"""
        if not self.text:
            self.text_offset = 0
            return
        
        # 计算当前光标位置的像素坐标
        text_before_cursor = self.text[:self.cursor_pos]
        cursor_pixel_pos = self.font.size(text_before_cursor)[0]
        
        # 输入框可显示区域的宽度（减去边距）
        visible_width = self.rect.width - 10
        
        # 如果光标超出右边界，向左滚动
        if cursor_pixel_pos - self.text_offset > visible_width:
            self.text_offset = cursor_pixel_pos - visible_width
        
        # 如果光标超出左边界，向右滚动
        if cursor_pixel_pos < self.text_offset:
            self.text_offset = cursor_pixel_pos
        
        # 确保偏移量不为负数
        self.text_offset = max(0, self.text_offset)
    
    def _get_cursor_pixel_pos(self) -> int:
        """获取光标的像素位置"""
        text_before_cursor = self.text[:self.cursor_pos]
        return self.font.size(text_before_cursor)[0] - self.text_offset

    def draw(self, screen: pygame.Surface) -> None:
        """绘制输入框"""
        # 选择颜色
        bg_color = self.bg_color_active if self.is_active else self.bg_color
        border_color = self.border_color_active if self.is_active else self.border_color
        
        # 绘制背景
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # 创建裁剪区域，防止文本超出输入框
        clip_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, 
                               self.rect.width - 4, self.rect.height - 4)
        screen.set_clip(clip_rect)
        
        # 绘制文本（考虑滚动偏移）
        text_x = self.rect.x + 5 - self.text_offset
        text_y = self.rect.y + 5
        
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            screen.blit(text_surface, (text_x, text_y))
        
        # 绘制输入法组合字符（如果存在）
        if self.composing and self.composition:
            cursor_pixel_pos = self._get_cursor_pixel_pos()
            comp_x = self.rect.x + 5 + cursor_pixel_pos
            comp_surface = self.font.render(self.composition, True, self.composition_color)
            screen.blit(comp_surface, (comp_x, text_y))
            
            # 为组合字符添加下划线标识
            underline_y = text_y + self.font.get_height()
            pygame.draw.line(screen, self.composition_color,
                           (comp_x, underline_y),
                           (comp_x + comp_surface.get_width(), underline_y), 1)
        
        # 取消裁剪
        screen.set_clip(None)
        
        # 绘制光标
        if self.is_active:
            cursor_pixel_pos = self._get_cursor_pixel_pos()
            cursor_x = self.rect.x + 5 + cursor_pixel_pos
            
            # 确保光标在可见区域内
            if self.rect.x + 5 <= cursor_x <= self.rect.right - 5:
                pygame.draw.line(screen, self.text_color, 
                               (cursor_x, self.rect.y + 5), 
                               (cursor_x, self.rect.bottom - 5), 2) 