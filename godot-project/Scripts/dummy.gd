extends RigidBody3D


enum shapes {
    RChest,
    LChest,
    Abdomen,
    Head,
}

func _on_hit(_a: RID, _b: Node, _c, local_shape_index: int) -> void:
    match local_shape_index:
        shapes.RChest:
            print('RChest')
        shapes.LChest:
            print('LChest')
        shapes.Abdomen:
            print('Abdomen')
        shapes.Head:
            print('Head')
