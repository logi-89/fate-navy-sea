import pygame
import math
import random
import constants
from constants import *
from helper.graphics import *
from helper.music import Music
from helper import scoreboard
import maps
import levels.level1
import levels.level2
import levels.level3
import levels.level4
import levels.level5

jukebox = None

# ── Storm / ocean helpers ──────────────────────────────────────────────────

def _ocean_waves(surface, t, ocean_top):
    w, h = surface.get_size()
    # deep ocean body
    pygame.draw.rect(surface, (4, 14, 32), (0, ocean_top, w, h - ocean_top))

    for layer, (color, amp, freq, speed, y_off) in enumerate([
        ((14, 60, 90),   3, 0.028, 0.30, 0),
        ((22, 90, 130),  5, 0.022, 0.50, 6),
        ((36, 120, 165), 4, 0.018, 0.70, 14),
    ]):
        base_y = ocean_top + y_off
        pts = [(x, base_y + math.sin(x * freq + t * speed + layer) * amp)
               for x in range(0, w + 10, 10)]
        pygame.draw.lines(surface, color, False, pts, 2) if len(pts) > 1 else None

    # white foam crests
    for x in range(0, w, 12):
        cy = ocean_top + math.sin(x * 0.028 + t * 0.5) * 3
        if math.sin(x * 0.12 + t * 2) > 0.65:
            pygame.draw.circle(surface, (180, 225, 250), (x, int(cy)), 2)


def _ship(surface, x, y, t, scale=1.0):
    mast_top = y - 72 * scale
    pygame.draw.line(surface, (20, 24, 35), (x, y), (x, mast_top), max(2, int(3 * scale)))

    hull = [(x - 55*scale, y), (x + 55*scale, y),
            (x + 70*scale, y + 16*scale + 2*math.sin(t*2)),
            (x - 70*scale, y + 16*scale + 2*math.sin(t*2 + 1))]
    pygame.draw.polygon(surface, (20, 24, 35), hull)

    l_sail = [(x, mast_top + 4*scale), (x - 32*scale, y - 22*scale), (x - 4*scale, y - 22*scale)]
    r_sail = [(x, mast_top + 4*scale), (x + 26*scale, y - 16*scale), (x + 4*scale, y - 16*scale)]
    pygame.draw.polygon(surface, (38, 44, 55), l_sail)
    pygame.draw.polygon(surface, (46, 52, 64), r_sail)

    flag = [(x, mast_top), (x + 22*scale, mast_top + 9*scale), (x, mast_top + 18*scale)]
    pygame.draw.polygon(surface, (70, 35, 35), flag)


_raindrops = []


def _init_rain(width, height, count=120):
    global _raindrops
    _raindrops = [[random.randint(0, width), random.randint(-height, 0),
                   random.uniform(4, 8), random.uniform(0.5, 1.5)]
                  for _ in range(count)]


def _update_rain(width, height):
    global _raindrops
    for d in _raindrops:
        d[0] -= d[3] * 1.8
        d[1] += d[3] * 9
        if d[1] > height:
            d[0] = random.randint(0, width)
            d[1] = random.randint(-20, -5)


def _draw_rain(surface):
    global _raindrops
    ws = surface.get_size()
    if not _raindrops or len(_raindrops) == 0:
        _init_rain(ws[0], ws[1])
    overlay = pygame.Surface(ws, pygame.SRCALPHA)
    for x, y, ln, spd in _raindrops:
        a = min(180, int(60 + spd * 40))
        pygame.draw.line(overlay, (160, 210, 240, a),
                         (x, y), (x - 3, y + ln), 1)
    surface.blit(overlay, (0, 0))


# ── Themed drawing helpers ─────────────────────────────────────────────────

def _draw_glowing_text(surface, text, font, color, center, glow_color=(70, 200, 240), radius=4):
    for r in range(radius, 0, -1):
        a = max(20, 80 - r * 15)
        g = font.render(text, True, glow_color)
        g.set_alpha(a)
        for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, -r)):
            surface.blit(g, g.get_rect(center=(center[0] + dx, center[1] + dy)))
    m = font.render(text, True, color)
    surface.blit(m, m.get_rect(center=center))


def _themed_button(surface, rect, text, font, hovered, accent=LIGHT_TEAL):
    bg = (60, 110, 170) if hovered else (35, 70, 105)
    pygame.draw.rect(surface, bg, rect, border_radius=14)
    pygame.draw.rect(surface, accent, rect, 2, border_radius=14)
    if hovered:
        glow = pygame.Surface((rect.w + 8, rect.h + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*accent[:3], 40), (4, 4, rect.w, rect.h), border_radius=16)
        surface.blit(glow, (rect.x - 4, rect.y - 4))
    t = font.render(text, True, WHITE)
    surface.blit(t, t.get_rect(center=rect.center))


