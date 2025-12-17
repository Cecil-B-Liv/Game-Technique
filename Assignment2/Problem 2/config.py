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
# DEFAULT_GAME_MODE = HUMAN_VS_AI  # Human vs AI
DEFAULT_GAME_MODE = AI_VS_AI    # AI vs AI
# DEFAULT_GAME_MODE = HUMAN_VS_HUMAN  # Human vs Human

# AI strength (iterations per move)
AI_ITER = {
    PLAYER1: 300,  # Weaker AI for Player 1
    PLAYER2: 600,  # Stronger AI for Player 2
}

# Win rate analysis settings
SHOW_WIN_RATES = True  # Toggle win rate display
WIN_RATE_ITERATIONS = 300  # MCTS iterations for win rate calculation

# Visual settings for PyGame
SQUARESIZE = 100
RADIUS = SQUARESIZE // 2 - 5
FPS = 60

# Colors (RGB format)
BACKGROUND_COLOR = (25, 28, 36)         # Dark blue-gray background
BOARD_COLOR = (41, 98, 255)             # Vibrant blue for the board

# Player Colors - High Contrast & Modern
PLAYER1_COLOR = (255, 75, 75)           # Bright coral red (Human)
PLAYER2_COLOR = (255, 215, 0)           # Golden yellow (AI)

# UI Element Colors
HINT_COLOR = (0, 255, 170)              # Bright cyan-green for AI hints
TEXT_COLOR = (245, 245, 250)            # Off-white for text

WIN_RATE_BAR_BG = (50, 50, 50)  # Background for win rate bars
WIN_RATE_BAR_FG = (100, 200, 100)  # Foreground for win rate bars

# Calculate screen size based on board dimensions
WIDTH = COLS * SQUARESIZE
# Add 2 extra rows: 1 for the hint marker and 1 for the message
HEIGHT = (ROWS + 2) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
