# =====================================================================
# arrival_behavior.py
# Lab 3: Arrival Behavior
# Course: Games and AI Techniques
# =====================================================================
# Goal:
#   Show how an agent can move toward a target and slow down smoothly
#   as it approaches, using Arrival steering behavior.
# =====================================================================

import pygame
import math
pygame.init()

# -----------------------------
# Window setup
# -----------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behavior: ARRIVAL")
clock = pygame.time.Clock()

# -----------------------------
# Vector helper functions
# -----------------------------


def vec_length(v):
    """Return the length (magnitude) of a 2D vector."""
    return math.sqrt(v[0]**2 + v[1]**2)


def vec_normalize(v):
    """Return a unit (length = 1) version of a vector."""
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

# -----------------------------
# Agent (the green triangle)
# -----------------------------


class Agent:
    def __init__(self, x, y):
        """Initialize the agent with position, velocity, etc."""
        self.position = (x, y)
        self.velocity = (0, 0)
        self.acceleration = (0, 0)
        self.max_speed = 4.0
        self.max_force = 0.1
        self.slowing_radius = 100.0

    def arrive(self, target):
        """ARRIVAL: move toward target and slow down near it."""
        desired = vec_sub(target, self.position)
        distance = vec_length(desired)
        if distance < 0.5:
            self.velocity = (0, 0)
            return # Stop moving when very close
        desired = vec_normalize(desired)
        if distance < self.slowing_radius:
            scaled_speed = self.max_speed * (distance / self.slowing_radius)
        else:
            scaled_speed = self.max_speed
        desired = vec_mul(desired, scaled_speed)
        steer = vec_sub(desired, self.velocity)
        steer = vec_limit(steer, self.max_force)
        self.acceleration = steer

    def update(self):
        """Update velocity and position based on acceleration."""
        self.velocity = vec_add(self.velocity, self.acceleration)
        self.velocity = vec_limit(self.velocity, self.max_speed)
        self.position = vec_add(self.position, self.velocity)
        self.acceleration = (0, 0)

    def draw(self, surface):
        """Draw the agent as a triangle pointing along its velocity."""
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

# -----------------------------
# Main game loop
# -----------------------------


def main():
    """Run the ARRIVAL behavior demo."""
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

        agent.arrive(target)
        agent.update()

        screen.fill((30, 30, 30))
        pygame.draw.circle(screen, (255, 60, 60),
                           (int(target[0]), int(target[1])), 8)
        agent.draw(screen)

        font = pygame.font.SysFont("consolas", 20)
        text = font.render(
            "Click - agent arrives and slows near target", True, (255, 255, 255))
        screen.blit(text, (20, 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
