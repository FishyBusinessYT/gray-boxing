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
        g = self._agents["a1_"]
        torso_z = self.data.qpos[g["qpos_ids"][2]]  # z del freejoint
        return not (self.healthy_z_height[0] < torso_z < self.healthy_z_height[1])

    def calculate_rewards(self) -> dict[str, float]:
        rewards = {}
        for prefix, g in self._agents.items():
            torso_body_id = g["body_ids"][0]  # a1_torso o a2_torso

            # Uprightness: componente Z del eje Z local del torso en frame global
            torso_z_axis = self.data.xmat[torso_body_id, 8]

            # Z position (ya usas g["qpos_ids"][2] en has_terminated, igual aquí)
            torso_z = self.data.qpos[g["qpos_ids"][2]]
            is_healthy = self.healthy_z_height[0] < torso_z < self.healthy_z_height[1]

            reward = self.healthy_reward if is_healthy else 0.0

            if is_healthy:
                upright_reward = self.upright_weight * max(0, torso_z_axis)
                reward += upright_reward

                height_error = abs(torso_z - self.target_height) / self.target_height
                height_reward = self.height_weight * np.exp(-10.0 * height_error)
                reward += height_reward

                ctrl = self.data.ctrl[g["actuator_ids"]]
                joint_dist = np.mean(np.square(ctrl))
                reward -= 0.1 * joint_dist

            ctrl = self.data.ctrl[g["actuator_ids"]]
            ctrl_cost = self.control_cost_weight * np.sum(ctrl ** 2)
            reward -= ctrl_cost

            rewards[prefix] = reward

        return rewards
