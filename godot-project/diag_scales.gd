extends SceneTree

func _initialize() -> void:
	var new_scene: PackedScene = load("res://Scenes/Character/character_enemy.tscn")
	var old_scene: PackedScene = load("res://Scenes/Character/character_enemy_old.tscn")
	_report("NEW", new_scene)
	_report("OLD", old_scene)
	quit()

func _report(label: String, packed: PackedScene) -> void:
	var root := packed.instantiate()
	get_root().add_child(root)
	var skels := _find_all(root, "Skeleton3D")
	print("=== ", label, " ===")
	print("skeletons: ", skels.size())
	for s in skels:
		print("  skeleton path: ", s.get_path(), "  global scale: ", s.global_transform.basis.get_scale())
		var top := Vector3.ZERO
		var bottom := Vector3.ZERO
		var first := true
		for i in s.get_bone_count():
			var p: Vector3 = s.global_transform * s.get_bone_global_pose(i).origin
			if first:
				top = p
				bottom = p
				first = false
			else:
				top = top.max(p)
				bottom = bottom.min(p)
		print("    bone world AABB: ", bottom, " .. ", top, "  height=", top.y - bottom.y)
	var aabb := AABB()
	var has := false
	for m in _find_all(root, "MeshInstance3D"):
		if m.mesh == null or not m.is_visible_in_tree():
			continue
		var box: AABB = m.global_transform * m.mesh.get_aabb()
		if not has:
			aabb = box
			has = true
		else:
			aabb = aabb.merge(box)
	print("  visible mesh world AABB: ", aabb, "  size=", aabb.size)
	root.queue_free()

func _find_all(n: Node, cls: String) -> Array:
	var out := []
	if n.is_class(cls):
		out.append(n)
	for c in n.get_children():
		out.append_array(_find_all(c, cls))
	return out
