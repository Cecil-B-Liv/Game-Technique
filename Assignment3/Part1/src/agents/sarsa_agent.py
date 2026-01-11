"""
SARSA Reinforcement Learning Agent
"""

import random
from typing import Tuple
from Assignment3.Part1.src.q_table import QTable
from Assignment3.Part1.src.constants import ALL_ACTIONS


def linear_epsilon(episode: int, start: float, end: float, decay_episodes: int) -> float:
    """
    Linear epsilon decay schedule.

    Args:
        episode: Current episode number
        start: Starting epsilon value
        end: Final epsilon value
        decay_episodes:  Number of episodes to decay over

    Returns:
        Current epsilon value
    """
    if decay_episodes <= 0:
        return end

    t = min(episode / decay_episodes, 1.0)
    return start + t * (end - start)

class SARSAAgent:
    """
    SARSA agent with epsilon-greedy policy (on-policy).

    Features:
    - Epsilon-greedy exploration
    - Random tie-breaking
    - Linear epsilon decay
    - On-policy TD update
    """

    def __init__(self, alpha: float, gamma: float,
                 epsilon_start: float, epsilon_end: float,
                 epsilon_decay_episodes: int):

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay_episodes = epsilon_decay_episodes

        self.q_table = QTable()
        self.current_episode = 0
        self.epsilon = epsilon_start


    def select_action(self, state: Tuple) -> int:
        """
        Select action using epsilon-greedy policy.
        (This is BOTH behavior and learning policy in SARSA)
        """
        # Explore
        if random.random() < self.epsilon:
            return random.choice(ALL_ACTIONS)

        # Exploit with random tie-breaking
        best_actions = self.q_table.best_actions(state)
        return random.choice(best_actions)

    def update(self, state: Tuple, action: int, reward: float,
               next_state: Tuple, next_action: int, done: bool):
        """
        SARSA update rule (on-policy).

        Q(s,a) ← Q(s,a) + α[r + γ·Q(s',a') - Q(s,a)]
        """
        current_q = self.q_table.get(state, action)

        if done:
            target = reward
        else:
            next_q = self.q_table.get(next_state, next_action)
            target = reward + self.gamma * next_q

        new_q = current_q + self.alpha * (target - current_q)
        self.q_table.set(state, action, new_q)

    def update_epsilon(self, episode: int):
        """
        Update epsilon based on episode number.
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
