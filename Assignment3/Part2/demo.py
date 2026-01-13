import pygame
import sys

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600  # Screen dimensions
PLAYER_SIZE = 20          # Player size
PLAYER_COLOR = (0, 255, 0)  # Green
BG_COLOR = (0, 0, 0)  # Black background
FPS = 60

# Setup Game Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deep RL Arena")

# Player Initialization
player_pos = [WIDTH // 2, HEIGHT // 2]  # Start in the middle
player_speed = 5

# Main Game Loop
clock = pygame.time.Clock()
while True:
    # Event Handling (Close the game on quit)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Keyboard Handling for Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:  # Move Up
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN]:  # Move Down
        player_pos[1] += player_speed
    if keys[pygame.K_LEFT]:  # Move Left
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT]:  # Move Right
        player_pos[0] += player_speed

    # Render Graphics
    screen.fill(BG_COLOR)  # Clear screen
    pygame.draw.rect(screen, PLAYER_COLOR, (*player_pos, PLAYER_SIZE, PLAYER_SIZE))
    pygame.display.flip()  # Update screen

    # Keep the game running at a constant FPS
    clock.tick(FPS)