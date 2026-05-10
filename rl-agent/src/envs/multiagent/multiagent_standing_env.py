from .multiagent_base_env import MultiAgentEnv
import numpy as np

class MultiHumanoidStandingEnv(MultiAgentEnv):
    def __init__(self, *args,
                 healthy_z_height=(1.0, 1.7),
                 target_height=1.425,
                 control_cost_weight=0.001,
                 upright_weight=10.0,
                 height_weight=5.0,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.healthy_z_height = healthy_z_height
        self.control_cost_weight = control_cost_weight
        self.upright_weight = upright_weight
        self.height_weight = height_weight
        self.target_height = target_height

    # Check if any of the agents has terminated
    def has_terminated(self) -> bool:
        for prefix, g in self._agents.items():
            torso_z = self.data.qpos[g["qpos_ids"][2]]  # z del freejoint
            if torso_z < 0.5:  # cayó
                return True
        return any(hp <= 0.0 for hp in self._hp.values())

    def calculate_rewards(self) -> dict[str, float]:
        rewards = {}
        for prefix, g in self._agents.items():
            # 1. Velocidad de avance (qvel DOF 0 = vx del freejoint)
            forward_vel = self.data.qvel[g["dof_ids"][0]]

            # 2. Penalización por esfuerzo de actuadores
            ctrl = self.data.ctrl[g["actuator_ids"]]
            ctrl_cost = 0.1 * np.sum(ctrl ** 2)

            # 3. Premio por estar vivo y upright
            torso_z = self.data.qpos[g["qpos_ids"][2]]
            alive = self.healthy_reward if torso_z > 0.5 else 0.0

            # 4. Fuerzas de contacto externas (daño recibido)
            contact_forces = self.data.cfrc_ext[g["body_ids"]]
            contact_cost = 5e-4 * np.sum(np.clip(contact_forces, -1, 1) ** 2)

            rewards[prefix] = alive + forward_vel - ctrl_cost - contact_cost

        return rewards