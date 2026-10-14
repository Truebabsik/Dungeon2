extends CharacterBody3D

const SPEED := 3.0
const MOUSE_SENSITIVITY := 0.003
const PITCH_LIMIT := deg_to_rad(80.0)
const IDLE_ANIMATION := "Idle_A"
# Глаза на 2.15 м (середина 2.1–2.2 по решению пользователя): доля высоты меша Ranger_Head от низа,
# (2.15 − 1.1928) / 1.0801 ≈ 0.886. Высота меша головы берётся из модели (bind-поза).
const EYE_LEVEL := 0.886
const FACE_OFFSET := 0.15

var top_camera: Camera3D
var fps_camera: Camera3D


func _ready() -> void:
	if Engine.is_editor_hint():
		set_physics_process(false)
		set_process_unhandled_input(false)
		return
	top_camera = get_parent().get_node("Camera3D") as Camera3D
	fps_camera = get_node("FPSCamera") as Camera3D
	var head := head_box()
	fps_camera.position = Vector3(head.get_center().x, head.position.y + head.size.y * EYE_LEVEL, head.position.z - FACE_OFFSET)
	var player := find_child("AnimationPlayer", true, false) as AnimationPlayer
	if player == null:
		push_error("у Character нет AnimationPlayer")
	else:
		player.play(IDLE_ANIMATION)
	capture_mouse()
	set_fps_view(true)


func _physics_process(_delta: float) -> void:
	var move_axis := Vector3.ZERO
	if Input.is_physical_key_pressed(KEY_W):
		move_axis.z -= 1.0
	if Input.is_physical_key_pressed(KEY_S):
		move_axis.z += 1.0
	if Input.is_physical_key_pressed(KEY_A):
		move_axis.x -= 1.0
	if Input.is_physical_key_pressed(KEY_D):
		move_axis.x += 1.0
	var direction := move_axis.normalized().rotated(Vector3.UP, rotation.y)
	velocity = Vector3(direction.x * SPEED, 0.0, direction.z * SPEED)
	move_and_slide()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var motion := event as InputEventMouseMotion
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			apply_mouse_motion(motion.relative)
	elif event is InputEventMouseButton:
		var button := event as InputEventMouseButton
		if button.pressed and button.button_index == MOUSE_BUTTON_LEFT:
			capture_mouse()
	elif event is InputEventKey:
		var key := event as InputEventKey
		if key.pressed and not key.echo:
			if key.physical_keycode == KEY_ESCAPE:
				release_mouse()
			elif key.physical_keycode == KEY_V:
				toggle_view()


func head_box() -> AABB:
	var head := get_node("Ranger").find_child("Ranger_Head", true, false) as MeshInstance3D
	return ((global_transform.affine_inverse() * head.global_transform) * head.get_aabb())


func apply_mouse_motion(relative: Vector2) -> void:
	rotation.y -= relative.x * MOUSE_SENSITIVITY
	fps_camera.rotation.x = clampf(fps_camera.rotation.x - relative.y * MOUSE_SENSITIVITY, -PITCH_LIMIT, PITCH_LIMIT)


func capture_mouse() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func release_mouse() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func toggle_view() -> void:
	set_fps_view(not fps_camera.current)


func set_fps_view(on: bool) -> void:
	fps_camera.current = on
	top_camera.current = not on
