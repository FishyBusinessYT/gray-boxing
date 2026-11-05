extends RigidBody3D

@export var skeleton: Skeleton3D
@export var bone_name: String

var bone_idx: int

func _ready() -> void:
    bone_idx = skeleton.find_bone(bone_name)
    body_entered.connect(_on_body_entered)

func _physics_process(_delta: float) -> void:
    global_transform = get_parent().global_transform


func _on_body_entered(body: Node) -> void:
    print("Hit: ", body.name)
