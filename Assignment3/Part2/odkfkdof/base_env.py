"""Base Gym environment - updated observation space."""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game. arena import Arena


class BaseArenaEnv(gym.Env):
    """Base environment class with expanded observations."""
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(self, render_mode=None):
        super().__init__()
        
        self.render_mode = render_mode
        self.arena = Arena(render_mode=(render_mode == "human"))
        
        # Updated:  18 observations now (added spawner count + accuracy)
        self.observation_space = spaces.Box(
            low=-1.5,
            high=1.5,
            shape=(18,),
            dtype=np.float32
        )
        
        self. action_space = None
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            np. random.seed(seed)
        obs = self.arena.reset()
        return obs, {}
    
    def step(self, action):
        raise NotImplementedError
        
    def render(self):
        self.arena.render()
        
    def close(self):
        self.arena.close()