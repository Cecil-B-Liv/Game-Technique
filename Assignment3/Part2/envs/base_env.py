"""
Base Gym environment for the arena. 

This file creates a bridge between our game (Arena) and the 
Stable Baselines3 RL library. It uses the Gymnasium API. 

Gymnasium (formerly OpenAI Gym) defines a standard interface: 
- reset(): Start a new episode, return initial observation
- step(action): Take an action, return (obs, reward, done, truncated, info)
- render(): Display the current state
- close(): Clean up resources
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game.arena import Arena


class BaseArenaEnv(gym.Env):
    """
    Base environment class. 
    
    This is subclassed by RotationEnv and DirectionalEnv to create
    environments with different action spaces.
    
    The observation space is the same for both: 
    - 16-dimensional continuous vector
    - All values normalized to approximately [-1, 1] or [0, 1]
    """
    
    # Gymnasium metadata
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(self, render_mode=None):
        """
        Initialize the environment.
        
        Args:
            render_mode: "human" to display window, None for headless training
        """
        super().__init__()
        
        self.render_mode = render_mode
        
        # Create the game arena
        # render_mode="human" tells arena to create a Pygame window
        self.arena = Arena(render_mode=(render_mode == "human"))
        
        # Define observation space
        # Box = continuous values within bounds
        # Shape (16,) means 16 numbers
        # Low/high define the valid range for each dimension
        self.observation_space = spaces.Box(
            low=-1.5,    # Slightly below -1 for safety
            high=1.5,    # Slightly above 1 for safety
            shape=(16,), # 16 observation values (updated from 12)
            dtype=np.float32
        )
        
        # Action space is defined in subclasses
        self.action_space = None
        
    def reset(self, seed=None, options=None):
        """
        Reset the environment for a new episode.
        
        This is called: 
        - At the start of training
        - After each episode ends (death, timeout, or win)
        
        Args:
            seed: Random seed for reproducibility
            options:  Additional options (unused)
            
        Returns:
            observation: Initial state observation
            info: Additional information (empty dict)
        """
        # Call parent reset (handles seeding)
        super().reset(seed=seed)
        
        # Set random seed if provided
        if seed is not None:
            np.random.seed(seed)
            
        # Reset the game
        obs = self.arena.reset()
        
        # Gymnasium expects (observation, info)
        return obs, {}
    
    def step(self, action):
        """
        Execute one step in the environment.
        
        This is implemented in subclasses because the action
        interpretation differs between control schemes.
        """
        raise NotImplementedError("Subclasses must implement step()")
        
    def render(self):
        """Render the current game state."""
        self.arena.render()
        
    def close(self):
        """Clean up resources."""
        self.arena.close()