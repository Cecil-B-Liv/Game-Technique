import pygame
import sys

# === Import core modules and configuration ===
from game import Connect4State  # Game state and logic
from mcts import mcts_search, ai_play_move, analyze_move_win_rates  # MCTS AI logic
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
    WIN_RATE_BAR_BG,
    WIN_RATE_BAR_FG,
    SIZE,
    FPS,
    AI_ITER,
    SHOW_WIN_RATES,
    WIN_RATE_ITERATIONS,
    COLS,
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
            move, stats = ai_play_move(
                state, n_iter=AI_ITER[state.current_player])

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
    Draw which player's turn it currently is, along with their color.

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


def draw_mcts_stats(screen, font, mcts_data, current_player):
    """
    Draw MCTS statistics including visit counts, win rates, and UCB scores.

    Arguments:
        screen: The PyGame surface to draw on.
        font: The PyGame font object for rendering text.
        mcts_data: Dictionary containing 'win_rates', 'visits', and 'ucb_scores'.
        current_player: The player for whom the stats are calculated.
    """
    if not mcts_data or 'visits' not in mcts_data:
        return

    small_font = pygame.font.SysFont("arial", 16, bold=True)
    tiny_font = pygame.font.SysFont("arial", 14, bold=True)

    bar_height = 50
    bar_y = SQUARESIZE + 5

    win_rates = mcts_data.get('win_rates', {})
    visits = mcts_data.get('visits', {})
    ucb_scores = mcts_data.get('ucb_scores', {})

    for col in range(COLS):
        x = col * SQUARESIZE + 10
        bar_width = SQUARESIZE - 20

        # Draw background bar
        bg_rect = pygame.Rect(x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, WIN_RATE_BAR_BG, bg_rect, border_radius=4)

        # Draw win rate bar if available
        if col in win_rates:
            win_rate = win_rates[col]
            fg_width = int(bar_width * win_rate)
            fg_rect = pygame.Rect(x, bar_y, fg_width, bar_height)

            # Color gradient based on win rate
            if win_rate >= 0.6:
                color = (100, 220, 100)  # Green for good moves
            elif win_rate >= 0.4:
                color = (240, 220, 70)   # Yellow for neutral moves
            else:
                color = (220, 100, 100)  # Red for bad moves

            pygame.draw.rect(screen, color, fg_rect, border_radius=4)

            # Draw win rate percentage with outline
            percentage_text = f"{int(win_rate * 100)}%"

            # Black outline for win rate
            for offset_x in [-1, 0, 1]:
                for offset_y in [-1, 0, 1]:
                    if offset_x != 0 or offset_y != 0:
                        outline_surf = small_font.render(
                            percentage_text, True, (0, 0, 0))
                        text_x = x + bar_width // 2 - outline_surf.get_width() // 2 + offset_x
                        text_y = bar_y + 8 + offset_y
                        screen.blit(outline_surf, (text_x, text_y))

            # White text on top
            text_surf = small_font.render(
                percentage_text, True, (255, 255, 255))
            text_x = x + bar_width // 2 - text_surf.get_width() // 2
            text_y = bar_y + 8
            screen.blit(text_surf, (text_x, text_y))

            # Draw visit count
            if col in visits:
                visit_text = f"Visits:{visits[col]}"
                visit_surf = tiny_font.render(
                    visit_text, True, (200, 200, 200))
                visit_x = x + bar_width // 2 - visit_surf.get_width() // 2
                visit_y = bar_y + 28

                # Draw outline for visibility
                for offset_x in [-1, 0, 1]:
                    for offset_y in [-1, 0, 1]:
                        if offset_x != 0 or offset_y != 0:
                            outline = tiny_font.render(
                                visit_text, True, (0, 0, 0))
                            screen.blit(
                                outline, (visit_x + offset_x, visit_y + offset_y))

                screen.blit(visit_surf, (visit_x, visit_y))


