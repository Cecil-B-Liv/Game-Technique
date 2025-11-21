# ============================================================================
# snake.py
# Purpose
#   Predator agent with a five-state FSM.
#   States: PatrolAway, PatrolHome, Aggro, Harmless, Confused.
#   Aggro chases the frog. Harmless returns home after pacification.
#   Confused wanders briefly after reaching home, then resumes patrol.
# Update order
#   Evaluate transitions first, then run the behavior for the active state.
# Drawing
#   Simple circle with a tiny eye that turns toward the current velocity.
# ============================================================================

from enum import Enum, auto
import math
import random
import pygame
from pygame.math import Vector2 as V2
from settings import (
    WIDTH, HEIGHT, WHITE,
    SNAKE_RADIUS, SNAKE_SPEED, AGGRO_RANGE, DEAGGRO_RANGE
)
from steering import arrive, seek, seek_with_avoid, integrate_velocity, pursue, wander_force


class SnakeState(Enum):
    PatrolAway = auto()
    PatrolHome = auto()
    Aggro = auto()
    Harmless = auto()
    Confused = auto()


class Snake:
    def __init__(self, pos, patrol_point, rects, font):
        self.font = font

        # Motion and shape
        self.pos = V2(pos)
        self.vel = V2(1, 0)
        self.radius = SNAKE_RADIUS
        self.speed = SNAKE_SPEED

        # Home base and patrol destination
        self.home = V2(pos)
        self.patrol_point = V2(patrol_point)

        # Initial state
        self.state = SnakeState.PatrolAway

        # Obstacles for avoidance
        self.rects = rects

        # Drawing hint for head direction
        self.heading_deg = 0.0

        # Color varies by state for quick visual debug
        self.color = (190, 130, 110)

        # Confused state timer
        self.confused_timer = 0.0

        # RNG for wander if needed
        self._rng_seed = random.randint(0, 999999)

    def set_state(self, st):
        """Switch to a new FSM state."""
        self.state = st

    def compute_obstacle_avoidance(self, look_ahead_distance=80):
        """
        Compute a steering force to avoid obstacles.
        Returns a Vector2 force that pushes away from nearby obstacles.
        """
        avoidance_force = V2(0, 0)
        
        # Normalize velocity for direction checking
        if self.vel.length_squared() > 0:
            forward = self.vel.normalize()
        else:
            forward = V2(1, 0)
        
        # Check each obstacle
        for rect in self.rects:
            # Find closest point on rectangle to snake
            closest_x = max(rect.left, min(self.pos.x, rect.right))
            closest_y = max(rect.top, min(self.pos.y, rect.bottom))
            closest_point = V2(closest_x, closest_y)
            
            # Vector from closest point to snake
            to_snake = self.pos - closest_point
            distance = to_snake.length()
            
            # Only avoid if obstacle is close
            avoidance_radius = self.radius + 30  # Detection radius
            
            if distance < avoidance_radius and distance > 0:
                # Check if obstacle is roughly in front of us
                to_obstacle = closest_point - self.pos
                if to_obstacle.length_squared() > 0:
                    to_obstacle_normalized = to_obstacle.normalize()
                    # Dot product to check if obstacle is ahead
                    ahead_factor = forward.dot(to_obstacle_normalized)
                    
                    # Only avoid obstacles that are ahead (dot > -0.5)
                    if ahead_factor > -0.5:
                        # Stronger avoidance when closer
                        strength = (avoidance_radius - distance) / avoidance_radius
                        # Push away from obstacle
                        avoidance_force += to_snake.normalize() * strength * self.speed * 2
        
        return avoidance_force

    def update(self, dt, frog):
        """
        Update state transitions based on distance to frog and timers.
        Then compute a steering force for the active state and integrate motion.
        """

        # Distance to frog for transitions
        dist = (frog.pos - self.pos).length()



        # ---------------- FSM transitions ----------------
        # Aggro snake calms down when frog is far
        if self.state == SnakeState.Aggro:
            if dist > DEAGGRO_RANGE:  # range check Aggro -> PatrolHome
                self.set_state(SnakeState.PatrolHome)
        # Patrol snakes enter Aggro when frog is close
        elif self.state in (SnakeState.PatrolHome, SnakeState.PatrolAway):
            if dist < AGGRO_RANGE:  # range check Patrol -> Aggro
                self.set_state(SnakeState.Aggro)
        # Harmless snake returns home after pacification
        elif self.state == SnakeState.Harmless:
            # When harmless snake reaches home, enter Confused briefly then resume patrol
            if (self.home - self.pos).length() < 12:
                self.confused_timer = 1.5  # seconds of confusion
                self.set_state(SnakeState.Confused)
        # Confused state times out to PatrolAway
        elif self.state == SnakeState.Confused:
            self.confused_timer -= dt
            if self.confused_timer <= 0:
                self.set_state(SnakeState.PatrolAway)

        # ---------------- State behaviours ----------------
        avoidance_weight = 1.0  # tune obstacle avoidance strength for all snakes 
        if self.state == SnakeState.Aggro:
            self.color = (255, 150, 150)
            # TODO: replace seek with pursue for smarter interception
            steer = pursue(self.pos, self.vel, frog.pos, frog.vel, self.speed)
            # steer = seek(self.pos, self.vel, frog.pos, self.speed)
            # Light avoidance to reduce obstacle collisions while aggro
            steer += seek_with_avoid(self.pos, self.vel, frog.pos,
                                     self.speed, self.radius, self.rects) * avoidance_weight  # tune weight

        elif self.state == SnakeState.PatrolAway: # patrol to patrol_point
            self.color = (180, 200, 255) # blueish
            steer = arrive(self.pos, self.vel, self.patrol_point, self.speed)
            steer += seek_with_avoid(self.pos, self.vel, self.patrol_point,
                                     self.speed, self.radius, self.rects) * avoidance_weight
            if (self.patrol_point - self.pos).length() < 10:
                self.set_state(SnakeState.PatrolHome) # turn green

        elif self.state == SnakeState.PatrolHome: # patrol back to home
            self.color = (180, 220, 180) # greenish
            steer = arrive(self.pos, self.vel, self.home, self.speed)
            steer += seek_with_avoid(self.pos, self.vel, self.home,
                                     self.speed, self.radius, self.rects) * avoidance_weight
            if (self.home - self.pos).length() < 10:
                self.set_state(SnakeState.PatrolAway) # turn blue

        elif self.state == SnakeState.Harmless:
            self.color = (190, 180, 255) # purpleish
            steer = arrive(self.pos, self.vel, self.home, self.speed * 0.9)
            steer += seek_with_avoid(
                self.pos, self.vel, self.home, self.speed * 0.9, self.radius, self.rects) * avoidance_weight

        else:  # Confused
            self.color = (245, 210, 160)
            # TODO: use wander_force for a gentle random walk during confusion
            steer = wander_force(self.vel, rng_seed=self._rng_seed)
            # steer = V2()

        # ADD OBSTACLE AVOIDANCE TO ALL STATES
        obstacle_avoidance = self.compute_obstacle_avoidance()
        
        # Combine steering with obstacle avoidance
        # Higher weight means stronger avoidance
        avoidance_weight = 2.5  # Tune this value (1.0 - 5.0)
        steer += obstacle_avoidance * avoidance_weight

        # Integrate velocity and update position
        self.vel = integrate_velocity(self.vel, steer, dt, self.speed)
        self.pos += self.vel * dt

        # Smooth eye heading based on velocity
        spd = self.vel.length()
        if spd > 4:
            def lerp(a, b, t): return a + (b - a) * t
            self.heading_deg = lerp(self.heading_deg, math.degrees(
                math.atan2(self.vel.y, self.vel.x)), 0.15)

        # Keep inside arena
        if self.pos.x < self.radius:
            self.pos.x = self.radius
        if self.pos.x > WIDTH - self.radius:
            self.pos.x = WIDTH - self.radius
        if self.pos.y < self.radius:
            self.pos.y = self.radius
        if self.pos.y > HEIGHT - self.radius:
            self.pos.y = HEIGHT - self.radius

    def draw(self, surf):
        # Body
        pygame.draw.circle(surf, self.color, self.pos, self.radius)
        # Simple eye in heading direction
        head = self.pos + V2(1, 0).rotate(self.heading_deg) * (self.radius - 2)
        pygame.draw.circle(surf, (30, 30, 30), head, 3)
        pygame.draw.circle(surf, WHITE, head, 5, 1)

        txt = self.font.render(self.state.name, True, (255,255,255))
        surf.blit(txt, (self.pos.x - txt.get_width()/2, self.pos.y - self.radius-16))    
