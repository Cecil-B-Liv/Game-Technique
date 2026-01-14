"""
Training script for directional movement control agent.  
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.env_util import make_vec_env
from envs.directional_env import DirectionalEnv


def train_directional_ppo():
    """Train PPO agent with directional controls."""
    
    # Create directories - SEPARATE folder for directional
    os.makedirs("models/directional", exist_ok=True)
    os.makedirs("logs/directional", exist_ok=True)
    
    n_envs = 4
    
    print("Creating training environments...")
    env = make_vec_env(
        DirectionalEnv,
        n_envs=n_envs,
        monitor_dir="./logs/directional/train_monitor"
    )
    
    eval_env = make_vec_env(
        DirectionalEnv,
        n_envs=1,
        monitor_dir="./logs/directional/eval_monitor"
    )
    
    policy_kwargs = dict(
        net_arch=dict(
            pi=[256, 256],
            vf=[256, 256]
        )
    )
    
    print("Creating PPO model...")
    model = PPO(
        "MlpPolicy",
        env,
        policy_kwargs=policy_kwargs,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        verbose=1,
        tensorboard_log="./logs/directional/tensorboard",
        device="auto"
    )
    
    # Save to DIRECTIONAL folder
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./models/directional/",  # <-- Separate folder
        log_path="./logs/directional/eval/",
        eval_freq=10000 // n_envs,
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        verbose=1
    )
    
    print("\n" + "=" * 60)
    print("TRAINING - DIRECTIONAL CONTROL")
    print("=" * 60)
    print(f"Parallel environments: {n_envs}")
    print(f"Total timesteps: 1,000,000")
    print(f"Best model:  ./models/directional/best_model.zip")
    print()
    print("TensorBoard:  tensorboard --logdir ./logs/directional/tensorboard")
    print("=" * 60 + "\n")
    
    model.learn(
        callback=callbacks,
        total_timesteps=1_000_000,
        callback=eval_callback,
        progress_bar=True
    )
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print("Best model:  ./models/directional/best_model.zip")
    print()
    print("To evaluate:")
    print("  python evaluation/evaluate_directional.py --mode eval")
    print("=" * 60)
    
    env.close()
    eval_env.close()


if __name__ == "__main__":
    train_directional_ppo()