extends Node3D
# ВРЕМЕННЫЙ просмотрщик зоны ворот (осмотр ведущим). Удалить после приёмки.
# WASD — полёт, QE — вниз/вверх, мышь — осмотр (Esc отпускает курсор).

var _yaw := 0.0
var _pitch := 0.0
const SPEED := 6.0
const SENS := 0.003

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		_yaw -= event.relative.x * SENS
		_pitch = clamp(_pitch - event.relative.y * SENS, deg_to_rad(-85.0), deg_to_rad(85.0))
		rotation = Vector3(_pitch, _yaw, 0.0)
	elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseButton and event.pressed and Input.mouse_mode == Input.MOUSE_MODE_VISIBLE:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _process(delta: float) -> void:
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		return
	var dir := Vector3.ZERO
	if Input.is_physical_key_pressed(KEY_W): dir -= basis.z
	if Input.is_physical_key_pressed(KEY_S): dir += basis.z
	if Input.is_physical_key_pressed(KEY_A): dir -= basis.x
	if Input.is_physical_key_pressed(KEY_D): dir += basis.x
	if Input.is_physical_key_pressed(KEY_E): dir += Vector3.UP
	if Input.is_physical_key_pressed(KEY_Q): dir -= Vector3.UP
	if dir != Vector3.ZERO:
		position += dir.normalized() * SPEED * delta
