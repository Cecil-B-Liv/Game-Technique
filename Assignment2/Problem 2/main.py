import pygame
import sys

# === Import core modules and configuration ===
from game import Connect4State  # Game state and logic
from mcts import mcts_search, ai_play_move  # MCTS AI logic
from config import (  # Game constants and color settings
    PLAYER1,
    PLAYER2,
    HUMAN_VS_HUMAN,
    HUMAN_VS_AI,
    AI_VS_AI,
    DEFAULT_GAME_MODE,
    SQUARESIZE,
    RADIUS,
    BACKGROUND_COLOR,
    BOARD_COLOR,
    PLAYER1_COLOR,
    PLAYER2_COLOR,
    HINT_COLOR,
    TEXT_COLOR,
    SIZE,
    FPS,
    AI_ITER
)

# ============================================
#     HELPERS FOR VISUAL ENHANCEMENTS
# ============================================


# Simulate multiple AI vs AI games to gather win/draw statistics
def simulate_games(simulations=100):
    """
    Automate AI vs AI gameplay to track win rates for Player 1 and Player 2.
    """
    player_1_wins = 0
    player_2_wins = 0
    draws = 0

    for game_num in range(simulations):
        state = Connect4State()
        game_over = False

        # Play a single game until it ends
        while not game_over:
            # AI turn logic: let the AI play for the current player
            move = ai_play_move(state, n_iter=AI_ITER[state.current_player])
            state.make_move(move)

            # Check for game end after each move
            game_over, message = check_game_over(state)

            # Debugging - Print game progress
            print(
                f"Game {game_num + 1}, Move: {move}, Current Player: {state.current_player}")

        # Analyze game result
        winner = state.check_winner()
        if winner == PLAYER1:
            player_1_wins += 1
        elif winner == PLAYER2:
            player_2_wins += 1
        else:
            draws += 1

    # Print and return statistics
    print(f"Simulated {simulations} games:")
    print(f"Player 1 Wins: {player_1_wins}")
    print(f"Player 2 Wins: {player_2_wins}")
    print(f"Draws: {draws}")

    return player_1_wins, player_2_wins, draws


def draw_player_turn(screen, font, current_player, game_over):
    """
    Draw which player’s turn it currently is, along with their color.

    Arguments:
        screen: The PyGame surface to draw on.
        font: The PyGame font object to render text.
        current_player: PLAYER1 or PLAYER2 to indicate which player's turn it is.
        game_over: Whether the game has ended. If True, do not display the turn.
    """

    # Only show turn if game is not over
    if game_over:
        return  # Do not render player turn once game is over

    color = PLAYER1_COLOR if current_player == PLAYER1 else PLAYER2_COLOR
    text = f"Player {current_player} Turn"
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (10, SQUARESIZE * 0.5))


