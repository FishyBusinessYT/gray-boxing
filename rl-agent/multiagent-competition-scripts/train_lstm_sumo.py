import gym
import gym_compete
import torch as th
from torch import nn
import numpy as np
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

"""
REPLICACIÓN DE POLÍTICA LSTM PARA SUMO HUMANOIDE (SB3-CONTRIB)

Este script demuestra cómo replicar la arquitectura exacta de TensorFlow utilizada en
el repositorio original de 'gym-compete' para los agentes de Sumo.

ARQUITECTURA REPLICADA:
1. MLP de Entrada: Una capa densa de 128 unidades con ReLU.
2. Capa Recurrente: Una celda LSTM de 128 unidades.
3. Desacoplamiento: Actor (pi) y Crítico (vf) tienen redes COMPLETAMENTE independientes.
4. Normalización: Observaciones y retornos normalizados con clip de 5.0.
"""

class SumoSingleAgentWrapper(gym.Wrapper):
    """
    Wrapper para convertir un entorno multi-agente en uno de un solo agente.
    
    SB3 no soporta entornos multi-agente nativamente. Este wrapper:
    - Filtra la observación para devolver solo la del agente seleccionado.
    - Maneja al oponente como un agente estático (acciones de ceros).
    """
    def __init__(self, env, agent_index=0):
        super().__init__(env)
        self.agent_index = agent_index
        # Redefinimos los espacios para que SB3 vea solo los de un agente
        self.observation_space = env.observation_space.spaces[agent_index]
        self.action_space = env.action_space.spaces[agent_index]

    def reset(self, **kwargs):
        # El entorno original devuelve una tupla (obs_agente0, obs_agente1)
        obs = self.env.reset(**kwargs)
        return obs[self.agent_index]

    def step(self, action):
        # Preparamos acciones para ambos agentes
        actions = [None, None]
        actions[self.agent_index] = action
        # El oponente simplemente se queda quieto
        actions[1 - self.agent_index] = np.zeros(self.env.action_space.spaces[1-self.agent_index].shape)
        
        obs, rewards, done, info = self.env.step(actions)
        # Devolvemos solo lo relevante para el agente que estamos entrenando
        return obs[self.agent_index], rewards[self.agent_index], done, info[self.agent_index]


class SumoFeaturesExtractor(BaseFeaturesExtractor):
    """
    EXTRACTOR DE CARACTERÍSTICAS (MLP ANTES DEL LSTM)
    
    En SB3-Contrib, 'net_arch' define las capas DESPUÉS del LSTM.
    Para poner capas ANTES del LSTM (como en el repo original), usamos un Custom Extractor.
    """
    def __init__(self, observation_space, features_dim=128):
        # features_dim será el tamaño de la entrada para el LSTM
        super().__init__(observation_space, features_dim)
        self.mlp = nn.Sequential(
            nn.Linear(observation_space.shape[0], features_dim),
            nn.ReLU(),
        )

    def forward(self, observations):
        return self.mlp(observations)


def train_lstm():
    # 1. Creación del entorno envuelto
    def make_env():
        env = gym.make("sumo-humans-v0")
        return SumoSingleAgentWrapper(env)

    # 2. Vectorización y Normalización
    # DummyVecEnv es necesario para VecNormalize
    venv = DummyVecEnv([make_env])
    # VecNormalize es el equivalente SB3 al 'normalize=True' del repo original
    venv = VecNormalize(venv, norm_obs=True, norm_reward=True, clip_obs=5.0)

    # 3. Configuración detallada de la arquitectura Recurrente
    policy_kwargs = dict(
        # Inyectamos nuestra capa MLP inicial (128, ReLU)
        features_extractor_class=SumoFeaturesExtractor,
        features_extractor_kwargs=dict(features_dim=128),
        
        # IMPORTANTE: Desactivar el compartido del extractor para que 
        # el Actor y el Crítico tengan su propio MLP de entrada independiente.
        share_features_extractor=False,
        
        # Configuración del LSTM
        lstm_hidden_size=128,  # Tamaño de la celda oculta
        n_lstm_layers=1,       # Número de capas LSTM apiladas
        
        # IMPORTANTE: Desactivar el compartido del LSTM para que
        # Actor y Crítico tengan memorias temporales separadas.
        shared_lstm=False,
        enable_critic_lstm=True,
        
        # net_arch=[] significa que NO habrá capas MLP adicionales después del LSTM
        net_arch=[],
        activation_fn=nn.ReLU,
    )

    # 4. Inicialización del Algoritmo
    model = RecurrentPPO(
        "MlpLstmPolicy",
        venv,
        policy_kwargs=policy_kwargs,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,      # Cuántos pasos recolectar antes de actualizar
        batch_size=64,     # Tamaño del minibatch para el entrenamiento del LSTM
        n_epochs=10,       # Cuántas veces pasar por los datos recolectados
    )

    print("Iniciando entrenamiento: Política LSTM Humanoides Sumo...")
    model.learn(total_timesteps=1000000)
    
    # Guardado de modelo y estadísticas de normalización
    model.save("sumo_lstm_policy")
    venv.save("sumo_lstm_vecnormalize.pkl")

if __name__ == "__main__":
    train_lstm()
