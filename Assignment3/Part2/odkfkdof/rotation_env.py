"""
Rotation-based control environment (Control Style 1).

This environment uses "tank controls": 
- Rotate left/right to change facing direction
- Thrust to move forward
- Separate shoot action

This is harder to learn than directional controls because
the agent must learn the relationship between rotation and movement.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from odkfkdof.base_env import BaseArenaEnv


class RotationEnv(BaseArenaEnv):
    """
    Environment with rotation-based controls.
    
    Action Space (Discrete with 5 actions):
        0: No action - stand still
        1: Thrust forward - move in facing direction
        2: Rotate left - turn counter-clockwise
        3: Rotate right - turn clockwise
        4: Shoot - fire projectile in facing direction
        
    The challenge:  Agent can only do ONE action per step. 
    It cannot thrust AND shoot, or rotate AND shoot.
    """
    
    def __init__(self, render_mode=None):
        super().__init__(render_mode)
        
        # Discrete(5) means integers 0, 1, 2, 3, 4
        self.action_space = spaces.Discrete(5)
        
    def step(self, action):
        """
        Execute rotation-based action.
        
        Args:
            action: Integer 0-4
            
        Returns:
            observation: New state after action (numpy array)
            reward: Reward for this step (float)
            terminated: True if episode ended (death/win)
            truncated: True if episode cut short (timeout)
            info: Additional information (dict)
        """
        # Call arena's rotation step function
        obs, reward, done, info = self.arena.step_rotation(action)
        
        # Gymnasium uses terminated/truncated instead of just done
        # terminated = natural end (death, win)
        # truncated = artificial end (timeout)
        truncated = info.get("timeout", False)
        terminated = done and not truncated
        
        return obs, reward, terminated, truncated, info