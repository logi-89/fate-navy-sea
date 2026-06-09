import maps
import pygame
import constants
import math
import random

constants.dev_mode = True

from constants import *
from helper import mapGeneration
from helper import graphics
from helper import death_screen
from helper import enemy as enemies_module
from helper import weapons

import levels
from levels import level2
from levels import menu

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

    WIDTH, HEIGHT = screen.get_size()
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
    coins           = map_data.get("coins", [])
    shop_triggers   = map_data.get("shop_triggers", [])
    lore_drop       = map_data["lore"]

    # Safely track map height
    world_h         = len(tile_map) * physics.TILE_SIZE

    spawn_x, spawn_y = 400, 500
    grounded = [p for p in platforms if HEIGHT // 4 < p.y < HEIGHT - 50]
    if grounded:
        best    = min(grounded, key=lambda p: p.x)
        spawn_x = best.x + 215
        spawn_y = best.top + 150

        if constants.dev_mode == True:
            w_mode = True
            #spawn_x = spawn_x + 7600
            #spawn_y = spawn_y - 467
            print("in dev mode")

            if w_mode == True:
                print("MOM, I JUST HIT A CLIP!!")
                spawn_x = 4030
                spawn_y = 150



    player_x               = float(spawn_x)
    player_y               = float(spawn_y)
    player_rect            = pygame.Rect(spawn_x, spawn_y, 40, 60)
    player_vel_y           = 0.0
    is_grounded            = False
    coyote_frames          = 0
    can_double_jump        = True
    idle_frames = [pygame.image.load(f"Death Knight Idle/idle_frame_{i}.png") for i in range(1, 9)]
    running_raw = [
        pygame.image.load("Death Knight Running/fame_r_1.png"),
        pygame.image.load("Death Knight Running/frame_r_2.png"),
        pygame.image.load("Death Knight Running/fame_r_3.png"),
    ]
    run_h = idle_frames[0].get_height()
    run_w_scale = int(running_raw[0].get_width() * run_h / running_raw[0].get_height())
    running_frames = [pygame.transform.scale(f, (run_w_scale, run_h)) for f in running_raw]
    shopkeeper_img = pygame.image.load("helper/mr shopKeeper.png")
    shopkeeper_img = pygame.transform.scale(shopkeeper_img, (60, 75))
    spear_frames_raw = [
        pygame.image.load(f"Death Knight Spear/s{i}.png") for i in range(1, 5)
    ]
    spear_h = idle_frames[0].get_height()
    spear_w_scale = [int(f.get_width() * spear_h / f.get_height()) for f in spear_frames_raw]
    spear_frames = [pygame.transform.scale(f, (spear_w_scale[i], spear_h)) for i, f in enumerate(spear_frames_raw)]
    attack_anim_start = 0
    camera_x               = 0
    camera_y               = 0
    show_warning_frames    = 0
    player_hp              = constants.PLAYER_MAX_HP
    invincible_timer       = 0
    player_facing          = 1
    weapon_list            = weapons.get_available(constants.dev_mode)
    selected_weapon        = 0
    ammo_counts            = {k: (WEAPON_DEFS[k]["ammo"] + constants.player_balloon_ammo_bonus if WEAPON_DEFS[k]["ammo"] > 0 else -1) for k in weapon_list if WEAPON_DEFS[k]["ammo"] > 0}
    projectiles            = []
    weapon_cooldown        = 0
    shop_cooldown          = 0

    # LORE POPUP STATE (uses constants.lore_display_text / constants.lore_display_timer)

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
        target_fps = constants.settings["fps"]
        if target_fps > 0:
            ms = clock.tick(target_fps)
        else:
            ms = clock.tick()
        dt = max(0.01, ms / 16.666667)

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
                if event.key == pygame.K_p and constants.dev_mode:
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

                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3) and input_allowed:
                    idx = event.key - pygame.K_1
                    if idx < len(weapon_list):
                        selected_weapon = idx
                        wk = weapon_list[idx]
                        if wk == "spear":
                            attack_anim_start = pygame.time.get_ticks()
                        if weapon_cooldown <= 0 and weapons.fire(wk, player_rect, player_facing, projectiles, ammo_counts, enemies):
                            weapon_cooldown = WEAPON_DEFS[wk]["cooldown"]

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

                    for lorey in lore_drop:
                        if not lorey["collected"] and player_rect.inflate(40, 20).colliderect(lorey["rect"]):
                            constants.lore_display_text = random.choice(maps.loreDrop)
                            constants.lore_display_timer = 300
                            lorey["collected"] = True

                if event.key == pygame.K_h and input_allowed and constants.player_flasks > 0 and player_hp < constants.PLAYER_MAX_HP:
                    constants.player_flasks -= 1
                    player_hp = min(player_hp + 40, constants.PLAYER_MAX_HP)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and input_allowed:
                if selected_weapon < len(weapon_list):
                    wk = weapon_list[selected_weapon]
                    if wk == "spear":
                        attack_anim_start = pygame.time.get_ticks()
                    if weapon_cooldown <= 0 and weapons.fire(wk, player_rect, player_facing, projectiles, ammo_counts, enemies):
                        weapon_cooldown = WEAPON_DEFS[wk]["cooldown"]

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
                elev_speed = abs(elev["speed"]) * dt
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
                door["offset_y"] = min(door["offset_y"] + 4 * dt, door["max_open"])
                door["rect"].y = door["origin_y"] + door["offset_y"]
                door["rect"].height = door["max_open"] - door["offset_y"]

        static_solids = platforms + [d["rect"] for d in breakable_doors if not d["broken"]] + \
                        [d["rect"] for d in animated_doors if d["rect"].height > 0 and (not d["open"] or d["offset_y"] < d["max_open"])]

        # HORIZONTAL PLAYER AXIS MOVEMENTS & COLLISIONS
        move_x = 0
        if keys[pygame.K_a] and input_allowed or keys[pygame.K_LEFT] and input_allowed:  move_x -= physics.PLAYER_SPEED * dt
        if keys[pygame.K_d] and input_allowed or keys[pygame.K_RIGHT] and input_allowed: move_x += physics.PLAYER_SPEED * dt
        if move_x > 0: player_facing = 1
        elif move_x < 0: player_facing = -1

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
            player_vel_y = min(player_vel_y + physics.GRAVITY * dt, physics.MAX_FALL_SPEED)
            player_y += player_vel_y * dt
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

        if shop_cooldown <= 0:
            for shop_t in shop_triggers:
                if player_rect.colliderect(shop_t["rect"]):
                    menu.shop_(screen, clock, SHOP_NAME_NE)
                    shop_cooldown = 60
                    weapon_list = weapons.get_available(constants.dev_mode)
                    ammo_counts = {k: (WEAPON_DEFS[k]["ammo"] + constants.player_balloon_ammo_bonus if WEAPON_DEFS[k]["ammo"] > 0 else -1) for k in weapon_list if WEAPON_DEFS[k]["ammo"] > 0}
                    if selected_weapon >= len(weapon_list):
                        selected_weapon = 0
                    break

        all_solids = static_solids + [e["rect"] for e in elevators]

        # Resolve Floors and Ceilings
        is_grounded = False
        for plat in all_solids:
            if player_rect.colliderect(plat):
                if player_vel_y >= 0:
                    if player_rect.bottom - player_vel_y * dt <= plat.top + SNAP_TOLERANCE:
                        player_rect.bottom = plat.top
                        player_y           = float(player_rect.y)
                        player_vel_y       = 0.0
                        is_grounded        = True
                        can_double_jump    = True
                elif player_vel_y < 0:
                    if player_rect.top - player_vel_y * dt >= plat.bottom - SNAP_TOLERANCE:
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
                if constants.lore_display_timer <= 0:
                    constants.lore_display_text = random.choice(maps.loreDrop)
                    constants.lore_display_timer = 300

        for c in coins:
            if not c["collected"] and player_rect.colliderect(c["rect"]):
                c["collected"] = True
                constants.player_coins += 50

        if is_grounded:
            coyote_frames = 6
        else:
            coyote_frames = max(0, coyote_frames - dt)

        if player_rect.y > HEIGHT + 190:
            player_x      = float(spawn_x)
            player_y      = float(spawn_y)
            player_rect.x = spawn_x
            player_rect.y = spawn_y
            player_vel_y = 0.0

        # ENEMY AI
        enemy_result = enemies_module.update_enemies(
            enemies, player_rect, player_vel_y,
            static_solids, platforms, screen, clock,
            lambda: levelONE(screen, tile_map),
            projectiles, dt
        )
        if enemy_result is not None:
            player_vel_y = enemy_result
            can_double_jump = True

        # ENEMY SIDE-CONTACT DAMAGE
        if invincible_timer <= 0:
            for enemy in enemies:
                if player_rect.colliderect(enemy["rect"]):
                    dmg = enemy.get("damage", ENEMY_DAMAGE)
                    player_hp -= dmg
                    invincible_timer = INVINCIBLE_FRAMES
                    kb = 10 if player_rect.centerx < enemy["rect"].centerx else -10
                    player_x += kb * dt
                    player_rect.x = int(player_x)
                    player_vel_y = -8
                    if player_hp <= 0:
                        death_screen.show_death_screen_ENEMIES(
                            screen, clock,
                            lambda: levelONE(screen, tile_map),
                            "You were killed by an enemy!"
                        )
                        return
                    break
        invincible_timer = max(0, invincible_timer - dt)

        # WEAPON UPDATES
        weapons.update(projectiles, static_solids, enemies)

        weapons.update(projectiles, static_solids, enemies, dt)

        # Warden bullet vs. player
        for p in projectiles[:]:
            if p["weapon"] == "warden_bullet" and p["rect"].colliderect(player_rect):
                player_hp -= p["dmg"]
                projectiles.remove(p)
                if player_hp <= 0:
                        death_screen.show_death_screen_ENEMIES(
                            screen, clock,
                            lambda: levelONE(screen, tile_map),
                            "You were killed by an enemy!"
                        )
                        return

        weapon_cooldown = max(0, weapon_cooldown - dt)
        shop_cooldown = max(0, shop_cooldown - dt)

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
        render_scale = constants.settings["render_scale"]
        if render_scale != 1.0:
            render_w = int(WIDTH * render_scale)
            render_h = int(HEIGHT * render_scale)
            render_surf = pygame.Surface((render_w, render_h))
            orig_screen = screen
            screen = render_surf

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

        for c in coins:
            if c["collected"]:
                continue
            vx = c["rect"].x - camera_x
            vy = c["rect"].y - camera_y
            if vx + c["rect"].width < 0 or vx > WIDTH or vy + c["rect"].height < 0 or vy > HEIGHT:
                continue
            cx = int(vx + c["rect"].width // 2)
            cy = int(vy + c["rect"].height // 2)
            pygame.draw.circle(screen, (255, 215, 0), (cx, cy), 8)
            pygame.draw.circle(screen, (255, 240, 150), (cx, cy), 8, 2)
            pygame.draw.circle(screen, (200, 160, 0), (cx, cy), 3)

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

        SPEAR_ANIM_DURATION = 400
        if attack_anim_start and pygame.time.get_ticks() - attack_anim_start < SPEAR_ANIM_DURATION:
            elapsed = pygame.time.get_ticks() - attack_anim_start
            idx = int(elapsed / (SPEAR_ANIM_DURATION / len(spear_frames)))
            if idx >= len(spear_frames):
                idx = len(spear_frames) - 1
            frame = spear_frames[idx]
        elif move_x != 0 and input_allowed:
            run_idx = (pygame.time.get_ticks() // 150) % len(running_frames)
            frame = running_frames[run_idx]
        else:
            frame_idx = (pygame.time.get_ticks() // 180) % len(idle_frames)
            frame = idle_frames[frame_idx]
        if player_facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(frame, (player_rect.x - camera_x - 24, player_rect.y - camera_y - 44))

        for shop_t in shop_triggers:
            sx = shop_t["rect"].x - camera_x
            sy = shop_t["rect"].y - camera_y - 25
            if -60 < sx < WIDTH and -75 < sy < HEIGHT:
                screen.blit(shopkeeper_img, (sx, sy))

        enemies_module.render_enemies(screen, enemies, camera_x, camera_y)
        weapons.render(screen, projectiles, camera_x, camera_y, dt)

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

        if render_scale != 1.0:
            pygame.transform.smoothscale(screen, (WIDTH, HEIGHT), orig_screen)
            screen = orig_screen

        # Lore drop text (crisp, not supersampled)
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
                q_surf = lore_font.render("?", True, (10, 30, 40))
                screen.blit(q_surf, (cx - q_surf.get_width() // 2, cy - q_surf.get_height() // 2))
                f_surf = pygame.font.Font(None, 20).render("[F]", True, (120, 220, 190))
                screen.blit(f_surf, (cx - f_surf.get_width() // 2, cy + radius + 4))

        # ── HUD ────────────────────────────────────────────────────────────────────
        hs = constants.settings["hud_scale"] / 100
        ui_font_sm  = pygame.font.Font(None, int(22 * hs))
        ui_font_xs  = pygame.font.Font(None, int(18 * hs))
        hud_dark    = (4, 10, 18, 200)
        hud_border  = (60, 180, 110, 60)
        hud_green   = (80, 220, 150)
        hud_dim     = (80, 140, 110)

        def draw_panel(surf, x, y, w, h, alpha=200):
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            br = max(1, int(5 * hs))
            pygame.draw.rect(s, (4, 12, 20, alpha), (0, 0, w, h), border_radius=br)
            pygame.draw.rect(s, (60, 180, 110, 55), (0, 0, w, h), 1, border_radius=br)
            surf.blit(s, (x, y))

        # ── TOP HINT BAR ──
        hints = [("A/D","move"), ("SPACE","jump"), ("E/Q","elevator"),
                ("F","action"), ("H","heal"), ("1-3","weapon"), ("P","quit (dev)"), ("ESC","quit")]
        hint_parts = []
        for key, action in hints:
            hint_parts.append((key, (100, 180, 140)))
            hint_parts.append((f" {action}", (60, 130, 100)))
            hint_parts.append(("  │  ", (40, 80, 60)))
        hint_parts = hint_parts[:-1]

        hint_total_w = sum(ui_font_xs.size(t)[0] for t, _ in hint_parts)
        draw_panel(screen, int(14 * hs), int(12 * hs), int((hint_total_w + 20) * hs), int(22 * hs), alpha=170)
        cx = int(24 * hs)
        for text, col in hint_parts:
            s = ui_font_xs.render(text, True, col)
            screen.blit(s, (cx, int(16 * hs)))
            cx += s.get_width()

        # ── COORDS (subtle) ──
        coord_s = ui_font_xs.render(f"x:{player_rect.x}  y:{player_rect.y}", True, (60, 110, 80))
        screen.blit(coord_s, (int(18 * hs), int(38 * hs)))

        # ── HEALTH PANEL ──
        PNL_X, PNL_Y, PNL_W, PNL_H = int(14 * hs), HEIGHT - int(100 * hs), int(190 * hs), int(56 * hs)
        draw_panel(screen, PNL_X, PNL_Y, PNL_W, PNL_H)
        lbl = ui_font_xs.render("INTEGRITY", True, (80, 140, 100))
        screen.blit(lbl, (PNL_X + int(10 * hs), PNL_Y + int(8 * hs)))

        bar_x, bar_y = PNL_X + int(10 * hs), PNL_Y + int(24 * hs)
        bar_w, bar_h = PNL_W - int(20 * hs), max(1, int(8 * hs))
        hp_ratio = max(0.0, player_hp / constants.PLAYER_MAX_HP)
        hp_color = (56, 200, 122) if hp_ratio > 0.4 else (220, 140, 40) if hp_ratio > 0.2 else (210, 60, 60)
        pygame.draw.rect(screen, (20, 45, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=max(1, int(4 * hs)))
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h), border_radius=max(1, int(4 * hs)))
        pygame.draw.rect(screen, (60, 140, 90, 80), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=max(1, int(4 * hs)))

        hp_val = ui_font_xs.render(f"{player_hp} / {constants.PLAYER_MAX_HP}", True, (100, 220, 160))
        screen.blit(hp_val, (PNL_X + int(10 * hs), PNL_Y + int(38 * hs)))

        flask_surf = ui_font_xs.render(f"⚕ {constants.player_flasks}", True, (140, 220, 100))
        screen.blit(flask_surf, (PNL_X + PNL_W - flask_surf.get_width() - int(8 * hs), PNL_Y + int(38 * hs)))

        # ── CLIPS / LOCKPICK PANEL ──
        clips_collected = sum(1 for c in paperclips if c["collected"])
        clips_total = len(paperclips)
        has_pick = constants.player_inventory_clips >= 1

        CL_X, CL_Y, CL_W, CL_H = int(14 * hs), HEIGHT - int(38 * hs), int(190 * hs), int(28 * hs)
        draw_panel(screen, CL_X, CL_Y, CL_W, CL_H)

        for i in range(min(clips_total, 5)):
            dot_col = (80, 210, 140) if i < clips_collected else (30, 70, 50)
            pygame.draw.circle(screen, dot_col, (CL_X + int(14 * hs) + i * int(14 * hs), CL_Y + int(14 * hs)), max(1, int(4 * hs)))

        pick_col  = (60, 230, 140) if has_pick else (200, 80, 70)
        pick_text = "READY" if has_pick else "NO PICK"
        p_surf = ui_font_xs.render(pick_text, True, pick_col)
        screen.blit(p_surf, (CL_X + CL_W - p_surf.get_width() - int(8 * hs), CL_Y + int(3 * hs)))

        coin_surf = ui_font_xs.render(f"¢ {constants.player_coins}", True, (255, 215, 0))
        screen.blit(coin_surf, (CL_X + CL_W - coin_surf.get_width() - int(8 * hs), CL_Y + int(14 * hs)))

        # ── WEAPON SLOTS ──
        slot_w, slot_h = int(160 * hs), int(24 * hs)
        slot_gap = int(4 * hs)
        for wi, wk in enumerate(weapon_list):
            defs   = WEAPON_DEFS[wk]
            active = wi == selected_weapon
            sx = WIDTH - slot_w - int(14 * hs)
            sy = HEIGHT - int(38 * hs) - (len(weapon_list) - 1 - wi) * (slot_h + slot_gap)

            bg_alpha = 210 if active else 150
            draw_panel(screen, sx, sy, slot_w, slot_h, alpha=bg_alpha)
            if active:
                br = max(1, int(5 * hs))
                pygame.draw.rect(screen, (60, 200, 120, 100), (sx, sy, slot_w, slot_h), 1, border_radius=br)
                pygame.draw.circle(screen, (60, 230, 130), (sx + int(8 * hs), sy + int(12 * hs)), max(1, int(3 * hs)))

            key_col  = (80, 190, 130) if active else (50, 110, 80)
            name_col = (140, 230, 180) if active else (90, 150, 120)
            ammo_col = (80, 210, 150) if active else (60, 110, 90)

            ammo    = ammo_counts.get(wk, defs["ammo"])
            ammo_s  = "∞" if defs["ammo"] < 0 else str(ammo)

            k_surf = ui_font_xs.render(str(wi + 1), True, key_col)
            n_surf = ui_font_xs.render(defs["name"].lower(), True, name_col)
            a_surf = ui_font_xs.render(ammo_s, True, ammo_col)

            screen.blit(k_surf, (sx + int(14 * hs), sy + int(5 * hs)))
            screen.blit(n_surf, (sx + int(28 * hs), sy + int(5 * hs)))
            screen.blit(a_surf, (sx + slot_w - a_surf.get_width() - int(8 * hs), sy + int(5 * hs)))

        # ── LOW AMMO / NO PICK WARNING ──
        if show_warning_frames > 0:
            warn_font = pygame.font.Font(None, int(30 * hs))
            warn_s = warn_font.render("Find a paperclip first!", True, (255, 100, 100))
            wx = WIDTH // 2 - warn_s.get_width() // 2
            draw_panel(screen, wx - int(12 * hs), HEIGHT // 2 - int(118 * hs), warn_s.get_width() + int(24 * hs), int(30 * hs))
            screen.blit(warn_s, (wx, HEIGHT // 2 - int(112 * hs)))
            show_warning_frames -= dt

        graphics.update_lore_display(screen, dt)

        pygame.display.flip()

    pygame.quit()
