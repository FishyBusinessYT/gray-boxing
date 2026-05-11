import numpy as np
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box
from gymnasium import utils
import mujoco
from pathlib import Path

ROOT_DIR = Path(__file__).parents[3]

_JNT_NPOS = {0: 7, 1: 4, 2: 1, 3: 1}  # free, ball, slide, hinge
_JNT_NDOF = {0: 6, 1: 3, 2: 1, 3: 1}

def _build_agent_indices(model, prefix: str) -> dict:
    """Calcula los índices en los arrays globales de MuJoCo para un prefijo dado."""
    actuator_ids = np.array([
        i for i in range(model.nu)
        if mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i).startswith(prefix)
    ], dtype=np.intp)

    body_ids = np.array([
        i for i in range(model.nbody)
        if mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, i).startswith(prefix)
    ], dtype=np.intp)

    joint_ids = [
        i for i in range(model.njnt)
        if mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i).startswith(prefix)
    ]

    qpos_ids, dof_ids = [], []
    for jid in joint_ids:
        jtype = int(model.jnt_type[jid])
        qpos_ids.extend(range(int(model.jnt_qposadr[jid]), int(model.jnt_qposadr[jid]) + _JNT_NPOS[jtype]))
        dof_ids.extend(range(int(model.jnt_dofadr[jid]), int(model.jnt_dofadr[jid]) + _JNT_NDOF[jtype]))

    return {
        "actuator_ids": actuator_ids,
        "body_ids": body_ids,
        "qpos_ids": np.array(qpos_ids, dtype=np.intp),
        "dof_ids": np.array(dof_ids, dtype=np.intp),
    }

class MultiAgentEnv(MujocoEnv):
    """
    Shared env. Needs a wrapper for each agent.
    """

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 100
    }
    PREFIXES = ("a1_", "a2_")
    STARTING_HP = {
        "chest_left": 10,
        "chest_right": 10,
        "shoulder_left": 10,
        "shoulder_right": 10,
        "head": 10,
        "waist": 10,
        "hip": 10,
        "left_thigh": 10,
        "left_shin": 10,
        "left_foot": 10,
        "right_thigh": 10,
        "right_shin": 10,
        "right_foot": 10,
        "left_arm": 10,
        "left_forearm": 10,
        "left_hand": 10,
        "right_arm": 10,
        "right_forearm": 10,
        "right_hand": 10,
    }

    def __init__(self,
            frame_skip=5,  # 2ms * 5 = 10ms. 100 actions per second
            reset_noise_scale=1e-2,
            **kwargs
        ):
        self.reset_noise_scale = reset_noise_scale
        super().__init__(str(ROOT_DIR / "assets/mujoco_envs/boxing_ring_with_agents.xml"), frame_skip, None, **kwargs) # None observation space

        # Agent obs spaces and action spaces, wrapper handles concat
        self._agents = {p: _build_agent_indices(self.model, p) for p in self.PREFIXES}
        self._hp = {p: self.STARTING_HP for p in self.PREFIXES}

        obs_size = self._get_agent_obs("a1_").size
        self.agent_obs_space = Box(-np.inf, np.inf, shape=(obs_size,), dtype=np.float32)
        self.agent_action_spaces = {
            p: Box(-1.0, 1.0, shape=(len(info["actuator_ids"]),), dtype=np.float32)
            for p, info in self._agents.items()
        }

        # placeholder required by MujocoEnv, wrapper will set the true values
        self.observation_space = self.agent_obs_space
        self.action_space = self.agent_action_spaces["a1_"]

    ###############
    # Obs
    ###############

    def _get_agent_obs(self, prefix: str) -> np.ndarray:
        g = self._agents[prefix]
        position = self.data.qpos[g["qpos_ids"]].copy()
        velocity = self.data.qvel[g["dof_ids"]].copy()
        com_inertia = self.data.cinert[g["body_ids"]].flat.copy()
        com_velocity = self.data.cvel[g["body_ids"]].flat.copy()
        actuator_forces = self.data.qfrc_actuator[g["dof_ids"]].copy()
        external_contact_forces = self.data.cfrc_ext[g["body_ids"]].flat.copy()

        # Don't exclude torso position

        return np.concatenate([
            position, velocity, com_inertia, com_velocity,
            actuator_forces, external_contact_forces,
            [*self._hp[prefix].values()], # Maybe will throw non sub error
        ]).astype(np.float32)

    def _get_all_obs(self) -> dict[str, np.ndarray]:
        return {p: self._get_agent_obs(p) for p in self.PREFIXES}

    ####################
    # Step
    ####################

    # Does single-step physics applying both the agent's actions at once
    def step_multi(self, actions: dict[str, np.ndarray]):
        full_ctrl = self.data.ctrl.copy()

        for prefix, action in actions.items():
            g = self._agents[prefix]
            ctrlrange = self.model.actuator_ctrlrange[g["actuator_ids"]]
            low, high = ctrlrange.T
            full_ctrl[g["actuator_ids"]] = np.clip(
                low + (action + 1.0) * 0.5 * (high - low), low, high
            )

        self.do_simulation(full_ctrl, self.frame_skip)
        obs = self._get_all_obs()
        rewards = self.calculate_rewards()
        terminated = self.has_terminated()

        return obs, rewards, terminated, False, {}

    # Placeholder required by MujocoEnv
    def step(self, action):
        raise RuntimeError("Usá step_multi(). Este env no tiene interfaz single-agent.")

    ######################
    # Methods to implement
    ######################

    def calculate_rewards(self) -> dict[str, float]:
        raise NotImplementedError

    def has_terminated(self) -> bool:
        raise NotImplementedError

    ########################
    # Reset
    ########################

    # Placeholder required by Mujocoenv.reset()
    def _get_obs(self):
        return self._get_agent_obs("a1_")

    def reset_model(self):
        mujoco.mj_resetDataKeyframe(self.model, self.data, 0)
        mujoco.mj_forward(self.model, self.data)

        qpos = self.data.qpos.copy()
        for g in self._agents.values():
            qpos[g["qpos_ids"]] += self.np_random.uniform(
                -self.reset_noise_scale, self.reset_noise_scale,
                size=len(g["qpos_ids"]),
            )
        self.set_state(qpos, self.data.qvel.copy())
        return self._get_obs()

    def reset_multi(self, **kwargs):
        """Reset que devuelve observaciones para ambos agentes."""
        self._hp = {p: self.STARTING_HP for p in self.PREFIXES}
        super().reset(**kwargs)
        return self._get_all_obs()

    ######################
    # Interface
    ######################

    # TODO: set_hp interface