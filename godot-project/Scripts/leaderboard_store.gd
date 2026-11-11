extends RefCounted

## JSON file used by the in-game and HTML leaderboards.
const FILE_NAME := "leaderboard.json"

## Editor builds keep the file at the project root. Export builds keep it
## beside the executable so the event machine can read and write it.
static func get_path() -> String:
	if OS.has_feature("editor"):
		return ProjectSettings.globalize_path("res://" + FILE_NAME)
	return OS.get_executable_path().get_base_dir().path_join(FILE_NAME)

## Reads every saved entry in save order. A missing or malformed file is
## treated as an empty leaderboard.
static func read_entries() -> Array[Dictionary]:
	var path := get_path()
	if not FileAccess.file_exists(path):
		return []

	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_warning("Could not open leaderboard file: %s" % path)
		return []

	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if not parsed is Dictionary:
		return []

	var raw_entries: Variant = parsed.get("entries", [])
	if not raw_entries is Array:
		return []

	var entries: Array[Dictionary] = []
	for raw_entry in raw_entries:
		if raw_entry is Dictionary:
			entries.append((raw_entry as Dictionary).duplicate(true))
	return entries

## Reads entries sorted by score descending. Ties keep their save order.
static func read_ranked_entries() -> Array[Dictionary]:
	var entries := read_entries()
	var indexed: Array[Dictionary] = []
	for index in entries.size():
		indexed.append({"entry": entries[index], "order": index})

	indexed.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var score_a := float(a["entry"].get("score", 0.0))
		var score_b := float(b["entry"].get("score", 0.0))
		if not is_equal_approx(score_a, score_b):
			return score_a > score_b
		return int(a["order"]) < int(b["order"])
	)

	var ranked: Array[Dictionary] = []
	for item in indexed:
		ranked.append(item["entry"])
	return ranked

## Appends one entry and writes atomically through a temporary file.
static func save_entry(entry: Dictionary) -> bool:
	var entries := read_entries()
	entries.append(entry.duplicate(true))
	return _write_entries(entries)

static func _write_entries(entries: Array[Dictionary]) -> bool:
	var path := get_path()
	var temp_path := path + ".tmp"

	var file := FileAccess.open(temp_path, FileAccess.WRITE)
	if file == null:
		push_error("Could not write leaderboard file: %s" % temp_path)
		return false

	file.store_string(JSON.stringify({"entries": entries}, "\t"))
	file.flush()
	file.close()

	var error := DirAccess.rename_absolute(temp_path, path)
	if error != OK:
		# Windows cannot always replace an existing destination atomically.
		DirAccess.remove_absolute(path)
		error = DirAccess.rename_absolute(temp_path, path)

	if error != OK:
		push_error("Could not replace leaderboard file: %s" % path)
		return false

	return true
