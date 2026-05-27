import pygame
import threading
from random import randint
import math
import constants
import maps

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
DOUBLE_JUMP_POWER= 0 # -13
TILE_SIZE = 50  # Each tile is 50x50 pixels

def build_platforms_from_map(tile_map, tile_size=TILE_SIZE):
    """
        # -> wall / solid platform
        ? -> paper clip pickup
        ! -> breakable door (3 hits)
        _ -> elevator platform (moves up/down)
        ^ -> animated door (opens upward)
    """
    platforms       = []
    breakable_doors = []
    paperclips      = []
    elevators       = []
    animated_doors  = []

    for row_idx, row in enumerate(tile_map):
        y   = row_idx * tile_size
        col = 0
        while col < len(row):
            ch = row[col]

            if ch == '#':
                start_col = col
                while col < len(row) and row[col] == '#':
                    col += 1
                width = (col - start_col) * tile_size
                platforms.append(pygame.Rect(start_col * tile_size, y, width, tile_size))

            elif ch == '!':
                start_col = col
                while col < len(row) and row[col] == '!':
                    col += 1
                width = (col - start_col) * tile_size
                rect  = pygame.Rect(start_col * tile_size, y, width, tile_size)
                breakable_doors.append({"rect": rect, "hp": 3, "broken": False})

            elif ch == '_':
                # Elevator: stores origin_y so it can oscillate up/down
                rect = pygame.Rect(col * tile_size, y, tile_size * 2, tile_size // 2)
                elevators.append({
                    "rect":     rect,
                    "origin_y": y,
                    "range":    150,   # pixels it travels up/down
                    "speed":    1.2,   # pixels per frame
                    "dir":      1,     # 1 = moving down, -1 = moving up
                })
                col += 2  # elevator occupies 2 tiles wide

            elif ch == '^':
                # Animated door: slides upward when player presses E nearby
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size * 2)
                animated_doors.append({
                    "rect":      rect,
                    "open":      False,
                    "offset_y":  0,          # how far it has slid up
                    "max_open":  tile_size * 2,
                })
                col += 1

            elif ch == '?':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                paperclips.append({"rect": rect, "collected": False})
                col += 1

            else:
                col += 1

    return {
        "platforms":       platforms,
        "breakable_doors": breakable_doors,
        "paperclips":      paperclips,
        "elevators":       elevators,
        "animated_doors":  animated_doors,
    }

