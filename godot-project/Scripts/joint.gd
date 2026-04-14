extends Generic6DOFJoint3D

@export var direction_key: String
@export var controller: PlayerController
@export var disable: bool


func _physics_process(delta: float) -> void:
    if disable: return

    if controller.directions.has(direction_key) and controller.directions[direction_key] != Vector3.ZERO:
        var current_dir: Vector3 = global_transform.basis * Vector3(0, 1, 0)
        var target_dir: Vector3 = controller.directions[direction_key]

        var correction: Quaternion = Quaternion(current_dir, target_dir)

        # Convert quaternion to axis-angle, then to angular velocity
        var axis: Vector3 = correction.get_axis()
        var angle: float = correction.get_angle()
        var angular_velocity = axis * angle * 0.25 / delta

        set('angular_motor_x/target_velocity', angular_velocity.x)
        set('angular_motor_y/target_velocity', angular_velocity.y)
        set('angular_motor_z/target_velocity', angular_velocity.z)
