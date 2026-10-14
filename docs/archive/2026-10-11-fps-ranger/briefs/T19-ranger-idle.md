# Бриф: T19 — Рейнджер на сцене, idle на его скелете (спайк)

Ты — исполнитель. Читай сначала `docs/agents/constraints.md`, затем `docs/agents/report-contract.md`.
Коммит не делать. Субагентов не вызывай. Полный дизайн: `docs/current/2026-10-11-fps-ranger/design.md`, план: `plan.md`, задача T19.

## Контекст

- `game/assets/kaykit_adventurers/characters/Ranger.glb` — меш с `skin`, скелет `Rig_Medium` (те же кости, что у `Rig_Medium_General`), анимаций в файле нет.
- `game/assets/kaykit_animations/animations/Rig_Medium/Rig_Medium_General.glb` — `AnimationPlayer` с `Idle_A`, зацикленной через `.import` (`loop_mode = 1`). Не трогать `.import`.
- В `game/level/level.tscn` узел `Character` (`Node3D`) содержит инстанс `Rig_Medium_General` с `AnimationPlayer`; скрипт `game/level/character_idle.gd` на `Character` вызывает `play("Idle_A")`.
- Узлы уровня (модули, `GridMapWall`, `GridMapFloor`, `GridUpper`, камера, свет, среда) и пользовательские `MeshInstance3D` (ChainLink, Book1, Cage и др.) — не трогать.

## Что сделать

1. **Проба (временная).** `E:\Temp\opencode\t19_probe.gd` (`extends SceneTree`): загрузить `Ranger.glb` и `Rig_Medium_General.glb`, найти `Skeleton3D` в обоих, сравнить списки имён костей, найти в `Rig_Medium_General` трек `Idle_A` и вывести его пути (`NodePath`) к костям. Вывести: совпадают ли имена костей, какие пути треков, есть ли пути, которых нет в скелете Рейнджера. Скрипт удалить после прогона.
2. **Если все пути совпадают.** В `game/level/level.tscn`:
   - внутри `Character` оставить инстанс `Ranger.glb` (меш и скелет) как видимого персонажа;
   - `Rig_Medium_General` с его мешем скрыть (`visible = false` на узле меша) или убрать меш, но сохранить `AnimationPlayer` с `Idle_A`, перевесив его на скелет Рейнджера (`root_node` или пути треков — выбери минимальный способ, который не ломает `Idle_A`);
   - `character_idle.gd` не менять, пока не доказано, что он нужен.
   Если пути не совпадают — **не менять сцену**, описать в отчёте варианты и остановиться.
3. **Проверка (headless).** Временный скрипт `E:\Temp\opencode\t19_anim.gd`: загрузить `res://level/level.tscn`, добавить в дерево, подождать 2 кадра, найти `AnimationPlayer` в `Character`, вывести `current_animation` и `is_playing()`. Удалить после.
4. **Не трогать:** `level_check.gd` (правки проверок — в T22), `.import` файлов, `mesh_library.tres`, `project.godot`, `art/**`.
5. **Прогон:** `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd` — ожидаемо `failed: 0`, код 0. Если проверка модулей упала из-за смены `Character` — записать в отчёт точное сообщение и не подгонять проверку (это правится в T22).

## Отчёт

Файл: `docs/current/2026-10-11-fps-ranger/reports/T19-ranger-idle-report.md`. Содержание: вывод пробы (имена костей, пути треков, совпадение), что сделано в сцене или почему не сделано, дословный вывод проверки анимации и `level_check.gd`.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые файлы, одну строку: совпали ли пути костей, `current_animation`, `is_playing`, `failed`, код проверки.
