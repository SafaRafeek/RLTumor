# import numpy as np
# import gymnasium as gym
# from gymnasium import spaces


# # ============================================================
# # HELPER FUNCTIONS
# # ============================================================

# def wrap_angle(angle):
#     """Wrap angle to [-pi, pi]."""
#     return (angle + np.pi) % (2 * np.pi) - np.pi


# # ============================================================
# # MICROSWIMMER ENVIRONMENT
# # ============================================================

# class MicroSwimmerEnv(gym.Env):

#     metadata = {"render_modes": ["human"]}

#     def __init__(
#         self,
#         tumor_radius=8.0,
#         n_obstacles=18,
#         obstacle_radius_range=(0.5, 1.0),
#         goal_radius=0.45,
#         max_steps=500,
#         seed=None,
#         fixed_obstacles=None,
#     ):
#         super().__init__()

#         # ----------------------------------------------------
#         # WORLD SETTINGS
#         # ----------------------------------------------------
#         self.tumor_radius = tumor_radius
#         self.goal_radius = goal_radius
#         self.max_steps = max_steps

#         # ----------------------------------------------------
#         # PHYSICS
#         # ----------------------------------------------------
#         self.dt = 0.08

#         self.drag = 0.15
#         self.max_speed = 1.5

#         self.max_acceleration = 1.2
#         self.max_turn_rate = 3.0

#         # ----------------------------------------------------
#         # OBSTACLES
#         # ----------------------------------------------------
#         self.n_obstacles = n_obstacles
#         self.obstacle_radius_range = obstacle_radius_range

#         # ----------------------------------------------------
#         # RNG
#         # ----------------------------------------------------
#         self.rng = np.random.default_rng(seed)

#         # ----------------------------------------------------
#         # ACTION SPACE
#         # [acceleration, steering]
#         # ----------------------------------------------------
#         self.action_space = spaces.Box(
#             low=np.array([-1.0, -1.0], dtype=np.float32),
#             high=np.array([1.0, 1.0], dtype=np.float32),
#             dtype=np.float32,
#         )

#         # ----------------------------------------------------
#         # OBSERVATION SPACE
#         # ----------------------------------------------------
#         obs_high = np.array([
#             tumor_radius,
#             tumor_radius,
#             self.max_speed,
#             self.max_speed,
#             np.pi,
#             tumor_radius,
#         ], dtype=np.float32)

#         self.observation_space = spaces.Box(
#             low=-obs_high,
#             high=obs_high,
#             dtype=np.float32,
#         )

#         # ----------------------------------------------------
#         # TARGET
#         # ----------------------------------------------------
#         self.goal = np.array([0.0, 0.0], dtype=np.float32)

#         # ----------------------------------------------------
#         # OBSTACLES
#         # ----------------------------------------------------
#         if fixed_obstacles is not None:
#             self.obstacles = fixed_obstacles
#         else:
#             self.obstacles = self.generate_obstacles()

#         # ----------------------------------------------------
#         # STATE
#         # ----------------------------------------------------
#         self.position = np.zeros(2, dtype=np.float32)
#         self.velocity = np.zeros(2, dtype=np.float32)
#         self.heading = 0.0

#         self.current_step = 0

#     # ========================================================
#     # GENERATE OBSTACLES
#     # ========================================================

#     def generate_obstacles(self):

#         obstacles = []

#         attempts = 0
#         max_attempts = 5000

#         while len(obstacles) < self.n_obstacles and attempts < max_attempts:

#             attempts += 1

#             r = self.rng.uniform(*self.obstacle_radius_range)

#             theta = self.rng.uniform(0, 2 * np.pi)
#             radial_distance = self.rng.uniform(
#                 1.5,
#                 self.tumor_radius - r - 0.5
#             )

#             x = radial_distance * np.cos(theta)
#             y = radial_distance * np.sin(theta)

#             center = np.array([x, y])

#             # ------------------------------------------------
#             # TARGET OVERLAP CHECK
#             # ------------------------------------------------
#             target_distance = np.linalg.norm(center - self.goal)

#             if target_distance < (r + self.goal_radius + 0.6):
#                 continue

#             # ------------------------------------------------
#             # OBSTACLE OVERLAP CHECK
#             # ------------------------------------------------
#             valid = True

#             for obstacle in obstacles:

#                 other_center = obstacle["center"]
#                 other_radius = obstacle["radius"]

#                 distance = np.linalg.norm(center - other_center)

#                 if distance < (r + other_radius + 0.25):
#                     valid = False
#                     break

#             if valid:
#                 obstacles.append({
#                     "center": center,
#                     "radius": r,
#                 })

#         return obstacles

#     # ========================================================
#     # RESET
#     # ========================================================

