extends SceneTree

# Headless-проверка уровня-сцены. Запуск:
# Godot_v4.7.2-stable_win64_console.exe --headless --path game --script res://tests/level_check.gd
# Вердикт — код возврата: 0 зелено, 1 провал проверки, 2 сцена не загрузилась или скрипт упал.

const LEVEL_SCENE := "res://level/level.tscn"
const CHARACTER_NAME := "Character"
const CHARACTER_PREFIX := "res://assets/kaykit_animations/"
const GRIDMAP_NAMES := ["GridMapWall", "GridMapFloor", "GridUpper"]
# 211 kaykit + 90 dungeon_pack/obj + 76 kaykit_resourcebits + 31 kaykit_adventurers
const GRIDMAP_LIBRARY_ITEMS := 408
const GRIDMAP_CELL_SIZE := Vector3(4, 4, 4)
const GRIDMAP_UPPER_NAME := "GridUpper"
const GRIDMAP_UPPER_Y := 4.0
const MODEL_PREFIX := "res://assets/kaykit/"
const MODEL_SUFFIX := ".gltf"
# Инстансы kaykit/*.gltf в сцене на момент правки: 26 (узлы MeshInstance3D пользователя сюда не входят).
const MODULES_EXPECTED := 26
const EXIT_OK := 0
const EXIT_FAIL := 1
const EXIT_BROKEN := 2
const CONTROLLER_SCRIPT := preload("res://level/character_controller.gd")
const CHARACTER_TYPE := "CharacterBody3D"
const CAMERA_NAME := "FPSCamera"
const TOP_CAMERA_NAME := "Camera3D"
# Высота глаз — локальная y камеры относительно origin Character (низ капсулы), решение пользователя 2.1–2.2 м.
const EYE_HEIGHT_MIN := 2.1
const EYE_HEIGHT_MAX := 2.2
const RANGER_NAME := "Ranger"
const RIG_NAME := "Rig_Medium_General"
const RIG_MESH_NAME := "Rig_Medium"
const ANIMATION_NAME := "Idle_A"
const WALL_GRID_NAME := "GridMapWall"
const FLOOR_GRID_NAME := "GridMapFloor"
const GRID_COLLISION_NAME := "GridCollision"
const COLLISION_CONTAINER_NAME := "Collision"
const WALL_BOX_PREFIX := "Wall_"
const FLOOR_BODY_NAME := "Floor"
const WALL_CELLS_EXPECTED := 115
const FLOOR_CELLS_EXPECTED := 276
# Движение к стене: стена выбрана по данным коллизий (см. T22-checks-report.md). Грань стены z = 32, старт z = 34.
const MOVE_WALL_PATH := "GridCollision/Collision/Wall_16_0_7"
const MOVE_START := Vector3(66.0, 2.05, 34.0)
const MOVE_FRAMES := 120
const MOVE_MIN_TRAVEL := 0.5
const MOVE_CLEARANCE := 0.05
const POSITION_EPS := 0.0001
# 7. Оболочка пещеры T1/T2r: cave_gate.glb грузится напрямую, без инстанса в level.tscn (задача 6).
# Размеры повторяют game/tools/build_cave_gate.py: поменял там — поменяй и здесь (см. отчёт T1).
const CAVE_GLB_PATH := "res://assets/cave_gate.glb"
const CAVE_MESH_INSTANCES := 1
# Габарит БЛОКА (не купола): после растяжки в +X под двор-яму (T2r-a3) пятно
# x ∈ [-8, +16] = 24 м, z = 16 м. Диапазоны узкие: блок не должен ни сжаться
# обратно, ни раздуться.
const CAVE_BLOCK_X_MIN := 22.0
const CAVE_BLOCK_X_MAX := 26.0
const CAVE_BLOCK_Z_MIN := 14.0
const CAVE_BLOCK_Z_MAX := 18.0
# Свод зала: апекс купола 7.0 м. Проверяется вертикальным сканом над центром
# зала (0, 0), а не по AABB блока: верхняя плоскость блока (9.0) — это крыша
# породы, и по ней высота свода не читается.
const CAVE_DOME_MIN := 6.4
const CAVE_DOME_MAX := 7.2
const CAVE_STEP_MAX := 0.1
const CAVE_INTERIOR_RADIUS := 6.5    # зона ровного пола: подъём от пола ближе этой границы = ступень
const CAVE_INTERIOR_MIN_CORNERS := 1900
const CAVE_OPEN_MIN_WIDTH := 3.0
const CAVE_OPEN_MIN_HEIGHT := 5.0
const CAVE_OPEN_X := 4.0             # проём смотрит на +X и начинается этой координаты
const CAVE_OPEN_X_MAX := 8.05        # проём кончается стеной двора (x = 8.0); дальше — двор,
                                      # его стены закрывают обзор и к проёму отношения не имеют
const CAVE_OPEN_SCAN_Z := 4.0        # сканируем полосу |z| <= 4 м (ось Z — «глубина» в glTF)
const CAVE_OPEN_Z_FROM := 0.15       # первая высота скана (кольца купола кратны 0.4)
const CAVE_OPEN_Z_TO := 5.0          # высота, до которой скан меряет ширину проёма (не измерение:
                                     # >= CAVE_OPEN_MIN_HEIGHT — только защита от опечатки в константах)
const CAVE_OPEN_Z_STEP := 0.1
const CAVE_OPEN_LINTEL_Z := 5.2      # контроль чувствительности: над проёмом есть перемычка
const CAVE_WELL_RHO := 2.6
const CAVE_WELL_PHIS := [90.0, 210.0, 330.0]
# Двор-яма (T2r-a3, design.md:65-68): глухая яма в породе под статую.
const CAVE_YARD_WALL_X := 8.0        # стена у ворот (та же плоскость, что и лоб тоннеля)
const CAVE_YARD_FAR_X := 15.0        # дальняя стена
const CAVE_YARD_HALF := 4.0          # половина ширины по Z
const CAVE_YARD_TOP_MIN := 6.0       # потолок двора не ниже
const CAVE_YARD_PROBE_Y := 3.0       # высота горизонтальных лучей проверки стен
const CAVE_YARD_SCAN_Z := 3.0        # точка вертикального скана потолка: в стороне от отверстия шахты
const CAVE_YARD_WALL_Z := 2.5        # z лучей проверки стен: внутри двора, вне проёма (|z| <= 1.9)
                                    # и не на колонке стены (колонки кратны ~0.213 м)
const CAVE_YARD_ROCK_MIN := 0.3      # минимальная толщина породы за дальней стеной
const CAVE_WALL_MIN := 0.1           # допуск на положение стен двора
const CAVE_EPS := 0.0001

const GATE_SCENE := "res://level/zones/gate_entrance.tscn"
const GATE_NODE_NAMES := ["Cave", "Portcullis", "Arch", "Brazier", "Lever", "WeaponRack", "Table", "Masonry", "Rail1", "Rail2", "Minecart", "MerchantSpot", "GuardRoom", "Yard", "FounderStatue", "Stall", "WallTorch"]
const GATE_BODY_NAMES := ["BrazierBody", "WeaponRackBody", "TableBody", "MasonryBody", "MinecartBody", "Rail1Body", "Rail2Body", "ArchLegLBody", "ArchLegRBody", "ArchLintelBody", "FounderStatueBody", "StallBody", "WallTorchBody"]
const GATE_BOXED_PROPS := [["Brazier", "BrazierBody"], ["WeaponRack", "WeaponRackBody"], ["Table", "TableBody"], ["Masonry", "MasonryBody"], ["Minecart", "MinecartBody"], ["Rail1", "Rail1Body"], ["Rail2", "Rail2Body"], ["FounderStatue", "FounderStatueBody"], ["Stall", "StallBody"], ["WallTorch", "WallTorchBody"]]
const GATE_GUARD_ROOM := "GuardRoom"
const GATE_GUARD_BOXES_MIN := 5
const GATE_OPENING_WIDTH := 3.8
const GATE_OPENING_HEIGHT := 5.0
# Арка arc2_1024 (T2-fix3): равномерный масштаб, поворот +90° по Y, ось прохода на x=ARCH_CUT_X.
# Граница ног и перемычки — в координатах меша до масштаба; замеры по мешу, не константы.
const ARCH_GLB_PATH := "res://assets/props/arc2_1024.glb"
const ARCH_SCALE := 7.05
const ARCH_CUT_X := 6.5
const ARCH_SPLIT_Y := 0.70
const ARCH_GAP_MIN := 3.5
const ARCH_LINTEL_MIN := 5.0
const ARCH_SCAN_FROM := 0.1
const ARCH_SCAN_TO := 4.9
const ARCH_SCAN_STEP := 0.1
const ARCH_CENTRE_HALF := 1.0
const ARCH_PASSAGE_HALF := 1.9
const ARCH_CLEAR_FROM := 1.0
const ARCH_BODIES := ["ArchLegLBody", "ArchLegRBody", "ArchLintelBody"]
# Единый допуск всех проверок зоны (мировые AABB, коробки, трансформы); проверки оболочки — CAVE_EPS.
const GATE_BOX_EPS := 0.02

# Решётка ворот (T3; ход сокращён в T3-д). open_height — СОБСТВЕННАЯ высота подъёма решётки,
# а не высота проёма (GATE_OPENING_HEIGHT = 5.0, решение пользователя 13.10.2026, ledger.md):
# нижняя часть уходит в нишу над проёмом, проход остаётся открытым для капсулы 1.8 м.
# 2.4 м (решение пользователя 14.10.2026): при 3.5 м верх решётки доходил до y = 8.51 и уходил
# в сплошную породу над нишей-дымоходом. Границы подъёма проверяет check_raised_grate_niche.
const PORTCULLIS_OPEN_HEIGHT := 2.4
# Потолок ожидания подъёма: анимация open_time (1.0 с) идёт в физических кадрах, ждать 2.5 с.
const PORTCULLIS_RAISE_FRAME_CAP := 150
const PORTCULLIS_REPEAT_FRAMES := 20    # сколько кадров ждём после третьего open()
# Верх ниши-дымохода в породе (build_cave_gate.py: NICHE_TOP). Проверка обязана УМЕРИТЬ его по
# геометрии оболочки, а не взять константой: иначе дефект «решётка выше ниши» можно вернуть,
# не зная ниши. CAVE_NICHE_TOP — только контроль, что проба нашла именно нишу.
const CAVE_NICHE_TOP := 8.0
const CAVE_NICHE_EPS := 0.05
# Точка под нишей: x между NICHE_BACK = 7.4 и стеной двора x = 8.0, z = 0 (центр проёма).
const PORTCULLIS_NICHE_PROBE := Vector2(7.7, 0.0)
# Зазор под поднятой решёткой должен быть не только «как капсула», но и с запасом на голову.
const PORTCULLIS_HEADROOM_MIN := 0.3
# Физическая проба прохода: капсула игрока (level.tscn: радиус 0.35, высота 1.8, начало узла
# Character — НИЗ капсулы, CollisionShape3D сдвинут на +0.9) едет из двора в тоннель по -X через
# решётку и арку. Старт на 0.05 — низ капсулы на 0.05 м выше пола двора (y = 0), как в check_movement.
const PORTCULLIS_CAPSULE_RADIUS := 0.35
const PORTCULLIS_CAPSULE_HEIGHT := 1.8
const PORTCULLIS_START := Vector3(8.6, 0.05, 0.0)
const PORTCULLIS_PUSH_FRAMES := 90
const PORTCULLIS_MIN_TRAVEL := 1.0     # капсула должна реально ехать, а не стоять на месте
const PORTCULLIS_PASSED_X := 6.5       # прошёл: за лбом породы (x = 6.8) и центром арки (x = 6.5)

# Рычаг (T4). Зона действия — Area3D UseZone под узлом Lever; проверяется и габарит зоны,
# и то, что она РЕАЛЬНО ловит капсулу (get_overlapping_bodies), а не только что try_use()
# вызывается руками. Точки стояния — в координатах корня зоны; y = 0.05 подобран так же,
# как PORTCULLIS_START: начало узла Character — НИЗ капсулы (капсула растёт вверх на 1.8 м).
# LEVER_STAND — в 0.7 м к востоку от рычага: это единственный открытый подход в караулку
# (стены с трёх сторон, GuardWallSouth/North обрываются на x = 4.05/4.3), а сам рычаг
# стоит вплотную к жаровне (меш рычага x 3.36..3.93, жаровня кончается на x = 3.17).
const LEVER_NODE := "Lever"
const LEVER_ZONE := "UseZone"
const LEVER_SCRIPT_PATH := "res://level/zones/lever.gd"
const LEVER_KEY_CALL := "is_physical_key_pressed(KEY_E)"
const LEVER_STAND := Vector3(4.4, 0.05, 3.2)     # у рычага: зона обязана накрывать
const LEVER_TUNNEL := Vector3(6.3, 0.05, 0.0)    # тоннель у ворот: зона обязана НЕ накрывать
const LEVER_YARD := Vector3(11.0, 0.05, 0.0)      # MerchantSpot во дворе: то же самое
const LEVER_ZONE_HALF_MIN := 0.7                 # уже — игрок в зону не попадёт
const LEVER_ZONE_HALF_MAX := 1.25                # шире — рычаг сработает «через всю караулку»
const LEVER_ZONE_FLOOR_MAX := 0.1                # низ зоны у пола: капсула должна входить целиком
const LEVER_ZONE_SETTLE_FRAMES := 4              # кадров на обновление Area3D после переноса капсулы
const LEVER_HOLD_FRAMES := 20                    # столько кадров «удержания» E проверяем

# Двор T2r-b2: статуя основателя, торговая палатка, настенный факел (design.md:62-63, :69, :77).
# Ассеты — выбранные пользователем модели Hunyuan (plan.md:58-60); проверка подмены ассета
# защищает от молчаливой замены меша под тем же именем узла.
const STATUE_GLB := "res://assets/props/founder_statue_1024.glb"
const STALL_GLB := "res://assets/props/stall_1024.glb"
const TORCH_GLB := "res://assets/props/wall-torch_1024.glb"
# Высота статуи — объекта ЦЕЛИКОМ, вместе с постаментом: design.md:62 говорит «скульптура
# ~4-5 м на ступенчатом постаменте», постамент добавляет ~1.4 м, поэтому мерить только
# скульптуру нельзя (занизит результат). Постамент собран в сцену детьми FounderStatue и
# входит в его мировой AABB, поэтому мера честная.
const STATUE_H_MIN := 4.0
const STATUE_H_MAX := 5.0
const STATUE_PEDESTAL_STEPS := 3      # ступенчатый постамент из коробок (design.md:62)
const STATUE_BASE_SIZE := 3.0         # постамент ~3x3 м (design.md:62)
const STATUE_BASE_TOL := 0.15
const STATUE_SEAT_EPS := 0.05         # скульптура стоит на постаменте без зазора и без провала
const STATUE_CENTRE_Z := 0.5          # фокус по центру проёма: |z| центра скульптуры <= 0.5
# Палатка и факел «~1 м» (plan.md:59-60): диапазон шире цели на 0.2 м в каждую сторону,
# но уже, чем был бы «1.0 +/- 50%».
const PROP_H_MIN := 0.8
const PROP_H_MAX := 1.4
const YARD_PROP_EPS := 0.05           # основание на полу двора (y = 0)
const STALL_SPOT_CLEAR := 1.2         # палатка не загораживает точку торговца (MerchantSpot)
# Факел настенный: низ заметно выше пола, верх ниже потолка двора, тело вплотную к породе.
const TORCH_MOUNT_MIN_Y := 1.2
const TORCH_MOUNT_MAX_Y := 2.2
const TORCH_WALL_GAP := 0.15
# Взгляд изнутри (design.md:63 «фокус взгляда изнутри через арку»): точка в зале перед
# тоннелем на высоте глаз камеры (EYE_HEIGHT 2.1-2.2 м). x = 4.0 — ближайшая к воротам
# типичная точка стояния (2.8 м перед лбом породы x = 6.8), то есть самая требовательная
# к обзору: чем ближе взгляд, тем уже проекция объекта на проём.
const VIEW_EYE := Vector3(4.0, 2.15, 0.0)
const VIEW_MARGIN := 0.2              # запас от края проёма по ширине и высоте
const VIEW_SIGHT_EPS := 0.05          # попадание в породу ближе этой дистанции = луч перекрыт
const VIEW_SAMPLES := 24              # выборка вершин меша для лучей (детерминированная)
const TORCH_SAMPLES := 8              # у факела силуэт и так читается его AABB

