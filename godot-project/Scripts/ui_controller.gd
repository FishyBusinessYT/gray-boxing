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
@onready var game: Node = game_scene.instantiate()

func _ready() -> void:
    main_menu.name = 'UI-NODE'
    pause_menu.name = 'UI-NODE'
    game_over.name = 'UI-NODE'
    leaderboard.name = 'UI-NODE'

    main_menu.get_node('ButtonsPanel/VBoxContainer/Start game').connect(
        'pressed', to_game
        )
    main_menu.get_node('ButtonsPanel/VBoxContainer/Leaderboard').connect(
        'pressed', to_leaderboard
        )
    main_menu.get_node('ButtonsPanel/VBoxContainer/Exit game').connect(
        'pressed', get_tree().quit
        )

    pause_menu.get_node('ButtonsPanel/VBoxContainer/Resume game').connect(
        'pressed', to_game
        )
    pause_menu.get_node('ButtonsPanel/VBoxContainer/Restart game').connect(
        'pressed', to_game
        )
    pause_menu.get_node('ButtonsPanel/VBoxContainer/Main menu').connect(
        'pressed', to_main_menu
        )

    game_over.get_node('ButtonsPanel/VBoxContainer/Restart game').connect(
        'pressed', to_game
        )
    game_over.get_node('ButtonsPanel/VBoxContainer/Main menu').connect(
        'pressed', to_main_menu
        )

    leaderboard.get_node('Main menu').connect('pressed', to_main_menu)

    game.get_node('PauseButton').connect('pressed', pause_game)
    game.get_node('EndGameButton').connect('pressed', to_game_over)

    to_main_menu()

func pause_game():
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))
    add_child(pause_menu)

func to_main_menu():
    remove_child(get_node('UI-NODE'))
    if get_node_or_null('Game'):
        remove_child(get_node('Game'))
    add_child(main_menu)

func to_game():
    if get_node_or_null('UI-NODE'):
        remove_child(get_node('UI-NODE'))
    if not get_node_or_null('Game'):
        add_child(game)

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
