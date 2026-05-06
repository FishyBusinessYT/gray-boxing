import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback, BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv, VecNormalize
from stable_baselines3.common.vec_env import sync_envs_normalization
from pathlib import Path
import torch.nn as nn
from stable_baselines3.common.monitor import Monitor

CURRENT_PATH = Path(__file__).parent.resolve()

class PerformanceLR:
    def __init__(self, initial_lr: float):
        self.current_lr = initial_lr

    def __call__(self, progress_remaining: float) -> float:
        return self.current_lr


class ReduceLROnPlateauCallback(BaseCallback):
    def __init__(self, lr_controller, patience: int = 3, factor: float = 0.5, verbose: int = 1):
        super().__init__(verbose)
        self.lr_controller = lr_controller
        self.patience = patience  # Cuántas evaluaciones esperar sin mejora
        self.factor = factor  # Multiplicador del LR (0.5 = reducir a la mitad)
        self.best_reward = -float('inf')  # Mejor reward histórico
        self.no_improvement_count = 0  # Contador de evaluaciones fallidas

    def _on_step(self) -> bool:
        """
        Este método se ejecuta después de que EvalCallback termina una evaluación
        siempre que se pase como 'callback_after_eval'.
        """
        # EvalCallback guarda el último resultado en 'self.parent.last_mean_reward'
        if hasattr(self.parent, 'last_mean_reward'):
            current_reward = self.parent.last_mean_reward

            if current_reward > self.best_reward:
                self.best_reward = current_reward
                self.no_improvement_count = 0
            else:
                self.no_improvement_count += 1

            if self.no_improvement_count >= self.patience:
                old_lr = self.lr_controller.current_lr
                self.lr_controller.current_lr *= self.factor
                self.no_improvement_count = 0
                if self.verbose > 0:
                    print(f"\n[LR Scheduler] ESTANCAMIENTO detectado ({self.patience} evaluaciones).")
                    print(f"[LR Scheduler] Reduciendo LR: {old_lr:.2e} -> {self.lr_controller.current_lr:.2e}")

        return True

# TODO: If I'll use SB3, I'll need to change the storage checkpoints so that they also store the .pkl
# TODO: More frecuent storage of the best model
if __name__ == "__main__": # Needed for multi-process running
    ######################
    # Environments
    ######################

    # Training env
    env = make_vec_env("Humanoid-v5", n_envs=16, vec_env_cls=SubprocVecEnv) # Parallel envs
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=5.0) # Normalize observations and rewards

    # GUI Eval env
    gui_eval_env = DummyVecEnv([
        lambda: gym.make("Humanoid-v5", render_mode="human") # Monitor to have accurate values for rewards. Not needed here
    ])
    gui_eval_env = VecNormalize(gui_eval_env, norm_obs=True, norm_reward=False, clip_obs=5.0)

    # Lr scheduler eval env
    lr_eval_env = DummyVecEnv([lambda: Monitor(gym.make("Humanoid-v5"))]) # Monitor needed here
    lr_eval_env = VecNormalize(lr_eval_env, norm_obs=True, norm_reward=False, clip_obs=5.0)

    # Share normalizations across training and eval envs
    sync_envs_normalization(env, gui_eval_env)
    sync_envs_normalization(env, lr_eval_env)

    #######################
    # Callbacks
    #######################

    # Lr controller eval
    lr_controller = PerformanceLR(initial_lr=3.56987e-05)
    reduce_lr_cb = ReduceLROnPlateauCallback(lr_controller, patience=8, factor=0.5)
    lr_eval_callback = EvalCallback(
        lr_eval_env,
        eval_freq=100_000 // env.num_envs,
        render=False,
        n_eval_episodes=10,
        deterministic=True,
        callback_after_eval=reduce_lr_cb
    )

    # GUI eval
    gui_eval_callback = EvalCallback(
        gui_eval_env,
        best_model_save_path=str(CURRENT_PATH / "training_results"),
        eval_freq=1_000_000 // env.num_envs,
        render=True,
        n_eval_episodes=5,
        deterministic=True,
    )

    # Checkpointing
    checkpoint_callback = CheckpointCallback(
        save_freq=1_000_000 // env.num_envs,
        save_path=str(CURRENT_PATH / "training_results/checkpoints"),
        name_prefix="ppo_humanoid"
    )

    ###########################
    # Model
    ###########################

    # Hparams taken from Humanoid-v4 rl-zoo params
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        device="cpu", # Runs faster on CPU because of the small net size
        batch_size=256,
        n_steps=2048 // env.num_envs, # The original yml uses 1 env, which means a 512 step buffer
        gamma=0.95, # Discount factor
        learning_rate=lr_controller, # Expects a function or a number for the lr
        ent_coef=0.00238306, # Controls exploration/exploitation
        clip_range=0.3, # How much can the policy change each iteration
        n_epochs=5, # Buffer size stays constant, that's why I don't touch the epochs
        gae_lambda=0.9,
        max_grad_norm=2,
        vf_coef=0.431892,
        policy_kwargs=dict(
            log_std_init=-2,
            ortho_init=False,
            activation_fn=nn.ReLU,
            net_arch=dict(pi=[256, 256], vf=[256, 256])
        )
    )


    # Training
    model.learn(
        total_timesteps=10_000_000,
        callback=[checkpoint_callback, gui_eval_callback, lr_eval_callback],
        progress_bar=True
    )

    # Parameter storage
    model.save("results/ppo_humanoid_final")
    env.save("results/vecnormalize.pkl") # Store the obs_rms for use in future testing envs
