import constants

import pygame
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

# Ground settings
ground_level = HEIGHT - constants.player_size

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
        title_text = font.render("Fate: navy sea", True, constants.WHITE)
        text_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, text_rect)

        # Draw buttons
        font = pygame.font.Font(None, 50)
        start_text = font.render("Start", True, constants.WHITE)
        credits_text = font.render("Credits", True, constants.WHITE)

        
