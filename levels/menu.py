import pygame
import constants
from constants import *
from helper.graphics import *
from helper.music import Music
import levels.level1
import levels.level2

def show_title_screen(screen, clock):
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
                if event.key == pygame.K_ESCAPE:  # ESC from Title Screen exits game
                    pygame.quit()
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    levels.level1.intro(screen, clock)
                    return True

        pygame.display.flip()
        clock.tick(60)
        t += 0.03


#The Tidal Trader? (Triple T)


def shop_(screen, clock, name):
    running = True
    font_title = pygame.font.Font(None, 80)
    font_item = pygame.font.Font(None, 36)
    music = Music("escalator music.mp3", True)

    while running:
        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))

        pygame.draw.rect(screen, (10, 45, 75), (0, 500, WIDTH, 200))

        title = font_title.render(name, True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 70)))

        coins_text = font_item.render(f"¢ {constants.player_coins}", True, (255, 215, 0))
        screen.blit(coins_text, (40, 30))

        # Shop items
        for i, item in enumerate(shop.SHOP_ITEMS):
            y = 150 + i * 70

            item_rect = pygame.Rect(100, y, WIDTH - 200, 55)

            pygame.draw.rect(screen, (20, 70, 110), item_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, item_rect, 2, border_radius=10)

            text = font_item.render(
                f"{item['name']} - {item['cost']}g",
                True,
                WHITE
            )

            desc = pygame.font.Font(None, 26).render(
                item["desc"],
                True,
                (200, 220, 240)
            )

            screen.blit(text, (120, y + 5))
            screen.blit(desc, (120, y + 28))

        exit_text = font_item.render("ESC - Leave Shop", True, WHITE)
        screen.blit(exit_text, (20, HEIGHT - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    music.stop()
                    return

        pygame.display.flip()
        clock.tick(60)