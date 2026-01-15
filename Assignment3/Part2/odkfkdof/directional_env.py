"""
Directional movement control environment (Control Style 2).

This environment uses simple directional controls:
- Press up/down/left/right to move
- The player automatically faces movement direction
- Separate shoot action

This is EASIER to learn than rotation controls because
the relationship between action and movement is direct.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from odkfkdof.base_env import BaseArenaEnv


class DirectionalEnv(BaseArenaEnv):
    """
    Environment with directional movement controls.
    
    Action Space (Discrete with 6 actions):
        0: No action - stand still
        1: Move up
        2: Move down
        3: Move left
        4: Move right
        5: Shoot
        
    Note: Player automatically faces movement direction,
    so shooting happens in the last moved direction.
    """
    
    def __init__(self, render_mode=None):
        super().__init__(render_mode)
        
        # Discrete(6) means integers 0, 1, 2, 3, 4, 5
        self.action_space = spaces.Discrete(6)
        
    def step(self, action):
        """
        Execute directional action.
        
        Args:
            action: Integer 0-5
            
        Returns:
            observation, reward, terminated, truncated, info
        """
        obs, reward, done, info = self.arena.step_directional(action)
        
        truncated = info.get("timeout", False)
        terminated = done and not truncated
        
        return obs, reward, terminated, truncated, info