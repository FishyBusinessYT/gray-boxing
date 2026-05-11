import gymnasium as gym
import src.envs
from src.envs.multiagent.self_play_env_wrapper import SelfPlayWrapper

env = gym.make("MultiHumanoidStanding")
obs = env.reset()

a1_indices = env.unwrapped._agents["a1_"]
a2_indices = env.unwrapped._agents["a2_"]

a1_torso_z = env.unwrapped.data.qpos[a1_indices["qpos_ids"][2]]
a2_torso_z = env.unwrapped.data.qpos[a2_indices["qpos_ids"][2]]

print(f"Initial a1_torso_z: {a1_torso_z}")
print(f"Initial a2_torso_z: {a2_torso_z}")
print(f"Healthy Z range: {env.unwrapped.healthy_z_height}")
print(f"Has terminated: {env.unwrapped.has_terminated()}")
