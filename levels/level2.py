import maps
import pygame
import math
import constants
import random 

from constants import *
from helper import mapGeneration
from helper import graphics
from helper import death_screen

clock = None
def intro(screen, set_clock):
    global clock
    clock = set_clock
    levelTWO(screen, maps.L2)


def levelTWO(screen: pygame.Surface, tile_map: list[str]) -> None:
    print("level 2...")
    global clock

    running = True
    map_data        = mapGeneration.build_platforms_from_map(tile_map)
    platforms       = map_data["platforms"]
    breakable_doors = map_data["breakable_doors"]
    paperclips      = map_data["paperclips"]
    elevators       = map_data["elevators"]
    animated_doors  = map_data["animated_doors"]
    world_w         = mapGeneration.map_world_width(tile_map)

    spawn_x, spawn_y = 100, 300
    grounded = [p for p in platforms if HEIGHT // 4 < p.y < HEIGHT - 50]
    if grounded:
        best    = min(grounded, key=lambda p: p.x)
        spawn_x = best.x - 1670
        spawn_y = best.top + 50

        if constants.dev_mode == True:
            spawn_x = spawn_x + 3000
    
    player_x               = float(spawn_x)
    player_y               = float(spawn_y)
    player_rect            = pygame.Rect(spawn_x, spawn_y, 40, 60)
    player_vel_y           = 0.0
    is_grounded            = False
    coyote_frames          = 0
    can_double_jump        = True
    camera_x               = 0
    player_inventory_clips = 0
    show_warning_frames    = 0

    SNAP_TOLERANCE = 8
    ui_font = pygame.font.Font(None, 30)

    COLOR_ELEVATOR = (80, 210, 190)
    COLOR_ANIM_DOOR = (50, 80, 160)

    light_glow_t = 0   
    bubble_pool = [
        {
            "x": random.random() * world_w, 
            "y": random.random() * HEIGHT,
            "r": 1 + random.random() * 4, 
            "speed": 0.4 + random.random() * 1.2,
            "drift": (random.random() - 0.5) * 0.3
        } for _ in range(80)
    ]
    particle_pool = [
        {
            "x": random.random() * world_w,
            "y": 30 + random.random() * 55,   
            "len": 12 + random.random() * 40, 
            "speed": 5 + random.random() * 9,
            "alpha": 0.15 + random.random() * 0.35
        } for _ in range(120)
    ]
    kelp_pool = [
        {
            "bx": x, 
            "phase": random.random() * 6.28,
            "h": 28 + random.random() * 38
        } for x in range(0, world_w, 55)
    ]

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    return

                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    if is_grounded or coyote_frames > 0:
                        player_vel_y    = physics.JUMP_POWER
                        is_grounded     = False
                        coyote_frames   = 0
                        can_double_jump = True
                        riding_elev     = None 
                    elif can_double_jump and physics.DOUBLE_JUMP_POWER != 0:
                        player_vel_y    = physics.DOUBLE_JUMP_POWER
                        can_double_jump = False
                        riding_elev     = None

                if event.key == pygame.K_f:
                    if riding_elev is None:
                        for door in breakable_doors:
                            if door["broken"]:
                                continue
                            if player_rect.inflate(20, 0).colliderect(door["rect"]):
                                if player_inventory_clips >= 1:
                                    door["hp"] -= 1
                                    if door["hp"] <= 0:
                                        door["broken"] = True
                                else:
                                    show_warning_frames = 90

                        for door in animated_doors:
                            if not door["open"]:
                                if player_rect.inflate(30, 30).colliderect(door["rect"]):
                                    door["open"] = True

        keys = pygame.key.get_pressed()

        #  ELEVATOR REGISTRATION 
        riding_elev = None
        for elev in elevators:
            if (elev["rect"].top - SNAP_TOLERANCE <= player_rect.bottom <= elev["rect"].top + SNAP_TOLERANCE and
                player_rect.right > elev["rect"].left and
                player_rect.left < elev["rect"].right and
                player_vel_y >= 0):
                riding_elev = elev
                break 

        #  Q / E PLAYER-CONTROLLED ELEVATOR MOVEMENT 
        for elev in elevators:
            prev_y = elev["float_y"]
            
            if elev is riding_elev:
                elev_speed = abs(elev["speed"])
                
                if keys[pygame.K_q]:
                    elev["float_y"] -= elev_speed
                    if elev["float_y"] < elev["origin_y"] - elev["range"]:
                        elev["float_y"] = elev["origin_y"] - elev["range"]
                elif keys[pygame.K_e]:
                    elev["float_y"] += elev_speed
                    if elev["float_y"] > elev["origin_y"] + elev["range"]:
                        elev["float_y"] = elev["origin_y"] + elev["range"]
                        
            elev["rect"].y = int(elev["float_y"])

            if elev is riding_elev:
                delta_y = elev["float_y"] - prev_y
                player_y += delta_y
                player_rect.y = int(player_y)

        # ANIMATED DOORS 
        for door in animated_doors:
            if door["open"] and door["offset_y"] < door["max_open"]:
                door["offset_y"] = min(door["offset_y"] + 4, door["max_open"])
                door["rect"].y -= 4
                door["rect"].height = max(4, door["max_open"] - door["offset_y"])

        static_solids = platforms + [d["rect"] for d in breakable_doors if not d["broken"]] + \
                        [d["rect"] for d in animated_doors if not d["open"] or d["offset_y"] < d["max_open"]]

        # HORIZONTAL PLAYER AXIS MOVEMENTS & COLLISIONS 
        move_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  move_x -= physics.PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x += physics.PLAYER_SPEED

        player_x = max(0.0, min(player_x + move_x, world_w - player_rect.width))
        player_rect.x = int(player_x)

        horizontal_solids = static_solids + [e["rect"] for e in elevators if e is not riding_elev]

        for plat in horizontal_solids:
            if player_rect.colliderect(plat):
                if move_x > 0:
                    player_rect.right = plat.left
                    player_x = float(player_rect.x)
                elif move_x < 0:
                    player_rect.left = plat.right
                    player_x = float(player_rect.x)

        #  VERTICAL PLAYER AXIS MOVEMENTS & COLLISIONS 
        player_vel_y = min(player_vel_y + physics.GRAVITY, physics.MAX_FALL_SPEED)
        player_y += player_vel_y
        player_rect.y = int(player_y)

        # ── CRUSH / SQUISH DETECTION UNDER ELEVATOR 
        for elev in elevators:
            if player_rect.colliderect(elev["rect"]):
                if elev is riding_elev and keys[pygame.K_e]:
                    player_rect.bottom = elev["rect"].bottom
                    for static_floor in static_solids:
                        if player_rect.colliderect(static_floor):
                            death_screen.show_death_screen_level_one(screen, clock, tile_map)
                            return

        all_solids = static_solids + [e["rect"] for e in elevators]

        is_grounded = False
        for plat in all_solids:
            if player_rect.colliderect(plat):
                if player_vel_y >= 0: 
                    if player_rect.bottom - player_vel_y <= plat.top + SNAP_TOLERANCE:
                        player_rect.bottom = plat.top
                        player_y           = float(player_rect.y)
                        player_vel_y       = 0.0
                        is_grounded        = True
                        can_double_jump    = True
                elif player_vel_y < 0: 
                    if player_rect.top - player_vel_y >= plat.bottom - SNAP_TOLERANCE:
                        player_rect.top = plat.bottom
                        player_y        = float(player_rect.y)
                        player_vel_y    = 0.0

        if riding_elev is not None:
            if player_rect.right > riding_elev["rect"].left and player_rect.left < riding_elev["rect"].right:
                is_grounded = True
                can_double_jump = True
            else:
                riding_elev = None

        #  ITEMS & BOUNDARIES 
        for clip in paperclips:
            if not clip["collected"] and player_rect.colliderect(clip["rect"]):
                clip["collected"] = True
                player_inventory_clips += 1

        if is_grounded:
            coyote_frames = 6
        else:
            coyote_frames = max(0, coyote_frames - 1)

        if player_rect.y > HEIGHT + 190:
            player_x      = float(spawn_x)
            player_y      = float(spawn_y)
            player_rect.x = spawn_x
            player_rect.y = spawn_y
            player_vel_y = 0.0

        camera_x = max(0, min(player_rect.x - WIDTH // 2, world_w - WIDTH))

        # ART RENDERING LAYER 
        light_glow_t += 1

        bg_surf = pygame.Surface((WIDTH, HEIGHT))
        for scanline in range(HEIGHT):
            frac = scanline / HEIGHT
            r = int(2  + frac * 4)
            g = int(13 + frac * 18)
            b = int(26 + frac * 22)
            pygame.draw.line(bg_surf, (r, g, b), (0, scanline), (WIDTH, scanline))
        screen.blit(bg_surf, (0, 0))

        grid_col = (10, 55, 75)
        for gy in range(30, HEIGHT - 50, 30):
            pygame.draw.line(screen, grid_col, (0, gy), (WIDTH, gy), 1)
        for gx in range(0, WIDTH, 80):
            pygame.draw.line(screen, grid_col, (gx, 0), (gx, HEIGHT), 1)

        pulse = abs(math.sin(light_glow_t * 0.04)) * 0.4 + 0.5   
        for lx in range(60, WIDTH, 140):
            glow_r = int(36 * pulse)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (50, 200, 160, int(60 * pulse)), (glow_r, glow_r), glow_r)
            screen.blit(glow_surf, (lx - glow_r, 0))
            dot_bright = int(160 + 95 * pulse)
            pygame.draw.circle(screen, (80, dot_bright, 180), (lx, 5), 3)

        # Fast speed particles
        for p in particle_pool:
            p["x"] -= p["speed"]
            if p["x"] + p["len"] < camera_x:
                p["x"] = camera_x + WIDTH + p["len"]
                p["y"] = 30 + random.random() * 55
            vx_p = int(p["x"] - camera_x)
            if -p["len"] < vx_p < WIDTH:
                alpha = int(p["alpha"] * 255)
                line_surf = pygame.Surface((int(p["len"]), 2), pygame.SRCALPHA)
                line_surf.fill((120, 220, 190, alpha))
                screen.blit(line_surf, (vx_p, int(p["y"])))

        # Kelp on ground 
        ground_y = HEIGHT - 80   
        for k in kelp_pool:
            k["phase"] += 0.022
            kx_screen = k["bx"] - camera_x
            if -20 < kx_screen < WIDTH + 20:
                segs = 6
                for s in range(segs):
                    frac = s / segs
                    f2   = (s + 1) / segs
                    sway1 = math.sin(k["phase"] + frac * 1.8) * 8 * frac
                    sway2 = math.sin(k["phase"] + f2   * 1.8) * 8 * f2
                    x1 = int(kx_screen + sway1)
                    y1 = int(ground_y - frac * k["h"])
                    x2 = int(kx_screen + sway2)
                    y2 = int(ground_y - f2 * k["h"])
                    g_green = int(80 + 100 * f2)
                    pygame.draw.line(screen, (20, g_green, 55), (x1, y1), (x2, y2), 2)

        # Platforms 
        for plat in platforms:
            vx = plat.x - camera_x
            if vx + plat.width < 0 or vx > WIDTH:
                continue
            pygame.draw.rect(screen, (8, 35, 55),  (vx, plat.y, plat.width, plat.height))
            pygame.draw.rect(screen, (12, 55, 80), (vx, plat.y, plat.width, 3))
            pygame.draw.rect(screen, (22, 100, 130),(vx, plat.y, plat.width, plat.height), 1)
            for gx_off in range(0, plat.width, 22):
                dot_alpha = int(90 + 50 * abs(math.sin(light_glow_t * 0.03 + gx_off)))
                dot_surf = pygame.Surface((5, 5), pygame.SRCALPHA)
                pygame.draw.circle(dot_surf, (30, 180, 130, dot_alpha), (2, 2), 2)
                screen.blit(dot_surf, (vx + gx_off + 9, plat.y + 6))

        # Breakable doors 
        for door in breakable_doors:
            if door["broken"]:
                continue
            vx = door["rect"].x - camera_x
            if vx + door["rect"].width < 0 or vx > WIDTH:
                continue
            color = (18, 40, 80) if door["hp"] >= 3 else (50, 18, 18)
            pygame.draw.rect(screen, color,
                             (vx, door["rect"].y, door["rect"].width, door["rect"].height))
            bolt_col = (30, 140, 200) if door["hp"] >= 3 else (200, 80, 50)
            pygame.draw.rect(screen, bolt_col,
                             (vx, door["rect"].y, door["rect"].width, door["rect"].height), 2)
            for i in range(door["hp"]):
                p_alpha = int(140 + 80 * abs(math.sin(light_glow_t * 0.06 + i)))
                dot_s = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.circle(dot_s, (30, 160, 220, p_alpha), (6, 6), 5)
                screen.blit(dot_s, (int(vx + 6 + i * 14), door["rect"].y + 5))

        # Paperclips 
        for clip in paperclips:
            if clip["collected"]:
                continue
            vx = clip["rect"].x - camera_x
            if vx + clip["rect"].width < 0 or vx > WIDTH:
                continue
            cx = int(vx + clip["rect"].width // 2)
            cy = int(clip["rect"].y + clip["rect"].height // 2)
            pygame.draw.circle(screen, COLOR_PAPERCLIP, (cx, cy), 8)
            pygame.draw.circle(screen, (220, 240, 255), (cx, cy), 8, 2)

        # Elevators 
        for elev in elevators:
            vx = elev["rect"].x - camera_x
            pygame.draw.rect(screen, (8, 55, 65),
                             (vx, elev["rect"].y, elev["rect"].width, elev["rect"].height),
                             border_radius=4)
            pygame.draw.rect(screen, (20, 200, 160),
                             (vx, elev["rect"].y, elev["rect"].width, elev["rect"].height),
                             2, border_radius=4)

        #  Animated doors 
        for door in animated_doors:
            if door["rect"].height <= 0:
                continue
            vx = door["rect"].x - camera_x
            pygame.draw.rect(screen, (10, 30, 80),
                             (vx, door["rect"].y, door["rect"].width, door["rect"].height))
            pygame.draw.rect(screen, (60, 140, 240),
                             (vx, door["rect"].y, door["rect"].width, door["rect"].height), 2)

        #  Floating bubbles 
        for b in bubble_pool:
            b["y"] -= b["speed"]
            b["x"] += b["drift"]
            if b["y"] + b["r"] < 0:
                b["y"] = HEIGHT + b["r"]
                b["x"] = camera_x + random.random() * world_w # Use random.random()
            vx_b = b["x"] - camera_x
            if -10 < vx_b < WIDTH + 10:
                bs = pygame.Surface((int(b["r"]*2+2), int(b["r"]*2+2)), pygame.SRCALPHA)
                pygame.draw.circle(bs, (120, 200, 180, 55), (int(b["r"]), int(b["r"])), int(b["r"]))
                pygame.draw.circle(bs, (160, 230, 210, 110), (int(b["r"]), int(b["r"])), int(b["r"]), 1)
                screen.blit(bs, (int(vx_b - b["r"]), int(b["y"] - b["r"])))

        #  Player 
        pr = pygame.Rect(player_rect.x - camera_x, player_rect.y,
                         player_rect.width, player_rect.height)
        shadow_s = pygame.Surface((pr.width + 10, 6), pygame.SRCALPHA)
        shadow_s.fill((20, 120, 100, 40))
        screen.blit(shadow_s, (pr.x - 5, pr.bottom + 2))
        pygame.draw.rect(screen, (220, 100, 0), pr, border_radius=4)
        pygame.draw.rect(screen, (255, 195, 0), pr, 2, border_radius=4)

        #  HUD 
        hud_surf = pygame.Surface((WIDTH, 20), pygame.SRCALPHA)
        hud_surf.fill((10, 80, 70, 50))
        screen.blit(hud_surf, (0, 0))

        clips_total     = len(paperclips)
        clips_collected = sum(1 for c in paperclips if c["collected"])
        hint    = ui_font.render(
            "A/D – Move  |  SPACE/W – Jump  |  Q/E – Elevator  |  F – Action  |  ESC – Quit",
            True, (80, 200, 170))
        pos_txt  = ui_font.render(f"x:{player_rect.x}  y:{player_rect.y}", True, (80, 180, 200))
        clip_txt = ui_font.render(f"Paperclips: {clips_collected}/{clips_total}", True, (140, 200, 200))
        inv_col  = (80, 220, 130) if player_inventory_clips >= 1 else (200, 90, 90)
        inv_lbl  = "Lock Pick: READY" if player_inventory_clips >= 1 else "Lock Pick: NEED PAPERCLIP"
        inv_txt  = ui_font.render(inv_lbl, True, inv_col)
        depth_txt = ui_font.render(
            f"NORTH WATERLINE — DEPTH {320 + int(10 * abs(math.sin(light_glow_t * 0.01)))}m",
            True, (50, 160, 190))

        screen.blit(hint,      (20, 20))
        screen.blit(pos_txt,   (20, 50))
        screen.blit(clip_txt,  (20, 80))
        screen.blit(inv_txt,   (20, 110))
        screen.blit(depth_txt, (WIDTH - depth_txt.get_width() - 20, 20))

        if show_warning_frames > 0:
            warn_txt = ui_font.render(
                "Find a paperclip first to pick this wall lock!", True, (220, 80, 80))
            screen.blit(warn_txt, (WIDTH // 2 - warn_txt.get_width() // 2, HEIGHT // 2 - 100))
            show_warning_frames -= 1

        pygame.display.flip()

    pygame.quit()