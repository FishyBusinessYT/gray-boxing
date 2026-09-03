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
@export var process_order: int = 0

var _skel: Skeleton3D
var _bone_idx: int = -1
var _parent_idx: int = -1
var _last_local_quat: Quaternion = Quaternion.IDENTITY
var _initialized := false

func _ready():
    _skel = get_skeleton()
    _bone_idx = get_bone_idx()
    _parent_idx = _skel.get_bone_parent(_bone_idx)
    process_priority = process_order
    # Arrancar desde la pose local real de reposo (twist inicial correcto)
    _last_local_quat = _skel.get_bone_pose(_bone_idx).basis.get_rotation_quaternion()

func _process(_delta: float) -> void:
    if disabled or _skel == null or _bone_idx == -1:
        return
    if not controller.directions.has(direction_key):
        return
    var target_dir_world: Vector3 = controller.directions[direction_key]
    if target_dir_world == Vector3.ZERO:
        return
    target_dir_world = target_dir_world.normalized()
    
    # Orientación actual del padre, YA actualizada este frame (gracias a process_priority)
    var parent_quat_skel: Quaternion
    if _parent_idx == -1:
        parent_quat_skel = Quaternion.IDENTITY
    else:
        parent_quat_skel = _skel.get_bone_global_pose(_parent_idx).basis.get_rotation_quaternion()

    var skel_world_quat: Quaternion = _skel.global_transform.basis.get_rotation_quaternion()
    var parent_to_world_quat: Quaternion = skel_world_quat * parent_quat_skel

    # Target expresado EN EL FRAME DEL PADRE (una sola conversión, sin ida y vuelta)
    var target_dir_local: Vector3 = parent_to_world_quat.inverse() * target_dir_world
    target_dir_local = target_dir_local.normalized()

    if direction_key == "r_knee_ankle":
        print("rotating")
        basis = basis * Basis(Vector3.UP, deg_to_rad(-90))

    # Dirección actual según NUESTRO propio estado recordado (no leído del engine)
    var current_dir_local: Vector3 = (_last_local_quat * bone_axis).normalized()

    # Swing incremental, calculado directamente en espacio local. Sin conjugaciones.
    var correction_local: Quaternion = Quaternion(current_dir_local, target_dir_local)
    var new_local_quat: Quaternion = correction_local * _last_local_quat

    _skel.set_bone_pose_rotation(_bone_idx, Basis(new_local_quat))
    _last_local_quat = new_local_quat
