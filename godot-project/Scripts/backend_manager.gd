extends Node

var process_id := -1


func _ready() -> void:
    var exe_name := "backend.exe" if OS.get_name() == "Windows" else "backend"
    var py_path := OS.get_executable_path().get_base_dir().path_join(exe_name)

    if OS.has_feature("editor"):
        py_path = ProjectSettings.globalize_path("res://").path_join("backend")

    if FileAccess.file_exists(py_path):
        process_id = OS.create_process(py_path, [], true)
    else:
        print('File at ' + py_path + ' not found! Check the README for more information.')
        await get_tree().create_timer(0.3).timeout
        get_tree().quit(1)

func _notification(what: int) -> void:
    if what == NOTIFICATION_WM_CLOSE_REQUEST and process_id != -1:
        OS.kill(process_id)
