extends RefCounted

const LeaderboardStore := preload("res://Scripts/leaderboard_store.gd")

## Total damage dealt during the current round.
static var total_damage: float = 0.0

## One entry per damaging hit, in hit order.
static var injuries: Array[Dictionary] = []

## Total damage per hit segment, for later displays and reports.
static var damage_by_segment: Dictionary = {}

static var _saved: bool = false

## Clears the round tally. Call when a new round starts.
static func reset() -> void:
	total_damage = 0.0
	injuries.clear()
	damage_by_segment.clear()
	_saved = false

## Tallies one damaging hit and its selected injury.
static func record_hit(segment: String, damage: float, injury: String) -> void:
	if damage <= 0.0 or injury.is_empty():
		return

	total_damage += damage
	damage_by_segment[segment] = (
		float(damage_by_segment.get(segment, 0.0)) + damage
	)

	injuries.append({
		"segment": segment,
		"dp": snappedf(damage, 0.01),
		"injury": injury,
	})

## Saves the current round as one leaderboard entry. A round is saved once;
## repeated calls after a successful finish do nothing.
static func finish_run(player_name: String) -> bool:
	if _saved:
		return false

	var safe_name := player_name.strip_edges()
	if safe_name.is_empty():
		safe_name = "Jugador"

	var entry := {
		"name": safe_name,
		"score": snappedf(total_damage, 0.01),
		"injuries": injuries.duplicate(true),
	}
	_saved = LeaderboardStore.save_entry(entry)
	return _saved