def draw_ucb_message(screen, font, last_move_col, mcts_data):
    """
    Display the UCB score of the last move made by the AI.

    Arguments:
        screen: The PyGame surface to draw on.
        font: The PyGame font object.
        last_move_col: The column of the last move.
        mcts_data: Dictionary containing UCB scores.
    """
    if last_move_col is None or not mcts_data or 'ucb_scores' not in mcts_data:
        return

    ucb_scores = mcts_data.get('ucb_scores', {})
    if last_move_col not in ucb_scores:
        return

    ucb_score = ucb_scores[last_move_col]
    small_font = pygame.font.SysFont("arial", 18, bold=True)

    # Create UCB text
    ucb_text = f"Last Move UCB: {ucb_score:.3f}"
    text_surf = small_font.render(ucb_text, True, TEXT_COLOR)

    # Draw with background for visibility
    padding = 5
    text_rect = text_surf.get_rect()
    bg_rect = pygame.Rect(
        SIZE[0] - text_rect.width - 20 - padding,
        SQUARESIZE + 60,
        text_rect.width + padding * 2,
        text_rect.height + padding * 2
    )
    pygame.draw.rect(screen, (40, 40, 40), bg_rect, border_radius=4)
    screen.blit(text_surf, (SIZE[0] - text_rect.width - 20, SQUARESIZE + 65))


