"""
Assignment II - Starter Code: Connect 4 in Pygame with MCTS based hint for 2 human players.

This file is meant to be the starter code, it is not a requirement, feel free to ignore it.
In your tasks, you need to implement:
    -  1 human player against an AI agent
    -  2 AI agents playing against each other.

Run this sample codeussing: 
    python connect4_mcts.py

Rememever that you need Pygame installed:
    pip install pygame
"""

import pygame
import sys
import math
import random

# ==========================================
#              PART 1 - GAME CONSTANTS AND COLORS
#             ==========================

# In Connect 4, the board has 6 rows and 7 columns.
ROWS = 6
COLS = 7

# So I use simple integers to represent the content of each cell.
EMPTY = 0      # No piece in this cell
PLAYER1 = 1    # Player 1 piece (red)
PLAYER2 = 2    # Player 2 piece (yellow)

# Visual settings for Pygame. Up to you if you want to tweak these to resiz
SQUARESIZE = 100
RADIUS = SQUARESIZE // 2 - 5

# Game modes constants
HUMAN_VS_HUMAN = 0
HUMAN_VS_AI = 1
AI_VS_AI = 2

# AI difficulty (iterations per player)
AI_ITER = {
    PLAYER1: 300,   # weaker AI
    PLAYER2: 100    # stronger AI
}


# Colors are given in RGB format (red, green, blue)
# BOARD_COLOR = (0, 0, 200)        # Blue board background
# BG_COLOR = (0, 0, 0)             # Black background
# PLAYER1_COLOR = (200, 0, 0)      # Red discs for player 1
# PLAYER2_COLOR = (230, 230, 0)    # Yellow discs for player 2
# TEXT_COLOR = (255, 255, 255)     # White text
# HINT_COLOR = (0, 200, 0)         # Green hint marker

BACKGROUND_COLOR = (30, 30, 30)
BOARD_COLOR = (20, 60, 120)

PLAYER1_COLOR = (220, 50, 50)    # red
PLAYER2_COLOR = (240, 220, 70)   # yellow

HINT_COLOR = (80, 200, 120)
TEXT_COLOR = (240, 240, 240)
BG_COLOR = BACKGROUND_COLOR


# Screen size
WIDTH = COLS * SQUARESIZE
# Extra 2 rows of space for messages and hint marker
HEIGHT = (ROWS + 2) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)

FPS = 60


# ====================================
#              PART 2 - CONNECT 4 STATE CLASS
# ====================================

class Connect4State:
    """
    This class represents a Connect 4 game state.

    It contains:
    - The board, a list of lists of integers.
    - The current player who should move next.

    I will keep all the game logic here, but again this is not a requirement so feel free:
    - Getting legal moves
    - Applying a move
    - Checking for a win or a draw
    """

    def __init__(self, board=None, current_player=PLAYER1):
        """
        Constructor for the game state.

        board:
            Either None (start a new empty baord)
            or an existing 2D list to copy.

        current_player:
            Either PLAYER1 or PLAYER2.
        """
        if board is None:
            # Create an empty baord with ROWS x COLS filled with EMPTY
            self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        else:
            # Make a deep copy of the baord so we do not modify the original
            self.board = [row[:] for row in board]

        self.current_player = current_player

    def clone(self):
        """
        Create a new Connect4State with the same board and current player.

        Useful in MCTS when we want to simulate moves without
        changing the original game state.
        """
        return Connect4State(self.board, self.current_player)

    def get_legal_moves(self):
        """
        Return a lits of columns (indices from 0 to COLS - 1)
        where a piece can still be dropped.

        A column is legal if its top cell (row 0) is EMPTY !!!! This is very important in the game logic
        """
        moves = []
        for c in range(COLS):
            if self.board[0][c] == EMPTY:
                moves.append(c)
        return moves

    def make_move(self, col):
        """
        Drop a piece for the current player in the given column.

        If the column is valid:
            - The piece will fall to the lowest available row.
            - The current player will switch to the other player.
            - The function returns True.

        If the column is full:
            - The function retunrs False and does nothing.
        """
        for r in range(ROWS - 1, -1, -1):  # Start from bottom row and go up
            if self.board[r][col] == EMPTY:
                self.board[r][col] = self.current_player
                # Switch to the other player
                self.current_player = PLAYER1 if self.current_player == PLAYER2 else PLAYER2
                return True
        return False  # Column was full

    def check_winner(self):
        """
        Check if there is a winner on the baord.

        Right, we need to look for 4 equal, non empty pieces in:
        - Horizontal lines
        - Vertical lines
        - Diagonals from top left to bottom right
        - Diagonals from bottom left to top right\
        This is very important.

        Returns:
            PLAYER1 if player 1 wins
            PLAYER2 if player 2 wins
            None if there is no winner
        """

        # Horizontal check
        for r in range(ROWS):
            for c in range(COLS - 3):
                piece = self.board[r][c]
                if piece != EMPTY:
                    if all(self.board[r][c + i] == piece for i in range(4)):
                        return piece

        # Vertical check
        for c in range(COLS):
            for r in range(ROWS - 3):
                piece = self.board[r][c]
                if piece != EMPTY:
                    if all(self.board[r + i][c] == piece for i in range(4)):
                        return piece

        # Diagonal check (top left to bottom right)
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                piece = self.board[r][c]
                if piece != EMPTY:
                    if all(self.board[r + i][c + i] == piece for i in range(4)):
                        return piece

        # Diagonal check (bottom left to top right)
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                piece = self.board[r][c]
                if piece != EMPTY:
                    if all(self.board[r - i][c + i] == piece for i in range(4)):
                        return piece

        # No winner found
        return None

    def is_full(self):
        """
        Check if the board is full.

        If the top row has no EMPTY cells, then no more moves can be played.
        """
        return all(self.board[0][c] != EMPTY for c in range(COLS))

    def is_terminal(self):
        """
        Check if the game is over.

        The game is terminal if:
        - someone won, or
        - the board is full (draw).
        """
        if self.check_winner() is not None:
            return True
        if self.is_full():
            return True
        return False

    def get_next_open_row(self, col):
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == EMPTY:
                return r
        return None


