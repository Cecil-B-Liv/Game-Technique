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
    ARRIVE_SLOW_RADIUS, ARRIVE_STOP_RADIUS, FLY_SPEED, NEIGHBOR_RADIUS,
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
    return V2(steer)

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
    return V2(steer)


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
    Typical approach
      For each neighbor inside sep_radius, add a vector pointing away with
      magnitude inversely proportional to distance. Normalize at the end.
    """
    steering_sum = (0, 0)
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        # Distance between self and other
        distance = vec_length(vec_sub(me_pos, neighbor_pos))

        # Changed perception to sep_radius here for clarity
        if 0 < distance < sep_radius:
            # Direction away from the neighbor
            diff = vec_sub(me_pos, neighbor_pos)
            diff = vec_normalize(diff)
            # Closer boids have stronger effect (1 / distance)
            diff = vec_mul(diff, 1 / distance)
            steering_sum = vec_add(steering_sum, diff)
            count += 1

    if count > 0:
        # Average the separation vectors
        steering_sum = vec_mul(steering_sum, 1.0 / count)
        # Normalize at the end for pure direction
        if vec_length(steering_sum) > 0:
            steering_sum = vec_normalize(steering_sum)
        return V2(steering_sum)

    # No close neighbors -> no separation force
    return V2(0, 0)


def boids_cohesion(me_pos, neighbors):
    """
    Pull toward the average position of neighbors.
    Typical approach
      Compute the center of mass of neighbors then steer toward that point.
    """
    center_of_mass = (0, 0)
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        center_of_mass = vec_add(center_of_mass, neighbor_pos)
        count += 1

    if count > 0:
        # Average position of neighbors
        center_of_mass = vec_mul(center_of_mass, 1 / count)
        # Direction toward center
        desired = vec_sub(center_of_mass, me_pos)
        if vec_length(desired) > 0:  # Avoid division by zero
            return V2(vec_normalize(desired))

    return V2(0, 0)


def boids_alignment(me_vel, neighbors):
    """
    Match the average velocity of neighbors.
    Typical approach
      Compute the average heading of neighbors then steer toward that heading.
    """
    avg_velocity = (0, 0)
    count = 0

    for neighbor_pos, neighbor_vel in neighbors:
        avg_velocity = vec_add(avg_velocity, neighbor_vel)
        count += 1

    if count > 0:
        # Average the neighbor velocities
        avg_velocity = vec_mul(avg_velocity, 1 / count)
        # Direction to match average heading
        steer = vec_sub(avg_velocity, me_vel)
        if vec_length(steer) > 0:
            return V2(vec_normalize(steer))

    return V2(0, 0)

# ---------------- Obstacle avoidance blend ----------------


def seek_with_avoid(pos, vel, target, max_speed, radius, rects, lookahead=AVOID_LOOKAHEAD):
    """
    Seek the target but avoid obstacles by sampling angled corridors.
    Idea
      1. Check a straight corridor first
      2. If blocked, rotate small angles left and right until a free path is found
      3. Use that direction for the seek
      4. If all blocked, apply a small braking force
    Use circlecast_hits_any_rect(p0, p1, radius, rects, step=6.0) to test each corridor.
    """
    # Direction to target
    to_target = vec_sub(target, pos)
    distance_to_target = vec_length(to_target)

    if distance_to_target == 0:
        return V2(0, 0)

    direction = vec_normalize(to_target)

    # --- 1. Try straight path first ---
    end_pos = vec_add(pos, vec_mul(direction, lookahead))

    if not circlecast_hits_any_rect(pos, end_pos, radius, rects):
        # Path is clear! Use normal seek
        return V2(seek(pos, vel, target, max_speed))

    # --- 2. Path blocked, try angled corridors ---
    angle = 0

    while angle <= AVOID_MAX_ANGLE:
        # Try both left and right at this angle
        for sign in [1, -1]:  # +angle (left), -angle (right)
            test_angle = angle * sign

            # Rotate direction by test_angle
            angle_rad = math.radians(test_angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Rotate the direction vector
            rotated_x = direction[0] * cos_a - direction[1] * sin_a
            rotated_y = direction[0] * sin_a + direction[1] * cos_a
            rotated_dir = (rotated_x, rotated_y)

            # Test this corridor
            test_end = vec_add(pos, vec_mul(rotated_dir, lookahead))

            if not circlecast_hits_any_rect(pos, test_end, radius, rects):
                # Found a clear path! Seek in this direction
                temp_target = vec_add(pos, vec_mul(rotated_dir, lookahead * 2))
                return V2(seek(pos, vel, temp_target, max_speed))

        # Increment angle and try again
        angle += AVOID_ANGLE_INCREMENT

    # --- 3. All paths blocked, apply braking ---
    # Return force opposite to velocity to slow down
    if vec_length(vel) > 0:
        brake = vec_normalize(vel)
        brake = vec_mul(brake, -max_speed * 0.3)  # Gentle brake
        return V2(brake)

    return V2(0, 0)


# ---------------- New behaviours to be implemented ----------------


def pursue(pos, vel, target_pos, target_vel, max_speed):
    """
    Predict the future position of the target then seek that point.
    Suggested
      distance = |target_pos - pos|
      time_horizon = distance / (max_speed + small_eps) ?? whats small eps??
      predicted    = target_pos + target_vel * time_horizon
      return seek toward predicted
    Replace simple seek in Snake Aggro with pursue for better interception.
    """
    # Step 1: Get distance to target's CURRENT position
    to_target = vec_sub(target_pos, pos)
    distance = vec_length(to_target)

    # Step 2: Estimate how long it will take to reach the target
    speed = vec_length(vel) if vec_length(vel) > 0 else max_speed
    prediction_time = distance/speed  # velocity based

    # Step 3: Predict where target will be in the future
    # Formula: future_pos = current_pos + (velocity × time)
    future_position = vec_add(
        target_pos,
        vec_mul(target_vel, prediction_time*0.5)  # tune factor
    )

    # Step 4: Calculate desired velocity toward PREDICTED position
    desired = vec_sub(future_position, pos)
    desired = vec_normalize(desired)
    desired = vec_mul(desired, max_speed)

    # Step 5: Calculate steering force (Reynolds steering formula)
    steer = vec_sub(desired, vel)
    # No limit needed here as wander is meant to be small
    return steer


def evade(pos, vel, threat_pos, threat_vel, max_speed):
    """
    Predict the future position of a threat then flee from that point.
    This is the inverse of pursue. Use the same prediction idea.
    """
    # raise NotImplementedError("Implement evade as inverse of pursue")
    to_pursuer = vec_sub(threat_pos, pos)
    distance = vec_length(to_pursuer)
    speed = vec_length(vel) if vec_length(vel) > 0 else max_speed
    prediction_time = distance/speed
    future_position = vec_add(threat_pos, vec_mul(
        threat_vel, prediction_time*0.5))
    desired = vec_sub(pos, future_position)
    desired = vec_normalize(desired)
    desired = vec_mul(desired, max_speed)
    steer = vec_sub(desired, vel)
    return steer


def wander_force(me_vel, jitter_deg=12.0, circle_distance=24.0, circle_radius=18.0, rng_seed=None):
    """
    Return a small random steering vector for gentle drift.
    Classic wander
      Project a small circle ahead along current heading, then jitter the
      target point on that circle by a tiny random angle each update.
    Use this for Fly Idle and Snake Confused.
    """
    # STEP 1: Randomly adjust the wander angle (random jitter between -jitter and +jitter)
    wander_angle = random.uniform(-jitter_deg,
                                   jitter_deg)

    # STEP 2: Calculate circle center position ahead of the agent (in the direction of velocity)
    circle_center = vec_mul(vec_normalize(
        me_vel), circle_distance)

    # STEP 3: Calculate displacement on circle edge
    displacement = (
        math.cos(wander_angle) * circle_radius,
        math.sin(wander_angle) * circle_radius
    )

    # STEP 4: Combine center + displacement = target point
    wander_force = vec_add(circle_center, displacement)

    # No limit needed here as wander is meant to be small
    return V2(wander_force)