def _storm_overlay(surface, t):
    w, h = surface.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(max(0, 55 * math.sin(y / h * math.pi * 0.6 + t * 0.05)))
        if a > 0:
            pygame.draw.line(grad, (100, 180, 230, a), (0, y), (w, y))
    surface.blit(grad, (0, 0))


# ── Title screen ────────────────────────────────────────────────────────────

def show_title_screen(screen, clock, jukebox_object):
    global jukebox
    jukebox = jukebox_object

    running = True
    t = 0.0
    lightning_timer = 0
    lightning_alpha = 0
    WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
    _init_rain(WIDTH, HEIGHT)

    title_font = pygame.font.Font(None, 112)
    sub_font = pygame.font.Font(None, 42)
    button_font = pygame.font.Font(None, 54)

    btn_w, btn_h, gap = 260, 58, 16
    cx = WIDTH // 2
    start_y = HEIGHT // 2 + 30
    start_btn   = pygame.Rect(cx - btn_w // 2, start_y,               btn_w, btn_h)
    chapt_btn   = pygame.Rect(cx - btn_w // 2, start_y + btn_h + gap,  btn_w, btn_h)
    sets_btn    = pygame.Rect(cx - btn_w // 2, start_y + (btn_h + gap) * 2, btn_w, btn_h)
    scores_btn  = pygame.Rect(cx - btn_w // 2, start_y + (btn_h + gap) * 3, btn_w, btn_h)

    while running:
        WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
        mouse_pos = pygame.mouse.get_pos()

        # ── background ──
        draw_vertical_gradient(screen, (3, 8, 22), (8, 30, 72))

        # lightning
        if lightning_timer > 0:
            lightning_timer -= 1
            lightning_alpha = random.randint(100, 200)
        else:
            lightning_alpha = max(0, lightning_alpha - 6)
            if lightning_alpha <= 0 and random.random() < 0.002:
                lightning_timer = random.randint(3, 8)

        # ocean
        ocean_top = HEIGHT - 220
        _ocean_waves(screen, t, ocean_top)

        # ship
        ship_x = int(WIDTH * 0.25 + math.sin(t * 0.15) * 20)
        ship_y = ocean_top + 10 + math.sin(t * 0.8) * 2
        _ship(screen, ship_x, ship_y, t, scale=1.6)
        # second smaller ship in the distance
        _ship(screen, int(WIDTH * 0.78) + int(math.sin(t * 0.1 + 2) * 15),
              ocean_top - 20 + math.sin(t * 0.6 + 1) * 1.5, t, scale=0.75)

        # rain
        _update_rain(WIDTH, HEIGHT)
        _draw_rain(screen)

        # storm overlay (subtle dark gradient)
        _storm_overlay(screen, t)

        # lightning flash
        if lightning_alpha > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((180, 210, 255, lightning_alpha))
            screen.blit(flash, (0, 0))

        # ── title ──
        title_center = (WIDTH // 2, HEIGHT // 3 - 10)
        _draw_glowing_text(screen, "FATE: NAVY SEA", title_font, WHITE, title_center,
                           glow_color=(70, 180, 240), radius=5)

        sub_text = sub_font.render("Set sail into the storm", True, (180, 220, 240))
        screen.blit(sub_text, sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 58)))

        # ── buttons ──
        h_start = start_btn.collidepoint(mouse_pos)
        h_chapt = chapt_btn.collidepoint(mouse_pos)
        h_sets  = sets_btn.collidepoint(mouse_pos)
        h_score = scores_btn.collidepoint(mouse_pos)

        _themed_button(screen, start_btn,  "Start",       button_font, h_start)
        _themed_button(screen, chapt_btn,  "Chapters",    button_font, h_chapt)
        _themed_button(screen, sets_btn,   "Settings",    button_font, h_sets)
        _themed_button(screen, scores_btn, "High Scores", button_font, h_score)

        # ── events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return screen
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    levels.level1.intro(screen, clock, jukebox)
                    return screen
                if chapt_btn.collidepoint(event.pos):
                    screen = chapter_select(screen, clock)
                    if not pygame.get_init():
                        return screen
                if sets_btn.collidepoint(event.pos):
                    screen = settings_menu(screen, clock)
                    if not pygame.get_init():
                        return screen
                if scores_btn.collidepoint(event.pos):
                    screen = scoreboard.show_high_scores(screen, clock)
                    if not pygame.get_init():
                        return screen

        pygame.display.flip()
        clock.tick(60)
        t += 0.03

    return screen


def chapter_select(screen, clock):
    global jukebox
    running = True
    WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
    font_title = pygame.font.Font(None, 76)
    font_chapter = pygame.font.Font(None, 40)
    font_desc = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    chapters = [
        ("Chapter 1", "The Depths", levels.level1.intro, "Descend into the abyss"),
        ("Chapter 2", "The Train", levels.level2.intro, "Board the phantom express"),
        ("Chapter 3", "The Laboratory", levels.level3.intro, "Secrets beneath the waves"),
        ("Chapter 4", "The Lab", levels.level4.intro, "Face the heart of the storm"),
        ("Chapter 5", "The Tower", levels.level5.intro, "Ascend beyond the waves"),
    ]
    t = 0.0

    while running:
        WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
        mouse_pos = pygame.mouse.get_pos()
        draw_vertical_gradient(screen, (3, 8, 22), (8, 30, 72))

        # subtle wave line at the top
        for x in range(0, WIDTH + 10, 10):
            y = 90 + math.sin(x * 0.03 + t * 0.5) * 3
            pygame.draw.circle(screen, (30, 120, 160), (x, int(y)), 1)

        _draw_glowing_text(screen, "SELECT CHAPTER", font_title, WHITE,
                           (WIDTH // 2, 50), glow_color=(50, 150, 200), radius=3)

        for i, (name, desc, func, tagline) in enumerate(chapters):
            y = 140 + i * 110
            rect = pygame.Rect(WIDTH // 2 - 220, y, 440, 85)
            hovered = rect.collidepoint(mouse_pos)

            bg = (50, 95, 145) if hovered else (28, 55, 85)
            border_c = LIGHT_TEAL if hovered else TEAL
            pygame.draw.rect(screen, bg, rect, border_radius=12)
            pygame.draw.rect(screen, border_c, rect, 2, border_radius=12)

            if hovered:
                glow = pygame.Surface((rect.w + 8, rect.h + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*LIGHT_TEAL[:3], 35), (4, 4, rect.w, rect.h), border_radius=14)
                screen.blit(glow, (rect.x - 4, rect.y - 4))

            # chapter number badge
            badge = pygame.Rect(rect.x + 10, rect.y + 12, 40, 40)
            pygame.draw.rect(screen, SEA_LIGHT, badge, border_radius=8)
            num_surf = font_chapter.render(str(i + 1), True, WHITE)
            screen.blit(num_surf, num_surf.get_rect(center=badge.center))

            n = font_chapter.render(name, True, WHITE)
            screen.blit(n, (rect.x + 62, rect.y + 10))
            d = font_desc.render(desc, True, (160, 210, 235))
            screen.blit(d, (rect.x + 62, rect.y + 44))
            tg = font_small.render(tagline, True, (100, 160, 190))
            screen.blit(tg, (rect.x + 62, rect.y + 64))

        back_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 65, 140, 44)
        back_hovered = back_rect.collidepoint(mouse_pos)
        _themed_button(screen, back_rect, "BACK", font_desc, back_hovered, accent=TEAL)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return screen
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, (name, desc, func, tagline) in enumerate(chapters):
                    y = 140 + i * 110
                    rect = pygame.Rect(WIDTH // 2 - 220, y, 440, 85)
                    if rect.collidepoint(event.pos):
                        func(screen, clock, jukebox)
                        return screen
                if back_rect.collidepoint(event.pos):
                    return screen

        pygame.display.flip()
        clock.tick(60)
        t += 0.03


def settings_menu(screen, clock):
    global jukebox
    running = True
    font_title = pygame.font.Font(None, 76)
    font_item = pygame.font.Font(None, 36)
    font_value = pygame.font.Font(None, 26)

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

    tutorial_on = constants.settings.get("show_tutorial", True)

    dragging_volume = False
    dragging_hud = False

    button_back = pygame.Rect(constants.WIDTH // 2 - 90, constants.HEIGHT - 90, 180, 48)

    def get_slider_rect(center_y):
        return pygame.Rect(constants.WIDTH // 2 - 90, center_y - 5, 300, 10)

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

    t = 0.0
    while running:
        WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
        mouse_pos = pygame.mouse.get_pos()

        draw_vertical_gradient(screen, (3, 8, 22), (8, 30, 72))

        # subtle wave line at the top
        for x in range(0, WIDTH + 10, 10):
            y = 90 + math.sin(x * 0.03 + t * 0.5) * 3
            pygame.draw.circle(screen, (30, 120, 160), (x, int(y)), 1)

        _draw_glowing_text(screen, "SETTINGS", font_title, WHITE,
                           (WIDTH // 2, 50), glow_color=(50, 150, 200), radius=3)

        # ── sliders ──
        labels = [
            ("Master Volume", 170, constants.settings["master_volume"], 100),
            ("HUD Scale",     250, constants.settings["hud_scale"],     200),
        ]

        for label, cy, val, max_val in labels:
            lbl = font_item.render(label, True, (180, 220, 240))
            screen.blit(lbl, (WIDTH // 2 - 310, cy - 12))

            val_text = font_value.render(f"{round(val/100,1)}", True, LIGHT_TEAL)
            screen.blit(val_text, (WIDTH // 2 + 220, cy - 8))

            slider = get_slider_rect(cy)
            pygame.draw.rect(screen, (15, 40, 60), slider, border_radius=5)
            ratio = val / max_val
            fill_w = int(slider.w * ratio)
            if fill_w > 0:
                fill = pygame.Rect(slider.x, slider.y, fill_w, slider.h)
                pygame.draw.rect(screen, TEAL, fill, border_radius=5)
            handle_x = slider.x + int(slider.w * ratio)
            pygame.draw.circle(screen, LIGHT_TEAL, (handle_x, slider.centery), 8)
            pygame.draw.circle(screen, TEAL, (handle_x, slider.centery), 8, 2)

        # ── cycling selectors (resolution, display mode, fps) ──
        cx = WIDTH // 2
        selectors = [
            ("Resolution",   330, constants.AVAILABLE_RESOLUTIONS, res_index,
             f"{constants.AVAILABLE_RESOLUTIONS[res_index][0]} x {constants.AVAILABLE_RESOLUTIONS[res_index][1]}"),
            ("Display Mode",  410, constants.DISPLAY_MODES, mode_index,
             constants.DISPLAY_MODES[mode_index].capitalize()),
            ("FPS",           490, constants.FPS_OPTIONS, fps_index,
             f"{constants.FPS_OPTIONS[fps_index]}" if constants.FPS_OPTIONS[fps_index] > 0 else "Uncapped"),
        ]

        # Tutorial toggle
        tut_label = font_item.render("Show Tutorial", True, (180, 220, 240))
        screen.blit(tut_label, (cx - 310, 565))
        tut_rect = pygame.Rect(cx - 85, 562, 170, 36)
        tut_color = TEAL if tutorial_on else (60, 80, 100)
        pygame.draw.rect(screen, (22, 55, 85), tut_rect, border_radius=8)
        pygame.draw.rect(screen, tut_color, tut_rect, 2, border_radius=8)
        tut_text = font_item.render("On" if tutorial_on else "Off", True, WHITE)
        screen.blit(tut_text, tut_text.get_rect(center=tut_rect.center))

        for s_label, s_cy, s_options, s_index, s_text in selectors:
            lbl = font_item.render(s_label, True, (180, 220, 240))
            screen.blit(lbl, (cx - 310, s_cy - 12))

            rect = pygame.Rect(cx - 85, s_cy - 18, 170, 36)
            pygame.draw.rect(screen, (22, 55, 85), rect, border_radius=8)
            pygame.draw.rect(screen, TEAL, rect, 2, border_radius=8)
            txt = font_item.render(s_text, True, WHITE)
            screen.blit(txt, txt.get_rect(center=rect.center))

            left  = pygame.Rect(cx - 112, s_cy - 12, 20, 20)
            right = pygame.Rect(cx + 92,  s_cy - 12, 20, 20)
            pygame.draw.polygon(screen, LIGHT_TEAL,
                [(left.x, left.centery), (left.right, left.y), (left.right, left.bottom)])
            pygame.draw.polygon(screen, LIGHT_TEAL,
                [(right.right, right.centery), (right.x, right.y), (right.x, right.bottom)])

        # ── back ──
        hovered_back = button_back.collidepoint(mouse_pos)
        _themed_button(screen, button_back, "BACK", font_item, hovered_back, accent=TEAL)

        # ── events (unchanged logic) ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                vol_slider = get_slider_rect(170)
                if vol_slider.collidepoint(event.pos):
                    dragging_volume = True
                    val = value_from_pos(vol_slider, event.pos[0])
                    constants.settings["master_volume"] = val
                    if jukebox:
                        jukebox.set_volume(val / 100.0)

                hud_slider = get_slider_rect(250)
                if hud_slider.collidepoint(event.pos):
                    dragging_hud = True
                    val = value_from_pos(hud_slider, event.pos[0], 200)
                    constants.settings["hud_scale"] = val

                # resolution arrows
                left  = pygame.Rect(cx - 112, 330 - 12, 20, 20)
                right = pygame.Rect(cx + 92,  330 - 12, 20, 20)
                if left.collidepoint(event.pos):
                    res_index = (res_index - 1) % len(constants.AVAILABLE_RESOLUTIONS)
                    constants.settings["display_w"], constants.settings["display_h"] = constants.AVAILABLE_RESOLUTIONS[res_index]
                    apply_display()
                if right.collidepoint(event.pos):
                    res_index = (res_index + 1) % len(constants.AVAILABLE_RESOLUTIONS)
                    constants.settings["display_w"], constants.settings["display_h"] = constants.AVAILABLE_RESOLUTIONS[res_index]
                    apply_display()

                # display mode arrows
                left  = pygame.Rect(cx - 112, 410 - 12, 20, 20)
                right = pygame.Rect(cx + 92,  410 - 12, 20, 20)
                if left.collidepoint(event.pos):
                    mode_index = (mode_index - 1) % len(constants.DISPLAY_MODES)
                    constants.settings["display_mode"] = constants.DISPLAY_MODES[mode_index]
                    apply_display()
                if right.collidepoint(event.pos):
                    mode_index = (mode_index + 1) % len(constants.DISPLAY_MODES)
                    constants.settings["display_mode"] = constants.DISPLAY_MODES[mode_index]
                    apply_display()

                # fps arrows
                left  = pygame.Rect(cx - 112, 490 - 12, 20, 20)
                right = pygame.Rect(cx + 92,  490 - 12, 20, 20)
                if left.collidepoint(event.pos):
                    fps_index = (fps_index - 1) % len(constants.FPS_OPTIONS)
                    constants.settings["fps"] = constants.FPS_OPTIONS[fps_index]
                if right.collidepoint(event.pos):
                    fps_index = (fps_index + 1) % len(constants.FPS_OPTIONS)
                    constants.settings["fps"] = constants.FPS_OPTIONS[fps_index]

                # tutorial toggle
                tut_rect = pygame.Rect(cx - 85, 562, 170, 36)
                if tut_rect.collidepoint(event.pos):
                    tutorial_on = not tutorial_on
                    constants.settings["show_tutorial"] = tutorial_on

                if button_back.collidepoint(event.pos):
                    running = False

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_volume = False
                dragging_hud = False

            if event.type == pygame.MOUSEMOTION:
                if dragging_volume:
                    vol_slider = get_slider_rect(170)
                    val = value_from_pos(vol_slider, event.pos[0])
                    constants.settings["master_volume"] = val
                    if jukebox:
                        jukebox.set_volume(val / 100.0)
                if dragging_hud:
                    hud_slider = get_slider_rect(250)
                    val = value_from_pos(hud_slider, event.pos[0], 200)
                    constants.settings["hud_scale"] = val

        pygame.display.flip()
        clock.tick(60)
        t += 0.03

    return screen


def shop_(screen, clock, name):
    global jukebox
    running = True
    font_title = pygame.font.Font(None, 80)
    font_item = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 26)
    music = Music("escalator music.mp3", True)

    # Track owned keys for display
    def is_owned(key):
        if key in ("flask", "balloon_ammo"):
            return False
        if key == "Spears":
            return "spear" in constants.player_owned_weapons
        return key in constants.player_owned_weapons

    def buy_item(item):
        if constants.player_coins < item["cost"]:
            return False
        constants.player_coins -= item["cost"]

        key = item["key"]
        if key in ("flask", "balloon_ammo"):
            pass
        elif key == "Spears":
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

        coins_text = font_item.render(
            f"¢ {constants.player_coins}", True, (255, 215, 0)
        )
        screen.blit(coins_text, (40, 30))

        item_rects = []
        for i, item in enumerate(shop.SHOP_ITEMS):
            y = 150 + i * 70
            rect = pygame.Rect(100, y, WIDTH - 200, 55)
            item_rects.append(rect)

            owned = is_owned(item["key"])
            stackable = item["key"] in ("flask", "balloon_ammo")
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
                text = font_item.render(
                    f"✓ {item['name']} — OWNED", True, (120, 200, 160)
                )
            elif stackable:
                count = (
                    constants.player_flasks
                    if item["key"] == "flask"
                    else constants.player_balloon_ammo_bonus
                )
                text = font_item.render(
                    f"{item['name']} ({'owned: ' + str(count)}) — {item['cost']}g",
                    True,
                    (200, 220, 240) if constants.player_coins < item["cost"] else WHITE,
                )
            else:
                text = font_item.render(
                    f"{item['name']} — {item['cost']}g",
                    True,
                    (200, 220, 240) if constants.player_coins < item["cost"] else WHITE,
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
