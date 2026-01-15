"""
Game entity classes:  Player, Enemy, Spawner, Projectile. 

Each class represents a game object with: 
- Position and movement
- Health (if applicable)
- Collision detection
- Drawing/rendering
"""

import random
import pygame
import math
import numpy as np
from game.constants import *



# =============================================================================
# PLAYER CLASS
# =============================================================================
class Player: 
    """
    The player-controlled ship.
    
    The player is the main character controlled by either: 
    - The AI agent during training/evaluation
    - Human input during manual play
    
    Attributes:
        x, y:  Position on screen (center of the player)
        vx, vy: Velocity (how fast moving in x and y directions)
        angle: Direction the player is facing (0 = right, 90 = up)
        health: Current health points
        shoot_cooldown: Frames until player can shoot again
        size:  Collision radius
    """
    
    def __init__(self, x, y):
        """
        Initialize player at given position.
        
        Args:
            x: Starting x position (usually center of screen)
            y: Starting y position (usually center of screen)
        """
        self.x = x                          # Current x position
        self.y = y                          # Current y position
        self.vx = 0.0                        # Velocity in x direction
        self.vy = 0.0                        # Velocity in y direction
        self.angle = 0.0                     # Facing direction in degrees
        self.health = PLAYER_MAX_HEALTH      # Start with full health
        self.shoot_cooldown = 0              # Can shoot immediately
        self.size = PLAYER_SIZE              # Collision radius
        
    def reset(self, x, y):
        """
        Reset player to initial state (called at start of each episode).
        
        This is important for RL - each episode should start fresh.
        """
        self. x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.health = PLAYER_MAX_HEALTH
        self.shoot_cooldown = 0
        
    def move_directional(self, dx, dy):
        """
        Move player in a direction (Control Style 2:  Directional).
        
        This is the simpler control scheme where: 
        - dx = -1 means move left, dx = 1 means move right
        - dy = -1 means move up, dy = 1 means move down
        
        Args:
            dx: Direction in x (-1, 0, or 1)
            dy: Direction in y (-1, 0, or 1)
        """
        # Set velocity based on direction
        self.vx = dx * PLAYER_SPEED
        self. vy = dy * PLAYER_SPEED
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Update angle to face movement direction (for shooting)
        # Only update if actually moving
        if dx != 0 or dy != 0:
            # atan2 gives angle in radians, convert to degrees
            # Note: negative dy because screen y-axis is inverted (down is positive)
            self.angle = math.degrees(math. atan2(-dy, dx))
            
        # Keep player inside screen bounds
        self._clamp_position()
        
    def rotate(self, direction):
        """
        Rotate player (Control Style 1: Rotation).
        
        Args:
            direction: -1 to rotate right (clockwise), 1 to rotate left (counter-clockwise)
        """
        self.angle += direction * PLAYER_ROTATION_SPEED
        self. angle %= 360  # Keep angle between 0 and 360
        
    def thrust(self):
        """
        Move forward in the direction player is facing (Control Style 1).
        
        Uses trigonometry to convert angle to x/y movement: 
        - cos(angle) gives x component
        - sin(angle) gives y component
        """
        # Convert angle from degrees to radians for math functions
        rad = math.radians(self.angle)
        
        # Calculate velocity components
        # cos gives x component, sin gives y component
        self.vx = math.cos(rad) * PLAYER_SPEED
        # Negative because screen y increases downward, but we want "up" to be negative y
        self.vy = -math.sin(rad) * PLAYER_SPEED
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Keep inside screen
        self._clamp_position()
        
    def _clamp_position(self):
        """
        Keep player within screen bounds.
        
        Uses max/min to ensure: 
        - x is at least 'size' pixels from left edge
        - x is at most 'SCREEN_WIDTH - size' from left edge
        - Same for y with top/bottom edges
        """
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self. size, self.y))
        
    def can_shoot(self):
        """Check if player can shoot (cooldown has expired)."""
        return self.shoot_cooldown <= 0
    
    def shoot(self):
        """
        Attempt to fire a projectile.
        
        Returns:
            Projectile object if successful, None if on cooldown
        """
        if self.can_shoot():
            # Reset cooldown
            self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
            
            # Calculate spawn position (front of player)
            rad = math.radians(self. angle)
            px = self.x + math.cos(rad) * self.size  # Spawn at front edge
            py = self.y - math.sin(rad) * self.size
            
            # Create and return new projectile
            return Projectile(px, py, self.angle)
        return None
    
    def update(self):
        """
        Update player state each frame.
        
        Called every step to: 
        - Decrease shoot cooldown
        - Apply friction to slow down
        """
        # Decrease cooldown timer
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Apply friction (velocity decreases over time)
        # 0.95 means player retains 95% of velocity each frame
        self.vx *= 0.95
        self. vy *= 0.95
            
    def take_damage(self, damage):
        """
        Apply damage to player.
        
        Args:
            damage: Amount of health to subtract
            
        Returns:
            True if player died, False otherwise
        """
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        """
        Draw player on the screen.
        
        Draws:
        1. A rotated ship image pointing in the facing direction
        2. A health bar above the player
        3. Different ship sprite based on damage level (4 stages)
        
        Args:
            screen: Pygame surface to draw on
        """
        # Determine damage stage based on health (4 stages: 100%, 75%, 50%, 25%)
        health_ratio = self.health / PLAYER_MAX_HEALTH
        if health_ratio > 0.75:
            damage_stage = 0  # Full health
        elif health_ratio > 0.5:
            damage_stage = 1  # 25% damage
        elif health_ratio > 0.25:
            damage_stage = 2  # 50% damage
        else:
            damage_stage = 3  # 75% damage
        
        # Load the appropriate sprite image
        image_path = f"sprites/player/player_damage_{damage_stage}.png"
        try:
            image = pygame.image.load(image_path)
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            return
        
        # The ship image points north, so we need to rotate it based on the angle
        # angle = 0 is east, so we add 90 to convert from north to east orientation
        rotated_image = pygame.transform.rotate(image, self.angle - 90)
        
        # Get the rect for the rotated image and center it on the player position
        image_rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        
        # Draw the rotated image
        screen.blit(rotated_image, image_rect)
        
        # Draw health bar above player
        bar_width = 40
        bar_height = 5
        
        # Red background (shows missing health)
        pygame.draw.rect(screen, RED, 
                        (self.x - bar_width // 2, self.y - self.size - 15, 
                        bar_width, bar_height))
        # Green foreground (shows current health)
        pygame.draw.rect(screen, GREEN,
                        (self.x - bar_width // 2, self.y - self.size - 15, 
                        int(bar_width * health_ratio), bar_height))


