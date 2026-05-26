import pygame
import threading
from random import randint

# Initialize Pygame
pygame.init()

# Game settings
WIDTH = 1400
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fate: navy sea")

# Game state variables
score = 0
xp = 0
coins = 0
game_over = False
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GROUND_COLOR = (50, 205, 50)
BUTTON_COLOR = (100, 100, 200)
HOVER_COLOR = (150, 150, 255)
BROWN = (128, 0, 0)

# Player settings
player_size = 150
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - player_size
player_speed = 5
player_velocity_y = 0
jump_height = -15
gravity = 1

# Ground settings
ground_level = HEIGHT - player_size

# Function to create a gradient
def draw_gradient(screen, color1, color2):
    for i in range(HEIGHT):
        r = color1[0] + (color2[0] - color1[0]) * i // HEIGHT
        g = color1[1] + (color2[1] - color1[1]) * i // HEIGHT
        b = color1[2] + (color2[2] - color1[2]) * i // HEIGHT
        pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))

# Title screen
def show_title_screen():
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_gradient(screen, (139, 70, 20), (0, 0, 0))

        # Draw title
        font = pygame.font.Font(None, 100)
        title_text = font.render("Fate: navy sea", True, WHITE)
        text_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, text_rect)

        # # Draw buttons
        # font = pygame.font.Font(None, 50)
        # start_text = font.render("Start", True, WHITE)
        # credits_text = font.render("Credits", True, WHITE)

# Death screen
def show_Death():
    font_large = pygame.font.Font(None, 80)
    font_small = pygame.font.Font(None, 50)

    # Draw the death message
    screen.fill((0, 0, 0))
    title_text = font_large.render("You Died!", True, (255, 0, 0))  # Red text
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)


show_title_screen()

