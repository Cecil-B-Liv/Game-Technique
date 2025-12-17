from config import (
    ROWS,
    COLS,
    EMPTY,
    PLAYER1,
    PLAYER2,
)

# ===================================
# CLASS RESPONSIBLE FOR GAME LOGIC
# ===================================


class Connect4State:
    """
    This class represents a Connect 4 game state.

    It contains:
    - The board: A list of lists of integers.
    - The current player who should move next.

    Game logic includes:
        - Getting legal moves
        - Applying a move
        - Checking for a win or a draw
        - Determining the next open row in a column
    """

    def __init__(self, board=None, current_player=PLAYER1):
        """
        Initialize the state with the board and current player.

        board: Either None (start a new empty board) or
               an existing 2D list to use for the board.
        current_player: Either PLAYER1 or PLAYER2.
        """
        self.last_move = None
        self.move_history = []  # Track moves as (row, col, player)
        # Create the board if it doesn't exist
        if board is None:
            self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        else:
            self.board = [row[:] for row in board]  # Deep copy
        self.current_player = current_player

    def clone(self):
        """
        Clone the current state for simulations.
        """
        return Connect4State(self.board, self.current_player)

    def get_legal_moves(self):
        """
        Get all valid columns where a move can be made.
        """
        return [col for col in range(COLS) if self.board[0][col] == EMPTY]

    def make_move(self, col):
        """
        Apply a move in the specified column.

        - The move will be applied to the lowest empty row in the column.
        - Tracks moves in the move history.
        - Alternates the current player.
        """
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == EMPTY:
                player = self.current_player
                self.board[r][col] = player
                self.last_move = (r, col)
                self.move_history.append((r, col, player))
                self.current_player = PLAYER1 if player == PLAYER2 else PLAYER2
                return True
        return False

    def get_next_open_row(self, col):
        """
        Find the next empty row in the given column.

        Arguments:
            col: The column index to check.

        Returns:
            The row index of the next available open row,
            or `None` if the column is full.
        """
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                return row
        return None

    def check_winner(self):
        """
        Check for a winner on the board (horizontal, vertical, or diagonal).
        """
        # Check Horizontal
        for c in range(COLS - 3):
            for r in range(ROWS):
                if self.board[r][c] != EMPTY and all(
                    self.board[r][c + i] == self.board[r][c] for i in range(4)
                ):
                    return self.board[r][c]
        # Check Vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if self.board[r][c] != EMPTY and all(
                    self.board[r + i][c] == self.board[r][c] for i in range(4)
                ):
                    return self.board[r][c]
        # Check Diagonal (Top Left to Bottom Right)
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if self.board[r][c] != EMPTY and all(
                    self.board[r + i][c + i] == self.board[r][c] for i in range(4)
                ):
                    return self.board[r][c]
        # Check Diagonal (Bottom Left to Top Right)
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if self.board[r][c] != EMPTY and all(
                    self.board[r - i][c + i] == self.board[r][c] for i in range(4)
                ):
                    return self.board[r][c]

        return None  # No winner

    def is_full(self):
        """
        Check if the board is full (no more valid moves).
        """
        return all(self.board[0][col] != EMPTY for col in range(COLS))

    def is_terminal(self):
        """
        Check if the game has ended (a player has won or the board is full).
        """
        return self.check_winner() is not None or self.is_full()

    def reset(self):
        """
        Reset the game board and player turn.
        """
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = PLAYER1
        self.move_history.clear()
