# Board dimensions
ROWS = 6
COLS = 7
EMPTY = 0

# Players
PLAYER1 = 1
PLAYER2 = 2

# Game modes
HUMAN_VS_HUMAN = 0
HUMAN_VS_AI = 1
AI_VS_AI = 2

# Set the default game mode - Uncomment the mode you'd like to use
DEFAULT_GAME_MODE = HUMAN_VS_AI  # Human vs AI
# DEFAULT_GAME_MODE = AI_VS_AI    # AI vs AI
# DEFAULT_GAME_MODE = HUMAN_VS_HUMAN  # Human vs Human

# AI strength (iterations per move)
AI_ITER = {
    PLAYER1: 300,  # Weaker AI for Player 1
    PLAYER2: 500,  # Stronger AI for Player 2
}

# Visual settings for PyGame
SQUARESIZE = 100
RADIUS = SQUARESIZE // 2 - 5
FPS = 60

# Colors (RGB format)
BACKGROUND_COLOR = (30, 30, 30)
BOARD_COLOR = (20, 60, 120)
PLAYER1_COLOR = (220, 50, 50)  # Red
PLAYER2_COLOR = (240, 220, 70)  # Yellow
HINT_COLOR = (80, 200, 120)
TEXT_COLOR = (240, 240, 240)

# Calculate screen size based on board dimensions
WIDTH = COLS * SQUARESIZE
# Add 2 extra rows: 1 for the hint marker and 1 for the message
HEIGHT = (ROWS + 2) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
