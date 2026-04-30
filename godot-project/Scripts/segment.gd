extends RigidBody3D

@export_enum(
    "neck_head",
    "l_shoulder_shoulder",
    "l_shoulder_elbow",
    "l_elbow_wrist",
    "l_wrist_hand",
    "r_shoulder_elbow",
    "r_elbow_wrist",
    "r_wrist_hand",
    "l_shoulder_hip",
    "r_shoulder_hip",
    "l_hip_hip",
    "l_hip_knee",
    "l_knee_ankle",
    "l_ankle_heel",
    "l_ankle_toe",
    "r_hip_knee",
    "r_knee_ankle",
    "r_ankle_heel",
    "r_ankle_toe",
    ) var direction_key: String
@export var controller: PlayerController
@export var disable: bool
@export var gain: int

@export var bone_axis := Vector3.UP


func _physics_process(_delta: float) -> void:
    if disable: return
    if not controller.directions.has(direction_key): return
    if controller.directions[direction_key] == Vector3.ZERO: return

    var current_dir: Vector3 = global_transform.basis * bone_axis
    var target_dir: Vector3 = controller.directions[direction_key]
    var correction: Quaternion = Quaternion(current_dir, target_dir)

    # Convert quaternion to axis-angle, then to angular velocity
    var axis: Vector3 = correction.get_axis()
    var angle: float = correction.get_angle()
    angular_velocity = axis * angle * gain
