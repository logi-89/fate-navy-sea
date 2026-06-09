import pygame

import constants
from constants import WEAPON_DEFS, WIDTH, HEIGHT


def get_available(dev_mode):
    if dev_mode:
        return ["spear", "water_gun", "water_balloon"]
    avail = ["spear"]
    if "Spears" in constants.player_owned_weapons:
        avail.append("spear")
    return avail

# def get_available_level_one():
#     return ["spear"]


def fire(weapon_key, player_rect, player_facing, projectiles, ammo_counts, enemies=None):
    defs = WEAPON_DEFS[weapon_key]

    melee_r = defs.get("melee_range", 0)
    if melee_r > 0:
        hit_y = player_rect.y - 24
        hit_h = player_rect.height + 24
        if player_facing > 0:
            hit_rect = pygame.Rect(player_rect.right, hit_y, melee_r, hit_h)
        else:
            hit_rect = pygame.Rect(player_rect.left - melee_r, hit_y, melee_r, hit_h)
        projectiles.append({
            "rect": hit_rect,
            "life": 6,
            "weapon": "spear_slash",
            "color": defs["color"],
        })
        hit = False
        if enemies:
            for e in enemies[:]:
                if hit_rect.colliderect(e["rect"]):
                    e["hp"] -= defs["dmg"]
                    if e["hp"] <= 0:
                        enemies.remove(e)
                        constants.total_score += 150
                        constants.total_kills += 1
                    constants.player_coins += 150
                    hit = True
        return hit

    ammo = ammo_counts.get(weapon_key, defs["ammo"])
    if ammo == 0:
        return False

    if defs["ammo"] > 0:
        ammo_counts[weapon_key] = ammo - 1

    spawn_x = player_rect.centerx + (24 if player_facing > 0 else -24)
    spawn_y = player_rect.y + 20

    vy = 0

    projectiles.append({
        "rect": pygame.Rect(spawn_x, spawn_y, 8, 8),
        "vx": defs["speed"] * player_facing,
        "vy": vy,
        "weapon": weapon_key,
        "dmg": defs["dmg"],
        "color": defs["color"],
        "life": 90,
    })
    return True


def update(projectiles, static_solids, enemies, dt=1.0):
    for p in projectiles[:]:
        if p["weapon"] == "spear_slash":
            continue

        p["rect"].x += int(p["vx"] * dt)
        p["rect"].y += int(p["vy"] * dt)

        if p["weapon"] not in ("warden_bullet", "water_gun", "water_balloon"):
            p["vy"] = min(p["vy"] + 0.4 * dt, 12)

        p["life"] -= dt
        if p["life"] <= 0:
            projectiles.remove(p)
            continue

        hit_wall = False
        for s in static_solids:
            if p["rect"].colliderect(s):
                hit_wall = True
                break
        if hit_wall:
            projectiles.remove(p)
            continue

        for e in enemies[:]:
            if p["weapon"] == "warden_bullet":
                break
            if p["rect"].colliderect(e["rect"]):
                e["hp"] = e.get("hp", 1) - p["dmg"]
                if p in projectiles:
                    projectiles.remove(p)
                if e["hp"] <= 0:
                    enemies.remove(e)
                    constants.player_coins += 150
                    constants.total_score += 150
                    constants.total_kills += 1
                break


def render(screen, projectiles, camera_x, camera_y, dt=1.0):
    for p in projectiles[:]:
        vx = p["rect"].x - camera_x
        vy = p["rect"].y - camera_y
        if vx + p["rect"].width < 0 or vx > WIDTH or vy + p["rect"].height < 0 or vy > HEIGHT:
            continue

        if p["weapon"] == "spear_slash":
            if constants.dev_mode:
                alpha = int(200 * p["life"] / 6)
                s = pygame.Surface((p["rect"].width, p["rect"].height), pygame.SRCALPHA)
                s.fill((p["color"][0], p["color"][1], p["color"][2], alpha))
                screen.blit(s, (vx, vy))
                pygame.draw.rect(screen, (255, 220, 160, alpha), (vx, vy, p["rect"].width, p["rect"].height), 2)
            p["life"] -= dt
            if p["life"] <= 0:
                projectiles.remove(p)
        elif p["weapon"] == "water_gun":
            cx = int(vx + p["rect"].width // 2)
            cy = int(vy + p["rect"].height // 2)
            pygame.draw.circle(screen, p["color"], (cx, cy), 5)
            pygame.draw.circle(screen, (180, 240, 255), (cx, cy), 5, 1)
        elif p["weapon"] == "warden_bullet":
            cx = int(vx + p["rect"].width // 2)
            cy = int(vy + p["rect"].height // 2)
            pygame.draw.circle(screen, (60, 180, 255), (cx, cy), 3)
            pygame.draw.circle(screen, (180, 230, 255), (cx, cy), 3, 1)
        else:
            cx = int(vx + p["rect"].width // 2)
            cy = int(vy + p["rect"].height // 2)
            pygame.draw.circle(screen, p["color"], (cx, cy), 7)
            pygame.draw.circle(screen, (150, 220, 240), (cx, cy), 7, 1)
            pygame.draw.circle(screen, (255, 255, 255, 100), (cx - 2, cy - 2), 2)
