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

    # Construct the basis. TODO: Do it for the rest of the parts
    var basis = Basis(
        controller.directions["l_shoulder_shoulder"],
        controller.directions["l_shoulder_hip"] * (-1),
        controller.directions["l_shoulder_shoulder"].cross(controller.directions["l_shoulder_hip"] * (-1))
    )
    basis = basis.orthonormalized() # Apply Gram-Schmidt

    DebugDraw3D.draw_arrow(
        global_position, global_position + basis.x, Color.RED, 0.1
    )
    DebugDraw3D.draw_arrow(
        global_position, global_position + basis.y, Color.GREEN, 0.1
    )
    DebugDraw3D.draw_arrow(
        global_position, global_position + basis.z, Color.YELLOW, 0.1
    )

    global_transform.basis = Basis(basis)
