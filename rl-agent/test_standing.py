import mujoco
import mujoco.viewer
import numpy as np
import time

# Cargar el modelo
model = mujoco.MjModel.from_xml_path('character.xml')
data = mujoco.MjData(model)

# Iniciar el visualizador
with mujoco.viewer.launch_passive(model, data) as viewer:
    # Resetear a la pose de la keyframe
    mujoco.mj_resetDataKeyframe(model, data, 0)
    
    print("Iniciando prueba de estabilidad en TIEMPO REAL...")
    print("Comandando rodillas a 0 (Extensión total esperada)")

    # Identificadores de actuadores (basado en el orden en XML)
    # act_knee_l es el actuador 19, act_knee_r es el 22
    
    while viewer.is_running():
        step_start = time.time()

        # Comandamos 0 a todos. Con ctrlrange simétrico, esto debería ser la pose neutral.
        data.ctrl[:] = 0.0

        # Simular un paso
        mujoco.mj_step(model, data)

        # Actualizar visualizador
        viewer.sync()

        # --- TELEMETRÍA ---
        if int(data.time * 10) > int((data.time - model.opt.timestep) * 10): # Cada 0.1s
             # qpos[23] es knee_l, qpos[30] es knee_r (aproximadamente)
             # Mejor buscar por nombre para estar seguros
             knee_l_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, 'knee-joint-l')
             knee_r_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, 'knee-joint-r')
             pelvis_y_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, 'pelvis_y')
             
             angle_l = np.rad2deg(data.qpos[model.jnt_qposadr[knee_l_id]])
             angle_r = np.rad2deg(data.qpos[model.jnt_qposadr[knee_r_id]])
             tilt_side = np.rad2deg(data.qpos[model.jnt_qposadr[pelvis_y_id]])
             
             print(f"T: {data.time:.2f}s | Rodilla L: {angle_l:5.1f}° | Rodilla R: {angle_r:5.1f}° | Tilt Lateral: {tilt_side:5.1f}° | Altura: {data.qpos[2]:.2f}m")

        # --- CONTROL DE FPS (TIEMPO REAL) ---
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)
