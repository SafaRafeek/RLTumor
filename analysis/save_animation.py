import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from stable_baselines3 import PPO
from env import MicroSwimmerEnv

model = PPO.load("microswimmer_ppo")

base_env = MicroSwimmerEnv(seed=42)
fixed_obstacles = base_env.obstacles
tumor_radius = base_env.tumor_radius

# -----------------------------
# 12 start positions
# -----------------------------
angles = np.linspace(0, 2*np.pi, 12, endpoint=False)
starts = []

for ang in angles:
    x = tumor_radius*np.cos(ang)
    y = tumor_radius*np.sin(ang)
    theta = ang + np.pi
    starts.append((x, y, theta))

# -----------------------------
# Run all trajectories
# -----------------------------
all_traj = []

for start in starts:

    env = MicroSwimmerEnv(
        seed=42,
        fixed_obstacles=fixed_obstacles
    )

    obs, _ = env.reset()

    env.position = np.array(
        [start[0], start[1]],
        dtype=np.float32
    )
    env.heading = start[2]

    obs = env._get_obs()

    tx = [env.position[0]]
    ty = [env.position[1]]

    done = False

    while not done:
        action, _ = model.predict(
            obs,
            deterministic=True
        )

        obs, reward, terminated, truncated, _ = env.step(action)

        tx.append(env.position[0])
        ty.append(env.position[1])

        done = terminated or truncated

    all_traj.append((tx, ty))


# -----------------------------
# Total frames
# -----------------------------
frames_per_traj = max(len(t[0]) for t in all_traj)
total_frames = frames_per_traj * len(all_traj)

# -----------------------------
# Plot
# -----------------------------
fig, ax = plt.subplots(figsize=(8,8))

ax.set_xlim(-10,10)
ax.set_ylim(-10,10)
ax.set_aspect("equal")

tumor = Circle((0,0), tumor_radius, fill=False, linewidth=2)
ax.add_patch(tumor)

goal = Circle((0,0), base_env.goal_radius, color="red")
ax.add_patch(goal)

for obstacle in fixed_obstacles:
    circ = Circle(
        obstacle["center"],
        obstacle["radius"],
        alpha=0.5
    )
    ax.add_patch(circ)

# start points
for s in starts:
    ax.plot(s[0], s[1], "go", markersize=6)

# lines
lines = []
dots = []

for _ in range(12):
    line, = ax.plot([], [], linewidth=2)
    dot, = ax.plot([], [], marker="o")
    lines.append(line)
    dots.append(dot)


def update(frame):

    completed = frame // frames_per_traj
    local_frame = frame % frames_per_traj

    for i in range(min(completed+1, len(all_traj))):

        tx, ty = all_traj[i]

        idx = min(local_frame, len(tx)-1) if i == completed else len(tx)-1

        lines[i].set_data(
            tx[:idx+1],
            ty[:idx+1]
        )

        dots[i].set_data(
            [tx[idx]],
            [ty[idx]]
        )

    return lines + dots


anim = FuncAnimation(
    fig,
    update,
    frames=total_frames,
    interval=50,
    blit=True
)

anim.save(
    "microswimmerall.gif",
    writer="pillow",
    fps=20
)

print("Saved microswimmer.gif")