# ============================================================
#                 PART 3 - MCTS EXPLANATION
# ============================================================
"""
Let me now explain the Monte Carlo Tree Search (MCTS) algorithm that we will use
to suggest a good move as a hint for the current player.

MCTS is built on 4 main steps that are repeated many times:

1. SELECTION
   - Start from the root node that represents the current game state.
   - If the node has already been visited and fully expanded,
     we use a formula called UCT (Upper Confidence bound applied to Trees)
     to pick the child that balances:
        * Exploitation: children that won more often in the past.
        * Exploration: children that have been visited fewer times.
   - We follow this path of best children until we reach a node that:
        * is not fully expanded, or
        * represents a terminal game state (win, loss, or draw).

2. EXPANSION
   - If the selected node is not terminal, we can add a new child.
   - A child corresponds to playing one of the moves that has not been tried yet.
   - We pick one untried move, apply it to a copy of the game state,
     and create a new child node that stores this new state.

3. SIMULATION (also called ROLLOUT)
   - From the newly created child state, we play a random game until the end.
   - That means we randomly select legal moves until we reach a win, loss, or draw.
   - At the end we know the result:
        * The root player wins, loses, or it is a draw.
   - We convert this result into a numeric reward:
        * 1.0 for a win for the root player
        * 0.0 for a loss for the root player
        * 0.5 for a draw

4. BACKPROPAGATION
   - We then walk back from the simulation node up to the root node.
   - For each node on this path we:
        * Increase the visit count.
        * Add the reward to the node's total wins.
   - This way, each node stores:
        * How many times we visited it.
        * How many wins the root player got through this node.

After doing many iterations of these four steps:
   - The root node will have some children, each corresponding to a possible move.
   - Each child has a visit count and a total win count.
   - We can then pick the child that has the most visits.
   - The move that leads to that child is our suggested move.

The main idea:
   - Random simulations plus statistics guide us to good moves.
   - More iterations usually gives a smarter suggestion.
"""


