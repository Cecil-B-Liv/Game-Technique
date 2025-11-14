# ============================================================================
# steering.py
# Purpose
#   Implement all steering behaviours here. Each function computes a steering
#   force vector. Entities apply that force to their velocity each frame.
# Key idea
#   desired_velocity minus current_velocity gives the steering force.
#   Use dt in update loops when integrating velocity to keep motion consistent.
# ============================================================================

import math
from pygame.math import Vector2 as V2
from utils import limit, circlecast_hits_any_rect
from settings import (
    ARRIVE_SLOW_RADIUS, ARRIVE_STOP_RADIUS,
    AVOID_LOOKAHEAD, AVOID_ANGLE_INCREMENT, AVOID_MAX_ANGLE
)

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

# ---------------- Base behaviours ----------------

def seek(pos, vel, target, max_speed):
    """
    Move toward a target. Returns a steering force.
    desired = direction_to_target * max_speed
    steering = desired - current_velocity
    """

    desired = vec_sub(target, pos)
    desired = vec_normalize(desired)
    desired = vec_mul(desired, max_speed)
    steer = vec_sub(desired, vel)
    steer = vec_limit(steer, max_speed)
    return steer

    # d = target - pos
    # if d.length_squared() == 0:
    #     return V2()
    # desired = d.normalize() * max_speed
    # return desired - vel

# TASK C- Flee behaviour


def flee(pos, vel, target, max_speed):
    """
    Move away from a target. This is the opposite of seek.
    You need to implement the mirror of seek using direction from threat to self.
    """
    # raise NotImplementedError("Implement flee using the opposite of seek")

    desired = vec_sub(pos, target)
    desired = vec_normalize(desired)
    desired = vec_mul(desired, max_speed)
    steer = vec_sub(desired, vel)
    steer = vec_limit(steer, max_speed)
    return steer


# TASK A- Arrival behaviour
def arrive(pos, vel, target, max_speed, slow_radius=ARRIVE_SLOW_RADIUS, stop_radius=ARRIVE_STOP_RADIUS):
    """
    Like seek when far, but slow down near the target.
    Rules
      If distance < stop_radius, return a force that cancels leftover velocity
      If distance < slow_radius, scale desired speed by distance / slow_radius
      Otherwise use full speed
    This should remove overshoot and jitter around the target.
    """
    # raise NotImplementedError("Implement arrive with slow and stop radii")
    desired = vec_sub(target, pos)
    distance = vec_length(desired)
    if distance < 0.5:
        vel = (0, 0)
        return V2(0, 0)  # need to return something to stop
    desired = vec_normalize(desired)
    if distance < slow_radius:
        scaled_speed = max_speed * (distance / slow_radius)
    else:
        scaled_speed = max_speed
    desired = vec_mul(desired, scaled_speed)
    steer = vec_sub(desired, vel)
    steer = vec_limit(steer, max_speed)
    return steer


def integrate_velocity(vel, force, dt, max_speed):
    """
    Apply a steering force to velocity using Euler integration.
    Then clamp to max speed and return the new velocity.
    Use this inside agent update methods after computing steering forces.
    """
    vel += limit(force, 500.0) * dt
    if vel.length() > max_speed:
        vel.scale_to_length(max_speed)
    return vel

# ---------------- Boids components ----------------
# TASK B- Boids Flocking


def boids_separation(me_pos, neighbors, sep_radius):
    """
    Push away from neighbors that are too close.
    neighbors: list of tuples (neighbor_pos, neighbor_vel)
    Typical approach
      For each neighbor inside sep_radius, add a vector pointing away with
      magnitude inversely proportional to distance. Normalize at the end.
    """
    # raise NotImplementedError("Implement boids separation")
    steering_sum = (0, 0)
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        # Distance between self and other
        distance = vec_length(vec_sub(me_pos, neighbor_pos))

        # Only consider boids that are within half the perception distance
        if 0 < distance < sep_radius:
            # Direction away from the neighbor
            diff = vec_sub(me_pos, neighbor_pos)
            diff = vec_normalize(diff)
            # Closer boids have stronger effect (1 / distance)
            diff = vec_mul(diff, 1 / distance)
            steering_sum = vec_add(steering_sum, diff)
            count += 1

    if count > 0:
        # Average steering direction
        steering_sum = vec_mul(steering_sum, 1 / count)
        # Turn this into a desired velocity
        steering_sum = vec_normalize(steering_sum)
        return steering_sum

    # No close neighbors -> no separation force
    return (0, 0)


