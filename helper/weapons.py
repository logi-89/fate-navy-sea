import pygame

from constants import WEAPON_DEFS, WIDTH, HEIGHT


def get_available(dev_mode):
    return ["spear", "water_gun", "water_balloon"] if dev_mode else []


def fire(weapon_key, player_rect, player_facing, projectiles, ammo_counts, enemies=None):
    defs = WEAPON_DEFS[weapon_key]

    melee_r = defs.get("melee_range", 0)
    if melee_r > 0:
        if player_facing > 0:
            hit_rect = pygame.Rect(player_rect.right, player_rect.y, melee_r, player_rect.height)
        else:
            hit_rect = pygame.Rect(player_rect.left - melee_r, player_rect.y, melee_r, player_rect.height)
        hit = False
        if enemies:
            for e in enemies[:]:
                if hit_rect.colliderect(e["rect"]):
                    e["hp"] -= defs["dmg"]
                    if e["hp"] <= 0:
                        enemies.remove(e)
                    hit = True
        return hit

    ammo = ammo_counts.get(weapon_key, defs["ammo"])
    if ammo == 0:
        return False

    if defs["ammo"] > 0:
        ammo_counts[weapon_key] = ammo - 1

    spawn_x = player_rect.right if player_facing > 0 else player_rect.left - 8
    spawn_y = player_rect.centery - 4

    vy = 0
    if weapon_key == "water_balloon":
        vy = -6

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


def update(projectiles, static_solids, enemies):
    for p in projectiles[:]:
        p["rect"].x += int(p["vx"])
        p["rect"].y += int(p["vy"])

        p["vy"] = min(p["vy"] + 0.4, 12)

        p["life"] -= 1
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
            if p["rect"].colliderect(e["rect"]):
                e["hp"] = e.get("hp", 1) - p["dmg"]
                if p in projectiles:
                    projectiles.remove(p)
                if e["hp"] <= 0:
                    enemies.remove(e)
                break


def render(screen, projectiles, camera_x, camera_y):
    for p in projectiles:
        vx = p["rect"].x - camera_x
        vy = p["rect"].y - camera_y
        if vx + p["rect"].width < 0 or vx > WIDTH or vy + p["rect"].height < 0 or vy > HEIGHT:
            continue

        if p["weapon"] == "water_gun":
            cx = int(vx + p["rect"].width // 2)
            cy = int(vy + p["rect"].height // 2)
            pygame.draw.circle(screen, p["color"], (cx, cy), 5)
            pygame.draw.circle(screen, (180, 240, 255), (cx, cy), 5, 1)
        else:
            cx = int(vx + p["rect"].width // 2)
            cy = int(vy + p["rect"].height // 2)
            pygame.draw.circle(screen, p["color"], (cx, cy), 7)
            pygame.draw.circle(screen, (150, 220, 240), (cx, cy), 7, 1)
            pygame.draw.circle(screen, (255, 255, 255, 100), (cx - 2, cy - 2), 2)
