"""
Evaluation script for rotation-based control agent. 
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os. path.dirname(os.path. abspath(__file__))))

import pygame
import time
from stable_baselines3 import PPO
from envs.rotation_env import RotationEnv


def evaluate_agent(model_path="./models/rotation_ppo_final", num_episodes=5):
    """Load and run trained rotation agent with visualization."""
    
    env = RotationEnv(render_mode="human")
    
    print(f"Loading model from: {model_path}")
    try:
        if not model_path.endswith('. zip'):
            model_path_zip = model_path + '.zip'
            if os.path. exists(model_path_zip):
                model_path = model_path_zip
        
        model = PPO.load(model_path)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("\nRun: python training/train_rotation.py first")
        return
    
    print(f"\nRunning {num_episodes} evaluation episodes...")
    print("Press Q to quit\n")
    
    all_rewards = []
    all_scores = []
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        done = False
        episode_reward = 0
        step = 0
        
        print(f"--- Episode {episode + 1}/{num_episodes} ---")
        
        while not done: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return
                if event.type == pygame. KEYDOWN and event.key == pygame.K_q:
                    env.close()
                    return
            
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            episode_reward += reward
            step += 1
            env.render()
            
        score = info.get('score', 0)
        phase = info. get('phase', 1)
        print(f"  Score:  {score}, Phase:  {phase}, Reward: {episode_reward:.2f}, Steps: {step}")
        
        all_rewards.append(episode_reward)
        all_scores.append(score)
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Average reward: {sum(all_rewards) / len(all_rewards):.2f}")
    print(f"Average score: {sum(all_scores) / len(all_scores):.2f}")
    print(f"Best score: {max(all_scores)}")
    print("=" * 50)
    
    env.close()


def play_manual():
    """Play manually with rotation controls."""
    
    env = RotationEnv(render_mode="human")
    obs, info = env.reset()
    
    print("\n" + "=" * 50)
    print("MANUAL PLAY MODE - Rotation Controls")
    print("=" * 50)
    print("Controls:")
    print("  W     - Thrust forward")
    print("  A     - Rotate left")
    print("  D     - Rotate right")
    print("  SPACE - Shoot")
    print("  Q     - Quit")
    print("=" * 50 + "\n")
    
    done = False
    total_reward = 0
    
    while not done:
        action = 0
        
        for event in pygame.event.get():
            if event.type == pygame. QUIT:
                env.close()
                return
        
        keys = pygame.key. get_pressed()
        
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
            
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward
        env.render()
    
    print(f"\nGame Over!  Score: {info.get('score', 0)}, Reward: {total_reward:.2f}")
    env.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["eval", "play"], default="eval")
    parser.add_argument("--model", default="./models/best_rotation_ppo/best_model")
    parser.add_argument("--episodes", type=int, default=5)
    
    args = parser.parse_args()
    
    if args.mode == "eval":
        evaluate_agent(args.model, args.episodes)
    else:
        play_manual()