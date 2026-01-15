"""
Main entry point for GridWorld Q-Learning with Intrinsic Reward support
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
    """Main function with intrinsic reward toggle"""
    running = True

    # User choices
    selected_agent = 0
    selected_level = 0
    use_intrinsic_reward = False  # New toggle for intrinsic reward
    intrinsic_strength = 0.05  # Default intrinsic reward strength

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

                # Toggle intrinsic reward (I key)
                if event.key == pygame.K_i:
                    use_intrinsic_reward = not use_intrinsic_reward
                    status = "ON" if use_intrinsic_reward else "OFF"
                    print(f"Intrinsic Reward: {status}")

                # Start training
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
                            epsilon_decay_episodes=config.epsilon_decay_episodes,
                            # use_intrinsic_reward=use_intrinsic_reward,
                            # intrinsic_strength=intrinsic_strength
                        )
                    else:
                        agent = QLearningAgent(
                            alpha=config.alpha,
                            gamma=config.gamma,
                            epsilon_start=config.epsilon_start,
                            epsilon_end=config.epsilon_end,
                            epsilon_decay_episodes=config.epsilon_decay_episodes,
                            use_intrinsic_reward=use_intrinsic_reward,
                            intrinsic_strength=intrinsic_strength
                        )

                    intrinsic_status = "WITH" if use_intrinsic_reward else "WITHOUT"
                    print(f"\nStarting GridWorld {AGENTS[selected_agent]} ({intrinsic_status} Intrinsic Reward)")
                    print(f"Level: {selected_level}")
                    print(f"Episodes: {config.episodes}")
                    print(f"Alpha: {config.alpha}, Gamma: {config.gamma}")
                    print(f"Epsilon: {config.epsilon_start} → {config.epsilon_end}")
                    if use_intrinsic_reward:
                        print(f"Intrinsic Strength: {intrinsic_strength}")
                    print()

                    # Create environment
                    env = GridWorld(level_layout)

                    # Create trainer
                    trainer = Trainer(
                        env, agent, renderer, config,
                        level=selected_level,
                        agent_name=AGENTS[selected_agent]
                    )

                    print("Training started.")
                    trainer.train()

                # Quit
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Draw menu with intrinsic reward status
        renderer.draw_menu(selected_agent, selected_level, use_intrinsic_reward)
    
    print("End Game")
    renderer.quit()


if __name__ == "__main__":
    main()