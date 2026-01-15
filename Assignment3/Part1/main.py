"""
Main entry point for GridWorld Q-Learning
"""

import random

import pygame

from Assignment3.Part1.src.environment import GridWorld
from Assignment3.Part1.src.agents.qlearning_agent import QLearningAgent
from Assignment3.Part1.src.agents.sarsa_agent import SARSAAgent
from Assignment3.Part1.src.renderer import Renderer
from Assignment3.Part1.src.trainer import Trainer
from Assignment3.Part1.src.config import Config
from Assignment3.Part1.src.constants import LEVELS, AGENTS, MAX_LEVEL
from Assignment3.Part1.src.config import load_config



def main():
    """Main function"""
    running = True
    # User choice
    selected_agent = 0
    selected_level = 0

    # Create renderer
    renderer = Renderer(tile_size=48)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                # Agent selection
                if event.key == pygame.K_UP:
                    selected_agent = (selected_agent - 1) % len(AGENTS)
                    print(f"Agent: {AGENTS[selected_agent]}")

                if event.key == pygame.K_DOWN:
                    selected_agent = (selected_agent + 1) % len(AGENTS)
                    print(f"Agent: {AGENTS[selected_agent]}")

                # Level selection
                if event.key == pygame.K_LEFT:
                    selected_level = max(0, selected_level - 1)
                    print(f"Level: {selected_level}")

                if event.key == pygame.K_RIGHT:
                    selected_level = min(MAX_LEVEL, selected_level + 1)
                    print(f"Level: {selected_level}")

                if event.key == pygame.K_RETURN:
                    # Load config for selected level
                    config_file = f"config_level{selected_level}.json"
                    config_dict = load_config(config_file)
                    config = Config(config_dict)

                    # Set random seed
                    random.seed(config.seed)

                    # Create level layout
                    level_layout = LEVELS[selected_level]

                    # Create agent based on selection
                    if AGENTS[selected_agent] == "SARSA":
                        agent = SARSAAgent(
                            alpha=config.alpha,
                            gamma=config.gamma,
                            epsilon_start=config.epsilon_start,
                            epsilon_end=config.epsilon_end,
                            epsilon_decay_episodes=config.epsilon_decay_episodes
                        )
                    else:
                        agent = QLearningAgent(
                            alpha=config.alpha,
                            gamma=config.gamma,
                            epsilon_start=config.epsilon_start,
                            epsilon_end=config.epsilon_end,
                            epsilon_decay_episodes=config.epsilon_decay_episodes
                        )

                    print(f"Starting GridWorld {AGENTS[selected_agent]}")
                    print(f"Level: {selected_level}")
                    print(f"Episodes: {config.episodes}")
                    print(f"Alpha: {config.alpha}, Gamma: {config.gamma}")
                    print(f"Epsilon: {config.epsilon_start} → {config.epsilon_end}")
                    print()

                    # Create environment
                    env = GridWorld(level_layout)

                    # Create trainer
                    trainer = Trainer(env, agent, renderer, config, level=selected_level, agent_name=AGENTS[selected_agent])

                    print("Training started.")
                    trainer.train()

                if event.key == pygame.K_ESCAPE:
                    running = False

        renderer.draw_menu(selected_agent, selected_level)
    
    print("End Game")
    renderer.quit()


if __name__ == "__main__":
    main()