"""
Game constants and configuration. 

This file contains all the "magic numbers" used throughout the game. 
Keeping them in one place makes it easy to tune the game balance.
"""

# =============================================================================
# SCREEN SETTINGS
# =============================================================================
SCREEN_WIDTH = 800    # Width of game window in pixels
SCREEN_HEIGHT = 600   # Height of game window in pixels
FPS = 60              # Frames per second (how fast the game runs)

# =============================================================================
# COLORS (RGB tuples)
# =============================================================================
# Each color is a tuple of (Red, Green, Blue) values from 0-255
BLACK = (0, 0, 0)         # Background color
WHITE = (255, 255, 255)   # Text and borders
RED = (255, 0, 0)         # Enemies and damage indicators
GREEN = (0, 255, 0)       # Health bars (healthy portion)
BLUE = (0, 100, 255)      # Player ship
YELLOW = (255, 255, 0)    # Projectiles (bullets)
PURPLE = (150, 0, 150)    # Spawners
ORANGE = (255, 165, 0)    # Could be used for effects

# =============================================================================
# PLAYER SETTINGS
# =============================================================================
PLAYER_SIZE = 20              # Radius of player hitbox in pixels
PLAYER_SPEED = 5.0            # How fast player moves (pixels per frame)
PLAYER_ROTATION_SPEED = 5.0   # How fast player rotates (degrees per frame)
PLAYER_MAX_HEALTH = 100       # Starting health points
PLAYER_SHOOT_COOLDOWN = 15    # Frames between shots (15 frames = 0.25 seconds at 60 FPS)

# =============================================================================
# ENEMY SETTINGS  
# =============================================================================
ENEMY_SIZE = 15       # Radius of enemy hitbox
ENEMY_SPEED = 2.0     # How fast enemies chase player (pixels per frame)
ENEMY_HEALTH = 30     # How much damage enemy can take before dying
ENEMY_DAMAGE = 10     # How much damage enemy deals on collision with player

# =============================================================================
# SPAWNER SETTINGS
# =============================================================================
SPAWNER_SIZE = 30             # Half-width of spawner (it's a square)
SPAWNER_HEALTH = 100          # How much damage spawner can take
SPAWN_INTERVAL = 120          # Frames between enemy spawns (120 = 2 seconds)
MAX_ENEMIES_PER_SPAWNER = 5   # Maximum active enemies from one spawner
SPAWNER_ANIMATION_SPEED = 5
# =============================================================================
# PROJECTILE SETTINGS
# =============================================================================
PROJECTILE_SPEED = 10.0   # How fast bullets travel (pixels per frame)
PROJECTILE_SIZE = 5       # Radius of bullet hitbox
PROJECTILE_DAMAGE = 20    # Damage dealt to enemies/spawners on hit

# =============================================================================
# PHASE/DIFFICULTY SETTINGS
# =============================================================================
INITIAL_SPAWNERS = 2      # Number of spawners at phase 1
SPAWNERS_PER_PHASE = 1    # Additional spawners added each phase
MAX_PHASES = 5            # Total phases to complete the game

# =============================================================================
# EPISODE LIMITS
# =============================================================================
MAX_STEPS = 3000          # Maximum steps before episode ends (timeout)
                          # At 60 FPS, this is 50 seconds of gameplay