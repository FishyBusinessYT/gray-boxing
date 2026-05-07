import gym
import numpy as np
import torch as th
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback

"""
IMPLEMENTACIÓN DE REDUCCIÓN DE LEARNING RATE EN PLATEAU (SB3) - ENTORNO ESTÁNDAR

Este script demuestra el uso del scheduler de LR basado en rendimiento usando
un entorno estándar de MuJoCo (Humanoid-v4), eliminando la necesidad de wrappers complejos.

COMPONENTES:
1. PerformanceLR: Controlador de LR que permite cambios dinámicos.
2. ReduceLROnPlateauCallback: Monitor de rendimiento.
3. Humanoid-v4: Entorno estándar de Gymnasium/MuJoCo.
"""

class PerformanceLR:
    """
    CONTROLADOR DINÁMICO DE LEARNING RATE
    
    SB3 espera una función para el parámetro 'learning_rate'.
    Esta clase actúa como esa función pero mantiene un estado interno ('current_lr')
    que podemos modificar desde fuera (desde un Callback).
    """
    def __init__(self, initial_lr: float):
        self.current_lr = initial_lr

    def __call__(self, progress_remaining: float) -> float:
        """
        Devuelve el LR actual. SB3 llama a esto antes de cada actualización.
        """
        return self.current_lr


class ReduceLROnPlateauCallback(BaseCallback):
    """
    CALLBACK PARA REDUCCIÓN DE LR EN PLATEAU
    
    Monitorea el 'mean_reward' obtenido durante las evaluaciones de EvalCallback.
    Si no hay un nuevo récord tras 'patience' evaluaciones, reduce el LR.
    """
    def __init__(self, lr_controller, patience: int = 3, factor: float = 0.5, verbose: int = 1):
        super().__init__(verbose)
        self.lr_controller = lr_controller
        self.patience = patience          # Cuántas evaluaciones esperar sin mejora
        self.factor = factor              # Multiplicador del LR
        self.best_reward = -float('inf')  # Mejor reward histórico
        self.no_improvement_count = 0     # Contador de evaluaciones fallidas

    def _on_step(self) -> bool:
        """
        Lógica de detección de estancamiento.
        """
        if hasattr(self.parent, 'last_mean_reward'):
            current_reward = self.parent.last_mean_reward
            
            if current_reward > self.best_reward:
                self.best_reward = current_reward
                self.no_improvement_count = 0
                if self.verbose > 0:
                    print(f"[LR Scheduler] ¡Nuevo récord! Reward: {current_reward:.2f}")
            else:
                self.no_improvement_count += 1

            if self.no_improvement_count >= self.patience:
                old_lr = self.lr_controller.current_lr
                self.lr_controller.current_lr *= self.factor
                self.no_improvement_count = 0
                if self.verbose > 0:
                    print(f"\n[LR Scheduler] ESTANCAMIENTO detectado en Humanoid.")
                    print(f"[LR Scheduler] Reduciendo LR: {old_lr:.2e} -> {self.lr_controller.current_lr:.2e}")
        
        return True


def train_humanoid():
    # Nombre del entorno estándar (requiere mujoco instalado)
    env_id = "Humanoid-v4"

    def make_env():
        # Aquí ya no necesitamos wrappers complejos
        return gym.make(env_id)

    # 1. Entorno de Entrenamiento
    venv = DummyVecEnv([make_env])
    venv = VecNormalize(venv, norm_obs=True, norm_reward=True)
    
    # 2. Entorno de Evaluación (Rewards reales)
    eval_env = DummyVecEnv([make_env])
    eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False)

    # 3. Configuración del Scheduler
    lr_controller = PerformanceLR(initial_lr=3e-4)
    reduce_lr_cb = ReduceLROnPlateauCallback(lr_controller, patience=5, factor=0.5)

    # 4. Configuración del EvalCallback
    eval_callback = EvalCallback(
        eval_env, 
        best_model_save_path='./logs/humanoid_best',
        log_path='./logs/', 
        eval_freq=20000,          # Humanoid es lento, evaluamos cada 20k pasos
        n_eval_episodes=10,
        callback_after_eval=reduce_lr_cb
    )

    # 5. Configuración del Modelo PPO
    # Nota: Humanoid suele requerir redes más grandes (e.g. 256x256 o 400x300)
    model = PPO(
        "MlpPolicy",
        venv,
        learning_rate=lr_controller,
        policy_kwargs=dict(net_arch=[256, 256], activation_fn=th.nn.ReLU),
        verbose=1,
        n_steps=2048,
        batch_size=64,
        gae_lambda=0.95,
        gamma=0.99,
        n_epochs=10,
        ent_coef=0.0,
    )

    print(f"Iniciando entrenamiento en {env_id} con ReduceLROnPlateau...")
    model.learn(total_timesteps=2000000, callback=eval_callback)
    model.save("humanoid_mlp_plateau_policy")

if __name__ == "__main__":
    train_humanoid()
