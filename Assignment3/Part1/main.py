"""
Main entry point for GridWorld Q-Learning
"""

import random

from Assignment3.Part1.src.environment import GridWorld
from Assignment3.Part1.src.agents.qlearning_agent import QLearningAgent
from Assignment3.Part1.src.agents.sarsa_agent import SARSAAgent
from Assignment3.Part1.src.renderer import Renderer
from Assignment3.Part1.src.trainer import Trainer
from Assignment3.Part1.src.config import Config
from Assignment3.Part1.src.constants import LEVELS
from Assignment3.Part1.src.config import load_config



def main():
    """Main function"""
    # Load configuration
    config_dict = load_config("config_level0.json")
    config = Config(config_dict)
    
    # Set random seed
    random.seed(config.seed)
    
    # Choose level (0-5)
    level_num = 1
    level_layout = LEVELS[level_num]

    # Use Sarsa for testing only, change latter
    USE_SARSA = False
    
    print(f"🎮 Starting GridWorld Q-Learning")
    print(f"📊 Level: {level_num}")
    print(f"🔢 Episodes: {config.episodes}")
    print(f"📈 Alpha: {config.alpha}, Gamma: {config.gamma}")
    print(f"🎲 Epsilon: {config.epsilon_start} → {config.epsilon_end}")
    print()
    
    # Create environment
    env = GridWorld(level_layout)
    
    # # Create agent
    # agent = QLearningAgent(
    #     alpha=config.alpha,
    #     gamma=config.gamma,
    #     epsilon_start=config.epsilon_start,
    #     epsilon_end=config.epsilon_end,
    #     epsilon_decay_episodes=config.epsilon_decay_episodes
    # )

    if USE_SARSA:
        agent = SARSAAgent(
            alpha=config.alpha,
            gamma=config.gamma,
            epsilon_start=config.epsilon_start,
            epsilon_end=config.epsilon_end,
            epsilon_decay_episodes=config.epsilon_decay_episodes
        )
        print("Using SARSA")
    else:
        agent = QLearningAgent(
            alpha=config.alpha,
            gamma=config.gamma,
            epsilon_start=config.epsilon_start,
            epsilon_end=config.epsilon_end,
            epsilon_decay_episodes=config.epsilon_decay_episodes
        )
        print("🧠 Using Q-Learning")

    # Create renderer
    renderer = Renderer(tile_size=config.tile_size)
    
    # Create trainer
    trainer = Trainer(env, agent, renderer, config, level=level_num)

    # while trainer.running:

    # Start training
    print("▶ Training started. Press V to toggle speed, R to reset, ESC to quit.")
    trainer.train()
    
    print("👋 Goodbye!")


if __name__ == "__main__":
    main()