Me voy a inspirar en [este](https://arxiv.org/abs/1710.03748) paper

# Modelo standing
Este debe ser el espacio de observaciones de mi modelo. Para esto voy a excluir la posicion $x,y$ y la rotacion del torso. Al trabajar con boxeo, tendria que incluir la posicion del torso para que sepa donde esta dentro del ring, y querria normalizar las posiciones respecto al ring. Normalizarlas entre 0 y 1 asi solo tiene que aprender el upper bound.

Los joints que tengo de mas respecto a [Humanoid-v4](https://github.com/openai/gym/blob/master/gym/envs/mujoco/humanoid_v4.py) son:
 - 3 para el cuello
 - 3 por cada muñeca
 - 3 por cada talon
 - 1 extra por cada hombro, para poder rotarlo

