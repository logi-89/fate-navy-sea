import pygame
import constants
from constants import *
from helper.graphics import *
from helper.music import Music
import levels.level1
import levels.level2

jukebox = None

def show_title_screen(screen, clock, jukebox_object):
    global jukebox

    jukebox = jukebox_object
    running = True
    t = 0

    title_font = pygame.font.Font(None, 110)
    sub_font = pygame.font.Font(None, 44)
    button_font = pygame.font.Font(None, 56)

    start_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 80, 240, 70)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        hovered = start_button.collidepoint(mouse_pos)

        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))
        pygame.draw.circle(screen, (160, 220, 255), (WIDTH // 2, 180), 90)
        pygame.draw.circle(screen, (200, 245, 255), (WIDTH // 2, 180), 55)
        pygame.draw.rect(screen, (10, 45, 75), (0, 430, WIDTH, 270))
        draw_waves(screen, t)

        title_text = title_font.render("Fate: Navy Sea", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)

        sub_text = sub_font.render("Set sail into the storm", True, (220, 245, 255))
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 65))
        screen.blit(sub_text, sub_rect)

        pygame.draw.rect(screen, title_screen.HOVER_COLOR if hovered else title_screen.BUTTON_COLOR, start_button, border_radius=18)
        pygame.draw.rect(screen, WHITE, start_button, 3, border_radius=18)

        start_text = button_font.render("Start", True,WHITE)
        start_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    levels.level1.intro(screen, clock)
                    return True

        pygame.display.flip()
        clock.tick(60)
        t += 0.03


def shop_(screen, clock, name):
    global jukebox
    running = True
    font_title = pygame.font.Font(None, 80)
    font_item = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 26)
    music = Music("escalator music.mp3", True)

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