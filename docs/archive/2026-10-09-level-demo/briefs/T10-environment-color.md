# Бриф: Задача 10 — окружение и цвет (фон, тёплый свет, тонмэппинг)

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`. Этот файл — только специфика задачи.
Коммит не делать. Субагентов не вызывай.

## Где это в проекте

Уровень собран (задачи 1–9). Сцена `game/level/level.tscn` содержит: корень `Level` (скрипт `level_builder.gd`),
`DirectionalLight3D` с `rotation_degrees = Vector3(-50, -30, 0)` и `Camera3D`. `WorldEnvironment` в сцене нет,
фон серый по умолчанию, свет холодный. Пользователь просит цвет как на `art/reference/reference.png`: тёмно-фиолетовый фон,
тёплый бежевый пол, тёплый свет, тёмные цветные тени.

## Что сделать

1. Добавить узел `WorldEnvironment` (дочерний узел корня сцены, рядом с `Camera3D`) с ресурсом `Environment`:
   - `background_mode = 1` (цвет), `background_color = Color(0.10, 0.06, 0.18, 1)` — тёмно-фиолетовый;
   - `ambient_light_source = 2` (цвет), `ambient_light_color = Color(0.42, 0.34, 0.50, 1)`, `ambient_light_energy = 0.8`;
   - `tonemap_mode = 3` (Filmic), `tonemap_exposure = 1.0`.
2. У существующего `DirectionalLight3D`:
   - `light_color = Color(1.0, 0.89, 0.72, 1)` — тёплый;
   - `light_energy = 1.2`;
   - `shadow_enabled = true`.
   Поворот (`rotation_degrees`) не менять.
3. Не менять: `Camera3D` (позиция, наклон, размер), узел `Level`, `level_map.gd`, `level_builder.gd`,
   `level_check.gd`, `project.godot`, ассеты, `art/**`.
4. Проверка: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`.
   Ожидаемо `failed: 0`, код `0`. Учесть: проверка 4 считает `Node3D`-потомков `Level`, `WorldEnvironment` — не `Node3D`,
   поэтому счёт не должен измениться; если изменился — это дефект, сообщить.
5. Скриншот: `E:\Temp\opencode\t10_capture.gd` (как в T9, с окном, `--resolution 1152x648`),
   файл `docs/current/2026-10-09-level-demo/reports/T10-scene-screenshot.png`. Скрипт удалить после прогона.
6. Посмотреть скриншот и `art/reference/reference.png` через `read`. Описать словами: фон, пол, тени, свет — что совпало и что нет.
   Не завышать оценку.

## Область

**Можно править:** `game/level/level.tscn` (добавить `WorldEnvironment` и `Environment`; у `DirectionalLight3D` только
`light_color`, `light_energy`, `shadow_enabled`),
`docs/current/2026-10-09-level-demo/reports/T10-environment-report.md`,
`docs/current/2026-10-09-level-demo/reports/T10-scene-screenshot.png`.
**Не трогать:** всё остальное.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T10-environment-report.md`.
Содержание: что добавлено в сцену (дословно значения), дословный вывод проверки, оценка скриншота по пунктам
(фон, пол, тени, свет), решения вопреки брифу.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые файлы,
одну строку про прогон (`failed`, код), открытые вопросы.
