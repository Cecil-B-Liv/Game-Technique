# =====================================================================
# pursuit_behavior.py
# Lab 4: Pursuit Behavior
# Course: Games and AI Techniques
# =====================================================================
# Goal:
#   Show how an agent can chase a moving target by predicting its future
#   position instead of just following its current location.
# =====================================================================

import pygame
import math
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behavior: PURSUIT")
clock = pygame.time.Clock()

# -----------------------------
# Vector helpers
# -----------------------------


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

# -----------------------------
# Target class
# -----------------------------


class Target:
    def __init__(self, x, y):
        self.position = (x, y)
        self.velocity = (5, 5)
        self.radius = 8

    def update(self):
        self.position = vec_add(self.position, self.velocity)
        x, y = self.position
        if x < self.radius or x > WIDTH-self.radius:
            self.velocity = (-self.velocity[0], self.velocity[1])
        if y < self.radius or y > HEIGHT-self.radius:
            self.velocity = (self.velocity[0], -self.velocity[1])

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 60, 60), (int(
            self.position[0]), int(self.position[1])), self.radius)

# -----------------------------
# Agent class
# -----------------------------


class Agent:
    def __init__(self, x, y):
        self.position = (x, y)
        self.velocity = (0, 0)
        self.acceleration = (0, 0)
        self.max_speed = 4.0
        self.max_force = 0.1

    def pursue(self, target):
        # Step 1: Calculate vector from agent to target's CURRENT position
        to_target = vec_sub(target.position, self.position)
        distance = vec_length(to_target)

        # Step 2: Estimate how long it will take to reach the target
        speed = vec_length(self.velocity) if vec_length(
            self.velocity) > 0 else self.max_speed
        # avoid division by zero
        prediction_time = distance/speed  # velocity based

        # Step 3: PREDICT where target will be in the future
        # Formula: future_pos = current_pos + (velocity × time)
        future_position = vec_add(
            target.position,
            vec_mul(target.velocity, prediction_time*0.5)  # tune factor
        )

        # Step 4: Calculate desired velocity toward PREDICTED position
        desired = vec_sub(future_position, self.position)
        desired = vec_normalize(desired)
        desired = vec_mul(desired, self.max_speed)

        # Step 5: Calculate steering force (Reynolds steering formula)
        steer = vec_sub(desired, self.velocity)
        steer = vec_limit(steer, self.max_force)

        # Step 6: Apply steering force as acceleration
        self.acceleration = steer

    def update(self):
        self.velocity = vec_add(self.velocity, self.acceleration)
        self.velocity = vec_limit(self.velocity, self.max_speed)
        self.position = vec_add(self.position, self.velocity)
        self.acceleration = (0, 0)

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

# -----------------------------
# Main loop
# -----------------------------


def main():
    running = True
    target = Target(WIDTH//3, HEIGHT//2)
    agent = Agent(WIDTH*0.8, HEIGHT//2)
    while running:
        dt = clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        target.update()
        agent.pursue(target)
        agent.update()
        screen.fill((30, 30, 30))
        target.draw(screen)
        agent.draw(screen)
        pygame.draw.line(screen, (100, 100, 255), (int(agent.position[0]), int(
            agent.position[1])), (int(target.position[0]), int(target.position[1])), 1)
        font = pygame.font.SysFont("consolas", 20)
        text = font.render("Agent pursues moving target",
                           True, (255, 255, 255))
        screen.blit(text, (20, 20))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
