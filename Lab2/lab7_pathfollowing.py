# =====================================================================
# path_following_behavior.py
# Lab 7: Path Following Behavior
# Course: Games and AI Techniques
# =====================================================================
# Goal:
#   Show how an agent can follow a defined route by predicting
#   its future position and steering back toward the path.
# =====================================================================

import pygame
import math

pygame.init()

# -----------------------------
# Window setup
# -----------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behavior: PATH FOLLOWING")
clock = pygame.time.Clock()

# -----------------------------
# Vector helpers
# -----------------------------


def vec_length(v):
    return math.sqrt(v[0]**2 + v[1]**2)


def vec_normalize(v):
    l = vec_length(v)
    if l == 0:
        return (0, 0)
    return (v[0]/l, v[1]/l)


def vec_sub(a, b):
    return (a[0]-b[0], a[1]-b[1])


def vec_add(a, b):
    return (a[0]+b[0], a[1]+b[1])


def vec_mul(v, s):
    return (v[0]*s, v[1]*s)


def vec_limit(v, max_value):
    l = vec_length(v)
    if l > max_value:
        v = vec_normalize(v)
        return (v[0]*max_value, v[1]*max_value)
    return v

# -----------------------------
# Path
# -----------------------------


class Path:
    def __init__(self):
        self.points = [
            (100, 300),
            (250, 200),
            (400, 150),
            (550, 250),
            (700, 350),
            (600, 450),
            (400, 500),
            (200, 400)
        ]
        self.radius = 20

    def draw(self, surface):
        for i in range(len(self.points) - 1):
            pygame.draw.line(surface, (100, 100, 100),
                             self.points[i], self.points[i+1], 2)
        for p in self.points:
            pygame.draw.circle(surface, (120, 120, 120),
                               (int(p[0]), int(p[1])), 4)

# -----------------------------
# Agent
# -----------------------------


class Agent:
    def __init__(self, x, y):
        self.position = (x, y)
        self.velocity = (2, 0)
        self.acceleration = (0, 0)
        self.max_speed = 3.5
        self.max_force = 0.1

    def follow_path(self, path):
        # STEP 1: Predict future position
        predict = vec_mul(vec_normalize(self.velocity), 50)
        predict_pos = vec_add(self.position, predict)

        # STEP 2: Find closest point on path to predicted position
        closest = self._get_closest_point_on_path(predict_pos, path.points)

        # STEP 3: Check distance from path
        distance = vec_length(vec_sub(predict_pos, closest))

        # STEP 4: If too far off, steer back to path
        if distance > path.radius:
            self.seek(closest)

    def _get_closest_point_on_path(self, predict_pos, points):
        closest_point = points[0]
        min_dist = float('inf')
        for i in range(len(points) - 1):
            a = points[i]
            b = points[i+1]
            ab = vec_sub(b, a)
            ab_len_sq = ab[0]**2 + ab[1]**2
            if ab_len_sq == 0:
                normal_point = a
            else:
                ap = vec_sub(predict_pos, a)
                t = (ap[0]*ab[0] + ap[1]*ab[1]) / ab_len_sq
                if t < 0:
                    t = 0
                elif t > 1:
                    t = 1
                normal_point = (a[0] + ab[0]*t, a[1] + ab[1]*t)
            dist = vec_length(vec_sub(predict_pos, normal_point))
            if dist < min_dist:
                min_dist = dist
                closest_point = normal_point
        return closest_point

    def seek(self, target):
        desired = vec_sub(target, self.position)
        desired = vec_normalize(desired)
        desired = vec_mul(desired, self.max_speed)
        steer = vec_sub(desired, self.velocity)
        steer = vec_limit(steer, self.max_force)
        self.acceleration = vec_add(self.acceleration, steer)

    def update(self):
        self.velocity = vec_add(self.velocity, self.acceleration)
        self.velocity = vec_limit(self.velocity, self.max_speed)
        self.position = vec_add(self.position, self.velocity)
        self.acceleration = (0, 0)
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

    def draw(self, surface):
        x, y = self.position
        if vec_length(self.velocity) == 0:
            angle = 0
        else:
            angle = math.degrees(
                math.atan2(-self.velocity[1], self.velocity[0]))
        size = 15
        pts = [
            (x + math.cos(math.radians(angle)) * size,
             y - math.sin(math.radians(angle)) * size),
            (x + math.cos(math.radians(angle + 120)) * size * 0.5,
             y - math.sin(math.radians(angle + 120)) * size * 0.5),
            (x + math.cos(math.radians(angle - 120)) * size * 0.5,
             y - math.sin(math.radians(angle - 120)) * size * 0.5)
        ]
        pygame.draw.polygon(surface, (0, 255, 0), pts)

# -----------------------------
# Main loop
# -----------------------------


def main():
    running = True
    path = Path()
    agent = Agent(150, 300)
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        agent.follow_path(path)
        agent.update()
        screen.fill((30, 30, 30))
        path.draw(screen)
        agent.draw(screen)
        font = pygame.font.SysFont("consolas", 20)
        text = font.render("Agent follows path", True, (255, 255, 255))
        screen.blit(text, (20, 20))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
