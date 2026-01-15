"""
Main arena game logic
"""

import pygame
import math
import random
import numpy as np
from game.constants import *
from game.entities import Player, Enemy, Spawner, Projectile


class Arena:
    """The main game arena with improved reward shaping."""

    def __init__(self, render_mode=False):
        self.render_mode = render_mode

        if render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("RL Arena")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
        else:
            self.screen = None

        self.player = None
        self.enemies = []
        self.spawners = []
        self.projectiles = []
        self.current_phase = 1
        self.step_count = 0
        self.score = 0

        # Track previous state for reward shaping
        self.prev_spawner_count = 0
        self.prev_enemy_count = 0
        self.prev_health = PLAYER_MAX_HEALTH
        self.prev_dist_to_spawner = 0
        self.shots_fired = 0
        self.shots_hit = 0

    def reset(self):
        """Reset the arena to initial state."""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.projectiles = []
        self.current_phase = 1
        self.step_count = 0
        self.score = 0

        # Reset tracking
        self.prev_health = PLAYER_MAX_HEALTH
        self.shots_fired = 0
        self.shots_hit = 0

        self._create_spawners(INITIAL_SPAWNERS)

        self.prev_spawner_count = len(self.spawners)
        self.prev_enemy_count = len(self.enemies)
        self.prev_dist_to_spawner = self._get_nearest_spawner_dist()

        return self._get_observation()

    def _create_spawners(self, count):
        """Create spawners at random positions away from player."""
        self.spawners = []
        for i in range(count):
            attempts = 0
            while attempts < 100:
                x = random.randint(SPAWNER_SIZE + 50,
                                   SCREEN_WIDTH - SPAWNER_SIZE - 50)
                y = random.randint(SPAWNER_SIZE + 50,
                                   SCREEN_HEIGHT - SPAWNER_SIZE - 50)
                dx = x - self.player.x
                dy = y - self.player. y
                if math.sqrt(dx*dx + dy*dy) > 200:
                    self.spawners.append(Spawner(x, y, i))
                    break
                attempts += 1

    def _get_nearest_spawner_dist(self):
        """Get distance to nearest spawner."""
        if not self.spawners:
            return 0
        nearest = min(
            self.spawners,
            key=lambda s: (s.x - self.player. x)**2 + (s.y - self.player.y)**2
        )
        dx = nearest.x - self.player.x
        dy = nearest.y - self.player.y
        return math.sqrt(dx*dx + dy*dy)

    def _get_nearest_enemy_dist(self):
        """Get distance to nearest enemy."""
        if not self.enemies:
            return float('inf')
        nearest = min(
            self.enemies,
            key=lambda e: (e.x - self.player.x)**2 + (e.y - self.player.y)**2
        )
        dx = nearest.x - self.player.x
        dy = nearest.y - self.player.y
        return math.sqrt(dx*dx + dy*dy)

    def _get_observation(self):
        """Create observation vector for the RL agent."""
        obs = []

        # Player position (normalized)
        obs.append(self.player.x / SCREEN_WIDTH)
        obs.append(self.player.y / SCREEN_HEIGHT)

        # Player velocity (normalized)
        obs.append(np.clip(self.player.vx / PLAYER_SPEED, -1, 1))
        obs.append(np.clip(self.player.vy / PLAYER_SPEED, -1, 1))

        # Player angle (sin/cos)
        angle_rad = math.radians(self.player.angle)
        obs.append(math.sin(angle_rad))
        obs.append(math.cos(angle_rad))

        # Player health (normalized)
        obs.append(self.player.health / PLAYER_MAX_HEALTH)

        # Can shoot
        obs.append(1.0 if self.player.can_shoot() else 0.0)

        # Nearest enemy info
        max_dist = math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)

        if self.enemies:
            nearest_enemy = min(
                self.enemies,
                key=lambda e: (e.x - self.player.x)**2 +
                (e.y - self.player.y)**2
            )
            dx = nearest_enemy.x - self.player.x
            dy = nearest_enemy.y - self. player.y
            dist = math.sqrt(dx*dx + dy*dy)
            obs.append(dist / max_dist)
            angle_to_enemy = math.atan2(-dy, dx)
            relative_angle = angle_to_enemy - angle_rad
            obs.append(math.sin(relative_angle))
            obs.append(math.cos(relative_angle))
        else:
            obs.append(1.0)
            obs.append(0.0)
            obs.append(1.0)

        # Nearest spawner info
        if self.spawners:
            nearest_spawner = min(
                self.spawners,
                key=lambda s: (s.x - self.player.x)**2 +
                (s.y - self.player.y)**2
            )
            dx = nearest_spawner.x - self. player.x
            dy = nearest_spawner.y - self. player.y
            dist = math.sqrt(dx*dx + dy*dy)
            obs.append(dist / max_dist)
            angle_to_spawner = math.atan2(-dy, dx)
            relative_angle = angle_to_spawner - angle_rad
            obs.append(math.sin(relative_angle))
            obs.append(math. cos(relative_angle))
        else:
            obs.append(1.0)
            obs.append(0.0)
            obs.append(1.0)

        # Current phase (normalized)
        obs.append(self.current_phase / MAX_PHASES)

        # Number of enemies (normalized)
        obs.append(min(len(self.enemies) / 10.0, 1.0))

        # Number of spawners remaining (helps agent know progress)
        obs.append(len(self.spawners) / (INITIAL_SPAWNERS + MAX_PHASES))

        # Accuracy hint (if shooting is effective)
        accuracy = self.shots_hit / max(self.shots_fired, 1)
        obs.append(accuracy)

        return np.array(obs, dtype=np.float32)

    def step_directional(self, action):
        """Execute one step with directional controls."""
        reward = 0.0

        dx, dy = 0, 0
        if action == 1:
            dy = -1
        elif action == 2:
            dy = 1
        elif action == 3:
            dx = -1
        elif action == 4:
            dx = 1
        elif action == 5:
            projectile = self. player.shoot()
            if projectile:
                self.projectiles. append(projectile)
                self.shots_fired += 1

        if dx != 0 or dy != 0:
            self.player.move_directional(dx, dy)

        return self._common_step(reward)

    def step_rotation(self, action):
        """Execute one step with rotation controls."""
        reward = 0.0

        if action == 1:
            self.player.thrust()
        elif action == 2:
            self.player.rotate(1)
        elif action == 3:
            self.player. rotate(-1)
        elif action == 4:
            projectile = self.player.shoot()
            if projectile:
                self.projectiles.append(projectile)
                self.shots_fired += 1

        return self._common_step(reward)

    def _common_step(self, reward):
        """Common game logic with IMPROVED reward function."""
        self.step_count += 1
        self.player.update()

        # =====================================================================
        # UPDATE SPAWNERS
        # =====================================================================
        for spawner in self.spawners:
            if spawner.update():
                angle = random.uniform(0, 2 * math.pi)
                ex = spawner.x + math. cos(angle) * (spawner.size + 20)
                ey = spawner.y + math.sin(angle) * (spawner.size + 20)
                self.enemies.append(Enemy(ex, ey, spawner.spawner_id))
                spawner.active_enemies += 1

        # =====================================================================
        # UPDATE ENEMIES
        # =====================================================================
        enemies_to_remove = []
        for enemy in self.enemies:
            enemy.update(self.player. x, self.player.y)

            if enemy.collides_with_player(self.player):
                damage = ENEMY_DAMAGE
                if self.player.take_damage(damage):
                    # === DEATH PENALTY ===
                    # Scale by how far we got (dying early is worse)
                    death_penalty = -200 - (self.current_phase * 50)
                    reward += death_penalty

                    return self._get_observation(), reward, True, {
                        "score": self.score,
                        "phase": self.current_phase,
                        "death":  True,
                        "steps": self.step_count
                    }
                else:
                    # === DAMAGE PENALTY ===
                    # Proportional to damage taken
                    reward -= 15.0

                enemies_to_remove.append(enemy)
                for spawner in self.spawners:
                    if spawner.spawner_id == enemy.spawner_id:
                        spawner.active_enemies -= 1
                        break

        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self. enemies.remove(enemy)

        # =====================================================================
        # UPDATE PROJECTILES
        # =====================================================================
        projectiles_to_remove = []

        for projectile in self.projectiles:
            if projectile.update():
                projectiles_to_remove.append(projectile)
                continue

            # Check enemy collisions
            for enemy in self.enemies[:]:
                if projectile.collides_with(enemy):
                    self.shots_hit += 1

                    if enemy.take_damage(PROJECTILE_DAMAGE):
                        self.enemies.remove(enemy)

                        # === ENEMY KILL REWARD ===
                        # Higher reward if many enemies (crowd control)
                        base_reward = 20.0
                        if len(self.enemies) > 5:
                            base_reward += 10.0  # Bonus for thinning the herd
                        reward += base_reward
                        self.score += 10

                        for spawner in self.spawners:
                            if spawner.spawner_id == enemy.spawner_id:
                                spawner.active_enemies -= 1
                                break
                    else:
                        # === DAMAGE REWARD ===
                        # Small reward for hitting but not killing
                        reward += 3.0

                    projectiles_to_remove.append(projectile)
                    break

            # Check spawner collisions
            if projectile not in projectiles_to_remove:
                for spawner in self.spawners[:]:
                    if projectile.collides_with(spawner):
                        self.shots_hit += 1

                        if spawner.take_damage(PROJECTILE_DAMAGE):
                            self.spawners.remove(spawner)

                            # === SPAWNER KILL REWARD ===
                            # BIG reward - this is the main objective!
                            # Scale with phase (harder phases = more reward)
                            spawner_reward = 100.0 + \
                                (self.current_phase * 25.0)
                            reward += spawner_reward
                            self. score += 50
                        else:
                            # === SPAWNER DAMAGE REWARD ===
                            # Encourage focusing fire on spawners
                            reward += 8.0

                        projectiles_to_remove.append(projectile)
                        break

        for p in projectiles_to_remove:
            if p in self.projectiles:
                self.projectiles.remove(p)

        # =====================================================================
        # PHASE PROGRESSION
        # =====================================================================
        if len(self.spawners) == 0:
            if self.current_phase < MAX_PHASES:
                self.current_phase += 1

                # === PHASE COMPLETE REWARD ===
                # Massive reward that scales with difficulty
                phase_reward = 200.0 + (self.current_phase * 75.0)
                reward += phase_reward
                self.score += 100

                # Create new spawners
                num_spawners = INITIAL_SPAWNERS + self. current_phase - 1
                self._create_spawners(num_spawners)
                self.prev_spawner_count = len(self.spawners)
            else:
                # === GAME WIN REWARD ===
                reward += 1000.0
                return self._get_observation(), reward, True, {
                    "score": self.score,
                    "phase": self.current_phase,
                    "won": True,
                    "steps": self.step_count
                }

        # =====================================================================
        # SHAPING REWARDS (guide learning without changing optimal policy)
        # =====================================================================

        # --- Approach Spawner Reward ---
        # Encourage moving toward spawners (the objective)
        current_dist_to_spawner = self._get_nearest_spawner_dist()
        if self.spawners:
            # Reward for getting closer, penalty for moving away
            dist_diff = self.prev_dist_to_spawner - current_dist_to_spawner
            approach_reward = dist_diff * 0.02  # Small but consistent
            reward += approach_reward
            self.prev_dist_to_spawner = current_dist_to_spawner

        # --- Danger Awareness ---
        # Penalty for being too close to enemies (encourages dodging)
        nearest_enemy_dist = self._get_nearest_enemy_dist()
        if nearest_enemy_dist < 80:  # Danger zone
            danger_penalty = -0.5 * (1 - nearest_enemy_dist / 80)
            reward += danger_penalty

        # --- Survival Reward ---
        # Small reward for staying alive (but not too much - we want action!)
        reward += 0.05

        # --- Health Conservation Bonus ---
        # Reward for maintaining health
        if self.player.health == PLAYER_MAX_HEALTH:
            reward += 0.02  # Small bonus for perfect health

        # --- Progress Tracking ---
        # Penalty for letting too many enemies accumulate
        if len(self. enemies) > 8:
            reward -= 0.1 * (len(self.enemies) - 8)

        # =====================================================================
        # TIMEOUT
        # =====================================================================
        done = self.step_count >= MAX_STEPS
        if done:
            # Penalty scaled by how little progress was made
            timeout_penalty = -50 - \
                (50 * (1 - self.current_phase / MAX_PHASES))
            reward += timeout_penalty

        return self._get_observation(), reward, done, {
            "score": self.score,
            "phase": self.current_phase,
            "enemies": len(self.enemies),
            "spawners": len(self.spawners),
            "steps": self.step_count,
            "health": self.player.health
        }

    def render(self):
        """Render the game."""
        if not self.render_mode:
            return
        
        image_path = f"sprites/background/background.jpg"
        try:
            image = pygame.image.load(image_path)
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            return

        # Calculate scale to fit screen (scale to width while maintaining aspect ratio)
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Scale based on width to ensure full coverage
        scale_factor = screen_width / image.get_width()
        new_width = screen_width
        new_height = int(image.get_height() * scale_factor)
        
        # If height is still too small, scale based on height instead
        if new_height < screen_height:
            scale_factor = screen_height / image.get_height()
            new_height = screen_height
            new_width = int(image.get_width() * scale_factor)
        
        # Scale the image
        scaled_image = pygame.transform.scale(image, (new_width, new_height))
        
        # Center it on the screen
        image_rect = scaled_image.get_rect(center=(screen_width // 2, screen_height // 2))
        
        self.screen.blit(scaled_image, image_rect)

        for spawner in self.spawners:
            spawner.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for projectile in self. projectiles:
            projectile. draw(self.screen)
        self.player.draw(self.screen)

        # HUD
        phase_text = self. font.render(
            f"Phase: {self.current_phase}", True, WHITE)
        score_text = self.font.render(f"Score: {self. score}", True, WHITE)
        health_text = self.font. render(
            f"Health: {self.player.health}", True, WHITE)
        enemies_text = self.font.render(
            f"Enemies: {len(self.enemies)}", True, WHITE)
        spawners_text = self.font.render(
            f"Spawners: {len(self.spawners)}", True, WHITE)
        step_text = self.font.render(f"Step: {self.step_count}", True, WHITE)
    

        self.screen.blit(phase_text, (10, 10))
        self.screen.blit(score_text, (10, 40))
        self.screen.blit(health_text, (10, 70))
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 150, 10))
        self.screen.blit(spawners_text, (SCREEN_WIDTH - 150, 40))
        self.screen.blit(step_text, (SCREEN_WIDTH - 150, 70))

        pygame. display.flip()
        self.clock.tick(FPS)

    def close(self):
        """Clean up pygame."""
        if self.render_mode:
            pygame.quit()