# =============================================================================
# ENEMY CLASS
# =============================================================================
class Enemy:
    """
    Enemy that chases and damages the player.
    
    Enemies are spawned by Spawners and will: 
    - Move toward the player's current position
    - Damage the player on contact
    - Be destroyed when shot enough times
    """
    
    def __init__(self, x, y, spawner_id):
        """
        Create an enemy at the given position.
        
        Args:
            x, y: Starting position
            spawner_id: ID of the spawner that created this enemy
                       (used to track spawner's active enemy count)
        """
        self.x = x
        self.y = y
        self.health = ENEMY_HEALTH
        self.size = ENEMY_SIZE
        self.spawner_id = spawner_id
        self.angle = 0  # Direction enemy is facing (toward player)
        self.sprite_variant = random.randint(0, 5)  # Random sprite (0-7, 8 total)
        
    def update(self, player_x, player_y):
        """
        Move toward the player. 
        
        Uses simple vector math: 
        1. Calculate direction vector to player
        2. Normalize it (make length = 1)
        3. Multiply by speed
        4. Calculate angle for sprite rotation
        
        Args:
            player_x, player_y: Current player position
        """
        # Calculate direction to player
        dx = player_x - self.x
        dy = player_y - self.y
        
        # Calculate distance (length of direction vector)
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Normalize and apply speed (avoid division by zero)
        if dist > 0:
            # (dx/dist, dy/dist) is a unit vector pointing at player
            self.x += (dx / dist) * ENEMY_SPEED
            self.y += (dy / dist) * ENEMY_SPEED
            
            # Calculate angle in degrees (pointing toward player)
            # atan2(dy, dx) returns angle in radians
            # We subtract 90 because sprite points north, not east
            self.angle = math.degrees(math.atan2(-dy, dx)) - 90
            
    def take_damage(self, damage):
        """Apply damage.  Returns True if enemy died."""
        self.health -= damage
        return self.health <= 0
    
    def collides_with_player(self, player):
        """
        Check if enemy is touching the player.
        
        Uses circle-circle collision: 
        Two circles collide if distance between centers < sum of radii
        """
        dx = self.x - player.x
        dy = self.y - player.y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < (self.size + player.size)
    
    def draw(self, screen):
        """
        Draw enemy as a rotated sprite pointing toward player with health bar.
        Uses one of 8 random sprite variants.
        """
        # Load the enemy sprite image (one of 8 variants)
        image_path = f"sprites/enemy/enemy_{self.sprite_variant}.png"
        try:
            image = pygame.image.load(image_path)
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            return
        
        # Rotate image based on angle toward player
        rotated_image = pygame.transform.rotate(image, self.angle)
        
        # Get the rect for the rotated image and center it on the enemy position
        image_rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        
        # Draw the rotated image
        screen.blit(rotated_image, image_rect)
        
        # Draw health bar
        bar_width = 30
        bar_height = 4
        health_ratio = self.health / ENEMY_HEALTH
        pygame.draw.rect(screen, RED,
                        (self.x - bar_width // 2, self.y - self.size - 10, 
                         bar_width, bar_height))
        pygame.draw.rect(screen, GREEN,
                        (self.x - bar_width // 2, self.y - self.size - 10,
                         int(bar_width * health_ratio), bar_height))


