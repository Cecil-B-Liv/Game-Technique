"""Main arena game logic."""

import pygame
import math
import random
import numpy as np
from game.constants import *
from game.entities import Player, Enemy, Spawner, Projectile


class Arena:
    """The main game arena."""
    
    def __init__(self, render_mode=False):
        self.render_mode = render_mode
        if render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("RL Arena")
            self.clock = pygame.time. Clock()
            self.font = pygame.font. Font(None, 36)
        else:
            self.screen = None
            
        self.player = None
        self.enemies = []
        self.spawners = []
        self.projectiles = []
        self.current_phase = 1
        self.step_count = 0
        self.score = 0
        
    def reset(self):
        """Reset the arena to initial state."""
        # Reset player at center
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self. projectiles = []
        self.current_phase = 1
        self.step_count = 0
        self.score = 0
        
        # Create initial spawners
        self._create_spawners(INITIAL_SPAWNERS)
        
        return self._get_observation()
    
    def _create_spawners(self, count):
        """Create spawners at random positions away from player."""
        self.spawners = []
        for i in range(count):
            while True:
                x = random. randint(SPAWNER_SIZE + 50, SCREEN_WIDTH - SPAWNER_SIZE - 50)
                y = random.randint(SPAWNER_SIZE + 50, SCREEN_HEIGHT - SPAWNER_SIZE - 50)
                # Ensure spawner is not too close to player
                dx = x - self.player.x
                dy = y - self. player.y
                if math.sqrt(dx*dx + dy*dy) > 200:
                    self.spawners.append(Spawner(x, y, i))
                    break
                    
    def _get_observation(self):
        """
        Create observation vector for the agent.
        
        Contains:
        - Player position (x, y) normalized to [0, 1]
        - Player velocity (vx, vy) normalized
        - Player angle normalized to [0, 1]
        - Player health normalized to [0, 1]
        - Distance and direction to nearest enemy (or default if none)
        - Distance and direction to nearest spawner (or default if none)
        - Current phase normalized
        - Number of enemies normalized
        """
        obs = []
        
        # Player position (normalized)
        obs.append(self.player.x / SCREEN_WIDTH)
        obs.append(self.player.y / SCREEN_HEIGHT)
        
        # Player velocity (normalized by max speed)
        obs.append(self.player.vx / PLAYER_SPEED)
        obs.append(self.player.vy / PLAYER_SPEED)
        
        # Player angle (normalized to [0, 1])
        obs.append(self.player.angle / 360.0)
        
        # Player health (normalized)
        obs.append(self. player.health / PLAYER_MAX_HEALTH)
        
        # Nearest enemy info
        if self.enemies:
            nearest_enemy = min(self.enemies, 
                               key=lambda e: (e.x - self.player. x)**2 + (e.y - self.player.y)**2)
            dx = nearest_enemy.x - self.player.x
            dy = nearest_enemy.y - self. player.y
            dist = math.sqrt(dx*dx + dy*dy)
            # Normalized distance (max possible is diagonal of screen)
            max_dist = math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)
            obs.append(dist / max_dist)
            # Relative angle to enemy
            angle_to_enemy = math.degrees(math.atan2(-dy, dx))
            relative_angle = (angle_to_enemy - self. player.angle) % 360
            obs.append(relative_angle / 360.0)
        else:
            obs.append(1.0)  # No enemy = max distance
            obs.append(0.0)  # Default angle
            
        # Nearest spawner info
        if self.spawners:
            nearest_spawner = min(self.spawners,
                                 key=lambda s: (s.x - self. player.x)**2 + (s.y - self.player. y)**2)
            dx = nearest_spawner.x - self.player.x
            dy = nearest_spawner.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            max_dist = math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)
            obs.append(dist / max_dist)
            angle_to_spawner = math. degrees(math.atan2(-dy, dx))
            relative_angle = (angle_to_spawner - self.player.angle) % 360
            obs.append(relative_angle / 360.0)
        else:
            obs.append(1.0)
            obs.append(0.0)
            
        # Current phase (normalized)
        obs.append(self.current_phase / MAX_PHASES)
        
        # Number of enemies (normalized, assume max ~20)
        obs.append(min(len(self.enemies) / 20.0, 1.0))
        
        return np.array(obs, dtype=np.float32)
    
    def step_rotation(self, action):
        """
        Step with rotation control scheme.
        Actions: 0=nothing, 1=thrust, 2=rotate_left, 3=rotate_right, 4=shoot
        """
        reward = 0.0
        
        # Apply action
        if action == 1:  # Thrust
            self. player.thrust()
        elif action == 2:  # Rotate left
            self.player.rotate(1)
        elif action == 3:  # Rotate right
            self.player.rotate(-1)
        elif action == 4:  # Shoot
            projectile = self.player.shoot()
            if projectile:
                self.projectiles.append(projectile)
                
        return self._common_step(reward)
    
    def step_directional(self, action):
        """
        Step with directional control scheme.
        Actions: 0=nothing, 1=up, 2=down, 3=left, 4=right, 5=shoot
        """
        reward = 0.0
        
        # Apply movement
        dx, dy = 0, 0
        if action == 1:  # Up
            dy = -1
        elif action == 2:  # Down
            dy = 1
        elif action == 3:  # Left
            dx = -1
        elif action == 4:  # Right
            dx = 1
        elif action == 5:  # Shoot
            projectile = self.player. shoot()
            if projectile: 
                self.projectiles.append(projectile)
                
        if dx != 0 or dy != 0:
            self.player.move_directional(dx, dy)
            
        return self._common_step(reward)
    
    def _common_step(self, reward):
        """Common step logic for both control schemes."""
        self.step_count += 1
        self.player.update()
        
        # Update spawners and spawn enemies
        for spawner in self.spawners:
            if spawner.update():
                # Spawn enemy near spawner
                angle = random.uniform(0, 2 * math.pi)
                ex = spawner.x + math. cos(angle) * (spawner.size + 20)
                ey = spawner.y + math.sin(angle) * (spawner.size + 20)
                self.enemies.append(Enemy(ex, ey, spawner.spawner_id))
                spawner.active_enemies += 1
                
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player.x, self. player.y)
            # Check collision with player
            if enemy. collides_with_player(self.player):
                if self.player.take_damage(ENEMY_DAMAGE):
                    # Player died
                    reward -= 100.0  # Strong negative reward for death
                    return self._get_observation(), reward, True, {"score": self.score}
                else:
                    reward -= 10.0  # Negative reward for taking damage
                # Remove enemy that collided
                self.enemies.remove(enemy)
                # Update spawner's active enemy count
                for spawner in self.spawners:
                    if spawner.spawner_id == enemy.spawner_id:
                        spawner.active_enemies -= 1
                        break
                        
        # Update projectiles
        projectiles_to_remove = []
        for projectile in self.projectiles:
            if projectile.update():  # Out of bounds
                projectiles_to_remove.append(projectile)
                continue
                
            # Check collision with enemies
            for enemy in self. enemies[: ]: 
                if projectile.collides_with(enemy):
                    if enemy.take_damage(PROJECTILE_DAMAGE):
                        self.enemies.remove(enemy)
                        reward += 10.0  # Reward for killing enemy
                        self.score += 10
                        # Update spawner count
                        for spawner in self.spawners:
                            if spawner.spawner_id == enemy.spawner_id:
                                spawner.active_enemies -= 1
                                break
                    projectiles_to_remove.append(projectile)
                    break
                    
            # Check collision with spawners
            for spawner in self.spawners[:]:
                if projectile. collides_with(spawner):
                    if spawner.take_damage(PROJECTILE_DAMAGE):
                        self.spawners.remove(spawner)
                        reward += 50.0  # Larger reward for destroying spawner
                        self.score += 50
                    if projectile not in projectiles_to_remove:
                        projectiles_to_remove. append(projectile)
                    break
                    
        # Remove spent projectiles
        for p in projectiles_to_remove: 
            if p in self.projectiles:
                self.projectiles.remove(p)
                
        # Check phase progression
        if len(self.spawners) == 0:
            if self.current_phase < MAX_PHASES:
                self.current_phase += 1
                reward += 100.0  # Big reward for phase completion
                self.score += 100
                # Create new spawners for next phase
                num_spawners = INITIAL_SPAWNERS + self. current_phase * SPAWNERS_PER_PHASE
                self._create_spawners(num_spawners)
            else:
                # Won the game! 
                reward += 500.0
                return self._get_observation(), reward, True, {"score": self.score, "won": True}
                
        # Small survival reward (optional shaping)
        reward += 0.01
        
        # Check max steps
        done = self.step_count >= MAX_STEPS
        if done:
            reward -= 20.0  # Penalty for timeout
            
        return self._get_observation(), reward, done, {"score": self.score}
    
    def render(self):
        """Render the game."""
        if not self.render_mode:
            return
            
        self.screen.fill(BLACK)
        
        # Draw all entities
        for spawner in self.spawners:
            spawner.draw(self. screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        self.player.draw(self.screen)
        
        # Draw HUD
        phase_text = self.font.render(f"Phase: {self. current_phase}", True, WHITE)
        score_text = self.font.render(f"Score: {self. score}", True, WHITE)
        health_text = self.font.render(f"Health: {self. player.health}", True, WHITE)
        enemies_text = self.font.render(f"Enemies: {len(self.enemies)}", True, WHITE)
        spawners_text = self.font.render(f"Spawners: {len(self.spawners)}", True, WHITE)
        
        self.screen.blit(phase_text, (10, 10))
        self.screen. blit(score_text, (10, 40))
        self.screen.blit(health_text, (10, 70))
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 150, 10))
        self.screen. blit(spawners_text, (SCREEN_WIDTH - 150, 40))
        
        pygame.display.flip()
        self.clock.tick(FPS)
        
    def close(self):
        """Clean up pygame."""
        if self.render_mode:
            pygame.quit()