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
    level_triggers = []

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
                elevators.append({
                    "rect":     rect,
                    "origin_y": float(y),
                    "range":    200,
                    "speed":    1.1,
                    "dir":      1,
                    "float_y":  float(y),
                })
                col += 2

            elif ch == '^':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size * 2)
                animated_doors.append({
                    "rect":      rect,
                    "open":      False,
                    "offset_y":  0,
                    "max_open":  tile_size * 2,
                })
                col += 1

            elif ch == '@':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                paperclips.append({"rect": rect, "collected": False})
                col += 1

            elif ch == '2':
                rect = pygame.Rect(col * tile_size, y, tile_size, tile_size)
                level_triggers.append({"rect": rect, "target_level": 2})
                col += 1  # Standard increment so the loop continues


            else:
                col += 1

    return {
        "platforms":       platforms,
        "breakable_doors": breakable_doors,
        "paperclips":      paperclips,
        "elevators":       elevators,
        "animated_doors":  animated_doors,
        "level_triggers":  level_triggers,
    }

def map_world_width(tile_map: list[str], tile_size: int = physics.TILE_SIZE):
    return max(len(row) for row in tile_map) * tile_size