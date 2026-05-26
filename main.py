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

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GROUND_COLOR = (50, 205, 50)
BUTTON_COLOR = (100, 100, 200)
HOVER_COLOR = (150, 150, 255)
BROWN = (128, 0, 0)

