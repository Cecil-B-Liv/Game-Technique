"""
GridWorld Environment
"""

from dataclasses import dataclass
from typing import Tuple, List, Dict, Set
import random
from .constants import ACTIONS


@dataclass
class StepResult:
    """Result of taking a step in the environment"""
    next_state: Tuple[int, int, int, int, int]  # (agent_x, agent_y, apple_mask, collected_key, chest_mask)
    reward: float
    done: bool
    info: dict


class GridWorld:
    """
    GridWorld environment for reinforcement learning. 
    
    Supports: 
    - Apples (reward +1)
    - Keys and Chests (chest gives +2)
    - Rocks (obstacles)
    - Fire (deadly)
    - Monsters (deadly, can move)
    """
    
    def __init__(self, layout: List[str], monster_move_prob=0.4):
        """
        Initialize GridWorld from a layout. 
        
        Layout symbols:
            S = Start position
            A = Apple (+1 reward)
            K = Key (opens chests)
            C = Chest (+2 reward, needs key)
            R = Rock (obstacle)
            F = Fire (deadly)
            M = Monster (deadly, moves randomly)
            (space) = Empty
            
        Args:
            layout:  List of strings representing the grid
            monster_move_prob: Probability that each monster moves per step
        """
        self. layout = layout
        self.w = len(layout[0])
        self.h = len(layout)
        self.monster_move_prob = monster_move_prob
        
        # Object sets and lists
        self.rocks:  Set[Tuple[int, int]] = set()
        self.fires: Set[Tuple[int, int]] = set()
        self.keys: Set[Tuple[int, int]] = set()

        self.chests: List[Tuple[int, int]] = []
        self.chest_index: Dict[Tuple[int, int], int] = {}

        self.apples: List[Tuple[int, int]] = []
        self.apple_index:  Dict[Tuple[int, int], int] = {}

        self.monsters: List[Tuple[int, int]] = []

        self. start = (0, 0)
        
        # Parse layout
        self._parse_layout()
        
        # Initialize state
        self.reset()
    
    def _parse_layout(self):
        """Parse the layout string into object positions"""
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                pos = (x, y)
                
                if ch == "A":
                    self.apple_index[pos] = len(self.apples)
                    self.apples.append(pos)
                elif ch == "S":
                    self.start = pos
                elif ch == "R":
                    self.rocks. add(pos)
                elif ch == "F":
                    self.fires. add(pos)
                elif ch == "K":
                    self.keys.add(pos)
                elif ch == "C": 
                    self.chest_index[pos] = len(self.chests)
                    self.chests.append(pos)
                elif ch == "M":
                    self.monsters.append(pos)
    
    def reset(self) -> Tuple[int, int, int, int, int]:
        """
        Reset environment to initial state.
        
        Returns:
            Initial state tuple (x, y, apple_mask)
        """
        self.agent = self.start
        self.alive = True

        # Use a set to hold the key collected positions
        self.collected_keys_positions: Set[Tuple[int, int]] = set()
        self.collected_keys = 0

        self.chest_mask = 0
        for i in range(len(self.chests)):
            self.chest_mask |= (1<<i)
        
        # Build apple bitmask (bit i = 1 if apple i is available)
        self.apple_mask = 0
        for i in range(len(self.apples)):
            self.apple_mask |= (1 << i)
        
        # Reset monsters to original positions
        self.current_monsters = self.monsters. copy()
        
        self.step_count = 0
        return self.encode_state()
    
    def encode_state(self) -> Tuple[int, int, int, int, int]:
        """
        Encode current state as a tuple. 
        
        For Level 0: (x, y, apple_mask) is sufficient
        For later levels, you may want to extend this.
        
        Returns:
            State tuple (agent_x, agent_y, apple_mask, collected_key, chest_mask)
        """
        # Count how many keys we're currently holding

        return self.agent[0], self.agent[1], self.apple_mask, self.collected_keys, self.chest_mask
    
    def in_bounds(self, pos:  Tuple[int, int]) -> bool:
        """Check if position is within grid bounds"""
        return 0 <= pos[0] < self.w and 0 <= pos[1] < self.h
    
    def blocked(self, pos: Tuple[int, int]) -> bool:
        """Check if position is blocked by a rock"""
        return pos in self.rocks
    
    def cell_contains_monster(self, pos: Tuple[int, int]) -> bool:
        """Check if position contains a monster"""
        return pos in self. current_monsters
    
    def try_move(self, pos: Tuple[int, int], action: int) -> Tuple[int, int]: 
        """
        Attempt to move from pos in the given action direction.
        Returns new position (or original if blocked).
        
        Args:
            pos: Current position (x, y)
            action:  Action index (0=UP, 1=RIGHT, 2=DOWN, 3=LEFT)
            
        Returns:
            New position after movement
        """
        dx, dy = ACTIONS[action]
        new_pos = (pos[0] + dx, pos[1] + dy)
        
        # Check bounds
        if not self.in_bounds(new_pos):
            return pos
        
        # Check obstacles
        if self.blocked(new_pos):
            return pos
        
        return new_pos
    
    def step(self, action: int) -> StepResult:
        """
        Execute one step in the environment.
        
        Args:
            action: Action to take (0=UP, 1=RIGHT, 2=DOWN, 3=LEFT)
            
        Returns:
            StepResult with (next_state, reward, done, info)
        """
        self.step_count += 1
        reward = 0.0
        done = False
        info = {}
        
        # 1) Move agent
        self.agent = self.try_move(self.agent, action)
        
        # 2) Check for death (fire or monster)
        if self.agent in self.fires or self.cell_contains_monster(self.agent):
            self.alive = False
            info["event"] = "death"
            return StepResult(self.encode_state(), reward, True, info)
        
        # 3) Check for apple collection
        if self.agent in self.apple_index:
            idx = self.apple_index[self.agent]
            # Check if this apple is still available (bit is set)
            if (self.apple_mask >> idx) & 1:
                # Clear the bit (collect the apple)
                self.apple_mask &= ~(1 << idx)
                reward += 1.0
                info["event"] = "apple"
        
        # 4) Check for key collection
        if self.agent in self.keys and self.agent not in self.collected_keys_positions:
            self.collected_keys_positions.add(self.agent)
            self.collected_keys += 1
            info["event"] = "key"
        
        # 5) Check for chest opening
        if self.agent in self.chests and self.collected_keys > 0:
            idx = self.chest_index[self.agent]
            # Check if the chest have opened or not
            if (self.chest_mask >> idx) & 1:
                # Clear the bit (open the chest)
                self.chest_mask &= ~(1 << idx)
                self.collected_keys -= 1
                reward += 2.0
                info["event"] = "chest"
        
        # 6) Move monsters
        self._update_monsters()
        
        # Check if agent is now on a monster after they moved
        if self.cell_contains_monster(self.agent):
            self.alive = False
            info["event"] = "death_by_monster"
            return StepResult(self.encode_state(), reward, True, info)
        
        # 7) Check win condition (all apples collected)
        if self.apple_mask == 0 and self.chest_mask == 0:
            done = True
            info["event"] = "win"
        
        return StepResult(self.encode_state(), reward, done, info)
    
    def _update_monsters(self):
        """Update monster positions (40% chance each monster moves)"""
        new_monsters = []
        
        for monster_pos in self.current_monsters:
            # Random chance to move
            if random.random() < self.monster_move_prob:
                # Try random moves until one works
                actions = list(range(4))
                random.shuffle(actions)
                
                moved = False
                for action in actions:
                    new_pos = self.try_move(monster_pos, action)
                    
                    # Monster moved successfully
                    if new_pos != monster_pos:
                        new_monsters.append(new_pos)
                        moved = True
                        break
                
                # If no valid move, stay in place
                if not moved:
                    new_monsters.append(monster_pos)
            else:
                # Monster doesn't move this turn
                new_monsters.append(monster_pos)
        
        self.current_monsters = new_monsters
    
    def get_apples_remaining(self) -> int:
        """Count how many apples are still available"""
        return bin(self.apple_mask).count('1')

    def get_chests_remaining(self) -> int:
        """Count how many chests are still not opened"""
        return bin(self.chest_mask).count('1')