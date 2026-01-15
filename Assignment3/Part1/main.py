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
    dual_mode = False  # Dual agent comparison mode
    
    # Dual mode configuration
    agent1_type = 0  # Index for left agent
    agent1_intrinsic = False
    agent2_type = 0  # Index for right agent
    agent2_intrinsic = False

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

                # Toggle dual mode (D key)
                if event.key == pygame.K_d:
                    dual_mode = not dual_mode
                    status = "ON" if dual_mode else "OFF"
                    print(f"Dual Mode: {status}")

                # Dual mode: Configure Agent 1 (Q key - cycle agent type)
                if event.key == pygame.K_q and dual_mode:
                    agent1_type = (agent1_type + 1) % len(AGENTS)
                    print(f"Agent 1: {AGENTS[agent1_type]}")

                # Dual mode: Toggle Agent 1 intrinsic (W key)
                if event.key == pygame.K_w and dual_mode:
                    agent1_intrinsic = not agent1_intrinsic
                    status = "ON" if agent1_intrinsic else "OFF"
                    print(f"Agent 1 Intrinsic: {status}")

                # Dual mode: Configure Agent 2 (E key - cycle agent type)
                if event.key == pygame.K_e and dual_mode:
                    agent2_type = (agent2_type + 1) % len(AGENTS)
                    print(f"Agent 2: {AGENTS[agent2_type]}")

                # Dual mode: Toggle Agent 2 intrinsic (R key)
                if event.key == pygame.K_r and dual_mode:
                    agent2_intrinsic = not agent2_intrinsic
                    status = "ON" if agent2_intrinsic else "OFF"
                    print(f"Agent 2 Intrinsic: {status}")

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

                    if dual_mode:
                        # DUAL MODE: Train 2 agents side-by-side
                        print(f"\n=== DUAL MODE ===")
                        print(f"Level: {selected_level}")
                        print(f"Agent 1: {AGENTS[agent1_type]} {'+ IR' if agent1_intrinsic else ''}")
                        print(f"Agent 2: {AGENTS[agent2_type]} {'+ IR' if agent2_intrinsic else ''}")
                        print(f"Episodes: {config.episodes}")
                        print()

                        # Create Agent 1
                        if AGENTS[agent1_type] == "SARSA":
                            agent1 = SARSAAgent(
                                alpha=config.alpha,
                                gamma=config.gamma,
                                epsilon_start=config.epsilon_start,
                                epsilon_end=config.epsilon_end,
                                epsilon_decay_episodes=config.epsilon_decay_episodes,
                                use_intrinsic_reward=agent1_intrinsic,
                                intrinsic_strength=intrinsic_strength
                            )
                        else:
                            agent1 = QLearningAgent(
                                alpha=config.alpha,
                                gamma=config.gamma,
                                epsilon_start=config.epsilon_start,
                                epsilon_end=config.epsilon_end,
                                epsilon_decay_episodes=config.epsilon_decay_episodes,
                                use_intrinsic_reward=agent1_intrinsic,
                                intrinsic_strength=intrinsic_strength
                            )

                        # Create Agent 2
                        if AGENTS[agent2_type] == "SARSA":
                            agent2 = SARSAAgent(
                                alpha=config.alpha,
                                gamma=config.gamma,
                                epsilon_start=config.epsilon_start,
                                epsilon_end=config.epsilon_end,
                                epsilon_decay_episodes=config.epsilon_decay_episodes,
                                use_intrinsic_reward=agent2_intrinsic,
                                intrinsic_strength=intrinsic_strength
                            )
                        else:
                            agent2 = QLearningAgent(
                                alpha=config.alpha,
                                gamma=config.gamma,
                                epsilon_start=config.epsilon_start,
                                epsilon_end=config.epsilon_end,
                                epsilon_decay_episodes=config.epsilon_decay_episodes,
                                use_intrinsic_reward=agent2_intrinsic,
                                intrinsic_strength=intrinsic_strength
                            )

                        # Create environments
                        env1 = GridWorld(level_layout)
                        env2 = GridWorld(level_layout)

                        # Create dual renderer
                        dual_renderer = Renderer(tile_size=48, dual_mode=True)

                        # Create trainers
                        agent1_name = f"{AGENTS[agent1_type]}" + (" +IR" if agent1_intrinsic else "")
                        agent2_name = f"{AGENTS[agent2_type]}" + (" +IR" if agent2_intrinsic else "")
                        
                        trainer1 = Trainer(
                            env1, agent1, dual_renderer, config,
                            level=selected_level,
                            agent_name=agent1_name,
                            screen_side="left"
                        )
                        trainer2 = Trainer(
                            env2, agent2, dual_renderer, config,
                            level=selected_level,
                            agent_name=agent2_name,
                            screen_side="right"
                        )

                        print("Training started. Press V to toggle speed, ESC to quit.")
                        trainer1.train_dual(trainer2)

                        # After training, recreate renderer with single-screen size
                        dual_renderer.quit()
                        renderer = Renderer(tile_size=48)

                    else:
                        # SINGLE MODE
                        # Create agent based on selection
                        if AGENTS[selected_agent] == "SARSA":
                            agent = SARSAAgent(
                                alpha=config.alpha,
                                gamma=config.gamma,
                                epsilon_start=config.epsilon_start,
                                epsilon_end=config.epsilon_end,
                                epsilon_decay_episodes=config.epsilon_decay_episodes,
                                use_intrinsic_reward=use_intrinsic_reward,
                                intrinsic_strength=intrinsic_strength
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

                        print("Training started. Press V to toggle speed, R to reset, ESC to quit.")
                        trainer.train()

                # Quit
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Draw menu
        if dual_mode:
            renderer.draw_menu_dual(selected_level, agent1_type, agent1_intrinsic, 
                                   agent2_type, agent2_intrinsic)
        else:
            renderer.draw_menu(selected_agent, selected_level, use_intrinsic_reward)
    
    print("End Game")
    renderer.quit()


if __name__ == "__main__":
    main()