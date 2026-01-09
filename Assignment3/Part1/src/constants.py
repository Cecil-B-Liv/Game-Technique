"""
Constants for GridWorld
"""

# Actions:  0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
A_UP = 0
A_RIGHT = 1
A_DOWN = 2
A_LEFT = 3

ALL_ACTIONS = [A_UP, A_RIGHT, A_DOWN, A_LEFT]

# Action vectors (dx, dy)
ACTIONS = [
    (0, -1),   # UP
    (1, 0),    # RIGHT
    (0, 1),    # DOWN
    (-1, 0),   # LEFT
]

# Colors (RGB)
COL_BG = (25, 28, 34)
COL_GRID = (45, 50, 58)
COL_AGENT = (74, 222, 128)
COL_APPLE = (252, 92, 101)
COL_ROCK = (100, 100, 100)
COL_FIRE = (255, 69, 0)
COL_KEY = (255, 215, 0)
COL_CHEST = (139, 69, 19)
COL_MONSTER = (148, 0, 211)
COL_TEXT = (240, 240, 240)

# Grid dimensions
WIDTH_TILES = 12
HEIGHT_TILES = 8

# Level layouts
LEVEL0 = [
    "S           ",
    "            ",
    "        A   ",
    "        A   ",
    "        A   ",
    "        A   ",
    "        A   ",
    "        A   "
]

LEVEL1 = [
    "S           ",
    "    FF      ",
    "    FF  A   ",
    "    FF  A   ",
    "    FF  A   ",
    "    FF  A   ",
    "    FF  A   ",
    "        A   "
]

LEVEL2 = [
    "S     R   C ",
    "      R     ",
    "  A   R   A ",
    "      R     ",
    "  K   R   A ",
    "      R     ",
    "            ",
    "            "
]

LEVEL3 = [
    "S   R     C ",
    "    R       ",
    "A   RRRR  A ",
    "    R       ",
    "K   R     A ",
    "    R       ",
    "    R     C ",
    "            "
]

LEVEL4 = [
    "S           ",
    "            ",
    "    M   A   ",
    "        A   ",
    "  M     A   ",
    "        A   ",
    "    M   A   ",
    "        A   "
]

LEVEL5 = [
    "S   R   M C ",
    "    R       ",
    "A   RRRR  A ",
    "    R       ",
    "K   R  M  A ",
    "    R       ",
    "    R       ",
    "  M         "
]

# Normalize all levels to proper width
def normalize_level(level, width=WIDTH_TILES):
    """Ensure all rows have the same width"""
    return [row.ljust(width)[:width] for row in level]

LEVEL0 = normalize_level(LEVEL0)
LEVEL1 = normalize_level(LEVEL1)
LEVEL2 = normalize_level(LEVEL2)
LEVEL3 = normalize_level(LEVEL3)
LEVEL4 = normalize_level(LEVEL4)
LEVEL5 = normalize_level(LEVEL5)

LEVELS = {
    0: LEVEL0,
    1: LEVEL1,
    2: LEVEL2,
    3: LEVEL3,
    4: LEVEL4,
    5: LEVEL5,
}