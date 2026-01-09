"""
Main entry point for GridWorld Q-Learning
"""

import random
from src import (
    GridWorld,
    QLearningAgent,
    Renderer,
    Trainer,
    load_config,
    LEVELS
)
from src.config import Config


def main():
    """Main function"""
    # Load configuration
    config_dict = load_config("config_level0.json")
    config = Config(config_dict)
    
    # Set random seed
    random.seed(config.seed)
    
    # Choose level (0-5)
    level_num = 0
    level_layout = LEVELS[level_num]
    
    print(f"🎮 Starting GridWorld Q-Learning")
    print(f"📊 Level: {level_num}")
    print(f"🔢 Episodes: {config.episodes}")
    print(f"📈 Alpha: {config.alpha}, Gamma: {config.gamma}")
    print(f"🎲 Epsilon: {config.epsilon_start} → {config.epsilon_end}")
    print()
    
    # Create environment
    env = GridWorld(level_layout)
    
    # Create agent
    agent = QLearningAgent(
        alpha=config.alpha,
        gamma=config.gamma,
        epsilon_start=config.epsilon_start,
        epsilon_end=config.epsilon_end,
        epsilon_decay_episodes=config.epsilon_decay_episodes
    )
    
    # Create renderer
    renderer = Renderer(tile_size=config.tile_size)
    
    # Create trainer
    trainer = Trainer(env, agent, renderer, config, level=level_num)
    
    # Start training
    print("▶ Training started. Press V to toggle speed, R to reset, ESC to quit.")
    trainer.train()
    
    print("👋 Goodbye!")


if __name__ == "__main__":
    main()