from config import (
    ROWS,
    COLS,
    EMPTY,
    PLAYER1,
    PLAYER2,
    SQUARESIZE,
    RADIUS,
    BACKGROUND_COLOR,
    BOARD_COLOR,
    PLAYER1_COLOR,
    PLAYER2_COLOR,
    HINT_COLOR,
    TEXT_COLOR
)


# Game state class and logic


class Connect4State:
    """
    This class represents a Connect 4 game state.

    It contains:
    - The board, a list of lists of integers.
    - The current player who should move next.

    Game logic:
    - Getting legal moves
    - Applying a move
    - Checking for a win or a draw
    """

    def __init__(self, board=None, current_player=PLAYER1):
        self.move_history = []  # list of (row, col, player)
        if board is None:
            self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        else:
            self.board = [row[:] for row in board]
        self.current_player = current_player

    def clone(self):
        return Connect4State(self.board, self.current_player)

    def get_legal_moves(self):
        return [col for col in range(COLS) if self.board[0][col] == EMPTY]

    # def make_move(self, col):
    #     for row in reversed(range(ROWS)):
    #         if self.board[row][col] == EMPTY:
    #             self.board[row][col] = self.current_player
    #             self.current_player = PLAYER1 if self.current_player == PLAYER2 else PLAYER2
    #             return True
    #     return False

    def make_move(self, col):
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == EMPTY:
                player = self.current_player
                self.board[r][col] = player
                self.move_history.append((r, col, player))
                self.current_player = (
                    PLAYER1 if player == PLAYER2 else PLAYER2
                )
                return True
        return False

    def check_winner(self):
        # Check horizontal, vertical, and diagonal for a win
        for c in range(COLS - 3):
            for r in range(ROWS):
                if self.board[r][c] != EMPTY and all(self.board[r][c + i] == self.board[r][c] for i in range(4)):
                    return self.board[r][c]
        for c in range(COLS):
            for r in range(ROWS - 3):
                if self.board[r][c] != EMPTY and all(self.board[r + i][c] == self.board[r][c] for i in range(4)):
                    return self.board[r][c]
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if self.board[r][c] != EMPTY and all(self.board[r + i][c + i] == self.board[r][c] for i in range(4)):
                    return self.board[r][c]
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if self.board[r][c] != EMPTY and all(self.board[r - i][c + i] == self.board[r][c] for i in range(4)):
                    return self.board[r][c]
        return None

    def is_full(self):
        return all(self.board[0][col] != EMPTY for col in range(COLS))

    def is_terminal(self):
        return self.check_winner() is not None or self.is_full()

    def get_next_open_row(self, col):
        for row in reversed(range(ROWS)):
            if self.board[row][col] == EMPTY:
                return row
        return None

    def check_winner_with_cells(self):
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                piece = self.board[r][c]
                if piece != EMPTY:
                    cells = [(r, c + i) for i in range(4)]
                    if all(self.board[rr][cc] == piece for rr, cc in cells):
                        return piece, cells

        # Vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                piece = self.board[r][c]
                if piece != EMPTY:
                    cells = [(r + i, c) for i in range(4)]
                    if all(self.board[rr][cc] == piece for rr, cc in cells):
                        return piece, cells

        # Diagonal TL → BR
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                piece = self.board[r][c]
                if piece != EMPTY:
                    cells = [(r + i, c + i) for i in range(4)]
                    if all(self.board[rr][cc] == piece for rr, cc in cells):
                        return piece, cells

        # Diagonal BL → TR
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                piece = self.board[r][c]
                if piece != EMPTY:
                    cells = [(r - i, c + i) for i in range(4)]
                    if all(self.board[rr][cc] == piece for rr, cc in cells):
                        return piece, cells

        return None, []

    def reset(self):
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = PLAYER1
        self.move_history.clear()
