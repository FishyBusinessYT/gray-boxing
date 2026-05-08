import mujoco
from pathlib import Path

ROOT_DIR = Path(__file__).parents[1].resolve()

model = mujoco.MjModel.from_xml_path(str(ROOT_DIR / "assets/mujoco_envs/openai_based.xml"))

# 1. Ver todas las masas con sus nombres
for i in range(model.nbody):
    nombre = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, i)
    masa = model.body_mass[i]
    print(f"Cuerpo: {nombre} | Masa: {masa:.4f} kg")