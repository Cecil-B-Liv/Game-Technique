"""
Pygame renderer for GridWorld visualization
"""
import os

import pygame
from .environment import GridWorld
from .constants import *


class Renderer:
    """
    Renders GridWorld using Pygame.

    Features:
    - Grid visualization
    - Agent, apples, rocks, fire, monsters
    - HUD with episode info
    """

    def __init__(self, tile_size: int = 48, dual_mode: bool = False):
        """
        Initialize Pygame renderer.

        Args:
            tile_size: Size of each tile in pixels
            dual_mode: Whether to use split-screen dual mode
        """
        self.tile_size = tile_size
        self.grid_width = WIDTH_TILES * tile_size
        self.grid_height = HEIGHT_TILES * tile_size
        self.dual_mode = dual_mode

        self.height = self.grid_height + HUD_HEIGHT
        self.width = self.grid_width * 2 if dual_mode else self.grid_width

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        caption = "GridWorld - Dual Mode" if dual_mode else "GridWorld - Q-Learning"
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 36)

        # Path
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        # Still Assets
        self.menu_bg = None
        self.apple_img = None
        self.chest_close_img = None
        self.chest_open_img = None
        self.key_img = None

        # Animation
        self.agent_down_frames = []
        self.agent_down_frames_tick = 0

        self.fire_frames = []
        self.fire_frames_tick = 0

        self.monster_frames = []
        self.monster_frames_tick = 0

        # Load assets automatically
        self.load_assets()

    def load_assets(self):
        print("Load still img")
        self.load_still_img()

        print("Load animation")
        self.load_animation()

    def load_still_img(self):
        sprite_path = os.path.join(self.current_dir, "..", "sprites")
        menu_bg_path = os.path.join(sprite_path, "main_menu_bg.png")
        apple_path = os.path.join(sprite_path, "apple.png")
        chest_close_path = os.path.join(sprite_path, "chest_close.png")
        chest_open_path = os.path.join(sprite_path, "chest_open.png")
        key_path = os.path.join(sprite_path, "key.png")

        # Load menu img
        print("Load main menu img")
        if os.path.exists(menu_bg_path):
            img = pygame.image.load(menu_bg_path).convert()
            self.menu_bg = pygame.transform.scale(img, (self.width, self.height))
        else:
            print("Warning: main_menu_bg.png not found")

        # Load apple img
        print("Load apple img")
        if os.path.exists(apple_path):
            img = pygame.image.load(apple_path).convert_alpha()
            self.apple_img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
        else:
            print("Warning: apple.png not found")

        # Load chest close
        print("Load close chest img")
        if os.path.exists(chest_close_path):
            img = pygame.image.load(chest_close_path).convert_alpha()
            self.chest_close_img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
        else:
            print("Warning: chest_close.png not found")

        # Load chest open
        print("Load open chest img")
        if os.path.exists(chest_open_path):
            img = pygame.image.load(chest_open_path).convert_alpha()
            self.chest_open_img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
        else:
            print("Warning: chest_open.png not found")

        # Load key
        print("Load key img")
        if os.path.exists(key_path):
            img = pygame.image.load(key_path).convert_alpha()
            self.key_img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
        else:
            print("Warning: key.png not found")

    def load_animation(self):
        agent_down_frames_path = os.path.join(self.current_dir, "..", "sprites", "player", "player_move_down")
        fire_frames_path = os.path.join(self.current_dir, "..", "sprites", "fire")
        monster_frames_path = os.path.join(self.current_dir, "..", "sprites", "monster")

        self.agent_load_animation(agent_down_frames_path)
        self.fire_load_animation(fire_frames_path)
        self.monster_animation_load(monster_frames_path)

    def monster_animation_load(self, folder_path: str):
        """
        Load monster animation
        """
        if not os.path.exists(folder_path):
            print(f"Error: Folder {folder_path} not found.")
            return

        # Get all image files and sort them to ensure correct order
        files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))])

        for filename in files:
            img_path = os.path.join(folder_path, filename)
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
            self.monster_frames.append(img)

        print(f"Loaded {len(self.monster_frames)} frames for monster animation.")

    def fire_load_animation(self, folder_path: str):
        """
        Load fire animation
        """
        if not os.path.exists(folder_path):
            print(f"Error: Folder {folder_path} not found.")
            return

        # Get all image files and sort them to ensure correct order
        files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))])

        for filename in files:
            img_path = os.path.join(folder_path, filename)
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
            self.fire_frames.append(img)

        print(f"Loaded {len(self.fire_frames)} frames for fire animation.")

    def agent_load_animation(self, folder_path: str):
        """
        Load the agent downward animation
        """
        if not os.path.exists(folder_path):
            print(f"Error: Folder {folder_path} not found.")
            return

        # Get all image files and sort them to ensure correct order
        files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))])

        for filename in files:
            img_path = os.path.join(folder_path, filename)
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
            self.agent_down_frames.append(img)

        print(f"Loaded {len(self.agent_down_frames)} frames for agent animation.")

    def draw(self, env: GridWorld, episode: int, step: int,
             epsilon: float, total_reward: float, level: int = 0,
             agent_name: str = "Unknown"):
        """
        Draw the current state of the environment.

        Args:
            env: GridWorld environment
            episode: Current episode number
            step: Current step in episode
            epsilon: Current epsilon value
            total_reward: Total reward accumulated
            level: Level number for display
            agent_name: Name of agent for display
        """
        # Background
        self.screen.fill(COL_BG)

        # Draw grid lines
        self._draw_grid(env)

        # Draw static objects
        self._draw_rocks(env)
        self._draw_fires(env)
        self._draw_keys(env)
        self._draw_chests(env)

        # Draw collectibles
        self._draw_apples(env)

        # Draw monsters
        self._draw_monsters(env)

        # Draw agent
        self._draw_agent(env)

        # Draw HUD
        self._draw_hud(episode, step, epsilon, total_reward,
                       env.get_apples_remaining(), level,
                       env.collected_keys,
                       chests_left=env.get_chests_remaining(),
                       agent_name=agent_name
                       )

        # Update display
        pygame.display.flip()

    def _draw_grid(self, env: GridWorld):
        """Draw grid lines"""
        for x in range(env.w):
            for y in range(env.h):
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(self.screen, COL_GRID, rect, 1)

    def _draw_agent(self, env: GridWorld):
        """Draw the agent with animation"""
        if not self.agent_down_frames:
            return

        animation_cooldown = len(self.agent_down_frames) * 2
        frame_index = (self.agent_down_frames_tick // animation_cooldown) % len(self.agent_down_frames)
        current_frame = self.agent_down_frames[frame_index]

        # Calculate position
        ax, ay = env.agent
        pos = (ax * self.tile_size, ay * self.tile_size)

        # Draw the frame
        self.screen.blit(current_frame, pos)
        self.agent_down_frames_tick += 1

    def _draw_apples(self, env: GridWorld):
        """Draw apples (only if not collected)"""
        if not self.apple_img:
            return

        for pos, idx in env.apple_index.items():
            # Check if apple is still available (bit is set)
            if (env.apple_mask >> idx) & 1:
                x = pos[0] * self.tile_size
                y = pos[1] * self.tile_size
                self.screen.blit(self.apple_img, (x, y))

    def _draw_rocks(self, env: GridWorld):
        """Draw rocks as gray squares"""
        for pos in env.rocks:
            rect = pygame.Rect(
                pos[0] * self.tile_size + 4,
                pos[1] * self.tile_size + 4,
                self.tile_size - 8,
                self.tile_size - 8
            )
            pygame.draw.rect(self.screen, COL_ROCK, rect)

    def _draw_fires(self, env: GridWorld):
        """Draw fire with animation"""
        if not self.fire_frames:
            return

        animation_cooldown = len(self.fire_frames) * 1
        frame_index = (self.fire_frames_tick // animation_cooldown) % len(self.fire_frames)
        current_frame = self.fire_frames[frame_index]

        for pos in env.fires:
            x = pos[0] * self.tile_size
            y = pos[1] * self.tile_size
            self.screen.blit(current_frame, (x, y))

        self.fire_frames_tick += 1

    def _draw_keys(self, env: GridWorld):
        """Draw keys (only if not collected)"""
        if not self.key_img:
            return

        for pos in env.keys:
            # Only draw if this key hasn't been collected yet
            if pos not in env.collected_keys_positions:
                x = pos[0] * self.tile_size
                y = pos[1] * self.tile_size
                self.screen.blit(self.key_img, (x, y))

    def _draw_chests(self, env: GridWorld):
        """Draw chests (open or closed)"""
        if not self.chest_close_img or not self.chest_open_img:
            return

        for pos in env.chests:
            idx = env.chest_index[pos]

            # Check if chest is still closed (bit is set in chest_mask)
            is_closed = (env.chest_mask >> idx) & 1

            x = pos[0] * self.tile_size
            y = pos[1] * self.tile_size

            # Draw appropriate image
            if is_closed:
                self.screen.blit(self.chest_close_img, (x, y))
            else:
                self.screen.blit(self.chest_open_img, (x, y))

    def _draw_monsters(self, env: GridWorld):
        """Draw monsters with animation"""
        if not self.monster_frames:
            return

        animation_cooldown = len(self.monster_frames) * 2
        frame_index = (self.monster_frames_tick // animation_cooldown) % len(self.monster_frames)
        current_frame = self.monster_frames[frame_index]

        for pos in env.current_monsters:
            x = pos[0] * self.tile_size
            y = pos[1] * self.tile_size
            self.screen.blit(current_frame, (x, y))

        self.monster_frames_tick += 1

    def _draw_hud(self, episode: int, step: int, epsilon: float,
                  total_reward: float, apples_left: int, level: int,
                  keys_held: int = 0, chests_left: int = 0,
                  agent_name: str = "Unknown"):
        """Draw heads-up display with stats"""
        hud_lines = [
            f"Agent: {agent_name} | Level {level} | Ep {episode + 1} | Step {step} | ε={epsilon:.3f}",
            f"Apples: {apples_left} | Keys: {keys_held} | Chests: {chests_left} | Return: {total_reward:.2f}",
            "Controls: V=toggle speed | R=reset | ESC=quit"
        ]

        y_offset = self.grid_height + 8
        for i, line in enumerate(hud_lines):
            text_surface = self.font.render(line, True, COL_TEXT)
            self.screen.blit(text_surface, (10, y_offset + i * 22))

    def draw_dual(self, env1: GridWorld, env2: GridWorld,
                  episode: int, steps1: int, steps2: int,
                  epsilon1: float, epsilon2: float,
                  reward1: float, reward2: float,
                  level: int,
                  agent1_name: str, agent2_name: str):
        """Draw two agents side-by-side (dual mode built on normal mode)"""
        # Background
        self.screen.fill(COL_BG)

        # Draw divider line
        pygame.draw.line(
            self.screen,
            (100, 100, 100),
            (self.grid_width, 0),
            (self.grid_width, self.height),
            2
        )

        # LEFT SIDE - Agent 1 (uses normal mode drawing with offset)
        self._draw_side(env1, 0, agent1_name)

        # RIGHT SIDE - Agent 2 (uses normal mode drawing with offset)
        self._draw_side(env2, self.grid_width, agent2_name)

        # Draw combined HUD at bottom
        self._draw_dual_hud(
            episode, steps1, steps2,
            epsilon1, epsilon2,
            reward1, reward2,
            env1, env2,
            level,
            agent1_name, agent2_name
        )

        pygame.display.flip()

    def _draw_side(self, env: GridWorld, x_offset: int, agent_name: str):
        """
        Draw one agent's environment at given x offset.
        This uses the same drawing logic as normal mode, just with an offset.
        """
        # Draw grid lines (same as normal mode)
        for x in range(env.w):
            for y in range(env.h):
                rect = pygame.Rect(
                    x_offset + x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(self.screen, COL_GRID, rect, 1)

        # Draw all elements with offset (mirrors normal mode)
        self._draw_rocks_offset(env, x_offset)
        self._draw_fires_offset(env, x_offset)
        self._draw_keys_offset(env, x_offset)
        self._draw_chests_offset(env, x_offset)
        self._draw_apples_offset(env, x_offset)
        self._draw_monsters_offset(env, x_offset)  # Fixed to use current_monsters
        self._draw_agent_offset(env, x_offset)

        # Draw agent name at top with background
        name_surface = self.font.render(agent_name, True, (255, 255, 255))
        bg_rect = pygame.Rect(x_offset + 5, 5, name_surface.get_width() + 10, name_surface.get_height() + 6)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), bg_rect, 2)
        self.screen.blit(name_surface, (x_offset + 10, 10))

    def _draw_agent_offset(self, env: GridWorld, x_offset: int):
        """Draw agent with x offset (same as normal mode)"""
        if not self.agent_down_frames:
            return

        animation_cooldown = len(self.agent_down_frames) * 2
        frame_index = (self.agent_down_frames_tick // animation_cooldown) % len(self.agent_down_frames)
        current_frame = self.agent_down_frames[frame_index]
        ax, ay = env.agent
        pos = (x_offset + ax * self.tile_size, ay * self.tile_size)
        self.screen.blit(current_frame, pos)

    def _draw_apples_offset(self, env: GridWorld, x_offset: int):
        """Draw apples with x offset (same as normal mode)"""
        if not self.apple_img:
            return

        for pos, idx in env.apple_index.items():
            if (env.apple_mask >> idx) & 1:
                x = x_offset + pos[0] * self.tile_size
                y = pos[1] * self.tile_size
                self.screen.blit(self.apple_img, (x, y))

    def _draw_rocks_offset(self, env: GridWorld, x_offset: int):
        """Draw rocks with x offset (same as normal mode)"""
        for pos in env.rocks:
            rect = pygame.Rect(
                x_offset + pos[0] * self.tile_size + 4,
                pos[1] * self.tile_size + 4,
                self.tile_size - 8,
                self.tile_size - 8
            )
            pygame.draw.rect(self.screen, COL_ROCK, rect)

    def _draw_fires_offset(self, env: GridWorld, x_offset: int):
        """Draw fires with x offset (same as normal mode)"""
        if not self.fire_frames:
            return

        animation_cooldown = len(self.fire_frames) * 1
        frame_index = (self.fire_frames_tick // animation_cooldown) % len(self.fire_frames)
        current_frame = self.fire_frames[frame_index]
        for pos in env.fires:
            x = x_offset + pos[0] * self.tile_size
            y = pos[1] * self.tile_size
            self.screen.blit(current_frame, (x, y))

    def _draw_keys_offset(self, env: GridWorld, x_offset: int):
        """Draw keys with x offset (same as normal mode)"""
        if not self.key_img:
            return

        for pos in env.keys:
            # Only draw if this key hasn't been collected yet
            if pos not in env.collected_keys_positions:
                x = x_offset + pos[0] * self.tile_size
                y = pos[1] * self.tile_size
                self.screen.blit(self.key_img, (x, y))

    def _draw_chests_offset(self, env: GridWorld, x_offset: int):
        """Draw chests with x offset (same as normal mode)"""
        if not self.chest_close_img or not self.chest_open_img:
            return

        for pos in env.chests:
            idx = env.chest_index[pos]
            # Check if chest is still closed (bit is set in chest_mask)
            is_closed = (env.chest_mask >> idx) & 1

            if is_closed:
                img = self.chest_close_img
            else:
                img = self.chest_open_img

            x = x_offset + pos[0] * self.tile_size
            y = pos[1] * self.tile_size
            self.screen.blit(img, (x, y))

    def _draw_monsters_offset(self, env: GridWorld, x_offset: int):
        """
        Draw monsters with x offset (FIXED: now uses current_monsters like normal mode)
        """
        if not self.monster_frames:
            return

        animation_cooldown = len(self.monster_frames) * 2
        frame_index = (self.monster_frames_tick // animation_cooldown) % len(self.monster_frames)
        current_frame = self.monster_frames[frame_index]

        # FIX: Changed from env.monsters to env.current_monsters (matching normal mode)
        for pos in env.current_monsters:
            x = x_offset + pos[0] * self.tile_size
            y = pos[1] * self.tile_size
            self.screen.blit(current_frame, (x, y))

    def _draw_dual_hud(self, episode: int, steps1: int, steps2: int,
                       epsilon1: float, epsilon2: float,
                       reward1: float, reward2: float,
                       env1: GridWorld, env2: GridWorld,
                       level: int,
                       agent1_name: str, agent2_name: str):
        """Draw HUD for dual mode"""
        y_offset = self.grid_height + 8

        # Left agent stats (condensed format)
        left_lines = [
            f"{agent1_name} | Lv:{level} | Ep:{episode + 1} | Step:{steps1} | ε={epsilon1:.3f}",
            f"Apple:{env1.get_apples_remaining()} Key:{env1.collected_keys} Chest:{env1.get_chests_remaining()} | Return={reward1:.2f}",
            "V=speed | ESC=quit"
        ]

        for i, line in enumerate(left_lines):
            text_surface = self.font.render(line, True, COL_TEXT)
            self.screen.blit(text_surface, (10, y_offset + i * 22))

        # Right agent stats (condensed format)
        right_lines = [
            f"{agent2_name} | Lv:{level} | Ep:{episode + 1} | Step:{steps2} | ε={epsilon2:.3f}",
            f"Apple:{env2.get_apples_remaining()} Key:{env2.collected_keys} Chest:{env2.get_chests_remaining()} | Return={reward2:.2f}",
            "V=speed | ESC=quit"
        ]

        x_right = self.grid_width + 10
        for i, line in enumerate(right_lines):
            text_surface = self.font.render(line, True, COL_TEXT)
            self.screen.blit(text_surface, (x_right, y_offset + i * 22))

    def draw_menu_dual(self, selected_level: int,
                       agent1_type: int, agent1_intrinsic: bool,
                       agent2_type: int, agent2_intrinsic: bool):
        """Draw menu for dual mode configuration"""
        self.screen.fill((10, 10, 10))

        # Title
        title = self.big_font.render("GridWorld - Dual Mode", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 60))

        # Level selection
        level_text = self.font.render(f"Level: {selected_level}   (← →)", True, (200, 200, 200))
        self.screen.blit(level_text, (self.width // 2 - level_text.get_width() // 2, 130))

        # Agent 1 config
        y = 180
        left_title = self.font.render("LEFT AGENT:", True, (100, 200, 255))
        self.screen.blit(left_title, (self.width // 4 - left_title.get_width() // 2, y))

        agent1_text = self.font.render(f"{AGENTS[agent1_type]}  (Q)", True, (200, 200, 200))
        self.screen.blit(agent1_text, (self.width // 4 - agent1_text.get_width() // 2, y + 30))

        ir1_status = "ON" if agent1_intrinsic else "OFF"
        ir1_color = (100, 255, 100) if agent1_intrinsic else (150, 150, 150)
        ir1_text = self.font.render(f"Intrinsic: {ir1_status}  (W)", True, ir1_color)
        self.screen.blit(ir1_text, (self.width // 4 - ir1_text.get_width() // 2, y + 60))

        # Agent 2 config
        right_title = self.font.render("RIGHT AGENT:", True, (255, 100, 100))
        self.screen.blit(right_title, (3 * self.width // 4 - right_title.get_width() // 2, y))

        agent2_text = self.font.render(f"{AGENTS[agent2_type]}  (E)", True, (200, 200, 200))
        self.screen.blit(agent2_text, (3 * self.width // 4 - agent2_text.get_width() // 2, y + 30))

        ir2_status = "ON" if agent2_intrinsic else "OFF"
        ir2_color = (100, 255, 100) if agent2_intrinsic else (150, 150, 150)
        ir2_text = self.font.render(f"Intrinsic: {ir2_status}  (R)", True, ir2_color)
        self.screen.blit(ir2_text, (3 * self.width // 4 - ir2_text.get_width() // 2, y + 60))

        # Instructions
        instructions = [
            "Press D to exit dual mode",
            "Press ENTER to start",
            "Press ESC to quit"
        ]
        for i, text in enumerate(instructions):
            surface = self.font.render(text, True, (200, 200, 200))
            self.screen.blit(surface, (self.width // 2 - surface.get_width() // 2, 300 + i * 30))

        pygame.display.flip()

    def draw_menu(self, selected_agent, selected_level, use_intrinsic_reward=False):
        """
        Draw the main menu with agent, level, and intrinsic reward selection.

        Args:
            selected_agent: Index of selected agent
            selected_level: Selected level number
            use_intrinsic_reward: Whether intrinsic reward is enabled
        """
        # Background
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill((10, 10, 10))

        # Title
        title = self.big_font.render("GridWorld RL", True, (255, 255, 255))
        self.screen.blit(
            title,
            (self.width // 2 - title.get_width() // 2, 100)
        )

        # Intrinsic reward status indicator
        intrinsic_status = "ON" if use_intrinsic_reward else "OFF"
        intrinsic_color = (100, 255, 100) if use_intrinsic_reward else (200, 200, 200)

        # Menu info
        lines = [
            f"Agent: {AGENTS[selected_agent]}   (↑ ↓)",
            f"Level: {selected_level}   (← →)",
            f"Intrinsic Reward: {intrinsic_status}   (I)",
            "",
            "Press D for Dual Mode",
            "Press ENTER to start",
            "Press ESC to quit"
        ]

        for i, text in enumerate(lines):
            # Special color for intrinsic reward line
            if i == 2:
                color = intrinsic_color
            else:
                color = (200, 200, 200)

            surface = self.font.render(text, True, color)
            self.screen.blit(
                surface,
                (self.width // 2 - surface.get_width() // 2, 200 + i * 30)
            )

        pygame.display.flip()

    def tick(self, fps: int):
        """Control frame rate"""
        self.clock.tick(fps)

    def quit(self):
        """Clean up Pygame"""
        pygame.quit()