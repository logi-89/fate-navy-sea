import pygame
import constants
from constants import *
from helper.graphics import *
from helper.music import Music
import maps
import levels.level1
import levels.level2
import levels.level3

jukebox = None

def show_title_screen(screen, clock, jukebox_object):
    global jukebox

    jukebox = jukebox_object
    running = True
    t = 0

    WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
    title_font = pygame.font.Font(None, 110)
    sub_font = pygame.font.Font(None, 44)
    button_font = pygame.font.Font(None, 56)

    start_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 40, 240, 60)
    chapters_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 110, 240, 60)
    settings_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 180, 240, 60)

    while running:
        WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
        mouse_pos = pygame.mouse.get_pos()
        hovered_start = start_button.collidepoint(mouse_pos)
        hovered_chapters = chapters_button.collidepoint(mouse_pos)
        hovered_settings = settings_button.collidepoint(mouse_pos)

        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))
        pygame.draw.circle(screen, (160, 220, 255), (WIDTH // 2, 180), 90)
        pygame.draw.circle(screen, (200, 245, 255), (WIDTH // 2, 180), 55)
        ocean_top = HEIGHT - 320
        pygame.draw.rect(screen, (10, 45, 75), (0, ocean_top, WIDTH, HEIGHT - ocean_top))
        draw_waves(screen, t)

        title_text = title_font.render("Fate: Navy Sea", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)

        sub_text = sub_font.render("Set sail into the storm", True, (220, 245, 255))
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 65))
        screen.blit(sub_text, sub_rect)

        pygame.draw.rect(screen, title_screen.HOVER_COLOR if hovered_start else title_screen.BUTTON_COLOR, start_button, border_radius=18)
        pygame.draw.rect(screen, WHITE, start_button, 3, border_radius=18)
        start_text = button_font.render("Start", True, WHITE)
        start_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_rect)

        pygame.draw.rect(screen, title_screen.HOVER_COLOR if hovered_chapters else title_screen.BUTTON_COLOR, chapters_button, border_radius=18)
        pygame.draw.rect(screen, WHITE, chapters_button, 3, border_radius=18)
        chapters_text = button_font.render("Chapters", True, WHITE)
        chapters_rect = chapters_text.get_rect(center=chapters_button.center)
        screen.blit(chapters_text, chapters_rect)

        pygame.draw.rect(screen, title_screen.HOVER_COLOR if hovered_settings else title_screen.BUTTON_COLOR, settings_button, border_radius=18)
        pygame.draw.rect(screen, WHITE, settings_button, 3, border_radius=18)
        settings_text = button_font.render("Settings", True, WHITE)
        settings_rect = settings_text.get_rect(center=settings_button.center)
        screen.blit(settings_text, settings_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return screen
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    levels.level1.intro(screen, clock)
                    return screen
                if chapters_button.collidepoint(event.pos):
                    screen = chapter_select(screen, clock)
                if settings_button.collidepoint(event.pos):
                    screen = settings_menu(screen, clock)

        pygame.display.flip()
        clock.tick(60)
        t += 0.03

    return screen


def chapter_select(screen, clock):
    running = True
    WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
    font_title = pygame.font.Font(None, 80)
    font_chapter = pygame.font.Font(None, 48)
    font_desc = pygame.font.Font(None, 28)

    chapters = [
        ("Chapter 1", "The Depths", levels.level1.intro),
        ("Chapter 2", "The Train", lambda s, c: levels.level2.levelTWO(s, maps.L2)),
        ("Chapter 3", "The Laboratory", levels.level3.intro),
    ]

    while running:
        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))

        title = font_title.render("Select Chapter", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

        for i, (name, desc, func) in enumerate(chapters):
            y = 150 + i * 120
            rect = pygame.Rect(WIDTH // 2 - 200, y, 400, 80)
            hovered = rect.collidepoint(pygame.mouse.get_pos())

            bg = title_screen.HOVER_COLOR if hovered else title_screen.BUTTON_COLOR
            pygame.draw.rect(screen, bg, rect, border_radius=12)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=12)

            n = font_chapter.render(name, True, WHITE)
            screen.blit(n, (rect.x + 20, rect.y + 8))
            d = font_desc.render(desc, True, (180, 220, 240))
            screen.blit(d, (rect.x + 20, rect.y + 45))

        back_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 70, 160, 50)
        back_hovered = back_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (50, 50, 70) if back_hovered else (40, 40, 55), back_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, back_rect, 2, border_radius=10)
        back_text = font_chapter.render("Back", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=back_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return screen
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, (name, desc, func) in enumerate(chapters):
                    y = 150 + i * 120
                    rect = pygame.Rect(WIDTH // 2 - 200, y, 400, 80)
                    if rect.collidepoint(event.pos):
                        func(screen, clock)
                        return screen
                if back_rect.collidepoint(event.pos):
                    return screen

        pygame.display.flip()
        clock.tick(60)


def settings_menu(screen, clock):
    global jukebox
    running = True
    font_title = pygame.font.Font(None, 80)
    font_item = pygame.font.Font(None, 40)
    font_value = pygame.font.Font(None, 30)

    res_index = 0
    for i, (rw, rh) in enumerate(constants.AVAILABLE_RESOLUTIONS):
        if rw == constants.settings["display_w"] and rh == constants.settings["display_h"]:
            res_index = i
            break

    mode_index = 0
    for i, m in enumerate(constants.DISPLAY_MODES):
        if m == constants.settings["display_mode"]:
            mode_index = i
            break

    fps_index = 0
    for i, fps in enumerate(constants.FPS_OPTIONS):
        if fps == constants.settings["fps"]:
            fps_index = i
            break

    rs_index = 0
    for i, rs in enumerate(constants.RENDER_SCALE_OPTIONS):
        if rs == constants.settings["render_scale"]:
            rs_index = i
            break

    dragging_volume = False
    dragging_hud = False

    button_back = pygame.Rect(constants.WIDTH // 2 - 100, constants.HEIGHT - 100, 200, 55)

    def get_slider_rect(center_y):
        return pygame.Rect(constants.WIDTH // 2 - 100, center_y - 6, 340, 12)

    def value_from_pos(slider, mouse_x, max_val=100):
        ratio = (mouse_x - slider.x) / slider.w
        return int(max(0, min(max_val, ratio * max_val)))

    def apply_display():
        nonlocal screen
        mode = constants.settings["display_mode"]
        dw = constants.settings["display_w"]
        dh = constants.settings["display_h"]
        if mode == "fullscreen":
            screen = pygame.display.set_mode((dw, dh), pygame.FULLSCREEN)
        elif mode == "borderless":
            info = pygame.display.Info()
            screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
            dw, dh = info.current_w, info.current_h
        else:
            screen = pygame.display.set_mode((dw, dh))
        constants.WIDTH = screen.get_width()
        constants.HEIGHT = screen.get_height()

    while running:
        WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
        mouse_pos = pygame.mouse.get_pos()

        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))

        title = font_title.render("Settings", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

        labels = [
            ("Master Volume", 180, constants.settings["master_volume"], 100),
            ("HUD Scale", 270, constants.settings["hud_scale"], 200),
        ]

        for label, cy, val, max_val in labels:
            lbl = font_item.render(label, True, (180, 220, 240))
            screen.blit(lbl, (WIDTH // 2 - 340, cy - 14))

            val_text = font_value.render(f"{round(val/100,1)}", True, (100, 220, 180))
            screen.blit(val_text, (WIDTH // 2 + 250, cy - 10))

            slider = get_slider_rect(cy)
            pygame.draw.rect(screen, (20, 50, 70), slider, border_radius=6)
            ratio = val / max_val
            fill_w = int(slider.w * ratio)
            if fill_w > 0:
                fill = pygame.Rect(slider.x, slider.y, fill_w, slider.h)
                pygame.draw.rect(screen, (60, 200, 160), fill, border_radius=6)
            handle_x = slider.x + int(slider.w * ratio)
            pygame.draw.circle(screen, (180, 255, 230), (handle_x, slider.centery), 9)
            pygame.draw.circle(screen, (60, 200, 160), (handle_x, slider.centery), 9, 2)

        # Resolution selector
        res_lbl = font_item.render("Resolution", True, (180, 220, 240))
        screen.blit(res_lbl, (WIDTH // 2 - 340, 340))
        rw, rh = constants.AVAILABLE_RESOLUTIONS[res_index]
        res_text = font_item.render(f"{rw} x {rh}", True, WHITE)
        res_rect = pygame.Rect(WIDTH // 2 - 100, 325, 200, 40)
        pygame.draw.rect(screen, (25, 65, 95), res_rect, border_radius=8)
        pygame.draw.rect(screen, (60, 160, 200), res_rect, 2, border_radius=8)
        screen.blit(res_text, res_text.get_rect(center=res_rect.center))

        left_arr = pygame.Rect(WIDTH // 2 - 130, 335, 22, 22)
        right_arr = pygame.Rect(WIDTH // 2 + 110, 335, 22, 22)
        pygame.draw.polygon(screen, (120, 220, 200), [(left_arr.right, left_arr.y), (left_arr.x, left_arr.centery), (left_arr.right, left_arr.bottom)])
        pygame.draw.polygon(screen, (120, 220, 200), [(right_arr.x, right_arr.y), (right_arr.right, right_arr.centery), (right_arr.x, right_arr.bottom)])

        # Display mode selector
        mode_lbl = font_item.render("Display Mode", True, (180, 220, 240))
        screen.blit(mode_lbl, (WIDTH // 2 - 340, 410))
        mode_text = font_item.render(constants.DISPLAY_MODES[mode_index].capitalize(), True, WHITE)
        mode_rect = pygame.Rect(WIDTH // 2 - 100, 395, 200, 40)
        pygame.draw.rect(screen, (25, 65, 95), mode_rect, border_radius=8)
        pygame.draw.rect(screen, (60, 160, 200), mode_rect, 2, border_radius=8)
        screen.blit(mode_text, mode_text.get_rect(center=mode_rect.center))

        mode_left = pygame.Rect(WIDTH // 2 - 130, 405, 22, 22)
        mode_right = pygame.Rect(WIDTH // 2 + 110, 405, 22, 22)
        pygame.draw.polygon(screen, (120, 220, 200), [(mode_left.right, mode_left.y), (mode_left.x, mode_left.centery), (mode_left.right, mode_left.bottom)])
        pygame.draw.polygon(screen, (120, 220, 200), [(mode_right.x, mode_right.y), (mode_right.right, mode_right.centery), (mode_right.x, mode_right.bottom)])

        # FPS selector
        fps_lbl = font_item.render("FPS", True, (180, 220, 240))
        screen.blit(fps_lbl, (WIDTH // 2 - 340, 480))
        fps_val = constants.FPS_OPTIONS[fps_index]
        fps_text = font_item.render(f"{fps_val if fps_val > 0 else 'Uncapped'}", True, WHITE)
        fps_rect = pygame.Rect(WIDTH // 2 - 100, 465, 200, 40)
        pygame.draw.rect(screen, (25, 65, 95), fps_rect, border_radius=8)
        pygame.draw.rect(screen, (60, 160, 200), fps_rect, 2, border_radius=8)
        screen.blit(fps_text, fps_text.get_rect(center=fps_rect.center))

        fps_left = pygame.Rect(WIDTH // 2 - 130, 475, 22, 22)
        fps_right = pygame.Rect(WIDTH // 2 + 110, 475, 22, 22)
        pygame.draw.polygon(screen, (120, 220, 200), [(fps_left.right, fps_left.y), (fps_left.x, fps_left.centery), (fps_left.right, fps_left.bottom)])
        pygame.draw.polygon(screen, (120, 220, 200), [(fps_right.x, fps_right.y), (fps_right.right, fps_right.centery), (fps_right.x, fps_right.bottom)])

        # Back button
        hovered_back = button_back.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (60, 110, 170) if hovered_back else (40, 80, 120), button_back, border_radius=12)
        pygame.draw.rect(screen, WHITE, button_back, 2, border_radius=12)
        back_text = font_item.render("BACK", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=button_back.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                vol_slider = get_slider_rect(180)
                if vol_slider.collidepoint(event.pos):
                    dragging_volume = True
                    val = value_from_pos(vol_slider, event.pos[0])
                    constants.settings["master_volume"] = val
                    if jukebox:
                        jukebox.set_volume(val / 100.0)

                hud_slider = get_slider_rect(270)
                if hud_slider.collidepoint(event.pos):
                    dragging_hud = True
                    val = value_from_pos(hud_slider, event.pos[0], 200)
                    constants.settings["hud_scale"] = val

                if left_arr.collidepoint(event.pos):
                    res_index = (res_index - 1) % len(constants.AVAILABLE_RESOLUTIONS)
                    constants.settings["display_w"], constants.settings["display_h"] = constants.AVAILABLE_RESOLUTIONS[res_index]
                    apply_display()
                if right_arr.collidepoint(event.pos):
                    res_index = (res_index + 1) % len(constants.AVAILABLE_RESOLUTIONS)
                    constants.settings["display_w"], constants.settings["display_h"] = constants.AVAILABLE_RESOLUTIONS[res_index]
                    apply_display()

                if mode_left.collidepoint(event.pos):
                    mode_index = (mode_index - 1) % len(constants.DISPLAY_MODES)
                    constants.settings["display_mode"] = constants.DISPLAY_MODES[mode_index]
                    apply_display()
                if mode_right.collidepoint(event.pos):
                    mode_index = (mode_index + 1) % len(constants.DISPLAY_MODES)
                    constants.settings["display_mode"] = constants.DISPLAY_MODES[mode_index]
                    apply_display()

                if fps_left.collidepoint(event.pos):
                    fps_index = (fps_index - 1) % len(constants.FPS_OPTIONS)
                    constants.settings["fps"] = constants.FPS_OPTIONS[fps_index]
                if fps_right.collidepoint(event.pos):
                    fps_index = (fps_index + 1) % len(constants.FPS_OPTIONS)
                    constants.settings["fps"] = constants.FPS_OPTIONS[fps_index]
                if button_back.collidepoint(event.pos):
                    running = False

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_volume = False
                dragging_hud = False

            if event.type == pygame.MOUSEMOTION:
                if dragging_volume:
                    vol_slider = get_slider_rect(180)
                    val = value_from_pos(vol_slider, event.pos[0])
                    constants.settings["master_volume"] = val
                    if jukebox:
                        jukebox.set_volume(val / 100.0)
                if dragging_hud:
                    hud_slider = get_slider_rect(270)
                    val = value_from_pos(hud_slider, event.pos[0], 200)
                    constants.settings["hud_scale"] = val

        pygame.display.flip()
        clock.tick(60)

    return screen


def shop_(screen, clock, name):
    global jukebox
    running = True
    font_title = pygame.font.Font(None, 80)
    font_item = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 26)
    music = Music(resource_path("escalator music.mp3"), True)

    # Track owned keys for display
    def is_owned(key):
        if key == "Spears":
            return "spear" in constants.player_owned_weapons
        return key in constants.player_owned_weapons

    def buy_item(item):
        if is_owned(item["key"]):
            return False
        if constants.player_coins < item["cost"]:
            return False
        constants.player_coins -= item["cost"]

        key = item["key"]
        if key == "Spears":
            constants.player_owned_weapons.append("spear")
        else:
            constants.player_owned_weapons.append(key)

        if key == "flask":
            constants.player_flasks += 1
        elif key == "balloon_ammo":
            constants.player_balloon_ammo_bonus += 3
        elif key == "max_hp":
            from constants import PLAYER_MAX_HP
            constants.PLAYER_MAX_HP += 25
        elif key == "speed":
            from constants import physics
            physics.PLAYER_SPEED += 1
        elif key == "Spears":
            pass
        return True

    feedback_text = ""
    feedback_timer = 0

    while running:
        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))
        pygame.draw.rect(screen, (10, 45, 75), (0, 500, WIDTH, 200))

        title = font_title.render(name, True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 70)))

        coins_text = font_item.render(f"¢ {constants.player_coins}", True, (255, 215, 0))
        screen.blit(coins_text, (40, 30))

        item_rects = []
        for i, item in enumerate(shop.SHOP_ITEMS):
            y = 150 + i * 70
            rect = pygame.Rect(100, y, WIDTH - 200, 55)
            item_rects.append(rect)

            owned = is_owned(item["key"])
            base_color = (40, 90, 130)
            border_color = (80, 140, 180)
            if owned:
                base_color = (20, 60, 80)
                border_color = (60, 100, 120)

            mouse_over = rect.collidepoint(pygame.mouse.get_pos())
            if mouse_over and not owned and not feedback_timer:
                border_color = (255, 220, 100)

            pygame.draw.rect(screen, base_color, rect, border_radius=10)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)

            if owned:
                text = font_item.render(f"✓ {item['name']} — OWNED", True, (120, 200, 160))
            else:
                text = font_item.render(
                    f"{item['name']} — {item['cost']}g",
                    True, (200, 220, 240) if constants.player_coins < item["cost"] else WHITE
                )
            desc = font_small.render(item["desc"], True, (160, 190, 210))

            screen.blit(text, (120, y + 5))
            screen.blit(desc, (120, y + 28))

        exit_text = font_item.render("ESC - Leave Shop", True, WHITE)
        screen.blit(exit_text, (20, HEIGHT - 50))

        if feedback_timer > 0:
            fb = font_item.render(feedback_text, True, (255, 215, 0))
            screen.blit(fb, (WIDTH // 2 - fb.get_width() // 2, HEIGHT - 100))
            feedback_timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    music.unload()
                    jukebox.resume()
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(item_rects):
                    if rect.collidepoint(event.pos):
                        item = shop.SHOP_ITEMS[i]
                        if is_owned(item["key"]):
                            feedback_text = "Already owned!"
                            feedback_timer = 45
                        elif buy_item(item):
                            feedback_text = f"Purchased {item['name']}!"
                            feedback_timer = 45
                        else:
                            feedback_text = "Not enough coins!"
                            feedback_timer = 45

        pygame.display.flip()
        clock.tick(60)