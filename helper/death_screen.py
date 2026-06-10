import pygame

from constants import *


# Accepts a restart_func callback so crushed players respawn in the
def show_death_screen(screen, clock, restart_func):
    """Displays Game Over when crushed. Calls restart_func() on respawn."""
    running = True
    title_font = pygame.font.Font(None, 100)
    sub_font = pygame.font.Font(None, 44)
    button_font = pygame.font.Font(None, 50)

    button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 70)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        hovered = button_rect.collidepoint(mouse_pos)

        screen.fill((20, 5, 5))
        pygame.draw.rect(screen, (80, 10, 10), (0, 0, WIDTH, HEIGHT), 15)

        title_text = title_font.render("GAME OVER", True, (255, 50, 50))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)

        sub_text = sub_font.render(
            "You were crushed by the elevator machinery!", True, (220, 180, 180)
        )
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 70))
        screen.blit(sub_text, sub_rect)

        pygame.draw.rect(
            screen,
            (140, 30, 30) if hovered else (90, 20, 20),
            button_rect,
            border_radius=12,
        )
        pygame.draw.rect(screen, (255, 100, 100), button_rect, 2, border_radius=12)

        btn_text = button_font.render("Respawn (R)", True, WHITE)
        btn_rect = btn_text.get_rect(center=button_rect.center)
        screen.blit(btn_text, btn_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False
                if event.key == pygame.K_r:
                    restart_func()
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    restart_func()
                    return True

        pygame.display.flip()
        clock.tick(60)


def show_death_screen_ENEMIES(screen, clock, restart_func, text):
    running = True
    title_font = pygame.font.Font(None, 100)
    sub_font = pygame.font.Font(None, 44)
    button_font = pygame.font.Font(None, 50)

    button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 70)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        hovered = button_rect.collidepoint(mouse_pos)

        screen.fill((20, 5, 5))
        pygame.draw.rect(screen, (80, 10, 10), (0, 0, WIDTH, HEIGHT), 15)

        title_text = title_font.render("GAME OVER", True, (255, 50, 50))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)

        sub_text = sub_font.render(text, True, (220, 180, 180))
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 70))
        screen.blit(sub_text, sub_rect)

        pygame.draw.rect(
            screen,
            (140, 30, 30) if hovered else (90, 20, 20),
            button_rect,
            border_radius=12,
        )
        pygame.draw.rect(screen, (255, 100, 100), button_rect, 2, border_radius=12)

        btn_text = button_font.render("Respawn (R)", True, WHITE)
        btn_rect = btn_text.get_rect(center=button_rect.center)
        screen.blit(btn_text, btn_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False
                if event.key == pygame.K_r:
                    restart_func()
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    restart_func()
                    return True

        pygame.display.flip()
        clock.tick(60)
