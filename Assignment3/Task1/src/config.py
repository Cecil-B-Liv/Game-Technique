"""
Configuration loader for training parameters
"""

import json
import os

DEFAULT_CFG = {
    "episodes":  800,
    "alpha":  0.2,
    "gamma": 0.95,
    "epsilonStart": 1.0,
    "epsilonEnd": 0.05,
    "epsilonDecayEpisodes": 700,
    "maxStepsPerEpisode": 400,
    "fpsVisual": 30,
    "fpsFast":  240,
    "tileSize": 48,
    "seed": 42
}

def load_config(config_file="config_level0.json"):
    """
    Load configuration from JSON file. 
    Falls back to defaults if file not found.
    
    Args:
        config_file: Name of config file to load
        
    Returns:
        dict: Configuration dictionary
    """
    cfg = DEFAULT_CFG.copy()
    
    # Try multiple paths
    possible_paths = [
        config_file,
        os.path.join("config", config_file),
        os.path.join(os.path.dirname(__file__), "..", "config", config_file),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    cfg.update(loaded)
                print(f"✓ Loaded config from:  {path}")
                return cfg
            except Exception as e:
                print(f"⚠ Error loading {path}: {e}")
    
    print("⚠ No config file found, using defaults")
    return cfg


class Config:
    """Configuration container with easy attribute access"""
    
    def __init__(self, config_dict):
        self._config = config_dict
        
        # Unpack common values
        self.episodes = int(config_dict["episodes"])
        self.alpha = float(config_dict["alpha"])
        self.gamma = float(config_dict["gamma"])
        self.epsilon_start = float(config_dict["epsilonStart"])
        self.epsilon_end = float(config_dict["epsilonEnd"])
        self.epsilon_decay_episodes = int(config_dict["epsilonDecayEpisodes"])
        self.max_steps = int(config_dict["maxStepsPerEpisode"])
        self.fps_visual = int(config_dict["fpsVisual"])
        self.fps_fast = int(config_dict["fpsFast"])
        self.tile_size = int(config_dict["tileSize"])
        self.seed = int(config_dict["seed"])
    
    def __getitem__(self, key):
        return self._config[key]
    
    def __repr__(self):
        return f"Config({self._config})"