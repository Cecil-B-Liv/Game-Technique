"""Game entity classes:  Player, Enemy, Spawner, Projectile."""

import pygame
import math
import numpy as np
from game.constants import *


class Player: 
    """The player-controlled ship."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0  # velocity x
        self.vy = 0.0  # velocity y
        self.angle = 0.0  # facing direction in degrees (0 = right)
        self.health = PLAYER_MAX_HEALTH
        self.shoot_cooldown = 0
        self.size = PLAYER_SIZE
        
    def reset(self, x, y):
        """Reset player to initial state."""
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.health = PLAYER_MAX_HEALTH
        self. shoot_cooldown = 0
        
    def move_directional(self, dx, dy):
        """Direct movement control (Control Style 2)."""
        self.vx = dx * PLAYER_SPEED
        self.vy = dy * PLAYER_SPEED
        self.x += self.vx
        self.y += self.vy
        # Update angle to face movement direction
        if dx != 0 or dy != 0:
            self.angle = math.degrees(math.atan2(-dy, dx))
        self._clamp_position()
        
    def rotate(self, direction):
        """Rotate player (Control Style 1). direction: -1=left, 1=right"""
        self.angle += direction * PLAYER_ROTATION_SPEED
        self. angle %= 360
        
    def thrust(self):
        """Move forward in facing direction (Control Style 1)."""
        rad = math.radians(self. angle)
        self.vx = math.cos(rad) * PLAYER_SPEED
        self.vy = -math.sin(rad) * PLAYER_SPEED  # negative because y increases downward
        self.x += self.vx
        self.y += self. vy
        self._clamp_position()
        
    def _clamp_position(self):
        """Keep player within screen bounds."""
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
        
    def can_shoot(self):
        """Check if player can shoot."""
        return self.shoot_cooldown <= 0
    
    def shoot(self):
        """Create a projectile.  Returns Projectile or None."""
        if self.can_shoot():
            self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
            rad = math.radians(self. angle)
            # Spawn projectile at front of player
            px = self.x + math.cos(rad) * self.size
            py = self. y - math.sin(rad) * self.size
            return Projectile(px, py, self.angle)
        return None
    
    def update(self):
        """Update player state each frame."""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        # Apply friction when not thrusting
        self.vx *= 0.95
        self.vy *= 0.95
            
    def take_damage(self, damage):
        """Apply damage to player."""
        self. health -= damage
        return self.health <= 0  # Returns True if dead
    
    def draw(self, screen):
        """Draw player as a triangle pointing in facing direction."""
        rad = math.radians(self. angle)
        # Triangle points
        front = (self.x + math.cos(rad) * self.size,
                 self.y - math.sin(rad) * self.size)
        back_left = (self.x + math.cos(rad + 2.5) * self.size * 0.7,
                     self.y - math.sin(rad + 2.5) * self.size * 0.7)
        back_right = (self.x + math.cos(rad - 2.5) * self.size * 0.7,
                      self.y - math. sin(rad - 2.5) * self.size * 0.7)
        pygame.draw.polygon(screen, BLUE, [front, back_left, back_right])
        # Health bar above player
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / PLAYER_MAX_HEALTH
        pygame.draw.rect(screen, RED, 
                        (self.x - bar_width//2, self. y - self.size - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN,
                        (self.x - bar_width//2, self. y - self.size - 15, 
                         int(bar_width * health_ratio), bar_height))


class Enemy:
    """Enemy that moves toward the player."""
    
    def __init__(self, x, y, spawner_id):
        self.x = x
        self.y = y
        self.health = ENEMY_HEALTH
        self.size = ENEMY_SIZE
        self.spawner_id = spawner_id  # Track which spawner created this enemy
        
    def update(self, player_x, player_y):
        """Move toward player."""
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.x += (dx / dist) * ENEMY_SPEED
            self.y += (dy / dist) * ENEMY_SPEED
            
    def take_damage(self, damage):
        """Apply damage.  Returns True if dead."""
        self.health -= damage
        return self.health <= 0
    
    def collides_with_player(self, player):
        """Check collision with player."""
        dx = self.x - player.x
        dy = self.y - player. y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < (self.size + player.size)
    
    def draw(self, screen):
        """Draw enemy as red circle."""
        pygame.draw. circle(screen, RED, (int(self.x), int(self.y)), self.size)
        # Health bar
        bar_width = 30
        bar_height = 4
        health_ratio = self. health / ENEMY_HEALTH
        pygame.draw.rect(screen, RED,
                        (self.x - bar_width//2, self.y - self.size - 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN,
                        (self.x - bar_width//2, self.y - self.size - 10,
                         int(bar_width * health_ratio), bar_height))


class Spawner:
    """Enemy spawner - destroy all to advance phase."""
    
    def __init__(self, x, y, spawner_id):
        self.x = x
        self.y = y
        self.health = SPAWNER_HEALTH
        self.size = SPAWNER_SIZE
        self.spawn_timer = SPAWN_INTERVAL
        self. spawner_id = spawner_id
        self.active_enemies = 0  # Track how many enemies from this spawner are alive
        
    def update(self):
        """Update spawn timer.  Returns True if should spawn enemy."""
        self.spawn_timer -= 1
        if self.spawn_timer <= 0 and self.active_enemies < MAX_ENEMIES_PER_SPAWNER:
            self.spawn_timer = SPAWN_INTERVAL
            return True
        return False
    
    def take_damage(self, damage):
        """Apply damage.  Returns True if destroyed."""
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        """Draw spawner as purple square."""
        rect = pygame.Rect(self. x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)
        pygame.draw.rect(screen, PURPLE, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)  # Border
        # Health bar
        bar_width = 50
        bar_height = 6
        health_ratio = self. health / SPAWNER_HEALTH
        pygame.draw.rect(screen, RED,
                        (self.x - bar_width//2, self.y - self.size - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN,
                        (self.x - bar_width//2, self.y - self.size - 15,
                         int(bar_width * health_ratio), bar_height))


class Projectile:
    """Player projectile."""
    
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.size = PROJECTILE_SIZE
        rad = math.radians(angle)
        self.vx = math.cos(rad) * PROJECTILE_SPEED
        self. vy = -math.sin(rad) * PROJECTILE_SPEED
        
    def update(self):
        """Move projectile.  Returns True if out of bounds."""
        self.x += self.vx
        self.y += self.vy
        # Check if out of screen
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
    
    def collides_with(self, entity):
        """Check collision with an entity."""
        dx = self. x - entity.x
        dy = self.y - entity.y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < (self. size + entity.size)
    
    def draw(self, screen):
        """Draw projectile as yellow circle."""
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)