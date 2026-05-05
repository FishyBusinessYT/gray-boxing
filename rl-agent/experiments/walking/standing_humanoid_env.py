import numpy as np
from src.base_humanoid_env import BaseHumanoidEnv

class StandingHumanoidEnv(BaseHumanoidEnv):
    def __init__(self, *args, healthy_z_height=(1.0, 5.0), control_cost_weight=0.1,  **kwargs):
        super().__init__(*args, **kwargs)
        self.healthy_z_height = healthy_z_height
        self.control_cost_weight = control_cost_weight

    def has_terminated(self):
        # Using relaxed Z range for stability
        z_pos = self.data.qpos[2]
        return not (self.healthy_z_height[0] < z_pos < self.healthy_z_height[1])

    def calculate_reward(self, action):
        # 1. Healthy reward (positive)
        is_healthy = not self.has_terminated()
        reward = self.healthy_reward if is_healthy else 0.0

        # 2. Control cost (negative, based on normalized actions [-1, 1])
        ctrl_cost = self.control_cost_weight * np.sum(np.square(action))

        reward -= ctrl_cost

        info = {
            "reward_survive": self.healthy_reward if is_healthy else 0.0,
            "reward_ctrl": -ctrl_cost,
            "z_height": self.data.qpos[2]
        }

        return reward, info