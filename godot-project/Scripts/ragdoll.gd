extends PhysicalBoneSimulator3D

@export var controller_skeleton: Skeleton3D
@export var linear_stiffness: float = 200.0
@export var linear_damping: float = 10.0

var bones: Array[PhysicalBone3D] = []

func _ready() -> void:
	bones.assign(get_children().filter(func(c): return c is PhysicalBone3D))
	physical_bones_start_simulation(["Arm.L", "Arm.R"])
	#physical_bones_start_simulation()

func _physics_process(delta: float) -> void:
	for b in bones:
		var target_pos: Vector3 = (
			controller_skeleton.global_transform *
			controller_skeleton.get_bone_global_pose(b.get_bone_id())
		).origin

		var current_pos := b.global_position
		var diff := target_pos - current_pos

		var force := (
			linear_stiffness * diff
			- linear_damping * b.linear_velocity
		)

		# impulse = force * dt
		b.apply_central_impulse(force * delta)
