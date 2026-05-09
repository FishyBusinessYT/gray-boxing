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
En un momento tuvo un reward > 3.0e+03, el problema es que parece haber tenido una explosion de gradiente por culpa de un mal clipping
ep_len_mean 258
ep_rew_mean 2.35e+03
Quizas tenga que haber reducido el lr mas veces. Solo se redujo 1 vez

### LSTMPolicy
Entrena ~10 veces mas lento que la MlpPolicy, y en el episodio 500k, si hubiera valido mas la pena, hubiera tenido un reward equivalente al de 5M en la MlpPolicy

# Diseño de entornos en mujoco
- Ponerle un poco de friccion al plano del piso, con 1 parece alcanzar
- Parece que cuando el actuador intenta superar al limite del joint(como lo que hacia con el -140,140 en las rodillas del old_agent), explota numericamente o la gradiente se satura ya que todos los valores entre 0 y -140 no producen un cambio en la posicion

Escale al modelo de 4.75 a 1.425

abs_z y abs_y estan arriba, abs_x esta abajo

Evaluacion
Los evaluo corriendolos 1M de epochs y viendo su max reward y ep length:
- OpenAI original: 719.2 pero creo que se midio mal y deberian ser 500
- Modelo basal: 147
- Modelo con doble de fuerza excepto en brazos: 376
- Modelo con triple de fuerza excepto en brazos: 752
# TODOs
### Training
TODO: If I'll use SB3, I'll need to change the storage checkpoints so that they also store the .pkl
TODO: More frecuent storage of the best model