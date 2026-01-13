"""Game constants and configuration."""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (150, 0, 150)
ORANGE = (255, 165, 0)

# Player settings
PLAYER_SIZE = 20
PLAYER_SPEED = 5.0
PLAYER_ROTATION_SPEED = 5.0  # degrees per frame
PLAYER_MAX_HEALTH = 100
PLAYER_SHOOT_COOLDOWN = 15  # frames

# Enemy settings
ENEMY_SIZE = 15
ENEMY_SPEED = 2.0
ENEMY_HEALTH = 30
ENEMY_DAMAGE = 10

# Spawner settings
SPAWNER_SIZE = 30
SPAWNER_HEALTH = 100
SPAWN_INTERVAL = 120  # frames between spawns
MAX_ENEMIES_PER_SPAWNER = 5

# Projectile settings
PROJECTILE_SPEED = 10.0
PROJECTILE_SIZE = 5
PROJECTILE_DAMAGE = 20

# Phase settings
INITIAL_SPAWNERS = 2
SPAWNERS_PER_PHASE = 1  # Additional spawners each phase
MAX_PHASES = 5

# Episode limits
MAX_STEPS = 3000