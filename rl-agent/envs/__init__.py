from gymnasium.envs.registration import register

register(
    id="StandingHumanoid",
    entry_point="envs.standing_humanoid_env:StandingHumanoidEnv",
    max_episode_steps=1000,
)
