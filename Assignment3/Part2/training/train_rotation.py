"""Training script for rotation-based control agent."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO, DQN
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from envs.rotation_env import RotationEnv


def train_rotation_ppo():
    """Train PPO agent with rotation controls."""
    
    # Create directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Create environment
    env = RotationEnv(render_mode=None)
    env = Monitor(env)
    
    # Create evaluation environment
    eval_env = RotationEnv(render_mode=None)
    eval_env = Monitor(eval_env)
    
    # PPO with custom neural network
    # policy_kwargs defines the network architecture
    policy_kwargs = dict(
        net_arch=dict(
            pi=[128, 128],  # Policy network:  2 hidden layers with 128 units
            vf=[128, 128]   # Value network: 2 hidden layers with 128 units
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
        tensorboard_log="./logs/rotation_ppo"
    )
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="./models/",
        name_prefix="rotation_ppo"
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./models/best_rotation_ppo/",
        log_path="./logs/",
        eval_freq=5000,
        deterministic=True,
        render=False
    )
    
    # Train
    print("Starting training for rotation-based control (PPO)...")
    print("This may take a while.  Monitor progress with TensorBoard:")
    print("  tensorboard --logdir ./logs")
    
    model.learn(
        total_timesteps=500000,
        callback=[checkpoint_callback, eval_callback],
        progress_bar=True
    )
    
    # Save final model
    model.save("./models/rotation_ppo_final")
    print("Training complete!  Model saved to ./models/rotation_ppo_final")
    
    env.close()
    eval_env.close()


def train_rotation_dqn():
    """Train DQN agent with rotation controls (alternative)."""
    
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    env = RotationEnv(render_mode=None)
    env = Monitor(env)
    
    # DQN with custom network
    policy_kwargs = dict(
        net_arch=[128, 128]  # 2 hidden layers
    )
    
    model = DQN(
        "MlpPolicy",
        env,
        policy_kwargs=policy_kwargs,
        learning_rate=1e-4,
        buffer_size=100000,
        learning_starts=1000,
        batch_size=64,
        tau=0.005,
        gamma=0.99,
        train_freq=4,
        target_update_interval=1000,
        exploration_fraction=0.3,
        exploration_final_eps=0.05,
        verbose=1,
        tensorboard_log="./logs/rotation_dqn"
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path="./models/",
        name_prefix="rotation_dqn"
    )
    
    print("Starting training for rotation-based control (DQN)...")
    model.learn(
        total_timesteps=300000,
        callback=checkpoint_callback,
        progress_bar=True
    )
    
    model.save("./models/rotation_dqn_final")
    print("Training complete! Model saved to ./models/rotation_dqn_final")
    
    env.close()


if __name__ == "__main__":
    # Choose one: 
    train_rotation_ppo()  # Recommended for this task
    # train_rotation_dqn()  # Alternative