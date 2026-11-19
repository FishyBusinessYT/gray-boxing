extends Control

## Reads leaderboard.json once per visit and lists the entries by score.

const LeaderboardStore := preload("res://Scripts/leaderboard_store.gd")
const ROW_FONT_SIZE := 22
const EMPTY_TEXT := "Sin puntajes todavía"

@onready var rows: VBoxContainer = $PanelContainer/VBoxContainer/MarginContainer/PanelContainer/ScrollContainer/VBoxContainer

## Rebuilds the visible rows from the persisted file. Call when the
## leaderboard is entered; the file is not watched or polled.
func refresh() -> void:
	for child in rows.get_children():
		child.free()

	var entries := LeaderboardStore.read_ranked_entries()
	if entries.is_empty():
		_add_row(EMPTY_TEXT)
		return

	for entry in entries:
		var entry_name := str(entry.get("name", "Jugador"))
		var score := roundi(float(entry.get("score", 0.0)))
		_add_row("%s: %d pts" % [entry_name, score])

func _add_row(text: String) -> void:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", ROW_FONT_SIZE)
	rows.add_child(label)
