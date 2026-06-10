import os
import math
import pygame

from constants import WIDTH, HEIGHT
import constants
from helper import death_screen
import os

_warden_idle = None
_warden_shoot = []


def _get_warden_sprites():
    global _warden_idle, _warden_shoot
    if _warden_idle is None:
        base = os.path.join(os.path.dirname(__file__), "..")
        img = pygame.image.load(
            os.path.join(base, "Warden Idle", "warden_shock_trooper(base).png")
        )
        _warden_idle = pygame.transform.scale(img, (175, 215))
        _warden_shoot = []
        for fname in (
            "warden_shock_shooter_frame_1.png",
            "warden_shock_shooter_frame_2.png",
        ):
            img = pygame.image.load(os.path.join(base, "Warden Shoot", fname))
            _warden_shoot.append(pygame.transform.scale(img, (175, 215)))
    return _warden_idle, _warden_shoot


class Enemies:
    def __init__(self, name, health, damage):
        self.name = name
        self.health = health
        self.damage = damage

    def take_damage(self, amount):
        self.health -= amount

        if self.health <= 0:
            print("💀")

    def attack(self):
        return self.damage

    def __str__(self):
        return f"{self.name} (HP: {self.health}, DMG: {self.damage})"


def update_enemies(
    enemies,
    player_rect,
    player_vel_y,
    static_solids,
    platforms,
    screen,
    clock,
    restart_func,
    projectiles,
    dt=1.0,
):
    for enemy in enemies[:]:
        dx = player_rect.centerx - enemy["rect"].centerx
        dy = player_rect.centery - enemy["rect"].centery
        dist = math.sqrt(dx * dx + dy * dy)

        can_see = False
        if dist < enemy["detect_range"]:
            can_see = True
            for obs in platforms:
                if obs.clipline(enemy["rect"].center, player_rect.center):
                    can_see = False
                    break

        enemy["state"] = "chase" if can_see else "patrol"

        if enemy.get("type") == "warden":
            move_x = 0
        elif enemy["state"] == "chase":
            enemy["dir"] = 1 if dx > 0 else -1
            move_x = enemy["chase_speed"] * enemy["dir"] * dt
        else:
            move_x = enemy["speed"] * enemy["dir"] * dt

        enemy["rect"].x += int(move_x)

        for plat in static_solids:
            if enemy["rect"].colliderect(plat):
                if move_x > 0:
                    enemy["rect"].right = plat.left
                    if enemy["state"] == "patrol":
                        enemy["dir"] = -1
                elif move_x < 0:
                    enemy["rect"].left = plat.right
                    if enemy["state"] == "patrol":
                        enemy["dir"] = 1

        if enemy["state"] == "patrol":
            if enemy["rect"].left <= enemy["patrol_left"]:
                enemy["rect"].left = int(enemy["patrol_left"])
                enemy["dir"] = 1
            elif enemy["rect"].right >= enemy["patrol_right"]:
                enemy["rect"].right = int(enemy["patrol_right"])
                enemy["dir"] = -1

        # Vertical movement
        enemy["vy"] = enemy.get("vy", 0)
        enemy["on_ground"] = enemy.get("on_ground", False)

        enemy["vy"] = min(enemy["vy"] + 0.8, 15)
        enemy["rect"].y += int(enemy["vy"])

        enemy["on_ground"] = False
        for plat in static_solids:
            if enemy["rect"].colliderect(plat):
                if enemy["vy"] >= 0:
                    enemy["rect"].bottom = plat.top
                    enemy["vy"] = 0
                    enemy["on_ground"] = True
                elif enemy["vy"] < 0:
                    enemy["rect"].top = plat.bottom
                    enemy["vy"] = 0

        # Jump when chasing, on ground, and player is above
        if (
            enemy["state"] == "chase"
            and enemy["on_ground"]
            and player_rect.bottom < enemy["rect"].top - 20
        ):
            enemy["vy"] = -14
            enemy["on_ground"] = False

        # ── WARDEN SHOOTING ──
        if enemy.get("type") == "warden":
            enemy["dir"] = 1 if player_rect.centerx > enemy["rect"].centerx else -1
            if enemy["state"] == "chase":
                if enemy["reload_timer"] > 0:
                    enemy["reload_timer"] -= 1
                elif enemy["burst_remaining"] > 0:
                    enemy["shoot_cooldown"] -= 1
                    if enemy["shoot_cooldown"] <= 0:
                        spawn_x = (
                            enemy["rect"].right
                            if enemy["dir"] > 0
                            else enemy["rect"].left - 8
                        )
                        spawn_y = enemy["rect"].centery - 4
                        speed = 8
                        projectiles.append(
                            {
                                "rect": pygame.Rect(spawn_x, spawn_y, 4, 4),
                                "vx": speed * enemy["dir"],
                                "vy": 3,
                                "weapon": "warden_bullet",
                                "dmg": 20,
                                "color": (60, 180, 255),
                                "life": 120,
                            }
                        )
                        enemy["burst_remaining"] -= 1
                        enemy["shoot_cooldown"] = 15
                if enemy["burst_remaining"] <= 0 and enemy["reload_timer"] <= 0:
                    enemy["reload_timer"] = 150
                    enemy["burst_remaining"] = 4
            else:
                enemy["burst_remaining"] = 4
                enemy["reload_timer"] = 0
                enemy["shoot_cooldown"] = 0

        if player_rect.colliderect(enemy["rect"]):
            if (
                player_vel_y > 0
                and player_rect.bottom - player_vel_y <= enemy["rect"].top + 10
            ):
                enemies.remove(enemy)
                constants.player_coins += 150
                return -12.0
    return None


def render_enemies(screen, enemies, camera_x, camera_y):
    for enemy in enemies:
        vx = enemy["rect"].x - camera_x
        vy = enemy["rect"].y - camera_y
        if (
            vx + enemy["rect"].width < 0
            or vx > WIDTH
            or vy + enemy["rect"].height < 0
            or vy > HEIGHT
        ):
            continue

        if enemy.get("type") == "warden":
            idle_spr, shoot_frames = _get_warden_sprites()
            if enemy["state"] == "chase" and (
                enemy["shoot_cooldown"] > 0 or enemy["burst_remaining"] < 4
            ):
                idx = (pygame.time.get_ticks() // 200) % len(shoot_frames)
                sprite = shoot_frames[idx]
            else:
                sprite = idle_spr
            if enemy["dir"] < 0:
                sprite = pygame.transform.flip(sprite, True, False)
            sx = vx - (sprite.get_width() - enemy["rect"].width) // 2
            sy = vy + enemy["rect"].height - sprite.get_height() + 35
            screen.blit(sprite, (sx, sy))
            continue

        col = (200, 50, 50) if enemy["state"] == "chase" else (160, 70, 50)
        pygame.draw.rect(
            screen,
            col,
            (vx, vy, enemy["rect"].width, enemy["rect"].height),
            border_radius=4,
        )
        pygame.draw.rect(
            screen,
            (255, 100, 100),
            (vx, vy, enemy["rect"].width, enemy["rect"].height),
            2,
            border_radius=4,
        )

        eye_dir = enemy["dir"]
        eye_off = 8 if eye_dir > 0 else -8
        eye_y = vy + 14
        pygame.draw.circle(screen, (255, 255, 200), (int(vx + 14 + eye_off), eye_y), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(vx + 14 + eye_off), eye_y), 3)
        pygame.draw.circle(screen, (255, 255, 200), (int(vx + 36 + eye_off), eye_y), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(vx + 36 + eye_off), eye_y), 3)
