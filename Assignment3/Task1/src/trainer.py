"""
Training loop for Q-Learning agent
"""

import pygame
from .environment import GridWorld
from .agent import QLearningAgent
from .renderer import Renderer
from .config import Config


class Trainer:
    """
    Manages the training loop for Q-Learning agent.
    
    Features:
    - Episode management
    - Visualization control (fast/slow mode)
    - Q-table reset (R key)
    - Pygame event handling
    """
    
    def __init__(self, env:  GridWorld, agent: QLearningAgent, 
                 renderer: Renderer, config: Config, level: int = 0):
        """
        Initialize trainer.
        
        Args:
            env: GridWorld environment
            agent: QLearningAgent
            renderer: Pygame renderer
            config: Configuration object
            level: Level number for display
        """
        self. env = env
        self.agent = agent
        self.renderer = renderer
        self.config = config
        self.level = level
        
        self.visualize = True  # Start in visual mode
        self.running = True
    
    def train(self):
        """Main training loop"""
        for episode in range(self.config. episodes):
            if not self.running:
                break
            
            # Update epsilon for this episode
            self.agent. update_epsilon(episode)
            
            # Run one episode
            self._run_episode(episode)
        
        # Cleanup
        self.renderer.quit()
        print(f"✓ Training complete!  {self.config.episodes} episodes")
    
    def _run_episode(self, episode: int):
        """
        Run a single episode.
        
        Args:
            episode: Episode number
        """
        state = self.env.reset()
        total_reward = 0.0
        steps = 0
        
        while self.running:
            # Handle Pygame events
            if not self._handle_events(episode):
                break
            
            # Select action
            action = self.agent.select_action(state)
            
            # Take step in environment
            result = self.env.step(action)
            
            # Update Q-table
            self.agent. update(state, action, result. reward, 
                            result.next_state, result.done)
            
            # Move to next state
            state = result.next_state
            total_reward += result.reward
            steps += 1
            
            # Render
            self._render(episode, steps, total_reward)
            
            # Check if episode is done
            if result.done or steps >= self.config.max_steps:
                # Draw final frame
                self._render(episode, steps, total_reward)
                break
    
    def _handle_events(self, episode: int) -> bool:
        """
        Handle Pygame events.
        
        Args:
            episode: Current episode number
            
        Returns:
            True if should continue, False if should quit
        """
        for event in pygame.event.get():
            if event.type == pygame. QUIT:
                self.running = False
                return False
            
            if event.type == pygame.KEYDOWN:
                # Toggle visualization speed
                if event.key == pygame.K_v:
                    self.visualize = not self. visualize
                    mode = "VISUAL" if self.visualize else "FAST"
                    print(f"→ Switched to {mode} mode")
                
                # Reset Q-table
                if event.key == pygame.K_r:
                    self.agent.reset_q_table()
                    self.env.reset()
                    print("→ Q-table reset!")
                
                # Quit
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
        
        return True
    
    def _render(self, episode: int, steps: int, total_reward: float):
        """
        Render the current state.
        
        Args:
            episode: Current episode
            steps: Steps in current episode
            total_reward:  Total reward accumulated
        """
        self.renderer.draw(
            self.env,
            episode,
            steps,
            self.agent.epsilon,
            total_reward,
            self.level
        )
        
        # Control frame rate
        if self.visualize:
            self. renderer.tick(self.config. fps_visual)
        else:
            # In fast mode, still render occasionally
            if steps % 5 == 0:
                self.renderer.tick(self.config.fps_fast)