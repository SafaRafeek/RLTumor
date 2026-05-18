from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv

from env import MicroSwimmerEnv


# ============================================================
# CREATE ENVIRONMENT
# ============================================================

def make_env():

    env = MicroSwimmerEnv(seed=42)

    env = Monitor(env)

    return env


# ============================================================
# TRAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("MICROSWIMMER PPO TRAINING")
    print("=" * 60)

    env = DummyVecEnv([make_env])

    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.005,
        tensorboard_log="./ppo_logs/",
    )

    total_timesteps = 300_000

    print(f"Training for {total_timesteps} timesteps...")

    model.learn(total_timesteps=total_timesteps)

    model.save("microswimmer_ppo")

    print("=" * 60)
    print("Training complete.")
    print("Model saved as microswimmer_ppo")
    print("=" * 60)