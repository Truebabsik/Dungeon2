# Отчёт T11: редактируемая сцена уровня и прототипы

Статус: DONE_WITH_CONCERNS. Два решения требуют решения ведущего (см. «Решения вопреки брифу» и «Открытые вопросы»).

## Что изменено

- `game/level/level.tscn` — переписан конвертацией (временный скрипт `E:\Temp\opencode\t11_convert.gd`, удалён).
  - Корень `Level` (`Node3D`): скрипт снят (`set_script(null)`), `ext_resource` на `level_builder.gd` в файле нет.
  - 285 детей-модулей `<kind>_<NNN>` (NNN с 001 по порядку `MODULES`), каждый — `instance=ExtResource(...)` на `res://assets/kaykit/<kind>.gltf`. Позиция и поворот совпадают с тем, что давал билдер (проверено: `floor_tile_large_001` с клеткой (4,0) даёт `Transform3D(..., 18, 0, 2)`).
  - Узел `Prototypes` (`Node3D`, дочерний `Level`), `position = (-20, 0, 0)`, 14 инстансов (см. ниже).
  - `DirectionalLight3D`, `Camera3D`, `WorldEnvironment` и `Environment_level` сохранены конвертацией; значения совпадают с прежним файлом (порядок свойств и `unique_id` переписаны Godot).
  - Всего узлов в сцене: 304 = 285 модулей + 14 прототипов + 5 служебных (`Level`, `Prototypes`, свет, камера, окружение). Инстансов: 299 = 285 + 14.
- `game/tests/level_check.gd` — переписан под сцену. Без `MODULES`, без `preload` удалённых файлов, без `class_name`, без жёстких чисел. Проверки: корень `Level`; модули и `.gltf`; `Prototypes` с одним инстансом на каждый kind (сравнение множеств); `Prototypes` вне плана (`x < -10`) и модули не его потомки; `Camera3D` и `WorldEnvironment` в корне.
- Удалены: `game/level/level_builder.gd`, `game/level/level_builder.gd.uid`, `game/level/level_map.gd`, `game/level/level_map.gd.uid`. Ссылок на них в `game/` (кроме `.godot/`) не осталось: проверено рекурсивным поиском до удаления и после.

Копии удалённых файлов и исходного `level.tscn` лежали во временном каталоге `E:\Temp\opencode\t11_backup_*` и удалены вместе с остальными временными файлами.

## Как конвертировано

Конвертация шла, пока `level_map.gd` и `level_builder.gd` существовали. Скрипт:
1. `load("res://level/level.tscn")`, `instantiate()`, `root.add_child(level)`. `_ready()` билдера создал модули.
2. `level.build()` вернул число созданных узлов; список берётся из `level.get("_spawned")` в порядке `MODULES`.
3. Каждому инстансу: `name = "<kind>_<NNN>"`, `owner = level`.
4. Прототипы: `Node3D` `Prototypes`, `owner = level`, `position = (-20, 0, 0)`. Для каждого kind из `MODULES` (порядок первого появления) инстанс `<kind>` с `owner = level`, `position = (0, 0, i*6)`, поворот 0.
5. `level.set_script(null)`, `PackedScene.pack(level)`, `ResourceSaver.save(..., "res://level/level.tscn")`. Pack не развернул инстансы в узлы: `instance=ExtResource` сохранился, `NEEDS_CONTEXT` не понадобился.

Вывод конвертации (дословно):
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

конвертация: build() создал 285, узлов-модулей 285
прототипы: 14
сохранено: res://level/level.tscn
convert exit: 0
```

## Список прототипов (14 видов, порядок первого появления в MODULES)

| i | kind | position |
|---|---|---|
| 0 | floor_tile_large | (0, 0, 0) |
| 1 | wall | (0, 0, 6) |
| 2 | wall_archedwindow_open | (0, 0, 12) |
| 3 | wall_doorway | (0, 0, 18) |
| 4 | barrel_large | (0, 0, 24) |
| 5 | pillar | (0, 0, 30) |
| 6 | shelves | (0, 0, 36) |
| 7 | chest | (0, 0, 42) |
| 8 | bed_frame | (0, 0, 48) |
| 9 | banner_patternA_red | (0, 0, 54) |
| 10 | table_medium | (0, 0, 60) |
| 11 | chair | (0, 0, 66) |
| 12 | coin_stack_small | (0, 0, 72) |
| 13 | stairs | (0, 0, 78) |

Позиции в файле — относительно `Prototypes` (локальные); `Prototypes` стоит в `(-20, 0, 0)`.

## Гейт и прогоны

Команды: `Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game ...`. Версия Godot 4.7.2.

1. `--import` (код 0):
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org
... (строки прогресса first_scan_filesystem и loading_editor_layout, все DONE) ...
import exit: 0
```
2. Зелёный прогон `--script res://tests/level_check.gd` (после удаления файлов, после конвертации):
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

