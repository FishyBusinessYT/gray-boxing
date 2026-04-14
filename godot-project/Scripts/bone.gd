extends RigidBody3D

@export var direction_key: String
@export var controller: PlayerController
@export var disable: bool


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _physics_process(delta: float) -> void:
    if disable: return
    if not controller.directions.has(direction_key): return
    if controller.directions[direction_key] == Vector3.ZERO: return

    var current_dir: Vector3 = global_transform.basis * Vector3(0, 1, 0)
    var target_dir: Vector3 = controller.directions[direction_key]
    var correction: Quaternion = Quaternion(current_dir, target_dir)

    # Convert quaternion to axis-angle, then to angular velocity
    var axis: Vector3 = correction.get_axis()
    var angle: float = correction.get_angle()
    angular_velocity = axis * angle * 0.5 / delta