var failed := 0
# Треугольники породы для проверок зоны (лучи видимости); наполняется в check_cave_shell,
# иначе читается напрямую из CAVE_GLB_PATH — проверка зоны не зависит от порядка вызовов.
var cave_tris_cache: Array = []


func _initialize() -> void:
	var packed := load(LEVEL_SCENE) as PackedScene
	if packed == null:
		print("сцена не загрузилась: %s" % LEVEL_SCENE)
		quit(EXIT_BROKEN)
		return
	var level := packed.instantiate()
	if level == null:
		print("сцена не инстанцировалась: %s" % LEVEL_SCENE)
		quit(EXIT_BROKEN)
		return
	root.add_child(level)
	# Узлы сцены получают _ready только на следующем кадре; анимация запускается в первом кадре, проверяем после второго.
	await process_frame
	await process_frame

	check_root(level)
	var modules := collect_modules(level)
	check_modules(modules)
	check_camera_and_environment(level)
	check_character(level)
	check_character_body(level)
	check_animation(level)
	check_grid_maps(level)
	check_grid_collision(level)
	check_view_toggle(level)
	check_mouse(level)
	await check_movement(level)
	check_cave_shell()
	await check_gate_entrance()

	print("failed: %d" % failed)
	quit(EXIT_FAIL if failed > 0 else EXIT_OK)


# 1. Корень сцены — Level.
func check_root(level: Node) -> void:
	if level.name == "Level":
		print("ok: корень Level существует")
		return
	failed += 1
	print("ПРОВАЛ корень сцены %s, ожидалось Level" % level.name)


# Модули уровня: Node3D-дети Level без света, камеры, персонажа и GridMap.
# Исключение: прямой MeshInstance3D без инстанса сцены (узлы пользователя ChainLink, Cage и т.п.).
func collect_modules(level: Node) -> Array:
	var modules: Array = []
	for child in level.get_children():
		if child is Light3D or child is Camera3D or has_character_instance(child) or is_grid_map(child):
			continue
		if is_bare_mesh(child):
			continue
		if child is Node3D:
			modules.append(child)
	return modules


# 2. Каждый модуль — инстанс res://assets/kaykit/<kind>.gltf, и файл существует. Пустой список — провал.
func check_modules(modules: Array) -> void:
	if modules.is_empty():
		failed += 1
		print("ПРОВАЛ у Level нет модулей-инстансов")
		return
	var bad: Array[String] = []
	for module in modules:
		var kind := kind_of(module)
		if kind == "" or not FileAccess.file_exists(MODEL_PREFIX + kind + MODEL_SUFFIX):
			bad.append(module.name)
	if not bad.is_empty():
		failed += 1
		print("ПРОВАЛ модули без инстанса .gltf: %s" % ", ".join(bad))
		return
	if modules.size() != MODULES_EXPECTED:
		failed += 1
		print("ПРОВАЛ модулей %d, ожидалось %d" % [modules.size(), MODULES_EXPECTED])
		return
	print("ok: модулей %d, у каждого инстанс .gltf" % modules.size())


# 3. Камера и WorldEnvironment — прямые дети корня.
func check_camera_and_environment(level: Node) -> void:
	var has_camera := false
	var has_env := false
	for child in level.get_children():
		if child is Camera3D:
			has_camera = true
		if child is WorldEnvironment:
			has_env = true
	if has_camera:
		print("ok: в корне есть Camera3D")
	else:
		failed += 1
		print("ПРОВАЛ в корне нет Camera3D")
	if has_env:
		print("ok: в корне есть WorldEnvironment")
	else:
		failed += 1
		print("ПРОВАЛ в корне нет WorldEnvironment")


# 4. Character — Node3D в корне; внутри него есть инстанс из res://assets/kaykit_animations/.
func check_character(level: Node) -> void:
	var character := level.get_node_or_null(CHARACTER_NAME)
	if character == null or not (character is Node3D):
		failed += 1
		print("ПРОВАЛ узла Character (Node3D) нет")
		return
	if has_character_instance(character):
		print("ok: Character есть, инстанс из kaykit_animations")
		return
	failed += 1
	print("ПРОВАЛ в Character нет инстанса из %s" % CHARACTER_PREFIX)


# 4a. Character — CharacterBody3D; FPSCamera дочерний, высота глаз 2.1–2.2 м; Ranger с мешем и скелетом; Rig скрыт.
func check_character_body(level: Node) -> void:
	var character := character_of(level)
	if character == null:
		failed += 1
		print("ПРОВАЛ Character не %s" % CHARACTER_TYPE)
		return
	if character.get_class() == CHARACTER_TYPE:
		print("ok: тип Character = %s" % CHARACTER_TYPE)
	else:
		failed += 1
		print("ПРОВАЛ тип Character %s, ожидалось %s" % [character.get_class(), CHARACTER_TYPE])

	var camera := character.get_node_or_null(CAMERA_NAME) as Camera3D
	if camera == null:
		failed += 1
		print("ПРОВАЛ в Character нет дочернего Camera3D %s" % CAMERA_NAME)
	else:
		print("ok: %s — дочерний Character" % CAMERA_NAME)
		if camera.position.y >= EYE_HEIGHT_MIN and camera.position.y <= EYE_HEIGHT_MAX:
			print("ok: высота %s %.4f м в диапазоне %.1f–%.1f" % [CAMERA_NAME, camera.position.y, EYE_HEIGHT_MIN, EYE_HEIGHT_MAX])
		else:
			failed += 1
			print("ПРОВАЛ высота %s %.4f м вне диапазона %.1f–%.1f" % [CAMERA_NAME, camera.position.y, EYE_HEIGHT_MIN, EYE_HEIGHT_MAX])

	var ranger := character.get_node_or_null(RANGER_NAME)
	if ranger == null:
		failed += 1
		print("ПРОВАЛ в Character нет узла %s" % RANGER_NAME)
	else:
		var meshes := count_of_class(ranger, "MeshInstance3D")
		var skeletons := count_of_class(ranger, "Skeleton3D")
		if meshes > 0 and skeletons > 0:
			print("ok: %s: мешей %d, скелетов %d" % [RANGER_NAME, meshes, skeletons])
		else:
			failed += 1
			print("ПРОВАЛ %s: мешей %d, скелетов %d; нужны оба" % [RANGER_NAME, meshes, skeletons])

	var rig := character.get_node_or_null(RIG_NAME)
	if rig == null or rig.get_node_or_null(RIG_MESH_NAME) == null:
		failed += 1
		print("ПРОВАЛ в %s нет %s" % [RIG_NAME, RIG_MESH_NAME])
	else:
		var rig_meshes := count_of_class(rig, "MeshInstance3D")
		var visible_rig_meshes := count_visible_meshes(rig)
		if rig_meshes > 0 and visible_rig_meshes == 0:
			print("ok: меш %s скрыт (мешей %d, видимых 0)" % [RIG_NAME, rig_meshes])
		else:
			failed += 1
			print("ПРОВАЛ меш %s не скрыт: мешей %d, видимых %d" % [RIG_NAME, rig_meshes, visible_rig_meshes])


# 4b. Character — AnimationPlayer играет Idle_A (проверка после второго кадра).
func check_animation(level: Node) -> void:
	var character := character_of(level)
	if character == null:
		return
	var player := character.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if player == null:
		failed += 1
		print("ПРОВАЛ в Character нет AnimationPlayer")
		return
	if player.current_animation == ANIMATION_NAME and player.is_playing():
		print("ok: AnimationPlayer играет %s после 2 кадров" % ANIMATION_NAME)
	else:
		failed += 1
		print("ПРОВАЛ AnimationPlayer: current_animation %s, is_playing %s, ожидалось %s" % [player.current_animation, str(player.is_playing()), ANIMATION_NAME])


# 5b. GridCollision: коробки стен = занятые ячейки GridMapWall, коробки пола = занятые ячейки GridMapFloor.
func check_grid_collision(level: Node) -> void:
	var grid_collision := level.get_node_or_null(GRID_COLLISION_NAME)
	if grid_collision == null:
		failed += 1
		print("ПРОВАЛ узла %s нет" % GRID_COLLISION_NAME)
		return
	print("ok: %s есть" % GRID_COLLISION_NAME)
	var container := grid_collision.get_node_or_null(COLLISION_CONTAINER_NAME)
	var wall_grid := level.get_node_or_null(WALL_GRID_NAME) as GridMap
	var floor_grid := level.get_node_or_null(FLOOR_GRID_NAME) as GridMap
	if container == null or wall_grid == null or floor_grid == null:
		failed += 1
		print("ПРОВАЛ нет контейнера %s или GridMap стен/пола" % COLLISION_CONTAINER_NAME)
		return

	var walls := 0
	for body in container.get_children():
		if body.name.begins_with(WALL_BOX_PREFIX):
			walls += 1
	var used_walls := wall_grid.get_used_cells().size()
	if walls == used_walls and walls == WALL_CELLS_EXPECTED:
		print("ok: коробок стен %d = занятых ячеек %s (%d)" % [walls, WALL_GRID_NAME, used_walls])
	else:
		failed += 1
		print("ПРОВАЛ коробок стен %d, ячеек %s %d, ожидалось %d" % [walls, WALL_GRID_NAME, used_walls, WALL_CELLS_EXPECTED])

	var floor_body := container.get_node_or_null(FLOOR_BODY_NAME)
	if floor_body == null:
		failed += 1
		print("ПРОВАЛ в %s нет тела %s" % [COLLISION_CONTAINER_NAME, FLOOR_BODY_NAME])
		return
	var shapes := 0
	for child in floor_body.get_children():
		if child is CollisionShape3D:
			shapes += 1
	var used_floor := floor_grid.get_used_cells().size()
	if shapes == used_floor and shapes == FLOOR_CELLS_EXPECTED:
		print("ok: шейпов пола %d = занятых ячеек %s (%d)" % [shapes, FLOOR_GRID_NAME, used_floor])
	else:
		failed += 1
		print("ПРОВАЛ шейпов пола %d, ячеек %s %d, ожидалось %d" % [shapes, FLOOR_GRID_NAME, used_floor, FLOOR_CELLS_EXPECTED])


# 6a. V через вызов toggle_view: переключает current между Camera3D и FPSCamera.
func check_view_toggle(level: Node) -> void:
	var character := character_of(level)
	var fps := character.get_node_or_null(CAMERA_NAME) as Camera3D if character != null else null
	var top := level.get_node_or_null(TOP_CAMERA_NAME) as Camera3D
	if character == null or fps == null or top == null:
		failed += 1
		print("ПРОВАЛ нет Character, %s или %s для проверки вида" % [CAMERA_NAME, TOP_CAMERA_NAME])
		return
	var controller: Variant = character
	if fps.current and not top.current:
		print("ok: старт: вид от первого лица")
	else:
		failed += 1
		print("ПРОВАЛ старт: %s.current %s, %s.current %s" % [CAMERA_NAME, str(fps.current), TOP_CAMERA_NAME, str(top.current)])
	controller.toggle_view()
	if top.current and not fps.current:
		print("ok: V: переключение на вид сверху")
	else:
		failed += 1
		print("ПРОВАЛ V: вид сверху не включился")
	controller.toggle_view()
	if fps.current and not top.current:
		print("ok: V: возврат к виду от первого лица")
	else:
		failed += 1
		print("ПРОВАЛ V: возврат к виду от первого лица не сработал")


# 6b. Мышь через вызов apply_mouse_motion: yaw по X, pitch по Y, pitch ограничен ±80°.
func check_mouse(level: Node) -> void:
	var character := character_of(level)
	var fps := character.get_node_or_null(CAMERA_NAME) as Camera3D if character != null else null
	if character == null or fps == null:
		failed += 1
		print("ПРОВАЛ нет Character или %s для проверки мыши" % CAMERA_NAME)
		return
	var controller: Variant = character
	var yaw0 := character.rotation.y
	var pitch0 := fps.rotation.x
	var sensitivity: float = CONTROLLER_SCRIPT.MOUSE_SENSITIVITY
	var limit: float = CONTROLLER_SCRIPT.PITCH_LIMIT

	controller.apply_mouse_motion(Vector2(100.0, 0.0))
	var yaw_delta := character.rotation.y - yaw0
	if absf(yaw_delta + 100.0 * sensitivity) < POSITION_EPS:
		print("ok: мышь вправо: yaw изменился на %.4f" % yaw_delta)
	else:
		failed += 1
		print("ПРОВАЛ мышь вправо: yaw изменился на %.4f, ожидалось %.4f" % [yaw_delta, -100.0 * sensitivity])

	controller.apply_mouse_motion(Vector2(0.0, -100.0))
	var pitch_delta := fps.rotation.x - pitch0
	if absf(pitch_delta - 100.0 * sensitivity) < POSITION_EPS:
		print("ok: мышь вверх: pitch изменился на %.4f" % pitch_delta)
	else:
		failed += 1
		print("ПРОВАЛ мышь вверх: pitch изменился на %.4f, ожидалось %.4f" % [pitch_delta, 100.0 * sensitivity])

	controller.apply_mouse_motion(Vector2(0.0, -100000.0))
	if absf(fps.rotation.x - limit) < POSITION_EPS:
		print("ok: pitch ограничен +80° (%.4f рад)" % fps.rotation.x)
	else:
		failed += 1
		print("ПРОВАЛ pitch не ограничен +80°: %.4f, ожидалось %.4f" % [fps.rotation.x, limit])

	controller.apply_mouse_motion(Vector2(0.0, 200000.0))
	if absf(fps.rotation.x + limit) < POSITION_EPS:
		print("ok: pitch ограничен -80° (%.4f рад)" % fps.rotation.x)
	else:
		failed += 1
		print("ПРОВАЛ pitch не ограничен -80°: %.4f, ожидалось %.4f" % [fps.rotation.x, -limit])

	character.rotation.y = yaw0
	fps.rotation.x = pitch0


# 6c. Движение: персонаж у стены, скорость вперёд (-Z) через move_and_slide, капсула не проходит коробку стены.
# Коробка стены и капсула перекрываются по высоте (капсула 2.05–3.85 м, коробка 1.84–6.0 м),
# поэтому расстояние считается в плоскости XZ от оси капсулы до грани коробки.
func check_movement(level: Node) -> void:
	var character := character_of(level)
	var wall_body := level.get_node_or_null(MOVE_WALL_PATH) as StaticBody3D
	if character == null or wall_body == null:
		failed += 1
		print("ПРОВАЛ нет Character или стены %s для проверки движения" % MOVE_WALL_PATH)
		return
	var wall_shape := wall_body.get_child(0) as CollisionShape3D
	var box := wall_shape.shape as BoxShape3D
	var capsule_node := character.get_node_or_null("CollisionShape3D") as CollisionShape3D
	var capsule := capsule_node.shape as CapsuleShape3D if capsule_node != null else null
	if box == null or capsule == null:
		failed += 1
		print("ПРОВАЛ нет BoxShape3D у стены или CapsuleShape3D у Character")
		return
	var radius := capsule.radius

	character.global_position = MOVE_START
	character.rotation.y = 0.0
	# Без клавиш _physics_process контроллера обнуляет скорость каждый кадр; на время прогона он отключён.
	character.set_physics_process(false)
	var forward := Vector3(0.0, 0.0, -1.0).rotated(Vector3.UP, character.rotation.y)
	var start := character.global_position
	for i in MOVE_FRAMES:
		character.velocity = forward * CONTROLLER_SCRIPT.SPEED
		character.move_and_slide()
		await physics_frame
	character.set_physics_process(true)

	var end := character.global_position
	var travelled := Vector2(end.x - start.x, end.z - start.z).length()
	var gap := box_distance_xz(end, wall_shape.global_position, box.size)
	print("info: стена %s, старт (%.2f, %.2f, %.2f), направление -Z, кадров %d" % [MOVE_WALL_PATH, start.x, start.y, start.z, MOVE_FRAMES])
	print("info: конец (%.4f, %.4f, %.4f), пройдено %.4f м, расстояние до стены %.4f м, радиус капсулы %.2f" % [end.x, end.y, end.z, travelled, gap, radius])
	if travelled < MOVE_MIN_TRAVEL:
		failed += 1
		print("ПРОВАЛ персонаж прошёл %.4f м, ожидалось не меньше %.2f: движение не сработало" % [travelled, MOVE_MIN_TRAVEL])
	else:
		print("ok: персонаж двигался к стене: %.4f м" % travelled)
	if gap >= radius - MOVE_CLEARANCE:
		print("ok: капсула не проходит сквозь стену: расстояние %.4f ≥ %.2f" % [gap, radius - MOVE_CLEARANCE])
	else:
		failed += 1
		print("ПРОВАЛ капсула прошла сквозь стену: расстояние %.4f < %.2f" % [gap, radius - MOVE_CLEARANCE])
	if gap <= radius + MOVE_CLEARANCE:
		print("ok: персонаж упёрся в стену: расстояние %.4f" % gap)
	else:
		failed += 1
		print("ПРОВАЛ персонаж не дошёл до стены: расстояние %.4f" % gap)


