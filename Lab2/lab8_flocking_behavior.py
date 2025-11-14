# =====================================================================
# flocking_behavior.py
# Lab 8: Flocking Behavior
# Course: Games and AI Techniques
# =====================================================================
# Goal:
#   Show how a group of agents (boids) can move like a flock
#   using three local steering rules:
#     - Separation: avoid crowding neighbors
#     - Alignment: match heading with neighbors
#     - Cohesion: move toward the local center of mass
# =====================================================================

import pygame
import math
import random

# ---------------------------------------------------------------------
# Pygame setup
# ---------------------------------------------------------------------
pygame.init()

# Window size
WIDTH, HEIGHT = 900, 600

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behavior: FLOCKING")

# Clock to limit FPS
clock = pygame.time.Clock()


# ---------------------------------------------------------------------
# Vector helper functions (2D)
# ---------------------------------------------------------------------
def vec_length(v):
    """Return the length (magnitude) of vector v."""
    return math.sqrt(v[0] ** 2 + v[1] ** 2)


def vec_normalize(v):
    """
    Return a unit vector in the same direction as v.
    If v is zero, return (0, 0).
    """
    length = vec_length(v)
    if length == 0:
        return (0, 0)
    return (v[0] / length, v[1] / length)


def vec_add(a, b):
    """Return the sum of vectors a and b."""
    return (a[0] + b[0], a[1] + b[1])


def vec_sub(a, b):
    """Return the vector a - b."""
    return (a[0] - b[0], a[1] - b[1])


def vec_mul(v, s):
    """Return vector v scaled by scalar s."""
    return (v[0] * s, v[1] * s)


def vec_limit(v, max_value):
    """
    Limit the magnitude of v to at most max_value.
    If it's already smaller, return v unchanged.
    """
    length = vec_length(v)
    if length > max_value:
        v = vec_normalize(v)
        return (v[0] * max_value, v[1] * max_value)
    return v


