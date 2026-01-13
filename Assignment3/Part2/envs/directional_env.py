"""Directional movement control environment (Control Style 2)."""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from envs.base_env import BaseArenaEnv


class DirectionalEnv(BaseArenaEnv):
    """
    Environment with directional movement controls.
    
    Actions:
        0: No action
        1: Move up
        2: Move down
        3: Move left
        4: Move right
        5: Shoot
    """
    
    def __init__(self, render_mode=None):
        super().__init__(render_mode)
        self.action_space = spaces. Discrete(6)
        
    def step(self, action):
        """Execute directional action."""
        obs, reward, done, info = self. arena.step_directional(action)
        truncated = False
        return obs, reward, done, truncated, info