#     def reset(self, seed=None, options=None):

#         super().reset(seed=seed)

#         self.current_step = 0

#         theta = self.rng.uniform(0, 2 * np.pi)

#         self.position = np.array([
#             self.tumor_radius * np.cos(theta),
#             self.tumor_radius * np.sin(theta),
#         ], dtype=np.float32)

#         direction = self.goal - self.position

#         self.heading = np.arctan2(direction[1], direction[0])

#         self.velocity = np.zeros(2, dtype=np.float32)

#         observation = self._get_obs()

#         info = {}

#         return observation, info

#     # ========================================================
#     # OBSERVATION
#     # ========================================================

#     def _get_obs(self):

#         distance_to_goal = np.linalg.norm(self.goal - self.position)

#         return np.array([
#             self.position[0],
#             self.position[1],
#             self.velocity[0],
#             self.velocity[1],
#             self.heading,
#             distance_to_goal,
#         ], dtype=np.float32)

#     # ========================================================
#     # COLLISION
#     # ========================================================

#     def check_collision(self):

#         for obstacle in self.obstacles:

#             center = obstacle["center"]
#             radius = obstacle["radius"]

#             distance = np.linalg.norm(self.position - center)

#             if distance <= radius:
#                 return True

#         return False

#     # ========================================================
#     # STEP
#     # ========================================================

#     def step(self, action):

#         self.current_step += 1

#         # ----------------------------------------------------
#         # ACTIONS
#         # ----------------------------------------------------
#         acceleration_command = float(action[0])
#         steering_command = float(action[1])

#         acceleration = acceleration_command * self.max_acceleration
#         angular_velocity = steering_command * self.max_turn_rate

#         # ----------------------------------------------------
#         # UPDATE HEADING
#         # ----------------------------------------------------
#         self.heading += angular_velocity * self.dt
#         self.heading = wrap_angle(self.heading)

#         # ----------------------------------------------------
#         # PROPULSION
#         # ----------------------------------------------------
#         forward_vector = np.array([
#             np.cos(self.heading),
#             np.sin(self.heading),
#         ])

#         self.velocity += forward_vector * acceleration * self.dt

#         # ----------------------------------------------------
#         # DRAG
#         # ----------------------------------------------------
#         self.velocity *= (1.0 - self.drag * self.dt)

#         # ----------------------------------------------------
#         # SPEED LIMIT
#         # ----------------------------------------------------
#         speed = np.linalg.norm(self.velocity)

#         if speed > self.max_speed:
#             self.velocity = (self.velocity / speed) * self.max_speed

#         # ----------------------------------------------------
#         # UPDATE POSITION
#         # ----------------------------------------------------
#         previous_distance = np.linalg.norm(self.goal - self.position)

#         self.position += self.velocity * self.dt

#         current_distance = np.linalg.norm(self.goal - self.position)

#         # ----------------------------------------------------
#         # REWARD
#         # ----------------------------------------------------
#         reward = 0.0

#         progress_reward = previous_distance - current_distance
#         reward += 5.0 * progress_reward

#         reward -= 0.01

#         terminated = False
#         truncated = False

#         info = {}

#         # ----------------------------------------------------
#         # GOAL
#         # ----------------------------------------------------
#         if current_distance <= self.goal_radius:

#             reward += 150.0

#             terminated = True

#             info["termination_reason"] = "goal_reached"

#         # ----------------------------------------------------
#         # COLLISION
#         # ----------------------------------------------------
#         elif self.check_collision():

#             reward -= 80.0

#             terminated = True

#             info["termination_reason"] = "collision"

#         # ----------------------------------------------------
#         # OUT OF BOUNDS
#         # ----------------------------------------------------
#         elif np.linalg.norm(self.position) > self.tumor_radius + 1.0:

#             reward -= 60.0

#             terminated = True

#             info["termination_reason"] = "out_of_bounds"

#         # ----------------------------------------------------
#         # MAX STEPS
#         # ----------------------------------------------------
#         elif self.current_step >= self.max_steps:

#             reward -= 10.0

#             truncated = True

#             info["termination_reason"] = "max_steps"

#         observation = self._get_obs()

#         return observation, reward, terminated, truncated, info

import numpy as np
import gymnasium as gym

