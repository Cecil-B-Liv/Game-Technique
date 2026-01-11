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
        self.width = WIDTH_TILES * tile_size
        self. height = HEIGHT_TILES * tile_size
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("GridWorld - Q-Learning")
        self.clock = pygame. time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)

        # Path
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.agent_down_frames_path = os.path.join(self.current_dir, "..", "sprites", "player", "player_idle_down")
        # Animation
        self.agent_down_frames = []
        self.agent_down_frames_tick = 0

        # Load assets automatically
        self.agent_load_animation(self.agent_down_frames_path)

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
                cx = pos[0] * self.tile_size + self.tile_size // 2
                cy = pos[1] * self.tile_size + self.tile_size // 2
                radius = self.tile_size // 3
                pygame.draw.circle(self.screen, COL_APPLE, (cx, cy), radius)
    
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
        for pos in env.fires:
            cx = pos[0] * self. tile_size + self.tile_size // 2
            cy = pos[1] * self.tile_size + self.tile_size // 2
            size = self.tile_size // 2
            
            points = [
                (cx, cy - size),
                (cx - size, cy + size),
                (cx + size, cy + size)
            ]
            pygame.draw.polygon(self.screen, COL_FIRE, points)
    
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
        for pos in env. current_monsters:
            cx = pos[0] * self.tile_size + self.tile_size // 2
            cy = pos[1] * self.tile_size + self.tile_size // 2
            size = self.tile_size // 3
            
            points = [
                (cx, cy - size),
                (cx + size, cy),
                (cx, cy + size),
                (cx - size, cy)
            ]
            pygame. draw.polygon(self.screen, COL_MONSTER, points)
    
    def _draw_hud(self, episode: int, step: int, epsilon: float,
                  total_reward: float, apples_left: int, level: int):
        """Draw heads-up display with stats"""
        hud_lines = [
            f"Level {level} | Ep {episode + 1} | Step {step} | ε={epsilon:.3f}",
            f"Apples: {apples_left} | Return: {total_reward:.2f}",
            "Controls:  V=toggle speed | R=reset | ESC=quit"
        ]
        
        y_offset = 8
        for i, line in enumerate(hud_lines):
            text_surface = self.font.render(line, True, COL_TEXT)
            self.screen.blit(text_surface, (10, y_offset + i * 22))
    
    def tick(self, fps: int):
        """Control frame rate"""
        self.clock.tick(fps)
    
    def quit(self):
        """Clean up Pygame"""
        pygame. quit()