extends Node3D

const RoundLog := preload("res://Scripts/round_log.gd")

signal game_ended

## Name stored in the leaderboard until the name-entry screen exists.
@export var player_name: String = "Jugador"

func _ready() -> void:
    RoundLog.reset()

func _on_timer_timeout() -> void:
    RoundLog.finish_run(player_name)
    emit_signal('game_ended')
