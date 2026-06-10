import csv
import os
import pygame
from datetime import datetime
import constants
from helper.graphics import draw_vertical_gradient

SCORE_FILE = "data/scores.csv"
FIELDS = ["name", "score", "time", "date", "time_str"]


def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    try:
        with open(SCORE_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            scores = []
            for row in reader:
                row["score"] = int(row["score"])
                row["time"] = float(row["time"])
                scores.append(row)
            return scores
    except (csv.Error, IOError, KeyError, ValueError):
        return []


def save_scores(scores):
    os.makedirs(os.path.dirname(SCORE_FILE), exist_ok=True)
    with open(SCORE_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(scores)


def add_score(name, score, time_secs):
    scores = load_scores()
    now = datetime.now()
    scores.append(
        {
            "name": name,
            "score": score,
            "time": time_secs,
            "date": now.strftime("%Y-%m-%d"),
            "time_str": now.strftime("%I:%M %p"),
        }
    )
    scores.sort(key=lambda s: (-s["score"], s["time"]))
    scores = scores[:100]
    save_scores(scores)
    return scores


def format_time(secs):
    secs = int(secs)
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def name_entry(screen, clock):
    running = True
    name = ""
    font = pygame.font.Font(None, 50)
    sub = pygame.font.Font(None, 30)
    prompt = "Enter your name and press ENTER to save score"

    while running:
        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))
        p = sub.render(prompt, True, (120, 180, 200))
        screen.blit(
            p, (constants.WIDTH // 2 - p.get_width() // 2, constants.HEIGHT // 2 - 80)
        )
        n = font.render(name + "|", True, constants.WHITE)
        screen.blit(
            n, (constants.WIDTH // 2 - n.get_width() // 2, constants.HEIGHT // 2 - 20)
        )

        inst = sub.render("ESC to skip - Backspace to delete", True, (80, 130, 150))
        screen.blit(
            inst,
            (constants.WIDTH // 2 - inst.get_width() // 2, constants.HEIGHT // 2 + 40),
        )

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                if event.key == pygame.K_ESCAPE:
                    return "Anonymous"
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_SPACE:
                    name += " "
                elif event.key <= 127 and len(name) < 20:
                    c = event.unicode
                    if c.isprintable():
                        name += c


def save_and_quit(screen, clock):
    name = name_entry(screen, clock)
    if name is None:
        return
    add_score(name, constants.total_score, constants.total_play_time / 1000)


def show_high_scores(screen, clock):
    running = True
    scores = load_scores()
    font_title = pygame.font.Font(None, 70)
    font_header = pygame.font.Font(None, 32)
    font_row = pygame.font.Font(None, 26)
    font_empty = pygame.font.Font(None, 36)

    while running:
        draw_vertical_gradient(screen, (8, 24, 48), (20, 110, 160))

        title = font_title.render("HIGH SCORES", True, constants.WHITE)
        screen.blit(title, (constants.WIDTH // 2 - title.get_width() // 2, 40))

        if not scores:
            empty = font_empty.render("No scores yet", True, (120, 160, 180))
            screen.blit(
                empty,
                (
                    constants.WIDTH // 2 - empty.get_width() // 2,
                    constants.HEIGHT // 2 - 20,
                ),
            )
        else:
            headers = ["#", "NAME", "SCORE", "TIME", "DATE"]
            col_x = [
                60,
                110,
                constants.WIDTH // 2 + 40,
                constants.WIDTH // 2 + 180,
                constants.WIDTH // 2 + 280,
            ]
            for j, h in enumerate(headers):
                hd = font_header.render(h, True, (100, 200, 160))
                screen.blit(hd, (col_x[j], 110))

            for i, s in enumerate(scores[:15]):
                y = 150 + i * 30
                rank = str(i + 1)
                name = s["name"][:18]
                score = str(s["score"])
                t = format_time(s["time"])
                date = s.get("date", "")
                cols = [rank, name, score, t, date]
                color = (200, 230, 255) if i < 3 else (150, 180, 200)
                for j, val in enumerate(cols):
                    r = font_row.render(val, True, color)
                    screen.blit(r, (col_x[j], y))

        back = font_header.render("ESC or click to go back", True, (80, 130, 150))
        screen.blit(
            back, (constants.WIDTH // 2 - back.get_width() // 2, constants.HEIGHT - 50)
        )

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return screen
            if event.type == pygame.MOUSEBUTTONDOWN:
                return screen
