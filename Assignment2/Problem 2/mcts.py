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

    def get_ucb_score(self, c_param=1.4):
        """
        Calculate the UCB score for this node.
        """
        import math
        if self.visits == 0 or self.parent is None:
            return 0.0
        exploitation = self.wins / self.visits
        exploration = c_param * \
            math.sqrt((2 * math.log(self.parent.visits) / self.visits))
        return exploitation + exploration

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
    UCB scores are calculated for all child nodes.
    UCB is defined as:
        UCB = (wins / visits) + c * sqrt( (2 * ln(parent_visits)) / visits )
        which is a combination of exploitation (average reward) and exploration (uncertainty). 

    - root_state: The current game state.
    - n_iter: Number of iterations for the MCTS algorithm.

    Returns:
        A tuple (best_move, mcts_stats) where mcts_stats contains visit counts and UCB scores
    """
    if root_state.is_terminal():
        return None, {}

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

    # Collect statistics for all children
    mcts_stats = {
        'visits': {},
        'win_rates': {},
        'ucb_scores': {},
        'best_move': best_child.move if best_child else None,
        'best_ucb': best_child.get_ucb_score() if best_child else 0.0
    }

    for child in root_node.children:
        col = child.move
        mcts_stats['visits'][col] = child.visits
        mcts_stats['win_rates'][col] = child.wins / \
            child.visits if child.visits > 0 else 0.0
        mcts_stats['ucb_scores'][col] = child.get_ucb_score()

    return best_child.move if best_child else None, mcts_stats


def analyze_move_win_rates(root_state, n_iter=400):
    """
    Analyze all legal moves and return their win rates and visit counts for the current player.

    Arguments:
        root_state: The current game state.
        n_iter: Number of MCTS iterations for analysis.

    Returns:
        A dictionary with 'win_rates', 'visits', and 'ucb_scores' for each column
    """
    if root_state.is_terminal():
        return {'win_rates': {}, 'visits': {}, 'ucb_scores': {}}

    root_player = root_state.current_player
    root_node = MCTSNode(root_state.clone())

    # Run MCTS iterations
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

    # Extract statistics from children
    result = {
        'win_rates': {},
        'visits': {},
        'ucb_scores': {}
    }

    for child in root_node.children:
        col = child.move
        if child.visits > 0:
            result['win_rates'][col] = child.wins / child.visits
            result['visits'][col] = child.visits
            result['ucb_scores'][col] = child.get_ucb_score()

    return result


def ai_play_move(state, n_iter=None):
    """
    AI plays a move using MCTS.

    Arguments:
        state: The current state of the game.
        n_iter: Number of MCTS iterations (None defaults to the player's iteration value in AI_ITER).

    Returns:
        A tuple (move, mcts_stats) containing the column index and MCTS statistics
    """
    if n_iter is None:
        # Use `AI_ITER` based on the current player
        n_iter = AI_ITER[state.current_player]

    move, mcts_stats = mcts_search(state, n_iter=n_iter)
    if move is not None:
        state.make_move(move)  # Apply the move
    return move, mcts_stats
