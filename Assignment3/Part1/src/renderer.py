"""
Pygame renderer for GridWorld visualization
"""
import os

import pygame
from typing import Optional
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
    
    def __init__(self, tile_size: int = 48):
        """
        Initialize Pygame renderer.
        
        Args:
            tile_size: Size of each tile in pixels
        """
        self.tile_size = tile_size
        self.grid_width = WIDTH_TILES * tile_size
        self.grid_height = HEIGHT_TILES * tile_size

        self.height = self.grid_height + HUD_HEIGHT
        self.width = self.grid_width
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("GridWorld - Q-Learning")
        self.clock = pygame. time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 36)

        # Path
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        # Still Assets
        self.menu_bg = None
        self.apple_img = None

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
        menu_bg_path = os.path.join(self.current_dir, "..", "sprites", "main_menu_bg.png")
        apple_path = os.path.join(self.current_dir, "..", "sprites", "apple.png")

        # Load menu img
        print("Load main menu img")
        if os.path.exists(menu_bg_path):
            img = pygame.image.load(menu_bg_path).convert()
            self.menu_bg = pygame.transform.scale(img, (self.width, self.height))
        else:
            print("Warning: main_menu_bg.png not found")

        # Load apple img
        if os.path.exists(apple_path):
            img = pygame.image.load(apple_path).convert_alpha()
            self.apple_img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
        else:
            print("Warning: apple.png not found")

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

        print(f"Loaded {len(self.monster_frames)} frames for agent animation.")
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

        print(f"Loaded {len(self.fire_frames)} frames for agent animation.")


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
             epsilon: float, total_reward: float, level: int = 0):
        """
        Draw the current state of the environment.
        
        Args:
            env: GridWorld environment
            episode: Current episode number
            step: Current step in episode
            epsilon: Current epsilon value
            total_reward: Total reward accumulated
            level: Level number for display
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
                       env.get_apples_remaining(), level)
        
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
        """Draw the agent as a green square"""
        animation_cooldown = len(self.agent_down_frames) * 2
        frame_index = (self.agent_down_frames_tick // animation_cooldown) % len(self.agent_down_frames)
        current_frame = self.agent_down_frames[frame_index]

        #Calculate position
        ax, ay = env.agent
        pos = (ax * self.tile_size, ay * self.tile_size)

        #Draw the frame
        self.screen.blit(current_frame, pos)
        self.agent_down_frames_tick += 1
    
    def _draw_apples(self, env: GridWorld):
        """Draw apples as red circles (only if not collected)"""
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
                self. tile_size - 8
            )
            pygame.draw.rect(self.screen, COL_ROCK, rect)
    
    def _draw_fires(self, env: GridWorld):
        """Draw fire as orange-red triangles"""

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
        """Draw keys as yellow circles"""
        for pos in env.keys:
            cx = pos[0] * self.tile_size + self.tile_size // 2
            cy = pos[1] * self.tile_size + self.tile_size // 2
            radius = self. tile_size // 4
            pygame.draw.circle(self.screen, COL_KEY, (cx, cy), radius)
    
    def _draw_chests(self, env: GridWorld):
        """Draw chests as brown rectangles"""
        for pos in env.chests:
            opened = pos in env.opened_chests
            color = (100, 50, 20) if opened else COL_CHEST
            
            rect = pygame.Rect(
                pos[0] * self.tile_size + 8,
                pos[1] * self.tile_size + 8,
                self.tile_size - 16,
                self. tile_size - 16
            )
            pygame.draw.rect(self.screen, color, rect)
    
    def _draw_monsters(self, env: GridWorld):
        """Draw monsters as purple diamonds"""

        animation_cooldown = len(self.monster_frames) * 2
        frame_index = (self.monster_frames_tick // animation_cooldown) % len(self.monster_frames)
        current_frame = self.monster_frames[frame_index]

        for pos in env.current_monsters:
            x = pos[0] * self.tile_size
            y = pos[1] * self.tile_size
            self.screen.blit(current_frame, (x, y))

        self.monster_frames_tick += 1
    
    def _draw_hud(self, episode: int, step: int, epsilon: float,
                  total_reward: float, apples_left: int, level: int):
        """Draw heads-up display with stats"""
        hud_lines = [
            f"Level {level} | Ep {episode + 1} | Step {step} | ε={epsilon:.3f}",
            f"Apples: {apples_left} | Return: {total_reward:.2f}",
            "Controls:  V=toggle speed | R=reset | ESC=quit"
        ]
        
        y_offset = self.grid_height + 8
        for i, line in enumerate(hud_lines):
            text_surface = self.font.render(line, True, COL_TEXT)
            self.screen.blit(text_surface, (10, y_offset + i * 22))

    def draw_menu(self, selected_agent, selected_level):
        # Background
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill((10, 10, 10))

        # Title
        title = self.big_font.render("GridWorld RL", True, (255, 255, 255))
        self.screen.blit(
            title,
            (self.width // 2 - title.get_width() // 2, 120)
        )

        # Menu info
        lines = [
            f"Agent: {AGENTS[selected_agent]}   (↑ ↓)",
            f"Level: {selected_level}   (← →)",
            "",
            "Press ENTER to start",
            "Press ESC to quit"
        ]

        for i, text in enumerate(lines):
            color = (200, 200, 200)
            surface = self.font.render(text, True, color)
            self.screen.blit(
                surface,
                (self.width // 2 - surface.get_width() // 2, 220 + i * 30)
            )

        pygame.display.flip()

    def tick(self, fps: int):
        """Control frame rate"""
        self.clock.tick(fps)
    
    def quit(self):
        """Clean up Pygame"""
        pygame. quit()