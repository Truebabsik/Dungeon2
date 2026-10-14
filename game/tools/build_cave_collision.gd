extends SceneTree

# Генерация коллизии оболочки пещеры из блока породы (задача T2r-b1).
#
# Запуск (headless, из корня репозитория):
#   Godot\Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#       --script res://tools/build_cave_collision.gd
#
# Что делает:
#   1. грузит res://assets/cave_gate.glb и берёт ArrayMesh первого MeshInstance3D;
#   2. заливает его треугольники в ConcavePolygonShape3D;
#   3. сохраняет ресурсом res://assets/cave_gate_collision.res (бинарный .res:
#      94 425 вершины текстом в .tscn делали бы файл нечитаемым);
#   4. печатает число треугольников и AABB формы и меша.
#
# ЗАВИСИМОСТЬ, КОТОРУЮ НЕЛЬЗЯ ЗАБЫВАТЬ: форма — производная от res://assets/cave_gate.glb.
# Поменял блок (build_cave_gate.py) — запусти этот инструмент заново. Иначе гейт
# res://tests/level_check.gd упадёт на проверке «коллизия оболочки»: она требует, чтобы
# число треугольников trimesh и AABB формы совпадали с мешем Cave (level_check.gd, check_gate_cave_collision).
# Провал там тихий по ощущениям: сцена выглядит нормально, краснеет одна строка.
#
# Вердикт — код возврата: 0 зелено, 2 блок не загрузился или ресурс не сохранился.

const CAVE_GLB_PATH := "res://assets/cave_gate.glb"
const OUT_PATH := "res://assets/cave_gate_collision.res"
const EXIT_OK := 0
const EXIT_BROKEN := 2

var _done := false


# Вся работа и печать — в первом _process: в _initialize наследника SceneTree
# вывод теряется, await process_frame — дедлок (docs/agents/constraints.md §3).
func _process(_delta: float) -> bool:
	if _done:
		return true
	_done = true
	quit(_build())
	return true


func _build() -> int:
	var packed := load(CAVE_GLB_PATH) as PackedScene
	if packed == null:
		push_error("генерация коллизии: не загрузился %s" % CAVE_GLB_PATH)
		return EXIT_BROKEN
	var instance := packed.instantiate()
	var mesh := first_mesh(instance)
	instance.free()
	if mesh == null:
		push_error("генерация коллизии: в %s нет MeshInstance3D с ArrayMesh" % CAVE_GLB_PATH)
		return EXIT_BROKEN
	var faces := mesh.get_faces()
	if faces.size() == 0 or faces.size() % 3 != 0:
		push_error("генерация коллизии: get_faces() дал %d вершин, это не набор треугольников" % faces.size())
		return EXIT_BROKEN
	var shape := ConcavePolygonShape3D.new()
	shape.set_faces(faces)
	var err := ResourceSaver.save(shape, OUT_PATH)
	if err != OK:
		push_error("генерация коллизии: ResourceSaver.save вернул %d для %s" % [err, OUT_PATH])
		return EXIT_BROKEN
	print("генерация коллизии: %s" % OUT_PATH)
	print("ok: форма собрана из %s: треугольников %d" % [CAVE_GLB_PATH, faces.size() / 3])
	print("ok: AABB формы %s" % str(faces_aabb(faces)))
	print("ok: AABB меша  %s" % str(mesh.get_aabb()))
	return EXIT_OK


# Первый ArrayMesh в поддереве инстанса — тот же поиск, что делает гейт (first_mesh_instance).
func first_mesh(node: Node) -> Mesh:
	if node is MeshInstance3D:
		var mesh := (node as MeshInstance3D).mesh
		if mesh is ArrayMesh:
			return mesh
	for child in node.get_children():
		var found := first_mesh(child)
		if found != null:
			return found
	return null


# AABB всех вершин набора точек.
func faces_aabb(faces: PackedVector3Array) -> AABB:
	var box := AABB(faces[0], Vector3.ZERO)
	for v in faces:
		box = box.expand(v)
	return box
