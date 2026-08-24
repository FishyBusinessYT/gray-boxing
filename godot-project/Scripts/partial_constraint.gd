extends BoneAttachment3D

@export_enum(
    "neck_head",
    "l_shoulder_shoulder", "l_shoulder_elbow", "l_elbow_wrist", "l_wrist_hand",
    "r_shoulder_elbow", "r_elbow_wrist", "r_wrist_hand", "l_shoulder_hip",
    "r_shoulder_hip", "l_hip_hip", "l_hip_knee", "l_knee_ankle", "l_ankle_heel",
    "l_ankle_toe", "r_hip_knee", "r_knee_ankle", "r_ankle_heel", "r_ankle_toe",
    ) var direction_key: String
@export var controller: PlayerController

@export var disabled := false
@export var bone_axis := Vector3.UP

func _process(_delta: float) -> void:
    if disabled: return
    if not controller.directions.has(direction_key): return
    if controller.directions[direction_key] == Vector3.ZERO: return

    var target_dir: Vector3 = controller.directions[direction_key]
    var current_dir: Vector3 = global_transform.basis * bone_axis
    var correction: Quaternion = Quaternion(current_dir, target_dir)

    DebugDraw3D.draw_arrow(
        global_position, global_position + target_dir, Color.RED, 0.01
    )
    DebugDraw3D.draw_arrow(
        global_position, global_position + current_dir, Color.GREEN, 0.01
    )
    DebugDraw3D.draw_arrow(
        global_position, global_position+bone_axis, Color.BLUE, 0.01
    )


    #quaternion = correction * quaternion
    var current_quat: Quaternion = global_transform.basis.get_rotation_quaternion()
    var new_quat: Quaternion = correction * current_quat

    global_transform.basis = Basis(new_quat)
