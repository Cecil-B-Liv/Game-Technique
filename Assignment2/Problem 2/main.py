import pygame
from game import Connect4State, PLAYER1, PLAYER2, ROWS, COLS
from mcts import ai_play_move, mcts_search

from config import (
    AI_ITER,
    PLAYER1,
    PLAYER2,
    HUMAN_VS_HUMAN,
    HUMAN_VS_AI,
    AI_VS_AI,
    FPS,
    SQUARESIZE)

import sys

# Game mode constants
HUMAN_VS_HUMAN = 0
HUMAN_VS_AI = 1
AI_VS_AI = 2

# Colors and visual settings
SQUARESIZE = 100
RADIUS = SQUARESIZE // 2 - 5
BACKGROUND_COLOR = (30, 30, 30)
BOARD_COLOR = (20, 60, 120)
PLAYER1_COLOR = (220, 50, 50)
PLAYER2_COLOR = (240, 220, 70)
HINT_COLOR = (80, 200, 120)
TEXT_COLOR = (240, 240, 240)
BG_COLOR = BACKGROUND_COLOR
WIDTH = COLS * SQUARESIZE
HEIGHT = (ROWS + 2) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
FPS = 60


class GameController:
    def __init__(self, screen, font, mode):
        self.screen = screen
        self.font = font
        self.mode = mode

        self.state = Connect4State()
        self.game_over = False
        self.message = "Player 1 turn"
        self.hint_col = None

        self.update_hint()


def update_hint(self):
    if self.mode != AI_VS_AI and not self.game_over:
        self.hint_col = mcts_search(self.state, n_iter=400)
    else:
        self.hint_col = None


def is_human_turn(mode, current_player):
    if mode == HUMAN_VS_HUMAN:
        return True
    if mode == HUMAN_VS_AI:
        return current_player == PLAYER1
    return False


def check_game_over(state):
    winner = state.check_winner()
    if winner == PLAYER1:
        return True, "Player 1 wins!"
    elif winner == PLAYER2:
        return True, "Player 2 wins!"
    elif state.is_full():
        return True, "It's a draw!"
    return False, ""


def animate_drop(screen, state, col, player, font, hint_col, message):
    row = state.get_next_open_row(col)
    if row is None:
        return
    color = PLAYER1_COLOR if player == PLAYER1 else PLAYER2_COLOR
    for r in range(row + 1):
        draw_board(screen, state, font, hint_col, message)
        pygame.draw.circle(screen, color, (col * SQUARESIZE + SQUARESIZE //
                           2, (r + 1) * SQUARESIZE + SQUARESIZE // 2), RADIUS)
        pygame.display.update()
        pygame.time.wait(50)


def draw_board(screen, state, font, hint_col=None, message=""):
    screen.fill(BG_COLOR)
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BOARD_COLOR, (c * SQUARESIZE,
                             (r + 1) * SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BG_COLOR, (c * SQUARESIZE + SQUARESIZE //
                               2, (r + 1) * SQUARESIZE + SQUARESIZE // 2), RADIUS)
    for c in range(COLS):
        for r in range(ROWS):
            if state.board[r][c] == PLAYER1:
                pygame.draw.circle(screen, PLAYER1_COLOR, (c * SQUARESIZE +
                                   SQUARESIZE // 2, (r + 1) * SQUARESIZE + SQUARESIZE // 2), RADIUS)
            elif state.board[r][c] == PLAYER2:
                pygame.draw.circle(screen, PLAYER2_COLOR, (c * SQUARESIZE +
                                   SQUARESIZE // 2, (r + 1) * SQUARESIZE + SQUARESIZE // 2), RADIUS)
    if hint_col is not None:
        pygame.draw.circle(screen, HINT_COLOR, (hint_col *
                           SQUARESIZE + SQUARESIZE // 2, SQUARESIZE // 2), RADIUS)
    if message:
        label = font.render(message, 1, TEXT_COLOR)
        screen.blit(label, (40, 10))
    pygame.display.update()


def handle_human_input(self, event):
    if (
        event.type == pygame.MOUSEBUTTONDOWN
        and not self.game_over
        and is_human_turn(self.mode, self.state.current_player)
    ):
        x, _ = event.pos
        col = x // SQUARESIZE

        if col in self.state.get_legal_moves():
            animate_drop(
                self.screen,
                self.state,
                col,
                self.state.current_player,
                self.font,
                self.hint_col,
                self.message
            )
            self.state.make_move(col)
            self.after_move()


def handle_ai_turn(self):
    if (
        not self.game_over
        and not is_human_turn(self.mode, self.state.current_player)
    ):
        pygame.time.delay(100 if self.mode == AI_VS_AI else 300)

        self.message = "AI is thinking..."
        draw_board(self.screen, self.state, self.font, None, self.message)
        pygame.display.update()

        move = mcts_search(
            self.state,
            n_iter=AI_ITER[self.state.current_player]
            if self.mode == AI_VS_AI
            else 500
        )

        if move is not None:
            animate_drop(
                self.screen,
                self.state,
                move,
                self.state.current_player,
                self.font,
                None,
                self.message
            )
            self.state.make_move(move)

        self.after_move()


def after_move(self):
    self.game_over, end_msg = check_game_over(self.state)
    if self.game_over:
        self.message = end_msg
        self.hint_col = None
    else:
        self.message = f"Player {self.state.current_player} turn"
        self.update_hint()

def reset(self):
    self.state.reset()
    self.game_over = False
    self.message = "Player 1 turn"
    self.update_hint()

def draw(self):
    mode_text = {
        HUMAN_VS_HUMAN: "Human vs Human",
        HUMAN_VS_AI: "Human vs AI",
        AI_VS_AI: "AI vs AI"
    }[self.mode]

    if not self.game_over:
        if self.mode == AI_VS_AI:
            self.message = (
                f"{mode_text} | "
                f"AI1 ({AI_ITER[PLAYER1]}) vs "
                f"AI2 ({AI_ITER[PLAYER2]}) | "
                f"Player {self.state.current_player} turn"
            )
        else:
            self.message = f"{mode_text} | Player {self.state.current_player} turn"

    draw_board(
        self.screen,
        self.state,
        self.font,
        self.hint_col,
        self.message
    )

def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect 4 with MCTS")
    font = pygame.font.SysFont("monospace", 40)
    clock = pygame.time.Clock()
    state = Connect4State()
    mode = HUMAN_VS_AI
    game_over = False
    message = ""
    hint_col = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEMOTION:
                if not game_over and is_human_turn(mode, state.current_player):
                    x = event.pos[0]
                    hint_col = x // SQUARESIZE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and is_human_turn(mode, state.current_player):
                    x = event.pos[0]
                    col = x // SQUARESIZE
                    if col in state.get_legal_moves():
                        animate_drop(
                            screen, state, col, state.current_player, font, hint_col, message)
                        state.make_move(col)
                        game_over, message = check_game_over(state)
                        hint_col = None
        if not game_over and not is_human_turn(mode, state.current_player):
            move = ai_play_move(state, n_iter=400)
            if move is not None:
                animate_drop(screen, state, move,
                             state.current_player ^ 3, font, hint_col, message)
                game_over, message = check_game_over(state)
        draw_board(screen, state, font, hint_col, message)
        clock.tick(FPS)


if __name__ == "__main__":
    main()
