# Бриф: T20 — коллизии из сетки и модулей

Ты — исполнитель. Читай сначала `docs/agents/constraints.md`, затем `docs/agents/report-contract.md`.
Коммит не делать. Субагентов не вызывай. Дизайн: `docs/current/2026-10-11-fps-ranger/design.md` (раздел «Решения», п. 2), план: `plan.md`, задача T20.

## Контекст

- Сетка: `GridMapWall`, `GridMapFloor`, `GridUpper` — узлы `GridMap` в `game/level/level.tscn`, `cell_size = (4, 4, 4)`, у `GridMapWall` 115 занятых ячеек, у `GridMapFloor` 276, у `GridUpper` 1 (проверь по сцене, не верь этим числам).
- Модули уровня — инстансы `.gltf` (26 штук по `level_check.gd`, `MODULES_EXPECTED`).
- Пользовательские узлы `MeshInstance3D` (ChainLink, Book1, Cage и др.) — не трогать и не коллизить.
- Персонаж `Character` пока `Node3D` (T21 сделает `CharacterBody3D`). Для T20 коллизии должны работать на отдельном `StaticBody3D`-дереве, которое не зависит от типа `Character`.

## Что сделать

1. **Скрипт `game/level/grid_collision_builder.gd`** (новый, `extends Node`, без `class_name` если в проекте так принято — сверься с существующими скриптами): при `_ready` (или явным методом `build()`) строит коллизии:
   - для каждой занятой ячейки `GridMapWall.get_used_cells()` — `StaticBody3D` с `CollisionShape3D` (`BoxShape3D`, размер `cell_size`), позиция = `map_to_local(cell)`;
   - пол: один `StaticBody3D` с плоским `BoxShape3D` (тонкий, `y = 0`) на весь охват `GridMapFloor` или по ячейкам — выбери вариант, который не даёт провалиться сквозь пол; записать выбор в отчёт;
   - модули: для каждого инстанса `.gltf` (узлы верхнего уровня с `scene_file_path` или `Node3D` с именем `*` из `level.tscn`, кроме `Character`, `GridMap*`, пользовательских `MeshInstance3D`) — `StaticBody3D` с `BoxShape3D` по AABB меша (объединённый AABB всех `MeshInstance3D` внутри инстанса в координатах родителя).
   Все коллизии — дочерние узлы одного контейнера `Collision` (создать в коде), не менять позиции модулей.
   Коллизии без `visible`-мешей: `StaticBody3D` без видимой геометрии.
2. **Подключение в сцену.** Добавить узел `GridCollision` (`Node`) с этим скриптом под корень `Level` в `level.tscn`. Ничего больше в сцене не менять.
3. **Проверка (headless).** Временный скрипт `E:\Temp\opencode\t20_check.gd`: загрузить `res://level/level.tscn`, добавить в дерево, подождать 2 кадра, вывести:
   - число `StaticBody3D` в `Collision` для стен = `GridMapWall.get_used_cells().size()`;
   - для пола — число и размеры коробок;
   - число коробок модулей = число модулей;
   - AABB каждой коробки модуля (для отчёта).
   Скрипт удалить после прогона.
4. **Не трогать:** `character_idle.gd`, `Character` (T21), `level_check.gd` (правки в T22), `.import`, `mesh_library.tres`, `project.godot`, `art/**`, пользовательские узлы и правки в `GridMap*`.
5. **Прогон:** `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd` — ожидаемо `failed: 0`, код 0. Если проверка упала из-за нового узла, записать точное сообщение в отчёт, не подгонять проверку.

## Отчёт

Файл: `docs/current/2026-10-11-fps-ranger/reports/T20-collision-report.md`. Содержание: выбор варианта пола и почему, число коробок по группам, AABB модулей (таблица), дословный вывод пробы и проверки.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые и созданные файлы, одну строку: число коробок стен, пола, модулей, `failed`, код проверки, открытые вопросы.
