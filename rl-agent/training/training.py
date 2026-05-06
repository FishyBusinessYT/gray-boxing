import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv, VecNormalize
from stable_baselines3.common.vec_env import sync_envs_normalization
from pathlib import Path

CURRENT_PATH = Path(__file__).parent.resolve()

# TODO: If I'll use SB3, I'll need to change the storage checkpoints so that they also store the .pkl
if __name__ == "__main__": # Needed for multi-process running
    env = make_vec_env("Humanoid-v5", n_envs=12, vec_env_cls=SubprocVecEnv) # Parallel envs
    env = VecNormalize(env, norm_obs=True, norm_reward=True) # Normalize observations and rewards

    # Eval env
    eval_env = DummyVecEnv([
        lambda: gym.make("Humanoid-v5", render_mode="human")
    ])
    eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False)

    # Share normalizations across training and eval envs
    sync_envs_normalization(env, eval_env)

    # Callbacks
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(CURRENT_PATH / "training_results"),
        eval_freq=100_000 // env.num_envs,
        render=True,
        n_eval_episodes=8,
        deterministic=True
    )
    checkpoint_callback = CheckpointCallback(
        save_freq=1_000_000 // env.num_envs,
        save_path=str(CURRENT_PATH / "training_results/checkpoints"),
        name_prefix="ppo_humanoid"
    )

    # Model
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        device="cpu" # Runs faster on CPU because of the small net size
    )


    # Training
    model.learn(
        total_timesteps=10_000_000,
        callback=[checkpoint_callback, eval_callback],
        progress_bar=True
    )

    # Parameter storage
    model.save("results/ppo_humanoid_final")
    env.save("results/vecnormalize.pkl") # Store the obs_rms for use in future testing envs