# ============================================================
#              PART 4 - MCTS DATA STRUCTURES AND CODE
# ============================================================

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
        self.state = state          # Game state at this node
        self.parent = parent        # Parent node
        self.move = move            # Move that led to this node from parent
        self.children = []          # List of child MCTSNode instances
        self.visits = 0             # Number of times this node has been visited
        self.wins = 0.0             # Sum of rewards from root player's point of view

    def is_fully_expanded(self):
        """
        Check if this node has created children for all legal moves.

        If the state is terminal, we consider it fully expanded,
        because there are no moves to expand.

        Otherwise:
        - We get all legal moves from this state.
        - We compare them with the moves that are already used by children.
        - If every legal move has a child, then the node is fully expanded.
        """
        if self.state.is_terminal():
            return True

        child_moves = {child.move for child in self.children}
        legal_moves = set(self.state.get_legal_moves())
        # Node is fully expanded if:
        # - the number of children matches the number of legal moves
        # - and every legal move already has a child
        return legal_moves.issubset(child_moves) and len(legal_moves) == len(child_moves)

    def best_child(self, c_param=1.4):
        """
        Select a child using the UCT formula.

        UCT score for a child:
            exploit = wins / visits
            explore = sqrt( 2 * ln(parent_visits) / child_visits )
            score = exploit + c_param * explore

        - exploit encourages moves that have good win ratio.
        - explore encourages trying moves that are less visited.

        c_param (exploration constant) controls how much we explore.
        A common choice is around 1.4 (square root of 2).

        If a child has never been visited (visits == 0),
        we treat its score as infinity to ensure it is explored at least once.
        """
        best_score = float("-inf")
        best_children = []

        for child in self.children:
            if child.visits == 0:
                # Encourage at least one visit for every child
                score = float("inf")
            else:
                exploit = child.wins / child.visits
                explore = math.sqrt(2 * math.log(self.visits) / child.visits)
                score = exploit + c_param * explore

            # Keep track of the best score and all children that achieve it
            if score > best_score:
                best_score = score
                best_children = [child]
            elif score == best_score:
                best_children.append(child)

        # If several children tie, pick one at random
        return random.choice(best_children)

    def most_visited_child(self):
        """
        After MCTS finishes, we want to pick the move that was explored the most.

        This function returns the child with the highest visit count.
        If there are no children (no moves), returns None.
        """
        if not self.children:
            return None
        return max(self.children, key=lambda c: c.visits)


def rollout(state, root_player):
    """
    Perform a random simulation (rollout) from the given state until the game ends.

    We work on a cloned state so we do not modify the original.

    At each step:
        - Get the list of legal moves.
        - Pick one move uniformly at random.
        - Apply this move.

    When the game reaches a terminal state:
        - If the winner is the root player, we return 1.0
        - If the winner is the opponent, we return 0.0
        - If there is no winner (draw), we return 0.5

    Arguments:
        state: Connect4State from which to start simulation
        root_player: the player we consider as "our" perspective
    """
    temp_state = state.clone()

    # Play random moves until the game is over
    while not temp_state.is_terminal():
        legal_moves = temp_state.get_legal_moves()
        if not legal_moves:
            break  # No moves left, should be a draw
        move = random.choice(legal_moves)
        temp_state.make_move(move)

    # Game is over, check the result
    winner = temp_state.check_winner()
    if winner is None:
        return 0.5
    if winner == root_player:
        return 1.0
    else:
        return 0.0


def mcts_search(root_state, n_iter=400):
    """
    Run MCTS from the given root_state and return the best move.

    Arguments:
        root_state:
            The current game state from which we search.
        n_iter:
            Number of MCTS iterations. More iterations usually means a better hint
            but it is also slower.

    Returns:
        The column index of the suggested move, or
        None if there is no legal move.

    Steps:
        1. Create a root MCTSNode that holds a copy of root_state.
        2. For n_iter iterations:
            a) Selection
            b) Expansion
            c) Simulation
            d) Backpropagation
        3. Return the move of the most visited child of the root.
    """
    # If the game is already finished, we return no move
    if root_state.is_terminal():
        return None

    # The root player is the player who is about to move in root_state
    root_player = root_state.current_player

    # Create a root node for the MCTS tree
    root_node = MCTSNode(root_state.clone())

    for _ in range(n_iter):
        # 1. Start at the root node and work on a fresh copy of root_state
        node = root_node
        state = root_state.clone()

        # 2. SELECTION
        # While the current node has children, is fully expanded,
        # and the state is not terminal, choose the best child with UCT.
        while node.children and node.is_fully_expanded() and not state.is_terminal():
            node = node.best_child()
            # Apply the move that led to this child to our simulation state
            if node.move is not None:
                state.make_move(node.move)

        # 3. EXPANSION
        # If the state is not terminal, we can expand by creating a new child.
        if not state.is_terminal():
            legal_moves = state.get_legal_moves()
            existing_moves = {child.move for child in node.children}
            # Untried moves are legal moves without a child yet
            untried_moves = [m for m in legal_moves if m not in existing_moves]

            if untried_moves:
                # Pick one untried move at random
                move = random.choice(untried_moves)
                # Apply it to the simulation state
                state.make_move(move)
                # Create the new child node
                child_node = MCTSNode(state.clone(), parent=node, move=move)
                # Attach this new child to the tree
                node.children.append(child_node)
                # And select this new child as the node to simulate from
                node = child_node

        # 4. SIMULATION (ROLLOUT)
        # From this node's state, simulate a random game until the end.
        reward = rollout(state, root_player)

        # 5. BACKPROPAGATION
        # Walk up the tree and update visit and win counts.
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent

    # After finishing all iterations, pick the child with the most visits.
    best_child = root_node.most_visited_child()
    if best_child is None:
        return None
    return best_child.move


