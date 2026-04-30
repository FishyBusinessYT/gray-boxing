import time
import numpy as np
import mujoco
import mujoco.viewer

# ── CONFIG ────────────────────────────────────────────────────────────────────

MODEL_PATH = "../character.xml"  # Asegúrate de que la ruta sea correcta

HOLD_TIME = 0.5  # Tiempo de espera en cada extremo (reducido para fluidez)
SPEED = 40.0  # Velocidad de movimiento en GRADOS por segundo
DT = 0.01  # Paso de tiempo para el loop de control/render

# None = todos. O una lista: ["act_neck", "act_shoulder_l"]
ONLY = None

# ── Actuadores (nombre, min_deg, max_deg) ─────────────────────────────────────
# Basado exactamente en tu XML <actuator>
ACTUATORS = [
    ("act_neck", -60, 60),
    ("act_shoulder_l", -90, 90),
    ("act_elbow_l", 0, 145),
    ("act_wrist_l", -45, 45),
    ("act_shoulder_r", -90, 90),
    ("act_elbow_r", 0, 145),
    ("act_wrist_r", -45, 45),
    ("act_pelvis", -70, 70),
    ("act_hip_l", -70, 70),
    ("act_knee_l", 0, 140),
    ("act_ankle_l", -20, 45),
    ("act_hip_r", -70, 70),
    ("act_knee_r", 0, 140),
    ("act_ankle_r", -20, 45),
]


# ─────────────────────────────────────────────────────────────────────────────

def move_actuator(model, data, viewer, act_name, ctrl_min, ctrl_max):
    act_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, act_name)
    if act_id == -1:
        print(f"  [!] '{act_name}' no encontrado en el XML, saltando.")
        return

    def go_to(target, label):
        current = data.ctrl[act_id]
        dist = target - current
        # Calculamos pasos basados en la velocidad (grados/s)
        steps = max(1, int(abs(dist) / (SPEED * DT)))

        for i in range(steps + 1):
            if not viewer.is_running(): return

            # Interpolación lineal simple
            data.ctrl[act_id] = current + (dist * (i / steps))

            mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(DT)

        # Mantener la posición
        t_end = time.time() + HOLD_TIME
        while time.time() < t_end and viewer.is_running():
            mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(DT)

        print(f"    {label:>10}  {target: .1f}°")

    print(f"\n[ACT] {act_name}  rango: [{ctrl_min}°, {ctrl_max}°]")
    go_to(0.0, "neutral")
    go_to(ctrl_min, "mínimo")
    go_to(ctrl_max, "máximo")
    go_to(0.0, "neutral")


def main():
    try:
        model = mujoco.MjModel.from_xml_path(MODEL_PATH)
        data = mujoco.MjData(model)
    except Exception as e:
        print(f"Error cargando el modelo: {e}")
        return

    # Filtrar actuadores si ONLY no es None
    actuators_to_test = ACTUATORS
    if ONLY is not None:
        actuators_to_test = [a for a in ACTUATORS if a[0] in ONLY]

    print("Iniciando visualizador MuJoCo...")
    with mujoco.viewer.launch_passive(model, data) as viewer:
        # Configuración de cámara inicial
        viewer.cam.distance = 5.0
        viewer.cam.lookat = [0, 0, 1.5]
        viewer.cam.elevation = -20

        print("Estabilizando física...")
        for _ in range(100):
            mujoco.mj_step(model, data)
            viewer.sync()

        for act_name, ctrl_min, ctrl_max in actuators_to_test:
            if not viewer.is_running():
                break
            move_actuator(model, data, viewer, act_name, ctrl_min, ctrl_max)

        print("\n✓ Secuencia completa. Cierra la ventana para salir.")
        while viewer.is_running():
            mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(DT)


if __name__ == "__main__":
    main()