# 7. Оболочка пещеры T1: glb грузится напрямую (PackedScene), в level.tscn не инстансируется.
# Проверяет импорт, материал с запечёнными картами, габариты, ровность пола, проём и колодцы.
# ОСИ: экспорт Blender Z-up -> glTF Y-up, поэтому в меше Godot ось Y вверх, пол лежит
# на y=0, проём смотрит на +X и ограничен по Z, световые колодцы лежат в плоскости XZ.
func check_cave_shell() -> void:
	if not FileAccess.file_exists(CAVE_GLB_PATH):
		failed += 1
		print("ПРОВАЛ файла оболочки нет: %s" % CAVE_GLB_PATH)
		return
	var packed := load(CAVE_GLB_PATH) as PackedScene
	if packed == null:
		failed += 1
		print("ПРОВАЛ оболочка не загрузилась как PackedScene: %s" % CAVE_GLB_PATH)
		return
	var shell := packed.instantiate()
	var mesh_instance := first_mesh_instance(shell)
	if mesh_instance == null:
		failed += 1
		print("ПРОВАЛ в оболочке нет MeshInstance3D")
		shell.free()
		return
	var instances := count_of_class(shell, "MeshInstance3D")
	if instances == CAVE_MESH_INSTANCES:
		print("ok: оболочка грузится напрямую, MeshInstance3D %d" % instances)
	else:
		failed += 1
		print("ПРОВАЛ MeshInstance3D в оболочке %d, ожидалось %d" % [instances, CAVE_MESH_INSTANCES])

	check_cave_material(mesh_instance)

	var mesh := mesh_instance.mesh as ArrayMesh
	if mesh == null:
		failed += 1
		print("ПРОВАЛ меш оболочки не ArrayMesh")
		shell.free()
		return
	var faces := mesh.get_faces()
	if faces.is_empty() or faces.size() % 3 != 0:
		failed += 1
		print("ПРОВАЛ у меша оболочки нет треугольников: вершин-в-треугольниках %d" % faces.size())
		shell.free()
		return
	var tris := cave_tris(faces)
	cave_tris_cache = tris
	print("info: оболочка: треугольников %d, поверхностей %d" % [tris.size(), mesh.get_surface_count()])

	var stats := cave_stats(tris)
	check_cave_block_size(stats)
	check_cave_dome(tris)
	check_cave_floor(stats)
	check_cave_floor_normals(mesh)
	check_cave_opening(tris)
	check_cave_wells(tris)
	check_cave_yard(tris)
	shell.free()


# Габарит БЛОКА породы: пятно плана и пол на y=0. Именно блок, а не купол:
# после растяжки в +X (T2r-a3) его пятно 24 x 16 м, тогда как купол — 14.4 м.
func check_cave_block_size(stats: Dictionary) -> void:
	var min_y: float = stats["min_y"]
	var dx: float = stats["dx"]
	var dz: float = stats["dz"]
	if dx >= CAVE_BLOCK_X_MIN and dx <= CAVE_BLOCK_X_MAX \
			and dz >= CAVE_BLOCK_Z_MIN and dz <= CAVE_BLOCK_Z_MAX:
		print("ok: габарит блока %.2f x %.2f м в диапазоне %.0f–%.0f x %.0f–%.0f" % [dx, dz,
			CAVE_BLOCK_X_MIN, CAVE_BLOCK_X_MAX, CAVE_BLOCK_Z_MIN, CAVE_BLOCK_Z_MAX])
	else:
		failed += 1
		print("ПРОВАЛ габарит блока %.2f x %.2f м вне диапазона %.0f–%.0f x %.0f–%.0f" % [dx, dz,
			CAVE_BLOCK_X_MIN, CAVE_BLOCK_X_MAX, CAVE_BLOCK_Z_MIN, CAVE_BLOCK_Z_MAX])
	if absf(min_y) <= CAVE_EPS:
		print("ok: пол лежит на y=0 (минимум %.4f)" % min_y)
	else:
		failed += 1
		print("ПРОВАЛ пол не на y=0: минимум %.4f" % min_y)


# Свод зала: вертикальный скан над центром полости (0, 0) должен упереться в
# купол на APEX_Z. Скан по XZ выбирает самую низкую грань, накрывающую точку, —
# это и есть высота свода над полом (крышка блока на 9.0 м сюда не попадает:
# над центром зала её нет).
func check_cave_dome(tris: Array) -> void:
	var dome := cave_surface_y(tris, 0.0, 0.0)
	if dome >= CAVE_DOME_MIN and dome <= CAVE_DOME_MAX:
		print("ok: свод над центром зала %.2f м в диапазоне %.1f–%.1f" % [dome, CAVE_DOME_MIN, CAVE_DOME_MAX])
	else:
		failed += 1
		print("ПРОВАЛ свод над центром зала %.2f м вне диапазона %.1f–%.1f" % [dome, CAVE_DOME_MIN, CAVE_DOME_MAX])


# Ровность пола: «подъём» — треугольник, касающийся пола (y=0) и поднимающийся выше
# CAVE_STEP_MAX. Все подъёмы обязаны лежать по краю пещеры (r >= CAVE_INTERIOR_RADIUS):
# внутри зоны пола ступеней нет. Дополнительно: первая вершина над полом >= CAVE_STEP_MAX
# и пол занимает зону (число углов на y=0).
func check_cave_floor(stats: Dictionary) -> void:
	var min_pos_y: float = stats["min_pos_y"]
	var corners: int = stats["floor_corners"]
	var risers: int = stats["risers"]
	var riser_min_r: float = stats["riser_min_r"]
	if riser_min_r >= CAVE_INTERIOR_RADIUS and corners >= CAVE_INTERIOR_MIN_CORNERS and min_pos_y >= CAVE_STEP_MAX:
		print("ok: пол ровный: подъёмов от пола %d, ближайший на r=%.2f м (зона пола r=%.1f м свободна), первая вершина над полом %.2f м >= %.1f, углов пола %d"
			% [risers, riser_min_r, CAVE_INTERIOR_RADIUS, min_pos_y, CAVE_STEP_MAX, corners])
	else:
		failed += 1
		print("ПРОВАЛ пол неровный: подъёмов %d, ближайший на r=%.4f (нужно >= %.1f), первая вершина над полом %.4f (нужно >= %.1f), углов пола %d (нужно >= %d)"
			% [risers, riser_min_r, CAVE_INTERIOR_RADIUS, min_pos_y, CAVE_STEP_MAX, corners, CAVE_INTERIOR_MIN_CORNERS])


# Нормали пола: треугольник, целиком лежащий в плоскости пола (все три вершины на y=0),
# обязан иметь нормаль вверх: и атрибут (средняя normal.y > 0), и обход вершин
# (знак геометрической нормали тройки) — сторонность коллизии Godot определяет обход,
# атрибут нормалей лишь дополнительный контроль. Перевёрнутый пол обрушил бы капсулу
# через trimesh в задаче 2: у Godot backface_collision = false, задняя грань не коллизит.
# Пол узнаётся по геометрии: в плоскости y=0 не может лежать ни стена, ни свод,
# поэтому разделение пол/стены надёжно и без нормалей; нормали читаются из импортированного
# меша (surface_get_arrays), в get_faces их нет.
func check_cave_floor_normals(mesh: ArrayMesh) -> void:
	var m := cave_floor_normals(mesh)
	if not m["has_normals"]:
		failed += 1
		print("ПРОВАЛ у поверхностей меша оболочки нет нормалей: ориентация пола не проверена")
		return
	var floor_tris: int = m["floor"]
	if floor_tris == 0:
		failed += 1
		print("ПРОВАЛ полевых треугольников пола нет: проверка нормалей вырождена")
		return
	var min_normal_y: float = m["min_ny"]
	var bad_tris: int = m["bad"]
	if bad_tris > 0:
		failed += 1
		print("ПРОВАЛ нормали пола смотрят вниз: полевых треугольников с normal.y <= 0 или нисходящим обходом — %d из %d, min normal.y %.3f"
			% [bad_tris, floor_tris, min_normal_y])
		return
	print("ok: нормали пола смотрят вверх: полевых треугольников %d, min normal.y %.3f" % [floor_tris, min_normal_y])


# Полевые треугольники пола и их нормали одной проходкой по поверхностям меша.
# «Полевой» = все три вершины на y=0 (см. cave_vert_on_floor); нормаль треугольника —
# среднее нормалей его вершин (у rim-вершин нормаль смешана со стеной, поэтому
# порог проверки — «вверх», а не «почти вертикально»).
func cave_floor_normals(mesh: ArrayMesh) -> Dictionary:
	var floor_tris := 0
	var bad_tris := 0
	var min_normal_y := INF
	var has_normals := true
	for s in mesh.get_surface_count():
		var arrays := mesh.surface_get_arrays(s)
		var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
		if normals.is_empty():
			has_normals = false
			continue
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		var indexed := not indices.is_empty()
		var tri_count := (indices.size() if indexed else verts.size()) / 3
		for t in tri_count:
			var i0: int = indices[t * 3] if indexed else t * 3
			var i1: int = indices[t * 3 + 1] if indexed else t * 3 + 1
			var i2: int = indices[t * 3 + 2] if indexed else t * 3 + 2
			var a: Vector3 = verts[i0]
			var b: Vector3 = verts[i1]
			var c: Vector3 = verts[i2]
			if not cave_vert_on_floor(a) or not cave_vert_on_floor(b) or not cave_vert_on_floor(c):
				continue
			floor_tris += 1
			var ny := (normals[i0].y + normals[i1].y + normals[i2].y) / 3.0
			min_normal_y = minf(min_normal_y, ny)
			# Сторонность коллизии Godot (backface_collision = false) определяется обходом
			# вершин, то есть знаком геометрической нормали тройки. Godot, в отличие от
			# OpenGL, считает фронтовой обход по часовой стрелке, поэтому фронтовая нормаль
			# = -((b-a)×(c-a)) = (c-a)×(b-a) — проверено пробой на QuadMesh: фронт +Z даёт
			# cross.z = -1. Атрибут нормалей — лишь дополнительный контроль. Считаем битым оба сбоя.
			var winding_up := ((c - a).cross(b - a)).y > 0.0
			if ny <= 0.0 or not winding_up:
				bad_tris += 1
	return {
		"has_normals": has_normals,
		"floor": floor_tris,
		"bad": bad_tris,
		"min_ny": min_normal_y,
	}


# Проём под арку: на высотах CAVE_OPEN_Z_FROM..CAVE_OPEN_Z_TO непрерывная полоса
# шириной >= 3 м вокруг z=0 свободна; на CAVE_OPEN_LINTEL_Z центр закрыт (контроль).
func check_cave_opening(tris: Array) -> void:
	var min_width := INF
	var min_h := 0.0
	var h := CAVE_OPEN_Z_FROM
	while h <= CAVE_OPEN_Z_TO + 0.0001:
		var width := cave_open_width(tris, h)
		if width < min_width:
			min_width = width
			min_h = h
		h += CAVE_OPEN_Z_STEP
	if min_width < CAVE_OPEN_MIN_WIDTH:
		failed += 1
		print("ПРОВАЛ проём: ширина %.2f м (нужно >= %.1f) на высоте %.2f"
			% [min_width, CAVE_OPEN_MIN_WIDTH, min_h])
	elif CAVE_OPEN_Z_TO < CAVE_OPEN_MIN_HEIGHT:
		failed += 1
		print("ПРОВАЛ проём: скан ширины до %.1f м ниже требуемой высоты %.1f м (опечатка в константах)"
			% [CAVE_OPEN_Z_TO, CAVE_OPEN_MIN_HEIGHT])
	else:
		print("ok: проём: скан ширины подтверждён до %.1f м от пола (ширина не меньше %.2f м, узкое место на высоте %.2f м)"
			% [CAVE_OPEN_Z_TO, min_width, min_h])
	var lintel := cave_open_width(tris, CAVE_OPEN_LINTEL_Z)
	if lintel <= 0.0:
		print("ok: контроль чувствительности: на высоте %.1f над проёмом перемычка (ширина 0)" % CAVE_OPEN_LINTEL_Z)
	else:
		failed += 1
		print("ПРОВАЛ контроль: на высоте %.1f центр открыт (ширина %.2f м) — скан не видит стену"
			% [CAVE_OPEN_LINTEL_Z, lintel])


# Световые колодцы: в точках колодцев через потолок нет геометрии;
# контроль — центр купола, где свод обязан быть.
func check_cave_wells(tris: Array) -> void:
	var open_wells := 0
	for phi in CAVE_WELL_PHIS:
		var rad := deg_to_rad(phi)
		var wx := CAVE_WELL_RHO * cos(rad)
		# Blender Y вверх уходит в glTF Z со сменой знака: Godot z = -blender y.
		var wz := -CAVE_WELL_RHO * sin(rad)
		var hits := cave_ceiling_hits(tris, wx, wz)
		if hits == 0:
			open_wells += 1
		else:
			print("info: колодец (%.2f, %.2f): треугольников потолка над ним %d" % [wx, wz, hits])
	if open_wells == CAVE_WELL_PHIS.size():
		print("ok: световые колодцы %d/%d открыты (центры %s)" % [open_wells, CAVE_WELL_PHIS.size(), str(CAVE_WELL_PHIS)])
	else:
		failed += 1
		print("ПРОВАЛ световых колодцев открыто %d из %d" % [open_wells, CAVE_WELL_PHIS.size()])
	var center_hits := cave_ceiling_hits(tris, 0.0, 0.0)
	if center_hits > 0:
		print("ok: контроль: свод над центром купола есть (%d треугольников)" % center_hits)
	else:
		failed += 1
		print("ПРОВАЛ контроль: над центром купола нет геометрии — тест колодцев не чувствителен")


