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
import random
from pygame.math import Vector2 as V2
from utils import limit, circlecast_hits_any_rect
from settings import (
    ARRIVE_SLOW_RADIUS, ARRIVE_STOP_RADIUS, FLY_SPEED, FPS, FROG_SPEED, NEIGHBOR_RADIUS,
    AVOID_LOOKAHEAD, AVOID_ANGLE_INCREMENT, AVOID_MAX_ANGLE, SNAKE_SPEED
)

# -----------------------------
# Vector helper functions
# -----------------------------
# These operate on 2D vectors represented as (x, y) tuples.
# Get from the lab code btw


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


def rotate_vector(vec, angle_deg):
    """
    Rotate a 2D vector by angle_deg degrees (counterclockwise).
    Positive angle = left rotation
    Negative angle = right rotation
    """
    import math
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    x, y = vec
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a

    return (new_x, new_y)

# ---------------- Base behaviours ----------------


def seek(pos, vel, target, max_speed):
    """
    Move toward a target. Returns a steering force.
    desired = direction_to_target * max_speed
    steering = desired - current_velocity
    """
    # desired = vec_sub(target, pos)
    # desired = vec_normalize(desired)
    # desired = vec_mul(desired, max_speed)
    # steer = vec_sub(desired, vel)
    # steer = vec_limit(steer, max_speed)
    # return V2(steer)

    d = target - pos
    if d.length_squared() == 0:
        return V2()
    desired = d.normalize() * max_speed
    return desired - vel


def flee(pos, vel, target, max_speed):
    """
    Move away from a target. This is the opposite of seek.
    You need to implement the mirror of seek using direction from threat to self.
    """
    away = vec_sub(pos, target)
    distance = vec_length(away)
    away = vec_normalize(away)

    # Increase flee speed when very close to threat
    panic_radius = 200.0  # can be tuned
    if distance < panic_radius:
        intensity = panic_radius / distance
        intensity = min(intensity, 3.0)  # Cap at 3x speed
    else:
        intensity = 1.0  # Normal flee speed when far

    desired = vec_mul(away, max_speed * intensity)
    steer = vec_sub(desired, vel)

    return V2(steer)


def arrive(pos, vel, target, max_speed, slow_radius=ARRIVE_SLOW_RADIUS, stop_radius=ARRIVE_STOP_RADIUS):
    """
    Like seek when far, but slow down near the target.
    Rules
      If distance < stop_radius, return a force that cancels leftover velocity
      If distance < slow_radius, scale desired speed by distance / slow_radius
      Otherwise use full speed
    This should remove overshoot and jitter around the target.
    """
    desired = target - pos
    distance = desired.length()

    if distance == 0:
        return V2(0, 0)

    # Normalize direction
    desired = desired.normalize()

    # Scale speed based on distance (check stop_radius FIRST!)
    if distance < stop_radius:
        # Apply strong braking
        braking_force = -vel * 5
        return braking_force
    elif distance < slow_radius:
        # Slowing zone - scale speed proportionally
        scaled_speed = max_speed * (distance / slow_radius)
    else:
        # Far away - full speed
        scaled_speed = max_speed

    desired_vec = desired.normalize() * scaled_speed
    # Steering force
    steer = desired_vec - vel
    return V2(steer)


def integrate_velocity(vel, force, dt, max_speed):
    """
    Apply a steering force to velocity using Euler integration.
    Then clamp to max speed and return the new velocity.
    Use this inside agent update methods after computing steering forces.
    """
    # Handle integration and speed clamping
    # Handle speed limit after applying force
    # return the new velocity
    vel += limit(force, 500.0) * dt
    if vel.length() > max_speed:
        vel.scale_to_length(max_speed)
    return vel

# ---------------- Boids components ----------------
# TASK B- Boids Flocking

# Note: No need to handle self check and handle neighbor radius here.
# The caller (Fly update) already does that.


def boids_separation(me_pos, neighbors, sep_radius):
    """
    Push away from neighbors that are too close.
    neighbors: list of tuples (neighbor_pos, neighbor_vel)
    Typical approach:
      For each neighbor inside sep_radius, add a vector pointing away with
      magnitude inversely proportional to distance. Normalize at the end.
    """
    steering_sum = V2()
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        # Distance between self and other
        diff = me_pos - neighbor_pos
        distance = diff.length()

        # Changed perception to sep_radius here for clarity
        if 0 < distance < sep_radius:
            # Direction away from the neighbor
            steering_sum += diff.normalize() / distance
            count += 1

    if count > 0:
        # Average the separation vectors
        steering_sum /= count
        # Return the force vector (with magnitude)
        return steering_sum.normalize() * FLY_SPEED * 1.5

    # No close neighbors -> no separation force
    return steering_sum*1.5*FLY_SPEED


def boids_cohesion(me_pos, neighbors):
    """
    Pull toward the average position of neighbors.
    Typical approach:
      Compute the center of mass of neighbors then steer toward that point.
    """
    center_of_mass = V2()
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        center_of_mass += neighbor_pos
        count += 1

    if count > 0:
        # Average position of neighbors
        center_of_mass /= count
        desired = center_of_mass - me_pos  # Point toward center
        # Return the force vector (with magnitude based on distance)
        return desired.normalize()*FLY_SPEED

    return center_of_mass*FLY_SPEED