def draw_end_game_message(screen, font, message):
    """
    Draw a banner-like message in the center of the screen when the game ends.

    Arguments:
        screen: The PyGame surface to draw on.
        font: The PyGame font object.
        message: The message to display (e.g., who won or if it's a draw).
    """
    # Create a semi-transparent overlay to dim the game space
    overlay = pygame.Surface(SIZE, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Dark semi-transparent overlay
    screen.blit(overlay, (0, 0))

    # Center the result message in the middle of the screen
    box = pygame.Rect(SIZE[0] // 2 - 250, SIZE[1] // 2 - 60, 500, 120)
    pygame.draw.rect(screen, BOARD_COLOR, box, border_radius=12)

    # Render the message in the center of the box
    text = font.render(message, True, TEXT_COLOR)
    screen.blit(
        text,
        (box.centerx - text.get_width() // 2,
         box.centery - text.get_height() // 2)
    )


def draw_board(screen, state, font, hint_col=None, message="", game_over=False):
    """
    Enhances the board drawing with dynamic data about the player's turn and game state.

    Arguments:
        hint_col: Column index for the hint (highlighted during HUMAN_VS_AI mode).
        message: Optional status message for additional info like game state feedback.
        game_over: Stops rendering "Player Turn" when the game has ended.
    """
    # Fill background
    screen.fill(BACKGROUND_COLOR)

    # Draw hint marker for AI suggestion (top row)
    if hint_col is not None and not game_over:
        x_center = hint_col * SQUARESIZE + SQUARESIZE // 2
        pygame.draw.circle(screen, HINT_COLOR, (x_center,
                           SQUARESIZE // 2), RADIUS // 2)

    # Draw the board grid and empty slots
    for c in range(state.board[0].__len__()):
        for r in range(state.board.__len__()):
            pygame.draw.rect(screen, BOARD_COLOR, (c * SQUARESIZE,
                             (r + 1) * SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(
                screen, BACKGROUND_COLOR,
                (c * SQUARESIZE + SQUARESIZE // 2, (r + 1)
                 * SQUARESIZE + SQUARESIZE // 2), RADIUS
            )

    # Draw player pieces
    for c in range(state.board[0].__len__()):
        for r in range(state.board.__len__()):
            piece = state.board[r][c]
            if piece == PLAYER1:
                color = PLAYER1_COLOR
            elif piece == PLAYER2:
                color = PLAYER2_COLOR
            else:
                continue
            pygame.draw.circle(
                screen, color,
                (c * SQUARESIZE + SQUARESIZE // 2,
                 (r + 1) * SQUARESIZE + SQUARESIZE // 2),
                RADIUS
            )

    # Highlight the last move with a white border
    if state.last_move:
        r, c = state.last_move
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (
                c * SQUARESIZE + SQUARESIZE // 2,
                (r + 1) * SQUARESIZE + SQUARESIZE // 2
            ),
            RADIUS,
            3
        )

    # Display player turn and HUD
    # draw_player_turn(screen, font, state.current_player, game_over)
    draw_hud(screen, font, DEFAULT_GAME_MODE, state.current_player, message)

    # Display the end-game message if applicable
    if game_over:
        draw_end_game_message(screen, font, message)

    # Update the display
    pygame.display.update()


def animated_thinking_text(base, frame):
    # Animate a thinking message with dots (for AI turn feedback)
    dots = "." * (frame % 4)
    return f"{base}{dots}"


def check_game_over(state):
    """
    Check if the game is over and determine the result.

    Returns:
        A tuple (is_terminal, message), where:
        - `is_terminal` is True if the game is over, otherwise False.
        - `message` is the result message to display (e.g., which player won or if it's a draw).
    """
    winner = state.check_winner()
    if winner is not None:
        # Return the winner as part of the message
        print(f"Winner identified: Player {winner}")  # Debugging winner logic
        return True, f"Player {winner} wins! Press R to restart."
    elif state.is_full():
        print("Draw: Board is full.")  # Debugging for draw
        return True, "It's a draw! Press R to restart."
    # Game is not over
    return False, ""


def animate_drop(screen, state, col, player, font, hint_col, message):
    """
    Animates a piece falling into the board.

    Arguments:
        screen: The PyGame screen to draw on.
        state: Current game state.
        col: Column where the piece is dropped.
        player: The player who made the move (PLAYER1 or PLAYER2).
        font: The PyGame font object.
        hint_col: The current hint column for AI moves.
        message: Text message to display at the top.
    """
    # Animate a piece falling into the correct row visually
    row = state.get_next_open_row(col)
    if row is None:
        return

    x = col * SQUARESIZE + SQUARESIZE // 2
    start_y = SQUARESIZE // 2
    target_y = (row + 1) * SQUARESIZE + SQUARESIZE // 2
    color = PLAYER1_COLOR if player == PLAYER1 else PLAYER2_COLOR

    y = start_y
    speed = 20  # Movement speed for the falling piece

    while y < target_y:
        draw_board(screen, state, font, hint_col, message)
        pygame.draw.circle(screen, color, (x, int(y)), RADIUS)
        pygame.display.update()
        y += speed
        pygame.time.delay(16)


def draw_hud(screen, font, game_mode, current_player, message):
    # Draws the top HUD bar with game mode, player, and message
    pygame.draw.rect(screen, BOARD_COLOR, (0, 0, SIZE[0], SQUARESIZE))

    # Map game mode to display text
    mode_text = {
        HUMAN_VS_HUMAN: "Human vs Human",
        HUMAN_VS_AI: "Human vs AI",
        AI_VS_AI: "AI vs AI"
    }[game_mode]

    # Compose HUD text elements
    texts = [
        (mode_text, TEXT_COLOR),
        (f"Player {current_player}", PLAYER1_COLOR if current_player ==
         PLAYER1 else PLAYER2_COLOR),
        (message, TEXT_COLOR),
    ]

    # Render each HUD text element with spacing
    x = 20
    for text, color in texts:
        surf = font.render(text, True, color)
        screen.blit(surf, (x, 15))
        x += surf.get_width() + 40


# =================================
#     MAIN GAME FUNCTION
# =================================
def main():
    """
    Main function to start the Connect 4 game with enhanced visuals for a smoother,
    more interactive demonstration experience.
    """
    thinking_frame = 0

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect 4 with MCTS (Demonstration Edition)")
    font = pygame.font.SysFont("arial", 30)
    clock = pygame.time.Clock()

    # Game State Initialization
    state = Connect4State()
    game_over = False
    message = "Player 1 Turn"

    # Initialize Game Mode
    GAME_MODE = DEFAULT_GAME_MODE
    hint_col = None

    # Generate the first hint if playing Human vs AI
    if GAME_MODE == HUMAN_VS_AI:
        hint_col = mcts_search(state, n_iter=400)

    # For testing
    if GAME_MODE == AI_VS_AI:
        simulate_games(simulations=20)
    # Main Loop Flag
    running = True

    thinking_frame = 0  # Used for animating AI thinking dots

    # Initialize PyGame and window
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect 4 with MCTS (Demonstration Edition)")
    font = pygame.font.SysFont("arial", 30)
    clock = pygame.time.Clock()

    # Game State Initialization
    state = Connect4State()
    game_over = False
    message = "Player 1 Turn"

    # Set the game mode (Human vs Human, Human vs AI, AI vs AI)
    GAME_MODE = DEFAULT_GAME_MODE
    hint_col = None

    # Generate the first AI hint if playing Human vs AI
    if GAME_MODE == HUMAN_VS_AI:
        hint_col = mcts_search(state, n_iter=400)

    # For testing: run AI vs AI simulations if selected
    if GAME_MODE == AI_VS_AI:
        simulate_games(simulations=20)

    running = True  # Main loop flag

    # Main Game Loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset the game
                    state = Connect4State()
                    game_over = False
                    message = "Player 1 Turn"
                    hint_col = mcts_search(
                        state, n_iter=400) if GAME_MODE == HUMAN_VS_AI else None

            # Handle mouse clicks for human moves
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and GAME_MODE in [HUMAN_VS_HUMAN, HUMAN_VS_AI]:
                col = event.pos[0] // SQUARESIZE
                if col in state.get_legal_moves():
                    animate_drop(screen, state, col,
                                 state.current_player, font, hint_col, message)
                    state.make_move(col)
                    thinking_frame = 0

                    # Check if the game is over after human move
                    game_over, message = check_game_over(state)

                    # If AI's turn in Human vs AI, show thinking animation and let AI play
                    if not game_over and GAME_MODE == HUMAN_VS_AI:
                        thinking_frame += 1
                        message = animated_thinking_text(
                            f"AI Player {state.current_player} thinking", thinking_frame
                        )
                        draw_board(screen, state, font, hint_col=None,
                                   message=message, game_over=game_over)

                        # Remember current player before the AI makes the move
                        ai_player = state.current_player

                        # AI makes its move
                        ai_move = ai_play_move(
                            state, n_iter=AI_ITER[ai_player])

                        # Animate drop for the correct player (ai_player)
                        animate_drop(screen, state, ai_move,
                                     ai_player, font, hint_col, message)

                        # Check if the game is over after AI move
                        game_over, message = check_game_over(state)

        # AI vs AI Logic: let both AIs play automatically
        if not game_over and GAME_MODE == AI_VS_AI:
            pygame.time.delay(500)  # Slow down for visibility
            message = f"AI Player {state.current_player} is thinking..."
            draw_board(screen, state, font, hint_col=None,
                       message=message, game_over=game_over)
            move = ai_play_move(state, n_iter=AI_ITER[state.current_player])
            animate_drop(screen, state, move, state.current_player ^
                         3, font, hint_col, message)
            thinking_frame = 0
            game_over, message = check_game_over(state)

        # Draw the updated board after every event/AI move
        draw_board(screen, state, font, hint_col, message, game_over=game_over)

    # Exit the Game Loop and close PyGame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
