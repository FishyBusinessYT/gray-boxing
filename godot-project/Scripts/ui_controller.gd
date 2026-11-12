extends Control

const RoundLog := preload("res://Scripts/round_log.gd")

@export var main_menu_scene: PackedScene
@export var pause_menu_scene: PackedScene
@export var game_over_scene: PackedScene
@export var leaderboard_scene: PackedScene
@export var game_scene: PackedScene

@onready var main_menu: Node = main_menu_scene.instantiate()
@onready var pause_menu: Node = pause_menu_scene.instantiate()
@onready var game_over: Node = game_over_scene.instantiate()
@onready var leaderboard: Node = leaderboard_scene.instantiate()

func _ready() -> void:
    # The menus must keep reacting while the round is paused.
    process_mode = Node.PROCESS_MODE_ALWAYS

    main_menu.name = 'UI-NODE'
    pause_menu.name = 'UI-NODE'
    game_over.name = 'UI-NODE'
    leaderboard.name = 'UI-NODE'

    main_menu.get_node('VBoxContainer/Start game').connect(
        'pressed', start_game
        )
    main_menu.get_node('VBoxContainer/Leaderboard').connect(
        'pressed', to_leaderboard
        )
    main_menu.get_node('VBoxContainer/Exit game').connect(
        'pressed', exit_game
        )

    pause_menu.get_node('ButtonsPanel/VBoxContainer/Resume game').connect(
        'pressed', start_game
        )
    pause_menu.get_node('ButtonsPanel/VBoxContainer/Restart game').connect(
        'pressed', restart_game
        )
    pause_menu.get_node('ButtonsPanel/VBoxContainer/Main menu').connect(
        'pressed', to_main_menu
        )

    game_over.get_node('ButtonsPanel/VBoxContainer/Restart game').connect(
        'pressed', restart_game
        )
    game_over.get_node('ButtonsPanel/VBoxContainer/Main menu').connect(
        'pressed', to_main_menu
        )

    leaderboard.get_node('Main menu').connect('pressed', to_main_menu)

    to_main_menu()

func pause_game() -> void:
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))

    if get_node_or_null('Game'):
        get_node('Game').pause_round()

    add_child(pause_menu)

func start_game() -> void:
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))

    get_tree().paused = false

    if get_node_or_null('Game'):
        get_node('Game').resume_round()
        return

    var game: Node = game_scene.instantiate()
    game.get_node('PauseButton').connect('pressed', pause_game)
    game.connect('game_ended', to_game_over)
    add_child(game)

func restart_game() -> void:
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))

    get_tree().paused = false
    _clear_game()
    start_game()

func exit_game() -> void:
    get_tree().root.propagate_notification(NOTIFICATION_WM_CLOSE_REQUEST)
    get_tree().quit()

func to_main_menu() -> void:
    get_tree().paused = false

    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))

    _clear_game()
    add_child(main_menu)

func to_game_over() -> void:
    get_tree().paused = false

    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))

    _clear_game()

    game_over.get_node('Score').text = 'Puntaje  %d' % roundi(
        RoundLog.total_damage
        )
    add_child(game_over)

func to_leaderboard() -> void:
    get_tree().paused = false

    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))

    _clear_game()
    add_child(leaderboard)

## Frees the running round so a restart never leaves a stale scene behind.
func _clear_game() -> void:
    var game := get_node_or_null('Game')
    if game == null:
        return

    remove_child(game)
    game.queue_free()
