# Window Size
WIDTH = 1500
HEIGHT = 900

import os
import sys


def resource_path(relative_path):
    try:
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
    except Exception:
        pass
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

# Colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (200, 40,  40)
DARK_RED   = (120, 10,  10)
ORANGE     = (220, 120, 40)
GOLD       = (255, 200, 50)
DARK_TEAL  = (0,   80,  90)
TEAL       = (30,  160, 150)
LIGHT_TEAL = (80,  220, 200)
SEA_DARK   = (5,   20,  45)
SEA_MID    = (10,  40,  80)
SEA_LIGHT  = (20,  70,  120)
SAND       = (180, 150, 90)
STONE      = (70,  80,  95)
STONE_DARK = (45,  50,  65)
BROWN      = (90,  55,  30)
PURPLE     = (100, 50,  160)
PINK       = (220, 80,  140)
GREY       = (120, 130, 140)
LIGHT_GREY = (180, 190, 200)

COLOR_DOOR_INTACT  = (30, 100, 160)   # deep sea blue door
COLOR_DOOR_DAMAGED = (60, 150, 200)   # lighter cracked blue
COLOR_PAPERCLIP    = (160, 240, 220)  # seafoam silver

# LOREEEE DROOOP!
lore_display_text  = None   # currently shown lore string (None = hidden)
lore_display_timer = 0      # frames remaining to show it



# Main Menu Colors
class title_screen:
    BUTTON_COLOR = (40, 80, 120)
    HOVER_COLOR = (60, 110, 170)

# Physics Constants
class physics:
    GRAVITY          = 0.981
    MAX_FALL_SPEED   = 18
    JUMP_POWER       = -16  
    PLAYER_SPEED     = 5
    DOUBLE_JUMP_POWER = 0 #-13 DO NOT ADD YET I PUT ZERO FOR A REASON
    TILE_SIZE = 50  # Each tile is 50x50 pixels

# Shop
class shop:
    # SHOP SCREEN
    SHOP_ITEMS = [
        {"name": "Health Flask", "desc": "+1 flask (heals 40 HP when used)", "cost": 115, "key": "flask"},
        {"name": "Water Gun Ammo +3", "desc": "+3 balloon capacity",         "cost": 120, "key": "balloon_ammo"},
        {"name": "Max HP +25", "desc": "Increase maximum health",            "cost": 260, "key": "max_hp"},
        {"name": "Sea Boots", "desc": "+1 speed permanently",                "cost": 200, "key": "speed"},
        #{"name": "Spears", "desc": "spears",                                 "cost": 180, "key": "Spears"},
    ]

# Sea gel palette
GROUND_TOP  = (40, 180, 160)   # bright teal surface
GROUND_SIDE = (20, 120, 110)   # deeper teal edge
GROUND_DIRT = (10,  70,  80)   # dark ocean-floor fill

dev_mode = False

PLAYER_MAX_HP = 100
ENEMY_DAMAGE = 15
ENEMY_HP = 1
INVINCIBLE_FRAMES = 60

WEAPON_DEFS = {
    "spear":         {"name": "Spear",         "dmg": 50, "speed": 14, "cooldown": 20, "ammo": -1, "color": (180, 120, 60), "melee_range": 80},
    "water_gun":     {"name": "Water Gun",     "dmg": 15, "speed": 22, "cooldown": 8,  "ammo": 50, "color": (80, 200, 240)},
    "water_balloon": {"name": "Water Balloon", "dmg": 25, "speed": 9,  "cooldown": 35, "ammo": 20, "color": (60, 180, 220)},
}

# Player settings
player_size = 150
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - player_size
player_speed = 5
player_velocity_y = 0
jump_height = -15
gravity = 1
player_inventory_clips = 0
player_coins = 0
total_score = 0
total_kills = 0
total_play_time = 0
player_flasks = 0
player_revive_tokens = 0
player_owned_weapons = []
player_balloon_ammo_bonus = 0

# Settings
settings = {
    "master_volume": 50,
    "hud_scale": 100,
    "display_w": 1500,
    "display_h": 900,
    "display_mode": "fullscreen",
    "fps": 60,
    "render_scale": 1.0,
}

RENDER_SCALE_OPTIONS = [1.0, 1.5, 2.0, 3.0]
FPS_OPTIONS = [30, 60, 90, 120, 240, 0]

AVAILABLE_RESOLUTIONS = [
    (1280, 720),
    (1366, 768),
    (1500, 900),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
]

DISPLAY_MODES = ["fullscreen", "borderless", "windowed"]

#shop names
SHOP_NAME_HM = "Harbor Market"
SHOP_NAME_PKS = "Pearlkeeper's Shop"
SHOP_NAME_NE = "Neptune's Exchange"
