from gymnasium.envs.registration import register

register(
    id="StandingHumanoid",
    entry_point="src.envs.standing_humanoid_env:StandingHumanoidEnv",
    max_episode_steps=1000,
)

register(
    id="MultiHumanoidStanding",
    entry_point="src.envs.multiagent.multiagent_standing_env:MultiHumanoidStandingEnv",
    max_episode_steps=1000,
)