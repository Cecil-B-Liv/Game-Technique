"""Base Gym environment for the arena."""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game.arena import Arena


class BaseArenaEnv(gym.Env):
    """Base environment class - subclass for specific control schemes."""
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self. arena = Arena(render_mode=(render_mode == "human"))
        
        # Observation space:  12-dimensional vector (see arena._get_observation)
        # All values normalized to approximately [0, 1] or [-1, 1]
        self.observation_space = spaces. Box(
            low=-1.0, 
            high=2.0,  # Some values might slightly exceed 1
            shape=(12,), 
            dtype=np.float32
        )
        
        # Action space defined in subclasses
        self.action_space = None
        
    def reset(self, seed=None, options=None):
        """Reset the environment."""
        super().reset(seed=seed)
        if seed is not None:
            np. random.seed(seed)
        obs = self. arena. reset()
        return obs, {}
    
    def step(self, action):
        """Execute one step - implemented in subclasses."""
        raise NotImplementedError
        
    def render(self):
        """Render the game."""
        self.arena.render()
        
    def close(self):
        """Clean up."""
        self.arena.close()