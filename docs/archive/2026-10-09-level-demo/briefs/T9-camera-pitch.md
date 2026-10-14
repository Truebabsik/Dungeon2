# Бриф: Задача 9 — угол камеры (наклон 45°)

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`. Этот файл — только специфика задачи.
Коммит не делать. Субагентов не вызывай.

## Где это в проекте

Пользователь запросил более крутой ракурс камеры: наклон **45°** вместо 35°. Поворот по Y остаётся **45°**.
Текущее состояние `game/level/level.tscn`: `Camera3D` с `rotation_degrees = Vector3(-35, 45, 0)`, `projection = 1`,
`size = 41.0`, `position = Vector3(70.38, 40, 58.38)`. Расчёт кадрирования для 35° описан в
`docs/current/2026-10-09-level-demo/reports/T6-layout-correction-report.md`, раздел 3 — использовать ту же методику.

## Что сделать

1. Установить `rotation_degrees = Vector3(-45, 45, 0)` у `Camera3D` в `game/level/level.tscn`.
2. Пересчитать кадрирование по методике T6, раздел 3, с новым наклоном. Базис камеры при наклоне 45°:
   right = (0.7071, 0, −0.7071); up = (−0.5, 0.7071, −0.5). Координаты: `R = 0.7071·(x − z)`, `U = −0.5·(x + z) + 0.7071·y`.
   Найти крайние точки плана по `MODULES` (учесть толщину стены 0.5 м и высоту стены 4 м), размах по R и U.
   Подобрать `size` так, чтобы план занимал не менее 85 % ширины кадра (1152×648) и помещался по высоте с запасом
   не меньше 0.5 единицы сверху и снизу. Позицию камеры вычислить так, чтобы центр плана попал в центр кадра:
   `position = центр плана в мировых координатах + направление камеры назад`. Значения записать в отчёт с расчётом.
3. Не менять `level_map.gd`, `level_builder.gd`, `level_check.gd`, `project.godot`, ассеты, другие узлы сцены.
4. Проверка: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`.
   Ожидаемо `failed: 0`, код `0`.
5. Скриншот: `E:\Temp\opencode\t9_capture.gd` (как в T8, с окном, `--resolution 1152x648`), файл
   `docs/current/2026-10-09-level-demo/reports/T9-scene-screenshot.png`. Скрипт удалить после прогона.
6. Посмотреть скриншот через `read`: весь план в кадре, нет обрезки по краям, центр плана в центре кадра.
   Описать словами, что видно, и не завышать оценку.

## Область

**Можно править:** `game/level/level.tscn` (только `Camera3D`: `rotation_degrees`, `position`, `size`),
`docs/current/2026-10-09-level-demo/reports/T9-camera-pitch-report.md`,
`docs/current/2026-10-09-level-demo/reports/T9-scene-screenshot.png`.
**Не трогать:** всё остальное.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T9-camera-pitch-report.md`.
Содержание: расчёт базиса, размаха по R и U, выбранные `size` и `position` с обоснованием, дословный вывод проверки,
оценка скриншота.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые файлы,
одну строку про прогон (`failed`, код, `size`, `position`), открытые вопросы.
