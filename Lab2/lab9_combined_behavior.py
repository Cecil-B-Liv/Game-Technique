# =====================================================================
# combined_behavior.py
# Lab 9: Combined Behaviors – Path Following + Collision Avoidance + Flocking
# Course: Games and AI Techniques
# =====================================================================
# Goal:
#   Demonstrate how multiple steering behaviors can be blended together.
#   Each boid (agent) simultaneously:
#     • Follows a visible path
#     • Avoids circular obstacles
#     • Applies flocking rules (Separation, Alignment, Cohesion)
# =====================================================================

import pygame, math, random

# ---------------------------------------------------------------------
# 1.  Initialize pygame and create the display window
# ---------------------------------------------------------------------
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behavior: Combined Behaviors")
clock = pygame.time.Clock()

# ---------------------------------------------------------------------
# 2.  Basic vector math helper functions (for 2D tuples)
# ---------------------------------------------------------------------
def vec_length(v):
    """Return the magnitude (length) of vector v."""
    return math.sqrt(v[0]**2 + v[1]**2)

def vec_normalize(v):
    """Return a unit vector in the same direction as v."""
    l = vec_length(v)
    if l == 0:
        return (0, 0)
    return (v[0]/l, v[1]/l)

def vec_add(a, b): return (a[0]+b[0], a[1]+b[1])
def vec_sub(a, b): return (a[0]-b[0], a[1]-b[1])
def vec_mul(v, s): return (v[0]*s, v[1]*s)

def vec_limit(v, maxv):
    """Limit the magnitude of v to at most maxv."""
    l = vec_length(v)
    if l > maxv:
        v = vec_normalize(v)
        return (v[0]*maxv, v[1]*maxv)
    return v

# ---------------------------------------------------------------------
# 3.  Environment classes – Path and Obstacle
# ---------------------------------------------------------------------
class Path:
    """Defines a curved polyline path for the boids to follow."""
    def __init__(self):
        # List of points forming a smooth path
        self.points = [
            (100, 400), (250, 250), (400, 200),
            (550, 300), (700, 450), (600, 520), (300, 500)
        ]
        # How far a boid can drift before correcting back to the path
        self.radius = 40

    def draw(self, surface):
        """Draw the path line and its small anchor points."""
        for i in range(len(self.points) - 1):
            pygame.draw.line(surface, (80, 80, 80),
                             self.points[i], self.points[i+1], 2)
        for p in self.points:
            pygame.draw.circle(surface, (120, 120, 120),
                               (int(p[0]), int(p[1])), 4)

class Obstacle:
    """Represents a static circular obstacle."""
    def __init__(self, x, y, r):
        self.pos = (x, y)
        self.radius = r

    def draw(self, surface):
        """Draw the obstacle as a filled gray circle."""
        pygame.draw.circle(surface, (160, 160, 160),
                           (int(self.pos[0]), int(self.pos[1])), self.radius)

