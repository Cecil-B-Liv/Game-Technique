"""
Training script for directional movement control agent.

This script trains an RL agent using PPO (Proximal Policy Optimization).

Key concepts:
- PPO is an "actor-critic" algorithm
- It has two neural networks:  policy (actor) and value (critic)
- Policy network outputs action probabilities
- Value network estimates expected future reward
"""

import os
import sys

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os. path.abspath(__file__))))

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    CheckpointCallback, 
    EvalCallback,
    CallbackList
)
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
from envs.directional_env import DirectionalEnv


def make_env(render_mode=None):
    """Factory function to create environment instances."""
    def _init():
        env = DirectionalEnv(render_mode=render_mode)
        return env
    return _init


def train_directional_ppo():
    """
    Train PPO agent with directional controls.
    
    Training Process:
    1. Create environment(s)
    2. Create PPO model with neural network
    3. Train for many timesteps
    4. Save the trained model
    """
    
    # Create directories for outputs
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # =========================================================================
    # ENVIRONMENT SETUP
    # =========================================================================
    
    # Number of parallel environments
    # More environments = faster training but more memory
    n_envs = 4  # Use 4 parallel environments
    
    # Create vectorized environment (runs multiple envs in parallel)
    # This is MUCH faster than a single environment
    env = make_vec_env(
        DirectionalEnv,
        n_envs=n_envs,
        monitor_dir="./logs/train_monitor"
    )
    
    # Create separate evaluation environment
    eval_env = make_vec_env(
        DirectionalEnv,
        n_envs=1,
        monitor_dir="./logs/eval_monitor"
    )
    
    # =========================================================================
    # MODEL CONFIGURATION
    # =========================================================================
    
    # Neural network architecture
    # pi = policy network (decides actions)
    # vf = value function network (estimates rewards)
    policy_kwargs = dict(
        net_arch=dict(
            pi=[256, 256],  # Policy:  2 hidden layers, 256 neurons each
            vf=[256, 256]   # Value: 2 hidden layers, 256 neurons each
        )
    )
    
    # Create PPO model
    model = PPO(
        # Policy type:  MLP (Multi-Layer Perceptron) for vector observations
        "MlpPolicy",
        
        # The environment to train on
        env,
        
        # Neural network configuration
        policy_kwargs=policy_kwargs,
        
        # Learning rate:  How fast to update weights
        # Too high = unstable, too low = slow learning
        learning_rate=3e-4,
        
        # Number of steps to collect before each update
        # Higher = more stable but slower
        n_steps=2048,
        
        # Mini-batch size for gradient updates
        batch_size=64,
        
        # Number of epochs per update
        # More epochs = more learning per batch
        n_epochs=10,
        
        # Discount factor:  How much to value future rewards
        # 0.99 means future rewards are almost as valuable as immediate
        gamma=0.99,
        
        # GAE lambda:  For advantage estimation
        # Higher = less bias, more variance
        gae_lambda=0.95,
        
        # Clipping range:  Limits policy updates
        # Prevents too-large changes that destabilize training
        clip_range=0.2,
        
        # Entropy coefficient:  Encourages exploration
        # Higher = more random actions (explore more)
        ent_coef=0.01,
        
        # Print training info
        verbose=1,
        
        # TensorBoard logging directory
        tensorboard_log="./logs/directional_ppo",
        
        # Device:  "auto" will use GPU if available
        device="auto"
    )
    
    # =========================================================================
    # CALLBACKS
    # =========================================================================
    
    # Save model periodically during training
    checkpoint_callback = CheckpointCallback(
        save_freq=25000 // n_envs,  # Save every 25000 total steps
        save_path="./models/",
        name_prefix="directional_ppo"
    )
    
    # Evaluate model periodically and save best version
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./models/best_directional_ppo/",
        log_path="./logs/eval/",
        eval_freq=10000 // n_envs,  # Evaluate every 10000 steps
        n_eval_episodes=5,          # Average over 5 episodes
        deterministic=True,         # Use deterministic actions for eval
        render=False                # Don't render during eval
    )
    
    callbacks = CallbackList([checkpoint_callback, eval_callback])
    
    # =========================================================================
    # TRAINING
    # =========================================================================
    
    print("=" * 60)
    print("Starting training for directional control (PPO)")
    print("=" * 60)
    print(f"Parallel environments: {n_envs}")
    print(f"Network architecture: {policy_kwargs}")
    print(f"Total timesteps: 1,000,000")
    print()
    print("Monitor progress with TensorBoard:")
    print("  tensorboard --logdir ./logs")
    print("=" * 60)
    
    # Train the model
    model.learn(
        total_timesteps=1_000_000,  # Train for 1 million steps
        callback=callbacks,
        progress_bar=True
    )
    
    # Save final model
    model.save("./models/directional_ppo_final")
    print("\nTraining complete!")
    print("Final model saved to:  ./models/directional_ppo_final")
    print("Best model saved to: ./models/best_directional_ppo/best_model")
    
    # Clean up
    env.close()
    eval_env.close()


if __name__ == "__main__":
    train_directional_ppo()