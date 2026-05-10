import xmltodict
from pathlib import Path
from boxing_env_building import create_ropes

ROOT_DIR = Path(__file__).parent.parent
with open(ROOT_DIR / "assets/mujoco_envs/boxing_ring.xml", "r") as f:
    data = xmltodict.parse(f.read())

boxing_env_with_ropes = create_ropes(data)

with open(ROOT_DIR / "assets/mujoco_envs/boxing_ring_with_ropes.xml", "w") as f:
    f.write(xmltodict.unparse(boxing_env_with_ropes, pretty=True, short_empty_elements=True))