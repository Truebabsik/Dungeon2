# Бриф: Задача 5 — визуальная сверка с референсом

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`. Этот файл — только специфика задачи.
Коммит не делать. Субагентов не вызывай.

## Где это в проекте

Задачи 1–4 сделаны и прошли ревью: сцена `game/level/level.tscn` собирает 312 модулей из `game/level/level_map.gd`
через `game/level/level_builder.gd`, headless-проверка `game/tests/level_check.gd` зелёная (`failed: 0`).
Цель этапа: сцена повторяет план `art/reference/reference.png` по раскладке комнат, коридоров, лестниц, дверей и реквизита.

**Этот бриф не правит уровень.** Задача — получить скриншот и описать расхождения с референсом. Решение о правках
принимает ведущий.

## Что сделать

1. Создать временный скрипт `E:\Temp\opencode\t5_capture.gd` (вне `game/`):
   ```
   extends SceneTree
   const LEVEL := preload("res://level/level.tscn")
   func _initialize() -> void:
       var lvl = LEVEL.instantiate()
       root.add_child(lvl)
       for i in 5:
           await process_frame
       var img := root.get_texture().get_image()
       img.save_png("F:/WORK/Dungeon2/docs/current/2026-10-09-level-demo/reports/T5-scene-screenshot.png")
       quit(0)
   ```
   Если `preload` даёт ошибку вне `game/` — использовать `load("res://level/level.tscn")`.
2. Запустить **с окном** (не `--headless`: headless не даёт рендера):
   `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --path F:\WORK\Dungeon2\game --resolution 1152x648 --script E:\Temp\opencode\t5_capture.gd`
   Зафиксировать код возврата. Если окно не открывается или процесс зависает — остановить и вернуть `BLOCKED` с причиной.
3. Проверить, что `T5-scene-screenshot.png` создан и не пустой (размер > 10 КБ).
4. Открыть скриншот и `art/reference/reference.png` через инструмент `read` и сравнить глазами.
5. Сделать список расхождений. Для каждого пункта: где на плане (примерно: верхний левый, центр, правый нижний и т.п.),
   что есть на референсе, что на скриншоте (стена/пол/лестница/колонна/дверь/реквизит/отсутствует/лишнее).
   Не более 15 пунктов, самые заметные сверху.
6. Удалить `E:\Temp\opencode\t5_capture.gd` после прогона.

## Область

**Можно править:** `docs/current/2026-10-09-level-demo/reports/T5-visual-check-report.md`,
`docs/current/2026-10-09-level-demo/reports/T5-scene-screenshot.png` (создать).
**Не трогать:** `game/**`, `art/**`, `docs/**` кроме отчёта и скриншота.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T5-visual-check-report.md`.
Содержание: параметры запуска и код возврата; путь к скриншоту; список расхождений по пункту 5; общая оценка
(совпадает в основном / частично / сильно расходится) с одним-двумя предложениями обоснования.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые файлы,
одну строку про прогон (код возврата, размер скриншота), общую оценку и число расхождений.
