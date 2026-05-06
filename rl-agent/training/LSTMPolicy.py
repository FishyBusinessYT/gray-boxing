import gymnasium as gym
from sb3_contrib import RecurrentPPO
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv, VecNormalize
from stable_baselines3.common.vec_env import sync_envs_normalization
from pathlib import Path
import torch.nn as nn

CURRENT_PATH = Path(__file__).parent.resolve()

# TODO: If I'll use SB3, I'll need to change the storage checkpoints so that they also store the .pkl
if __name__ == "__main__": # Needed for multi-process running
    # The observation clipping is done on the OpenAI paper
    env = make_vec_env("Humanoid-v5", n_envs=16, vec_env_cls=SubprocVecEnv) # Parallel envs
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=0.5) # Normalize observations and rewards

    # Eval env
    eval_env = DummyVecEnv([
        lambda: gym.make("Humanoid-v5", render_mode="human")
    ])
    eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False, clip_obs=0.5)

    # Share normalizations across training and eval envs
    sync_envs_normalization(env, eval_env)

    # Callbacks
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(CURRENT_PATH / "training_results"),
        eval_freq=1_000_000 // env.num_envs,
        render=True,
        n_eval_episodes=8,
        deterministic=True
    )
    checkpoint_callback = CheckpointCallback(
        save_freq=1_000_000 // env.num_envs,
        save_path=str(CURRENT_PATH / "training_results/checkpoints"),
        name_prefix="ppo_humanoid"
    )

    # Model. Hparams taken from Humanoid-v4 rl-zoo params
    policy_kwargs = dict(
        # IMPORTANTE: Desactivar el compartido del extractor para que
        # el Actor y el Crítico tengan su propio MLP de entrada independiente.
        share_features_extractor=False,

        # Configuración del LSTM
        lstm_hidden_size=128,  # Tamaño de la celda oculta
        n_lstm_layers=1,  # Número de capas LSTM apiladas

        # IMPORTANTE: Desactivar el compartido del LSTM para que
        # Actor y Crítico tengan memorias temporales separadas.
        shared_lstm=False,
        enable_critic_lstm=True,

        # net_arch=[] significa que NO habrá capas MLP adicionales después del LSTM
        net_arch=[],
        activation_fn=nn.ReLU,
    )

    model = RecurrentPPO(
        "MlpLstmPolicy",
        env,
        policy_kwargs=policy_kwargs,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048 // env.num_envs,      # Cuántos pasos recolectar antes de actualizar
        batch_size=64,     # Tamaño del minibatch para el entrenamiento del LSTM
        n_epochs=10,       # Cuántas veces pasar por los datos recolectados
        device="cpu" # Runs slightly faster on CPU
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