ok: корень Level существует
ok: модулей 285, у каждого инстанс .gltf
ok: в Prototypes по одному инстансу на каждый kind (14)
ok: Prototypes вне плана, x = -20.0
ok: модули уровня не находятся в Prototypes
ok: в корне есть Camera3D
ok: в корне есть WorldEnvironment
failed: 0
level_check exit: 0
```

## Мутации (копия `game/` в `E:\Temp\opencode\t11_mut\game`)

Мутация А — точно по брифу: удалить один инстанс модуля (`stairs_268` из двух инстансов вида `stairs`):
```
ok: корень Level существует
ok: модулей 284, у каждого инстанс .gltf
ok: в Prototypes по одному инстансу на каждый kind (14)
ok: Prototypes вне плана, x = -20.0
ok: модули уровня не находятся в Prototypes
ok: в корне есть Camera3D
ok: в корне есть WorldEnvironment
failed: 0
mutA exit: 0
```

Мутация Б — удалить все инстансы вида `stairs` (`stairs_268` и `stairs_285`):
```
ok: корень Level существует
ok: модулей 283, у каждого инстанс .gltf
ПРОВАЛ Prototypes: лишний kind stairs
ok: Prototypes вне плана, x = -20.0
ok: модули уровня не находятся в Prototypes
ok: в корне есть Camera3D
ok: в корне есть WorldEnvironment
failed: 1
mutB exit: 1
```

Вывод: проверка ловит удаление вида целиком (мутация Б, имя ассерта «в Prototypes по одному инстансу на каждый kind»). Одиночное удаление (мутация А) не ловится, потому что ни у одного вида нет единственного экземпляра (минимум 2: `wall_archedwindow_open`, `coin_stack_small`, `stairs`), а бриф требует без жёстких чисел. Это ограничение дизайна проверки, см. «Открытые вопросы».

## Скриншот и регрессия визуала

Скрипт `E:\Temp\opencode\t11_capture.gd` (временный, удалён): окно, `--resolution 1152x648`, 10 кадров `process_frame` и `RenderingServer.frame_post_draw`, `root.get_texture().get_image().save_png(...)`. Исходный `t10_capture.gd` в T10 не сохранился, поэтому скрипт написан заново по описанию в отчёте T10.
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

D3D12 12_0 - Forward+ - Using Device #0: NVIDIA - NVIDIA GeForce RTX 4060

сохранено 1152x648, err 0
capture exit: 0
```

Сравнение с `T10-scene-screenshot.png` (1152x648, оба):
- попиксельно (`System.Drawing`): 581 отличающийся пиксель, bbox x 35..58, y 0..27;
- это одна бочка в левом верхнем углу кадра, прототип `barrel_large` (`Prototypes`, z = 24);
- раскладка, стены, пол, свет, камера совпадают: различий в остальной части кадра нет.

Вывод: раскладка и камера совпали. Прототип попадает в кадр (см. «Открытые вопросы»).

## Решения вопреки брифу

- Ничего не сделано вопреки брифу в части раскладки и позиций. Прототипы поставлены по брифу: `(-20, 0, 0)`, `z = i*6`.
- Ожидание брифа «мутация одного инстанса → код 1» не выполнено: с правилом «без жёстких чисел» и сравнением по набору видов это невозможно (см. «Открытые вопросы»). Проверку не ослаблял и не усиливал.
- Файлы `.uid` удалённых скриптов удалены вместе со скриптами: иначе остались бы сиротские метаданные.

## Что заметил и не стал делать

- Прототип `barrel_large` попадает в кадр камеры при `x = -20` (видно в скриншоте). Визуальная регрессия по плану уровня нулевая, но прототипы видны игроку в редакторе и в сборке. Бриф фиксирует `x = -20`, я не менял.
- В `level.tscn` узлы модулей теперь называются `<kind>_<NNN>`, а не `<kind>`. Имя прототипа — `<kind>` без номера (как в брифе). Это не конфликтует, но в дереве выглядит разнородно. Не менял.
- `level_check.gd` проверяет `scene_file_path` инстанса. В Godot 4.7.2 он заполнен у инстансов, загруженных из `PackedScene`, так что проверка не давала ложного красного.
- Конвертация перенесла весь `level.tscn` через `pack`: `unique_id` и порядок свойств переписаны Godot. Значения свойств света, камеры и окружения прежние.

## Открытые вопросы

1. **Одиночное удаление модуля не ловится** (мутация А, код 0). Варианты: (а) принять (проверка структурная: набор видов и типы узлов, без чисел по брифу); (б) добавить проверку, что у каждого вида в модулях не меньше 2 экземпляров — это тоже жёсткое правило, но мягкое; (в) сравнивать число модулей с сохранённым значением в данных — противоречит «без чисел». Нужно решение ведущего.
2. **Прототип виден в кадре** (`x = -20`). Вариант: увеличить отступ (например, `x = -40`). Не менял без решения.
