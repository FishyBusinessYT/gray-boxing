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
            frame_skip=5,  # 2ms * = 10ms. 100 actions per second
            exclude_torso_horizontal_position=True,
            healthy_reward=10,
            reset_noise_scale=1e-2,
            **kwargs
        ):
        super().__init__(str(ROOT_DIR / "character.xml"), frame_skip, None, **kwargs) # None observation space

        self.observation_space = Box(low=-np.inf, high=np.inf, shape=(444,), dtype=np.float32)

        self.exclude_torso_horizontal_position = exclude_torso_horizontal_position
        self.healthy_reward = healthy_reward
        self.reset_noise_scale = reset_noise_scale

    # Separation used for future environments where the obs will also contain the other agent's obs
    def _get_obs(self):
        raise Exception("Not implemented yet.")

    def _get_self_obs(self):
        # Taken from OpenAI's humanoid model
        position = self.data.qpos.flat.copy() # Positions/rotations of each joint(positions AND quaternion rotations for the free joint)
        velocity = self.data.qvel.flat.copy() # Same as qpos but with velocities
        com_inertia = self.data.cinert.flat.copy() # Spatial velocity vector of each rigidbody(defined by <body>)
        com_velocity = self.data.cvel.flat.copy() # Mass and inertia of each rigidbody
        actuator_forces = self.data.qfrc_actuator.flat.copy()
        external_contact_forces = self.data.cfrc_ext.flat.copy()

        if self.exclude_torso_horizontal_position:
            position = position[2:] # Exclude xy

        return np.concatenate([position, velocity, com_inertia, com_velocity, actuator_forces, external_contact_forces]).astype(np.float32)

    def control_cost(self, action):
        raise Exception("Not implemented yet.")

    def has_terminated(self):
        raise Exception("Not implemented yet.")

    def step(self, action):
        self.do_simulation(action, self.frame_skip)

        observation = self._get_obs()
        ctrl_cost = self.control_cost(action)
        reward = self.healthy_reward - ctrl_cost
        terminated = self.has_terminated()
        info = {
            "ctrl_cost": ctrl_cost,
        }

        #if self.render_mode == "human":
        #    self.render()
        return observation, reward, terminated, False, info # obs, reward, terminated, truncated, info

    def reset_model(self):
        mujoco.mj_resetDataKeyframe(self.model, self.data, 0) # Reset the model to the zero keyframe
        mujoco.mj_forward(self.model, self.data) # Forward pass to update the positions based on the joints rotations
        # Add noise
        qpos = self.init_qpos + self.np_random.uniform(low=-self.reset_noise_scale, high=self.reset_noise_scale, size=self.model.nq)
        self.set_state(qpos, self.init_qvel)
        # Return the observation
        return self._get_obs()