def is_human_turn(mode, current_player):
    if mode == HUMAN_VS_HUMAN:
        return True
    if mode == HUMAN_VS_AI:
        return current_player == PLAYER1
    if mode == AI_VS_AI:
        return False
    return False


def ai_play_move(state, n_iter=500):
    move = mcts_search(state, n_iter=n_iter)
    if move is not None:
        state.make_move(move)
    return move


def check_game_over(state):
    winner = state.check_winner()
    if winner is not None:
        return True, f"Player {winner} wins, press R to restart"
    if state.is_full():
        return True, "Draw, press R to restart"
    return False, None


def animate_drop(screen, state, col, player, font, hint_col, message):
    row = state.get_next_open_row(col)
    if row is None:
        return

    x = col * SQUARESIZE + SQUARESIZE // 2
    start_y = SQUARESIZE // 2
    target_y = (row + 1) * SQUARESIZE + SQUARESIZE // 2

    color = PLAYER1_COLOR if player == PLAYER1 else PLAYER2_COLOR

    y = start_y
    speed = 20  # pixels per frame

    while y < target_y:
        draw_board(screen, state, font, hint_col, message)
        pygame.draw.circle(screen, color, (x, int(y)), RADIUS)
        pygame.display.update()

        y += speed
        pygame.time.delay(16)


# ============================================================
#             PART 5 - DRAWING THE GAME WITH PYGAME
# ============================================================

def draw_board(screen, state, font, hint_col=None, message=""):
    """
    Draw the entire game screen.

    This includes:
    - A message text at the top (whose turn, winner, instructions).
    - A small green hint marker at the top to show the suggested column.
    - The blue board with circular holes.
    - The pieces for both players.

    Arguments:
        screen: the Pygame surface where we draw
        state: the Connect4State we want to display
        font:  a Pygame font object for rendering text
        hint_col: optional column index for the hint move
        message: text message to display at the top
    """
    # Fill the screen with background color
    screen.fill(BG_COLOR)

    # Draw message area at the top
    text_surface = font.render(message, True, TEXT_COLOR)
    screen.blit(text_surface, (10, 5))

    # Draw hint marker if we have a suggested column
    if hint_col is not None:
        x_center = hint_col * SQUARESIZE + SQUARESIZE // 2
        pygame.draw.circle(
            screen,
            HINT_COLOR,
            (x_center, SQUARESIZE),
            RADIUS // 2,
        )

    # Draw blue board and empty holes
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(
                screen,
                BOARD_COLOR,
                (
                    c * SQUARESIZE,
                    (r + 2) * SQUARESIZE,
                    SQUARESIZE,
                    SQUARESIZE,
                ),
            )
            pygame.draw.circle(
                screen,
                BG_COLOR,
                (
                    c * SQUARESIZE + SQUARESIZE // 2,
                    (r + 2) * SQUARESIZE + SQUARESIZE // 2,
                ),
                RADIUS,
            )

    # Draw pieces for player 1 and player 2
    for c in range(COLS):
        for r in range(ROWS):
            piece = state.board[r][c]
            if piece == PLAYER1:
                color = PLAYER1_COLOR
            elif piece == PLAYER2:
                color = PLAYER2_COLOR
            else:
                continue  # Skip empty cells
            pygame.draw.circle(
                screen,
                color,
                (
                    c * SQUARESIZE + SQUARESIZE // 2,
                    (r + 2) * SQUARESIZE + SQUARESIZE // 2,
                ),
                RADIUS,
            )

    # Finally, update the display
    pygame.display.update()


# ============================================================
#              PART 6 - MAIN GAME LOOP WITH PYGAME
# ============================================================

