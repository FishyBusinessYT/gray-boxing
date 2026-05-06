En el paper de [OpenAI](https://arxiv.org/pdf/1710.03748) usan LSTM

rl-baselines3-zoo tiene hiperparámetros ya configurados para SB3, incluido en problemas como Humanoid-v4

El problema con SB3 es que no tiene un LSTMPolicy, pero sb3-contrib si lo tiene(recurrencia normal, creo que no es una red contextual)
### MlpPolicy
Con la MlpPolicy, tuve estos resultados en el epoch 6M
- ep_len_mean: 157
- ep_rew_mean: 1.26e+03

A los 10M
- ep_len_mean: 244
- ep_rew_mean: 2.11e+03
### LrScheduler - MLP
En un momento tuvo un reward de 3.5e+03, el problema es que parece haber tenido una explosion de gradiente por culpa de un mal clipping

| rollout/           |          |
|    ep_len_mean     | 258      |
|    ep_rew_mean     | 2.35e+03 |
Quizas tenga que haber reducido el lr mas veces. Solo se redujo 1 vez
### LSTMPolicy
Entrena ~10 veces mas lento que la MlpPolicy, y en el episodio 500k, si hubiera valido mas la pena, hubiera tenido un reward equivalente al de 5M en la MlpPolicy