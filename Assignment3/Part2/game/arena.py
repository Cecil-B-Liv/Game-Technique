"""
Main arena game logic. 

This file contains the Arena class which: 
- Manages all game entities (player, enemies, spawners, projectiles)
- Handles game physics and collisions
- Provides observations for the RL agent
- Calculates rewards

THIS IS THE MOST IMPORTANT FILE FOR RL TRAINING. 
"""

import pygame
import math
import random
import numpy as np
from game.constants import *
from game.entities import Player, Enemy, Spawner, Projectile


class Arena:
    """
    The main game arena. 

    This class is the "game engine" that: 
    1. Maintains game state (all entities, score, phase)
    2. Updates the game each step
    3. Detects collisions
    4. Provides observations to the RL agent
    5. Calculates rewards
    """

    def __init__(self, render_mode=False):
        """
        Initialize the arena.

        Args:
            render_mode: If True, create a Pygame window for visualization. 
                        Set to False during training for speed.
        """
        self.render_mode = render_mode

        # Only initialize Pygame graphics if rendering
        if render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame. display.set_caption("RL Arena")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
        else:
            self.screen = None

        # Game state (will be initialized in reset())
        self.player = None
        self.enemies = []
        self.spawners = []
        self.projectiles = []
        self.current_phase = 1
        self.step_count = 0
        self.score = 0

    def reset(self):
        """
        Reset the arena to initial state.

        Called at the start of each episode.
        Returns the initial observation.
        """
        # Create player at center of screen (Player code in entities.py)
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Clear all entities
        self.enemies = []
        self.projectiles = []

        # Reset counters
        self.current_phase = 1
        self.step_count = 0
        self.score = 0

        # Create initial spawners
        self._create_spawners(INITIAL_SPAWNERS)

        return self._get_observation()

    def _create_spawners(self, count):
        """
        Create spawners at random positions.

        Ensures spawners are: 
        - Not too close to screen edges
        - Not too close to the player
        """
        self.spawners = []
        for i in range(count):
            # Keep trying until we find a valid position
            attempts = 0
            while attempts < 100:  # Prevent infinite loop
                # Random position with margin from edges
                x = random.randint(SPAWNER_SIZE + 50,
                                   SCREEN_WIDTH - SPAWNER_SIZE - 50)
                y = random.randint(SPAWNER_SIZE + 50,
                                   SCREEN_HEIGHT - SPAWNER_SIZE - 50)

                # Check distance from player
                dx = x - self.player.x
                dy = y - self.player. y
                dist = math.sqrt(dx*dx + dy*dy)

                if dist > 200:  # At least 200 pixels from player
                    self.spawners.append(Spawner(x, y, i))
                    break
                attempts += 1

    def _get_observation(self):
        """
        Create observation vector for the RL agent.

        *** THIS IS CRITICAL FOR RL SUCCESS ***

        The observation must contain ALL information the agent needs to make decisions.
        Each value should be normalized (usually to [0,1] or [-1,1]) for better training.

        Current observation (16 values):
        [0]  player_x normalized
        [1]  player_y normalized
        [2]  player_vx normalized
        [3]  player_vy normalized
        [4]  player_angle normalized (sin component)
        [5]  player_angle normalized (cos component)
        [6]  player_health normalized
        [7]  can_shoot (0 or 1)
        [8]  nearest_enemy_distance normalized
        [9]  nearest_enemy_angle (sin)
        [10] nearest_enemy_angle (cos)
        [11] nearest_spawner_distance normalized
        [12] nearest_spawner_angle (sin)
        [13] nearest_spawner_angle (cos)
        [14] current_phase normalized
        [15] num_enemies normalized
        """
        obs = []

        # --- Player Position (normalized to [0, 1]) ---
        obs.append(self.player.x / SCREEN_WIDTH)
        obs.append(self.player.y / SCREEN_HEIGHT)

        # --- Player Velocity (normalized by max speed, gives [-1, 1]) ---
        obs.append(np.clip(self.player.vx / PLAYER_SPEED, -1, 1))
        obs.append(np. clip(self.player.vy / PLAYER_SPEED, -1, 1))

        # --- Player Angle (use sin/cos instead of raw angle) ---
        # This is important!  Raw angle has discontinuity at 0/360
        # sin/cos representation is continuous
        angle_rad = math.radians(self.player.angle)
        obs.append(math.sin(angle_rad))  # -1 to 1
        obs.append(math.cos(angle_rad))  # -1 to 1

        # --- Player Health (normalized to [0, 1]) ---
        obs.append(self.player.health / PLAYER_MAX_HEALTH)

        # --- Can Shoot (binary: 0 or 1) ---
        # This helps the agent know when shooting is possible
        obs.append(1.0 if self.player.can_shoot() else 0.0)

        # --- Nearest Enemy Info ---
        # Diagonal distance
        max_dist = math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)

        if self.enemies:
            # Find nearest enemy
            nearest_enemy = min(
                self.enemies,
                key=lambda e:  (e.x - self.player. x)**2 +
                (e.y - self.player.y)**2
            )

            # Distance (normalized)
            dx = nearest_enemy.x - self.player.x
            dy = nearest_enemy.y - self. player.y
            dist = math.sqrt(dx*dx + dy*dy)
            obs.append(dist / max_dist)

            # Relative angle to enemy (using sin/cos)
            # This tells the agent which direction to turn/move
            angle_to_enemy = math. atan2(-dy, dx)  # Radians
            relative_angle = angle_to_enemy - angle_rad
            obs.append(math.sin(relative_angle))
            obs.append(math.cos(relative_angle))
        else:
            # No enemies - use default values
            obs.append(1.0)   # Max distance (far away)
            obs.append(0.0)   # Neutral angle
            obs.append(1.0)

        # --- Nearest Spawner Info ---
        if self.spawners:
            nearest_spawner = min(
                self.spawners,
                key=lambda s: (s.x - self.player. x)**2 +
                (s.y - self.player.y)**2
            )

            dx = nearest_spawner.x - self.player.x
            dy = nearest_spawner.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            obs.append(dist / max_dist)

            angle_to_spawner = math. atan2(-dy, dx)
            relative_angle = angle_to_spawner - angle_rad
            obs.append(math.sin(relative_angle))
            obs.append(math.cos(relative_angle))
        else:
            obs.append(1.0)
            obs.append(0.0)
            obs.append(1.0)

        # --- Phase and Enemy Count ---
        obs.append(self.current_phase / MAX_PHASES)
        obs.append(min(len(self.enemies) / 10.0, 1.0))  # Normalize, cap at 10

        return np.array(obs, dtype=np.float32)

    def step_rotation(self, action):
        """
        Execute one step with rotation controls.

        Actions:
            0: No action (do nothing)
            1: Thrust forward
            2: Rotate left (counter-clockwise)
            3: Rotate right (clockwise)
            4: Shoot

        *** PROBLEM IDENTIFIED ***
        The agent can only do ONE action per step. This means it can't
        thrust AND shoot, or rotate AND shoot.  This makes learning hard.

        Args:
            action: Integer 0-4

        Returns:
            observation, reward, done, info
        """
        reward = 0.0

        # Apply the selected action
        if action == 1:    # Thrust forward
            self.player.thrust()
        elif action == 2:  # Rotate left
            self.player.rotate(1)
        elif action == 3:  # Rotate right
            self.player.rotate(-1)
        elif action == 4:  # Shoot
            projectile = self.player.shoot()
            if projectile:
                self.projectiles.append(projectile)
        # action == 0 does nothing

        return self._common_step(reward)

    def step_directional(self, action):
        """
        Execute one step with directional controls.

        Actions:
            0: No action
            1: Move up
            2: Move down
            3: Move left
            4: Move right
            5: Shoot

        Args:
            action: Integer 0-5

        Returns: 
            observation, reward, done, info
        """
        reward = 0.0

        # Determine movement direction
        dx, dy = 0, 0
        if action == 1:    # Up
            dy = -1
        elif action == 2:  # Down
            dy = 1
        elif action == 3:  # Left
            dx = -1
        elif action == 4:  # Right
            dx = 1
        elif action == 5:  # Shoot
            projectile = self.player.shoot()
            if projectile:
                self.projectiles.append(projectile)

        # Apply movement
        if dx != 0 or dy != 0:
            self.player.move_directional(dx, dy)

        return self._common_step(reward)

    def _common_step(self, reward):
        """
        Common game logic for both control schemes.

        This is called after the action is applied and handles:
        1. Updating all entities
        2. Spawning new enemies
        3. Collision detection
        4. Reward calculation
        5. Phase progression

        Args:
            reward: Initial reward (usually 0, may have action-based rewards)

        Returns:
            observation, reward, done, info
        """
        self.step_count += 1
        self.player.update()

        # Track events for reward calculation
        enemies_killed = 0
        spawners_destroyed = 0
        damage_taken = 0

        # =================================================================
        # UPDATE SPAWNERS - Spawn new enemies
        # =================================================================
        for spawner in self.spawners:
            if spawner.update():  # Returns True if should spawn
                # Spawn enemy at random position near spawner
                angle = random.uniform(0, 2 * math.pi)
                ex = spawner.x + math.cos(angle) * (spawner.size + 20)
                ey = spawner.y + math.sin(angle) * (spawner.size + 20)
                self.enemies.append(Enemy(ex, ey, spawner.spawner_id))
                spawner.active_enemies += 1

        # =================================================================
        # UPDATE ENEMIES - Move toward player, check collisions
        # =================================================================
        enemies_to_remove = []
        for enemy in self.enemies:
            enemy.update(self.player. x, self.player.y)

            # Check collision with player
            if enemy.collides_with_player(self.player):
                damage_taken += ENEMY_DAMAGE
                if self.player.take_damage(ENEMY_DAMAGE):
                    # Player died!
                    reward -= 100.0  # Large penalty for death
                    return self._get_observation(), reward, True, {
                        "score": self.score,
                        "phase": self.current_phase,
                        "death":  True
                    }
                else:
                    reward -= 10.0  # Penalty for taking damage

                # Remove enemy after collision
                enemies_to_remove.append(enemy)
                # Update spawner's count
                for spawner in self.spawners:
                    if spawner.spawner_id == enemy.spawner_id:
                        spawner.active_enemies -= 1
                        break

        # Remove collided enemies
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)

        # =================================================================
        # UPDATE PROJECTILES - Move, check collisions
        # =================================================================
        projectiles_to_remove = []

        for projectile in self.projectiles:
            # Move projectile
            if projectile.update():  # Returns True if out of bounds
                projectiles_to_remove.append(projectile)
                continue

            # Check collision with enemies
            # [: ] creates a copy to iterate safely
            for enemy in self.enemies[:]:
                if projectile.collides_with(enemy):
                    if enemy.take_damage(PROJECTILE_DAMAGE):
                        # Enemy killed!
                        self.enemies.remove(enemy)
                        enemies_killed += 1
                        reward += 15.0  # Reward for killing enemy
                        self.score += 10

                        # Update spawner count
                        for spawner in self.spawners:
                            if spawner.spawner_id == enemy.spawner_id:
                                spawner.active_enemies -= 1
                                break

                    projectiles_to_remove.append(projectile)
                    break  # Projectile can only hit one thing

            # Check collision with spawners
            if projectile not in projectiles_to_remove:
                for spawner in self.spawners[:]:
                    if projectile.collides_with(spawner):
                        if spawner.take_damage(PROJECTILE_DAMAGE):
                            # Spawner destroyed!
                            self.spawners.remove(spawner)
                            spawners_destroyed += 1
                            reward += 75.0  # Large reward for destroying spawner
                            self.score += 50

                        projectiles_to_remove.append(projectile)
                        break

        # Remove used projectiles
        for p in projectiles_to_remove:
            if p in self.projectiles:
                self.projectiles.remove(p)

        # =================================================================
        # PHASE PROGRESSION
        # =================================================================
        if len(self.spawners) == 0:
            if self.current_phase < MAX_PHASES:
                self.current_phase += 1
                reward += 150.0  # Big reward for completing phase
                self.score += 100

                # Create more spawners for next phase
                num_spawners = INITIAL_SPAWNERS + self.current_phase - 1
                self._create_spawners(num_spawners)
            else:
                # Won the game!
                reward += 500.0
                return self._get_observation(), reward, True, {
                    "score": self.score,
                    "phase": self.current_phase,
                    "won": True
                }

        # =================================================================
        # SHAPING REWARDS (help guide learning)
        # =================================================================

        # Small reward for surviving each step
        reward += 0.1

        # Reward for being close to spawners (encourages approach)
        if self.spawners:
            nearest_spawner = min(
                self.spawners,
                key=lambda s: (s.x - self.player. x)**2 +
                (s.y - self.player.y)**2
            )
            dx = nearest_spawner.x - self.player.x
            dy = nearest_spawner.y - self.player.y
            dist_to_spawner = math.sqrt(dx*dx + dy*dy)
            # Small reward for being close (max 0.5 when very close)
            reward += 0.5 * (1 - dist_to_spawner /
                             math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2))

        # Penalty for being too close to enemies (encourages dodging)
        if self.enemies:
            nearest_enemy = min(
                self.enemies,
                key=lambda e: (e.x - self.player.x)**2 +
                (e.y - self.player.y)**2
            )
            dx = nearest_enemy.x - self.player.x
            dy = nearest_enemy.y - self.player. y
            dist_to_enemy = math.sqrt(dx*dx + dy*dy)
            # Small penalty for being too close (within 100 pixels)
            if dist_to_enemy < 100:
                reward -= 0.3 * (1 - dist_to_enemy / 100)

        # =================================================================
        # CHECK TIMEOUT
        # =================================================================
        done = self.step_count >= MAX_STEPS
        if done:
            reward -= 30.0  # Penalty for timeout

        return self._get_observation(), reward, done, {
            "score": self.score,
            "phase": self.current_phase,
            "enemies_killed": enemies_killed,
            "spawners_destroyed": spawners_destroyed
        }

    def render(self):
        """
        Render the game visually.

        Only works if render_mode=True was set in __init__. 
        """
        if not self.render_mode:
            return

        # Clear screen
        self.screen.fill(BLACK)

        # Draw all entities (order matters for layering)
        for spawner in self.spawners:
            spawner.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        self.player.draw(self.screen)

        # Draw HUD (Heads-Up Display)
        phase_text = self.font.render(
            f"Phase: {self.current_phase}", True, WHITE)
        score_text = self.font.render(f"Score: {self. score}", True, WHITE)
        health_text = self.font.render(
            f"Health: {self. player.health}", True, WHITE)
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

        # Update display
        pygame.display.flip()

        # Control frame rate
        self.clock.tick(FPS)

    def close(self):
        """Clean up Pygame resources."""
        if self.render_mode:
            pygame.quit()
