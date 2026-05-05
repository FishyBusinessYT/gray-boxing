import numpy as np
from src.base_humanoid_env import BaseHumanoidEnv

class StandingHumanoidEnv(BaseHumanoidEnv):
    def __init__(self, *args,
                 healthy_z_height=(2.5, 10.0),
                 control_cost_weight=0.001,
                 upright_weight=10.0,
                 height_weight=5.0,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.healthy_z_height = healthy_z_height
        self.control_cost_weight = control_cost_weight
        self.upright_weight = upright_weight
        self.height_weight = height_weight
        self.target_height = 3.7 # From XML torso position

    def has_terminated(self):
        z_pos = self.data.qpos[2]
        return not (self.healthy_z_height[0] < z_pos < self.healthy_z_height[1])

    def calculate_reward(self, action):
        # 1. Healthy reward (reducido para que no baste con "no morir")
        is_healthy = not self.has_terminated()
        reward = 5.0 if is_healthy else 0.0

        upright_reward = height_reward = 0.0

        if is_healthy:
            # 2. Uprightness reward (MUCHO más estricto)
            # torso_z_axis es el componente Z del eje Z local del torso.
            # 1.0 = vertical, 0.0 = horizontal.
            torso_z_axis = self.data.xmat[1][8]
            # Usamos una potencia para penalizar desviaciones pequeñas mucho más
            upright_reward = self.upright_weight * (max(0, torso_z_axis) ** 2)
            reward += upright_reward

            # 3. Height reward (Cuadrática para precisión)
            z_pos = self.data.qpos[2]
            # Error normalizado de altura
            height_error = abs(z_pos - self.target_height) / self.target_height
            height_reward = self.height_weight * np.exp(-10.0 * height_error)
            reward += height_reward

            # 4. Joint limit penalty (Para evitar que se "apoye" en los límites)
            # Esto ayuda a que el agente prefiera el centro del rango
            joint_dist = np.mean(np.square(action))
            reward -= 0.1 * joint_dist

        # 5. Control cost
        ctrl_cost = self.control_cost_weight * np.sum(np.square(action))
        reward -= ctrl_cost

        info = {
            "reward_survive": 5.0 if is_healthy else 0.0,
            "reward_upright": upright_reward if is_healthy else 0.0,
            "reward_height": height_reward if is_healthy else 0.0,
            "z_height": self.data.qpos[2]
        }

        return reward, info