import copy
import random
from stable_baselines3.common.callbacks import BaseCallback

class SelfPlayCallback(BaseCallback):
    """
    Actualiza periódicamente la policy del oponente con un checkpoint
    del agente actual. Mantiene un pool de checkpoints pasados para
    evitar que el agente solo aprenda a ganarle a su versión más reciente.

    Parámetros:
        update_freq:    timesteps entre actualizaciones del oponente
        pool_size:      cuántos checkpoints pasados conservar
        sample_recent:  probabilidad de usar el checkpoint más reciente
                        (vs uno aleatorio del pool)
    """

    def __init__(
        self,
        update_freq:   int   = 100_000,
        pool_size:     int   = 5,
        sample_recent: float = 0.5,
        verbose:       int   = 0,
    ):
        super().__init__(verbose)
        self.update_freq  = update_freq
        self.pool_size = pool_size
        self.sample_recent = sample_recent
        self._policy_pool: list = []   # checkpoints congelados
        self._last_update: int  = 0

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_update >= self.update_freq:
            self._update_opponent()
            self._last_update = self.num_timesteps
        return True

    def _update_opponent(self):
        # Congelar una copia de la policy actual
        frozen = copy.deepcopy(self.model.policy)
        frozen.set_training_mode(False)
        self._policy_pool.append(frozen)

        # Mantener el pool acotado (FIFO)
        if len(self._policy_pool) > self.pool_size:
            self._policy_pool.pop(0)

        # Elegir qué checkpoint asignar como oponente
        opponent = self._sample_opponent()
        self.training_env.env_method("set_opponent", opponent)

        if self.verbose >= 1:
            print(
                f"[SelfPlay] t={self.num_timesteps:,} — "
                f"pool={len(self._policy_pool)} checkpoints, "
                f"opponent={'latest' if opponent is self._policy_pool[-1] else 'random'}"
            )

    def _sample_opponent(self):
        """
        Con probabilidad sample_recent usa el checkpoint más reciente;
        si no, elige uno al azar del pool.
        """
        if len(self._policy_pool) == 1:
            return self._policy_pool[-1]

        if random.random() < self.sample_recent:
            return self._policy_pool[-1]
        else:
            return random.choice(self._policy_pool[:-1])