"""Rotation-based control environment (Control Style 1)."""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from envs.base_env import BaseArenaEnv


class RotationEnv(BaseArenaEnv):
    """
    Environment with rotation-based controls.
    
    Actions: 
        0: No action
        1: Thrust forward
        2: Rotate left
        3: Rotate right
        4: Shoot
    """
    
    def __init__(self, render_mode=None):
        super().__init__(render_mode)
        self.action_space = spaces.Discrete(5)
        
    def step(self, action):
        """Execute rotation-based action."""
        obs, reward, done, info = self.arena.step_rotation(action)
        # Gymnasium expects (obs, reward, terminated, truncated, info)
        truncated = False
        return obs, reward, done, truncated, info