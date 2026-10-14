# Бриф: Задача 16 — MeshLibrary из всех статичных моделей и GridMap в сцене

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`. Этот файл — только специфика задачи.
Коммит не делать. Субагентов не вызывай.

## Где это в проекте

Пользователь хочет перетаскивать объекты в редакторе через палитру GridMap. Исходники:
- `game/assets/kaykit/*.gltf` — 211 статичных моделей KayKit (с `.bin` и `dungeon_texture.png`);
- `game/assets/dungeon_pack/obj/*.obj` — 90 моделей с `.mtl` (цвета заданы в материалах, внешних текстур нет).
Анимированные риги и манекены (`game/assets/kaykit_animations/`) в библиотеку **не** входят.
Уровень `game/level/level.tscn` — редактируемая сцена (модули — инстансы, `Character`, `Prototypes`, свет, камера, среда).
Клетка уровня — 4 м, поэтому `GridMap.cell_size = Vector3(4, 4, 4)`.

## Что сделать

1. **Библиотека.** Временный headless-скрипт `E:\Temp\opencode\t16_build_lib.gd` (`extends SceneTree`, вне `game/`) создаёт
   `res://assets/mesh_library.tres` (`MeshLibrary`). Для каждого файла:
   - `.gltf` — имя элемента = имя файла без расширения (например `wall`), для `.obj` — `obj_<имя файла>`;
   - загрузить `PackedScene`, инстанцировать, собрать все `MeshInstance3D` (рекурсивно) с их трансформами относительно корня,
     получить один `Mesh` для элемента (если мешей несколько — объединить поверхности с учётом трансформов; если один — взять его);
   - `set_item_name`, `set_item_mesh`; `set_item_preview` не обязателен.
   Ошибку на одном файле не глушить: записать в отчёт и продолжить. Ожидаемо: 301 элемент (211 + 90), если нет сбоев.
   Сохранить через `ResourceSaver.save`. Скрипт удалить после прогона.
2. **GridMap в сцене.** В `game/level/level.tscn` добавить узел `GridMap` (тип `GridMap`), дочерний **корня сцены** `Level`
   (рядом с `Prototypes`, `Character`). Свойства: `mesh_library` = `res://assets/mesh_library.tres`,
   `cell_size = Vector3(4, 4, 4)`. Ячейки пустые: в сцене ничего не расставлять.
3. **Проверка `level_check.gd`.** `GridMap` — наследник `Node3D`, поэтому его надо исключить из подсчёта модулей так же, как
   `Character` (по имени `GridMap` и условию: тип `GridMap`). Не ослаблять проверку модулей. Добавить проверку: узел `GridMap`
   существует, у него `mesh_library` загружена и содержит 301 элемент (или сколько получилось, если были сбои — тогда провал).
   Прогон: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`
   — ожидаемо `failed: 0`, код `0`.
4. **Импорт.** `--import` той же версией Godot — код `0`.
5. **Не трогать:** модули уровня, `Character`, `Prototypes`, свет, камеру, среду, `project.godot`, `art/**`.

## Область

**Можно править:** `game/level/level.tscn` (только добавить `GridMap`), `game/tests/level_check.gd`,
создать `game/assets/mesh_library.tres`,
`docs/current/2026-10-09-level-demo/reports/T16-mesh-library-report.md`.
**Не трогать:** всё остальное.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T16-mesh-library-report.md`.
Содержание: способ объединения мешей, число элементов (ожидаемо 301), список файлов с ошибками (если есть),
размер `mesh_library.tres`, дословные выводы `--import` и проверки, решения вопреки брифу.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые и созданные файлы,
одну строку: число элементов библиотеки, `failed`, код `--import`, код проверки, открытые вопросы.
