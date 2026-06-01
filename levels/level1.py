import maps

import pygame

import constants

constants.dev_mode = True

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
    lore_drop = map_data["lore"]

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

    spawn_x, spawn_y = 100, 100
    grounded = [p for p in platforms if HEIGHT // 4 < p.y < HEIGHT - 50]
    if grounded:
        best    = min(grounded, key=lambda p: p.x)
        spawn_x = best.x + 250
        spawn_y = best.top + 200

        if constants.dev_mode == True:
            spawn_x = spawn_x + 6000
            spawn_y = spawn_y - 200

    player_x               = float(spawn_x)
    player_y               = float(spawn_y)
    player_rect            = pygame.Rect(spawn_x, spawn_y, 40, 60)

    # Nudge spawn upward if it overlaps a platform
    for plat in platforms:
        if player_rect.colliderect(plat):
            player_rect.bottom = plat.top
            spawn_x = player_rect.x
            spawn_y = player_rect.y
            break
    player_vel_y           = 0.0
    is_grounded            = False
    coyote_frames          = 0
    can_double_jump        = True
    camera_x               = 0
    show_warning_frames    = 0

    # ── LORE POPUP STATE 
    lore_display_text  = None   # currently shown lore string (None = hidden)
    lore_display_timer = 0      # frames remaining to show it (0 = hidden)

    SNAP_TOLERANCE = 8
    ui_font   = pygame.font.Font(None, 30)
    lore_font = pygame.font.Font(None, 26)   # slightly smaller for lore text

    #COLOR_ELEVATOR = (80, 210, 190)
    COLOR_ELEVATOR  = (25, 75, 75)
    #COLOR_ANIM_DOOR = (50, 80, 160)
    COLOR_ANIM_DOOR = (45, 55, 65)

    # Loading screen — blocks input during transition
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

    input_allowed = False

    while running:
        dt = clock.tick(60)

        # Wait for all keys to be released before allowing input
        if not input_allowed:
            key_state = pygame.key.get_pressed()
            all_released = True
            for scancode in range(len(key_state)):
                if key_state[scancode]:
                    all_released = False
                    break
            if all_released:
                input_allowed = True

        # Initialise early so the event handler never reads unbound
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

                # Jumping controls (W, SPACE, UP) completely separated from elevator riding
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

                # F Key — interact with doors AND lore drops
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

                    # ── LORE DROP interaction: press F near a "?" to read ──
                    import random
                    for lorey in lore_drop:
                        if not lorey["collected"]:
                            continue
                        if player_rect.inflate(40, 20).colliderect(lorey["rect"]):
                            lore_display_text  = random.choice(maps.loreDrop)
                            lore_display_timer = 300   # 5s at 60 fps

        keys = pygame.key.get_pressed()

        # ── ELEVATOR REGISTRATION ─────────────────────────────────────
        # Find which elevator platform the player is landing/standing on
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
                
                # E=UP / Q=DOWN (standardised across both levels)
                if keys[pygame.K_e] and input_allowed:
                    # Move UP (decrease Y)
                    elev["float_y"] -= elev_speed
                    if elev["float_y"] < elev["origin_y"] - elev["range"]:
                        elev["float_y"] = elev["origin_y"] - elev["range"]
                elif keys[pygame.K_q] and input_allowed:
                    # Move DOWN (increase Y)
                    elev["float_y"] += elev_speed
                    if elev["float_y"] > elev["max_y"]:
                        elev["float_y"] = elev["max_y"]
                        
            elev["rect"].y = int(elev["float_y"])

            # Move the player smoothly along with the elevator platform
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

        # Separate static solids from dynamic elevators
        static_solids = platforms + [d["rect"] for d in breakable_doors if not d["broken"]] + \
                        [d["rect"] for d in animated_doors if not d["open"] or d["offset_y"] < d["max_open"]]

        # HORIZONTAL PLAYER AXIS MOVEMENTS & COLLISIONS 
        move_x = 0
        if keys[pygame.K_a] and input_allowed or keys[pygame.K_LEFT] and input_allowed:  move_x -= physics.PLAYER_SPEED
        if keys[pygame.K_d] and input_allowed or keys[pygame.K_RIGHT] and input_allowed: move_x += physics.PLAYER_SPEED

        player_x = max(0.0, min(player_x + move_x, world_w - player_rect.width))
        player_rect.x = int(player_x)

        # Exclude currently ridden elevator from horizontal body blocks 
        horizontal_solids = static_solids + [e["rect"] for e in elevators if e is not riding_elev]

        # Resolve Horizontal Walls (allows jumping and running off easily)
        for plat in horizontal_solids:
            if player_rect.colliderect(plat):
                if move_x > 0:
                    player_rect.right = plat.left
                    player_x = float(player_rect.x)
                elif move_x < 0:
                    player_rect.left = plat.right
                    player_x = float(player_rect.x)

        #  VERTICAL PLAYER AXIS MOVEMENTS & COLLISIONS 
        if riding_elev is None:
            player_vel_y = min(player_vel_y + physics.GRAVITY, physics.MAX_FALL_SPEED)
            player_y += player_vel_y
            player_rect.y = int(player_y)

        # CRUSH / SQUISH DETECTION UNDER ELEVATOR 
        for elev in elevators:
            if player_rect.colliderect(elev["rect"]):
                # Crush: Q = DOWN, so driving down into a ceiling is fatal
                if elev is riding_elev and keys[pygame.K_q]:
                    player_rect.bottom = elev["rect"].bottom
                    for static_floor in static_solids:
                        if player_rect.colliderect(static_floor):
                            death_screen.show_death_screen(screen, clock, lambda: levelONE(screen, tile_map))
                            return

    # TOOOOOO LEVEL 2 !!!!!!!!!!!!
        for trigger in map_data.get("level_triggers", []):
            if player_rect.colliderect(trigger["rect"]):
                if trigger["target_level"] == 2:
                    print("TOOOOOO LEVEL 2 !!!!!!!!!!!!")
                    levels.level2.intro(screen, clock)
                    return

        # Re-include ALL platforms for floor and ceiling validation
        all_solids = static_solids + [e["rect"] for e in elevators]

        # Resolve Floors and Ceilings
        is_grounded = False
        for plat in all_solids:
            if player_rect.colliderect(plat):
                if player_vel_y >= 0: # Falling/Grounded down
                    if player_rect.bottom - player_vel_y <= plat.top + SNAP_TOLERANCE:
                        player_rect.bottom = plat.top
                        player_y           = float(player_rect.y)
                        player_vel_y       = 0.0
                        is_grounded        = True
                        can_double_jump    = True
                elif player_vel_y < 0: # Jumping up into ceiling
                    if player_rect.top - player_vel_y >= plat.bottom - SNAP_TOLERANCE:
                        player_rect.top = plat.bottom
                        player_y        = float(player_rect.y)
                        player_vel_y    = 0.0

        # Maintain ground tracking if riding an active elevator
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
                constants.player_inventory_clips += 1

        #  LORE DROP collection: walk over "?" to reveal it 
        for lorey in lore_drop:
            if not lorey["collected"] and player_rect.colliderect(lorey["rect"]):
                lorey["collected"] = True   # player has reached the question mark

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
        graphics.draw_vertical_gradient(screen, (4, 8, 15), (14, 42, 54))

        for plat in platforms:
            vx = plat.x - camera_x
            if vx + plat.width < 0 or vx > WIDTH:
                continue
            pygame.draw.rect(screen, GROUND_TOP, (vx, plat.y, plat.width, 8))
            pygame.draw.rect(screen, GROUND_DIRT, (vx, plat.y + 8, plat.width, plat.height - 8))
            pygame.draw.rect(screen, GROUND_SIDE, (vx, plat.y, plat.width, plat.height), 2)

        for door in breakable_doors:
            if door["broken"]:
                continue
            vx = door["rect"].x - camera_x
            if vx + door["rect"].width < 0 or vx > WIDTH:
                continue
            color = COLOR_DOOR_DAMAGED if door["hp"] < 3 else COLOR_DOOR_INTACT
            pygame.draw.rect(screen, color, (vx, door["rect"].y, door["rect"].width, door["rect"].height))
            pygame.draw.rect(screen, (220, 160, 80), (vx, door["rect"].y, door["rect"].width, door["rect"].height), 3)
            for i in range(door["hp"]):
                pygame.draw.circle(screen, (255, 220, 80), (int(vx + 10 + i * 14), door["rect"].y + 8), 5)

        for clip in paperclips:
            if clip["collected"]:
                continue
            vx = clip["rect"].x - camera_x
            if vx + clip["rect"].width < 0 or vx > WIDTH:
                continue
            cx = int(vx + clip["rect"].width // 2)
            cy = int(clip["rect"].y + clip["rect"].height // 2)
            pygame.draw.circle(screen, COLOR_PAPERCLIP, (cx, cy), 8)
            pygame.draw.circle(screen, (240, 240, 255), (cx, cy), 8, 2)

        for lorey in lore_drop:
            vx = lorey["rect"].x - camera_x
            if vx + lorey["rect"].width < 0 or vx > WIDTH:
                continue
            cx = int(vx + lorey["rect"].width // 2)
            cy = int(lorey["rect"].y + lorey["rect"].height // 2)

            if not lorey["collected"]:
                # Pulsing cyan question-mark orb (pre-pickup)
                pulse = abs(pygame.time.get_ticks() % 1200 - 600) / 600.0   # 0..1 sine-like
                radius = int(10 + pulse * 4)
                alpha_surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                glow_col = (40, int(180 + pulse * 60), int(200 + pulse * 55), 90)
                pygame.draw.circle(alpha_surf, glow_col, (radius + 2, radius + 2), radius + 2)
                screen.blit(alpha_surf, (cx - radius - 2, cy - radius - 2))
                pygame.draw.circle(screen, (80, 220, 210), (cx, cy), radius)
                pygame.draw.circle(screen, (180, 255, 245), (cx, cy), radius, 2)
                q_surf = lore_font.render("?", True, (10, 30, 40))
                screen.blit(q_surf, (cx - q_surf.get_width() // 2, cy - q_surf.get_height() // 2))
                # small "F" hint badge below
                f_surf = pygame.font.Font(None, 20).render("[F]", True, (120, 220, 190))
                screen.blit(f_surf, (cx - f_surf.get_width() // 2, cy + radius + 4))
            else:
                # Collected — show a faint dim dot so player knows they can re-press F
                pygame.draw.circle(screen, (30, 80, 90), (cx, cy), 6)
                pygame.draw.circle(screen, (60, 140, 160), (cx, cy), 6, 1)

        for elev in elevators:
            vx = elev["rect"].x - camera_x
            pygame.draw.rect(screen, COLOR_ELEVATOR, (vx, elev["rect"].y, elev["rect"].width, elev["rect"].height),
                             border_radius=4)
            pygame.draw.rect(screen, (200, 255, 240), (vx, elev["rect"].y, elev["rect"].width, elev["rect"].height), 2,
                             border_radius=4)

        for door in animated_doors:
            if door["rect"].height <= 0:
                continue
            vx = door["rect"].x - camera_x
            pygame.draw.rect(screen, COLOR_ANIM_DOOR, (vx, door["rect"].y, door["rect"].width, door["rect"].height))
            pygame.draw.rect(screen, (120, 180, 255), (vx, door["rect"].y, door["rect"].width, door["rect"].height), 3)

        pr = pygame.Rect(player_rect.x - camera_x, player_rect.y, player_rect.width, player_rect.height)
        pygame.draw.rect(screen, (255, 140, 0), pr, border_radius=4)
        pygame.draw.rect(screen, (255, 200, 0), pr, 3, border_radius=4)

        # WATER-THEMED LORE POPUP
        if lore_display_text and lore_display_timer > 0:
            lore_display_timer -= 1

            # Fade out in the last 60 frames
            alpha = 255
            if lore_display_timer < 60:
                alpha = int(255 * lore_display_timer / 60)

            # Panel dimensions
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
            panel_h  = line_h * len(lines) + pad_y * 2 + 36   # +36 for header row

            panel_x  = WIDTH  // 2 - panel_w // 2
            panel_y  = HEIGHT // 2 - panel_h // 2

            # Draw on a transparent surface so we can alpha-blend
            surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

            # Background: deep ocean teal with partial transparency
            bg_col = (8, 28, 44, min(210, alpha))
            pygame.draw.rect(surf, bg_col, (0, 0, panel_w, panel_h), border_radius=10)

            # Layered water shimmer bands
            for band_i, band_y_off in enumerate(range(0, panel_h, 18)):
                band_alpha = int(12 * (1 - band_i / (panel_h // 18 + 1)) * alpha / 255)
                band_col   = (40, 140, 160, band_alpha)
                pygame.draw.rect(surf, band_col,
                                 (0, band_y_off, panel_w, 9), border_radius=4)

            # Border: bioluminescent seafoam ring
            border_col = (80, 200, 185, min(220, alpha))
            pygame.draw.rect(surf, border_col, (0, 0, panel_w, panel_h), 2, border_radius=10)

            # Inner highlight line at the top (simulates water surface glint)
            glint_col = (160, 255, 240, min(80, alpha))
            pygame.draw.line(surf, glint_col, (12, 3), (panel_w - 12, 3), 1)

            # Header: "~  TRANSMISSION  ~" styled title
            header_font = pygame.font.Font(None, 22)
            header_surf = header_font.render("~  T R A N S M I S S I O N  ~", True,
                                             (100, 220, 200))
            header_surf.set_alpha(alpha)
            surf.blit(header_surf, (panel_w // 2 - header_surf.get_width() // 2, pad_y - 4))

            # Separator squiggle (just a line with dots)
            sep_y = pad_y + 20
            pygame.draw.line(surf, (50, 140, 150, min(160, alpha)),
                             (pad_x, sep_y), (panel_w - pad_x, sep_y), 1)

            # Lore text lines
            text_col = (190, 240, 230)
            for li, line in enumerate(lines):
                t_surf = lore_font.render(line, True, text_col)
                t_surf.set_alpha(alpha)
                surf.blit(t_surf, (pad_x, sep_y + 8 + li * line_h))

            screen.blit(surf, (panel_x, panel_y))

            if lore_display_timer == 0:
                lore_display_text = None

        #  HUD / TEXT DATA 
        clips_total = len(paperclips)
        clips_collected = sum(1 for c in paperclips if c["collected"])
        
        # Bioluminescent green/seafoam tone for text legibility
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
    # I love pygame