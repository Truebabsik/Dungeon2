extends Node

const COLLISION_NAME := "Collision"
const WALL_GRID_NAME := "GridMapWall"
const FLOOR_GRID_NAME := "GridMapFloor"
const FLOOR_BODY_NAME := "Floor"


func _ready() -> void:
	build()


func build() -> void:
	var level := get_parent() as Node3D
	var container := Node3D.new()
	container.name = COLLISION_NAME
	add_child(container)
	build_walls(level, container)
	build_floor(level, container)
	build_modules(level, container)


func build_walls(level: Node3D, container: Node3D) -> void:
	var grid := level.get_node(WALL_GRID_NAME) as GridMap
	for cell in grid.get_used_cells():
		var visual := cell_visual_box(grid, cell)
		var body := make_body(container, "Wall_%d_%d_%d" % [cell.x, cell.y, cell.z], visual.get_center())
		add_box(body, Vector3.ZERO, visual.size)


func build_floor(level: Node3D, container: Node3D) -> void:
	var grid := level.get_node(FLOOR_GRID_NAME) as GridMap
	var body := make_body(container, FLOOR_BODY_NAME, Vector3.ZERO)
	for cell in grid.get_used_cells():
		var visual := cell_visual_box(grid, cell)
		add_box(body, visual.get_center(), visual.size)


func build_modules(level: Node3D, container: Node3D) -> void:
	var level_inverse := level.global_transform.affine_inverse()
	for child in level.get_children():
		var module := child as Node3D
		if module == null or module.scene_file_path == "":
			continue
		var meshes: Array[MeshInstance3D] = []
		collect_meshes(module, meshes)
		if meshes.is_empty():
			continue
		var body := make_body(container, "Module_" + module.name, Vector3.ZERO)
		for mesh_node in meshes:
			add_trimesh(body, mesh_node, level_inverse)


# Визуальный AABB одной ячейки в координатах Level: меш элемента библиотеки с ориентацией, сдвигом элемента и позицией ячейки.
func cell_visual_box(grid: GridMap, cell: Vector3i) -> AABB:
	var item := grid.get_cell_item(cell)
	var mesh := grid.mesh_library.get_item_mesh(item)
	var rot: Basis = grid.get_basis_with_orthogonal_index(grid.get_cell_item_orientation(cell))
	var item_xf := grid.mesh_library.get_item_mesh_transform(item)
	return (grid.transform * Transform3D(rot, grid.map_to_local(cell)) * item_xf) * mesh.get_aabb()


func collect_meshes(node: Node, out: Array[MeshInstance3D]) -> void:
	for child in node.get_children():
		var mesh_node := child as MeshInstance3D
		if mesh_node != null and mesh_node.mesh != null:
			out.append(mesh_node)
		collect_meshes(child, out)


func make_body(parent: Node3D, body_name: String, pos: Vector3) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = body_name
	body.position = pos
	parent.add_child(body)
	return body


func add_trimesh(body: StaticBody3D, mesh_node: MeshInstance3D, level_inverse: Transform3D) -> void:
	var faces: ConcavePolygonShape3D = mesh_node.mesh.create_trimesh_shape()
	var shape := CollisionShape3D.new()
	shape.shape = faces
	shape.transform = level_inverse * mesh_node.global_transform
	body.add_child(shape)


func add_box(body: StaticBody3D, center: Vector3, size: Vector3) -> void:
	var box := BoxShape3D.new()
	box.size = size
	var shape := CollisionShape3D.new()
	shape.shape = box
	shape.position = center
	body.add_child(shape)
