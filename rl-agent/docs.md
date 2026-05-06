En el paper de [OpenAI](https://arxiv.org/pdf/1710.03748) usan LSTM

rl-baselines3-zoo tiene hiperparámetros ya configurados para SB3, incluido en problemas como Humanoid-v4

El problema con SB3 es que no tiene un LSTMPolicy, pero sb3-contrib si lo tiene(recurrencia normal, creo que no es una red contextual)
