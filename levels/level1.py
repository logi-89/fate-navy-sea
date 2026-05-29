import maps

import pygame

import constants

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

    spawn_x, spawn_y = 100, 300
    grounded = [p for p in platforms if HEIGHT // 4 < p.y < HEIGHT - 50]
    if grounded:
        best    = min(grounded, key=lambda p: p.x)
        spawn_x = best.x + 250
        spawn_y = best.top + 200

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

                # Jumping controls (W, SPACE, UP) completely separated from elevator riding
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

                # F Key now serves as global Action key (doors) when NOT actively driving downward
                if event.key == pygame.K_f:
                    # Only process door actions if we aren't using the key to drive an elevator down
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

        # ── Q / E PLAYER-CONTROLLED ELEVATOR MOVEMENT ──────────────────
        for elev in elevators:
            prev_y = elev["float_y"]
            
            if elev is riding_elev:
                elev_speed = abs(elev["speed"])
                
                if keys[pygame.K_q]:
                    # Move UP (decrease Y)
                    elev["float_y"] -= elev_speed
                    if elev["float_y"] < elev["origin_y"] - elev["range"]:
                        elev["float_y"] = elev["origin_y"] - elev["range"]
                elif keys[pygame.K_e]:
                    # Move DOWN (increase Y)
                    elev["float_y"] += elev_speed
                    if elev["float_y"] > elev["origin_y"] + elev["range"]:
                        elev["float_y"] = elev["origin_y"] + elev["range"]
                        
            elev["rect"].y = int(elev["float_y"])

            # Move the player smoothly along with the elevator platform
            if elev is riding_elev:
                delta_y = elev["float_y"] - prev_y
                player_y += delta_y
                player_rect.y = int(player_y)

        # ANIMATED DOORS ─────────────────────────────────────
        for door in animated_doors:
            if door["open"] and door["offset_y"] < door["max_open"]:
                door["offset_y"] = min(door["offset_y"] + 4, door["max_open"])
                door["rect"].y -= 4
                door["rect"].height = max(4, door["max_open"] - door["offset_y"])

        # Separate static solids from dynamic elevators
        static_solids = platforms + [d["rect"] for d in breakable_doors if not d["broken"]] + \
                        [d["rect"] for d in animated_doors if not d["open"] or d["offset_y"] < d["max_open"]]

        # HORIZONTAL PLAYER AXIS MOVEMENTS & COLLISIONS ────────────────
        move_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  move_x -= physics.PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x += physics.PLAYER_SPEED

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

        #  VERTICAL PLAYER AXIS MOVEMENTS & COLLISIONS ──────────────────
        player_vel_y = min(player_vel_y + physics.GRAVITY, physics.MAX_FALL_SPEED)
        player_y += player_vel_y
        player_rect.y = int(player_y)

        # ── CRUSH / SQUISH DETECTION UNDER ELEVATOR ───────────────────────
        for elev in elevators:
            if player_rect.colliderect(elev["rect"]):
                # If player is driven downwards into a static solid wall/floor
                if elev is riding_elev and keys[pygame.K_e]:
                    player_rect.bottom = elev["rect"].bottom
                    for static_floor in static_solids:
                        if player_rect.colliderect(static_floor):
                            death_screen.show_death_screen_level_one(screen, clock, tile_map)
                            return

# TOOOOOO LEVEL 2 !!!!!!!!!!!!
        for trigger in map_data.get("level_triggers", []):
            #if player_rect.colliderect(trigger["rect"]):
            if player_rect.colliderect(trigger["rect"]):
                if trigger["target_level"] == 2:
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

        #  ITEMS & BOUNDARIES ───────────────────────────────────────────
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

        # ART RENDERING LAYER ───────────────────────────────────────────
        graphics.draw_vertical_gradient(screen, (10, 30, 60), (30, 90, 140))

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

        # UI Text Data
        clips_total = len(paperclips)
        clips_collected = sum(1 for c in paperclips if c["collected"])
        hint = ui_font.render("A/D – Move   |   SPACE/W – Jump   |   Q – Elev Up   |   E – Elev Down   |  F – Action Button   |  ESC – Quit", True, (255, 255, 255))
        pos_txt = ui_font.render(f"x:{player_rect.x}  y:{player_rect.y}", True, (200, 220, 255))
        clip_txt = ui_font.render(f"Paperclips Found: {clips_collected}/{clips_total}", True, (200, 200, 220))

        if player_inventory_clips >= 1:
            inv_txt = ui_font.render("Lock Pick: READY", True, (150, 255, 150))
        else:
            inv_txt = ui_font.render("Lock Pick: NEED PAPERCLIP", True, (255, 150, 150))

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