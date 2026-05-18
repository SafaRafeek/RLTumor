import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# LOAD RESULTS
# ============================================================

# Use either CSV or XLSX
# df = pd.read_csv("microswimmer_results.csv")

df = pd.read_excel("microswimmer_results.xlsx")


# ============================================================
# BASIC INFO
# ============================================================

print("=" * 60)
print("MICROSWIMMER RESULTS ANALYSIS")
print("=" * 60)

print("\nTotal Runs:")
print(len(df))

print("\nObstacle Counts:")
print(df["obstacle_count"].unique())


# ============================================================
# SUCCESS COLUMN
# ============================================================

df["success"] = df["result"] == "target reached"


# ============================================================
# SUCCESS RATE BY OBSTACLE COUNT
# ============================================================

success_rates = (
    df.groupby("obstacle_count")["success"]
    .mean()
    * 100
)

print("\n" + "=" * 60)
print("SUCCESS RATE (%)")
print("=" * 60)

for obstacle_count, rate in success_rates.items():

    print(
        f"{obstacle_count} obstacles : "
        f"{rate:.2f}%"
    )


# ============================================================
# PLOT 1
# SUCCESS RATE BAR CHART
# ============================================================

plt.figure(figsize=(8, 5))

plt.bar(
    success_rates.index.astype(str),
    success_rates.values
)

plt.xlabel("Number of Obstacles")
plt.ylabel("Success Rate (%)")

plt.title(
    "Microswimmer Success Rate vs Obstacle Count"
)

plt.ylim(0, 100)

plt.grid(True)

plt.show()


# ============================================================
# PLOT 2
# TRAJECTORY LENGTH HISTOGRAM
# ============================================================

plt.figure(figsize=(8, 5))

plt.hist(
    df["trajectory_length"],
    bins=30
)

plt.xlabel("Trajectory Length")
plt.ylabel("Frequency")

plt.title("Distribution of Trajectory Lengths")

plt.grid(True)

plt.show()


# ============================================================
# PLOT 3
# SUCCESS VS FAILURE COUNTS
# ============================================================

success_failure = (
    df.groupby(
        ["obstacle_count", "success"]
    )
    .size()
    .unstack(fill_value=0)
)

success_failure.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.xlabel("Obstacle Count")
plt.ylabel("Number of Simulations")

plt.title(
    "Successful vs Failed Simulations"
)

plt.grid(True)

plt.show()


# ============================================================
# PLOT 4
# AVERAGE TRAJECTORY LENGTH
# ============================================================

avg_length = (
    df.groupby("obstacle_count")[
        "trajectory_length"
    ]
    .mean()
)

plt.figure(figsize=(8, 5))

plt.plot(
    avg_length.index,
    avg_length.values,
    marker="o"
)

plt.xlabel("Obstacle Count")
plt.ylabel("Average Trajectory Length")

plt.title(
    "Average Trajectory Length vs Obstacles"
)

plt.grid(True)

plt.show()


# ============================================================
# TERMINATION REASON ANALYSIS
# ============================================================

termination_counts = (
    df.groupby(
        ["obstacle_count", "termination_reason"]
    )
    .size()
    .unstack(fill_value=0)
)

print("\n" + "=" * 60)
print("TERMINATION REASONS")
print("=" * 60)

print(termination_counts)


# ============================================================
# PLOT 5
# TERMINATION REASONS
# ============================================================

termination_counts.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 6)
)

plt.xlabel("Obstacle Count")
plt.ylabel("Count")

plt.title(
    "Termination Reasons by Obstacle Count"
)

plt.grid(True)

plt.show()


# ============================================================
# BEST/WORST START POSITIONS
# ============================================================

start_success = (
    df.groupby("start_position")["success"]
    .mean()
    * 100
)

print("\n" + "=" * 60)
print("START POSITION SUCCESS RATES")
print("=" * 60)

for start_pos, rate in start_success.items():

    print(
        f"Start Position {start_pos}: "
        f"{rate:.2f}%"
    )


# ============================================================
# PLOT 6
# START POSITION SUCCESS RATE
# ============================================================

plt.figure(figsize=(10, 5))

plt.bar(
    start_success.index.astype(str),
    start_success.values
)

plt.xlabel("Start Position")
plt.ylabel("Success Rate (%)")

plt.title(
    "Success Rate by Start Position"
)

plt.ylim(0, 100)

plt.grid(True)

plt.show()

# ============================================================
# TIME-TO-TARGET ANALYSIS
# ============================================================

# ------------------------------------------------------------
# ONLY SUCCESSFUL TRAJECTORIES
# ------------------------------------------------------------

successful_df = df[
    df["success"] == True
].copy()

# ------------------------------------------------------------
# CONVERT STEPS -> TIME
# ------------------------------------------------------------

# Must match env.py
dt = 0.08

successful_df["time_to_target"] = (
    successful_df["trajectory_length"] * dt
)

# ------------------------------------------------------------
# AVERAGE TIME PER OBSTACLE COUNT
# ------------------------------------------------------------

avg_time = (
    successful_df
    .groupby("obstacle_count")["time_to_target"]
    .mean()
)

print("\n" + "=" * 60)
print("AVERAGE TIME TO REACH TARGET")
print("=" * 60)

for obstacle_count, t in avg_time.items():

    print(
        f"{obstacle_count} obstacles : "
        f"{t:.2f} seconds"
    )

# ============================================================
# PLOT 7
# TIME TO TARGET VS OBSTACLE COUNT
# ============================================================

plt.figure(figsize=(8, 5))

plt.plot(
    avg_time.index,
    avg_time.values,
    marker="o"
)

plt.xlabel("Number of Obstacles")
plt.ylabel("Average Time to Reach Target (s)")

plt.title(
    "Average Time Taken by Successful Microswimmers"
)

plt.grid(True)

plt.show()

# ============================================================
# PLOT 8
# TIME DISTRIBUTION HISTOGRAM
# ============================================================

plt.figure(figsize=(8, 5))

plt.hist(
    successful_df["time_to_target"],
    bins=25
)

plt.xlabel("Time to Reach Target (s)")
plt.ylabel("Frequency")

plt.title(
    "Distribution of Successful Arrival Times"
)

plt.grid(True)

plt.show()

# ============================================================
# SAVE TIME ANALYSIS
# ============================================================

time_summary = pd.DataFrame({

    "obstacle_count": avg_time.index,

    "average_time_to_target_sec":
        avg_time.values,
})

time_summary.to_csv(
    "time_analysis_summary.csv",
    index=False
)

time_summary.to_excel(
    "time_analysis_summary.xlsx",
    index=False
)

print("\nSaved:")
print("- time_analysis_summary.csv")
print("- time_analysis_summary.xlsx")

# ============================================================
# SAVE SUMMARY
# ============================================================

summary_df = pd.DataFrame({

    "obstacle_count": success_rates.index,

    "success_rate_percent": success_rates.values,

    "average_trajectory_length":
        avg_length.values,
})

summary_df.to_csv(
    "analysis_summary.csv",
    index=False
)

summary_df.to_excel(
    "analysis_summary.xlsx",
    index=False
)

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)

print("\nSaved:")
print("- analysis_summary.csv")
print("- analysis_summary.xlsx")