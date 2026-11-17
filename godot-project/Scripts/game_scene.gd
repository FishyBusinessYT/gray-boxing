extends Node3D

enum RoundState { PLAYING, PAUSED, GAME_OVER }

const RoundLog := preload("res://Scripts/round_log.gd")

signal game_ended

## Name stored in the leaderboard until the name-entry screen exists.
@export var player_name: String = "Jugador"
## Length of one round, in seconds.
@export var round_duration: float = 60.0

## Explicit round state. The UI controller drives the transitions.
var round_state: RoundState = RoundState.PLAYING

@onready var round_timer: Timer = $Timer

func _ready() -> void:
	# The UI stays active during pause, so the round opts back into pausing.
	process_mode = Node.PROCESS_MODE_PAUSABLE
	RoundLog.reset()
	$DamageHUD.refresh_score()
	round_timer.wait_time = round_duration
	round_timer.start()
	round_state = RoundState.PLAYING

## Stops the timer and the physics simulation until resume_round() runs.
func pause_round() -> void:
	if round_state != RoundState.PLAYING:
		return
	round_state = RoundState.PAUSED
	get_tree().paused = true

## Continues the round with the time that was left when it paused.
func resume_round() -> void:
	if round_state != RoundState.PAUSED:
		return
	round_state = RoundState.PLAYING
	get_tree().paused = false

## Ends the round once and reports the final score through game_ended.
func end_round() -> void:
	if round_state == RoundState.GAME_OVER:
		return
	round_state = RoundState.GAME_OVER
	round_timer.stop()
	RoundLog.finish_run(player_name)
	emit_signal('game_ended')

func _on_timer_timeout() -> void:
	end_round()
