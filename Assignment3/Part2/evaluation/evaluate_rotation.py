"""Evaluation script for rotation-based control agent."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from stable_baselines3 import PPO, DQN
from envs.rotation_env import RotationEnv


def evaluate_rotation(model_path="./models/rotation_ppo_final", num_episodes=5):
    """
    Load and evaluate the rotation control agent visually.
    
    Args:
        model_path: Path to the trained model
        num_episodes:  Number of episodes to run
    """
    # Create environment with rendering
    env = RotationEnv(render_mode="human")
    
    # Load the trained model
    try:
        model = PPO. load(model_path)
        print(f"Loaded PPO model from {model_path}")
    except: 
        try:
            model = DQN.load(model_path)
            print(f"Loaded DQN model from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Make sure you have trained a model first!")
            return
    
    print(f"\nRunning {num_episodes} evaluation episodes...")
    print("Press 'Q' or close the window to quit early.\n")
    
    total_rewards = []
    
    for episode in range(num_episodes):
        obs, _ = env.reset()
        done = False
        episode_reward = 0
        step = 0
        
        print(f"Episode {episode + 1}/{num_episodes}")
        
        while not done:
            # Handle pygame events
            for event in pygame. event.get():
                if event.type == pygame.QUIT: 
                    env.close()
                    return
                if event.type == pygame.KEYDOWN:
                    if event. key == pygame.K_q:
                        env.close()
                        return
            
            # Get action from model
            action, _ = model.predict(obs, deterministic=True)
            
            # Step environment
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            step += 1
            
            # Render
            env.render()
            
        print(f"  Score: {info. get('score', 0)}, Total Reward: {episode_reward:. 2f}, Steps: {step}")
        total_rewards.append(episode_reward)
    
    print(f"\nEvaluation complete!")
    print(f"Average reward: {sum(total_rewards)/len(total_rewards):.2f}")
    print(f"Best episode: {max(total_rewards):. 2f}")
    
    env.close()


def play_human_rotation():
    """Play the game manually with rotation controls for testing."""
    env = RotationEnv(render_mode="human")
    obs, _ = env.reset()
    
    print("\nManual Play Mode (Rotation Controls)")
    print("Controls:")
    print("  W - Thrust forward")
    print("  A - Rotate left")
    print("  D - Rotate right")
    print("  SPACE - Shoot")
    print("  Q - Quit\n")
    
    done = False
    total_reward = 0
    
    while not done:
        action = 0  # No action by default
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.close()
                return
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            break
        elif keys[pygame.K_w]: 
            action = 1  # Thrust
        elif keys[pygame.K_a]:
            action = 2  # Rotate left
        elif keys[pygame.K_d]: 
            action = 3  # Rotate right
        elif keys[pygame.K_SPACE]: 
            action = 4  # Shoot
            
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        env.render()
        
    print(f"Game Over! Score: {info.get('score', 0)}, Total Reward: {total_reward:.2f}")
    env.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["eval", "play"], default="eval",
                       help="'eval' to watch AI, 'play' to play manually")
    parser.add_argument("--model", default="./models/rotation_ppo_final",
                       help="Path to trained model")
    parser.add_argument("--episodes", type=int, default=5,
                       help="Number of episodes for evaluation")
    args = parser.parse_args()
    
    if args.mode == "eval": 
        evaluate_rotation(args. model, args.episodes)
    else:
        play_human_rotation()