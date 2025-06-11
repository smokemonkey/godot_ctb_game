import pygame
import sys
from time_system import TimeManager, Calendar, TimeUnit
from ui_components import Button, TextDisplay, InputBox
from font_manager import font_manager

# Initialize pygame
pygame.init()

# Set up display
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("回合制游戏时间系统测试")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# 字体管理已在font_manager中处理

# Game clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Initialize time system
time_manager = TimeManager()
calendar = Calendar(time_manager)

# Initialize UI components
ui_components = []

# Time display
time_display = TextDisplay(20, 20, 300, 150)
ui_components.append(time_display)

# Input box for days
day_input = InputBox(20, 200, 100, 30)
ui_components.append(day_input)

# Input box for hours  
hour_input = InputBox(20, 250, 100, 30)
ui_components.append(hour_input)

# Input box for era name
era_input_box = InputBox(20, 340, 150, 30, input_type="text")
ui_components.append(era_input_box)

# Buttons
def advance_days():
    days = day_input.get_value()
    if days > 0:
        time_manager.advance_time(days, TimeUnit.DAY)
        day_input.clear()

def advance_hours():
    hours = hour_input.get_value()
    if hours > 0:
        time_manager.advance_time(hours, TimeUnit.HOUR)
        hour_input.clear()

def add_era():
    era_name = era_input_box.get_text()
    if era_name:
        time_manager.add_era_node(era_name)
        era_input_box.clear()
    else:
        # 如果输入框为空，使用预设的纪年名称
        era_names = ["开元", "贞观", "永乐", "康熙", "乾隆"]
        current_era_count = len(time_manager._era_nodes)
        if current_era_count < len(era_names):
            time_manager.add_era_node(era_names[current_era_count])

def reset_time():
    time_manager._total_hours = 0
    time_manager._era_nodes.clear()

def advance_1_day():
    time_manager.advance_time(1, TimeUnit.DAY)

def advance_10_days():
    time_manager.advance_time(10, TimeUnit.DAY)

def advance_100_days():
    time_manager.advance_time(100, TimeUnit.DAY)

def advance_1_year():
    time_manager.advance_time(360, TimeUnit.DAY)

# Create buttons
buttons = [
    Button(140, 200, 80, 30, "推进天数", callback=advance_days),
    Button(140, 250, 80, 30, "推进小时", callback=advance_hours),
    Button(180, 340, 80, 30, "添加纪年", callback=add_era),
    Button(20, 390, 60, 30, "重置", callback=reset_time),
    Button(90, 390, 60, 30, "+1天", callback=advance_1_day),
    Button(160, 390, 60, 30, "+10天", callback=advance_10_days),
    Button(230, 390, 70, 30, "+100天", callback=advance_100_days),
    Button(310, 390, 60, 30, "+1年", callback=advance_1_year),
]

ui_components.extend(buttons)

# Labels for input boxes
labels = [
    ("时间显示:", 20, 0),
    ("输入天数:", 20, 180),
    ("输入小时:", 20, 230),
    ("输入纪年名:", 20, 320),
]

# Add some initial test data
time_manager.advance_time(365, TimeUnit.DAY)  # 前进一年多一点
time_manager.add_era_node("开元")  # 添加一个测试纪年

# Update time display
def update_time_display():
    status_text = calendar.get_time_status_text()
    time_display.set_text(status_text)

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
        # Handle UI events
        for component in ui_components:
            component.handle_event(event)
    
    # Update time display
    update_time_display()
    
    # Fill the screen with white color
    screen.fill(WHITE)
    
    # Draw labels
    for label_text, x, y in labels:
        label_font = font_manager.get_label_font(200, 20, label_text)
        label_surface = label_font.render(label_text, True, BLACK)
        screen.blit(label_surface, (x, y))
    
    # Draw UI components
    for component in ui_components:
        component.draw(screen)
    
    # Draw instructions
    instructions = [
        "时间系统测试界面",
        "• 输入数字后点击按钮推进时间",
        "• 快捷按钮可以快速推进时间",
        "• 输入纪年名称后点击添加纪年按钮",
        "• 纪年输入框为空时使用预设纪年",
        "• 重置按钮将时间重置到公元前1000年",
        "• ESC键退出程序"
    ]
    
    y_offset = 450
    for instruction in instructions:
        if instruction.startswith("时间系统测试界面"):
            instruction_font = font_manager.get_font(20)
            text_surface = instruction_font.render(instruction, True, BLACK)
        else:
            instruction_font = font_manager.get_font(14)
            text_surface = instruction_font.render(instruction, True, GRAY)
        screen.blit(text_surface, (20, y_offset))
        y_offset += instruction_font.get_height() + 5
    
    # Update display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit() 