# =============================================================================
# SPAWNER CLASS
# =============================================================================
class Spawner:
    """
    Enemy spawner - the main objective. 
    
    Spawners: 
    - Periodically create new enemies
    - Must be destroyed to progress to the next phase
    - Have limited active enemies at once
    """
    
    def __init__(self, x, y, spawner_id):
        """
        Create a spawner. 
        
        Args:
            x, y: Position (center of the spawner)
            spawner_id:  Unique ID for this spawner
        """
        self.x = x
        self.y = y
        self.health = SPAWNER_HEALTH
        self.size = SPAWNER_SIZE
        self.spawn_timer = SPAWN_INTERVAL  # Countdown to next spawn
        self.spawner_id = spawner_id
        self.active_enemies = 0  # How many enemies from this spawner are alive
        self.animation_frame = 0  # Current frame (0-6, cycles through 7 frames)
        self.animation_counter = 0  # Counter to control animation speed
        
    def update(self):
        """
        Update spawner.  Returns True if should spawn an enemy.
        
        Decrements timer each frame. When timer hits 0:
        - Reset timer
        - Return True (signal to spawn enemy)
        
        Only spawns if under the enemy limit. 
        Also updates animation frame.
        """
        self.spawn_timer -= 1
        
        # Update animation (cycle through frames)
        self.animation_counter += 1
        if self.animation_counter >= SPAWNER_ANIMATION_SPEED:  # Adjust speed as needed
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 7  # Cycle 0-6
        
        if self.spawn_timer <= 0 and self.active_enemies < MAX_ENEMIES_PER_SPAWNER:
            self.spawn_timer = SPAWN_INTERVAL
            return True
        return False
    
    def take_damage(self, damage):
        """Apply damage.  Returns True if spawner was destroyed."""
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        """Draw spawner as an animated portal sprite with health bar."""
        # Load the current animation frame
        image_path = f"sprites/spawner/portal1_frame_{self.animation_frame + 1}.png"
        try:
            image = pygame.image.load(image_path)
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            return
        
        # Get the rect for the image and center it on the spawner position
        image_rect = image.get_rect(center=(int(self.x), int(self.y)))
        
        # Draw the animated sprite
        screen.blit(image, image_rect)
        
        # Health bar
        bar_width = 50
        bar_height = 6
        health_ratio = self.health / SPAWNER_HEALTH
        pygame.draw.rect(screen, RED,
                        (self.x - bar_width // 2, self.y - self.size - 15, 
                         bar_width, bar_height))
        pygame.draw.rect(screen, GREEN,
                        (self.x - bar_width // 2, self.y - self.size - 15,
                         int(bar_width * health_ratio), bar_height))


# =============================================================================
# PROJECTILE CLASS
# =============================================================================
class Projectile:
    """
    Player's bullet/projectile.
    
    Projectiles: 
    - Travel in a straight line
    - Damage enemies and spawners on contact
    - Are removed when hitting something or leaving screen
    """
    
    def __init__(self, x, y, angle):
        """
        Create a projectile.
        
        Args:
            x, y: Starting position (usually at player's front)
            angle: Direction of travel in degrees
        """
        self. x = x
        self.y = y
        self.angle = angle
        self.size = PROJECTILE_SIZE
        
        # Calculate velocity from angle
        rad = math.radians(angle)
        self.vx = math.cos(rad) * PROJECTILE_SPEED
        self.vy = -math.sin(rad) * PROJECTILE_SPEED
        
    def update(self):
        """
        Move projectile.  Returns True if out of bounds.
        
        Projectiles move in a straight line at constant speed.
        """
        self.x += self.vx
        self.y += self.vy
        
        # Check if outside screen (should be removed)
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
    
    def collides_with(self, entity):
        """Check collision with any entity (enemy or spawner)."""
        dx = self.x - entity.x
        dy = self.y - entity.y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < (self.size + entity.size)
    
    def draw(self, screen):
        """Draw projectile as a yellow circle."""
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)