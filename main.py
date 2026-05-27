import pygame
import threading
from random import randint
import math
import constants

pygame.init()

WIDTH = 1400
HEIGHT = 850
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fate: navy sea")

clock = pygame.time.Clock()

# Button Colors for Title Screen
BUTTON_COLOR = (40, 80, 120)
HOVER_COLOR = (60, 110, 170)

# Physics
GRAVITY          = 0.7
MAX_FALL_SPEED   = 18
JUMP_POWER       = -16
PLAYER_SPEED     = 5
DOUBLE_JUMP_POWER= 0 #-13

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

        # Sunlight + glow
        pygame.draw.circle(screen, (160, 220, 255), (WIDTH // 2, 180), 90)
        pygame.draw.circle(screen, (200, 245, 255), (WIDTH // 2, 180), 55)

        # Water surface
        pygame.draw.rect(screen, (10, 45, 75), (0, 430, WIDTH, 270))
        draw_waves(screen, t)

        title_text = title_font.render("Fate: Navy Sea", True, constants.WHITE)
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
        pygame.draw.rect(screen, constants.WHITE, button_rect, 3, border_radius=18)

        start_text = button_font.render("Start", True, constants.WHITE)
        start_rect = start_text.get_rect(center=button_rect.center)
        screen.blit(start_text, start_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    intro()
                    return True

        pygame.display.flip()
        clock.tick(60)
        t += 0.03

#  SHOP SCREEN
SHOP_ITEMS = [
    {"name": "Health Flask",      "desc": "+1 flask (heals 40 HP when used)",   "cost": 15,  "key": "flask"},
    {"name": "Sword Upgrade",     "desc": "+15 sword damage",                   "cost": 30,  "key": "sword_dmg"},
    {"name": "Water Gun Ammo +3",   "desc": "+3 balloon capacity",                "cost": 20,  "key": "balloon_ammo"},
    {"name": "Max HP +25",        "desc": "Increase maximum health",            "cost": 40,  "key": "max_hp"},
    {"name": "Sea Boots",         "desc": "+1 speed permanently",               "cost": 50,  "key": "speed"},
    {"name": "Revive Token",      "desc": "Auto-revive once with 30 HP",        "cost": 80,  "key": "revive"},
]

def run_shop():
    # Background
    draw_vertical_gradient(screen, (5, 20, 35), (15, 60, 90))
    selected = 0
    # Platforms (X, Y, Width, Height)

def introLORE():
    screen.fill(constants.BLACK)

#intro aka the start of the game
def intro():

    introLORE()
    print("le bron")
    levelONE()


def levelONE():
    running = True
    
    # Simple Player Setup TESTING
    player_rect = pygame.Rect(100, 100, 40, 60)
    player_vel_y = 0
    is_grounded = False
    can_double_jump = True

    # Platforms (X, Y, Width, Height)
    platforms = [
        pygame.Rect(0, 600, 1200, 100),       # Starting Dock
        pygame.Rect(400, 480, 200, 30),       # Floating crate 1
        pygame.Rect(750, 400, 250, 30),       # Floating crate 2
        pygame.Rect(1150, 520, 300, 30),      # Low bridge
        pygame.Rect(1550, 600, 1500, 100),     # Main island shore
        pygame.Rect(1800, 450, 200, 40),       # Elevated cliff ledge
        pygame.Rect(2200, 350, 300, 40),       # High watchtower deck
    ]
    
    # Camera variable to track world scrolling
    camera_x = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    if is_grounded:
                        player_vel_y = JUMP_POWER
                        is_grounded = False
                        can_double_jump = True
                    elif can_double_jump:
                        player_vel_y = DOUBLE_JUMP_POWER
                        can_double_jump = False

        keys = pygame.key.get_pressed()
        move_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += PLAYER_SPEED

        player_rect.x += move_x

        player_vel_y += GRAVITY
        if player_vel_y > MAX_FALL_SPEED:
            player_vel_y = MAX_FALL_SPEED
        player_rect.y += player_vel_y

        is_grounded = False
        for plat in platforms:
            if player_rect.colliderect(plat):
                if player_vel_y > 0 and player_rect.bottom - player_vel_y <= plat.top + 4:
                    player_rect.bottom = plat.top
                    player_vel_y = 0
                    is_grounded = True
                    can_double_jump = True
                elif player_vel_y < 0 and player_rect.top - player_vel_y >= plat.bottom - 4:
                    player_rect.top = plat.bottom
                    player_vel_y = 0

        if player_rect.y > HEIGHT + 200:
            player_rect.x = 100
            player_rect.y = 100
            player_vel_y = 0

        camera_x = player_rect.x - WIDTH // 2

        draw_vertical_gradient(screen, constants.SEA_MID, constants.SEA_LIGHT)

        for plat in platforms:
            view_rect = pygame.Rect(plat.x - camera_x, plat.y, plat.width, plat.height)
            if view_rect.right > 0 and view_rect.left < WIDTH:
                pygame.draw.rect(screen, constants.STONE if "cliff" in str(plat) else constants.SAND, view_rect)
                pygame.draw.rect(screen, constants.STONE_DARK, view_rect, 2)

        # Draw Player
        player_view_rect = pygame.Rect(player_rect.x - camera_x, player_rect.y, player_rect.width, player_rect.height)
        pygame.draw.rect(screen, constants.ORANGE, player_view_rect, border_radius=4)
        pygame.draw.rect(screen, constants.GOLD, player_view_rect, 3, border_radius=4)

        # UI Instructions overlay
        ui_font = pygame.font.Font(None, 30)
        instructions = ui_font.render("A / D to Move | SPACE to Jump", True, constants.WHITE)
        screen.blit(instructions, (20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

show_title_screen()