# ---------------------------------------------------------------------
# 4.  Boid class – combines all steering behaviors
# ---------------------------------------------------------------------
class Boid:
    def __init__(self, x, y):
        """Initialize a boid with random velocity and default limits."""
        self.position = (x, y)
        # Give it a small random starting velocity
        angle = random.uniform(0, 2*math.pi)
        self.velocity = (math.cos(angle)*2, math.sin(angle)*2)
        # Acceleration accumulates steering forces each frame
        self.acceleration = (0, 0)

        # Movement constraints
        self.max_speed = 4.0      # how fast it can move
        self.max_force = 0.08     # how strong steering can be
        self.perception = 70      # how far it senses neighbors

    # -------------------------------------------------------------
    #  SEEK behavior (used by other rules)
    # -------------------------------------------------------------
    def seek(self, target):
        """Return steering force toward a target point."""
        desired = vec_sub(target, self.position)
        desired = vec_mul(vec_normalize(desired), self.max_speed)
        steer = vec_limit(vec_sub(desired, self.velocity), self.max_force)
        return steer

    # -------------------------------------------------------------
    #  PATH FOLLOWING
    # -------------------------------------------------------------
    def follow_path(self, path):
        """Predict ahead and stay close to the defined path."""
        # Predict future position along velocity direction
        predict = vec_mul(vec_normalize(self.velocity), 50)
        predict_pos = vec_add(self.position, predict)

        # Find nearest point on path to the predicted position
        closest = self._closest_point_on_path(predict_pos, path.points)
        dist = vec_length(vec_sub(predict_pos, closest))

        # If predicted pos is too far from the path, steer toward it
        if dist > path.radius:
            return self.seek(closest)
        return (0, 0)

    def _closest_point_on_path(self, p, pts):
        """Find the nearest projection of p onto the polyline."""
        closest = pts[0]
        min_d = float('inf')
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i+1]
            ap = vec_sub(p, a)
            ab = vec_sub(b, a)
            ab = vec_normalize(ab)
            # Project vector ap onto ab
            proj_len = ap[0]*ab[0] + ap[1]*ab[1]
            proj = vec_mul(ab, proj_len)
            n = vec_add(a, proj)
            # Clamp projection to segment endpoints
            if (n[0] < min(a[0], b[0]) or n[0] > max(a[0], b[0]) or
                n[1] < min(a[1], b[1]) or n[1] > max(a[1], b[1])):
                n = b
            d = vec_length(vec_sub(p, n))
            if d < min_d:
                min_d = d
                closest = n
        return closest

    # -------------------------------------------------------------
    #  OBSTACLE AVOIDANCE
    # -------------------------------------------------------------
    def avoid_obstacles(self, obstacles):
        """Steer away from any obstacle that is too close."""
        total = (0, 0)
        for o in obstacles:
            to_obs = vec_sub(o.pos, self.position)
            dist = vec_length(to_obs)
            safe = o.radius + 25  # safety margin around obstacle
            if 0 < dist < safe:
                # Compute steering force directly away from obstacle center
                away = vec_mul(vec_normalize(
                    vec_sub(self.position, o.pos)), self.max_speed)
                steer = vec_limit(vec_sub(away, self.velocity),
                                  self.max_force * 2)
                total = vec_add(total, steer)
        return total

    # -------------------------------------------------------------
    #  FLOCKING RULES
    # -------------------------------------------------------------
    def separation(self, boids):
        """Steer away from neighbors that are too close."""
        steer = (0, 0)
        count = 0
        for o in boids:
            if o is self:
                continue
            d = vec_length(vec_sub(self.position, o.position))
            if 0 < d < self.perception / 2:
                diff = vec_mul(vec_normalize(
                    vec_sub(self.position, o.position)), 1/d)
                steer = vec_add(steer, diff)
                count += 1
        if count > 0:
            steer = vec_mul(steer, 1/count)
            steer = vec_sub(vec_mul(vec_normalize(steer), self.max_speed),
                            self.velocity)
            steer = vec_limit(steer, self.max_force * 1.5)
            return steer
        return (0, 0)

    def alignment(self, boids):
        """Match average velocity (heading) of nearby boids."""
        avg = (0, 0)
        count = 0
        for o in boids:
            if o is self:
                continue
            d = vec_length(vec_sub(self.position, o.position))
            if d < self.perception:
                avg = vec_add(avg, o.velocity)
                count += 1
        if count > 0:
            avg = vec_mul(avg, 1/count)
            desired = vec_mul(vec_normalize(avg), self.max_speed)
            steer = vec_limit(vec_sub(desired, self.velocity), self.max_force)
            return steer
        return (0, 0)

    def cohesion(self, boids):
        """Move toward the center of nearby boids."""
        center = (0, 0)
        count = 0
        for o in boids:
            if o is self:
                continue
            d = vec_length(vec_sub(self.position, o.position))
            if d < self.perception:
                center = vec_add(center, o.position)
                count += 1
        if count > 0:
            center = vec_mul(center, 1/count)
            return self.seek(center)
        return (0, 0)

    # -------------------------------------------------------------
    #  COMBINE ALL BEHAVIORS
    # -------------------------------------------------------------
    def apply_behaviors(self, boids, path, obstacles):
        """Blend all steering behaviors together into one force."""
        sep = vec_mul(self.separation(boids), 1.5)
        ali = self.alignment(boids)
        coh = self.cohesion(boids)
        path_follow = self.follow_path(path)
        avoid = self.avoid_obstacles(obstacles)
        # Sum all individual steering forces
        total = vec_add(vec_add(vec_add(vec_add(sep, ali), coh),
                                path_follow), avoid)
        # Apply the total as this frame's acceleration
        self.acceleration = vec_add(self.acceleration, total)

    # -------------------------------------------------------------
    #  UPDATE PHYSICS AND DRAW
    # -------------------------------------------------------------
    def update(self):
        """Update velocity, position, and wrap around screen edges."""
        # Apply acceleration to velocity
        self.velocity = vec_limit(vec_add(self.velocity, self.acceleration),
                                  self.max_speed)
        # Move position by velocity
        self.position = vec_add(self.position, self.velocity)
        # Reset acceleration for next frame
        self.acceleration = (0, 0)

        # Screen wrapping logic
        x, y = self.position
        if x > WIDTH:
            x = 0
        if x < 0:
            x = WIDTH
        if y > HEIGHT:
            y = 0
        if y < 0:
            y = HEIGHT
        self.position = (x, y)

    def draw(self, surf):
        """Draw the boid as a triangle pointing in its velocity direction."""
        x, y = self.position
        angle = 0 if vec_length(self.velocity) == 0 else math.degrees(
            math.atan2(-self.velocity[1], self.velocity[0]))
        size = 10
        pts = [
            (x + math.cos(math.radians(angle)) * size,
             y - math.sin(math.radians(angle)) * size),
            (x + math.cos(math.radians(angle + 120)) * size * 0.5,
             y - math.sin(math.radians(angle + 120)) * size * 0.5),
            (x + math.cos(math.radians(angle - 120)) * size * 0.5,
             y - math.sin(math.radians(angle - 120)) * size * 0.5)
        ]
        pygame.draw.polygon(surf, (0, 255, 180), pts)

