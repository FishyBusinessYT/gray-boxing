import mujoco

model = mujoco.MjModel.from_xml_path("./assets/mujoco_envs/boxing_ring.xml")

for i in range(model.nsite):
    print(model.site(i).name)