# Двор-яма (T2r-a3): глухая яма в породе с потолком и стенами по периметру.
# Проверяется лучами по готовому мешу: четыре горизонтальных луча из центра двора
# на высоте CAVE_YARD_PROBE_Y должны упереться в стены на заданных координатах
# (стена у ворот — вне проёма, поэтому луч идёт при |z| = 3.0), за дальней стеной
# должна быть порода, а потолок (скан при z = CAVE_YARD_SCAN_Z, то есть в стороне
# от отверстия шахты) — не ниже CAVE_YARD_TOP_MIN.
func check_cave_yard(tris: Array) -> void:
	var cx := 0.5 * (CAVE_YARD_WALL_X + CAVE_YARD_FAR_X)
	var origin := Vector3(cx, CAVE_YARD_PROBE_Y, CAVE_YARD_WALL_Z)
	# Пути лучей переводим в координаты: hit = o + t*d по изменяемой оси.
	var far_hits := cave_rays(tris, origin, Vector3(1.0, 0.0, 0.0), 2)
	var near_hits := cave_rays(tris, origin, Vector3(-1.0, 0.0, 0.0), 1)
	var plus_hits := cave_rays(tris, origin, Vector3(0.0, 0.0, 1.0), 1)
	var minus_hits := cave_rays(tris, origin, Vector3(0.0, 0.0, -1.0), 1)
	var ceil := cave_surface_y(tris, cx, CAVE_YARD_SCAN_Z)
	var bad: Array = []
	var far_x: float = -1.0
	var rock: float = -1.0
	if far_hits.size() < 2:
		bad.append("дальняя стена не найдена (попаданий луча %d)" % far_hits.size())
	else:
		far_x = cx + float(far_hits[0])
		rock = far_hits[1] - far_hits[0]
		if absf(far_x - CAVE_YARD_FAR_X) > CAVE_WALL_MIN:
			bad.append("дальняя стена на x = %.3f вместо %.2f" % [far_x, CAVE_YARD_FAR_X])
		elif rock < CAVE_YARD_ROCK_MIN:
			bad.append("породы за дальней стеной %.3f м < %.2f" % [rock, CAVE_YARD_ROCK_MIN])
	var near_x: float = cx - float(near_hits[0]) if not near_hits.is_empty() else -1.0
	if absf(near_x - CAVE_YARD_WALL_X) > CAVE_WALL_MIN:
		bad.append("стена у ворот x = %.3f вместо %.2f" % [near_x, CAVE_YARD_WALL_X])
	var plus_z: float = CAVE_YARD_WALL_Z + float(plus_hits[0]) if not plus_hits.is_empty() else -1.0
	if absf(plus_z - CAVE_YARD_HALF) > CAVE_WALL_MIN:
		bad.append("боковая стена z = %.3f вместо %.2f" % [plus_z, CAVE_YARD_HALF])
	var minus_z: float = CAVE_YARD_WALL_Z - float(minus_hits[0]) if not minus_hits.is_empty() else -1.0
	if absf(minus_z + CAVE_YARD_HALF) > CAVE_WALL_MIN:
		bad.append("боковая стена z = %.3f вместо %.2f" % [minus_z, CAVE_YARD_HALF])
	if ceil < CAVE_YARD_TOP_MIN:
		bad.append("потолок двора %.2f м < %.1f" % [ceil, CAVE_YARD_TOP_MIN])
	if bad.is_empty():
		print("ok: двор-яма: стены x = %.2f / %.2f, боковые |z| = %.2f, потолок %.2f м, породы за дальней стеной %.2f м"
			% [near_x, far_x, plus_z, ceil, rock])
	else:
		failed += 1
		print("ПРОВАЛ двор-яма: %s" % "; ".join(bad))


# Материал оболочки: запечённые растровые карты (glTF процедурные ноды не переживает).
func check_cave_material(instance: MeshInstance3D) -> void:
	var mat: BaseMaterial3D = null
	var mesh := instance.mesh as ArrayMesh
	if mesh != null and mesh.get_surface_count() > 0:
		mat = mesh.surface_get_material(0) as BaseMaterial3D
	if mat == null:
		mat = instance.material_override as BaseMaterial3D
	if mat == null:
		failed += 1
		print("ПРОВАЛ у меша оболочки нет BaseMaterial3D")
		return
	if mat.albedo_texture != null:
		print("ok: альбедо-текстура подключена (%s)" % mat.albedo_texture.resource_path)
	else:
		failed += 1
		print("ПРОВАЛ у материала оболочки нет альбедо-текстуры (bake не подключился)")
	if mat.normal_enabled and mat.normal_texture != null:
		print("ok: карта нормалей подключена (%s)" % mat.normal_texture.resource_path)
	else:
		failed += 1
		print("ПРОВАЛ карта нормалей не подключена (normal_enabled=%s)" % str(mat.normal_enabled))
	if mat.roughness_texture != null:
		print("ok: карта шероховатости подключена (%s)" % mat.roughness_texture.resource_path)
	else:
		failed += 1
		print("ПРОВАЛ у материала оболочки нет карты шероховатости (metallicRoughness из glb не подключился)")


# 8. Зона входа (T2): инстанс без add_child; узлы, высота арки, решётка в проёме, коллизии,
# двор и торговец. Мировые AABB считаются композицией трансформов (дерево сцены не нужно).
func check_gate_entrance() -> void:
	var packed := load(GATE_SCENE) as PackedScene
	if packed == null:
		failed += 1
		print("ПРОВАЛ сцена зоны не загрузилась: %s" % GATE_SCENE)
		return
	var zone := packed.instantiate() as Node3D
	if zone == null:
		failed += 1
		print("ПРОВАЛ сцена зоны не инстанцировалась: %s" % GATE_SCENE)
		return
	check_gate_nodes(zone)
	check_gate_portcullis(zone)
	check_gate_portcullis_clear(zone)
	check_gate_colliders(zone)
	check_gate_arch(zone)
	check_gate_table(zone)
	check_gate_cave_collision(zone)
	check_gate_yard(zone)
	check_gate_yard_props(zone)
	# Механика решётки — последняя: она двигает Portcullis вверх, а мерки AABB выше
	# (перекрытие проёма, верх решётки под перемычкой) считают решётку закрытой.
	root.add_child(zone)
	await check_gate_portcullis_closed(zone)
	await check_gate_portcullis_open(zone)
	root.remove_child(zone)
	zone.free()

	# Рычаг (T4) проверяется на СВОЕМ экземпляре зоны, а не на этом же: он тоже поднимает
	# решётку, и общий инстанс связал бы две механики порядком вызовов (кто первый поднял —
	# тот и виноват). Свой экземпляр начинает с гарантированно закрытой решётки.
	await check_lever_zone_instance()


# Отдельный экземпляр зоны для проверки рычага.
func check_lever_zone_instance() -> void:
	var packed := load(GATE_SCENE) as PackedScene
	if packed == null:
		failed += 1
		print("ПРОВАЛ рычаг: сцена зоны не загрузилась для отдельного экземпляра: %s" % GATE_SCENE)
		return
	var zone := packed.instantiate() as Node3D
	if zone == null:
		failed += 1
		print("ПРОВАЛ рычаг: сцена зоны не инстанцировалась для отдельного экземпляра")
		return
	root.add_child(zone)
	await process_frame
	await check_gate_lever(zone)
	root.remove_child(zone)
	zone.free()


# Все узлы зоны на месте; караулка и ход внутрь — коробки и маркер будущего хода.
func check_gate_nodes(zone: Node) -> void:
	var missing: Array[String] = []
	for node_name in GATE_NODE_NAMES + GATE_BODY_NAMES:
		if zone.get_node_or_null(node_name) == null:
			missing.append(node_name)
	if missing.is_empty():
		print("ok: узлы зоны на месте, узлов в дереве %d" % count_nodes(zone))
	else:
		failed += 1
		print("ПРОВАЛ узлы зоны не найдены: %s" % ", ".join(missing))
	var guard := zone.get_node_or_null(GATE_GUARD_ROOM)
	var boxes := count_of_class(guard, "StaticBody3D") if guard != null else 0
	if boxes >= GATE_GUARD_BOXES_MIN and zone.get_node_or_null(GATE_GUARD_ROOM + "/CorridorFuture") != null:
		print("ok: караулка и ход внутрь: коробок %d, маркер CorridorFuture на месте" % boxes)
	else:
		failed += 1
		print("ПРОВАЛ караулка: коробок %d, ожидалось >= %d, нужен CorridorFuture" % [boxes, GATE_GUARD_BOXES_MIN])


# Оболочка: у Cave есть StaticBody3D с ConcavePolygonShape3D (trimesh); число треугольников и
# AABB всех вершин trimesh совпадают с мешем Cave в пределах GATE_BOX_EPS.
# Проём в оболочке проверяет check_cave_opening (T1), здесь не дублируется.
func check_gate_cave_collision(zone: Node) -> void:
	var cave := zone.get_node_or_null("Cave") as Node3D
	if cave == null:
		failed += 1
		print("ПРОВАЛ у Cave нет узла для проверки коллизии")
		return
	var shape_faces := cave_trimesh_faces(cave)
	var shape_tris := shape_faces.size() / 3
	var shape_box := faces_aabb(shape_faces)
	var mesh_instance := first_mesh_instance(cave)
	var mesh_tris := 0
	var mesh_box := AABB()
	if mesh_instance != null:
		mesh_tris = mesh_instance.mesh.get_faces().size() / 3
		mesh_box = mesh_instance.mesh.get_aabb()
	if shape_tris > 0 and shape_tris == mesh_tris and aabb_close(shape_box, mesh_box):
		print("ok: коллизия оболочки trimesh %d треугольников = меш %d, AABB совпадает (%s)" % [shape_tris, mesh_tris, str(mesh_box)])
	else:
		failed += 1
		print("ПРОВАЛ коллизия оболочки: trimesh %d треугольников, меш %d, AABB trimesh %s, AABB меша %s; нужно совпадение и больше 0"
			% [shape_tris, mesh_tris, str(shape_box), str(mesh_box)])


# Faces первого ConcavePolygonShape3D у StaticBody3D-детей узла; пусто, если коллизии нет.
func cave_trimesh_faces(node: Node) -> PackedVector3Array:
	for body in node.get_children():
		if body is StaticBody3D:
			for child in body.get_children():
				if child is CollisionShape3D and (child as CollisionShape3D).shape is ConcavePolygonShape3D:
					return ((child as CollisionShape3D).shape as ConcavePolygonShape3D).get_faces()
	return PackedVector3Array()


# AABB всех вершин набора точек; пустой AABB, если точек нет.
func faces_aabb(faces: PackedVector3Array) -> AABB:
	if faces.is_empty():
		return AABB()
	var box := AABB(faces[0], Vector3.ZERO)
	for v in faces:
		box = box.expand(v)
	return box


# Решётка закрывает проём: AABB перекрывает прямоугольник проёма и стоит в стене; коллизии нет.
func check_gate_portcullis(zone: Node) -> void:
	var portcullis := zone.get_node_or_null("Portcullis") as Node3D
	if portcullis == null:
		failed += 1
		print("ПРОВАЛ у Portcullis нет узла")
		return
	var box := prop_world_aabb(portcullis)
	var half := GATE_OPENING_WIDTH * 0.5
	if box.position.z <= -half and box.end.z >= half and box.position.y <= GATE_BOX_EPS and box.end.y >= GATE_OPENING_HEIGHT - GATE_BOX_EPS and box.position.x >= CAVE_OPEN_X:
		print("ok: решётка перекрывает проём: z %.2f..%.2f, y %.2f..%.2f, x от %.2f" % [box.position.z, box.end.z, box.position.y, box.end.y, box.position.x])
	else:
		failed += 1
		print("ПРОВАЛ решётка не перекрывает проём %.1fx%.1f: z %.2f..%.2f, y %.2f..%.2f, x от %.2f"
			% [GATE_OPENING_WIDTH, GATE_OPENING_HEIGHT, box.position.z, box.end.z, box.position.y, box.end.y, box.position.x])
	# T3: собственная коллизия решётки — AnimatableBody3D с коробкой по AABB меша.
	# До T3 здесь стояла временная проверка, ЗАПРЕЩАВШАЯ коллизию («её ставит задача 3»):
	# направление поменяно на требование, иначе проём оставался бы «проходимым».
	if portcullis.is_class("AnimatableBody3D") and count_of_class(portcullis, "CollisionShape3D") > 0 and aabb_close(body_box(portcullis), box):
		print("ok: у решётки есть коллизия (задача 3 выполнена): AnimatableBody3D, коробка по AABB меша %s" % str(box))
	else:
		failed += 1
		print("ПРОВАЛ у решётки нет коллизии: нужен AnimatableBody3D с CollisionShape3D по AABB меша (в сцене коробка %s)"
			% str(body_box(portcullis)))


# Решётка закрыта на старте и держит проём: под ней капсула не проходит.
# Физическая проверка, поэтому зона уже в дереве (см. check_gate_entrance).
func check_gate_portcullis_closed(zone: Node) -> void:
	var portcullis := zone.get_node_or_null("Portcullis")
	if portcullis == null or not portcullis.has_method("is_open") or not portcullis.has_method("open"):
		failed += 1
		print("ПРОВАЛ у Portcullis нет механики подъёма (нужны open() и is_open())")
		return
	if not portcullis.is_open():
		print("ok: решётка закрыта на старте: is_open() == false")
	else:
		failed += 1
		print("ПРОВАЛ решётка открыта на старте: is_open() == true")
	var grate_face: float = prop_world_aabb(portcullis as Node3D).position.x
	var end := await push_capsule(zone, PORTCULLIS_PUSH_FRAMES)
	var travelled := capsule_travel(end)
	if travelled < PORTCULLIS_MIN_TRAVEL:
		failed += 1
		print("ПРОВАЛ капсула не проехала к решётке: путь %.2f м < %.2f" % [travelled, PORTCULLIS_MIN_TRAVEL])
	if end.x >= grate_face:
		print("ok: капсула не проходит сквозь закрытую решётку: конец x %.2f >= внутренняя грань %.2f" % [end.x, grate_face])
	else:
		failed += 1
		print("ПРОВАЛ капсула прошла сквозь закрытую решётку: конец x %.2f < внутренняя грань %.2f" % [end.x, grate_face])


# open() поднимает решётку на open_height, повторный вызов ничего не добавляет, проход открыт.
func check_gate_portcullis_open(zone: Node) -> void:
	var portcullis := zone.get_node_or_null("Portcullis")
	if portcullis == null or not portcullis.has_method("open") or not portcullis.has_method("is_open"):
		return   # провал уже выведен в check_gate_portcullis_closed
	var closed_y: float = (portcullis as Node3D).position.y
	portcullis.open()
	portcullis.open()   # повторный вызов на середине подъёма
	var frames := 0
	while frames < PORTCULLIS_RAISE_FRAME_CAP and not portcullis.is_open():
		await physics_frame
		frames += 1
	var raised: float = (portcullis as Node3D).position.y - closed_y
	if frames < PORTCULLIS_RAISE_FRAME_CAP and absf(raised - PORTCULLIS_OPEN_HEIGHT) <= GATE_BOX_EPS and portcullis.is_open():
		print("ok: open() поднял решётку на %.2f м за %d физ. кадров, is_open() == true" % [raised, frames])
	else:
		failed += 1
		print("ПРОВАЛ open(): подъём на %.2f м (нужно %.2f), is_open() %s, ждал %d физ. кадров"
			% [raised, PORTCULLIS_OPEN_HEIGHT, str(portcullis.is_open()), frames])
	# Третий вызов — уже после полного подъёма: подъём должен остаться ровно open_height.
	portcullis.open()
	for i in PORTCULLIS_REPEAT_FRAMES:
		await physics_frame
	var after_repeat: float = (portcullis as Node3D).position.y - closed_y
	if after_repeat <= PORTCULLIS_OPEN_HEIGHT + GATE_BOX_EPS:
		print("ok: повторный open() ничего не добавил: подъём после трёх вызовов %.2f м" % after_repeat)
	else:
		failed += 1
		print("ПРОВАЛ повторный open() накопил подъём: %.2f м > %.2f" % [after_repeat, PORTCULLIS_OPEN_HEIGHT])
	# Границы подъёма (пока решётка поднята): встать под верх ниши и оставить проход для капсулы.
	check_raised_grate_niche(portcullis as Node3D)
	var end := await push_capsule(zone, PORTCULLIS_PUSH_FRAMES)
	var travelled := capsule_travel(end)
	if travelled < PORTCULLIS_MIN_TRAVEL:
		failed += 1
		print("ПРОВАЛ капсула не проехала к воротам: путь %.2f м < %.2f" % [travelled, PORTCULLIS_MIN_TRAVEL])
	if end.x <= PORTCULLIS_PASSED_X:
		print("ok: капсула проходит сквозь поднятую решётку: конец x %.2f <= %.2f" % [end.x, PORTCULLIS_PASSED_X])
	else:
		failed += 1
		print("ПРОВАЛ капсула не прошла поднятую решётку: конец x %.2f > %.2f" % [end.x, PORTCULLIS_PASSED_X])
	# Возвращаем закрытое положение: мерки AABB решётки не должны зависеть от порядка вызовов.
	(portcullis as Node3D).position.y = closed_y


