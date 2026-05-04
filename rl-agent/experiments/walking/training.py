import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv, VecNormalize
from .standing_humanoid_env import StandingHumanoidEnv
from gymnasium.envs.registration import register

register(
    id="StandingHumanoid",
    entry_point="experiments.walking.standing_humanoid_env:StandingHumanoidEnv",
    max_episode_steps=1000,
)

if __name__ == "__main__":
    # ===== 1. ENTRENAMIENTO =====
    env = make_vec_env("StandingHumanoid", n_envs=16, vec_env_cls=SubprocVecEnv)

    # Normalización
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.0)

    # ===== 2. EVALUACIÓN =====
    eval_env = DummyVecEnv([
        lambda: gym.make("StandingHumanoid", render_mode="human")
    ])

    eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False)

    # MUY IMPORTANTE: compartir estadísticas
    eval_env.obs_rms = env.obs_rms


    # ===== 3. CALLBACKS =====
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./logs/best_model",
        log_path="./logs/results",
        eval_freq=100_000 // env.num_envs,
        render=True,
        n_eval_episodes=8,
        deterministic=True
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=1_000_000 // env.num_envs,
        save_path="./checkpoints",
        name_prefix="ppo_humanoid"
    )


    # ===== 4. MODELO (más capacidad + mejor config) =====
    policy_kwargs = dict(
        net_arch=dict(
            pi=[256, 256, 128],
            vf=[256, 256, 128]
        )
    )

    model = PPO(
        "MlpPolicy",
        env,
        policy_kwargs=policy_kwargs,
        batch_size=512,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        verbose=1,
        device="cpu"
    )


    # ===== 5. ENTRENAMIENTO =====
    model.learn(
        total_timesteps=10_000_000,
        callback=[checkpoint_callback, eval_callback],
        progress_bar=True
    )

    # ===== 6. GUARDAR =====
    model.save("ppo_humanoid_final")

    # Guardar estadísticas de normalización (CLAVE para usar el modelo después)
    env.save("vecnormalize.pkl")