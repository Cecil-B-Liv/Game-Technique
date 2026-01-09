"""
Q-Table for storing and retrieving Q-values
"""

from typing import Dict, List, Tuple
from .constants import ALL_ACTIONS


class QTable:
    """
    Q-Table stores Q-values for (state, action) pairs.
    
    Uses a dictionary for sparse storage (only stores visited states).
    Supports random tie-breaking for epsilon-greedy policy.
    """
    
    def __init__(self):
        """Initialize empty Q-table"""
        self.q:  Dict[Tuple, float] = {}
    
    def get(self, state:  Tuple, action: int) -> float:
        """
        Get Q-value for (state, action) pair.
        Returns 0.0 for unseen pairs.
        
        Args:
            state: State tuple
            action: Action index
            
        Returns:
            Q-value (float)
        """
        return self.q.get((state, action), 0.0)
    
    def set(self, state: Tuple, action: int, value: float):
        """
        Set Q-value for (state, action) pair.
        
        Args:
            state: State tuple
            action: Action index
            value: New Q-value
        """
        self.q[(state, action)] = value
    
    def best_value(self, state: Tuple) -> float:
        """
        Get the maximum Q-value for a state across all actions.
        
        Args:
            state: State tuple
            
        Returns:
            Maximum Q-value
        """
        return max(self.get(state, a) for a in ALL_ACTIONS)
    
    def best_actions(self, state: Tuple) -> List[int]:
        """
        Get all actions that have the maximum Q-value for this state.
        Used for random tie-breaking in epsilon-greedy. 
        
        Args:
            state: State tuple
            
        Returns:
            List of action indices with maximum Q-value
        """
        q_values = [self.get(state, a) for a in ALL_ACTIONS]
        max_q = max(q_values)
        return [a for a, q in zip(ALL_ACTIONS, q_values) if q == max_q]
    
    def __len__(self):
        """Return number of (state, action) pairs stored"""
        return len(self. q)
    
    def __repr__(self):
        return f"QTable(size={len(self. q)})"