# Границы подъёма решётки (T3-д). Дефект, найденный в T3: при ходе 3.5 м верх решётки доходил до
# y = 8.51, а ниша-дымоход вырезана в породе только до y = 8.0 — верхние полметра уходили в
# сплошную породу. Проверка фиксирует ОБЕ границы, а не «просто проходит»:
#   - верх поднятой решётки не выше верха ниши; верх ниши МЕРЯЕТСЯ по геометрии оболочки
#     (cave_surface_y над PORTCULLIS_NICHE_PROBE), а не берётся константой — иначе дефект можно
#     вернуть, не зная ниши. CAVE_NICHE_TOP — контроль чувствительности пробы;
#   - зазор снизу (низ поднятой решётки) — не меньше капсулы плюс запас на голову.
func check_raised_grate_niche(portcullis: Node3D) -> void:
	var box := prop_world_aabb(portcullis)
	var niche_top: float = cave_surface_y(get_cave_tris(), PORTCULLIS_NICHE_PROBE.x, PORTCULLIS_NICHE_PROBE.y)
	var gap := box.position.y
	var bad: Array[String] = []
	if not is_finite(niche_top) or absf(niche_top - CAVE_NICHE_TOP) > CAVE_NICHE_EPS:
		bad.append("верх ниши %.2f м вместо %.2f — проба не нашла нишу (x %.2f, z %.2f)"
			% [niche_top, CAVE_NICHE_TOP, PORTCULLIS_NICHE_PROBE.x, PORTCULLIS_NICHE_PROBE.y])
	if box.end.y > niche_top:
		bad.append("верх решётки %.2f м выше верха ниши %.2f м (ход слишком большой)" % [box.end.y, niche_top])
	var needed := PORTCULLIS_CAPSULE_HEIGHT + PORTCULLIS_HEADROOM_MIN
	if gap < needed:
		bad.append("зазор под решёткой %.2f м < капсула %.1f + запас %.1f = %.2f м"
			% [gap, PORTCULLIS_CAPSULE_HEIGHT, PORTCULLIS_HEADROOM_MIN, needed])
	if bad.is_empty():
		print("ok: границы подъёма: решётка y %.2f..%.2f, верх ниши %.2f (запас %.2f м), зазор снизу %.2f м >= %.2f м"
			% [box.position.y, box.end.y, niche_top, niche_top - box.end.y, gap, needed])
	else:
		failed += 1
		print("ПРОВАЛ границы подъёма решётки: %s" % "; ".join(bad))


# Путь капсулы по плоскости XZ от старта прогона: вертикаль в этой пробе не участвует.
func capsule_travel(end: Vector3) -> float:
	return Vector2(end.x - PORTCULLIS_START.x, end.z - PORTCULLIS_START.z).length()


# Прогон капсулы игрока через ворота по -X (из двора в тоннель); вертикаль не участвует —
# низ капсулы на 0.05 м выше пола двора, как в check_movement. Возвращает конечную позицию.
func push_capsule(zone: Node, frames: int) -> Vector3:
	var body := CharacterBody3D.new()
	body.name = "ProbeCapsule"
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = PORTCULLIS_CAPSULE_RADIUS
	capsule.height = PORTCULLIS_CAPSULE_HEIGHT
	shape.shape = capsule
	shape.position = Vector3(0.0, PORTCULLIS_CAPSULE_HEIGHT * 0.5, 0.0)
	body.add_child(shape)
	zone.add_child(body)
	body.global_position = PORTCULLIS_START
	await physics_frame   # тело должно встать в физический мир до первого move_and_slide
	var forward := Vector3(-1.0, 0.0, 0.0)
	for i in frames:
		body.velocity = forward * CONTROLLER_SCRIPT.SPEED
		body.move_and_slide()
		await physics_frame
	var end := body.global_position
	print("info: капсула (прогон %d): старт (%.2f, %.2f, %.2f), конец (%.2f, %.2f, %.2f), путь по XZ %.2f м, шагов %d"
		% [frames, PORTCULLIS_START.x, PORTCULLIS_START.y, PORTCULLIS_START.z, end.x, end.y, end.z, capsule_travel(end), frames])
	zone.remove_child(body)
	body.free()
	return end


# Капсула игрока для пробы зоны рычага: тот же размер, что у персонажа уровня, и то же
# соглашение — начало узла это НИЗ капсулы, поэтому точка стояния задаётся низом, а тело
# растёт вверх на PORTCULLIS_CAPSULE_HEIGHT. Скорость не гасится (см. check_movement):
# капсула стоит на месте и не участвует в движении.
func spawn_probe_capsule(zone: Node, at: Vector3) -> CharacterBody3D:
	var body := CharacterBody3D.new()
	body.name = "LeverProbeCapsule"
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = PORTCULLIS_CAPSULE_RADIUS
	capsule.height = PORTCULLIS_CAPSULE_HEIGHT
	shape.shape = capsule
	shape.position = Vector3(0.0, PORTCULLIS_CAPSULE_HEIGHT * 0.5, 0.0)
	body.add_child(shape)
	zone.add_child(body)
	body.global_position = at
	body.velocity = Vector3.ZERO
	return body


func drop_probe_capsule(zone: Node, body: Node) -> void:
	zone.remove_child(body)
	(body as Node).free()


# Переставить капсулу и дождаться, пока Area3D пересчитает пересечения.
func move_probe_capsule(body: CharacterBody3D, at: Vector3) -> void:
	body.global_position = at
	body.velocity = Vector3.ZERO


# Рычаг (T4): скрипт, зона действия, физическая клавиша E, одно срабатывание.
func check_gate_lever(zone: Node) -> void:
	check_lever_setup(zone)
	await check_lever_mechanics(zone)


# Статическая часть рычага: скрипт lever.gd с try_use, Area3D зоны действия нужного
# габарита, portcullis_path, ведущий на Portcullis, и физическая клавиша E в исходнике.
func check_lever_setup(zone: Node) -> void:
	var lever := zone.get_node_or_null(LEVER_NODE)
	var portcullis := zone.get_node_or_null("Portcullis")
	var bad: Array[String] = []
	if lever == null or not (lever is Node3D):
		failed += 1
		print("ПРОВАЛ рычаг: нет узла %s" % LEVER_NODE)
		return
	var script: Variant = (lever as Node3D).get_script()
	if script == null or script.resource_path != LEVER_SCRIPT_PATH:
		bad.append("скрипт %s, ожидался %s" % [str(script.resource_path) if script != null else "нет", LEVER_SCRIPT_PATH])
	elif not (lever as Node3D).has_method("try_use"):
		bad.append("в %s нет метода try_use" % LEVER_SCRIPT_PATH)

	var zone_node := (lever as Node3D).get_node_or_null(LEVER_ZONE)
	if zone_node == null or not (zone_node is Area3D):
		bad.append("нет узла зоны действия %s/%s типа Area3D" % [LEVER_NODE, LEVER_ZONE])
	elif not zone_node.monitoring:
		bad.append("зона %s/%s не наблюдает тела (monitoring выключен)" % [LEVER_NODE, LEVER_ZONE])
	else:
		bad.append_array(lever_zone_size_bad(zone_node as Area3D))

	var path: Variant = (lever as Node3D).get("portcullis_path")   # null, если скрипта нет
	if path == null or (path as NodePath).is_empty():
		bad.append("не задан экспорт portcullis_path")
	elif (lever as Node3D).get_node_or_null(path) != portcullis:
		bad.append("portcullis_path %s ведёт не на Portcullis" % str(path))

	bad.append_array(lever_key_bad())

	if bad.is_empty():
		print("ok: рычаг: скрипт %s, зона %s, portcullis_path %s, клавиша %s"
			% [LEVER_SCRIPT_PATH, lever_zone_desc(zone_node as Area3D), str(path), LEVER_KEY_CALL])
	else:
		failed += 1
		print("ПРОВАЛ рычаг (устройство): %s" % "; ".join(bad))


# Габарит зоны действия: накрывает место стояния, но не всю караулку, и по высоте
# достаёт от пола до макушки капсулы. Меряется по мировой коробке зоны (в координатах
# корня зоны), потому что UseZone смещена относительно рычага.
func lever_zone_size_bad(zone_node: Area3D) -> Array[String]:
	var bad: Array[String] = []
	var box := zone_world_box(zone_node)
	if box.size.x <= 0.0 or box.size.z <= 0.0 or box.size.y <= 0.0:
		return ["зона %s без формы (мировая коробка %s)" % [LEVER_ZONE, str(box)]]
	for axis in [box.size.x, box.size.z]:
		var half: float = axis * 0.5
		if half < LEVER_ZONE_HALF_MIN or half > LEVER_ZONE_HALF_MAX:
			bad.append("половина зоны по XZ %.2f м вне %.2f-%.2f" % [half, LEVER_ZONE_HALF_MIN, LEVER_ZONE_HALF_MAX])
	if box.position.y > LEVER_ZONE_FLOOR_MAX:
		bad.append("низ зоны y %.2f: капсула в зону снизу не встанет" % box.position.y)
	if box.end.y < PORTCULLIS_CAPSULE_HEIGHT:
		bad.append("верх зоны y %.2f ниже роста капсулы %.2f" % [box.end.y, PORTCULLIS_CAPSULE_HEIGHT])
	return bad


# Коробка зоны в МИРОВЫХ координатах, в системе корня сцены-зоны (зона в дереве, а её
# масштаб несёт узел Lever — 1.04, поэтому transform относительно родителя не годится).
func zone_world_box(zone_node: Area3D) -> AABB:
	var shape_node: CollisionShape3D = null
	for child in zone_node.get_children():
		if child is CollisionShape3D and (child as CollisionShape3D).shape != null:
			shape_node = child
			break
	if shape_node == null:
		return AABB()
	var xf := zone_node.global_transform * shape_node.transform
	if shape_node.shape is BoxShape3D:
		var size: Vector3 = (shape_node.shape as BoxShape3D).size
		return xf * AABB(-size * 0.5, size)
	return AABB(shape_node.global_position - Vector3.ONE, Vector3(2.0, 2.0, 2.0))


func lever_zone_desc(zone_node: Area3D) -> String:
	var box := zone_world_box(zone_node)
	return "%s (%.2f x %.2f x %.2f м, пол %.2f..%.2f)" % [LEVER_ZONE, box.size.x, box.size.y, box.size.z, box.position.y, box.end.y]


# Клавиша взаимодействия — ФИЗИЧЕСКАЯ E (AGENTS.md), и не через событие _input. В headless
# состояние клавиши нельзя подделать: проба (temp/t4_probe.txt) показала, что
# Input.parse_input_event не меняет Input.is_physical_key_pressed — ни с одним
# сочетанием keycode/physical_keycode. Поэтому требование проверяется по исходнику скрипта:
# это единственный способ не оставить клавишу непроверенной вовсе.
func lever_key_bad() -> Array[String]:
	var bad: Array[String] = []
	if not FileAccess.file_exists(LEVER_SCRIPT_PATH):
		return ["файла скрипта нет: %s" % LEVER_SCRIPT_PATH]
	var src := FileAccess.get_file_as_string(LEVER_SCRIPT_PATH)
	if not src.contains(LEVER_KEY_CALL):
		bad.append("в %s нет вызова %s" % [LEVER_SCRIPT_PATH, LEVER_KEY_CALL])
	if src.contains("is_key_pressed("):
		bad.append("в %s есть логическая is_key_pressed(" % LEVER_SCRIPT_PATH)
	if src.contains("_unhandled_input") or src.contains("func _input("):
		bad.append("в %s клавиша читается через событие _input, а не опросом" % LEVER_SCRIPT_PATH)
	return bad


