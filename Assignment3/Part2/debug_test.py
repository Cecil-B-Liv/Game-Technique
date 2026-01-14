"""
Debug script to verify everything works before training.
Run this first to catch errors quickly.
"""

import sys
import os
sys.path. insert(0, os.path. dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        import pygame
        print("  ✓ pygame")
        import gymnasium
        print("  ✓ gymnasium")
        import numpy as np
        print("  ✓ numpy")
        from stable_baselines3 import PPO
        print("  ✓ stable_baselines3")
        import tensorboard
        print("  ✓ tensorboard")
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    return True


def test_game_modules():
    """Test that our game modules load."""
    print("\nTesting game modules...")
    try:
        from game.constants import SCREEN_WIDTH, PLAYER_SPEED
        print(f"  ✓ constants (SCREEN_WIDTH={SCREEN_WIDTH})")
        from game.entities import Player, Enemy, Spawner, Projectile
        print("  ✓ entities")
        from game.arena import Arena
        print("  ✓ arena")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    return True


def test_environments():
    """Test that environments work correctly."""
    print("\nTesting environments...")
    try:
        from envs.directional_env import DirectionalEnv
        from envs.rotation_env import RotationEnv
        
        # Test directional env
        env = DirectionalEnv(render_mode=None)
        obs, info = env.reset()
        print(f"  ✓ DirectionalEnv created")
        print(f"    Observation shape: {obs.shape}")
        print(f"    Observation range: [{obs.min():.2f}, {obs.max():.2f}]")
        print(f"    Action space: {env.action_space}")
        
        # Take a few random steps
        for i in range(10):
            action = env.action_space.sample()
            obs, reward, term, trunc, info = env.step(action)
        print(f"  ✓ DirectionalEnv step() works")
        env.close()
        
        # Test rotation env
        env = RotationEnv(render_mode=None)
        obs, info = env.reset()
        print(f"  ✓ RotationEnv created")
        print(f"    Action space: {env.action_space}")
        env.close()
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    return True


def test_training_setup():
    """Test that PPO can be created with our env."""
    print("\nTesting training setup...")
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.env_util import make_vec_env
        from envs.directional_env import DirectionalEnv
        
        # Create vectorized environment
        env = make_vec_env(DirectionalEnv, n_envs=2)
        print("  ✓ Vectorized environment created")
        
        # Create model
        model = PPO(
            "MlpPolicy",
            env,
            verbose=0,
            n_steps=64,  # Small for testing
            batch_size=32
        )
        print("  ✓ PPO model created")
        
        # Train for a tiny bit
        model.learn(total_timesteps=100)
        print("  ✓ Training works")
        
        # Test prediction
        obs = env.reset()
        action, _ = model.predict(obs, deterministic=True)
        print(f"  ✓ Prediction works (action: {action})")
        
        env.close()
        
    except Exception as e: 
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    return True


def test_rendering():
    """Test that rendering works (optional - requires display)."""
    print("\nTesting rendering (will open a window briefly)...")
    try:
        from envs.directional_env import DirectionalEnv
        import pygame
        
        env = DirectionalEnv(render_mode="human")
        obs, info = env.reset()
        
        # Run for 60 frames (1 second)
        for i in range(60):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
            action = env.action_space.sample()
            obs, reward, term, trunc, info = env.step(action)
            env.render()
            if term or trunc:
                obs, info = env.reset()
                
        env.close()
        print("  ✓ Rendering works")
        
    except Exception as e:
        print(f"  ✗ Error (may be OK if no display): {e}")
        return False
    return True


if __name__ == "__main__": 
    print("=" * 60)
    print("RL ARENA DEBUG TEST")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Game Modules", test_game_modules()))
    results.append(("Environments", test_environments()))
    results.append(("Training Setup", test_training_setup()))
    
    # Only test rendering if --render flag is passed
    if "--render" in sys.argv:
        results.append(("Rendering", test_rendering()))
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("All tests passed!  You can start training.")
        print("\nNext steps:")
        print("  1. python evaluation/evaluate_directional.py --mode play")
        print("     (Play manually to understand the game)")
        print("  2. python training/train_directional.py")
        print("     (Train the AI)")
    else:
        print("Some tests failed. Fix the errors above before training.")