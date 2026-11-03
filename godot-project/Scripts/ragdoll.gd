extends PhysicalBoneSimulator3D

@export var controller_skeleton: Skeleton3D
@export var linear_stiffness: float = 200.0
@export var linear_damping: float = 10.0
@export var angular_stiffness: float = 100.0
@export var angular_damping: float = 5.0

var bones: Array[PhysicalBone3D] = []

func _ready() -> void:
	bones.assign(get_children().filter(func(c): return c is PhysicalBone3D))
	physical_bones_start_simulation()

func _physics_process(delta: float) -> void:
	for b in bones:
		var target: Transform3D = (
			controller_skeleton.global_transform
			* controller_skeleton.get_bone_global_pose(b.get_bone_id())
			* b.body_offset
		)

		# Resorte lineal (Hooke): F = k*x - c*v
		var pos_error := target.origin - b.global_position
		var force := linear_stiffness * pos_error - linear_damping * b.linear_velocity
		b.apply_central_impulse(force * delta)

		# Resorte angular (Hooke): α = k*θ - c*ω
		var err_q := target.basis.get_rotation_quaternion() * b.global_transform.basis.get_rotation_quaternion().inverse()
		if err_q.w < 0.0:
			err_q = -err_q # camino más corto
		var rot_error := err_q.get_axis() * err_q.get_angle() # eje * ángulo

		var angular_accel := angular_stiffness * rot_error - angular_damping * b.angular_velocity
		b.angular_velocity += angular_accel * delta
