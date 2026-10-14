extends SceneTree
# Каноническая проверка сжатого glb (скилл downscaling-glb-textures).
# Считает меши/тр., объединённый AABB и размеры текстур по слотам материала.
#
# Проверенные грабли headless (не повторять):
#   - НЕ использовать calc_loop_triangles() — в headless на импортированном glb виснет навсегда.
#     Тр. считаем через surface_get_arrays(s)[Mesh.ARRAY_INDEX].
#   - НЕ использовать await process_frame — в наследнике SceneTree это дедлок (цикл ждёт сам себя).
#   - НЕ использовать Timer-watchdog — таймеру нужны кадры, а при дедлоке их нет.
#   - print() в _initialize буферизуется и теряется при раннем quit(). Поэтому вся работа и печать —
#     в первом кадре _process, там stdout отдаётся штатно.
# Делаем: _initialize — только загрузка и add_child; _process (первый кадр) — обход, замер, печать, quit.
#
# Запуск из корня проекта (glb должен лежать ВНУТРИ проекта и быть прогнан через --import):
#   Godot\Godot_v4.7.2-stable_win64_console.exe --headless --path <папка проекта> --import
#   Godot\Godot_v4.7.2-stable_win64_console.exe --headless --path <папка проекта> --script res://check_glb.gd -- res://model.glb
#
# Код возврата: 0 успех, 1 ошибка (не загрузился / нет мешей).

const TEX_PROPS := [
	"albedo_texture",
	"metallic_roughness_texture",
	"metallic_texture",
	"roughness_texture",
	"normal_texture",
	"orm_texture",
]

var _scene: Node = null
var _started := false


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var path := "res://model.glb"
	if args.size() > 0 and args[0] != "":
		path = args[0]
	var packed := ResourceLoader.load(path)
	if packed == null or not (packed is PackedScene):
		push_error("не загрузился PackedScene: %s" % path)
		quit(1)
		return
	_scene = packed.instantiate()
	root.add_child(_scene)      # inside tree — global_transform считается в кадре


func _process(_dt: float) -> bool:
	if _started:
		return false
	_started = true

	var meshes := {}
	var insts := []
	_collect(_scene, meshes, insts)

	var total_tris := 0
	for me in meshes.keys():
		for s in range(me.get_surface_count()):
			var arr: Array = me.surface_get_arrays(s)
			var idx = arr[Mesh.ARRAY_INDEX]
			var vert = arr[Mesh.ARRAY_VERTEX]
			if idx != null:
				total_tris += idx.size() / 3
			elif vert != null:
				total_tris += vert.size() / 3

	var union := AABB()
	var first := true
	var slots := {}
	for inst in insts:
		var world: Transform3D = inst.global_transform
		var laabb: AABB = inst.get_aabb()
		for i in range(8):
			var c := world * laabb.get_endpoint(i)
			if first:
				union = AABB(c, Vector3.ZERO)
				first = false
			else:
				union = union.expand(c)
		_gather_tex(inst, slots)

	print("MESHES: %d" % meshes.size())
	print("MESHINSTANCES: %d" % insts.size())
	print("TRIANGLES: %d" % total_tris)
	print("AABB_SIZE: %s" % union.size)
	print("AABB_POS: %s" % union.position)
	for key in slots:
		print("TEX %s: %s" % [key, slots[key]])

	if meshes.is_empty() or total_tris <= 0:
		push_error("нет мешей/треугольников")
		quit(1)
		return false
	print("RESULT: OK")
	quit(0)
	return false


func _collect(node: Node, meshes: Dictionary, insts: Array) -> void:
	if node is MeshInstance3D and node.mesh != null:
		meshes[node.mesh] = true
		insts.append(node)
	for c in node.get_children():
		_collect(c, meshes, insts)


func _gather_tex(inst: MeshInstance3D, slots: Dictionary) -> void:
	for s in range(inst.get_surface_override_material_count()):
		var mat := inst.get_surface_override_material(s)
		if mat == null and inst.mesh != null and s < inst.mesh.get_surface_count():
			mat = inst.mesh.surface_get_material(s)
		if mat == null:
			continue
		for prop in TEX_PROPS:
			if not (prop in mat):
				continue
			var tex = mat.get(prop)
			if tex is Texture2D:
				var key := "%s[%d].%s" % [mat.resource_name, s, prop]
				if not slots.has(key):
					slots[key] = "%dx%d" % [tex.get_width(), tex.get_height()]
