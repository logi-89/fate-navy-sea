import maps
import pygame
import constants
import math

#constants.dev_mode = True

from constants import *
from helper import mapGeneration
from helper import graphics
from helper import death_screen

import levels
from levels import level2

clock = None

def introLORE(screen: pygame.Surface) -> None:
    screen.fill(BLACK)

def intro(screen, set_clock):
    global clock

    clock = set_clock
    introLORE(screen)
    print("[DEBUG] Show intro")
    levelONE(screen, maps.L1)


def levelONE(screen: pygame.Surface, tile_map: list[str]) -> None:
    global clock

    running = True
    map_data        = mapGeneration.build_platforms_from_map(tile_map)
    platforms       = map_data["platforms"]
    breakable_doors = map_data["breakable_doors"]
    paperclips      = map_data["paperclips"]
    elevators       = map_data["elevators"]
    animated_doors  = map_data["animated_doors"]
    world_w         = mapGeneration.map_world_width(tile_map)
    water           = map_data["water"]
    enemies         = map_data.get("enemies", [])
    
    # Safely track map height
    world_h         = len(tile_map) * 40  
    lore_drop = map_data["lore"]
    spawn_x, spawn_y = 100, -200
    grounded = [p for p in platforms if HEIGHT // 4 < p.y < HEIGHT - 50]
    if grounded:
        best    = min(grounded, key=lambda p: p.x)
        spawn_x = best.x + 200
        spawn_y = best.top + 150

        if constants.dev_mode == True:
            spawn_x = spawn_x + 7600
            spawn_y = spawn_y - 467

    player_x               = float(spawn_x)
    player_y               = float(spawn_y)
    player_rect            = pygame.Rect(spawn_x, spawn_y, 40, 60)
    player_vel_y           = 0.0
    is_grounded            = False
    coyote_frames          = 0
    can_double_jump        = True
    camera_x               = 0
    camera_y               = 0
    show_warning_frames    = 0

    # LORE POPUP STATE 
    lore_display_text  = None   
    lore_display_timer = 0      

    SNAP_TOLERANCE = 8
    ui_font   = pygame.font.Font(None, 30)
    lore_font = pygame.font.Font(None, 26)   

    COLOR_ELEVATOR  = (25, 75, 75)
    COLOR_ANIM_DOOR = (45, 55, 65)
    # Cap elevator downward travel at the nearest platform below
    for elev in elevators:
        floor_y = None
        for plat in platforms:
            if (plat.top > elev["rect"].bottom and
                plat.left < elev["rect"].right and
                plat.right > elev["rect"].left):
                if floor_y is None or plat.top < floor_y:
                    floor_y = plat.top
        if floor_y is not None:
            elev["max_y"] = floor_y - elev["rect"].height
        else:
            elev["max_y"] = elev["origin_y"] + elev["range"]

    # Nudge spawn upward if it overlaps a platform
    for plat in platforms:
        if player_rect.colliderect(plat):
            player_rect.bottom = plat.top
            spawn_x = player_rect.x
            spawn_y = player_rect.y
            break

    # Loading screen
    loading_font = pygame.font.Font(None, 48)
    for _ in range(15):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return
        screen.fill((4, 8, 15))
        text = loading_font.render("Loading...", True, (120, 220, 190))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        clock.tick(60)
    pygame.event.clear()

    camera_x = float(spawn_x - WIDTH // 2)
    camera_y = float(spawn_y - HEIGHT // 2)
    input_allowed = False

    while running:
        dt = clock.tick(60)

        if not input_allowed:
            key_state = pygame.key.get_pressed()
            all_released = True
            for scancode in range(len(key_state)):
                if key_state[scancode]:
                    all_released = False
                    break
            if all_released:
                input_allowed = True

        riding_elev = None

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

                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP) and input_allowed:
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

                if event.key == pygame.K_f and input_allowed:
                    for door in breakable_doors:
                        if door["broken"]:
                            continue
                        if player_rect.inflate(20, 0).colliderect(door["rect"]):
                            if constants.player_inventory_clips >= 1:
                                door["hp"] -= 1
                                if door["hp"] <= 0:
                                    door["broken"] = True
                            else:
                                show_warning_frames = 90

                    for door in animated_doors:
                        if not door["open"]:
                            if player_rect.inflate(30, 30).colliderect(door["rect"]):
                                door["open"] = True

                    import random
                    for lorey in lore_drop:
                        if not lorey["collected"]:
                            continue
                        if player_rect.inflate(40, 20).colliderect(lorey["rect"]):
                            lore_display_text  = random.choice(maps.loreDrop)
                            lore_display_timer = 300   

        keys = pygame.key.get_pressed()

        # ── ELEVATOR REGISTRATION ─────────────────────────────────────
        riding_elev = None
        for elev in elevators:
            if (elev["rect"].top - SNAP_TOLERANCE <= player_rect.bottom <= elev["rect"].top + SNAP_TOLERANCE and
                player_rect.right > elev["rect"].left and
                player_rect.left < elev["rect"].right and
                player_vel_y >= 0):
                riding_elev = elev
                break 

        # ── Q / E PLAYER-CONTROLLED ELEVATOR MOVEMENT 
        for elev in elevators:
            prev_y = elev["float_y"]
            
            if elev is riding_elev:
                elev_speed = abs(elev["speed"])
                if keys[pygame.K_e] and input_allowed:
                    elev["float_y"] -= elev_speed
                    if elev["float_y"] < elev["min_y"]:
                        elev["float_y"] = elev["min_y"]

                elif keys[pygame.K_q] and input_allowed:
                    elev["float_y"] += elev_speed
                    if elev["float_y"] > elev["max_y"]:
                        elev["float_y"] = elev["max_y"]
                        
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
        if keys[pygame.K_a] and input_allowed or keys[pygame.K_LEFT] and input_allowed:  move_x -= physics.PLAYER_SPEED
        if keys[pygame.K_d] and input_allowed or keys[pygame.K_RIGHT] and input_allowed: move_x += physics.PLAYER_SPEED

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

        # VERTICAL PLAYER AXIS MOVEMENTS & COLLISIONS 
        if riding_elev is None:
            player_vel_y = min(player_vel_y + physics.GRAVITY, physics.MAX_FALL_SPEED)
            player_y += player_vel_y
            player_rect.y = int(player_y)

        # CRUSH / SQUISH DETECTION UNDER ELEVATOR 
        for elev in elevators:
            if player_rect.colliderect(elev["rect"]):
                if elev is riding_elev and keys[pygame.K_q]:
                    player_rect.bottom = elev["rect"].bottom
                    for static_floor in static_solids:
                        if player_rect.colliderect(static_floor):
                            death_screen.show_death_screen(screen, clock, lambda: levelONE(screen, tile_map))
                            return

        # LEVEL TRANSITION TRIGGER
        for trigger in map_data.get("level_triggers", []):
            if player_rect.colliderect(trigger["rect"]):
                if trigger["target_level"] == 2:
                    print("TOOOOOO LEVEL 2 !!!!!!!!!!!!")
                    levels.level2.intro(screen, clock)
                    return

        all_solids = static_solids + [e["rect"] for e in elevators]

        # Resolve Floors and Ceilings
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

        # ITEMS & BOUNDARIES 
        for clip in paperclips:
            if not clip["collected"] and player_rect.colliderect(clip["rect"]):
                clip["collected"] = True
                constants.player_inventory_clips += 1

        for lorey in lore_drop:
            if not lorey["collected"] and player_rect.colliderect(lorey["rect"]):
                lorey["collected"] = True   

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

        # ENEMY AI
        for enemy in enemies[:]:
            dx = player_rect.centerx - enemy["rect"].centerx
            dy = player_rect.centery - enemy["rect"].centery
            dist = math.sqrt(dx*dx + dy*dy)

            can_see = False
            if dist < enemy["detect_range"]:
                can_see = True
                for obs in platforms:
                    if obs.clipline(enemy["rect"].center, player_rect.center):
                        can_see = False
                        break

            enemy["state"] = "chase" if can_see else "patrol"

            if enemy["state"] == "chase":
                enemy["dir"] = 1 if dx > 0 else -1
                move_x = enemy["chase_speed"] * enemy["dir"]
            else:
                move_x = enemy["speed"] * enemy["dir"]

            enemy["rect"].x += int(move_x)

            for plat in static_solids:
                if enemy["rect"].colliderect(plat):
                    if move_x > 0:
                        enemy["rect"].right = plat.left
                        if enemy["state"] == "patrol":
                            enemy["dir"] = -1
                    elif move_x < 0:
                        enemy["rect"].left = plat.right
                        if enemy["state"] == "patrol":
                            enemy["dir"] = 1

            if enemy["state"] == "patrol":
                if enemy["rect"].left <= enemy["patrol_left"]:
                    enemy["rect"].left = int(enemy["patrol_left"])
                    enemy["dir"] = 1
                elif enemy["rect"].right >= enemy["patrol_right"]:
                    enemy["rect"].right = int(enemy["patrol_right"])
                    enemy["dir"] = -1

            if player_rect.colliderect(enemy["rect"]):
                if player_vel_y > 0 and player_rect.bottom - player_vel_y <= enemy["rect"].centery:
                    enemies.remove(enemy)
                    player_vel_y = -12
                    can_double_jump = True
                else:
                    death_screen.show_death_screen_ENEMIES(
                        screen, clock,
                        lambda: levelONE(screen, tile_map),
                        "You were killed by an enemy!"
                    )
                    return

        # SMOOTH  CAMERA LERP TRACKING
        max_cam_x = max(0, world_w - WIDTH)
        max_cam_y = max(0, world_h - HEIGHT)

        target_cam_x = player_rect.centerx - WIDTH // 2
        target_cam_y = player_rect.centery - HEIGHT // 2

        target_cam_x = max(0, min(target_cam_x, max_cam_x))
        target_cam_y = max(0, min(target_cam_y, max_cam_y))

        LARP = 0.12
        camera_x += (target_cam_x - camera_x) * LARP
        camera_y += (target_cam_y - camera_y) * LARP

        # Snap to avoid sub-pixel drift when very close
        if abs(camera_x - target_cam_x) < 0.5:
            camera_x = target_cam_x
        if abs(camera_y - target_cam_y) < 0.5:
            camera_y = target_cam_y

        # Single integer offset used for ALL rendering this frame
        cam_ix = int(camera_x)
        cam_iy = int(camera_y)

        # ART RENDERING LAYER
        graphics.draw_vertical_gradient(screen, (4, 8, 15), (14, 42, 54))

        for plat in platforms:
            vx = plat.x - camera_x
            vy = plat.y - camera_y
            if vx + plat.width < 0 or vx > WIDTH or vy + plat.height < 0 or vy > HEIGHT:
                continue
            pygame.draw.rect(screen, GROUND_TOP, (vx, vy, plat.width, 8))
            pygame.draw.rect(screen, GROUND_DIRT, (vx, vy + 8, plat.width, plat.height - 8))
            pygame.draw.rect(screen, GROUND_SIDE, (vx, vy, plat.width, plat.height), 2)

        for door in breakable_doors:
            if door["broken"]:
                continue
            vx = door["rect"].x - camera_x
            vy = door["rect"].y - camera_y
            if vx + door["rect"].width < 0 or vx > WIDTH or vy + door["rect"].height < 0 or vy > HEIGHT:
                continue
            color = COLOR_DOOR_DAMAGED if door["hp"] < 3 else COLOR_DOOR_INTACT
            pygame.draw.rect(screen, color, (vx, vy, door["rect"].width, door["rect"].height))
            pygame.draw.rect(screen, (220, 160, 80), (vx, vy, door["rect"].width, door["rect"].height), 3)
            for i in range(door["hp"]):
                pygame.draw.circle(screen, (255, 220, 80), (int(vx + 10 + i * 14), vy + 8), 5)

        for clip in paperclips:
            if clip["collected"]:
                continue
            vx = clip["rect"].x - camera_x
            vy = clip["rect"].y - camera_y
            if vx + clip["rect"].width < 0 or vx > WIDTH or vy + clip["rect"].height < 0 or vy > HEIGHT:
                continue
            cx = int(vx + clip["rect"].width // 2)
            cy = int(vy + clip["rect"].height // 2)
            pygame.draw.circle(screen, COLOR_PAPERCLIP, (cx, cy), 8)
            pygame.draw.circle(screen, (240, 240, 255), (cx, cy), 8, 2)

        for lorey in lore_drop:
            vx = lorey["rect"].x - camera_x
            vy = lorey["rect"].y - camera_y
            if vx + lorey["rect"].width < 0 or vx > WIDTH or vy + lorey["rect"].height < 0 or vy > HEIGHT:
                continue
            cx = int(vx + lorey["rect"].width // 2)
            cy = int(vy + lorey["rect"].height // 2)

            if not lorey["collected"]:
                pulse = abs(pygame.time.get_ticks() % 1200 - 600) / 600.0   
                radius = int(10 + pulse * 4)
                alpha_surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                glow_col = (40, int(180 + pulse * 60), int(200 + pulse * 55), 90)
                pygame.draw.circle(alpha_surf, glow_col, (radius + 2, radius + 2), radius + 2)
                screen.blit(alpha_surf, (cx - radius - 2, cy - radius - 2))
                pygame.draw.circle(screen, (80, 220, 210), (cx, cy), radius)
                pygame.draw.circle(screen, (180, 255, 245), (cx, cy), radius, 2)
                q_surf = lore_font.render("?", True, (10, 30, 40))
                screen.blit(q_surf, (cx - q_surf.get_width() // 2, cy - q_surf.get_height() // 2))
                f_surf = pygame.font.Font(None, 20).render("[F]", True, (120, 220, 190))
                screen.blit(f_surf, (cx - f_surf.get_width() // 2, cy + radius + 4))
            else:
                pygame.draw.circle(screen, (30, 80, 90), (cx, cy), 6)
                pygame.draw.circle(screen, (60, 140, 160), (cx, cy), 6, 1)

        for elev in elevators:
            vx = elev["rect"].x - camera_x
            vy = elev["rect"].y - camera_y
            pygame.draw.rect(screen, COLOR_ELEVATOR, (vx, vy, elev["rect"].width, elev["rect"].height),
                             border_radius=4)
            pygame.draw.rect(screen, (200, 255, 240), (vx, vy, elev["rect"].width, elev["rect"].height), 2,
                            border_radius=4)

        for door in animated_doors:
            if door["rect"].height <= 0:
                continue
            vx = door["rect"].x - camera_x
            vy = door["rect"].y - camera_y
            pygame.draw.rect(screen, COLOR_ANIM_DOOR, (vx, vy, door["rect"].width, door["rect"].height))
            pygame.draw.rect(screen, (120, 180, 255), (vx, vy, door["rect"].width, door["rect"].height), 3)

        pr = pygame.Rect(player_rect.x - camera_x, player_rect.y - camera_y, player_rect.width, player_rect.height)
        pygame.draw.rect(screen, (255, 140, 0), pr, border_radius=4)
        pygame.draw.rect(screen, (255, 200, 0), pr, 3, border_radius=4)

        # ENEMY RENDERING
        for enemy in enemies:
            vx = enemy["rect"].x - camera_x
            vy = enemy["rect"].y - camera_y
            if vx + enemy["rect"].width < 0 or vx > WIDTH or vy + enemy["rect"].height < 0 or vy > HEIGHT:
                continue

            col = (200, 50, 50) if enemy["state"] == "chase" else (160, 70, 50)
            pygame.draw.rect(screen, col, (vx, vy, enemy["rect"].width, enemy["rect"].height), border_radius=4)
            pygame.draw.rect(screen, (255, 100, 100), (vx, vy, enemy["rect"].width, enemy["rect"].height), 2, border_radius=4)

            eye_dir = enemy["dir"]
            eye_off = 8 if eye_dir > 0 else -8
            eye_y = vy + 14
            pygame.draw.circle(screen, (255, 255, 200), (int(vx + 14 + eye_off), eye_y), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(vx + 14 + eye_off), eye_y), 3)
            pygame.draw.circle(screen, (255, 255, 200), (int(vx + 36 + eye_off), eye_y), 5)
            pygame.draw.circle(screen, (0, 0, 0), (int(vx + 36 + eye_off), eye_y), 3)

        # WATER RENDERING
        water_time = pygame.time.get_ticks() / 1000.0
        for w in water:
            vx = w.x - camera_x
            vy = w.y - camera_y
            if vx + w.width < 0 or vx > WIDTH or vy + w.height < 0 or vy > HEIGHT:
                continue

            # Deep water body
            pygame.draw.rect(screen, (10, 40, 80), (vx, vy + 6, w.width, w.height - 6))

            # Animated surface wave strip
            wave_surf = pygame.Surface((w.width, 10), pygame.SRCALPHA)
            for wx_off in range(0, w.width, 4):
                wave_y = int(3 + 3 * math.sin((wx_off / 18.0) + water_time * 2.5))
                pygame.draw.circle(wave_surf, (40, 140, 210, 180), (wx_off, wave_y), 3)
            screen.blit(wave_surf, (vx, vy))

            # Shimmer lines
            for shimmer_i in range(3):
                sx = int(vx + (w.width * (0.2 + shimmer_i * 0.3)) +
                        10 * math.sin(water_time * 1.4 + shimmer_i * 2.1))
                sy = int(vy + 10 + shimmer_i * 8)
                shimmer_alpha = int(60 + 40 * math.sin(water_time * 2.0 + shimmer_i))
                shimmer_surf = pygame.Surface((30, 3), pygame.SRCALPHA)
                shimmer_surf.fill((120, 210, 255, shimmer_alpha))
                screen.blit(shimmer_surf, (sx, sy)) 

        # WATER-THEMED LORE POPUP
        if lore_display_text and lore_display_timer > 0:
            lore_display_timer -= 1

            alpha = 255
            if lore_display_timer < 60:
                alpha = int(255 * lore_display_timer / 60)

            pad_x, pad_y = 28, 18
            max_text_w   = 680
            words        = lore_display_text.split()
            lines        = []
            cur_line     = ""
            for word in words:
                test = (cur_line + " " + word).strip()
                if lore_font.size(test)[0] <= max_text_w:
                    cur_line = test
                else:
                    lines.append(cur_line)
                    cur_line = word
            if cur_line:
                lines.append(cur_line)

            line_h   = lore_font.get_height() + 4
            panel_w  = max_text_w + pad_x * 2
            panel_h  = line_h * len(lines) + pad_y * 2 + 36   

            panel_x  = WIDTH  // 2 - panel_w // 2
            panel_y  = HEIGHT // 2 - panel_h // 2

            surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            bg_col = (8, 28, 44, min(210, alpha))
            pygame.draw.rect(surf, bg_col, (0, 0, panel_w, panel_h), border_radius=10)

            for band_i, band_y_off in enumerate(range(0, panel_h, 18)):
                band_alpha = int(12 * (1 - band_i / (panel_h // 18 + 1)) * alpha / 255)
                band_col   = (40, 140, 160, band_alpha)
                pygame.draw.rect(surf, band_col, (0, band_y_off, panel_w, 9), border_radius=4)

            border_col = (80, 200, 185, min(220, alpha))
            pygame.draw.rect(surf, border_col, (0, 0, panel_w, panel_h), 2, border_radius=10)

            glint_col = (160, 255, 240, min(80, alpha))
            pygame.draw.line(surf, glint_col, (12, 3), (panel_w - 12, 3), 1)

            header_font = pygame.font.Font(None, 22)
            header_surf = header_font.render("~  T R A N S M I S S I O N  ~", True, (100, 220, 200))
            header_surf.set_alpha(alpha)
            surf.blit(header_surf, (panel_w // 2 - header_surf.get_width() // 2, pad_y - 4))

            sep_y = pad_y + 20
            pygame.draw.line(surf, (50, 140, 150, min(160, alpha)), (pad_x, sep_y), (panel_w - pad_x, sep_y), 1)

            text_col = (190, 240, 230)
            for li, line in enumerate(lines):
                t_surf = lore_font.render(line, True, text_col)
                t_surf.set_alpha(alpha)
                surf.blit(t_surf, (pad_x, sep_y + 8 + li * line_h))

            screen.blit(surf, (panel_x, panel_y))

            if lore_display_timer == 0:
                lore_display_text = None

        # HUD / TEXT DATA 
        clips_total = len(paperclips)
        clips_collected = sum(1 for c in paperclips if c["collected"])
        
        TEXT_COLOR = (120, 220, 190)
        
        hint = ui_font.render("A/D – Move   |   SPACE/W – Jump   |   E/Q – Elevator   |  F – Action Button   |  ESC – Quit", True, TEXT_COLOR)
        pos_txt = ui_font.render(f"x:{player_rect.x}  y:{player_rect.y}", True, (90, 160, 175))
        clip_txt = ui_font.render(f"Contraband Picks Found: {clips_collected}/{clips_total}", True, TEXT_COLOR)

        if constants.player_inventory_clips >= 1:
            inv_txt = ui_font.render("Lock Pick: READY", True, (80, 255, 140))
        else:
            inv_txt = ui_font.render("Lock Pick: NEED PAPERCLIP", True, (245, 110, 110))

        screen.blit(hint, (20, 20))
        screen.blit(pos_txt, (20, 50))
        screen.blit(clip_txt, (20, 80))
        screen.blit(inv_txt, (20, 110))

        if show_warning_frames > 0:
            warn_txt = ui_font.render("Find a paperclip first to pick this wall lock!", True, (255, 100, 100))
            screen.blit(warn_txt, (WIDTH // 2 - warn_txt.get_width() // 2, HEIGHT // 2 - 100))
            show_warning_frames -= 1

        pygame.display.flip()

    pygame.quit()
