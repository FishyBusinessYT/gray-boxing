import gymnasium as gym
from gymnasium import spaces
import mujoco
import numpy as np
from stable_baselines3 import PPO
import os

class HumanoidStandEnv(gym.Env):
    def __init__(self, model_path):
        super(HumanoidStandEnv, self).__init__()

        # Cargar modelo
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)

        # Espacio de acciones: Tus 14 actuadores (rango de -1 a 1 para facilitar el aprendizaje)
        nu = self.model.nu
        self.action_space = spaces.Box(low=-1, high=1, shape=(nu,), dtype=np.float32)

        # Espacio de observaciones: Posiciones y velocidades de los joints + orientación del torso
        # (Ajustamos el tamaño dinámicamente según el modelo)
        obs_size = self.model.nq + self.model.nv
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float32)

    def _get_obs(self):
        # Concatenamos posiciones (qpos) y velocidades (qvel)
        return np.concatenate([self.data.qpos, self.data.qvel]).astype(np.float32)

    def step(self, action):
        # 1. Aplicar la acción (escalada al rango de control del XML)
        ctrl_ranges = self.model.actuator_ctrlrange
        denorm_action = (action + 1) / 2 * (ctrl_ranges[:, 1] - ctrl_ranges[:, 0]) + ctrl_ranges[:, 0]
        self.data.ctrl[:] = denorm_action

        # 2. Simular un paso físico
        mujoco.mj_step(self.model, self.data)

        # 3. Calcular Recompensa
        torso_height = self.data.qpos[2]  # Z es el índice 2 en el freejoint

        # Recompensa simple: Estar alto - castigo por usar demasiada energía
        reward = torso_height - 0.1 * np.sum(np.square(action))

        # 4. Condición de término (Si el torso cae por debajo de cierta altura)
        terminated = torso_height < 1.5  # El torso empieza en 3.7, si baja de 1.5 se asume caída
        truncated = False

        return self._get_obs(), reward, terminated, truncated, {}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)
        return self._get_obs(), {}


# ── ENTRENAMIENTO ─────────────────────────────────────────────────────────────

MODEL_PATH = "character.xml"  # Cambia esto a la ruta de tu XML corregido


def train():
    # Crear el entorno
    env = HumanoidStandEnv(MODEL_PATH)

    # Definir el modelo PPO (Proximal Policy Optimization)
    # MlpPolicy es ideal para datos vectoriales (no imágenes)
    model = PPO("MlpPolicy", env, verbose=1, device="auto", tensorboard_log="./ppo_stand_log/")

    print("Entrenando... Presiona Ctrl+C para detener y guardar.")
    try:
        # 500,000 pasos suelen bastar para un balance básico
        model.learn(total_timesteps=500000)
    except KeyboardInterrupt:
        print("Guardando modelo...")

    model.save("humanoid_stand_model")
    print("Modelo guardado exitosamente.")


if __name__ == "__main__":
    train()