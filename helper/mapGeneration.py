import random
from constants import *

import pygame

def build_platforms_from_map(tile_map: list[str], tile_size: int = physics.TILE_SIZE):
    """
        # -> wall / solid platform
        @ -> paper clip pickup
        ! -> breakable door (3 hits)
        _ -> elevator platform (moves up/down)
        ^ -> animated door (opens upward)
        num -> #level
    """
    platforms       = []
    breakable_doors = []
    paperclips      = []
    elevators       = []
    animated_doors  = []
    level_triggers  = []
    lore = []
    water = []
    enemies = []
    coins = []
    shop_triggers = []

    for row_idx, row in enumerate(tile_map):
        y   = row_idx * tile_size
        col = 0
        while col < len(row):
            ch = row[col]

            if ch == '#':
                start_col = col
                while col < len(row) and row[col] == '#':
                    col += 1
                width = (col - start_col) * tile_size
                platforms.append(pygame.Rect(start_col * tile_size, y, width, tile_size))

            elif ch == '!':
                start_col = col
                while col < len(row) and row[col] == '!':
                    col += 1
                width = (col - start_col) * tile_size
                rect  = pygame.Rect(start_col * tile_size, y, width, tile_size)
                breakable_doors.append({"rect": rect, "hp": 3, "broken": False})

            elif ch == '_':
                rect = pygame.Rect(col * tile_size, y, tile_size * 2, tile_size // 2)
                
                # Scan upward for a # tile to set upper limit
                min_y = float(y)  # default: don't move up at all
                for scan_row in range(row_idx - 1, -1, -1):
                    if col < len(tile_map[scan_row]) and tile_map[scan_row][col] == '#':
                        min_y = float(scan_row * tile_size + tile_size)
                        break
                
                # Scan downward for a # tile to set lower limit
                max_y = float(y + 200)  # default fallback
                for scan_row in range(row_idx + 1, len(tile_map)):
                    if col < len(tile_map[scan_row]) and tile_map[scan_row][col] == '#':
                        max_y = float(scan_row * tile_size - tile_size // 2)
                        break
                
                elevators.append({
                    "rect":     rect,
                    "origin_y": float(y),
                    "min_y":    min_y,
                    "max_y":    max_y,
                    "speed":    1.5,
                    "dir":      1,
                    "float_y":  float(y),
                })
                col += 1

            elif ch == '^':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size * 2)
                animated_doors.append({
                    "rect":      rect,
                    "origin_y":  rect.y,
                    "open":      False,
                    "offset_y":  0,
                    "max_open":  tile_size * 2,
                })
                col += 1

            elif ch == '@':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                paperclips.append({"rect": rect, "collected": False})
                col += 1

            elif ch == '$':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                coins.append({"rect": rect, "collected": False})
                col += 1

            elif ch == '?':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                lore.append({"rect": rect, "collected": False})
                col += 1

            elif ch =='~':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                water.append(rect)
                col += 1

            elif ch == 'E':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                enemies.append({
                    "rect": rect,
                    "start_x": float(rect.x),
                    "patrol_left": float(rect.x - 150),
                    "patrol_right": float(rect.x + 150),
                    "dir": random.choice([-1, 1]),
                    "speed": 2,
                    "chase_speed": 4,
                    "detect_range": 350,
                    "state": "patrol",
                    "hp": 100,
                    "max_hp": 100,
                    "damage": 15,
                })
                col += 1

            elif ch == 'W':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                enemies.append({
                    "rect": rect,
                    "start_x": float(rect.x),
                    "patrol_left": float(rect.x - 150),
                    "patrol_right": float(rect.x + 150),
                    "dir": random.choice([-1, 1]),
                    "speed": 1,
                    "chase_speed": 1,
                    "detect_range": 750,
                    "state": "patrol",#fixed
                    "hp": 150,
                    "max_hp": 150,
                    "damage": 5,
                })
                col += 1

            elif ch == 'F':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                enemies.append({
                    "rect": rect,
                    "start_x": float(rect.x),
                    "patrol_left": float(rect.x - 150),
                    "patrol_right": float(rect.x + 150),
                    "dir": random.choice([-1, 1]),
                    "speed": 1,
                    "chase_speed": 1,
                    "detect_range": 750,
                    "state": "patrol",#fixed
                    "hp": 500,
                    "max_hp": 500,
                    "damage": 33,
                })
                col += 1

            elif ch == 'S':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                shop_triggers.append({"rect": rect})
                col += 1

            elif ch.isdigit():
                # Any digit 1-9 encodes a target level (e.g. '1' -> L1, '2' -> L2)
                target = int(ch)
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                level_triggers.append({"rect": rect, "target_level": target})
                col += 1

            else:
                col += 1

    return {
        "platforms":       platforms,
        "breakable_doors": breakable_doors,
        "paperclips":      paperclips,
        "elevators":       elevators,
        "animated_doors":  animated_doors,
        "level_triggers":  level_triggers,
        "lore":            lore,
        "water":           water,
        "enemies":         enemies,
        "coins":           coins,
        "shop_triggers":   shop_triggers,
    }

def map_world_width(tile_map: list[str], tile_size: int = physics.TILE_SIZE):
    return max(len(row) for row in tile_map) * tile_size