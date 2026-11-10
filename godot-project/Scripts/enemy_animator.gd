extends AnimationPlayer

## Animation played between attacks. Leave empty to stay on the attack's last frame.
var idle_animation: StringName = &"Fighting Idle/mixamo_com"

## Random range (in seconds) to wait between the end of one attack and the next.
var min_interval: float = 1.0
var max_interval: float = 4.0

var _rng := RandomNumberGenerator.new()
var _valid_attacks: Array[StringName] = []

func _ready() -> void:
    _rng.randomize()
    for animation in get_animation_list():
        if animation != idle_animation:
            _valid_attacks.append(animation)
    _on_animation_finished('')

func _on_animation_finished(anim_name: StringName) -> void:
    if anim_name == idle_animation:
        return

    _play_looped(idle_animation)
    await get_tree().create_timer(_rng.randf_range(min_interval, max_interval)).timeout
    _play_attack(_valid_attacks[_rng.randi_range(0, _valid_attacks.size() - 1)])

func _play_looped(animation: StringName) -> void:
    get_animation(animation).loop_mode = Animation.LOOP_LINEAR
    play(animation)

func _play_attack(animation: StringName) -> void:
    # Attacks must play once, otherwise animation_finished never fires.
    get_animation(animation).loop_mode = Animation.LOOP_NONE
    play(animation)
