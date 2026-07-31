extends PhysicalBoneSimulator3D

@export var controller_skeleton: Skeleton3D
@export var skeleton: Skeleton3D

@export var linear_stiffness: float  # = 1200
@export var linear_damping: float  # = 40

@export var angular_stiffness: float  # = 4000
@export var angular_damping: float  # = 80

var bones
func _ready() -> void:
    physical_bones_start_simulation()
    bones = get_children().filter(func(c): return c is PhysicalBone3D)

func _physics_process(delta: float) -> void:
    for b: PhysicalBone3D in bones:
        var target_transform: Transform3D = (
            controller_skeleton.global_transform *
            controller_skeleton.get_bone_global_pose(b.get_bone_id())
            )
        var current_transform: Transform3D = (
            global_transform *
            skeleton.get_bone_global_pose(b.get_bone_id())
        )

        var pos_diff: Vector3 = target_transform.origin - current_transform.origin
        var force: Vector3 = hookes_law(
            pos_diff,
            b.linear_velocity,
            linear_stiffness,
            linear_damping
        )
        b.linear_velocity += force * delta

        var rot_diff: Basis = (
            target_transform.basis *
            current_transform.basis.inverse()
        )
        var torque: Vector3 = hookes_law(
            rot_diff.get_euler(),
            b.angular_velocity,
            angular_stiffness,
            angular_damping
        )
        b.angular_velocity += torque * delta

func hookes_law(displacement: Vector3, current_vel: Vector3, stiffness: float, damping: float):
    return (stiffness * displacement) - (damping * current_vel)
