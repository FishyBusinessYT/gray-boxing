import mujoco.viewer
from pathlib import Path

ROOT_DIR = Path(__file__).parents[1].resolve()

model = mujoco.MjModel.from_xml_path(str(ROOT_DIR / "assets/mujoco_envs/old_agent.xml"))
data = mujoco.MjData(model)
mujoco.viewer.launch(model, data)