# ---------------------------------------------------------------------
# 5.  MAIN GAME LOOP
# ---------------------------------------------------------------------
def main():
    """Run the simulation showing all combined behaviors."""
    running = True

    # Create the environment: path and obstacles
    path = Path()
    obstacles = [
        Obstacle(300, 350, 25),
        Obstacle(500, 250, 30),
        Obstacle(650, 400, 35)
    ]

    # Create a flock of boids at random positions
    boids = [Boid(random.randint(0, WIDTH),
                  random.randint(0, HEIGHT)) for _ in range(25)]

    while running:
        # Control frame rate (~60 FPS)
        dt = clock.tick(60) / 1000.0

        # --- Handle user events (e.g., quit) ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # --- Update all boids ---
        for b in boids:
            b.apply_behaviors(boids, path, obstacles)
        for b in boids:
            b.update()

        # --- Drawing section ---
        screen.fill((30, 30, 35))        # dark background
        path.draw(screen)                # draw the path
        for o in obstacles:
            o.draw(screen)               # draw obstacles
        for b in boids:
            b.draw(screen)               # draw each boid

        # Display instructional text
        font = pygame.font.SysFont("consolas", 18)
        msg = font.render(
            "Combined: Flocking + Path Following + Avoidance", True, (255, 255, 255))
        screen.blit(msg, (20, 20))
        pygame.display.flip()

    pygame.quit()

# Run the program
if __name__ == "__main__":
    main()
