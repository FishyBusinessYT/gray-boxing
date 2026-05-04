import gymnasium as gym
from stable_baselines3 import PPO

# 1. Crear entorno con render
env = gym.make("Humanoid-v5", render_mode="human")

# 2. Cargar modelo
model = PPO.load("./ppo_humanoid_final")

# 3. Resetear entorno
obs, _ = env.reset()

# 4. Loop de simulación
while True:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        print(terminated, truncated)
        obs, _ = env.reset()