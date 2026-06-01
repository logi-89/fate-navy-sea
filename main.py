import pygame

from constants import *
from helper import graphics
from levels import menu

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fate: navy sea")

clock = pygame.time.Clock()
   
def run_shop():
    graphics.draw_vertical_gradient(screen, (5, 20, 35), (15, 60, 90))
    selected = 0

menu.show_title_screen(screen, clock) 
#menu.shop_(screen, clock, "lentons") 