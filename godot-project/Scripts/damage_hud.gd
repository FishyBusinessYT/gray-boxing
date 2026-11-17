extends CanvasLayer

const BodyPartScript := preload("res://Scripts/body_part.gd")
const RoundLog := preload("res://Scripts/round_log.gd")

## Round countdown shown under the total damage score.
@onready var countdown_timer: Timer = get_node_or_null("../Timer") as Timer

## Label in the top-right corner that shows the round's total damage.
@onready var score_label: Label = $DamageScore
## Label under the score that shows the remaining round time.
@onready var time_label: Label = $TimeLeft
## Full-screen container that owns the short-lived injury labels.
@onready var floating_root: Control = $FloatingLabels

var _last_seconds_left: int = -1

## How long an injury label stays on screen before it is freed, in seconds.
@export var float_duration: float = 1.1
## How far an injury label rises, in pixels.
@export var float_rise: float = 70.0

func _ready() -> void:
	for node in get_tree().get_nodes_in_group(BodyPartScript.GROUP):
		var part := node as BodyPartScript
		if part == null:
			continue
		part.injury_sustained.connect(_on_injury_sustained.bind(part))

	refresh_score()
	_update_time_left()

func _process(_delta: float) -> void:
	_update_time_left()

## Updates the countdown label only when the displayed second changes.
func _update_time_left() -> void:
	if countdown_timer == null:
		return

	var seconds_left := ceili(countdown_timer.time_left)
	if seconds_left == _last_seconds_left:
		return

	_last_seconds_left = seconds_left
	var minutes := floori(seconds_left / 60.0)
	var seconds := seconds_left % 60
	time_label.text = "Tiempo  %d:%02d" % [minutes, seconds]

## Syncs the top-right score with the round log.
func refresh_score() -> void:
	score_label.text = "DP TOTAL  %d" % roundi(RoundLog.total_damage)

func _on_injury_sustained(
		_segment: String,
		damage: float,
		injury: String,
		_source: Node,
		part: Node3D) -> void:
	refresh_score()
	_spawn_injury_label(part, injury, damage)

## Projects the hit part into screen space and pops a readable, short-lived
## label over it. Labels ignore the mouse so they never block gameplay input.
func _spawn_injury_label(part: Node3D, injury: String, damage: float) -> void:
	var camera := get_viewport().get_camera_3d()
	if camera == null or part == null:
		return

	var world_position := part.global_position + Vector3(0.0, 0.35, 0.0)
	if camera.is_position_behind(world_position):
		return

	var label := Label.new()
	label.text = "%s\n%d DP" % [injury, roundi(damage)]
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.size = Vector2(520.0, 56.0)
	label.add_theme_font_size_override("font_size", 20)
	label.add_theme_color_override("font_color", Color(1.0, 0.95, 0.75))
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	label.add_theme_constant_override("outline_size", 4)

	var screen_position := camera.unproject_position(world_position)
	screen_position += Vector2(-label.size.x * 0.5, -label.size.y)
	screen_position.x += randf_range(-24.0, 24.0)
	label.position = screen_position

	floating_root.add_child(label)

	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(
		label,
		"position",
		label.position + Vector2(0.0, -float_rise),
		float_duration
	).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.tween_property(
		label,
		"modulate:a",
		0.0,
		float_duration * 0.55
	).set_delay(float_duration * 0.45)
	tween.chain().tween_callback(label.queue_free)