from gymnasium import spaces


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def wrap_angle(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


# ============================================================
# RAY / CIRCLE INTERSECTION
# ============================================================

def ray_circle_intersect(ray_origin, ray_dir, circle_center, radius):

    oc = ray_origin - circle_center

    a = np.dot(ray_dir, ray_dir)
    b = 2.0 * np.dot(oc, ray_dir)
    c = np.dot(oc, oc) - radius**2

    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        return None

    sqrt_disc = np.sqrt(discriminant)

    t1 = (-b - sqrt_disc) / (2 * a)
    t2 = (-b + sqrt_disc) / (2 * a)

    valid_ts = [t for t in [t1, t2] if t > 0]

    if len(valid_ts) == 0:
        return None

    return min(valid_ts)


# ============================================================
# MICROSWIMMER ENVIRONMENT
# ============================================================

class MicroSwimmerEnv(gym.Env):

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        tumor_radius=8.0,
        n_obstacles=12,
        obstacle_radius_range=(0.5, 1.0),
        goal_radius=0.4,
        max_steps=700,
        seed=None,
        fixed_obstacles=None,
    ):

        super().__init__()

        # ----------------------------------------------------
        # WORLD
        # ----------------------------------------------------
        self.tumor_radius = tumor_radius
        self.goal_radius = goal_radius
        self.max_steps = max_steps

        # ----------------------------------------------------
        # PHYSICS
        # ----------------------------------------------------
        self.dt = 0.08

        self.drag = 0.25

        self.v = 0.0
        self.v_max = 1.8

        self.a_max = 1.2

        self.omega_max = 3.0

        # ----------------------------------------------------
        # LIDAR
        # ----------------------------------------------------
        self.n_rays = 10
        self.lidar_range = 3.0

        # ----------------------------------------------------
        # RANDOM
        # ----------------------------------------------------
        self.rng = np.random.default_rng(seed)

        # ----------------------------------------------------
        # OBSTACLES
        # ----------------------------------------------------
        self.n_obstacles = n_obstacles
        self.obstacle_radius_range = obstacle_radius_range

        # ----------------------------------------------------
        # ACTION SPACE
        # ----------------------------------------------------
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0], dtype=np.float32),
            high=np.array([1.0, 1.0], dtype=np.float32),
            dtype=np.float32,
        )

        # ----------------------------------------------------
        # OBSERVATION SPACE
        # ----------------------------------------------------
        obs_dim = 8 + self.n_rays

        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32,
        )

        # ----------------------------------------------------
        # TARGET
        # ----------------------------------------------------
        self.goal = np.array([0.0, 0.0], dtype=np.float32)

        # ----------------------------------------------------
        # OBSTACLES
        # ----------------------------------------------------
        if fixed_obstacles is not None:
            self.obstacles = fixed_obstacles
        else:
            self.obstacles = self.generate_obstacles()

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------
        self.position = np.zeros(2, dtype=np.float32)

        self.heading = 0.0

        self.current_step = 0

    # ========================================================
    # OBSTACLE GENERATION
    # ========================================================

    def generate_obstacles(self):

        obstacles = []

        attempts = 0

        while len(obstacles) < self.n_obstacles and attempts < 5000:

            attempts += 1

            r = self.rng.uniform(*self.obstacle_radius_range)

            theta = self.rng.uniform(0, 2 * np.pi)

            radial_distance = self.rng.uniform(
                1.5,
                self.tumor_radius - r - 0.5
            )

            x = radial_distance * np.cos(theta)
            y = radial_distance * np.sin(theta)

            center = np.array([x, y])

            # ------------------------------------------------
            # TARGET CLEARANCE
            # ------------------------------------------------
            target_distance = np.linalg.norm(center - self.goal)

            if target_distance < (r + self.goal_radius + 0.7):
                continue

            # ------------------------------------------------
            # OVERLAP CHECK
            # ------------------------------------------------
            valid = True

            for obstacle in obstacles:

                d = np.linalg.norm(
                    center - obstacle["center"]
                )

                if d < (r + obstacle["radius"] + 0.3):
                    valid = False
                    break

            if valid:

                obstacles.append({
                    "center": center,
                    "radius": r,
                })

        return obstacles

    # ========================================================
    # RESET
    # ========================================================

    def reset(self, seed=None, options=None):

        super().reset(seed=seed)

        self.current_step = 0

        theta = self.rng.uniform(0, 2 * np.pi)

        self.position = np.array([
            self.tumor_radius * np.cos(theta),
            self.tumor_radius * np.sin(theta),
        ], dtype=np.float32)

        # ----------------------------------------------------
        # FACE CENTER
        # ----------------------------------------------------
        direction = self.goal - self.position

        self.heading = np.arctan2(
            direction[1],
            direction[0]
        )

        self.v = 0.0

        observation = self._get_obs()

        info = {}

        return observation, info

    # ========================================================
    # LIDAR
    # ========================================================

    def _lidar(self):

        readings = []

        angles = np.linspace(
            -np.pi,
            np.pi,
            self.n_rays,
            endpoint=False
        )

        for angle_offset in angles:

            ray_angle = self.heading + angle_offset

            ray_dir = np.array([
                np.cos(ray_angle),
                np.sin(ray_angle),
            ])

            min_distance = self.lidar_range

            for obstacle in self.obstacles:

                d = ray_circle_intersect(
                    self.position,
                    ray_dir,
                    obstacle["center"],
                    obstacle["radius"]
                )

                if d is not None:
                    min_distance = min(min_distance, d)

            readings.append(min_distance / self.lidar_range)

        return np.array(readings, dtype=np.float32)

    # ========================================================
    # OBSERVATION
    # ========================================================

    def _get_obs(self):

        dx = self.goal[0] - self.position[0]
        dy = self.goal[1] - self.position[1]

        dist = np.hypot(dx, dy)

        goal_angle = np.arctan2(dy, dx)

        relative_goal_angle = wrap_angle(
            goal_angle - self.heading
        )

        return np.concatenate([

            np.array([
                dx,
                dy,
                np.cos(self.heading),
                np.sin(self.heading),
                dist,
                relative_goal_angle,
                self.v,
                0.0
            ], dtype=np.float32),

            self._lidar()

        ]).astype(np.float32)

    # ========================================================
    # COLLISION
    # ========================================================

    def check_collision(self):

        for obstacle in self.obstacles:

            d = np.linalg.norm(
                self.position - obstacle["center"]
            )

            if d <= obstacle["radius"]:
                return True

        return False

    # ========================================================
    # STEP
    # ========================================================

    def step(self, action):

        self.current_step += 1

        # ----------------------------------------------------
        # ACTIONS
        # ----------------------------------------------------
        acceleration_command = float(action[0])

        steering_command = float(action[1])

        a = acceleration_command * self.a_max

        omega = steering_command * self.omega_max

        # ----------------------------------------------------
        # UPDATE HEADING
        # ----------------------------------------------------
        self.heading += omega * self.dt

        self.heading = wrap_angle(self.heading)

        # ----------------------------------------------------
        # UPDATE VELOCITY
        # ----------------------------------------------------
        self.v += self.dt * (a - self.drag * self.v)

        self.v = np.clip(self.v, 0.0, self.v_max)

        # ----------------------------------------------------
        # UPDATE POSITION
        # ----------------------------------------------------
        previous_distance = np.linalg.norm(
            self.goal - self.position
        )

        self.position += self.dt * self.v * np.array([
            np.cos(self.heading),
            np.sin(self.heading),
        ])

        current_distance = np.linalg.norm(
            self.goal - self.position
        )

        # ====================================================
        # REWARD
        # ====================================================

        reward = 0.0

        # ----------------------------------------------------
        # PROGRESS REWARD
        # ----------------------------------------------------
        progress_reward = previous_distance - current_distance

        reward += 25.0 * progress_reward

        # ----------------------------------------------------
        # HEADING REWARD
        # ----------------------------------------------------
        goal_angle = np.arctan2(
            -self.position[1],
            -self.position[0]
        )

        heading_error = wrap_angle(
            goal_angle - self.heading
        )

        reward += -0.1 * (heading_error ** 2)

        # ----------------------------------------------------
        # PROXIMITY PENALTY
        # ----------------------------------------------------
        min_dist = np.inf

        for obstacle in self.obstacles:

            d = (
                np.linalg.norm(
                    self.position - obstacle["center"]
                )
                - obstacle["radius"]
            )

            min_dist = min(min_dist, d)

        reward += -0.3 * max(0, 0.8 - min_dist)

        # ----------------------------------------------------
        # SMALL STEP PENALTY
        # ----------------------------------------------------
        reward -= 0.01

        terminated = False
        truncated = False

        info = {}

        # ----------------------------------------------------
        # GOAL
        # ----------------------------------------------------
        if current_distance <= self.goal_radius:

            reward += 250.0

            terminated = True

            info["termination_reason"] = "goal_reached"

        # ----------------------------------------------------
        # COLLISION
        # ----------------------------------------------------
        elif self.check_collision():

            reward -= 120.0

            terminated = True

            info["termination_reason"] = "collision"

        # ----------------------------------------------------
        # OUT OF BOUNDS
        # ----------------------------------------------------
        elif np.linalg.norm(self.position) > self.tumor_radius + 1.0:

            reward -= 80.0

            terminated = True

            info["termination_reason"] = "out_of_bounds"

        # ----------------------------------------------------
        # MAX STEPS
        # ----------------------------------------------------
        elif self.current_step >= self.max_steps:

            reward -= 15.0

            truncated = True

            info["termination_reason"] = "max_steps"

        observation = self._get_obs()

        return observation, reward, terminated, truncated, info