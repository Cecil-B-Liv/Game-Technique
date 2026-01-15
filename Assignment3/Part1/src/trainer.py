"""
Training loop for Q-Learning agent with Intrinsic Reward support
"""

import pygame
from .environment import GridWorld
from .renderer import Renderer
from .config import Config
import matplotlib.pyplot as plt


class Trainer:
    """
    Manages the training loop for Q-Learning agent.

    Features:
    - Episode management
    - Visualization control (fast/slow mode)
    - Q-table reset (R key)
    - Pygame event handling
    - Intrinsic reward support
    """

    def __init__(self, env: GridWorld, agent,
                 renderer: Renderer, config: Config, level: int = 0, agent_name: str = "Unknown",
                 screen_side: str = "single"):
        """
        Initialize trainer.

        Args:
            env: GridWorld environment
            agent: QLearningAgent or SARSAAgent
            renderer: Pygame renderer
            config: Configuration object
            level: Level number for display
            agent_name: Name of the agent for display
            screen_side: 'single', 'left', or 'right' for dual mode
        """
        self.env = env
        self.agent = agent
        self.renderer = renderer
        self.config = config
        self.level = level
        self.agent_name = agent_name
        self.screen_side = screen_side

        self.visualize = True  # Start in visual mode
        self.running = True

        # Use for plotting the learning curve
        self.episode_returns = []

    def train(self):
        """Main training loop"""
        for episode in range(self.config.episodes):
            if not self.running:
                break

            # Update epsilon for this episode
            self.agent.update_epsilon(episode)

            # Reset episode-specific counters (for intrinsic reward)
            if self.agent.use_intrinsic_reward:
                self.agent.reset_counter()

            # Run one episode
            self._run_episode(episode)

        # Cleanup
        self._plot_learning_curve()
        print(f"✓ Training complete! {self.config.episodes} episodes")

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

            # SARSA
            if self.agent.__class__.__name__ == "SARSAAgent":
                # SARSA: choose next action BEFORE update
                next_action = self.agent.select_action(result.next_state)

                self.agent.update(
                    state, action, result.reward,
                    result.next_state, next_action, result.done
                )
            # Q-learning
            else:
                self.agent.update(
                    state, action, result.reward,
                    result.next_state, result.done
                )

            # Move to next state
            state = result.next_state

            # Track environment reward only (not intrinsic) for plotting
            total_reward += result.reward
            steps += 1

            # Render
            self._render(episode, steps, total_reward)

            # Check if episode is done
            if result.done or steps >= self.config.max_steps:
                # Draw final frame
                self._render(episode, steps, total_reward)

                # Get value for plotting learning curve
                self.episode_returns.append(total_reward)
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
            if event.type == pygame.QUIT:
                self.running = False
                return False

            if event.type == pygame.KEYDOWN:
                # Toggle visualization speed
                if event.key == pygame.K_v:
                    self.visualize = not self.visualize
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
            total_reward: Total reward accumulated
        """
        self.renderer.draw(
            self.env,
            episode,
            steps,
            self.agent.epsilon,
            total_reward,
            self.level,
            agent_name=self.agent_name
        )

        # Control frame rate
        if self.visualize:
            self.renderer.tick(self.config.fps_visual)
        else:
            # In fast mode, still render occasionally
            if steps % 5 == 0:
                self.renderer.tick(self.config.fps_fast)

    def _plot_learning_curve(self):
        """Plot the learning curve after training"""
        algo_name = self.agent.__class__.__name__.replace("Agent", "")
        intrinsic_label = " (with Intrinsic)" if self.agent.use_intrinsic_reward else ""

        plt.figure(figsize=(8, 5))
        plt.plot(self.episode_returns, alpha=0.4, label="Episode Return")

        # Moving average (smooth)
        window = int(self.config.episodes * 0.025)
        if len(self.episode_returns) >= window:
            ma = [
                sum(self.episode_returns[i:i + window]) / window
                for i in range(len(self.episode_returns) - window + 1)
            ]
            plt.plot(
                range(window - 1, len(self.episode_returns)),
                ma,
                linewidth=2,
                label=f"Moving Avg ({window})"
            )

        plt.xlabel("Episode")
        plt.ylabel("Total Reward")
        plt.title(f"{algo_name}{intrinsic_label} Learning Curve (Level {self.level})")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

    def train_dual(self, other_trainer):
        """Train two agents side-by-side with synchronized episodes and steps"""
        for episode in range(self.config.episodes):
            if not self.running:
                break

            # Update epsilon for both agents
            self.agent.update_epsilon(episode)
            other_trainer.agent.update_epsilon(episode)

            # Reset counters for intrinsic reward
            if self.agent.use_intrinsic_reward:
                self.agent.reset_counter()
            if other_trainer.agent.use_intrinsic_reward:
                other_trainer.agent.reset_counter()

            # Run both agents simultaneously (step-by-step)
            self._run_episode_dual_synchronized(episode, other_trainer)

            if not self.running:
                break

        # Plot both learning curves separately
        self._plot_dual_curves(other_trainer)
        print(f"✓ Dual training complete! {self.config.episodes} episodes")

    def _run_episode_dual_synchronized(self, episode: int, other_trainer):
        """Run both agents simultaneously, step-by-step"""
        # Reset both environments
        state1 = self.env.reset()
        state2 = other_trainer.env.reset()
        
        total_reward1 = 0.0
        total_reward2 = 0.0
        steps1 = 0
        steps2 = 0
        
        done1 = False
        done2 = False

        while self.running and (not done1 or not done2):
            # Handle events
            if not self._handle_events(episode):
                break

            # Agent 1 (left) step
            if not done1:
                action1 = self.agent.select_action(state1)
                result1 = self.env.step(action1)

                # Update agent 1
                if self.agent.__class__.__name__ == "SARSAAgent":
                    next_action1 = self.agent.select_action(result1.next_state)
                    self.agent.update(
                        state1, action1, result1.reward,
                        result1.next_state, next_action1, result1.done
                    )
                else:
                    self.agent.update(
                        state1, action1, result1.reward,
                        result1.next_state, result1.done
                    )

                state1 = result1.next_state
                total_reward1 += result1.reward
                steps1 += 1
                done1 = result1.done or steps1 >= self.config.max_steps

            # Agent 2 (right) step
            if not done2:
                action2 = other_trainer.agent.select_action(state2)
                result2 = other_trainer.env.step(action2)

                # Update agent 2
                if other_trainer.agent.__class__.__name__ == "SARSAAgent":
                    next_action2 = other_trainer.agent.select_action(result2.next_state)
                    other_trainer.agent.update(
                        state2, action2, result2.reward,
                        result2.next_state, next_action2, result2.done
                    )
                else:
                    other_trainer.agent.update(
                        state2, action2, result2.reward,
                        result2.next_state, result2.done
                    )

                state2 = result2.next_state
                total_reward2 += result2.reward
                steps2 += 1
                done2 = result2.done or steps2 >= self.config.max_steps

            # Render both agents with their own step counts
            self._render_dual(episode, steps1, steps2, total_reward1, total_reward2, other_trainer)

            # Check if both are done
            if done1 and done2:
                break
            
        self._render_dual(episode, steps1, steps2, total_reward1, total_reward2, other_trainer)
        # Record episode returns
        self.episode_returns.append(total_reward1)
        other_trainer.episode_returns.append(total_reward2)

    def _render_dual(self, episode: int, steps1: int, steps2: int, reward1: float, reward2: float, other_trainer):
        """Render both agents side-by-side"""
        self.renderer.draw_dual(
            self.env, other_trainer.env,
            episode, steps1, steps2,
            self.agent.epsilon, other_trainer.agent.epsilon,
            reward1, reward2,
            self.level,
            self.agent_name, other_trainer.agent_name
        )

        # Control frame rate
        if self.visualize:
            self.renderer.tick(self.config.fps_visual)
        else:
            # Use max of both step counts for frame rate control
            if max(steps1, steps2) % 5 == 0:
                self.renderer.tick(self.config.fps_fast)

    def _plot_dual_curves(self, other_trainer):
        """Plot two separate learning curves for comparison"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))

        # Calculate shared y-axis limits for easier comparison
        all_returns = self.episode_returns + other_trainer.episode_returns
        y_min = min(all_returns)
        y_max = max(all_returns)
        y_margin = (y_max - y_min) * 0.1  # Add 10% margin
        shared_ylim = (y_min - y_margin, y_max + y_margin)

        # Agent 1 plot
        algo_name1 = self.agent.__class__.__name__.replace("Agent", "")
        intrinsic_label1 = " +IR" if self.agent.use_intrinsic_reward else ""
        
        ax1.plot(self.episode_returns, alpha=0.4, color='blue', label="Episode Return")
        window = int(self.config.episodes * 0.025)
        if len(self.episode_returns) >= window:
            ma = [
                sum(self.episode_returns[i:i + window]) / window
                for i in range(len(self.episode_returns) - window + 1)
            ]
            ax1.plot(
                range(window - 1, len(self.episode_returns)),
                ma,
                linewidth=2,
                color='darkblue',
                label=f"Moving Avg ({window})"
            )
        ax1.set_xlabel("Episode")
        ax1.set_ylabel("Total Reward")
        ax1.set_title(f"{algo_name1}{intrinsic_label1} (Level {self.level})")
        ax1.set_ylim(shared_ylim)  # Apply shared y-axis scale
        ax1.legend()
        ax1.grid()

        # Agent 2 plot
        algo_name2 = other_trainer.agent.__class__.__name__.replace("Agent", "")
        intrinsic_label2 = " +IR" if other_trainer.agent.use_intrinsic_reward else ""
        
        ax2.plot(other_trainer.episode_returns, alpha=0.4, color='red', label="Episode Return")
        if len(other_trainer.episode_returns) >= window:
            ma = [
                sum(other_trainer.episode_returns[i:i + window]) / window
                for i in range(len(other_trainer.episode_returns) - window + 1)
            ]
            ax2.plot(
                range(window - 1, len(other_trainer.episode_returns)),
                ma,
                linewidth=2,
                color='darkred',
                label=f"Moving Avg ({window})"
            )
        ax2.set_xlabel("Episode")
        ax2.set_ylabel("Total Reward")
        ax2.set_title(f"{algo_name2}{intrinsic_label2} (Level {self.level})")
        ax2.set_ylim(shared_ylim)  # Apply shared y-axis scale
        ax2.legend()
        ax2.grid()

        plt.tight_layout()
        plt.show()