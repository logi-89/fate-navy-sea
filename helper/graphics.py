import pygame
import math

import constants
from constants import *


def draw_waves(surface, offset):
    surf_w, surf_h = surface.get_size()
    base_y = surf_h - 300
    for i in range(10):
        y = base_y + i * 22
        points = []
        for x in range(0, surf_w + 20, 20):
            wave = math.sin((x * 0.015) + offset + i * 0.4) * 8
            points.append((x, y + wave))
        if len(points) > 1:
            pygame.draw.aalines(surface, (170, 230, 255), False, points)


def draw_vertical_gradient(surface, top_color, bottom_color):
    surf_w, surf_h = surface.get_size()
    for y in range(surf_h):
        t = y / surf_h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (surf_w, y))


def update_lore_display(screen, dt=1.0):
    if constants.lore_display_timer > 0 and constants.lore_display_text:
        fade_threshold = 60
        alpha = 255

        if constants.lore_display_timer <= fade_threshold:
            alpha = int((constants.lore_display_timer / fade_threshold) * 255)

        lore_display(screen, constants.lore_display_text, alpha)
        constants.lore_display_timer -= dt


def lore_display(screen, lore_display_text, alpha=255):
    lore_font = pygame.font.Font(None, 26)
    pad_x, pad_y = 28, 18
    max_text_w = 680
    words = lore_display_text.split()
    lines = []
    cur_line = ""
    for word in words:
        test = (cur_line + " " + word).strip()
        if lore_font.size(test)[0] <= max_text_w:
            cur_line = test
        else:
            lines.append(cur_line)
            cur_line = word
    if cur_line:
        lines.append(cur_line)

    line_h = lore_font.get_height() + 4
    panel_w = max_text_w + pad_x * 2
    panel_h = line_h * len(lines) + pad_y * 2 + 36

    scr_w, scr_h = screen.get_size()
    panel_x = scr_w // 2 - panel_w // 2
    panel_y = scr_h // 2 - panel_h // 2

    surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (8, 28, 44, 210), (0, 0, panel_w, panel_h), border_radius=10)

    for band_i, band_y_off in enumerate(range(0, panel_h, 18)):
        band_alpha = int(12 * (1 - band_i / (panel_h // 18 + 1)))
        pygame.draw.rect(
            surf,
            (40, 140, 160, band_alpha),
            (0, band_y_off, panel_w, 9),
            border_radius=4,
        )

    pygame.draw.rect(
        surf, (80, 200, 185, 220), (0, 0, panel_w, panel_h), 2, border_radius=10
    )
    pygame.draw.line(surf, (160, 255, 240, 80), (12, 3), (panel_w - 12, 3), 1)

    header_surf = pygame.font.Font(None, 22).render(
        "~  T R A N S M I S S I O N  ~", True, (100, 220, 200)
    )
    surf.blit(header_surf, (panel_w // 2 - header_surf.get_width() // 2, pad_y - 4))

    sep_y = pad_y + 20
    pygame.draw.line(
        surf, (50, 140, 150, 160), (pad_x, sep_y), (panel_w - pad_x, sep_y), 1
    )

    for li, line in enumerate(lines):
        t_surf = lore_font.render(line, True, (190, 240, 230))
        surf.blit(t_surf, (pad_x, sep_y + 8 + li * line_h))

    if alpha < 255:
        surf.set_alpha(alpha)
    screen.blit(surf, (panel_x, panel_y))
