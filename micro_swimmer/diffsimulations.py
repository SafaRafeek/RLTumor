import os
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
# RUN SINGLE TRAJECTORY
# ============================================================

def run_single_trajectory(env, model, start_x, start_y):

    # --------------------------------------------------------
    # RESET ENV
    # --------------------------------------------------------
    obs, _ = env.reset()

    env.position = np.array(
        [start_x, start_y],
        dtype=np.float32
    )

    # Face center
    direction = env.goal - env.position

    env.heading = np.arctan2(
        direction[1],
        direction[0]
    )

    env.v = 0.0

    obs = env._get_obs()

    # --------------------------------------------------------
    # STORE TRAJECTORY
    # --------------------------------------------------------
    trajectory_x = [env.position[0]]
    trajectory_y = [env.position[1]]

    done = False

    while not done:

        action, _ = model.predict(
            obs,
            deterministic=True
        )

        obs, reward, terminated, truncated, info = env.step(action)

        trajectory_x.append(env.position[0])
        trajectory_y.append(env.position[1])

        done = terminated or truncated

    reason = info.get(
        "termination_reason",
        "unknown"
    )

    reached_target = (reason == "goal_reached")

    return (
        trajectory_x,
        trajectory_y,
        reached_target,
        reason
    )


# ============================================================
# DRAW SIMULATION
# ============================================================

def draw_simulation(
    env,
    trajectories,
    obstacle_count,
    sim_index
):

    plt.clf()

    ax = plt.gca()

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)

    ax.set_aspect("equal")

    ax.set_title(
        f"{obstacle_count} Obstacles | Simulation {sim_index}"
    )

    # --------------------------------------------------------
    # TUMOR BOUNDARY
    # --------------------------------------------------------
    tumor_circle = Circle(
        (0, 0),
        env.tumor_radius,
        fill=False,
        linewidth=2,
    )

    ax.add_patch(tumor_circle)

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------
    target = Circle(
        (0, 0),
        env.goal_radius,
        color="red",
    )

    ax.add_patch(target)

    # --------------------------------------------------------
    # OBSTACLES
    # --------------------------------------------------------
    for obstacle in env.obstacles:

        obstacle_circle = Circle(
            obstacle["center"],
            obstacle["radius"],
            alpha=0.5,
        )

        ax.add_patch(obstacle_circle)

    # --------------------------------------------------------
    # TRAJECTORIES
    # --------------------------------------------------------
    for traj_x, traj_y, reached in trajectories:

        if reached:
            color = "green"
        else:
            color = "blue"

        ax.plot(
            traj_x,
            traj_y,
            linewidth=1.5,
            color=color,
        )

        ax.scatter(
            traj_x[-1],
            traj_y[-1],
            s=20,
            color=color,
        )

    # create folder
    os.makedirs("simulation_images", exist_ok=True)

    # save figure
    filename = (
        f"simulation_images/"
        f"obstacles_{obstacle_count}_sim_{sim_index}.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.draw()
    
    plt.pause(0.5)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("BATCH MICSWIMMER SIMULATIONS")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------
    model = PPO.load("microswimmer_ppo")

    # --------------------------------------------------------
    # FIGURE
    # --------------------------------------------------------
    plt.figure(figsize=(8, 8))

    # --------------------------------------------------------
    # RESULTS STORAGE
    # --------------------------------------------------------
    results = []

    # ========================================================
    # SIMULATION CONFIGS
    # ========================================================

    simulation_configs = [

        # 1 simulation with no obstacles
        (0, 1),

        # 20 simulations each
        (3, 20),
        (6, 20),
        (9, 20),
        (12, 20),
        (15, 20),
    ]

    # ========================================================
    # RUN ALL SIMULATIONS
    # ========================================================

    for obstacle_count, num_simulations in simulation_configs:

        print("\n" + "=" * 60)
        print(f"Obstacle Count: {obstacle_count}")
        print("=" * 60)

        for sim_num in range(1, num_simulations + 1):

            print("\n" + "-" * 60)
            print(
                f"Simulation {sim_num} "
                f"with {obstacle_count} obstacles"
            )
            print("-" * 60)

            # ------------------------------------------------
            # CREATE ENV
            # ------------------------------------------------
            env = MicroSwimmerEnv(
                seed=sim_num,
                n_obstacles=obstacle_count,
            )

            # ------------------------------------------------
            # START POSITIONS
            # ------------------------------------------------
            start_positions = generate_start_positions(
                env.tumor_radius,
                12
            )

            trajectories = []

            success_count = 0

            # =================================================
            # RUN 12 START POSITIONS
            # =================================================

            for start_index, (x0, y0) in enumerate(start_positions):

                (
                    traj_x,
                    traj_y,
                    reached_target,
                    reason
                ) = run_single_trajectory(
                    env,
                    model,
                    x0,
                    y0
                )

                trajectories.append(
                    (
                        traj_x,
                        traj_y,
                        reached_target
                    )
                )

                if reached_target:
                    success_count += 1

                # --------------------------------------------
                # STORE RESULT
                # --------------------------------------------
                if reached_target:
                    result_text = "target reached"
                else:
                    result_text = "target not reached"

                results.append({

                    "obstacle_count": obstacle_count,

                    "simulation_number": sim_num,

                    "start_position": start_index + 1,

                    "result": result_text,

                    "termination_reason": reason,

                    "trajectory_length": len(traj_x),
                })

                print(
                    f"Start {start_index + 1}: "
                    f"{result_text}"
                )

            # ------------------------------------------------
            # DRAW ALL 12 TRAJECTORIES
            # ------------------------------------------------
            draw_simulation(
                env,
                trajectories,
                obstacle_count,
                sim_num
            )

            print(
                f"Success Rate: "
                f"{success_count}/12"
            )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    df = pd.DataFrame(results)

    csv_filename = "microswimmer_results.csv"

    xlsx_filename = "microswimmer_results.xlsx"

    df.to_csv(csv_filename, index=False)

    df.to_excel(xlsx_filename, index=False)

    print("\n" + "=" * 60)
    print("ALL SIMULATIONS COMPLETE")
    print("=" * 60)

    print(f"\nCSV saved as: {csv_filename}")
    print(f"Excel saved as: {xlsx_filename}")

    plt.show()