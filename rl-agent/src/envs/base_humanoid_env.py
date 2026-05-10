import numpy as np
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box
from gymnasium import utils
import mujoco
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

# self.data.cinert gives center of mass positions and inertia
def mass_center(model, data):
    mass = np.expand_dims(model.body_mass, axis=1)
    xpos = data.xipos
    return (np.sum(mass * xpos, axis=0) / np.sum(mass))[0:2].copy()

class BaseHumanoidEnv(MujocoEnv):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 100
    }

    def __init__(self,
            frame_skip=5,  # 2ms * 5 = 10ms. 100 actions per second
            exclude_torso_horizontal_position=True,
            healthy_reward=20.0,
            reset_noise_scale=1e-2,
            **kwargs
        ):
        super().__init__(str(ROOT_DIR / "assets/mujoco_envs/agent.xml"), frame_skip, None, **kwargs) # None observation space

        # Action space: normalized [-1, 1] for RL stability
        action_size = self.model.nu
        self.action_space = Box(low=-1.0, high=1.0, shape=(action_size,), dtype=np.float32)

        # Exclude torso horizontal position if requested
        self.exclude_torso_horizontal_position = exclude_torso_horizontal_position

        # Calculate dynamic observation size
        obs_size = self._get_self_obs().size
        self.observation_space = Box(low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float32)

        self.healthy_reward = healthy_reward
        self.reset_noise_scale = reset_noise_scale

    def _get_self_obs(self):
        # Position and Velocity
        position = self.data.qpos.flat.copy()
        velocity = self.data.qvel.flat.copy()

        # Com inertia and velocity (cinert is 10-dim, cvel is 6-dim per body)
        # Exclude worldbody (index 0)
        com_inertia = self.data.cinert[1:].flat.copy()
        com_velocity = self.data.cvel[1:].flat.copy()

        # Actuator forces (exclude freejoint DOF: first 6)
        actuator_forces = self.data.qfrc_actuator[6:].flat.copy()

        # External contact forces (exclude worldbody)
        external_contact_forces = self.data.cfrc_ext[1:].flat.copy()

        if self.exclude_torso_horizontal_position:
            position = position[2:] # Exclude xy

        return np.concatenate([
            position,
            velocity,
            com_inertia,
            com_velocity,
            actuator_forces,
            external_contact_forces
        ]).astype(np.float32)

    def step(self, action):
        # 1. Scale action from [-1, 1] to degrees (ctrlrange)
        ctrlrange = self.model.actuator_ctrlrange
        low, high = ctrlrange.T
        scaled_action = low + (action + 1.0) * 0.5 * (high - low)
        scaled_action = np.clip(scaled_action, low, high)

        # 2. Simulate
        self.do_simulation(scaled_action, self.frame_skip)

        # 3. Gather state
        observation = self._get_obs()
        terminated = self.has_terminated()

        # 4. Calculate rewards (delegated to child classes)
        reward, info = self.calculate_reward(action)

        return observation, reward, terminated, False, info

    def _get_obs(self):
        raise NotImplementedError

    def calculate_reward(self, action):
        raise NotImplementedError

    def has_terminated(self):
        raise NotImplementedError

    def reset_model(self):
        mujoco.mj_resetDataKeyframe(self.model, self.data, 0) # Reset the model to the zero keyframe
        mujoco.mj_forward(self.model, self.data) # Forward pass to update the positions based on the joints rotations
        # Add noise
        qpos = self.init_qpos + self.np_random.uniform(low=-self.reset_noise_scale, high=self.reset_noise_scale, size=self.model.nq)
        self.set_state(qpos, self.init_qvel)
        # Return the observation
        return self._get_obs()