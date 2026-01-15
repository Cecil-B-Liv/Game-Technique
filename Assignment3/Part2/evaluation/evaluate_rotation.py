"""Evaluation script for rotation-based control agent."""

from envs.rotation_env import RotationEnv
from stable_baselines3 import PPO
import numpy as np
import time
import pygame
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_MODEL_PATH = "./models/rotation/best_model"


def evaluate_agent(model_path=DEFAULT_MODEL_PATH, num_episodes=20):
    """
    Evaluate agent and collect all metrics. 
    """

    env = RotationEnv(render_mode="human")

    if not model_path.endswith('. zip'):
        if os.path.exists(model_path + '. zip'):
            model_path = model_path + '.zip'

    print(f"Loading model from: {model_path}")
    try:
        model = PPO.load(model_path)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("\nTrain first: python training/train_rotation.py")
        return

    print(f"\nEvaluating over {num_episodes} episodes...")
    print("Controls: Q=quit, SPACE=pause\n")

    all_rewards = []
    all_scores = []
    all_phases = []
    all_steps = []

    for episode in range(num_episodes):
        obs, info = env.reset()
        done = False
        episode_reward = 0
        step = 0

        print(f"Episode {episode + 1}/{num_episodes}", end=" ")

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        env.close()
                        return
                    if event.key == pygame.K_SPACE:
                        paused = True
                        print("(Paused)", end=" ")
                        while paused:
                            for e in pygame.event.get():
                                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                                    paused = False
                                if e.type == pygame.QUIT:
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

        all_rewards.append(episode_reward)
        all_scores.append(score)
        all_phases.append(phase)
        all_steps.append(step)

        print(
            f"| Score: {score} | Phase: {phase} | Reward: {episode_reward:.1f} | Steps: {step}")
        time.sleep(0.3)

    print("\n" + "=" * 60)
    print("EVALUATION METRICS - ROTATION CONTROL")
    print("=" * 60)
    print(f"Episodes Evaluated:     {num_episodes}")
    print(
        f"Average Reward:         {np.mean(all_rewards):.2f} ± {np.std(all_rewards):.2f}")
    print(
        f"Average Score:          {np.mean(all_scores):.2f} ± {np.std(all_scores):.2f}")
    print(f"Average Phase Reached:  {np.mean(all_phases):.2f}")
    print(f"Max Phase Achieved:     {max(all_phases)}")
    print(f"Average Episode Length: {np. mean(all_steps):.0f} steps")
    print(f"Best Score:             {max(all_scores)}")
    print(f"Worst Score:             {min(all_scores)}")
    print("=" * 60)

    env.close()

    return {
        "avg_reward":  np.mean(all_rewards),
        "std_reward": np.std(all_rewards),
        "avg_score": np. mean(all_scores),
        "std_score": np.std(all_scores),
        "avg_phase": np.mean(all_phases),
        "max_phase": max(all_phases),
        "avg_steps":  np.mean(all_steps)
    }


def evaluate_no_render(model_path=DEFAULT_MODEL_PATH, num_episodes=50):
    """Fast evaluation without rendering."""

    env = RotationEnv(render_mode=None)

    if not model_path.endswith('.zip'):
        if os.path.exists(model_path + '.zip'):
            model_path = model_path + '.zip'

    print(f"Loading model from: {model_path}")
    try:
        model = PPO.load(model_path)
    except Exception as e:
        print(f"Error: {e}")
        return None

    print(f"Fast evaluation over {num_episodes} episodes (no rendering)...\n")

    all_rewards = []
    all_scores = []
    all_phases = []
    all_steps = []

    for episode in range(num_episodes):
        obs, info = env.reset()
        done = False
        episode_reward = 0
        step = 0

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            episode_reward += reward
            step += 1

        all_rewards.append(episode_reward)
        all_scores.append(info.get('score', 0))
        all_phases.append(info.get('phase', 1))
        all_steps.append(step)

        if (episode + 1) % 10 == 0:
            print(f"  Completed {episode + 1}/{num_episodes} episodes...")

    env.close()

    print("\n" + "=" * 60)
    print("EVALUATION METRICS - ROTATION CONTROL")
    print("=" * 60)
    print(f"Episodes Evaluated:     {num_episodes}")
    print(
        f"Average Reward:         {np.mean(all_rewards):.2f} ± {np.std(all_rewards):.2f}")
    print(
        f"Average Score:          {np.mean(all_scores):.2f} ± {np. std(all_scores):.2f}")
    print(f"Average Phase Reached:  {np.mean(all_phases):.2f}")
    print(f"Max Phase Achieved:     {max(all_phases)}")
    print(f"Average Episode Length: {np.mean(all_steps):.0f} steps")
    print(f"Best Score:             {max(all_scores)}")
    print(f"Worst Score:            {min(all_scores)}")
    print("=" * 60)

    return {
        "avg_reward": np.mean(all_rewards),
        "std_reward": np.std(all_rewards),
        "avg_score": np.mean(all_scores),
        "std_score":  np.std(all_scores),
        "avg_phase": np.mean(all_phases),
        "max_phase": max(all_phases),
        "avg_steps": np.mean(all_steps)
    }


def play_manual():
    """Play manually with rotation controls."""

    env = RotationEnv(render_mode="human")
    obs, info = env.reset()

    print("\n" + "=" * 50)
    print("MANUAL PLAY - Rotation Controls")
    print("=" * 50)
    print("W     - Thrust forward")
    print("A     - Rotate left")
    print("D     - Rotate right")
    print("SPACE - Shoot")
    print("Q     - Quit")
    print("=" * 50 + "\n")

    done = False
    total_reward = 0

    while not done:
        action = 0

        for event in pygame.event.get():
            if event.type == pygame. QUIT:
                env.close()
                return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            break
        elif keys[pygame.K_w]:
            action = 1
        elif keys[pygame.K_a]:
            action = 2
        elif keys[pygame.K_d]:
            action = 3
        elif keys[pygame.K_SPACE]:
            action = 4

        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward
        env.render()

    print(
        f"\nGame Over! Score: {info. get('score', 0)} | Phase: {info.get('phase', 1)} | Reward: {total_reward:.2f}")
    env.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["eval", "fast", "play"], default="eval",
                        help="eval=visual, fast=no render (more episodes), play=manual")
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--episodes", type=int, default=5)

    args = parser.parse_args()

    if args.mode == "eval":
        evaluate_agent(args.model, args.episodes)
    elif args.mode == "fast":
        evaluate_no_render(args. model, args.episodes)
    else:
        play_manual()
