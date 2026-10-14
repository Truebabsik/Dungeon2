# Бриф: T21 — контроллер: движение, мышь, виды

Ты — исполнитель. Читай сначала `docs/agents/constraints.md`, затем `docs/agents/report-contract.md`.
Коммит не делать. Субагентов не вызывай. Дизайн: `docs/current/2026-10-11-fps-ranger/design.md` (пункты 3–7), план: `plan.md` (задача T21).
Предыдущие отчёты: `reports/T19-ranger-idle-report.md`, `reports/T19-ranger-idle-review.md`, `reports/T20-collision-report.md`, `reports/T20-collision-review-2.md`.

## Контекст

- `game/level/level.tscn`, узел `Character` сейчас `Node3D`. Внутри: `Rig_Medium_General` (меш скрыт, `AnimationPlayer` с `Idle_A`, `root_node` ведёт на `Ranger`), `Ranger` (`Ranger.glb`, меш и скелет). Ranger сдвинут относительно origin `Character` (T19, M1: тело в origin, манекен был на x = 1.55).
- `game/level/character_idle.gd` на `Character` делает `play("Idle_A")`, путь жёсткий (T19, M5).
- `game/level/grid_collision_builder.gd` + узел `GridCollision` строят коллизии стен, пола (один `StaticBody3D`, пол на y ≈ 1.0…2.29) и модулей (T20). Коллизии работают на отдельном дереве, их не трогать.
- Камера сверху: `Camera3D` (ортографическая, `current = true`), не менять параметры.
- Пользовательские узлы (`MeshInstance3D` и др.) и узлы уровня — не трогать.

## Что сделать

1. **`Character` → `CharacterBody3D`.** Узел `Character` заменяется на `CharacterBody3D` с именем `Character` (сохранить имя, на него ссылаются `character_idle.gd` и проверки). Сохранить его позицию из сцены (клетка (18, 18)). Внутри: `CollisionShape3D` с `CapsuleShape3D` (радиус 0.35, высота 1.8), `Rig_Medium_General` и `Ranger` перенести как есть; чтобы визуал не сдвинулся, компенсировать локальный сдвиг Ranger так, как он был (проверь по T19-отчёту).
2. **Стартовая точка.** Проверь, что старт `Character` не внутри коробки стены (по данным коллизий T20). Если внутри — перенести на ближайшую свободную клетку пола и записать в отчёт.
3. **Скрипт `game/level/character_controller.gd`** (новый, на `Character`, `extends CharacterBody3D`):
   - WASD в плоскости XZ относительно yaw тела (не камеры отдельно); скорость 3 м/с; `velocity.y = 0` (гравитации нет); `move_and_slide()`.
   - Мышь: `Input.MOUSE_MODE_CAPTURED` при старте; движение мыши поворачивает yaw тела и pitch камеры; pitch ограничен −80°…+80°; чувствительность — константа в скрипте.
   - `Esc` — `MOUSE_MODE_VISIBLE`; клик левой кнопкой по окну — снова `MOUSE_MODE_CAPTURED`.
   - Клавиша `V` переключает `current` между `Camera3D` (сверху) и `FPSCamera`. Старт — вид от первого лица.
4. **`FPSCamera`.** Новый `Camera3D` — дочерний узел `Character`, на высоте головы около 1.6 м (локально), `current = false` по умолчанию, `fov` по умолчанию. Тело видно (решение пользователя), поэтому камера чуть впереди головы, чтобы не упираться в меш: сместить вперёд на 0.1–0.2 м.
5. **Перенос логики `character_idle.gd`.** Жёсткий путь в `character_idle.gd` (M5): либо оставить скрипт, но сделать путь к `AnimationPlayer` устойчивым (поиск по имени узла в поддереве `Character`), либо перенести `play("Idle_A")` в `character_controller.gd`. Выбери вариант, который не дублирует логику, и запиши выбор в отчёт.
6. **Скрипт не должен мешать редактору.** В `_ready` проверять `Engine.is_editor_hint()`: в редакторе управление не включать.
7. **Проверка (headless).** Временный скрипт `E:\Temp\opencode\t21_check.gd`: загрузить `res://level/level.tscn`, добавить в дерево, 2 кадра; проверить: тип `Character` = `CharacterBody3D`; `FPSCamera` существует и дочерний `Character`; `V` (через вызов функции переключения) переключает `current`; вызов поворота мышью меняет yaw/pitch, pitch ограничен; `Esc` переводит `Input.mouse_mode` в `VISIBLE` (через вызов функции). Удалить после.
8. **Не трогать:** `level_check.gd` (правки в T22), коллизии (T20), `Camera3D` сверху, модули, `GridMap*`, пользовательские узлы, `.import`, `mesh_library.tres`, `project.godot`, `art/**`.
9. **Прогон:** `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`. Ожидаемо `failed: 0`, код 0. Если упало из-за типа `Character` — точное сообщение в отчёт, не подгонять (правка в T22).

## Отчёт

Файл: `docs/current/2026-10-11-fps-ranger/reports/T21-controller-report.md`. Содержание: что изменено в `Character`, стартовая точка, выбор по `character_idle.gd`, дословный вывод пробы и `level_check.gd`, решения вопреки брифу.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые и созданные файлы, одну строку: тип `Character`, `FPSCamera`, переключение `V`, `failed`, код проверки, открытые вопросы.
