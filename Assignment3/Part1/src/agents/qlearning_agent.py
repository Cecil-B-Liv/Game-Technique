"""
Q-Learning Agent with Intrinsic Reward Support
"""

import random
from typing import Tuple
from Assignment3.Part1.src.q_table import QTable
from Assignment3.Part1.src.constants import ALL_ACTIONS
from Assignment3.Part1.src.visisit_counter import VisitCounter


def linear_epsilon(episode: int, start: float, end: float, decay_episodes: int) -> float:
    """
    Linear epsilon decay schedule.

    Args:
        episode: Current episode number
        start: Starting epsilon value
        end: Final epsilon value
        decay_episodes: Number of episodes to decay over

    Returns:
        Current epsilon value
    """
    if decay_episodes <= 0:
        return end

    t = min(episode / decay_episodes, 1.0)
    return start + t * (end - start)


class QLearningAgent:
    """
    Q-Learning agent with epsilon-greedy policy and optional intrinsic reward.

    Features:
    - Epsilon-greedy exploration
    - Random tie-breaking
    - Linear epsilon decay
    - Intrinsic reward for exploration
    """

    def __init__(self, alpha: float, gamma: float,
                 epsilon_start: float, epsilon_end: float,
                 epsilon_decay_episodes: int,
                 use_intrinsic_reward: bool = False,
                 intrinsic_strength: float = 0.1):
        """
        Initialize Q-Learning agent.

        Args:
            alpha: Learning rate (0-1)
            gamma: Discount factor (0-1)
            epsilon_start: Initial exploration rate
            epsilon_end: Final exploration rate
            epsilon_decay_episodes: Episodes to decay epsilon over
            use_intrinsic_reward: Whether to use intrinsic reward
            intrinsic_strength: Scaling factor for intrinsic reward
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay_episodes = epsilon_decay_episodes

        self.q_table = QTable()
        self.current_episode = 0
        self.epsilon = epsilon_start

        # Intrinsic reward components
        self.use_intrinsic_reward = use_intrinsic_reward
        self.visit_counter = VisitCounter(intrinsic_strength)

    def reset_counter(self):
        """Reset episode-specific counters (call at start of each episode)"""
        self.visit_counter.reset_counter()

    def select_action(self, state: Tuple) -> int:
        """
        Select action using epsilon-greedy policy with random tie-breaking.

        Args:
            state: Current state tuple

        Returns:
            Action index (0-3)
        """
        # Explore
        if random.random() < self.epsilon:
            return random.choice(ALL_ACTIONS)

        # Exploit with random tie-breaking
        best_actions = self.q_table.best_actions(state)
        return random.choice(best_actions)

    def update(self, state: Tuple, action: int, reward: float,
               next_state: Tuple, done: bool):
        """
        Q-Learning update rule (off-policy) with optional intrinsic reward.

        Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]

        Args:
            state: Current state
            action: Action taken
            reward: Environment reward received
            next_state: Next state after action
            done: Whether episode ended
        """
        # Calculate total reward (environment + intrinsic)
        total_reward = reward

        if self.use_intrinsic_reward:
            # Record visit to next_state and get intrinsic reward
            intrinsic_reward = self.visit_counter.get_intrinsic_reward(next_state)
            self.visit_counter.visit(next_state)
            total_reward += intrinsic_reward

        current_q = self.q_table.get(state, action)

        if done:
            # Terminal state: no future rewards
            target = total_reward
        else:
            # Bootstrap from best next action (off-policy)
            max_next_q = self.q_table.best_value(next_state)
            target = total_reward + self.gamma * max_next_q

        # Update Q-value
        new_q = current_q + self.alpha * (target - current_q)
        self.q_table.set(state, action, new_q)

    def update_epsilon(self, episode: int):
        """
        Update epsilon based on episode number.

        Args:
            episode: Current episode number
        """
        self.current_episode = episode
        self.epsilon = linear_epsilon(
            episode,
            self.epsilon_start,
            self.epsilon_end,
            self.epsilon_decay_episodes
        )

    def reset_q_table(self):
        """Reset Q-table (for R key functionality)"""
        self.q_table = QTable()
        self.current_episode = 0
        self.epsilon = self.epsilon_start
        self.visit_counter.reset_counter()