# Механика рычага. Проба идёт ПО ЦЕПОЧКЕ: пересечение капсулы с Area3D -> body_entered ->
# флаг «игрок в зоне» -> опрос физической клавиши (фронт нажатия) -> try_use() -> Portcullis.open().
# Клавишу в headless подделать нельзя (temp/t4_probe.txt), поэтому на время пробы рычагу
# отключён СВОЙ опрос ввода, а состояние клавиши передаётся аргументом poll_interaction.
# Без отключения проба врала бы: между её шагами идут await physics_frame, за них рычаг
# опрашивал бы настоящий Input (в headless он всегда отпущен) и каждый раз «отпускал»
# зажатую клавишу — фронт нажатия слезал бы и удержание выглядело бы ненажатием.
# Приём тот же, что в check_movement: клавиатуру игнорируем, логику гоняем сами.
func check_lever_mechanics(zone: Node) -> void:
	var lever := zone.get_node_or_null(LEVER_NODE)
	var portcullis := zone.get_node_or_null("Portcullis")
	var zone_node := zone.get_node_or_null(LEVER_NODE + "/" + LEVER_ZONE)
	if lever == null or portcullis == null or zone_node == null:
		failed += 1
		print("ПРОВАЛ рычаг (механика не проверялась): нет узлов %s, Portcullis или %s/%s"
			% [LEVER_NODE, LEVER_NODE, LEVER_ZONE])
		return
	var missing: Array[String] = []
	if not lever.has_method("try_use") or not lever.has_method("poll_interaction"):
		missing.append("нет try_use()/poll_interaction()")
	# Проба обязана начинаться с закрытой решётки: иначе подъём на open_height неотличим
	# от «уже поднята», и проверка прошла бы вхолостую (дефект, найденный в T3-д).
	if portcullis.is_open():
		missing.append("решётка уже открыта на входе пробы: y %.4f" % portcullis.position.y)
	if not missing.is_empty():
		failed += 1
		print("ПРОВАЛ рычаг (механика не проверялась): %s" % "; ".join(missing))
		return

	var closed_y: float = portcullis.position.y
	print("info: рычаг: вход в пробу — решётка закрыта на y %.4f, is_open() %s" % [closed_y, str(portcullis.is_open())])
	lever.set_physics_process(false)
	var capsule := spawn_probe_capsule(zone, LEVER_TUNNEL)
	await physics_frame
	await physics_frame

	# 1. Вне зоны try_use() ничего не делает.
	var outside = lever.try_use(false)
	if outside == false and portcullis.position.y == closed_y and not portcullis.is_open():
		print("ok: рычаг вне зоны: try_use(false) -> false, решётка на y %.4f не двинулась" % closed_y)
	else:
		failed += 1
		print("ПРОВАЛ рычаг вне зоны: try_use(false) -> %s, решётка y %.4f (было %.4f)" % [str(outside), portcullis.position.y, closed_y])

	# 2. Зона не накрывает тоннель у ворот, и удержание E вне зоны ничего не делает.
	#    Про статические тела в зоне (порода, стены) в счёт не идут: важно лишь, где КАПСУЛА.
	var in_tunnel: Array = await wait_overlaps(zone_node, capsule)
	if not in_tunnel.has(capsule):
		print("ok: зона не накрывает тоннель: капсула на (%.2f, %.2f, %.2f) вне %s (тела в зоне: %s)"
			% [LEVER_TUNNEL.x, LEVER_TUNNEL.y, LEVER_TUNNEL.z, LEVER_ZONE, body_names(in_tunnel)])
	else:
		failed += 1
		print("ПРОВАЛ зона рычага накрывает тоннель: капсула на (%.2f, %.2f, %.2f) попала в %s" % [LEVER_TUNNEL.x, LEVER_TUNNEL.y, LEVER_TUNNEL.z, LEVER_ZONE])
	lever.poll_interaction(true)   # игрок ДЕРЖИТ E, стоя в тоннеле
	if not portcullis.is_open() and lever.used == false:
		print("ok: удержание E вне зоны: решётка закрыта, used == false")
	else:
		failed += 1
		print("ПРОВАЛ удержание E вне зоны сработало: is_open() %s, used %s" % [str(portcullis.is_open()), str(lever.used)])

	# 3. Капсула реально попадает в зону; E всё ещё зажата с прошлого шага — вход в зону
	#    не должен «дозарядить» рычаг (фронт нажатия был ДО входа в зону).
	move_probe_capsule(capsule, LEVER_STAND)
	var in_zone: Array = await wait_overlaps(zone_node, capsule)
	if in_zone.has(capsule):
		print("ok: зона рычага ловит капсулу: тело в %s на (%.2f, %.2f, %.2f), зона %s"
			% [LEVER_ZONE, LEVER_STAND.x, LEVER_STAND.y, LEVER_STAND.z, lever_zone_desc(zone_node)])
	else:
		failed += 1
		print("ПРОВАЛ зона рычага не поймала капсулу: тело на (%.2f, %.2f, %.2f) вне %s" % [LEVER_STAND.x, LEVER_STAND.y, LEVER_STAND.z, LEVER_ZONE])
	lever.poll_interaction(true)   # E всё ещё нажата: это «удержание», а не нажатие
	if not lever.used and not portcullis.is_open():
		print("ok: вход в зону на зажатой E не срабатывает: used == false, решётка закрыта")
	else:
		failed += 1
		print("ПРОВАЛ вход в зону на зажатой E сработал: used %s, is_open() %s" % [str(lever.used), str(portcullis.is_open())])

	# 4. Отпустил и нажал в зоне — решётка поднимается.
	lever.poll_interaction(false)
	var fired = lever.poll_interaction(true)
	if fired and lever.used:
		print("ok: нажатие E в зоне: poll_interaction(true) -> true, used == true")
	else:
		failed += 1
		print("ПРОВАЛ нажатие E в зоне: poll_interaction(true) -> %s, used %s" % [str(fired), str(lever.used)])
	var frames := 0
	while frames < PORTCULLIS_RAISE_FRAME_CAP and not portcullis.is_open():
		await physics_frame
		frames += 1
	var raised: float = portcullis.position.y - closed_y
	if portcullis.is_open() and absf(raised - PORTCULLIS_OPEN_HEIGHT) <= GATE_BOX_EPS:
		print("ok: рычаг поднял решётку на %.2f м за %d физ. кадров, is_open() == true" % [raised, frames])
	else:
		failed += 1
		print("ПРОВАЛ рычаг не поднял решётку: подъём на %.2f м (нужно %.2f), is_open() %s, ждал %d физ. кадров"
			% [raised, PORTCULLIS_OPEN_HEIGHT, str(portcullis.is_open()), frames])
	portcullis.position.y = closed_y + raised   # решение is_open() — по position, не по флагу

	# 5. Рычаг уже использован: ни удержание E, ни повторный try_use() ничего не делают.
	for i in LEVER_HOLD_FRAMES:
		lever.poll_interaction(true)
	await physics_frame
	var repeat = lever.try_use(true)
	var again = lever.try_use(false)
	if not repeat and not again and absf(portcullis.position.y - (closed_y + raised)) <= POSITION_EPS:
		print("ok: повтор не срабатывает: удержание E %d кадров, try_use(true) -> false, try_use(false) -> false, решётка осталась на подъёме %.2f м"
			% [LEVER_HOLD_FRAMES, raised])
	else:
		failed += 1
		print("ПРОВАЛ повторное срабатывание: try_use(true) -> %s, try_use(false) -> %s, решётка y %.4f (ожидалась %.4f)"
			% [str(repeat), str(again), portcullis.position.y, closed_y + raised])

	# 6. Зона не накрывает двор: капсулу уносят к MerchantSpot.
	move_probe_capsule(capsule, LEVER_YARD)
	var in_yard: Array = await wait_overlaps(zone_node, capsule)
	if not in_yard.has(capsule):
		print("ok: зона не накрывает двор: капсула на (%.2f, %.2f, %.2f) вне %s (тела в зоне: %s)"
			% [LEVER_YARD.x, LEVER_YARD.y, LEVER_YARD.z, LEVER_ZONE, body_names(in_yard)])
	else:
		failed += 1
		print("ПРОВАЛ зона рычага накрывает двор: капсула на (%.2f, %.2f, %.2f) попала в %s" % [LEVER_YARD.x, LEVER_YARD.y, LEVER_YARD.z, LEVER_ZONE])

	drop_probe_capsule(zone, capsule)
	lever.set_physics_process(true)
	portcullis.position.y = closed_y


# Имена тел, пересекающих зону, — для info-строк: важно знать, ЧТО именно попало в зону
# (капсула игрока или стена караулки), а не только сколько.
func body_names(bodies: Array) -> String:
	var names: Array[String] = []
	for body in bodies:
		names.append(str(body.name))
	if names.is_empty():
		return "нет"
	names.sort()   # get_overlapping_bodies() не обещает порядок, а лог должен быть детерминирован
	return ", ".join(names)


# Тела, пересекающие Area3D, после LEVER_ZONE_SETTLE_FRAMES физических кадров.
func wait_overlaps(zone_node: Area3D, body: CharacterBody3D) -> Array:
	for i in LEVER_ZONE_SETTLE_FRAMES:
		await physics_frame
	return zone_node.get_overlapping_bodies()


# Решётка не врезана в коллизии зоны: её AABB не пересекает ни один StaticBody3D
# (коробки и trimesh оболочки; пересечение — объём больше GATE_BOX_EPS по всем осям).
func check_gate_portcullis_clear(zone: Node) -> void:
	var portcullis := zone.get_node_or_null("Portcullis") as Node3D
	if portcullis == null:
		return
	var box := prop_world_aabb(portcullis)
	var colliders: Array = []
	var total_colliders: Array = []
	collect_colliders(zone, Transform3D.IDENTITY, total_colliders)
	# Свою коробку решётки (T3) исключаем: она по построению совпадает с AABB меша, о котором
	# идёт речь, и иначе проверка всегда находила бы «пересечение сама с собой».
	for entry in total_colliders:
		if not is_within(portcullis, entry[3]):
			colliders.append(entry)
	var hits: Array[String] = []
	for entry in colliders:
		if shape_hits_box(entry[1], entry[0], box):
			hits.append(entry[2])
	if hits.is_empty():
		print("ok: решётка не пересекает коллизии зоны (проверено %d фигур, всего в зоне %d)" % [colliders.size(), total_colliders.size()])
	else:
		failed += 1
		print("ПРОВАЛ решётка пересекает коллизии: %s" % ", ".join(hits))


# Коллизионные фигуры поддерева: [трансформ в координатах корня, shape, имя тела, узел тела].
func collect_colliders(node: Node, parent_xf: Transform3D, out: Array) -> void:
	var xf := parent_xf
	if node is Node3D:
		xf = parent_xf * (node as Node3D).transform
	if node is CollisionShape3D and (node as CollisionShape3D).shape != null:
		out.append([xf, (node as CollisionShape3D).shape, node.get_parent().name, node.get_parent()])
	for child in node.get_children():
		collect_colliders(child, xf, out)


# Внутри ли поддерева root узел node.
func is_within(root: Node, node: Node) -> bool:
	var current := node
	while current != null:
		if current == root:
			return true
		current = current.get_parent()
	return false


# Пересекает ли фигура коробку: для BoxShape3D — её AABB, для trimesh — каждый треугольник.
func shape_hits_box(shape: Shape3D, xf: Transform3D, box: AABB) -> bool:
	if shape is BoxShape3D:
		var size := (shape as BoxShape3D).size
		return aabb_overlaps(xf * AABB(-size * 0.5, size), box)
	if shape is ConcavePolygonShape3D:
		var faces := (shape as ConcavePolygonShape3D).get_faces()
		for i in range(0, faces.size(), 3):
			var tri := AABB(xf * faces[i], Vector3.ZERO).expand(xf * faces[i + 1]).expand(xf * faces[i + 2])
			if aabb_overlaps(tri, box):
				return true
	return false


# Объёмное пересечение двух AABB больше GATE_BOX_EPS по каждой оси (касание не считается).
func aabb_overlaps(a: AABB, b: AABB) -> bool:
	var lo := a.position.max(b.position)
	var hi := a.end.min(b.end)
	return hi.x - lo.x > GATE_BOX_EPS and hi.y - lo.y > GATE_BOX_EPS and hi.z - lo.z > GATE_BOX_EPS


# Стол лежит набок: поворот 90° вокруг X (высота стола, ось Y меша, легла вдоль Z), низ AABB на y=0.
func check_gate_table(zone: Node) -> void:
	var table := zone.get_node_or_null("Table") as Node3D
	if table == null:
		failed += 1
		print("ПРОВАЛ у Table нет узла")
		return
	var box := prop_world_aabb(table)
	var lying := table.transform.basis.y.normalized().distance_to(Vector3.BACK) <= GATE_BOX_EPS
	if lying and absf(box.position.y) <= GATE_BOX_EPS:
		print("ok: стол лежит набок (поворот 90° вокруг X), низ AABB на y %.4f" % box.position.y)
	else:
		failed += 1
		print("ПРОВАЛ стол: лежит набок %s, низ AABB на y %.4f" % [str(lying), box.position.y])


# Крупный реквизит: коробка коллизии совпадает с AABB меша.
func check_gate_colliders(zone: Node) -> void:
	var bad: Array[String] = []
	for pair in GATE_BOXED_PROPS:
		var prop_name: String = pair[0]
		var body_name: String = pair[1]
		var prop := zone.get_node_or_null(prop_name) as Node3D
		var body := zone.get_node_or_null(body_name) as StaticBody3D
		if prop == null or body == null or not has_box_shape(body):
			bad.append(prop_name)
		elif not aabb_close(body_box(body), prop_world_aabb(prop)):
			bad.append(prop_name)
	if bad.is_empty():
		print("ok: коллизии крупного реквизита совпадают с AABB мешей (%d)" % GATE_BOXED_PROPS.size())
	else:
		failed += 1
		print("ПРОВАЛ коллизия не совпадает с AABB меша или отсутствует: %s" % ", ".join(bad))


# Арка в проёме: масштаб, просвет и свод по мешу (сечения в мировых координатах), решётка
# под перемычкой, коллизии ног и перемычки совпадают с AABB частей меша.
func check_gate_arch(zone: Node) -> void:
	var arch := zone.get_node_or_null("Arch") as Node3D
	if arch == null:
		failed += 1
		print("ПРОВАЛ у Arch нет узла")
		return
	var arch_basis := arch.transform.basis
	if absf(arch_basis.x.length() - ARCH_SCALE) <= 0.001 and absf(arch_basis.y.length() - ARCH_SCALE) <= 0.001 and absf(arch_basis.z.length() - ARCH_SCALE) <= 0.001:
		print("ok: арка: масштаб %.2f равномерный" % ARCH_SCALE)
	else:
		failed += 1
		print("ПРОВАЛ масштаб арки %.3f %.3f %.3f, нужен равномерный %.2f" % [arch_basis.x.length(), arch_basis.y.length(), arch_basis.z.length(), ARCH_SCALE])
	var packed := load(ARCH_GLB_PATH) as PackedScene
	if packed == null:
		failed += 1
		print("ПРОВАЛ арка не загрузилась: %s" % ARCH_GLB_PATH)
		return
	var model := packed.instantiate() as Node3D
	var model_faces := collect_faces(model, Transform3D.IDENTITY)
	model.free()
	var world := PackedVector3Array()
	for v in model_faces:
		world.append(arch.transform * v)
	var gap_min := INF
	var gap_h := 0.0
	var h := ARCH_SCAN_FROM
	while h <= ARCH_SCAN_TO + 0.0001:
		var zs := mesh_cut(world, 1, h, 0, ARCH_CUT_X)
		var left := -INF
		var right := INF
		for z in zs:
			if z < 0.0 and z > left:
				left = z
			if z > 0.0 and z < right:
				right = z
		var gap := right - left if left > -INF and right < INF else 0.0
		if gap < gap_min:
			gap_min = gap
			gap_h = h
		h += ARCH_SCAN_STEP
	if gap_min >= ARCH_GAP_MIN:
		print("ok: арка: просвет между ногами %.2f м (узкое место на высоте %.2f м) >= %.1f" % [gap_min, gap_h, ARCH_GAP_MIN])
	else:
		failed += 1
		print("ПРОВАЛ просвет арки %.2f м (высота %.2f м), нужно >= %.1f" % [gap_min, gap_h, ARCH_GAP_MIN])
	var lintel := INF
	var corner := INF
	for k in range(77):
		var c := -ARCH_PASSAGE_HALF + 0.05 * k
		var low := INF
		for y in mesh_cut(world, 2, c, 0, ARCH_CUT_X):
			if y > ARCH_CLEAR_FROM and y < low:
				low = y
		if low < corner:
			corner = low
		if absf(c) <= ARCH_CENTRE_HALF + 0.0001 and low < lintel:
			lintel = low
	if lintel >= ARCH_LINTEL_MIN:
		print("ok: арка: свод (низ перемычки в центре) %.2f м >= %.1f" % [lintel, ARCH_LINTEL_MIN])
	else:
		failed += 1
		print("ПРОВАЛ свод арки %.2f м, нужно >= %.1f" % [lintel, ARCH_LINTEL_MIN])
	print("info: арка: у внутренних углов ног низ перемычки %.2f м (край прохода, не норматив)" % corner)
	var portcullis := zone.get_node_or_null("Portcullis") as Node3D
	var grate_top := prop_world_aabb(portcullis).end.y if portcullis != null else INF
	if grate_top <= lintel:
		print("ok: верх решётки %.2f м <= низа перемычки %.2f м" % [grate_top, lintel])
	else:
		failed += 1
		print("ПРОВАЛ верх решётки %.2f м выше низа перемычки арки %.2f м" % [grate_top, lintel])
	var legs_l := PackedVector3Array()
	var legs_r := PackedVector3Array()
	var lintel_part := PackedVector3Array()
	for v in model_faces:
		var wv: Vector3 = arch.transform * v
		if v.y >= ARCH_SPLIT_Y:
			lintel_part.append(wv)
		elif v.x < 0.0:
			legs_l.append(wv)
		else:
			legs_r.append(wv)
	var parts := [legs_l, legs_r, lintel_part]
	var bad: Array[String] = []
	for i in ARCH_BODIES.size():
		var body := zone.get_node_or_null(ARCH_BODIES[i]) as StaticBody3D
		if body == null or not has_box_shape(body) or not aabb_close(body_box(body), faces_aabb(parts[i])):
			bad.append(ARCH_BODIES[i])
	if bad.is_empty():
		print("ok: коллизии арки (ноги и перемычка) совпадают с AABB частей меша (%d)" % ARCH_BODIES.size())
	else:
		failed += 1
		print("ПРОВАЛ коллизия арки не совпадает с AABB меша или отсутствует: %s" % ", ".join(bad))
	var box_l := body_box(zone.get_node("ArchLegLBody") as Node3D)
	var box_r := body_box(zone.get_node("ArchLegRBody") as Node3D)
	var box_gap := maxf(box_l.position.z - box_r.end.z, box_r.position.z - box_l.end.z)
	if box_gap >= ARCH_GAP_MIN:
		print("ok: коллизии ног: просвет между коробками %.2f м >= %.1f" % [box_gap, ARCH_GAP_MIN])
	else:
		failed += 1
		print("ПРОВАЛ коллизии ног: просвет между коробками %.2f м < %.1f" % [box_gap, ARCH_GAP_MIN])


# Вершины меша поддерева в координатах корня (без дерева сцены).
func collect_faces(node: Node, parent_xf: Transform3D) -> PackedVector3Array:
	var out := PackedVector3Array()
	var xf := parent_xf
	if node is Node3D:
		xf = parent_xf * (node as Node3D).transform
	if node is MeshInstance3D:
		for v in (node as MeshInstance3D).mesh.get_faces():
			out.append(xf * v)
	for child in node.get_children():
		out.append_array(collect_faces(child, xf))
	return out


