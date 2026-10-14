# Ревью T22: проверки уровня, движение у стены

Ревьюер: отдельный субагент. Код не правился. Субагенты не вызывались.
Вход: `docs/agents/review-checklist.md`, `T22-checks-report.md`, `T21-controller-report.md` (раздел 11), `design.md` (пп. 3–7, «Решения» п. 4), `plan.md` (T21, T22), `game/tests/level_check.gd`, `game/level/character_controller.gd`, `game/level/level.tscn`.

## 4. Гейт (проверено самостоятельно)

Команда: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`
(путь из задания; в отчётах T19–T21 тот же бинарник лежит в `F:\WORK\` без папки-обёртки, запуск через него тоже работает).

- Код возврата: **0** (`Start-Process ... -PassThru`, `ExitCode = 0`).
- `ok`: **27**, `failed: 0`. Число `ok` совпадает с отчётом T22 §3, построчно.
- Stderr / `SCRIPT ERROR` / `WARNING`: не выводятся.

## Пункты задания

1. Контроллер (`character_controller.gd`)
   - ADDRESSED: WASD через `Input.is_physical_key_pressed`, строки 36–43.
   - ADDRESSED: V и Esc через `physical_keycode`, строки 61–63.
   - ADDRESSED: `EYE_LEVEL` с комментарием-источником, строки 7–8. `FACE_OFFSET` без комментария, строка 10 (см. Minor 1).
   - ADDRESSED: editor-guard, строки 17–20 (отключены `_physics_process` и `_unhandled_input`).
   - ADDRESSED: переключение V через `toggle_view` / `set_fps_view`, строки 85–91.
   - ADDRESSED: захват мыши при старте (строка 30) и кликом (строки 56–57), Esc отпускает (строка 62).
   - ADDRESSED: лишнего кода не найдено; `capture_mouse` / `set_fps_view` переиспользованы, `top_camera` и `IDLE_ANIMATION` используются.
2. Сцена (`level.tscn`)
   - ADDRESSED: `Ranger` повёрнут на 180° по Y, `Transform3D(-1,0,0, 0,1,0, 0,0,-1, 0,0,0)`, строка 95. Матрица корректна, без сдвига по origin.
   - ADDRESSED: визуал не сдвинут. Центр AABB тела по Z смещён на 0.004 м (отчёт T21 §11), по X и Y нет. Смещение за счёт асимметрии, не за счёт трансформа.
   - ADDRESSED: `FPSCamera` в сцене `Transform3D(…, 0, 2.1498, -0.685)`, строка 102. Совпадает с `_ready` (controller 24): `1.1928 + 1.0801·0.886 = 2.1498`, `z = -0.535 − 0.15 = -0.685`. Гейт подтверждает 2.1498.
   - ADDRESSED: `CapsuleShape3D_character` radius 0.35, height 1.8, строки 41–43; `CollisionShape3D` y=0.9, строки 97–99. Капсула от 0 до 1.8, нижняя точка = origin.
3. `level_check.gd`
   - ADDRESSED: существующие проверки не ослаблены. Числа 26 / 408 / 115 / 276 / 1 и условия `check_modules`, `check_grid_maps`, `check_camera_and_environment` те же. `check_character` (153–163) проверяет `Node3D`, это ослабления не даёт, `CharacterBody3D` — потомок. Git-репозитория нет, построчный diff не сделан; сверка по числам и по гейтам T20/T21.
   - ADDRESSED: новые проверки могут провалиться. Условия читаются: диапазон высоты камеры 185–189; `meshes > 0 and skeletons > 0` 198; `rig_meshes > 0 and visible == 0` 211; `walls == used and == 115` 256; `shapes == used and == 276` 272; `travelled ≥ 0.5` 393; `gap ≥ r − 0.05` 398; `gap ≤ r + 0.05` 403; `|yaw_delta + 100·S| < eps` 324; pitch-лимит 339, 346.
   - ADDRESSED: движение через вызовы, не ввод. Строки 376–386: `velocity = forward·SPEED`, `move_and_slide()` в цикле. `_physics_process` на время прогона отключён.
   - ADDRESSED: отключение `_physics_process` восстанавливается. `set_physics_process(false)` строка 379, `set_physics_process(true)` строка 386; между ними нет `return`, восстановление безусловное. Значение `true` зашито, не сохранено (Minor 2).
4. Гейт: ADDRESSED (см. раздел 4 выше).
5. Временные скрипты: ADDRESSED. `glob E:\Temp\opencode\t2*` — файлов нет.
6. Esc и курсор: ADDRESSED как ограничение. Не проверяется headless, отмечено в T21 §6.3 и T22 §5, передано в T23.

## Находки

- Critical 0
- Important 0
- Minor 1: `FACE_OFFSET` (`character_controller.gd:10`) без комментария-источника, при том что `EYE_LEVEL` его имеет. Значение 0.15 м — решение дизайна, стоит указать «design.md п. 4».
- Minor 2: `check_movement` восстанавливает `set_physics_process(true)` безусловно (`level_check.gd:386`). Надёжнее сохранить `is_physics_processing()` до отключения и вернуть его.
- Minor 3: дублирование в проверках вида и мыши. `var controller: Variant = character` и поиск `fps` повторены в `check_view_toggle` (281–282, 288) и `check_mouse` (310–311, 316). Можно вынести хелпер.
- Minor 4: `level_check.gd:173` — `get_class() == CHARACTER_TYPE` избыточно, тип уже проверен кастом в `character_of` (411–412).
- Minor 5: переключение V в гейте вызывает `toggle_view()` напрямую. Связка `physical_keycode == KEY_V` не покрыта гейтом; проверялась только пробой T21b, которая удалена. Оставить для T23 или вернуть пробу в гейт.
- Minor 6: `design.md`, строка 24: фраза «Поворот по yaw меняет тело, по pitch — камеру, pitch ограничен −80°…+80°.» повторена дважды. Удалить дубликат.

## Итог

**Принято.** Гейт зелёный (код 0, 27 ok, failed 0). Critical и Important нет. Minor 1–6 записаны, решение по каждому — на ведущем: правка сейчас или отдельным списком в T23. Esc, курсор и физическая раскладка V — только в редакторе (T23).

отчёт: F:\WORK\Dungeon2\docs\current\2026-10-11-fps-ranger\reports\T22-review.md
