import pygame
import constants
from helper.graphics import draw_vertical_gradient

PAGES = [
    {
        "title": "Movement",
        "lines": [
            "A / LEFT ARROW  — Move left",
            "D / RIGHT ARROW — Move right",
            "SPACE / W / UP  — Jump (hold for height)",
            "Double jump also available!",
        ],
    },
    {
        "title": "Weapons & Combat",
        "lines": [
            "1 / 2 / 3  — Switch weapon slot",
            "LEFT CLICK  — Fire selected weapon",
            "Spear (slot 1): melee attack",
            "Water Gun (slot 2): ranged, uses ammo",
            "Water Balloon (slot 3): ranged, uses ammo",
        ],
    },
    {
        "title": "Paperclips & Doors",
        "lines": [
            "F  — Use paperclip on a breakable door",
            "Paperclips are found as glowing dots",
            "Each door takes 3 hits to break open",
        ],
    },
    {
        "title": "Elevators & Interaction",
        "lines": [
            "Stand on an elevator platform",
            "E  — Move elevator up",
            "Q  — Move elevator down",
            "F  — Open animated doors / collect lore",
            "H  — Use health flask (heals 40 HP)",
        ],
    },
    {
        "title": "Shop & Items",
        "lines": [
            "Walk over a shopkeeper (S tile) to open the shop",
            "Spend coins on flasks, ammo, HP, and speed",
            "Golden coins ($) are scattered around each level",
        ],
    },
]

def show_tutorial(screen, clock):
    if not constants.settings.get("show_tutorial", True):
        return
    page = 0
    running = True
    title_font = pygame.font.Font(None, 72)
    line_font = pygame.font.Font(None, 32)
    hint_font = pygame.font.Font(None, 26)

    while running and page < len(PAGES):
        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))

        p = PAGES[page]
        title = title_font.render(p["title"], True, constants.WHITE)
        screen.blit(title, (constants.WIDTH // 2 - title.get_width() // 2, 80))

        for i, line in enumerate(p["lines"]):
            surf = line_font.render(line, True, (180, 220, 240))
            screen.blit(surf, (constants.WIDTH // 2 - surf.get_width() // 2, 200 + i * 50))

        hint = hint_font.render(f"Page {page + 1} of {len(PAGES)}  —  SPACE/ENTER to continue, ESC to skip", True, (100, 160, 180))
        screen.blit(hint, (constants.WIDTH // 2 - hint.get_width() // 2, constants.HEIGHT - 100))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    page += 1
                if event.key == pygame.K_ESCAPE:
                    running = False
