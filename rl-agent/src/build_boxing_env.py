import xmltodict
from pathlib import Path
from boxing_env_building import create_ropes, add_agents

ROOT_DIR = Path(__file__).parent.parent
with open(ROOT_DIR / "assets/mujoco_envs/boxing_ring_template.xml", "r") as f:
    data = xmltodict.parse(f.read())

#boxing_env = create_ropes(data)
boxing_env = add_agents(data, ROOT_DIR / "assets/mujoco_envs/agent.xml")

with open(ROOT_DIR / "assets/mujoco_envs/boxing_ring_with_agents.xml", "w") as f:
    f.write(xmltodict.unparse(boxing_env, pretty=True, short_empty_elements=True))