def draw_board(screen, state, font, hint_col=None, message="", game_over=False, mcts_data=None, last_ai_move=None):
    """
    Enhances the board drawing with dynamic data about the player's turn and game state.

    Arguments:
        hint_col: Column index for the hint (highlighted during HUMAN_VS_AI mode).
        message: Optional status message for additional info like game state feedback.
        game_over: Stops rendering "Player Turn" when the game has ended.
        mcts_data: Dictionary containing MCTS statistics (win rates, visits, UCB scores).
        last_ai_move: The column of the last AI move (to display UCB).
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
    draw_hud(screen, font, DEFAULT_GAME_MODE, state.current_player, message)

    # Draw MCTS stats if available
    if mcts_data and not game_over and SHOW_WIN_RATES:
        draw_mcts_stats(screen, font, mcts_data, state.current_player)

    # Draw UCB score of last AI move
    if last_ai_move is not None and mcts_data:
        draw_ucb_message(screen, font, last_ai_move, mcts_data)

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


def animate_drop(screen, state, col, player, font, hint_col, message, mcts_data=None, last_ai_move=None):
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
        mcts_data: MCTS statistics to display.
        last_ai_move: The column of the last AI move.
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
        draw_board(screen, state, font, hint_col, message,
                   mcts_data=mcts_data, last_ai_move=last_ai_move)
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

    # Initialize PyGame and window
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect 4 with MCTS (Enhanced Edition)")
    font = pygame.font.SysFont("arial", 30)
    clock = pygame.time.Clock()

    # Game State Initialization
    state = Connect4State()
    game_over = False
    message = "Player 1 Turn"

    # Set the game mode (Human vs Human, Human vs AI, AI vs AI)
    GAME_MODE = DEFAULT_GAME_MODE
    hint_col = None
    mcts_data = {}
    last_ai_move = None

    # Generate the first AI hint and MCTS stats if playing Human vs AI
    if GAME_MODE == HUMAN_VS_AI and SHOW_WIN_RATES:
        message = "Analyzing moves..."
        draw_board(screen, state, font, hint_col,
                   message, game_over, mcts_data)
        mcts_data = analyze_move_win_rates(state, n_iter=WIN_RATE_ITERATIONS)
        if mcts_data and 'win_rates' in mcts_data:
            hint_col = max(
                mcts_data['win_rates'], key=mcts_data['win_rates'].get) if mcts_data['win_rates'] else None
        message = "Your Turn"

    # For testing: run AI vs AI simulations if selected
    # if GAME_MODE == AI_VS_AI:
    #     simulate_games(simulations=10)

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
                    last_ai_move = None
                    message = "Analyzing moves..." if GAME_MODE == HUMAN_VS_AI and SHOW_WIN_RATES else "Player 1 Turn"

                    if GAME_MODE == HUMAN_VS_AI and SHOW_WIN_RATES:
                        draw_board(screen, state, font, None,
                                   message, game_over, {})
                        mcts_data = analyze_move_win_rates(
                            state, n_iter=WIN_RATE_ITERATIONS)
                        if mcts_data and 'win_rates' in mcts_data:
                            hint_col = max(
                                mcts_data['win_rates'], key=mcts_data['win_rates'].get) if mcts_data['win_rates'] else None
                        message = "Your Turn"
                    else:
                        hint_col = None
                        mcts_data = {}

            # Handle mouse clicks for human moves
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and GAME_MODE in [HUMAN_VS_HUMAN, HUMAN_VS_AI]:
                col = event.pos[0] // SQUARESIZE
                if col in state.get_legal_moves():
                    animate_drop(screen, state, col,
                                 state.current_player, font, hint_col, message, mcts_data, last_ai_move)
                    state.make_move(col)
                    thinking_frame = 0
                    mcts_data = {}  # Clear MCTS data after move
                    last_ai_move = None

                    # Check if the game is over after human move
                    game_over, message = check_game_over(state)

                    # If AI's turn in Human vs AI, show thinking animation and let AI play
                    if not game_over and GAME_MODE == HUMAN_VS_AI:
                        thinking_frame += 1
                        message = animated_thinking_text(
                            f"AI Player {state.current_player} thinking", thinking_frame
                        )
                        draw_board(screen, state, font, hint_col=None,
                                   message=message, game_over=game_over, mcts_data=None, last_ai_move=None)

                        # Remember current player before the AI makes the move
                        ai_player = state.current_player

                        # AI makes its move and gets statistics
                        ai_move, ai_stats = ai_play_move(
                            state, n_iter=AI_ITER[ai_player])

                        last_ai_move = ai_move

                        # Animate drop for the correct player (ai_player)
                        animate_drop(screen, state, ai_move,
                                     ai_player, font, hint_col, message, ai_stats, last_ai_move)

                        # Check if the game is over after AI move
                        game_over, message = check_game_over(state)

                        # Calculate new MCTS stats for human's next turn
                        if not game_over and SHOW_WIN_RATES:
                            message = "Analyzing moves..."
                            draw_board(screen, state, font, None,
                                       message, game_over, {}, last_ai_move)
                            mcts_data = analyze_move_win_rates(
                                state, n_iter=WIN_RATE_ITERATIONS)
                            if mcts_data and 'win_rates' in mcts_data:
                                hint_col = max(
                                    mcts_data['win_rates'], key=mcts_data['win_rates'].get) if mcts_data['win_rates'] else None
                            message = "Your Turn"

        # AI vs AI Logic: let both AIs play automatically
        if not game_over and GAME_MODE == AI_VS_AI:
            pygame.time.delay(500)  # Slow down for visibility
            message = f"AI Player {state.current_player} is thinking..."
            draw_board(screen, state, font, hint_col=None,
                       message=message, game_over=game_over, mcts_data=None, last_ai_move=last_ai_move)

            ai_player = state.current_player
            move, ai_stats = ai_play_move(state, n_iter=AI_ITER[ai_player])
            last_ai_move = move

            animate_drop(screen, state, move, ai_player,
                         font, hint_col, message, ai_stats, last_ai_move)
            thinking_frame = 0
            game_over, message = check_game_over(state)

        # Draw the updated board after every event/AI move
        draw_board(screen, state, font, hint_col, message, game_over=game_over,
                   mcts_data=mcts_data, last_ai_move=last_ai_move)
        clock.tick(FPS)

    # Exit the Game Loop and close PyGame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
