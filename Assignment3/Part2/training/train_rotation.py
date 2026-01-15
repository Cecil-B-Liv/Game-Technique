"""
Training script for rotation-based control agent. 
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.rotation_env import RotationEnv
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3 import PPO


def train_rotation_ppo():
    """Train PPO agent with rotation controls - saves ONLY the best model."""

    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    n_envs = 16

    print("Creating training environments...")
    env = make_vec_env(
        RotationEnv,
        n_envs=n_envs,
        monitor_dir="./logs/rotation_train_monitor"
    )

    eval_env = make_vec_env(
        RotationEnv,
        n_envs=1,
        monitor_dir="./logs/rotation_eval_monitor"
    )

    policy_kwargs = dict(
        net_arch=dict(
            pi=[256, 256, 128],
            vf=[256, 256, 128]
        )
    )

    print("Creating PPO model...")
    model = PPO(
        "MlpPolicy",
        env,
        policy_kwargs=policy_kwargs,
        learning_rate=1e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.02,
        verbose=1,
        tensorboard_log="./logs/rotation_ppo",
        device="auto"
    )

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./models/rotation/",
        log_path="./logs/rotation_eval/",
        eval_freq=10000 // n_envs,
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        verbose=1
    )

    print("\n" + "=" * 60)
    print("TRAINING - ROTATION CONTROL (PPO)")
    print("=" * 60)
    print(f"Parallel environments: {n_envs}")
    print(f"Total timesteps: 3,000,000")
    print(f"Best model saved to: ./models/rotation/best_model.zip")
    print("=" * 60 + "\n")

    model.learn(
        total_timesteps=3_000_000,
        callback=eval_callback,
        progress_bar=True
    )

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Best model saved to: ./models/rotation/best_model.zip")
    print()
    print("To evaluate:")
    print("  python evaluation/evaluate_rotation.py --mode eval --model ./models/rotation/best_model")
    print("=" * 60)

    env.close()
    eval_env.close()


if __name__ == "__main__":
    train_rotation_ppo()
