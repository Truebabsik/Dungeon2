# Ревью: Задача 2 — данные карты и билдер

Ревьюер: субагент, по брифу `briefs/T2-map-builder.md`, отчёту `reports/T2-map-builder-report.md`, `design.md` (раздел 2), `docs/agents/constraints.md`, `docs/agents/review-checklist.md`. Правок не вносил.

## Гейт (headless-проба ревьюера)

Проба: `E:\Temp\opencode\t2_review_probe.gd` (extends SceneTree, `preload` обоих файлов, `build()`, `quit(0 if n == MODULES.size() else 1)`). Удалена после прогона, проверено: в `E:\Temp\opencode` файла нет.

Команда:
```
F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script E:\Temp\opencode\t2_review_probe.gd
```
(Путь из брифа `F:\WORK\Godot_v4.7.2-stable_win64_console.exe` не существует; рабочий путь — внутри каталога `F:\WORK\Godot_v4.7.2-stable_win64.exe\`, как в отчёте.)

Вывод (stdout):
```
MODULES.size() = 312
build() = 312
children = 312
```
Код возврата: `0`. Stderr содержит шум утечек RID/ObjectDB при выходе: проба не освобождала созданный `LevelBuilder`. Это не дефект билдера и на вердикт не влияет (по constraints §1.1 вердикт — код возврата).

## По пунктам брифа

1. `level_map.gd` — **ADDRESSED.** `CELL_SIZE := 4.0` (`level_map.gd:7`), `MODULES: Array` (`:9`), записи `{ "kind", "cell": Vector2i, "rot" }` (`:11` и далее, `:325` закрытие). `rot` ∈ {0, 90, 180}: 180 встречается один раз (`:319`, chair), 270 не используется. `kind` — 14 уникальных значений, все есть среди 16 файлов `game/assets/kaykit/` (проверено по листингу диска: `banner_patternA_red, barrel_large, bed_frame, chair, chest, coin_stack_small, floor_tile_large, pillar, shelves, stairs, table_medium, wall, wall_archedwindow_open, wall_doorway` — 14 из 16; `torch_mounted`, `wall_corner` не используются, причина в отчёте).
2. `level_builder.gd` — **ADDRESSED** с замечанием (Minor 1).
   - без `class_name`: ✔ (`level_builder.gd:1`, grep по `class_name` в `game/level/` — 0);
   - `func build() -> int`: ✔ (`:11`);
   - полы в центре клетки: ✔ (`:41-42`, `origin + HALF,HALF`);
   - стена `rot 0` → `(cell.x*4+2, 0, cell.y*4)`: ✔ (`:43-45`, `origin + (HALF,0,0)`);
   - стена `rot 90` → `(cell.x*4, 0, cell.y*4+2)`: ✔ (`:46`, `origin + (0,0,HALF)`);
   - прочее в центре клетки: ✔ (`:47`);
   - поворот `rot` по Y: ✔ (`:33`);
   - невалидный `rot` / неизвестный `kind`: `push_error` + `continue`, в счёт не входит: ✔ (`:17-19`, `:21-23`, `:25-27`, `:29-31`);
   - табы: ✔ (проверка по строкам с пробелом в начале — 0 в обоих файлах);
   - константы: `CELL`, `HALF`, `MODEL_PATH`, `VALID_ROTS` вынесены (`:5-8`), `4` и `2` в формулах не встречаются.
3. Лишние файлы — **ADDRESSED.** `game/`: `project.godot`, `.gitignore`, `assets/kaykit/`, `level/` (два `.gd`), плюс `.godot/` — кэш Godot, в `.gitignore` (`.godot/`, `game/.gitignore:1`). Временных проб в `game/` нет. В `E:\Temp\opencode\` проба задачи 2 (`t2_probe.gd`) и генератор `t2_gen.py` отсутствуют. Там остались `t1_err.txt`, `t1_import_rerun.txt`, `t1_out.txt` — артефакты задачи 1, вне области T2.
4. Headless-проба — **ADDRESSED.** Код 0, `MODULES.size() = 312`, `build() = 312`, `children = 312`. Совпадает с отчётом (312 / 312 / 312 / exit 0).
5. Выборочная проверка записей `MODULES` — **ADDRESSED:**
   - `:152` wall (0,0) rot 0 → `(2, 0, 0)`, северная грань ✔;
   - `:230` wall (0,0) rot 90 → `(0, 0, 2)`, западная грань ✔;
   - `:235` wall_doorway (5,1) rot 90 → `(20, 0, 6)`, западная грань клетки ✔;
   - `:288` chest (12,1) rot 90 → `(50, 0, 6)`, центр клетки, поворот 90 ✔;
   - `:324` stairs (-1,4) rot 90 → `(-4, 0, 18)`, центр клетки; `stairs` есть в `assets/kaykit/` ✔.
   Состав групп сверен с отчётом: floor 140 (`:11-150`), wall rot 0 — 69 + rot 90 — 38 = 107, doorway 14, arched 3, props 48 (`:277-324`). Итого 312 ✔.
6. DRY — **ADDRESSED.** Формула клетки `cell * CELL` написана один раз (`level_builder.gd:40`), полуклетка `HALF` один раз (`:6`). Ветки пола, стены и прочего различаются только смещением, формулы не дублируются. Замечание по `rot % 180` — Minor 1.

## Находки

- Critical 0
- Important 0
- Minor 3:
  1. `level_builder.gd:44` — ветка стены задана через `rot % 180 == 0`, а не по брифу (`rot == 0` / `rot == 90`). Для 180/270 бриф не определяет позицию стены; решение отмечено в отчёте (решение 3). В `MODULES` таких записей нет, дефекта сейчас нет. Желательно вписать правило в `design.md` или `constraints.md`, когда понадобится.
  2. `level_map.gd:1-3` — заголовок-комментарий описывает правила осей и поворотов; совпадает с кодом, дублировать не нужно. Замечания по сути нет, отмечено для полноты: если правило поворота стены появится в `design.md`, комментарий тоже надо обновить.
  3. `E:\Temp\opencode\t1_*.txt` — артефакты задачи 1 остались. Вне области задачи 2, решение ведущего: удалить или оставить.

## Assessment

**Да.** Бриф выполнен по всем пунктам; проба проходит с кодом 0 и числами 312/312/312. Найденных Critical и Important нет; три Minor записаны выше, решение по ним за ведущим.

отчёт: F:\WORK\Dungeon2\docs\current\2026-10-09-level-demo\reports\T2-map-builder-review.md
