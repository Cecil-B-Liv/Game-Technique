# =====================================================================
# seek_behavior.py
# Lab 1: Seek Behavior
# Course: Games and AI Techniques
# =====================================================================
# Goal:
#   Show how an agent (triangle) can smoothly move toward a target
#   using simple steering physics.
#
# Concepts reviewed #$ Please refer to the lecture on Stering Vehavior:
#   - position, velocity, acceleration
#   - desired velocity
#   - steering = desired - velocity
#   - apply steering gradually to move toward the target
# =====================================================================

import pygame
import math
pygame.init()

# ----
# Window settings of our display game
####
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behavior: SEEK")
clock = pygame.time.Clock()

# --
# Vector helper functions
########


def vec_length(v):
    """Return the length (magnitude) of a 2D vector."""
    return math.sqrt(v[0]**2 + v[1]**2)


def vec_normalize(v):
    """Return the normalized (unit) version of a vector."""
    length = vec_length(v)
    if length == 0:
        return (0, 0)
    return (v[0]/length, v[1]/length)


def vec_sub(a, b):
    """Subtract vector b from a."""
    return (a[0]-b[0], a[1]-b[1])


def vec_add(a, b):
    """Add two vectors."""
    return (a[0]+b[0], a[1]+b[1])


def vec_mul(v, scalar):
    """Multiply a vector by a scalar."""
    return (v[0]*scalar, v[1]*scalar)


def vec_limit(v, max_value):
    """Limit the magnitude of a vector to max_value."""
    length = vec_length(v)
    if length > max_value:
        v = vec_normalize(v)
        return (v[0]*max_value, v[1]*max_value)
    return v

####
# Our Agent (the green triangle)
####


class Agent:
    def __init__(self, x, y):
        """Initialize the agent with position, velocity, etc."""
        self.position = (x, y)
        self.velocity = (0, 0)
        self.acceleration = (0, 0)
        self.max_speed = 4.0
        self.max_force = 0.1

    def seek(self, target):
        """Steer smoothly toward the target."""
        desired = vec_sub(target, self.position)
        desired = vec_normalize(desired)
        desired = vec_mul(desired, self.max_speed)
        steer = vec_sub(desired, self.velocity)
        steer = vec_limit(steer, self.max_force)
        self.acceleration = steer

    def update(self):
        """Update physics each frame."""
        self.velocity = vec_add(self.velocity, self.acceleration)
        self.velocity = vec_limit(self.velocity, self.max_speed)
        self.position = vec_add(self.position, self.velocity)
        self.acceleration = (0, 0)

    def draw(self, surface):
        """Draw the agent as a triangle pointing in its velocity direction."""
        x, y = self.position
        if vec_length(self.velocity) == 0:
            angle = 0
        else:
            angle = math.degrees(
                math.atan2(-self.velocity[1], self.velocity[0]))
        size = 15
        points = [
            (x + math.cos(math.radians(angle)) * size,
             y - math.sin(math.radians(angle)) * size),
            (x + math.cos(math.radians(angle + 120)) * size * 0.5,
             y - math.sin(math.radians(angle + 120)) * size * 0.5),
            (x + math.cos(math.radians(angle - 120)) * size * 0.5,
             y - math.sin(math.radians(angle - 120)) * size * 0.5)
        ]
        pygame.draw.polygon(surface, (0, 255, 0), points)


# The Main

def main():
    """Run the SEEK behavior demo."""
    running = True
    agent = Agent(WIDTH // 2, HEIGHT // 2)
    target = (WIDTH // 2, HEIGHT // 2)

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                target = pygame.mouse.get_pos()

        agent.seek(target)
        agent.update()

        screen.fill((30, 30, 30))
        pygame.draw.circle(screen, (255, 60, 60),
                           (int(target[0]), int(target[1])), 8)
        agent.draw(screen)

        font = pygame.font.SysFont("consolas", 20)
        text = font.render(
            "Click anywhere - agent seeks target", True, (255, 255, 255))
        screen.blit(text, (20, 20))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
