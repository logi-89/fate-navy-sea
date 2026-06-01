# Window Size
WIDTH = 1400
HEIGHT = 850

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
    DOUBLE_JUMP_POWER= -13
    TILE_SIZE = 50  # Each tile is 50x50 pixels

# Shop
class shop:
    # SHOP SCREEN
    SHOP_ITEMS = [
        {"name": "Health Flask", "desc": "+1 flask (heals 40 HP when used)", "cost": 15, "key": "flask"},
        {"name": "Sword Upgrade", "desc": "+15 sword damage", "cost": 30, "key": "sword_dmg"},
        {"name": "Water Gun Ammo +3", "desc": "+3 balloon capacity", "cost": 20, "key": "balloon_ammo"},
        {"name": "Max HP +25", "desc": "Increase maximum health", "cost": 40, "key": "max_hp"},
        {"name": "Sea Boots", "desc": "+1 speed permanently", "cost": 50, "key": "speed"},
        {"name": "Revive Token", "desc": "Auto-revive once with 30 HP", "cost": 80, "key": "revive"},
        {"name": "spears", "desc": "spears", "cost": 80, "key": "spears"},
    ]

# Sea gel palette
GROUND_TOP  = (40, 180, 160)   # bright teal surface
GROUND_SIDE = (20, 120, 110)   # deeper teal edge
GROUND_DIRT = (10,  70,  80)   # dark ocean-floor fill

dev_mode = False

COLOR_DOOR_INTACT  = (30, 100, 160)   # deep sea blue door
COLOR_DOOR_DAMAGED = (60, 150, 200)   # lighter cracked blue
COLOR_PAPERCLIP    = (160, 240, 220)  # seafoam silver

# Player settings
player_size = 150
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - player_size
player_speed = 5
player_velocity_y = 0
jump_height = -15
gravity = 1

