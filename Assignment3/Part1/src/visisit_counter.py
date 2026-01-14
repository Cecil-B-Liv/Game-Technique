"""
Visit Counter for Intrinsic Reward Calculation
"""

from typing import Dict, Tuple
import math


class VisitCounter:
    def __init__(self, intrinsic_strength: float = 0.1):
        self.intrinsic_strength = intrinsic_strength
        self.visit_counts: Dict[Tuple, int] = {}      # (State / Number of Visit)
        self.step_penalty = 0.01

    def reset_counter(self):
        """Clear the calculation at the end of each episode"""
        self.visit_counts.clear()

    def visit(self, state: Tuple) -> int:
        """
        Record a visit to a state and return the visit count.
        """
        intrinsic_state = (state[0], state[1])
        if intrinsic_state not in self.visit_counts:
            self.visit_counts[intrinsic_state] = 0
        self.visit_counts[intrinsic_state] += 1
        return self.visit_counts[intrinsic_state]

    def get_intrinsic_reward(self, state: Tuple) -> float:
        """
        Calculate intrinsic reward for visiting a state.
        Formula: r_i = intrinsic_strength / sqrt(n(s) + 1)
        """
        intrinsic_state = (state[0], state[1])
        number_of_visit = self.visit_counts.get(intrinsic_state, 0)
        return self.intrinsic_strength / math.sqrt(number_of_visit + 1)

    def get_visit_count(self, state: Tuple) -> int:
        intrinsic_state = (state[0], state[1])
        return self.visit_counts.get(intrinsic_state, 0)