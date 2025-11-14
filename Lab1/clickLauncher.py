# Step 1 - Import pygame and initialize it
# pygame.init() sets up all the internal modules you will use later
import pygame
pygame.init()

# Step 2 - Create the game window and a clock to measure frame time
# WIDTH and HEIGHT control your window resolution
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Click Launcher")

# The clock lets you limit FPS (frame per second) and compute a stable delta time (dt)
clock = pygame.time.Clock()

# Step 3 - Define where the launcher sits, how big it is, and default aim
CENTER = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)  # screen center
LAUNCHER_RADIUS = 16                                   # circle size
BAR_LENGTH = 28                                        # aim bar length

# The launcher starts by facing right (unit vector pointing right)
aim_direction = pygame.math.Vector2(1, 0)

# Colors in RGB format
BACKGROUND = (24, 26, 30)        # dark background
LAUNCHER_COLOR = (200, 220, 255)  # pale blue launcher
ORB_COLOR = (120, 240, 120)      # green orbs

# Step 4 - Helper functions used to compute aim and launcher tip
def direction_from_center(target_pos):
    """Return a unit vector from the launcher center toward the clicked point."""
    v = pygame.math.Vector2(target_pos) - CENTER
    if v.length() == 0:
        # If you click exactly at the center, keep facing right
        return pygame.math.Vector2(1, 0)
    return v.normalize()

def tip_position(aim_vector):
    """Return the endpoint of the launcher bar where the orb should spawn."""
    return CENTER + aim_vector * (LAUNCHER_RADIUS + BAR_LENGTH)

# Step 5 - Sprite group to manage and draw all active orbs
orbs = pygame.sprite.Group()

# Step 6 - A small glowing orb that moves in the aim direction
class EnergyOrb(pygame.sprite.Sprite):
    """
    A small glowing orb that travels in the direction the Launcher is pointing.
    Uses Vector2 for smooth subpixel motion.
    """
    def __init__(self, start_pos, aim_vector, speed=520):
        super().__init__()

        # Create a small circular image with alpha channel
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORB_COLOR, (5, 5), 5)
        self.rect = self.image.get_rect(center=start_pos)

        # Position and velocity as vectors
        self.position = pygame.math.Vector2(start_pos)
        self.velocity = pygame.math.Vector2(
            aim_vector) * speed  # pixels per second

    def update(self, dt):
        # Move by velocity scaled by delta time
        self.position += self.velocity * dt
        self.rect.center = (round(self.position.x), round(self.position.y))

        # If the orb goes off-screen, remove it to keep performance healthy
        if (self.rect.right < -20 or self.rect.left > WIDTH + 20 or
                self.rect.bottom < -20 or self.rect.top > HEIGHT + 20):
            self.kill()

# Step 7 - Main game loop
# - Poll events such as window close and mouse clicks
# - Update sprite positions using dt from the clock
# - Draw launcher, aim bar, and any active orbs
running = True
while running:
    # dt is time since last frame in seconds - keeps motion consistent
    dt = clock.tick(60) / 1000.0  # targeting 60 FPS

    # 1) Handle window events and user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # User clicked the close button - exit loop
            running = False

        # Left mouse click spawns an orb in the current aim direction
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Recompute aim toward the click point
            aim_direction = direction_from_center(event.pos)
            # Spawn an orb at the tip of the launcher bar
            start = tip_position(aim_direction)
            orbs.add(EnergyOrb(start, aim_direction))

    # 2) Update all orbs with the current dt
    orbs.update(dt)

    # 3) Draw a fresh frame
    screen.fill(BACKGROUND)

    # Draw launcher body at the center
    pygame.draw.circle(screen, LAUNCHER_COLOR, CENTER, LAUNCHER_RADIUS)

    # Draw the launcher bar to indicate aim direction
    tip = tip_position(aim_direction)
    pygame.draw.line(screen, LAUNCHER_COLOR, CENTER, tip, 4)

    # Draw active orbs in the group
    orbs.draw(screen)

    # Push the frame to the display
    pygame.display.flip()

# Clean up when the window is closed
pygame.quit()
