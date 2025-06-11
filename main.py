import pygame
import sys

# Initialize pygame
pygame.init()

# Set up display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blank Game Window")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

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
    
    # Fill the screen with white color
    screen.fill(WHITE)
    
    # Update display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit() 