extends Node3D

signal game_ended

func _on_timer_timeout() -> void:
    emit_signal('game_ended')