# Сечение плоскостью axis = value; точки пересечения сечения с прямой line_axis = line_value.
# Возвращает координату третьей оси (отсортировано). Так меряются просвет и свод арки.
func mesh_cut(faces: PackedVector3Array, axis: int, value: float, line_axis: int, line_value: float) -> Array:
	var other := 3 - axis - line_axis
	var res: Array = []
	for i in range(0, faces.size(), 3):
		var pts: Array = []
		for e in [[0, 1], [1, 2], [2, 0]]:
			var p: Vector3 = faces[i + e[0]]
			var q: Vector3 = faces[i + e[1]]
			if (p[axis] - value >= 0.0) != (q[axis] - value >= 0.0):
				pts.append(p + (q - p) * ((value - p[axis]) / (q[axis] - p[axis])))
		if pts.size() != 2:
			continue
		var a: Vector3 = pts[0]
		var b: Vector3 = pts[1]
		var la: float = a[line_axis]
		var lb: float = b[line_axis]
		if (la - line_value) * (lb - line_value) <= 0.0 and la != lb:
			var t := (line_value - la) / (lb - la)
			res.append((a + (b - a) * t)[other])
	res.sort()
	return res


# Двор — ровная площадка, верх на y=0; торговец стоит на её поверхности.
func check_gate_yard(zone: Node) -> void:
	var yard := zone.get_node_or_null("Yard") as StaticBody3D
	var merchant := zone.get_node_or_null("MerchantSpot") as Node3D
	if yard == null or merchant == null or not has_box_shape(yard):
		failed += 1
		print("ПРОВАЛ нет двора (StaticBody3D с BoxShape3D) или MerchantSpot")
		return
	var top := body_box(yard).end.y
	if absf(top) <= GATE_BOX_EPS and absf(merchant.position.y - top) <= GATE_BOX_EPS:
		print("ok: MerchantSpot на поверхности двора: y %.4f, верх двора %.4f" % [merchant.position.y, top])
	else:
		failed += 1
		print("ПРОВАЛ MerchantSpot не на y≈0: y %.4f, верх двора %.4f" % [merchant.position.y, top])


# Двор T2r-b2: статуя основателя, торговая палатка, настенный факел.
# Общее для всех трёх — размеры, положение в границах двора и то, что меш взят из
# ожидаемого ассета; отличаются основанием (пол/стена) и видимостью из проёма.
func check_gate_yard_props(zone: Node) -> void:
	check_gate_statue(zone)
	check_gate_stall(zone)
	check_gate_torch(zone)


# Статуя: высота объекта вместе с постаментом, постамент ступенчатый ~3x3 м, скульптура
# стоит на нём без зазора, центр по z — по центру проёма, и статуя видна из зала.
func check_gate_statue(zone: Node) -> void:
	var statue := zone.get_node_or_null("FounderStatue") as Node3D
	if statue == null:
		failed += 1
		print("ПРОВАЛ у FounderStatue нет узла")
		return
	var bad: Array[String] = []
	bad.append_array(prop_mesh_problems(statue, STATUE_GLB))
	var box := prop_world_aabb(statue)
	if box.size.y < STATUE_H_MIN or box.size.y > STATUE_H_MAX:
		bad.append("высота с постаментом %.2f м вне %.1f-%.1f м" % [box.size.y, STATUE_H_MIN, STATUE_H_MAX])
	if absf(box.position.y) > YARD_PROP_EPS:
		bad.append("основание на y %.3f, а пол двора y=0" % box.position.y)
	if not yard_contains_box(box):
		bad.append("AABB %s выходит за границы двора" % str(box))
	var pedestal := statue.get_node_or_null("Pedestal") as Node3D
	var sculpture := statue.get_node_or_null("Sculpture") as Node3D
	var base_world := AABB()
	if pedestal == null or sculpture == null:
		bad.append("внутри FounderStatue нет узлов Pedestal и Sculpture")
	else:
		var steps := count_of_class(pedestal, "MeshInstance3D")
		var base := prop_world_aabb(pedestal)
		# prop_world_aabb не включает трансформ самого корня (соглашение функции), поэтому
		# скульптура и постамент меряются в одной системе координат FounderStatue, а в мир
		# переводятся её трансформом.
		var seat := prop_world_aabb(sculpture)
		var seat_world := statue.transform * seat
		if steps < STATUE_PEDESTAL_STEPS:
			bad.append("ступеней постамента %d, нужно >= %d" % [steps, STATUE_PEDESTAL_STEPS])
		if absf(base.size.x - STATUE_BASE_SIZE) > STATUE_BASE_TOL or absf(base.size.z - STATUE_BASE_SIZE) > STATUE_BASE_TOL:
			bad.append("постамент %.2f x %.2f м вместо %.1f x %.1f" % [base.size.x, base.size.z, STATUE_BASE_SIZE, STATUE_BASE_SIZE])
		if absf(seat.position.y - base.end.y) > STATUE_SEAT_EPS:
			bad.append("скульптура стоит на y %.3f, верх постамента y %.3f" % [seat.position.y, base.end.y])
		if absf(seat_world.get_center().z) > STATUE_CENTRE_Z:
			bad.append("центр скульптуры по z %.2f, нужно |z| <= %.1f" % [seat_world.get_center().z, STATUE_CENTRE_Z])
		base_world = statue.transform * base
		print("info: статуя: скульптура %.2f x %.2f x %.2f м, низ y %.2f, центр по z %.2f; постамент %d ступени %.2f x %.2f x %.2f м, верх y %.2f"
			% [seat_world.size.x, seat_world.size.y, seat_world.size.z, seat_world.position.y, seat_world.get_center().z,
			steps, base_world.size.x, base_world.size.y, base_world.size.z, base_world.end.y])
	bad.append_array(view_cone_bad(box))
	var blocked := sight_blocked(mesh_sample_points(sculpture, VIEW_SAMPLES, statue.transform), VIEW_EYE)
	if not blocked.is_empty():
		bad.append("луч от %s не доходит до %d точек скульптуры: %s" % [str(VIEW_EYE), blocked.size(), ", ".join(blocked)])
	if bad.is_empty():
		print("ok: статуя: высота с постаментом %.2f м в диапазоне %.1f-%.1f, ступенчатый постамент %.2f x %.2f м, AABB %s, видна из проёма"
			% [box.size.y, STATUE_H_MIN, STATUE_H_MAX, base_world.size.x, base_world.size.z, str(box)])
	else:
		failed += 1
		print("ПРОВАЛ статуя: %s" % "; ".join(bad))


# Торговая палатка: ~1 м, стоит на полу двора, в границах двора и не загораживает MerchantSpot.
func check_gate_stall(zone: Node) -> void:
	var stall := zone.get_node_or_null("Stall") as Node3D
	if stall == null:
		failed += 1
		print("ПРОВАЛ у Stall нет узла")
		return
	var bad: Array[String] = []
	bad.append_array(prop_mesh_problems(stall, STALL_GLB))
	var box := prop_world_aabb(stall)
	if box.size.y < PROP_H_MIN or box.size.y > PROP_H_MAX:
		bad.append("высота %.2f м вне %.1f-%.1f м" % [box.size.y, PROP_H_MIN, PROP_H_MAX])
	if absf(box.position.y) > YARD_PROP_EPS:
		bad.append("основание на y %.3f, а пол двора y=0" % box.position.y)
	if not yard_contains_box(box):
		bad.append("AABB %s выходит за границы двора" % str(box))
	var merchant := zone.get_node_or_null("MerchantSpot") as Node3D
	if merchant != null:
		var clear := box_distance_xz(merchant.position, box.get_center(), box.size)
		if clear < STALL_SPOT_CLEAR:
			bad.append("до MerchantSpot %.2f м, нужно >= %.1f" % [clear, STALL_SPOT_CLEAR])
	if bad.is_empty():
		print("ok: палатка: высота %.2f м в диапазоне %.1f-%.1f, на полу двора, AABB %s, до MerchantSpot >= %.1f м"
			% [box.size.y, PROP_H_MIN, PROP_H_MAX, str(box), STALL_SPOT_CLEAR])
	else:
		failed += 1
		print("ПРОВАЛ палатка: %s" % "; ".join(bad))


# Факел настенный: ~1 м, висит на высоте, вплотную к породе двора и виден из проёма.
func check_gate_torch(zone: Node) -> void:
	var torch := zone.get_node_or_null("WallTorch") as Node3D
	if torch == null:
		failed += 1
		print("ПРОВАЛ у WallTorch нет узла")
		return
	var bad: Array[String] = []
	bad.append_array(prop_mesh_problems(torch, TORCH_GLB))
	var box := prop_world_aabb(torch)
	if box.size.y < PROP_H_MIN or box.size.y > PROP_H_MAX:
		bad.append("высота %.2f м вне %.1f-%.1f м" % [box.size.y, PROP_H_MIN, PROP_H_MAX])
	if box.position.y < TORCH_MOUNT_MIN_Y or box.position.y > TORCH_MOUNT_MAX_Y:
		bad.append("низ y %.2f: настенный факел вешается на высоте %.1f-%.1f м, а не стоит на полу" % [box.position.y, TORCH_MOUNT_MIN_Y, TORCH_MOUNT_MAX_Y])
	if not yard_contains_box(box):
		bad.append("AABB %s выходит за границы двора" % str(box))
	var gap := minf(absf(CAVE_YARD_WALL_X - box.position.x), minf(absf(box.end.x - CAVE_YARD_FAR_X), minf(absf(-CAVE_YARD_HALF - box.position.z), absf(box.end.z - CAVE_YARD_HALF))))
	if gap > TORCH_WALL_GAP:
		bad.append("до ближайшей стены двора %.2f м, нужно <= %.2f (факел висит на rock)" % [gap, TORCH_WALL_GAP])
	bad.append_array(view_cone_bad(box))
	var blocked := sight_blocked(mesh_sample_points(torch, TORCH_SAMPLES), VIEW_EYE)
	if not blocked.is_empty():
		bad.append("луч от %s не доходит до %d точек факела: %s" % [str(VIEW_EYE), blocked.size(), ", ".join(blocked)])
	if bad.is_empty():
		print("ok: факел: высота %.2f м, навешен на %.2f-%.2f (зазор до породы %.2f м), AABB %s, виден из проёма"
			% [box.size.y, box.position.y, box.end.y, gap, str(box)])
	else:
		failed += 1
		print("ПРОВАЛ факел: %s" % "; ".join(bad))


# Проверки, общие для всех трёх объектов двора: в поддереве ровно один инстанс меша,
# он из ожидаемого ассета и масштаб по нему равномерный (как на арке). Проверяется узел
# с инстансом, а не корень: у FounderStatue масштаб несёт Sculpture. Проблемы
# возвращаются списком — счётчик failed считает вызывающая сторона, один провал на объект.
func prop_mesh_problems(node: Node3D, path: String) -> Array[String]:
	var bad: Array[String] = []
	var instances: Array = []
	collect_scene_instances(node, instances)
	if instances.size() != 1:
		bad.append("инстансов меша в поддереве %d, ожидался 1" % instances.size())
		return bad
	var mesh_node := instances[0] as Node3D
	if mesh_node.scene_file_path != path:
		bad.append("инстанс %s, ожидался %s" % [mesh_node.scene_file_path, path])
	var basis := mesh_node.transform.basis
	var scale := basis.x.length()
	if absf(basis.y.length() - scale) > 0.001 or absf(basis.z.length() - scale) > 0.001:
		bad.append("масштаб по осям %.3f %.3f %.3f, нужен равномерный" % [scale, basis.y.length(), basis.z.length()])
	return bad


func collect_scene_instances(node: Node, out: Array) -> void:
	if node.scene_file_path != "":
		out.append(node)
	for child in node.get_children():
		collect_scene_instances(child, out)


# AABB объекта целиком внутри вырубленного двора (стены x = 8/15, |z| = 4, допуск CAVE_WALL_MIN).
func yard_contains_box(box: AABB) -> bool:
	return box.position.x >= CAVE_YARD_WALL_X - CAVE_WALL_MIN and box.end.x <= CAVE_YARD_FAR_X + CAVE_WALL_MIN \
		and box.position.z >= -CAVE_YARD_HALF - CAVE_WALL_MIN and box.end.z <= CAVE_YARD_HALF + CAVE_WALL_MIN


# Конус обзора: проекция AABB на плоскость проёма (x = CAVE_YARD_WALL_X) из точки взгляда
# должна помещаться в проём мимо VIEW_MARGIN — «статуя по центру» (design.md:63).
func view_cone_bad(box: AABB) -> Array[String]:
	var bad: Array[String] = []
	var z_worst := 0.0
	var y_lo := INF
	var y_hi := -INF
	var behind := 0
	for corner in aabb_corners(box):
		if corner.x <= CAVE_YARD_WALL_X:
			behind += 1
			continue
		var cross := view_plane_hit(VIEW_EYE, corner)
		z_worst = maxf(z_worst, absf(cross.z))
		y_lo = minf(y_lo, cross.y)
		y_hi = maxf(y_hi, cross.y)
	if behind == aabb_corners(box).size():
		bad.append("объект целиком за плоскостью проёма x=%.1f" % CAVE_YARD_WALL_X)
		return bad
	var half := GATE_OPENING_WIDTH * 0.5
	if z_worst > half - VIEW_MARGIN:
		bad.append("силуэт выходит за проём: |z| %.2f на проёме, нужно <= %.2f" % [z_worst, half - VIEW_MARGIN])
	if y_lo < GATE_BOX_EPS or y_hi > GATE_OPENING_HEIGHT - VIEW_MARGIN:
		bad.append("силуэт не вписывается по высоте: y %.2f..%.2f на проёме, нужно %.2f..%.2f" % [y_lo, y_hi, GATE_BOX_EPS, GATE_OPENING_HEIGHT - VIEW_MARGIN])
	return bad


# Пересечение отрезка «взгляд -> точка» с плоскостью проёма.
func view_plane_hit(eye: Vector3, point: Vector3) -> Vector3:
	var f := (CAVE_YARD_WALL_X - eye.x) / (point.x - eye.x)
	return eye + (point - eye) * f


# Точки проверки видимости: углы AABB плюс детерминированная выборка вершин меша
# (шаг по индексу). Углы дают силуэт, выборка — реальную форму модели. `outer` —
# трансформ предка, в системе координат которого меряем (prop_world_aabb трансформ корня
# не включает, а лучи бьют по мировой породе).
func mesh_sample_points(node: Node3D, samples: int, outer: Transform3D = Transform3D.IDENTITY) -> PackedVector3Array:
	var out := PackedVector3Array()
	if node == null:
		return out
	for corner in aabb_corners(outer * prop_world_aabb(node)):
		out.append(corner)
	var verts := collect_faces(node, outer)
	if verts.is_empty() or samples <= 0:
		return out
	var step := maxi(1, verts.size() / samples)
	var i := 0
	while i < verts.size():
		out.append(verts[i])
		i += step
	return out


func aabb_corners(box: AABB) -> Array:
	return [
		Vector3(box.position.x, box.position.y, box.position.z),
		Vector3(box.end.x, box.position.y, box.position.z),
		Vector3(box.position.x, box.end.y, box.position.z),
		Vector3(box.end.x, box.end.y, box.position.z),
		Vector3(box.position.x, box.position.y, box.end.z),
		Vector3(box.end.x, box.position.y, box.end.z),
		Vector3(box.position.x, box.end.y, box.end.z),
		Vector3(box.end.x, box.end.y, box.end.z),
	]


