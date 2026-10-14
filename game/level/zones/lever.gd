extends Node3D

# Рычаг ворот (T4). Единственное, что рычаг умеет, — поднять решётку: он зовёт
# Portcullis.open() по ссылке portcullis_path. Обратного действия нет, рычаг односторонний
# (design.md:6 «решётка поднимается и остаётся открытой»).
#
# Почему скрипт на самом узле Lever, а не на Area3D: узел рычага — это и декорация,
# и точка входа, а зона действия — его ребёнок UseZone. Если скрипт переедет на зону,
# ссылка portcullis_path станет путьём от Area3D и «../Portcullis» перестанет работать.

## Путь к решётке (задаётся в сцене). Отсчитывается от узла рычага.
@export var portcullis_path: NodePath
## Узел зоны действия: капсула персонажа внутри него поднимает рычаг.
@export var use_zone_path: NodePath = ^"UseZone"

## Рычаг сработал. Ставится только после успешного вызова Portcullis.open(), поэтому
## сломанная ссылка не сжигает рычаг: починил ссылку — рычаг снова работает.
var used := false

var _player_in_zone := false
var _key_was_down := false


func _ready() -> void:
	if get_node_or_null(use_zone_path) == null:
		push_error("рычаг: нет зоны действия %s" % use_zone_path)
		return
	var zone := get_node(use_zone_path) as Area3D
	zone.body_entered.connect(_refresh_player_in_zone)
	zone.body_exited.connect(_refresh_player_in_zone)


## Физический кадр. Ввод читается только здесь и только как ФИЗИЧЕСКАЯ клавиша
## (AGENTS.md: клавиши физические, чтобы раскладка не ломала управление).
func _physics_process(_delta: float) -> void:
	poll_interaction(Input.is_physical_key_pressed(KEY_E))


## Опрос клавиши взаимодействия за один физический кадр; возвращает true, если рычаг
## сработал именно в этом кадре.
##
## Клавиша передаётся аргументом, а не читается внутри, — по двум причинам:
##  - защита от удержания обязана быть проверяемой: в headless-прогоне состояние клавиши
##    не подделывается (Input.parse_input_event не меняет Input.is_physical_key_pressed),
##    и только через аргумент гейт вообще может её прогнать;
##  - ввод читается ровно в одном месте (_physics_process), а логика решения — в другом.
##
## ЗАЩИТА ОТ ПОВТОРА НА УДЕРЖАНИЕ: срабатывает ФРОНТ нажатия (`key_down and not
## _key_was_down`), а не уровень «клавиша зажата». Пока игрок держит E, каждый физический
## кадр приходит key_down == true, но фронт возникает ровно один раз — на первом кадре
## после нажатия. Второй слой — флаг used: рычаг односторонний, и даже новое нажатие
## (после отпускания) его уже не сработает.
##
## Что это даёт сверх одной проверки used: игрок, держащий E ещё ДО входа в зону, не
## «дозаряжает» рычаг входом в зону — фронт нажатия был до того, как персонаж оказался
## в зоне, и ждать следующего отпускания-нажатия придётся осознанно. Без фронта такое
## поведение зависело бы от единственного флага и ломалось бы при любом сбросе.
func poll_interaction(key_down: bool) -> bool:
	var fired := false
	if key_down and not _key_was_down:
		fired = try_use(_player_in_zone)
	_key_was_down = key_down
	return fired


## Опустить рычаг. player_in_zone — персонаж внутри зоны действия. Возвращает true,
## только если в этом вызове действительно пошла команда на подъём решётки.
func try_use(player_in_zone: bool) -> bool:
	if used or not player_in_zone:
		return false
	var portcullis := get_node_or_null(portcullis_path)
	if portcullis == null or not portcullis.has_method("open"):
		push_error("рычаг: %s — не Portcullis" % portcullis_path)
		return false
	used = true
	portcullis.open()
	return true


## Тело персонажа вошло в зону или вышло из неё. Флаг берётся из самого Area3D, а не
## ставится по сигналу вслепую: зону могут пересекать несколько тел сразу, и одиночный
## флаг «вошёл — true, вышел — false» сбивался бы на втором теле (например, на стене
## караулки, если её коробка заденет край зоны). Учитываются только CharacterBody3D:
## стены, реквизит и порода — не персонаж, рычаг от них срабатывать не должен.
func _refresh_player_in_zone(_body: Node3D) -> void:
	_player_in_zone = false
	var zone := get_node_or_null(use_zone_path) as Area3D
	if zone == null:
		return
	for body in zone.get_overlapping_bodies():
		if body is CharacterBody3D:
			_player_in_zone = true
			return