def map_world_width(tile_map, tile_size=TILE_SIZE):
    return max(len(row) for row in tile_map) * tile_size

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
        pygame.draw.circle(screen, (160, 220, 255), (WIDTH // 2, 180), 90)
        pygame.draw.circle(screen, (200, 245, 255), (WIDTH // 2, 180), 55)
        pygame.draw.rect(screen, (10, 45, 75), (0, 430, WIDTH, 270))
        draw_waves(screen, t)

        title_text = title_font.render("Fate: Navy Sea", True, constants.WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)

        sub_text = sub_font.render("Set sail into the storm", True, (220, 245, 255))
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 65))
        screen.blit(sub_text, sub_rect)

        pygame.draw.rect(screen, HOVER_COLOR if hovered else BUTTON_COLOR, button_rect, border_radius=18)
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

# SHOP SCREEN
SHOP_ITEMS = [
    {"name": "Health Flask",      "desc": "+1 flask (heals 40 HP when used)",   "cost": 15,  "key": "flask"},
    {"name": "Sword Upgrade",     "desc": "+15 sword damage",                   "cost": 30,  "key": "sword_dmg"},
    {"name": "Water Gun Ammo +3", "desc": "+3 balloon capacity",                "cost": 20,  "key": "balloon_ammo"},
    {"name": "Max HP +25",        "desc": "Increase maximum health",            "cost": 40,  "key": "max_hp"},
    {"name": "Sea Boots",         "desc": "+1 speed permanently",               "cost": 50,  "key": "speed"},
    {"name": "Revive Token",      "desc": "Auto-revive once with 30 HP",        "cost": 80,  "key": "revive"},
    {"name": "spears",            "desc": "spears",                             "cost": 80,  "key": "spears"},
]

def run_shop():
    draw_vertical_gradient(screen, (5, 20, 35), (15, 60, 90))
    selected = 0

def introLORE():
    screen.fill(constants.BLACK)

def intro():
    introLORE()
    print("le bron")
    levelONE(maps.L1)

def levelONE(tile_map):
    running         = True
    map_data        = build_platforms_from_map(tile_map)
    platforms       = map_data["platforms"]
    breakable_doors = map_data["breakable_doors"]
    paperclips      = map_data["paperclips"]
    elevators       = map_data["elevators"]
    animated_doors  = map_data["animated_doors"]
    world_w         = map_world_width(tile_map)

    # Spawn: find the leftmost low platform and sit the player on top of it
    spawn_x, spawn_y = 100, 300
    grounded = [p for p in platforms if p.y > HEIGHT // 4 and p.y < HEIGHT - 50]
    if grounded:
        best     = min(grounded, key=lambda p: p.x)
        spawn_x  = best.x + 250
        spawn_y  = best.top + 400        # player height (60) + 2 px gap

    player_rect     = pygame.Rect(spawn_x, spawn_y, 40, 60)
    player_vel_y    = 0
    is_grounded     = False
    can_double_jump = True
    camera_x        = 0

    ui_font = pygame.font.Font(None, 30)

    # ── Sea gel palette ───────────────────────────────────────────────────
    GROUND_TOP  = (40, 180, 160)
    GROUND_SIDE = (20, 120, 110)
    GROUND_DIRT = (10,  70,  80)

    COLOR_DOOR_INTACT  = (30, 100, 160)
    COLOR_DOOR_DAMAGED = (60, 150, 200)
    COLOR_PAPERCLIP    = (160, 240, 220)
    COLOR_ELEVATOR     = (80, 210, 190)
    COLOR_ANIM_DOOR    = (50,  80, 160)
 
    # Colors for extra tile types
    COLOR_DOOR_INTACT  = (160,  80,  30)   # brown breakable door
    COLOR_DOOR_DAMAGED = (200, 120,  50)   # lighter when damaged
    COLOR_PAPERCLIP    = (200, 200, 220)   # silver paperclip
 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    if is_grounded:
                        player_vel_y    = JUMP_POWER
                        is_grounded     = False
                        can_double_jump = True
                    elif can_double_jump and DOUBLE_JUMP_POWER != 0:
                        player_vel_y    = DOUBLE_JUMP_POWER
                        can_double_jump = False
 
                if event.key == pygame.K_e:
                    # breakable doors
                    for door in breakable_doors:
                        if door["broken"]:
                            continue
                        if player_rect.inflate(20, 0).colliderect(door["rect"]):
                            door["hp"] -= 1
                            if door["hp"] <= 0:
                                door["broken"] = True
                    # animated ^ doors
                    for door in animated_doors:
                        if not door["open"]:
                            if player_rect.inflate(30, 30).colliderect(door["rect"]):
                                door["open"] = True
 
        keys   = pygame.key.get_pressed()
        # ── horizontal movement ───────────────────────────────────────────
        move_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  move_x -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x += PLAYER_SPEED

        player_rect.x = max(0, min(player_rect.x + move_x, world_w - player_rect.width))

        # Solid rects = platforms + intact breakable doors +
        #               elevator rects + closed animated doors
        solid_rects = (
            platforms
            + [d["rect"] for d in breakable_doors if not d["broken"]]
            + [e["rect"] for e in elevators]
            + [d["rect"] for d in animated_doors
               if not d["open"] or d["offset_y"] < d["max_open"]]
        )

        # ── resolve horizontal collisions ─────────────────────────────────
        for plat in solid_rects:
            if player_rect.colliderect(plat):
                if move_x > 0:
                    player_rect.right = plat.left
                elif move_x < 0:
                    player_rect.left = plat.right

        # ── vertical movement ─────────────────────────────────────────────
        player_vel_y = min(player_vel_y + GRAVITY, MAX_FALL_SPEED)
        player_rect.y += int(player_vel_y)

        # ── collect paperclips ────────────────────────────────────────────
        for clip in paperclips:
            if not clip["collected"] and player_rect.colliderect(clip["rect"]):
                clip["collected"] = True

        # ── resolve vertical collisions ───────────────────────────────────
        is_grounded = False
        for plat in solid_rects:
            if player_rect.colliderect(plat):
                if player_vel_y > 0 and player_rect.bottom - int(player_vel_y) <= plat.top + 5:
                    player_rect.bottom = plat.top
                    player_vel_y       = 0
                    is_grounded        = True
                    can_double_jump    = True
                elif player_vel_y < 0 and player_rect.top - int(player_vel_y) >= plat.bottom - 5:
                    player_rect.top = plat.bottom
                    player_vel_y    = 0

        # ── elevator logic ────────────────────────────────────────────────
        for elev in elevators:
            elev["rect"].y += elev["speed"] * elev["dir"]
            if elev["rect"].y > elev["origin_y"] + elev["range"]:
                elev["dir"] = -1
            elif elev["rect"].y < elev["origin_y"] - elev["range"]:
                elev["dir"] = 1
            # carry player if standing on it
            if (is_grounded and
                    player_rect.bottom == elev["rect"].top and
                    player_rect.right  > elev["rect"].left and
                    player_rect.left   < elev["rect"].right):
                player_rect.y += int(elev["speed"] * elev["dir"])

        # ── animated door logic ───────────────────────────────────────────
        for door in animated_doors:
            if door["open"] and door["offset_y"] < door["max_open"]:
                door["offset_y"] = min(door["offset_y"] + 4, door["max_open"])
                door["rect"].y   = (door["rect"].y - 4)   # slide upward
                door["rect"].height = max(4, door["max_open"] - door["offset_y"])

        if player_rect.y > HEIGHT + 200:
            player_rect.x = spawn_x
            player_rect.y = spawn_y
            player_vel_y  = 0
        
        camera_x = max(0, min(player_rect.x - WIDTH // 2, world_w - WIDTH))
 
        # ── draw ──────────────────────────────────────────────────────────
        draw_vertical_gradient(screen, (10, 30, 60), (30, 90, 140))
 
        # walls / platforms
        for plat in platforms:
            vx = plat.x - camera_x
            if vx + plat.width < 0 or vx > WIDTH:
                continue
            pygame.draw.rect(screen, GROUND_TOP,  (vx, plat.y,     plat.width, 8))
            pygame.draw.rect(screen, GROUND_DIRT, (vx, plat.y + 8, plat.width, plat.height - 8))
            pygame.draw.rect(screen, GROUND_SIDE, (vx, plat.y,     plat.width, plat.height), 2)
 
        # breakable doors  (!)
        for door in breakable_doors:
            if door["broken"]:
                continue
            vx = door["rect"].x - camera_x
            if vx + door["rect"].width < 0 or vx > WIDTH:
                continue
            color = COLOR_DOOR_DAMAGED if door["hp"] < 3 else COLOR_DOOR_INTACT
            pygame.draw.rect(screen, color,      (vx, door["rect"].y, door["rect"].width, door["rect"].height))
            pygame.draw.rect(screen, (220,160,80),(vx, door["rect"].y, door["rect"].width, door["rect"].height), 3)
            # show remaining HP as small pips
            for i in range(door["hp"]):
                pygame.draw.circle(screen, (255,220,80),
                                   (int(vx + 10 + i * 14), door["rect"].y + 8), 5)
 
        # paperclips  (?)
        for clip in paperclips:
            if clip["collected"]:
                continue
            vx = clip["rect"].x - camera_x
            if vx + clip["rect"].width < 0 or vx > WIDTH:
                continue
            cx = int(vx + clip["rect"].width  // 2)
            cy = int(clip["rect"].y + clip["rect"].height // 2)
            pygame.draw.circle(screen, COLOR_PAPERCLIP, (cx, cy), 8)
            pygame.draw.circle(screen, (240,240,255),   (cx, cy), 8, 2)

        # elevators (_)
        for elev in elevators:
            vx = elev["rect"].x - camera_x
            pygame.draw.rect(screen, COLOR_ELEVATOR,
                             (vx, elev["rect"].y, elev["rect"].width, elev["rect"].height),
                             border_radius=4)
            pygame.draw.rect(screen, (200, 255, 240),
                             (vx, elev["rect"].y, elev["rect"].width, elev["rect"].height),
                             2, border_radius=4)

        # animated doors (^)
        for door in animated_doors:
            if door["rect"].height <= 0:
                continue
            vx = door["rect"].x - camera_x
            pygame.draw.rect(screen, COLOR_ANIM_DOOR,
                             (vx, door["rect"].y, door["rect"].width, door["rect"].height))
            pygame.draw.rect(screen, (120, 180, 255),
                             (vx, door["rect"].y, door["rect"].width, door["rect"].height), 3)
 
        # player
        pr = pygame.Rect(player_rect.x - camera_x, player_rect.y, player_rect.width, player_rect.height)
        pygame.draw.rect(screen, (255, 140, 0), pr, border_radius=4)
        pygame.draw.rect(screen, (255, 200, 0), pr, 3, border_radius=4)
 
        # HUD
        clips_total     = len(paperclips)
        clips_collected = sum(1 for c in paperclips if c["collected"])
        hint    = ui_font.render("A/D – Move   |   SPACE – Jump   |   E – Break door", True, (255, 255, 255))
        pos_txt = ui_font.render(f"x:{player_rect.x}  y:{player_rect.y}", True, (200, 220, 255))
        clip_txt= ui_font.render(f"Paperclips: {clips_collected}/{clips_total}", True, (200, 200, 220))
        screen.blit(hint,    (20, 20))
        screen.blit(pos_txt, (20, 50))
        screen.blit(clip_txt,(20, 80))
 
        pygame.display.flip()
        clock.tick(60)
 
    pygame.quit()
 
 
show_title_screen()
