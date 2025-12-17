from game import Connect4State
import random

from config import PLAYER1, PLAYER2

AI_PROFILES = {
    "easy": 100,
    "medium": 400,
    "hard": 1200,
}

class MCTSNode:
    """
    Node in the MCTS tree.

    It stores:
    - state: a Connect4State instance
    - parent: parent node in the tree (None for root)
    - move: the move (column index) that led from the parent state to this state
    - children: list of child MCTSNode objects
    - visits: how many times this node was visited in the search
    - wins: total reward from the root player's perspective
    """

    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = state.get_legal_moves()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.4):
        import math
        choices_weights = [
            (child.wins / child.visits) + c_param *
            math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

    def most_visited_child(self):
        if not self.children:
            return None
        return max(self.children, key=lambda c: c.visits)
    

def rollout(state, root_player):
    temp_state = state.clone()
    while not temp_state.is_terminal():
        legal_moves = temp_state.get_legal_moves()
        if not legal_moves:
            break
        move = random.choice(legal_moves)
        temp_state.make_move(move)
    winner = temp_state.check_winner()
    if winner is None:
        return 0.5
    if winner == root_player:
        return 1.0
    else:
        return 0.0


def mcts_search(root_state, n_iter=400):
    if root_state.is_terminal():
        return None
    root_player = root_state.current_player
    root_node = MCTSNode(root_state.clone())
    for _ in range(n_iter):
        node = root_node
        # Selection
        while node.is_fully_expanded() and node.children:
            node = node.best_child()
        # Expansion
        if not node.is_fully_expanded():
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            next_state = node.state.clone()
            next_state.make_move(move)
            child_node = MCTSNode(next_state, parent=node, move=move)
            node.children.append(child_node)
            node = child_node
        # Simulation
        reward = rollout(node.state, root_player)
        # Backpropagation
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent
    best_child = root_node.most_visited_child()
    if best_child is None:
        return None
    return best_child.move


# def ai_play_move(state, n_iter=500):
#     move = mcts_search(state, n_iter)
#     if move is not None:
#         state.make_move(move)
#     return move

def ai_play_move(state, n_iter=None, profile=None):
    # 1. Immediate win
    win_move = find_immediate_win(state)
    if win_move is not None:
        state.make_move(win_move)
        return win_move

    # 2. Immediate block
    block_move = find_immediate_block(state)
    if block_move is not None:
        state.make_move(block_move)
        return block_move

    # 3. MCTS fallback
    if profile is not None:
        n_iter = AI_PROFILES.get(profile, 400)
    elif n_iter is None:
        n_iter = 400

    move = mcts_search(state, n_iter=n_iter)
    if move is not None:
        state.make_move(move)
    return move


def find_immediate_win(state):
    for move in state.get_legal_moves():
        temp = state.clone()
        temp.make_move(move)
        if temp.check_winner() == state.current_player:
            return move
    return None

def find_immediate_block(state):
    opponent = PLAYER1 if state.current_player == PLAYER2 else PLAYER2

    for move in state.get_legal_moves():
        temp = state.clone()
        temp.make_move(move)
        if temp.check_winner() == opponent:
            return move
    return None