def main():
    """
    Main function that runs the Pygame event loop.

    Game behavior (just for this starter because your assignment behavior is different):
        - 2 human players alternate turns.
        - The MCTS algorithm always computes a hint for the current player.
        - The hint is shown as a small green marker above the suggested column.
        - Players click with the mouse in the column where they want to drop a piece.
        - If a player wins or the board is full, a message is displayed.
        - Press R to restart the game.

    This function does not contain any MCTS logic itself.
    It just calls mcts_search to get the hint move.
    """
    pygame.init()

    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("MCTS Connect4")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)

    # ==========================
    # SELECT GAME MODE HERE
    # ==========================
    # GAME_MODE = HUMAN_VS_AI
    GAME_MODE = AI_VS_AI
    # GAME_MODE = HUMAN_VS_HUMAN

    state = Connect4State()
    game_over = False

    message = "Player 1 turn"
    hint_col = None

    # Only show hints if a human is playing
    if GAME_MODE != AI_VS_AI:
        hint_col = mcts_search(state, n_iter=400)

    running = True
    while running:
        clock.tick(FPS)

        # ==========================
        # EVENT HANDLING
        # ==========================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    state = Connect4State()
                    game_over = False
                    message = "Player 1 turn"
                    hint_col = (
                        mcts_search(state, n_iter=400)
                        if GAME_MODE != AI_VS_AI
                        else None
                    )

            # --------------------------
            # HUMAN INPUT
            # --------------------------
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and not game_over
                and is_human_turn(GAME_MODE, state.current_player)
            ):
                x, _ = event.pos
                col = x // SQUARESIZE

                if col in state.get_legal_moves():
                    animate_drop(
                        screen,
                        state,
                        col,
                        state.current_player,
                        font,
                        hint_col,
                        message
                    )
                    state.make_move(col)

                    game_over, end_msg = check_game_over(state)
                    if game_over:
                        message = end_msg
                        hint_col = None
                    else:
                        message = f"Player {state.current_player} turn"
                        hint_col = (
                            mcts_search(state, n_iter=400)
                            if GAME_MODE != AI_VS_AI
                            else None
                        )

        # ==========================
        # AI TURN (AUTOMATIC)
        # ==========================
        # if (
        #     not game_over
        #     and not is_human_turn(GAME_MODE, state.current_player)
        # ):
        #     pygame.time.delay(100 if GAME_MODE == AI_VS_AI else 300)

        #     message = "AI is thinking..."
        #     draw_board(screen, state, font, hint_col, message)
        #     pygame.display.update()

        #     if GAME_MODE == AI_VS_AI:
        #         ai_play_move(state, n_iter=AI_ITER[state.current_player])
        #     else:
        #         ai_play_move(state, n_iter=500)

        #     game_over, end_msg = check_game_over(state)
        #     if game_over:
        #         message = end_msg
        #         hint_col = None
        #     else:
        #         message = f"Player {state.current_player} turn"
        #         hint_col = (
        #             mcts_search(state, n_iter=400)
        #             if GAME_MODE != AI_VS_AI
        #             else None
        #         )
        # ==========================
        # AI TURN (AUTOMATIC)
        # ==========================
        if (
            not game_over
            and not is_human_turn(GAME_MODE, state.current_player)
        ):
            pygame.time.delay(100 if GAME_MODE == AI_VS_AI else 300)

            # Show thinking message
            message = "AI is thinking..."
            draw_board(screen, state, font, None, message)
            pygame.display.update()

            # 1. AI decides move
            n_iter = (
                AI_ITER[state.current_player]
                if GAME_MODE == AI_VS_AI
                else 500
            )
            move = mcts_search(state, n_iter=n_iter)

            # 2. Animate drop
            if move is not None:
                animate_drop(
                    screen,
                    state,
                    move,
                    state.current_player,
                    font,
                    None,        # disable hint during animation
                    message
                )

                # 3. Apply move AFTER animation
                state.make_move(move)

            # 4. Check game end
            game_over, end_msg = check_game_over(state)
            if game_over:
                message = end_msg
                hint_col = None
            else:
                hint_col = (
                    mcts_search(state, n_iter=400)
                    if GAME_MODE != AI_VS_AI
                    else None
                )

        mode_text = {
            HUMAN_VS_HUMAN: "Human vs Human",
            HUMAN_VS_AI: "Human vs AI",
            AI_VS_AI: "AI vs AI"
        }[GAME_MODE]

        if not game_over:
            if GAME_MODE == AI_VS_AI:
                message = (
                    f"{mode_text} | "
                    f"AI1 ({AI_ITER[PLAYER1]}) vs "
                    f"AI2 ({AI_ITER[PLAYER2]}) | "
                    f"Player {state.current_player} turn"
                )
            else:
                message = f"{mode_text} | Player {state.current_player} turn"

        draw_board(screen, state, font, hint_col, message)

    pygame.quit()
    sys.exit()


# This ensures that main() is called only when this file is run directly,
# not when it is imported as a module in another script.
if __name__ == "__main__":
    main()
