import math
import pygame

from constants import WIDTH, HEIGHT
import constants
from helper import death_screen

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

def update_enemies(enemies, player_rect, player_vel_y, static_solids, platforms, screen, clock, restart_func):
    for enemy in enemies[:]:
        dx = player_rect.centerx - enemy["rect"].centerx
        dy = player_rect.centery - enemy["rect"].centery
        dist = math.sqrt(dx*dx + dy*dy)

        can_see = False
        if dist < enemy["detect_range"]:
            can_see = True
            for obs in platforms:
                if obs.clipline(enemy["rect"].center, player_rect.center):
                    can_see = False
                    break

        enemy["state"] = "chase" if can_see else "patrol"

        if enemy["state"] == "chase":
            enemy["dir"] = 1 if dx > 0 else -1
            move_x = enemy["chase_speed"] * enemy["dir"]
        else:
            move_x = enemy["speed"] * enemy["dir"]

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
        if enemy["state"] == "chase" and enemy["on_ground"] and player_rect.bottom < enemy["rect"].top - 20:
            enemy["vy"] = -14
            enemy["on_ground"] = False

        if player_rect.colliderect(enemy["rect"]):
            if player_vel_y > 0 and player_rect.bottom - player_vel_y <= enemy["rect"].top + 10:
                enemies.remove(enemy)
                constants.player_coins += 150
                return -12.0
    return None


def render_enemies(screen, enemies, camera_x, camera_y):
    for enemy in enemies:
        vx = enemy["rect"].x - camera_x
        vy = enemy["rect"].y - camera_y
        if vx + enemy["rect"].width < 0 or vx > WIDTH or vy + enemy["rect"].height < 0 or vy > HEIGHT:
            continue

        col = (200, 50, 50) if enemy["state"] == "chase" else (160, 70, 50)
        pygame.draw.rect(screen, col, (vx, vy, enemy["rect"].width, enemy["rect"].height), border_radius=4)
        pygame.draw.rect(screen, (255, 100, 100), (vx, vy, enemy["rect"].width, enemy["rect"].height), 2, border_radius=4)

        eye_dir = enemy["dir"]
        eye_off = 8 if eye_dir > 0 else -8
        eye_y = vy + 14
        pygame.draw.circle(screen, (255, 255, 200), (int(vx + 14 + eye_off), eye_y), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(vx + 14 + eye_off), eye_y), 3)
        pygame.draw.circle(screen, (255, 255, 200), (int(vx + 36 + eye_off), eye_y), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(vx + 36 + eye_off), eye_y), 3)
