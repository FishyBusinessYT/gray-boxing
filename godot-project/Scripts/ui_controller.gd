extends Control

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

func pause_game():
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))
    add_child(pause_menu)

func start_game():
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))

    if not get_node_or_null('Game'):
        var game: Node = game_scene.instantiate()
        game.get_node('PauseButton').connect('pressed', pause_game)
        game.connect('game_ended', to_game_over)
        add_child(game)

func restart_game():
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))
    if get_node_or_null('Game'):
        get_node('Game').queue_free()
        remove_child(get_node('Game'))
    start_game()

func exit_game():
    get_tree().root.propagate_notification(NOTIFICATION_WM_CLOSE_REQUEST)
    get_tree().quit()

func to_main_menu():
    remove_child(get_node('UI-NODE'))
    if get_node_or_null('Game'):
        remove_child(get_node('Game'))
    add_child(main_menu)

func to_game_over():
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))
    if get_node_or_null('Game'):
        remove_child(get_node('Game'))
    add_child(game_over)

func to_leaderboard():
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))
    if get_node_or_null('Game'):
        remove_child(get_node('Game'))
    add_child(leaderboard)
