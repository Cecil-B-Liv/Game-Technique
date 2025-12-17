from game import Connect4State
import random
from config import PLAYER1, PLAYER2, AI_ITER


class MCTSNode:
    """
    Node in the MCTS tree.

    - Stores a Connect4State instance, its parent node, and the move leading to it.
    - Tracks visits, wins, and unexplored moves.
    """

    def __init__(self, state, parent=None, move=None):
        """
        Initialize the MCTS node with a given state, parent, and move.
        """
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = state.get_legal_moves()  # Legal moves not yet tried

    def is_fully_expanded(self):
        """
        Check if all legal moves have been tried from this node.
        """
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.4):
        """
        Select the best child node using the UCT (Upper Confidence Bound) formula.
        """
        import math
        return max(
            self.children,
            key=lambda child: (child.wins / child.visits) + c_param * math.sqrt(
                (2 * math.log(self.visits) / child.visits)
            )
        )

    def most_visited_child(self):
        """
        Return the most visited child node.
        """
        return max(self.children, key=lambda child: child.visits, default=None)


def rollout(state, root_player):
    """
    Perform a random simulation (rollout) until the game ends.

    - Returns 1.0 if the root player wins, 0.0 for loss, 0.5 for draw.
    """
    temp_state = state.clone()

    while not temp_state.is_terminal():
        legal_moves = temp_state.get_legal_moves()
        move = random.choice(legal_moves)
        temp_state.make_move(move)

    winner = temp_state.check_winner()
    if winner == root_player:
        return 1.0
    elif winner is None:
        return 0.5
    else:
        return 0.0


def mcts_search(root_state, n_iter=400):
    """
    Perform Monte Carlo Tree Search (MCTS) to compute the best move.

    - root_state: The current game state.
    - n_iter: Number of iterations for the MCTS algorithm.
    """
    if root_state.is_terminal():
        return None

    root_player = root_state.current_player
    root_node = MCTSNode(root_state.clone())

    for _ in range(n_iter):
        # Selection
        node = root_node
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
        while node:
            node.visits += 1
            node.wins += reward
            node = node.parent

    best_child = root_node.most_visited_child()
    return best_child.move if best_child else None


def ai_play_move(state, n_iter=None):
    """
    AI plays a move using MCTS.

    Arguments:
        state: The current state of the game.
        n_iter: Number of MCTS iterations (None defaults to the player's iteration value in AI_ITER).

    Returns:
        The column index of the move played.
    """
    if n_iter is None:
        # Use `AI_ITER` based on the current player
        n_iter = AI_ITER[state.current_player]

    move = mcts_search(state, n_iter=n_iter)
    if move is not None:
        state.make_move(move)  # Apply the move
    return move
