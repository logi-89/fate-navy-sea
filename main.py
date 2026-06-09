import pygame

from constants import *
from helper import graphics, music
from levels import menu
import levels.level1

pygame.init()

#screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fate: navy sea")

clock = pygame.time.Clock()
   
def run_shop():
    graphics.draw_vertical_gradient(screen, (5, 20, 35), (15, 60, 90))
    selected = 0

if dev_mode:
    levels.level1.intro(screen, clock)
else:
    jukebox = music.Music("F4T3_ navy sea.mp3", loop=True)
    screen = menu.show_title_screen(screen, clock, jukebox)
#menu.shop_(screen, clock, "lentons") 