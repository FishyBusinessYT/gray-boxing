from .multiagent_base_env import MultiAgentEnv
import numpy as np

class MultiHumanoidStandingEnv(MultiAgentEnv):
    def __init__(self, *args,
                 healthy_z_height=(1.2, 1.9),
                 target_height=1.625,
                 control_cost_weight=0.001,
                 upright_weight=10.0,
                 height_weight=5.0,
                 healthy_reward=5.0,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.healthy_z_height = healthy_z_height
        self.control_cost_weight = control_cost_weight
        self.upright_weight = upright_weight
        self.height_weight = height_weight
        self.target_height = target_height
        self.healthy_reward = healthy_reward

    # Check if any of the agents has terminated
    def has_terminated(self) -> bool:
        for prefix, g in self._agents.items():
            torso_z = self.data.qpos[g["qpos_ids"][2]]  # z del freejoint
            if torso_z < self.healthy_z_height[0]:  # cayó
                return True

    def calculate_rewards(self) -> dict[str, float]:
        rewards = {}
        for prefix, g in self._agents.items():
            # 2. Penalización por esfuerzo de actuadores
            ctrl = self.data.ctrl[g["actuator_ids"]]
            ctrl_cost = self.control_cost_weight * np.sum(ctrl ** 2)

            # 3. Premio por estar vivo y upright
            torso_z = self.data.qpos[g["qpos_ids"][2]]
            alive = self.healthy_reward if torso_z > self.healthy_z_height[0] else 0.0

            rewards[prefix] = alive + - ctrl_cost

        return rewards