def boids_alignment(me_vel, neighbors):
    """
    Match the average velocity of neighbors.
    Typical approach:
      Compute the average heading of neighbors then steer toward that heading.
    """
    avg_velocity = V2()
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        avg_velocity += neighbor_vel
        count += 1

    if count > 0:
        # Average the neighbor velocities
        avg_velocity /= count
        # Steering force to match average velocity
        steer = avg_velocity - me_vel
        # Return the steering force (with magnitude)
        return steer.normalize() * FLY_SPEED

    return avg_velocity*FLY_SPEED


# ---------------- Obstacle avoidance blend ----------------

# seek with_avoid function updated with adaptive lookahead
def seek_with_avoid(pos, vel, target, max_speed, radius, rects, lookahead=AVOID_LOOKAHEAD):
    """
    Seek the target but avoid obstacles by sampling angled corridors.
    Enhanced to prevent getting stuck by checking multiple angles simultaneously
    and choosing the best direction that balances reaching target and avoiding obstacles.
    """
    # Calculate the desired direction toward target
    desired_dir = vec_sub(target, pos)
    distance_to_target = vec_length(desired_dir)

    if distance_to_target < 0.01:
        return V2(0, 0)

    desired_dir = vec_normalize(desired_dir)

    # Adjust lookahead based on current speed (faster = longer lookahead)
    lookahead_point = vec_add(pos, vec_mul(desired_dir, lookahead))

    if not circlecast_hits_any_rect(pos, lookahead_point, radius, rects, step=6.0):
        # Clear path - go straight
        desired = vec_mul(desired_dir, max_speed)
        steer = vec_sub(desired, vel)
        return V2(steer)

    # Obstacle ahead - test angled paths
    max_angle = AVOID_MAX_ANGLE
    angle_step = AVOID_ANGLE_INCREMENT

    for angle_deg in range(int(angle_step), int(max_angle) + 1, int(angle_step)):
        # Try left
        left_dir = rotate_vector(desired_dir, angle_deg)
        left_point = vec_add(pos, vec_mul(left_dir, lookahead))

        if not circlecast_hits_any_rect(pos, left_point, radius, rects, step=6.0):
            desired = vec_mul(left_dir, max_speed)
            steer = vec_sub(desired, vel)
            return V2(steer)

        # Try right
        right_dir = rotate_vector(desired_dir, -angle_deg)
        right_point = vec_add(pos, vec_mul(right_dir, lookahead))

        if not circlecast_hits_any_rect(pos, right_point, radius, rects, step=6.0):
            desired = vec_mul(right_dir, max_speed)
            steer = vec_sub(desired, vel)
            return V2(steer)

    # All paths blocked - brake
    brake = vec_mul(vel, -1.0)
    return V2(brake)

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
    # Get distance to target's current position
    to_target = vec_sub(target_pos, pos)
    distance = vec_length(to_target)

    if distance < 0.01:
        return V2(0, 0)

    # Use max_speed for consistent prediction
    small_eps = 0.001
    prediction_time = distance / (max_speed + small_eps)

    # Predict future position
    future_position = vec_add(target_pos, vec_mul(target_vel, prediction_time))

    # Calculate desired velocity toward PREDICTED position
    desired = vec_sub(future_position, pos)
    desired = vec_normalize(desired)
    desired = vec_mul(desired, max_speed)

    # Calculate steering force (Reynolds steering formula)
    steer = vec_sub(desired, vel)
    return V2(steer)


def evade(pos, vel, threat_pos, threat_vel, max_speed):
    """
    Predict the future position of a threat then flee from that point.
    This is the inverse of pursue. Use the same prediction idea.
    """
    to_threat = vec_sub(threat_pos, pos)
    distance = vec_length(to_threat)

    if distance < 0.01:
        # Too close - flee in any direction
        return V2(-vel[0], -vel[1]) if vec_length(vel) > 0 else V2(1, 0) * max_speed

    # Use max_speed for consistent prediction
    small_eps = 0.001
    prediction_time = distance / (max_speed + small_eps)

    # Predict future position
    future_position = threat_pos + (threat_vel * prediction_time)

    # Flee from prediction
    away = pos - future_position

    # Optional panic scaling
    panic_radius = 200.0
    if distance < panic_radius:
        intensity = panic_radius / distance
        intensity = min(intensity, 3.0)
    else:
        intensity = 1.0

    desired = away.normalize()
    desired = desired * max_speed * intensity

    steer = desired - vel
    return V2(steer)

def wander_force(me_vel, jitter_deg=12.0, circle_distance=24.0, circle_radius=18.0, rng_seed=None):
    """
    Return a small random steering vector for gentle drift.
    Classic wander
      Project a small circle ahead along current heading, then jitter the
      target point on that circle by a tiny random angle each update.
    Use this for Fly Idle and Snake Confused.
    """
    # Randomly adjust the wander angle (random jitter between -jitter and +jitter)
    wander_angle = random.uniform(-jitter_deg,
                                  jitter_deg)

    # Calculate circle center position ahead of the agent (in the direction of velocity)
    circle_center = vec_mul(vec_normalize(
        me_vel), circle_distance)

    # Calculate displacement on circle edge
    displacement = (
        math.cos(wander_angle) * circle_radius,
        math.sin(wander_angle) * circle_radius
    )

    # Combine center + displacement = target point
    wander_force = vec_add(circle_center, displacement)

    # No limit needed here as wander is meant to be small
    return V2(wander_force) * 150
