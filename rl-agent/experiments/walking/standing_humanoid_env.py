import numpy as np
from src.humanoid_base_env import HumanoidBaseEnv

class StandingHumanoidEnv(HumanoidBaseEnv):
    def __init__(self, *args, healthy_z_height=(3.3, 3.9), control_cost_weight=0.1,  **kwargs):
        super().__init__(*args, **kwargs)
        self.healthy_z_height = healthy_z_height
        self.control_cost_weight = control_cost_weight

    def _get_obs(self):
        return self._get_self_obs() # Just return self's stuff

    def has_terminated(self):
        return self.healthy_z_height[0]  < self.data.qpos[2] < self.healthy_z_height[1]

    def control_cost(self, action):
        return self.control_cost_weight * np.sum(np.square(self.data.ctrl))