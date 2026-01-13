"""Training script for directional movement control agent."""

import os
import sys
sys.path.insert(0, os.path.dirname(os. path.dirname(os.path. abspath(__file__))))

from stable_baselines3 import PPO, DQN
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from envs.directional_env import DirectionalEnv


def train_directional_ppo():
    """Train PPO agent with directional controls."""
    
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    env = DirectionalEnv(render_mode=None)
    env = Monitor(env)
    
    eval_env = DirectionalEnv(render_mode=None)
    eval_env = Monitor(eval_env)
    
    policy_kwargs = dict(
        net_arch=dict(
            pi=[128, 128],
            vf=[128, 128]
        )
    )
    
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
        verbose=1,
        tensorboard_log="./logs/directional_ppo"
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="./models/",
        name_prefix="directional_ppo"
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./models/best_directional_ppo/",
        log_path="./logs/",
        eval_freq=5000,
        deterministic=True,
        render=False
    )
    
    print("Starting training for directional control (PPO)...")
    print("Monitor with:  tensorboard --logdir ./logs")
    
    model.learn(
        total_timesteps=500000,
        callback=[checkpoint_callback, eval_callback],
        progress_bar=True
    )
    
    model.save("./models/directional_ppo_final")
    print("Training complete! Model saved to ./models/directional_ppo_final")
    
    env.close()
    eval_env.close()


if __name__ == "__main__": 
    train_directional_ppo()