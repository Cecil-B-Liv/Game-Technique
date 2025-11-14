# =====================================================================
# wander_behavior.py
# Lab 6: Wander Behavior
# Course: Games and AI Techniques
# =====================================================================
# Goal:
#   Create natural, random wandering movement by gently changing
#   direction each frame using a projected "wander circle."
# =====================================================================

import pygame
import math
import random
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behavior: WANDER")
clock = pygame.time.Clock()


def vec_length(v): return math.sqrt(v[0]**2 + v[1]**2)


def vec_normalize(v):
    l = vec_length(v)
    if l == 0:
        return (0, 0)
    return (v[0]/l, v[1]/l)


def vec_sub(a, b): return (a[0]-b[0], a[1]-b[1])
def vec_add(a, b): return (a[0]+b[0], a[1]+b[1])
def vec_mul(v, s): return (v[0]*s, v[1]*s)


def vec_limit(v, maxv):
    l = vec_length(v)
    if l > maxv:
        v = vec_normalize(v)
        return (v[0]*maxv, v[1]*maxv)
    return v


class Agent:
    def __init__(self, x, y):
        self.position = (x, y)
        self.velocity = (2, 0)
        self.acceleration = (0, 0)
        self.max_speed = 8
        self.max_force = 0.1
        self.wander_radius = 20    # Size of the wander circle
        self.wander_distance = 40   # How far ahead to project the circle
        # How much randomness per frame (in radians)
        self.wander_jitter = 1
        self.wander_angle = 0.0        # Current angle on the circle

    def wander(self):
        # STEP 1: Randomly adjust the wander angle (random jitter between -jitter and +jitter)
        self.wander_angle += random.uniform(-self.wander_jitter,
                                            self.wander_jitter)

        # STEP 2: Calculate circle center position ahead of the agent (in the direction of velocity)
        circle_center = vec_mul(vec_normalize(
            self.velocity), self.wander_distance)

        # STEP 3: Calculate displacement on circle edge
        displacement = (
            math.cos(self.wander_angle) * self.wander_radius,
            math.sin(self.wander_angle) * self.wander_radius
        )

        # STEP 4: Combine center + displacement = target point
        wander_force = vec_add(circle_center, displacement)

        # STEP 5: Limit the steering force
        steer = vec_limit(wander_force, self.max_force)

        # STEP 6: Apply to acceleration
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
            (x+math.cos(math.radians(angle))*size,
             y-math.sin(math.radians(angle))*size),
            (x+math.cos(math.radians(angle+120))*size*0.5,
             y-math.sin(math.radians(angle+120))*size*0.5),
            (x+math.cos(math.radians(angle-120))*size*0.5,
             y-math.sin(math.radians(angle-120))*size*0.5)
        ]
        pygame.draw.polygon(surface, (0, 255, 0), pts)


def main():
    running = True
    agent = Agent(WIDTH//2, HEIGHT//2)
    while running:
        dt = clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        agent.wander()
        agent.update()
        screen.fill((30, 30, 30))
        agent.draw(screen)
        font = pygame.font.SysFont("consolas", 20)
        text = font.render("Agent wanders randomly", True, (255, 255, 255))
        screen.blit(text, (20, 20))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
