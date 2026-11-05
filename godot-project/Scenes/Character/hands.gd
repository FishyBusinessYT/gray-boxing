extends RigidBody3D

const BodyPartScript := preload("res://Scripts/body_part.gd")

## Skeleton that drives this hand.
@export var skeleton: Skeleton3D
## Bone this hand follows.
@export var bone_name: String

## Impact force (mass * relative speed) required before the hit deals damage.
@export var minimum_impact_force: float = 1.0
## Damage dealt per unit of impact force.
@export var damage_per_force: float = 1.0
## Maximum damage a single hit can deal, regardless of impact force.
@export var maximum_damage: float = 100.0

var bone_idx: int

var _previous_position: Vector3
var _tracked_velocity: Vector3

func _ready() -> void:
	bone_idx = skeleton.find_bone(bone_name)
	_previous_position = global_position
	body_entered.connect(_on_body_entered)

func _physics_process(delta: float) -> void:
	global_transform = get_parent().global_transform

<<<<<<< HEAD
	# The parent bone moves this body by teleporting it, so the physics engine
	# does not report the punch speed. Derive it from the movement instead.
	if delta > 0.0:
		_tracked_velocity = (global_position - _previous_position) / delta
	_previous_position = global_position

func _on_body_entered(body: Node) -> void:
	var part := body as BodyPartScript
	if part == null:
		return

	var impact_force := _calculate_impact_force(part)
	if impact_force < minimum_impact_force:
		return

	var damage := minf(impact_force * damage_per_force, maximum_damage)
	part.apply_damage(damage, self)

func _calculate_impact_force(part: BodyPartScript) -> float:
	var relative_velocity := _tracked_velocity - part.linear_velocity
	return mass * relative_velocity.length()
=======
func _on_body_entered(body: Node) -> void:
    print('AAAAAAHHAAAAAAAAAAAAAAAAAAAA')
    print("Hit: ", body.name)
>>>>>>> d72073802dbbf283254bc179bb78c9e6e895066a