# ---------------------------------------------------------------------
# Boid class: one agent in the flock
# ---------------------------------------------------------------------
class Boid:
    def __init__(self, x, y):
        """
        Initialize a boid at position (x, y) with a random velocity.
        """
        # Current position
        self.position = (x, y)

        # Random initial velocity direction
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = (math.cos(angle) * 2.0, math.sin(angle) * 2.0)

        # Current acceleration (steering force); reset each frame
        self.acceleration = (0, 0)

        # Movement constraints
        self.max_speed = 4.0      # maximum speed
        self.max_force = 0.05     # maximum steering force

        # How far this boid can "see" neighbors
        self.perception = 70.0

    # -----------------------------------------------------------------
    # Flocking rule 1: Separation
    # -----------------------------------------------------------------
    def separation(self, boids):
        """
        Separation rule:
        Steer away from boids that are too close to avoid crowding.
        """
        steering_sum = (0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            # Distance between self and other
            distance = vec_length(vec_sub(self.position, other.position))

            # Only consider boids that are within half the perception distance
            if 0 < distance < self.perception / 2:
                # Direction away from the neighbor
                diff = vec_sub(self.position, other.position)
                diff = vec_normalize(diff)

                # Closer boids have stronger effect (1 / distance)
                diff = vec_mul(diff, 1 / distance)

                steering_sum = vec_add(steering_sum, diff)
                count += 1

        if count > 0:
            # Average steering direction
            steering_sum = vec_mul(steering_sum, 1 / count)

            # Turn this into a desired velocity
            desired = vec_normalize(steering_sum)
            desired = vec_mul(desired, self.max_speed)

            # Steering = desired - current velocity
            steer = vec_sub(desired, self.velocity)
            steer = vec_limit(steer, self.max_force * 1.5)  # separation a bit stronger
            return steer

        # No close neighbors -> no separation force
        return (0, 0)

    # -----------------------------------------------------------------
    # Flocking rule 2: Alignment
    # -----------------------------------------------------------------
    def alignment(self, boids):
        """
        Alignment rule:
        Steer toward the average heading (velocity) of nearby boids.
        """
        avg_velocity = (0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            distance = vec_length(vec_sub(self.position, other.position))

            # Consider neighbors within perception radius
            if distance < self.perception:
                avg_velocity = vec_add(avg_velocity, other.velocity)
                count += 1

        if count > 0:
            # Average the neighbor velocities
            avg_velocity = vec_mul(avg_velocity, 1 / count)

            # Turn into desired velocity
            desired = vec_normalize(avg_velocity)
            desired = vec_mul(desired, self.max_speed)

            # Steering force to adjust current velocity toward desired
            steer = vec_sub(desired, self.velocity)
            steer = vec_limit(steer, self.max_force)
            return steer

        return (0, 0)

    # -----------------------------------------------------------------
    # Flocking rule 3: Cohesion
    # -----------------------------------------------------------------
    def cohesion(self, boids):
        """
        Cohesion rule:
        Steer toward the average position (center of mass) of neighbors.
        """
        center_of_mass = (0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            distance = vec_length(vec_sub(self.position, other.position))

            # Consider neighbors within perception radius
            if distance < self.perception:
                center_of_mass = vec_add(center_of_mass, other.position)
                count += 1

        if count > 0:
            # Average position of neighbors
            center_of_mass = vec_mul(center_of_mass, 1 / count)

            # Use seek to move toward this center point
            return self.seek(center_of_mass)

        return (0, 0)

    # -----------------------------------------------------------------
    # Seek helper: used by cohesion
    # -----------------------------------------------------------------
    def seek(self, target):
        """
        Basic seek behavior:
        Return a steering force that moves toward 'target'.
        """
        desired = vec_sub(target, self.position)
        desired = vec_normalize(desired)
        desired = vec_mul(desired, self.max_speed)

        steer = vec_sub(desired, self.velocity)
        steer = vec_limit(steer, self.max_force)
        return steer

    # -----------------------------------------------------------------
    # Combine all three flocking behaviors
    # -----------------------------------------------------------------
    def apply_behaviors(self, boids):
        """
        Compute separation, alignment, and cohesion,
        then blend their forces and store as acceleration.
        """
        # Compute each rule
        sep = self.separation(boids)   # avoid crowding
        ali = self.alignment(boids)    # match heading
        coh = self.cohesion(boids)     # move toward group center

        # Weight each force to tune the behavior
        sep = vec_mul(sep, 1.5)
        ali = vec_mul(ali, 1.0)
        coh = vec_mul(coh, 1.0)

        # Sum all steering forces
        steering = vec_add(vec_add(sep, ali), coh)

        # Add to acceleration (forces accumulate for this frame)
        self.acceleration = vec_add(self.acceleration, steering)

    # -----------------------------------------------------------------
    # Physics update
    # -----------------------------------------------------------------
    def update(self):
        """
        Apply acceleration, update velocity and position,
        then wrap around the screen edges.
        """
        # Velocity changes by acceleration
        self.velocity = vec_add(self.velocity, self.acceleration)
        self.velocity = vec_limit(self.velocity, self.max_speed)

        # Position changes by velocity
        self.position = vec_add(self.position, self.velocity)

        # Reset acceleration for the next frame
        self.acceleration = (0, 0)

        # Screen wrapping (boid exits one side and re-enters from opposite)
        x, y = self.position

        if x > WIDTH:
            x = 0
        elif x < 0:
            x = WIDTH

        if y > HEIGHT:
            y = 0
        elif y < 0:
            y = HEIGHT

        self.position = (x, y)

    # -----------------------------------------------------------------
    # Drawing the boid
    # -----------------------------------------------------------------
    def draw(self, surface):
        """
        Draw the boid as a small triangle pointing in its direction of travel.
        """
        x, y = self.position

        # Compute facing angle from velocity
        if vec_length(self.velocity) == 0:
            angle = 0
        else:
            angle = math.degrees(math.atan2(-self.velocity[1], self.velocity[0]))

        size = 10  # triangle size

        # Triangle vertices relative to the boid's position and facing
        points = [
            # Tip (forward)
            (x + math.cos(math.radians(angle)) * size,
             y - math.sin(math.radians(angle)) * size),

            # Back-left
            (x + math.cos(math.radians(angle + 120)) * size * 0.5,
             y - math.sin(math.radians(angle + 120)) * size * 0.5),

            # Back-right
            (x + math.cos(math.radians(angle - 120)) * size * 0.5,
             y - math.sin(math.radians(angle - 120)) * size * 0.5)
        ]

        pygame.draw.polygon(surface, (0, 255, 180), points)


# ---------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------
def main():
    """
    Run the flocking demo:
    - create a list of boids
    - update their flocking behavior every frame
    - draw them to the screen
    """
    running = True

    # Create a bunch of boids at random positions
    boids = [
        Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        for _ in range(40)
    ]

    while running:
        # Limit to ~60 FPS
        dt = clock.tick(60) / 1000.0  # (dt not used yet, but useful later)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # First, compute behaviors (based on neighbors)
        for b in boids:
            b.apply_behaviors(boids)

        # Then update positions using the accumulated acceleration
        for b in boids:
            b.update()

        # Clear screen
        screen.fill((25, 25, 30))

        # Draw all boids
        for b in boids:
            b.draw(screen)

        # On-screen text
        font = pygame.font.SysFont("consolas", 20)
        text = font.render(
            "Flocking: Separation + Alignment + Cohesion",
            True,
            (255, 255, 255)
        )
        screen.blit(text, (20, 20))

        # Present frame
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
