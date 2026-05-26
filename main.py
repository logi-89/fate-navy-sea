import pygame
import threading
from random import randint
import math

pygame.init()

WIDTH = 1400
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fate: navy sea")

clock = pygame.time.Clock()

WHITE = (245, 250, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (8, 24, 48)
MID_BLUE = (18, 74, 122)
LIGHT_BLUE = (85, 170, 220)
SEA_GREEN = (40, 140, 160)
BUTTON_COLOR = (30, 90, 150)
HOVER_COLOR = (55, 130, 210)

def draw_vertical_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_waves(surface, offset):
    for i in range(10):
        y = 470 + i * 22
        points = []
        for x in range(0, WIDTH + 20, 20):
            wave = math.sin((x * 0.015) + offset + i * 0.4) * 8
            points.append((x, y + wave))
        if len(points) > 1:
            pygame.draw.aalines(surface, (170, 230, 255), False, points)


def show_title_screen():
    running = True
    t = 0

    title_font = pygame.font.Font(None, 110)
    sub_font = pygame.font.Font(None, 44)
    button_font = pygame.font.Font(None, 56)

    button_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 80, 240, 70)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        hovered = button_rect.collidepoint(mouse_pos)

        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))

        # Sunlight / glow
        pygame.draw.circle(screen, (160, 220, 255), (WIDTH // 2, 180), 90)
        pygame.draw.circle(screen, (200, 245, 255), (WIDTH // 2, 180), 55)

        # Water surface
        pygame.draw.rect(screen, (10, 45, 75), (0, 430, WIDTH, 270))
        draw_waves(screen, t)

        # Title text
        title_text = title_font.render("Fate: Navy Sea", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)

        sub_text = sub_font.render("Set sail into the storm", True, (220, 245, 255))
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 65))
        screen.blit(sub_text, sub_rect)

        # Button
        pygame.draw.rect(
            screen,
            HOVER_COLOR if hovered else BUTTON_COLOR,
            button_rect,
            border_radius=18
        )
        pygame.draw.rect(screen, WHITE, button_rect, 3, border_radius=18)

        start_text = button_font.render("Start", True, WHITE)
        start_rect = start_text.get_rect(center=button_rect.center)
        screen.blit(start_text, start_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    running = False

        pygame.display.flip()
        clock.tick(60)
        t += 0.03

show_title_screen()
