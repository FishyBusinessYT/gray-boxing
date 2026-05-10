import numpy as np
import gymnasium as gym
from gymnasium.spaces import Box

class SelfPlayWrapper(gym.Env):
    """
    Envuelve MultiHumanoidEnv en una interfaz single-agent para SB3.

    El agente controlado ve [own_obs, opponent_obs] y controla solo sus actuadores.
    El oponente usa una policy congelada (o random si es None).

    La simetría es clave: ambos agentes ven [propio, ajeno] con el mismo orden,
    así la misma policy puede jugar desde cualquier slot.
    """
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, base_env, controlled: str = "a1_"):
        super().__init__()
        assert controlled in base_env.PREFIXES, f"Prefijo inválido: {controlled}"

        self.env = base_env
        self.controlled = controlled
        self.opponent = "a2_" if controlled == "a1_" else "a1_"

        # Policy del oponente — None = random
        self._opponent_policy = None

        # Espacios
        own_size = base_env.agent_obs_space.shape[0]
        self.observation_space = Box(
            low=-np.inf, high=np.inf,
            shape=(own_size * 2,),   # [own_obs | opponent_obs]
            dtype=np.float32,
        )
        self.action_space = base_env.agent_action_spaces[controlled]

        # Estado interno
        self._last_obs: dict | None = None

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_opponent(self, policy):
        """
        Asigna una nueva policy al oponente.
        Acepta cualquier objeto con .predict(obs) → (action, state).
        Si policy es None, el oponente actúa aleatoriamente.
        """
        self._opponent_policy = policy

    # ------------------------------------------------------------------
    # Gym interface
    # ------------------------------------------------------------------

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        obs_dict = self.env.reset_multi(seed=seed, options=options)
        self._last_obs = obs_dict
        return self._build_obs(obs_dict), {} # obs, info

    def step(self, action: np.ndarray):
        opp_action = self._get_opponent_action()

        actions = {
            self.controlled: action,
            self.opponent: opp_action,
        }
        obs_dict, rewards, terminated, truncated, info = self.env.step_multi(actions)
        self._last_obs = obs_dict

        obs    = self._build_obs(obs_dict)
        reward = rewards[self.controlled]
        return obs, reward, terminated, truncated, info

    def render(self):
        return self.env.render()

    def close(self):
        self.env.close()

    # ------------------------------------------------------------------
    # Interno
    # ------------------------------------------------------------------

    def _build_obs(self, obs_dict: dict) -> np.ndarray:
        """[own_obs | opponent_obs] — mismo orden para ambos agentes."""
        return np.concatenate([
            obs_dict[self.controlled],
            obs_dict[self.opponent],
        ]).astype(np.float32)

    def _get_opponent_action(self) -> np.ndarray:
        # Random action if there isn't an opponent policy
        if self._opponent_policy is None:
            return self.action_space.sample()

        # El oponente ve [su_obs | obs_del_controlado] — perspectiva simétrica
        opp_obs = np.concatenate([
            self._last_obs[self.opponent],
            self._last_obs[self.controlled],
        ]).astype(np.float32)

        action, _ = self._opponent_policy.predict(opp_obs, deterministic=False)
        return action