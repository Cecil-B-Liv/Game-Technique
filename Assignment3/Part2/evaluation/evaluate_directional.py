"""Evaluation script for directional movement control agent."""

import os
import sys
sys. path.insert(0, os. path.dirname(os.path. dirname(os.path.abspath(__file__))))

import pygame
from stable_baselines3 import PPO, DQN
from envs.directional_env import DirectionalEnv


def evaluate_directional(model_path="./models/directional_ppo_final", num_episodes=5):
    """Load and evaluate the directional control agent visually."""
    
    env = DirectionalEnv(render_mode="human")
    
    try:
        model = PPO. load(model_path)
        print(f"Loaded PPO model from {model_path}")
    except:
        try: 
            model = DQN.load(model_path)
            print(f"Loaded DQN model from {model_path}")
        except Exception as e:
            print(f"Error loading model:  {e}")
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return
                if event.type == pygame. KEYDOWN and event.key == pygame.K_q:
                    env.close()
                    return
            
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            step += 1
            env.render()
            
        print(f"  Score: {info.get('score', 0)}, Reward: {episode_reward:.2f}, Steps: {step}")
        total_rewards.append(episode_reward)
    
    print(f"\nAverage reward: {sum(total_rewards)/len(total_rewards):.2f}")
    env.close()


def play_human_directional():
    """Play manually with directional controls."""
    env = DirectionalEnv(render_mode="human")
    obs, _ = env.reset()
    
    print("\nManual Play Mode (Directional Controls)")
    print("Controls:  Arrow keys to move, SPACE to shoot, Q to quit\n")
    
    done = False
    total_reward = 0
    
    while not done:
        action = 0
        
        for event in pygame. event.get():
            if event.type == pygame.QUIT: 
                env.close()
                return
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            break
        elif keys[pygame.K_UP]:
            action = 1
        elif keys[pygame.K_DOWN]:
            action = 2
        elif keys[pygame.K_LEFT]:
            action = 3
        elif keys[pygame.K_RIGHT]:
            action = 4
        elif keys[pygame.K_SPACE]:
            action = 5
            
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        env. render()
        
    print(f"Game Over! Score: {info.get('score', 0)}, Reward: {total_reward:.2f}")
    env.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["eval", "play"], default="eval")
    parser.add_argument("--model", default="./models/directional_ppo_final")
    parser.add_argument("--episodes", type=int, default=5)
    args = parser.parse_args()
    
    if args.mode == "eval":
        evaluate_directional(args.model, args.episodes)
    else:
        play_human_directional()