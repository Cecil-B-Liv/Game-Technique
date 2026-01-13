"""
Evaluation script for directional movement agent.

This script loads a trained model and runs it in the game
with visualization so you can see how it performs.
"""

import os
import sys
sys. path.insert(0, os. path.dirname(os.path. dirname(os.path.abspath(__file__))))

import pygame
import time
from stable_baselines3 import PPO
from envs.directional_env import DirectionalEnv


def evaluate_agent(model_path="./models/directional_ppo_final", num_episodes=5):
    """
    Load and run trained agent with visualization.
    
    Args:
        model_path: Path to saved model file
        num_episodes: Number of games to play
    """
    # Create environment WITH rendering
    env = DirectionalEnv(render_mode="human")
    
    # Load the trained model
    print(f"Loading model from: {model_path}")
    try:
        # Try loading as . zip file
        if not model_path.endswith('.zip'):
            model_path_zip = model_path + '.zip'
            if os.path.exists(model_path_zip):
                model_path = model_path_zip
        
        model = PPO.load(model_path)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model:  {e}")
        print("\nMake sure you have trained a model first!")
        print("Run:  python training/train_directional. py")
        return
    
    print(f"\nRunning {num_episodes} evaluation episodes...")
    print("Press Q to quit, SPACE to pause\n")
    
    all_rewards = []
    all_scores = []
    
    for episode in range(num_episodes):
        # Reset environment
        obs, info = env.reset()
        done = False
        episode_reward = 0
        step = 0
        
        print(f"--- Episode {episode + 1}/{num_episodes} ---")
        
        while not done:
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame. QUIT:
                    env. close()
                    return
                if event.type == pygame. KEYDOWN:
                    if event. key == pygame.K_q:
                        env.close()
                        return
                    if event.key == pygame.K_SPACE:
                        # Pause
                        print("Paused.  Press SPACE to continue.")
                        paused = True
                        while paused:
                            for e in pygame.event.get():
                                if e.type == pygame.KEYDOWN and e. key == pygame.K_SPACE:
                                    paused = False
                                if e.type == pygame.QUIT:
                                    env.close()
                                    return
            
            # Get action from model
            # deterministic=True means always pick the best action (no exploration)
            action, _ = model.predict(obs, deterministic=True)
            
            # Execute action
            obs, reward, terminated, truncated, info = env. step(action)
            done = terminated or truncated
            episode_reward += reward
            step += 1
            
            # Render
            env.render()
            
        # Episode finished
        score = info.get('score', 0)
        phase = info. get('phase', 1)
        print(f"  Score:  {score}, Phase reached: {phase}, "
              f"Total reward: {episode_reward:.2f}, Steps: {step}")
        
        all_rewards.append(episode_reward)
        all_scores.append(score)
        
        # Short delay between episodes
        time.sleep(1)
    
    # Print summary
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Episodes played: {num_episodes}")
    print(f"Average reward: {sum(all_rewards) / len(all_rewards):.2f}")
    print(f"Average score: {sum(all_scores) / len(all_scores):.2f}")
    print(f"Best reward: {max(all_rewards):.2f}")
    print(f"Best score: {max(all_scores)}")
    print(f"Worst reward: {min(all_rewards):.2f}")
    print("=" * 50)
    
    env.close()


def play_manual():
    """
    Play the game manually to test and understand it.
    
    This is useful for: 
    1. Testing that the game works
    2. Understanding the difficulty
    3. Comparing human vs AI performance
    """
    env = DirectionalEnv(render_mode="human")
    obs, info = env.reset()
    
    print("\n" + "=" * 50)
    print("MANUAL PLAY MODE - Directional Controls")
    print("=" * 50)
    print("Controls:")
    print("  Arrow Keys - Move (Up/Down/Left/Right)")
    print("  SPACE      - Shoot")
    print("  Q          - Quit")
    print("=" * 50 + "\n")
    
    done = False
    total_reward = 0
    
    while not done:
        # Default:  no action
        action = 0
        
        # Process events
        for event in pygame.event.get():
            if event. type == pygame.QUIT: 
                env.close()
                return
        
        # Check held keys
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_q]:
            break
        elif keys[pygame.K_UP]:
            action = 1
        elif keys[pygame.K_DOWN]:
            action = 2
        elif keys[pygame. K_LEFT]:
            action = 3
        elif keys[pygame.K_RIGHT]:
            action = 4
        elif keys[pygame.K_SPACE]:
            action = 5
            
        # Execute action
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward
        
        # Render
        env.render()
    
    print("\n" + "=" * 50)
    print("GAME OVER")
    print("=" * 50)
    print(f"Final Score: {info.get('score', 0)}")
    print(f"Phase Reached: {info.get('phase', 1)}")
    print(f"Total Reward: {total_reward:.2f}")
    print("=" * 50)
    
    env.close()


if __name__ == "__main__": 
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate or play the RL Arena")
    parser.add_argument(
        "--mode", 
        choices=["eval", "play"], 
        default="eval",
        help="'eval' to watch trained AI, 'play' to play manually"
    )
    parser.add_argument(
        "--model", 
        default="./models/best_directional_ppo/best_model",
        help="Path to trained model file"
    )
    parser.add_argument(
        "--episodes", 
        type=int, 
        default=5,
        help="Number of episodes to run"
    )
    
    args = parser.parse_args()
    
    if args.mode == "eval":
        evaluate_agent(args.model, args. episodes)
    else:
        play_manual()