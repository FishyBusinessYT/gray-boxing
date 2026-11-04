extends AnimationPlayer

## Animations the enemy can randomly choose from.
@export var attack_animations: PackedStringArray = [
	"Hook/mixamo_com",
	"Jab Cross/mixamo_com",
	"Uppercut/mixamo_com",
]

## Animation played between attacks. Leave empty to stay on the attack's last frame.
@export var idle_animation: StringName = &"Fighting Idle/mixamo_com"

## Random range (in seconds) to wait between the end of one attack and the next.
@export_range(0.0, 30.0, 0.1) var min_interval: float = 1.0
@export_range(0.0, 30.0, 0.1) var max_interval: float = 3.0

var _rng := RandomNumberGenerator.new()
var _valid_attacks: Array[StringName] = []
var _valid_idle := false

func _ready() -> void:
	_rng.randomize()

	for animation in attack_animations:
		if has_animation(animation):
			_valid_attacks.append(animation)
		else:
			push_warning("Attack animation '%s' not found on %s." % [animation, name])

	if _valid_attacks.is_empty():
		push_warning("No valid attack animations on %s." % name)
		return

	_valid_idle = idle_animation != &"" and has_animation(idle_animation)
	_run()

func _run() -> void:
	var low := minf(min_interval, max_interval)
	var high := maxf(min_interval, max_interval)

	while is_inside_tree():
		if _valid_idle:
			_play_looped(idle_animation)

		await get_tree().create_timer(_rng.randf_range(low, high)).timeout
		if not is_inside_tree():
			return

		_play_attack(_valid_attacks[_rng.randi_range(0, _valid_attacks.size() - 1)])
		await animation_finished

func _play_looped(animation: StringName) -> void:
	get_animation(animation).loop_mode = Animation.LOOP_LINEAR
	play(animation)

func _play_attack(animation: StringName) -> void:
	# Attacks must play once, otherwise animation_finished never fires.
	get_animation(animation).loop_mode = Animation.LOOP_NONE
	play(animation)