# Точки объекта, до которых взгляд из eye не доходит: луч упирается в породу раньше точки.
# Луч идёт по породе (cave_rays), поэтому учитывается и стена у ворот, и весь коридор.
func sight_blocked(points: PackedVector3Array, eye: Vector3) -> Array[String]:
	var blocked: Array[String] = []
	if points.is_empty():
		return blocked
	var tris := get_cave_tris()
	if tris.is_empty():
		failed += 1
		print("ПРОВАЛ нечем проверить видимость: порода не прочиталась")
		return blocked
	# Отсев треугольников вне коридора лучей (по x) — породы за спиной и позади объекта
	# в лучах не участвуют.
	var x_hi := eye.x
	for point in points:
		x_hi = maxf(x_hi, point.x)
	var corridor: Array = []
	for tri in tris:
		var t_lo: float = tri[0].x
		var t_hi: float = t_lo
		for k in 3:
			t_lo = minf(t_lo, tri[k].x)
			t_hi = maxf(t_hi, tri[k].x)
		if t_hi >= eye.x - 0.5 and t_lo <= x_hi + 0.5:
			corridor.append(tri)
	for point in points:
		var dir := point - eye
		var dist := dir.length()
		if dist <= 0.001:
			continue
		var hits := cave_rays(corridor, eye, dir / dist, 1)
		if not hits.is_empty() and float(hits[0]) < dist - VIEW_SIGHT_EPS:
			blocked.append("(%.2f, %.2f, %.2f)" % [point.x, point.y, point.z])
	return blocked


# Треугольники породы: из check_cave_shell, иначе читаются напрямую из CAVE_GLB_PATH.
func get_cave_tris() -> Array:
	if not cave_tris_cache.is_empty():
		return cave_tris_cache
	var packed := load(CAVE_GLB_PATH) as PackedScene
	if packed == null:
		return [] as Array
	var shell := packed.instantiate()
	cave_tris_cache = cave_tris(collect_faces(shell, Transform3D.IDENTITY))
	shell.free()
	return cave_tris_cache


# AABB всех мешей поддерева в координатах узла-родителя (без дерева сцены).
func prop_world_aabb(node: Node3D) -> AABB:
	var parts: Array = []
	collect_mesh_aabbs(node, Transform3D.IDENTITY, parts)
	if parts.is_empty():
		return AABB()
	var result: AABB = parts[0]
	for i in range(1, parts.size()):
		result = result.merge(parts[i])
	return result


func collect_mesh_aabbs(node: Node, parent_xf: Transform3D, out: Array) -> void:
	var xf := parent_xf
	if node is Node3D:
		xf = parent_xf * (node as Node3D).transform
	if node is MeshInstance3D:
		out.append(xf * (node as MeshInstance3D).get_aabb())
	for child in node.get_children():
		collect_mesh_aabbs(child, xf, out)


# Мировая коробка StaticBody3D с BoxShape3D (тела без поворота).
func body_box(body: Node3D) -> AABB:
	for child in body.get_children():
		if child is CollisionShape3D and (child as CollisionShape3D).shape is BoxShape3D:
			var shape := (child as CollisionShape3D).shape as BoxShape3D
			var local := AABB(-shape.size * 0.5, shape.size)
			return (body.transform * (child as CollisionShape3D).transform) * local
	return AABB()


func has_box_shape(body: Node) -> bool:
	for child in body.get_children():
		if child is CollisionShape3D and (child as CollisionShape3D).shape is BoxShape3D:
			return true
	return false


func aabb_close(a: AABB, b: AABB) -> bool:
	return a.position.distance_to(b.position) <= GATE_BOX_EPS and a.size.distance_to(b.size) <= GATE_BOX_EPS


func count_nodes(node: Node) -> int:
	var count := 1
	for child in node.get_children():
		count += count_nodes(child)
	return count


# Узел Character типа CharacterBody3D; иначе null (провал выводится в check_character_body).
func character_of(level: Node) -> CharacterBody3D:
	return level.get_node_or_null(CHARACTER_NAME) as CharacterBody3D


# Число потомков заданного класса в поддереве.
func count_of_class(node: Node, cls: String) -> int:
	var count := 0
	for child in node.get_children():
		if child.is_class(cls):
			count += 1
		count += count_of_class(child, cls)
	return count


# Число MeshInstance3D в поддереве, видимых с учётом видимости предков.
func count_visible_meshes(node: Node) -> int:
	var count := 0
	for child in node.get_children():
		if child is MeshInstance3D and child.is_visible_in_tree():
			count += 1
		count += count_visible_meshes(child)
	return count


# Расстояние в плоскости XZ от точки до прямоугольника коробки; 0, если точка внутри.
func box_distance_xz(point: Vector3, box_center: Vector3, size: Vector3) -> float:
	var dx := maxf(absf(point.x - box_center.x) - size.x * 0.5, 0.0)
	var dz := maxf(absf(point.z - box_center.z) - size.z * 0.5, 0.0)
	return Vector2(dx, dz).length()


# Персонаж уровня: узел Character с инстансом из res://assets/kaykit_animations/ среди детей.
# Имя без пути инстанса не считается персонажем.
func has_character_instance(node: Node) -> bool:
	if node.name != CHARACTER_NAME:
		return false
	for child in node.get_children():
		if child.scene_file_path.begins_with(CHARACTER_PREFIX):
			return true
	return false


# 5. GridMapWall и GridMapFloor — прямые дети корня, GridMap с библиотекой нужного размера.
func check_grid_maps(level: Node) -> void:
	for grid_name in GRIDMAP_NAMES:
		check_grid_map(level, grid_name)


func check_grid_map(level: Node, grid_name: String) -> void:
	var grid: Node = level.get_node_or_null(grid_name)
	if grid == null or not (grid is GridMap):
		failed += 1
		print("ПРОВАЛ узла %s (GridMap) нет" % grid_name)
		return
	var gm := grid as GridMap
	var lib: MeshLibrary = gm.mesh_library
	if lib == null:
		failed += 1
		print("ПРОВАЛ у %s не загружена mesh_library" % grid_name)
		return
	var items := lib.get_item_list().size()
	if items != GRIDMAP_LIBRARY_ITEMS:
		failed += 1
		print("ПРОВАЛ %s: mesh_library элементов %d, ожидалось %d" % [grid_name, items, GRIDMAP_LIBRARY_ITEMS])
		return
	if gm.cell_size != GRIDMAP_CELL_SIZE:
		failed += 1
		print("ПРОВАЛ %s: cell_size %s, ожидалось %s" % [grid_name, str(gm.cell_size), str(GRIDMAP_CELL_SIZE)])
		return
	if grid_name == GRIDMAP_UPPER_NAME and not is_equal_approx(gm.position.y, GRIDMAP_UPPER_Y):
		failed += 1
		print("ПРОВАЛ %s: position.y %s, ожидалось %s" % [grid_name, str(gm.position.y), str(GRIDMAP_UPPER_Y)])
		return
	print("ok: %s, mesh_library с %d элементами, cell_size %s, ячеек %d" % [grid_name, items, str(gm.cell_size), gm.get_used_cells().size()])


# MeshInstance3D без инстанса сцены: узел, созданный прямо в level.tscn, а не модуль из .gltf.
func is_bare_mesh(node: Node) -> bool:
	return node is MeshInstance3D and node.scene_file_path == ""


# GridMap уровня: не модуль, а палитра ячеек; считается по имени и типу.
func is_grid_map(node: Node) -> bool:
	return GRIDMAP_NAMES.has(node.name) and node is GridMap


# kind инстанса по пути сцены; пустая строка, если узел не инстанс res://assets/kaykit/.
func kind_of(node: Node) -> String:
	var path: String = node.scene_file_path
	if not path.begins_with(MODEL_PREFIX) or not path.ends_with(MODEL_SUFFIX):
		return ""
	return path.trim_prefix(MODEL_PREFIX).trim_suffix(MODEL_SUFFIX)


# Первый MeshInstance3D в поддереве; null, если мешей нет.
func first_mesh_instance(node: Node) -> MeshInstance3D:
	if node is MeshInstance3D:
		return node
	for child in node.get_children():
		var found := first_mesh_instance(child)
		if found != null:
			return found
	return null


# Треугольники меша в фиксированном порядке: [[Vector3, Vector3, Vector3], ...].
func cave_tris(faces: PackedVector3Array) -> Array:
	var tris: Array = []
	for i in range(0, faces.size() - 2, 3):
		tris.append([faces[i], faces[i + 1], faces[i + 2]])
	return tris


# Габариты и ровность пола одной проходкой по треугольникам (ось Y вверх).
func cave_stats(tris: Array) -> Dictionary:
	var min_x := INF
	var max_x := -INF
	var min_y := INF
	var max_y := -INF
	var min_z := INF
	var max_z := -INF
	var min_pos_y := INF
	var floor_corners := 0
	var risers := 0
	var riser_min_r := INF
	for tri in tris:
		var tri_max_y := -INF
		var tri_min_r := INF
		var touches_floor := false
		for i in 3:
			var v: Vector3 = tri[i]
			min_x = minf(min_x, v.x)
			max_x = maxf(max_x, v.x)
			min_y = minf(min_y, v.y)
			max_y = maxf(max_y, v.y)
			min_z = minf(min_z, v.z)
			max_z = maxf(max_z, v.z)
			if v.y > CAVE_EPS and v.y < min_pos_y:
				min_pos_y = v.y
			var r := Vector2(v.x, v.z).length()
			tri_min_r = minf(tri_min_r, r)
			tri_max_y = maxf(tri_max_y, v.y)
			if cave_vert_on_floor(v):
				touches_floor = true
				if r < CAVE_INTERIOR_RADIUS:
					floor_corners += 1
		# Подъём от пола: касается y=0 и выше допустимого перепада.
		if touches_floor and tri_max_y > CAVE_STEP_MAX:
			risers += 1
			riser_min_r = minf(riser_min_r, tri_min_r)
	return {
		"min_y": min_y,
		"max_y": max_y,
		"dx": max_x - min_x,
		"dz": max_z - min_z,
		"min_pos_y": min_pos_y,
		"floor_corners": floor_corners,
		"risers": risers,
		"riser_min_r": riser_min_r,
	}


# Отрезок по Z, который треугольник занимает на высоте h (ось Y вверх, стена на +X).
# null — высота задета не была или треугольник не из стены прохода.
# Границы по X: проём начинается у стены зала (CAVE_OPEN_X) и кончается плоскостью
# стены двора (CAVE_OPEN_X_MAX). Всё, что дальше, — уже двор: его стены не имеют
# отношения к проёму и закрыли бы обзор (после появления двора в T2r-a3).
func cave_wall_span(tri: Array, h: float) -> Variant:
	for i in 3:
		var v: Vector3 = tri[i]
		if v.x < CAVE_OPEN_X or v.x > CAVE_OPEN_X_MAX:
			return null
	var zs: Array = []
	for i in 3:
		var a: Vector3 = tri[i]
		var b: Vector3 = tri[(i + 1) % 3]
		if absf(a.y - b.y) <= CAVE_EPS:
			continue
		var t := (h - a.y) / (b.y - a.y)
		if t < -CAVE_EPS or t > 1.0 + CAVE_EPS:
			continue
		var z := lerpf(a.z, b.z, t)
		if zs.is_empty() or absf(z - zs.back()) > CAVE_EPS:
			zs.append(z)
	if zs.size() < 2:
		return null
	zs.sort()
	return [zs.front(), zs.back()]


# Ширина непрерывного проёма вокруг z=0 на высоте h; 0 — центр закрыт.
func cave_open_width(tris: Array, h: float) -> float:
	var spans: Array = []
	for tri in tris:
		var span: Variant = cave_wall_span(tri, h)
		if span != null:
			spans.append(span)
	if spans.is_empty():
		return 0.0
	spans.sort_custom(func(a, b): return a[0] < b[0])
	var merged: Array = []
	for span in spans:
		if not merged.is_empty() and span[0] <= merged.back()[1] + CAVE_EPS:
			merged.back()[1] = maxf(merged.back()[1], span[1])
		else:
			merged.append([span[0], span[1]])
	var left := -CAVE_OPEN_SCAN_Z
	var right := CAVE_OPEN_SCAN_Z
	for span in merged:
		if span[0] <= 0.0 and span[1] >= 0.0:
			return 0.0
		if span[1] < 0.0:
			left = maxf(left, span[1])
		elif span[0] > 0.0:
			right = minf(right, span[0])
	return right - left


# Число треугольников потолка над точкой в плоскости XZ (пол исключён); 0 — колодец открыт.
func cave_ceiling_hits(tris: Array, x: float, z: float) -> int:
	var hits := 0
	for tri in tris:
		if cave_is_floor_tri(tri):
			continue
		if cave_contains_xz(tri, x, z):
			hits += 1
	return hits


# Высота поверхности над точкой (x, z): минимальная по граням (пол исключён),
# проекция которых накрывает точку. Высота берётся интерполяцией по треугольнику,
# а не минимумом вершин — иначе на наклонной грани ответ был бы занижен.
# INF — над точкой нет поверхности (например, прямо над отверстием шахты).
func cave_surface_y(tris: Array, x: float, z: float) -> float:
	var best := INF
	for tri in tris:
		if cave_is_floor_tri(tri):
			continue
		if not cave_contains_xz(tri, x, z):
			continue
		var a: Vector3 = tri[0]
		var b: Vector3 = tri[1]
		var c: Vector3 = tri[2]
		var den := (b.z - c.z) * (a.x - c.x) + (c.x - b.x) * (a.z - c.z)
		if absf(den) < CAVE_EPS:
			continue
		var wb := ((b.z - c.z) * (x - c.x) + (c.x - b.x) * (z - c.z)) / den
		var wc := ((c.z - a.z) * (x - c.x) + (a.x - c.x) * (z - c.z)) / den
		best = minf(best, a.y * (1.0 - wb - wc) + b.y * wb + c.y * wc)
	return best


# Первые `limit` попаданий луча (o, d) по мешу: расстояния t по возрастанию.
# Свой Мёллер–Трамбор: встроенного лучепинания у ArrayMesh нет, а проверки
# границы двора (стены по периметру, порода за дальней стеной) без лучей не
# выразить — проекция видна только сбоку.
func cave_rays(tris: Array, o: Vector3, d: Vector3, limit: int) -> Array:
	var hits: Array = []
	for tri in tris:
		var a: Vector3 = tri[0]
		var b: Vector3 = tri[1]
		var c: Vector3 = tri[2]
		var e1 := b - a
		var e2 := c - a
		var p := d.cross(e2)
		var det := e1.dot(p)
		if absf(det) < 1e-12:
			continue
		var inv := 1.0 / det
		var tv := o - a
		var u := tv.dot(p) * inv
		if u < -CAVE_EPS or u > 1.0 + CAVE_EPS:
			continue
		var q := tv.cross(e1)
		var v := d.dot(q) * inv
		if v < -CAVE_EPS or u + v > 1.0 + CAVE_EPS:
			continue
		var t := e2.dot(q) * inv
		if t <= 1e-4:
			continue
		hits.append(t)
	hits.sort()
	# Совпадающие t (грань из двух треугольников) схлопываем.
	var out: Array = []
	for t in hits:
		if out.is_empty() or t - out.back() > 0.01:
			out.append(t)
		if out.size() == limit:
			break
	return out


# Вершина лежит в плоскости пола y=0 (тот же порог, что и в проверках пола оболочки).
func cave_vert_on_floor(v: Vector3) -> bool:
	return absf(v.y) <= CAVE_EPS


# Пол — треугольник целиком на y=0.
func cave_is_floor_tri(tri: Array) -> bool:
	for i in 3:
		if not cave_vert_on_floor(tri[i]):
			return false
	return true


# Точка внутри треугольника при взгляде сверху (барицентрические координаты, плоскость XZ).
func cave_contains_xz(tri: Array, x: float, z: float) -> bool:
	var a: Vector3 = tri[0]
	var b: Vector3 = tri[1]
	var c: Vector3 = tri[2]
	var v0x := b.x - a.x
	var v0z := b.z - a.z
	var v1x := c.x - a.x
	var v1z := c.z - a.z
	var denom := v0x * v1z - v1x * v0z
	if absf(denom) < 0.000000001:
		return false
	var px := x - a.x
	var pz := z - a.z
	var u := (px * v1z - v1x * pz) / denom
	var v := (v0x * pz - px * v0z) / denom
	return u >= -CAVE_EPS and v >= -CAVE_EPS and u + v <= 1.0 + CAVE_EPS
