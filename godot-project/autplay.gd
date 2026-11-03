extends AnimationPlayer

## Name of the animation to play on start.
@export var animation_name: StringName = &""

func _ready() -> void:
	if animation_name == &"":
		push_warning("No animation selected on %s." % name)
		return

	if not has_animation(animation_name):
		push_warning("Animation '%s' not found on %s." % [animation_name, name])
		return

	# Force the animation to loop, regardless of its own loop setting.
	get_animation(animation_name).loop_mode = Animation.LOOP_LINEAR
	play(animation_name)
