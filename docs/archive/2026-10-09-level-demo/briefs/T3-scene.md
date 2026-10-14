# Бриф: Задача 3 — сцена и камера

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`. Этот файл — только специфика задачи.
Коммит не делать. Субагентов не вызывай.

## Где это в проекте

Задачи 1 и 2 сделаны: `game/project.godot` (главная сцена `res://level/level.tscn` — ещё не существует),
`game/assets/kaykit/` и `game/level/level_builder.gd` с методом `build() -> int` (узел `Node3D`, создаёт модули по `MODULES`).
Спецификация: `docs/current/2026-10-09-level-demo/design.md`, раздел 2. План: `plan.md`, «Задача 3».

## Что сделать

Создать `game/level/level.tscn` — текстовую сцену Godot 4.7 (`[gd_scene format=3]`) с узлами:

1. Корень `Node3D` с именем `Level`, скрипт `res://level/level_builder.gd`.
2. `DirectionalLight3D` — направленный свет, поворот `Vector3(-50, -30, 0)` в градусах, энергия по умолчанию.
3. `Camera3D` — дочерний узел корня сцены, **не** `Level`.
   - `projection = 1` (ортографическая, `PROJECTION_ORTHOGONAL`);
   - `size` — подобрать так, чтобы весь план вмещался в кадр. План из `MODULES` имеет размер в клетках; определить
     размер по `MODULES` (минимальный и максимальный `cell`), диапазон в метрах — `(max - min + 1) * 4`. Значение
     записать в сцену числом, посчитанным из `MODULES`, а не на глаз, и указать расчёт в отчёте;
   - `rotation_degrees = Vector3(-35, 45, 0)` — поворот 45° по Y и 35° вниз к горизонту;
   - `current = true`.
   - Позиция камеры: `Vector3(0, 40, 0)` — выше плана, направление задаётся поворотом. Значение 40 записать как
     проверенное, а не угаданное: убедиться, что план попадает в кадр (см. доказательство).
4. Главная сцена проекта указана в `project.godot` как `res://level/level.tscn` — не менять.

**Единственная правка `level_builder.gd`:** добавить метод `func _ready() -> void:` с вызовом `build()` — без него
уровень пустой. Больше в этом файле ничего не менять. Это решение ведущего, зафиксировано в `ledger.md`.

## Область

**Можно править:** `game/level/level.tscn` (создать), `game/level/level_builder.gd` (только добавить `_ready()`, см. выше),
`docs/current/2026-10-09-level-demo/reports/T3-scene-report.md`.
**Не трогать:** `game/project.godot`, `game/level/level_map.gd`, `game/assets/**`, `art/**`, `docs/**` кроме отчёта.

## Доказательство

1. Проба загрузки: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --import`
   — код возврата `0`, ошибки `Cannot open file 'res://level/level.tscn'` в stderr больше быть не должно.
2. Проба сцены: временный headless-скрипт `extends SceneTree` в `E:\Temp\opencode\t3_probe.gd`, который:
   - загружает `res://level/level.tscn` через `load`, создаёт экземпляр, добавляет в дерево;
   - выводит число детей корня `Level` после `_ready` (должно быть `MODULES.size()`, если `build()` вызывается из
     `_ready` — если `build()` не вызывается автоматически, отметить это и не менять билдер);
   - выводит `Camera3D.size` и `rotation_degrees`.
   Запуск: `...console.exe --headless --path F:\WORK\Dungeon2\game --script E:\Temp\opencode\t3_probe.gd`. Проба удаляется после.
3. Дословные выводы обоих прогонов и код возврата — в отчёт.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T3-scene-report.md`.
Содержание: что создано, расчёт `size` камеры из `MODULES`, как вызывается `build()` (из `_ready` или нет),
дословные выводы проб, решения вопреки брифу.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`),
изменённые файлы, одну строку про прогон (код `--import`, число детей, `size`), открытые вопросы.
