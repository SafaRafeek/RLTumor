import time

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Circle
from stable_baselines3 import PPO

from env import MicroSwimmerEnv


# ============================================================
# GENERATE START POSITIONS
# ============================================================

def generate_start_positions(radius, n_positions=12):

    angles = np.linspace(
        0,
        2 * np.pi,
        n_positions,
        endpoint=False
    )

    positions = []

    for angle in angles:

        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        positions.append((x, y))

    return positions


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("MICROSWIMMER TUMOR NAVIGATION")
    print("=" * 60)

    # --------------------------------------------------------
    # FIXED ENVIRONMENT
    # --------------------------------------------------------
    base_env = MicroSwimmerEnv(seed=7)

    fixed_obstacles = base_env.obstacles

    # --------------------------------------------------------
    # LOAD TRAINED MODEL
    # --------------------------------------------------------
    model = PPO.load("microswimmer_ppo")

    # --------------------------------------------------------
    # FIGURE
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 8))

    tumor_radius = base_env.tumor_radius

    start_positions = generate_start_positions(
        tumor_radius,
        12
    )

    # ========================================================
    # RUN 12 SIMULATIONS
    # ========================================================

    for sim_index, (x0, y0) in enumerate(start_positions):

        print("\n" + "-" * 60)
        print(f"Simulation {sim_index + 1} / 12")
        print("-" * 60)

        # ----------------------------------------------------
        # CLEAR FIGURE
        # ----------------------------------------------------
        plt.clf()

        ax = plt.gca()

        # ----------------------------------------------------
        # CREATE ENV
        # ----------------------------------------------------
        env = MicroSwimmerEnv(
            seed=7,
            fixed_obstacles=fixed_obstacles,
        )

        obs, _ = env.reset()

        # ----------------------------------------------------
        # MANUAL START POSITION
        # ----------------------------------------------------
        env.position = np.array(
            [x0, y0],
            dtype=np.float32
        )

        # Face toward center
        direction = env.goal - env.position

        env.heading = np.arctan2(
            direction[1],
            direction[0]
        )

        env.velocity = np.zeros(2, dtype=np.float32)

        obs = env._get_obs()

        # ----------------------------------------------------
        # STORE TRAJECTORY
        # ----------------------------------------------------
        trajectory_x = [env.position[0]]
        trajectory_y = [env.position[1]]

        done = False

        # ====================================================
        # RUN POLICY
        # ====================================================

        while not done:

            action, _ = model.predict(
                obs,
                deterministic=True
            )

            obs, reward, terminated, truncated, info = env.step(action)

            trajectory_x.append(env.position[0])
            trajectory_y.append(env.position[1])

            done = terminated or truncated

        # ----------------------------------------------------
        # DEBUG INFO
        # ----------------------------------------------------
        reason = info.get(
            "termination_reason",
            "unknown"
        )

        print(f"Trajectory length: {len(trajectory_x)}")
        print(f"Termination reason: {reason}")

        # ====================================================
        # DRAW ENVIRONMENT
        # ====================================================

        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)

        ax.set_aspect("equal")

        ax.set_title(
            f"Microswimmer Tumor Navigation - Run {sim_index + 1}"
        )

        # ----------------------------------------------------
        # TUMOR BOUNDARY
        # ----------------------------------------------------
        tumor_circle = Circle(
            (0, 0),
            tumor_radius,
            fill=False,
            linewidth=2,
        )

        ax.add_patch(tumor_circle)

        # ----------------------------------------------------
        # TARGET
        # ----------------------------------------------------
        target = Circle(
            (0, 0),
            env.goal_radius,
            color="red",
        )

        ax.add_patch(target)

        # ----------------------------------------------------
        # OBSTACLES
        # ----------------------------------------------------
        for obstacle in fixed_obstacles:

            obstacle_circle = Circle(
                obstacle["center"],
                obstacle["radius"],
                alpha=0.6,
            )

            ax.add_patch(obstacle_circle)

        # ----------------------------------------------------
        # PATH + SWIMMER
        # ----------------------------------------------------
        path_line, = ax.plot(
            [],
            [],
            linewidth=2,
        )

        swimmer_dot, = ax.plot(
            [],
            [],
            marker="o",
            markersize=8,
        )

        # ====================================================
        # MANUAL ANIMATION LOOP
        # ====================================================

        for frame in range(len(trajectory_x)):

            x = trajectory_x[:frame + 1]
            y = trajectory_y[:frame + 1]

            path_line.set_data(x, y)

            swimmer_dot.set_data(
                [trajectory_x[frame]],
                [trajectory_y[frame]]
            )

            plt.draw()

            plt.pause(0.035)

        # ----------------------------------------------------
        # HOLD FINAL TRAJECTORY
        # ----------------------------------------------------
        time.sleep(1.0)

    print("\nAll simulations completed.")

    plt.show()