def boids_cohesion(me_pos, neighbors):
    """
    Pull toward the average position of neighbors.
    Typical approach
      Compute the center of mass of neighbors then steer toward that point.
    """
    # raise NotImplementedError("Implement boids cohesion")
    center_of_mass = (0, 0)
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        distance = vec_length(vec_sub(me_pos, neighbor_pos))
        # Consider neighbors within perception radius
        if distance < self.perception:    
            center_of_mass = vec_add(center_of_mass, neighbor_pos)
            count += 1

    if count > 0:
        # Average position of neighbors
        center_of_mass = vec_mul(center_of_mass, 1 / count)

        # Use seek to move toward this center point
        return seek(center_of_mass)

    return (0, 0)


def boids_alignment(me_vel, neighbors):
    """
    Match the average velocity of neighbors.
    Typical approach
      Compute the average heading of neighbors then steer toward that heading.
    """
    # raise NotImplementedError("Implement boids alignment")
    avg_velocity = (0, 0)
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        # if other is self:
        #     continue
        # distance = vec_length(vec_sub(me_pos, other.position))
        # Consider neighbors within perception radius
        # if distance < self.perception:
        avg_velocity = vec_add(avg_velocity, other.position)
        count += 1

    if count > 0:
        # Average the neighbor velocities
        avg_velocity = vec_mul(avg_velocity, 1 / count)

        # # Turn into desired velocity
        # desired = vec_normalize(steering_sum )
        # desired = vec_mul(desired, self.max_speed)

        # # Steering force to adjust current velocity toward desired
        # steer = vec_sub(desired, self.velocity)
        # steer = vec_limit(steer, self.max_force)
        steer = vec_sub(avg_velocity, me_vel)
        steer = vec_normalize(steer)
        return steer

    return (0, 0)

# ---------------- Obstacle avoidance blend ----------------

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

def seek_with_avoid(pos, vel, target, max_speed, radius, rects, lookahead=AVOID_LOOKAHEAD):
    """
    Seek the target but avoid obstacles by sampling angled corridors.
    Idea
      1. Check a straight corridor first
      2. If blocked, rotate small angles left and right until a free path is found
      3. Use that direction for the seek
      4. If all blocked, apply a small braking force
    Use circlecast_hits_any_rect to test each corridor.
    """
    # raise NotImplementedError(
    #     "Implement angled corridor search with circle casts")
    avoid = avoid_obstacles(rects)


# ---------------- New behaviours to be implemented ----------------


def pursue(pos, vel, target_pos, target_vel, max_speed):
    """
    Predict the future position of the target then seek that point.
    Suggested
      distance = |target_pos - pos|
      time_horizon = distance / (max_speed + small_eps)
      predicted    = target_pos + target_vel * time_horizon
      return seek toward predicted
    Replace simple seek in Snake Aggro with pursue for better interception.
    """
    raise NotImplementedError("Implement pursue with prediction")


def evade(pos, vel, threat_pos, threat_vel, max_speed):
    """
    Predict the future position of a threat then flee from that point.
    This is the inverse of pursue. Use the same prediction idea.
    """
    raise NotImplementedError("Implement evade as inverse of pursue")


def wander_force(me_vel, jitter_deg=12.0, circle_distance=24.0, circle_radius=18.0, rng_seed=None):
    """
    Return a small random steering vector for gentle drift.
    Classic wander
      Project a small circle ahead along current heading, then jitter the
      target point on that circle by a tiny random angle each update.
    Use this for Fly Idle and Snake Confused.
    """
    raise NotImplementedError("Implement wander_force")
