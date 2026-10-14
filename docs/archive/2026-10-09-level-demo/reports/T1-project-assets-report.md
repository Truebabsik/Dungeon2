# Отчёт T1 — проект Godot и ассеты

Статус: DONE_WITH_CONCERNS (см. «Решения вопреки брифу» и «Что заметил»).

## Что изменено

1. `game/project.godot` (создан):
   - `config_version=5` (формат Godot 4);
   - `config/name="Dungeon2"`;
   - `config/features=PackedStringArray("4.7", "Forward Plus")`;
   - `run/main_scene="res://level/level.tscn"` (сцены ещё нет, ожидаемо);
   - `rendering_device/driver.windows="d3d12"` (как в соседнем `F:\WORK\Fixer\game\project.godot`).
   - Иконка не указана: `res://icon.svg` в проекте нет.

2. `game/assets/kaykit/` (создан), плоская раскладка, относительные `uri` сохранены:
   - 16 `.gltf` из `art/KayKit_Dungeon_Pack_1.1_FREE/Assets/gltf/`:
     `floor_tile_large`, `wall`, `wall_corner`, `wall_doorway`, `wall_archedwindow_open`, `stairs`, `pillar`,
     `table_medium`, `chair`, `barrel_large`, `bed_frame`, `chest`, `shelves`, `coin_stack_small`,
     `torch_mounted`, `banner_patternA_red`;
   - 16 соответствующих `.bin` (по одному на каждый `.gltf`);
   - `dungeon_texture.png` (общая текстура, лежит рядом с `.gltf` в паке, а не в `Assets/textures/`);
   - `License.txt` из корня пака.
   - 17 файлов `*.import` (`*.gltf.import` ×16 и `dungeon_texture.png.import`), созданных пробой `--import` (см. «Исправления после ревью»).
    - Всего файлов в `game/assets/kaykit/`: 16 + 16 + 1 + 1 + 17 = 51 (проверено `Get-ChildItem`).

3. `docs/current/2026-10-09-level-demo/reports/T1-project-assets-report.md` (этот файл).

Оригинал `art/**` не менялся. Коммит не делался.

## Внешние ресурсы по каждому `.gltf`

У каждого из 16 файлов ровно два внешних `uri` (все найдены и скопированы):

| .gltf | буфер (.bin) | текстура |
|---|---|---|
| floor_tile_large | floor_tile_large.bin | dungeon_texture.png |
| wall | wall.bin | dungeon_texture.png |
| wall_corner | wall_corner.bin | dungeon_texture.png |
| wall_doorway | wall_doorway.bin | dungeon_texture.png |
| wall_archedwindow_open | wall_archedwindow_open.bin | dungeon_texture.png |
| stairs | stairs.bin | dungeon_texture.png |
| pillar | pillar.bin | dungeon_texture.png |
| table_medium | table_medium.bin | dungeon_texture.png |
| chair | chair.bin | dungeon_texture.png |
| barrel_large | barrel_large.bin | dungeon_texture.png |
| bed_frame | bed_frame.bin | dungeon_texture.png |
| chest | chest.bin | dungeon_texture.png |
| shelves | shelves.bin | dungeon_texture.png |
| coin_stack_small | coin_stack_small.bin | dungeon_texture.png |
| torch_mounted | torch_mounted.bin | dungeon_texture.png |
| banner_patternA_red | banner_patternA_red.bin | dungeon_texture.png |

Всего `uri` в JSON: 32 (16 буферов + 16 текстур), найдено на диске: 32, отсутствующих: 0.
Поиск `uri` — регулярным выражением `"uri"\s*:\s*"..."` по всем 16 файлам; проверка — `Test-Path` относительно каталога самого `.gltf`.

## Проверка

- `Test-Path`-проверка скопированных `.gltf`: 16 файлов в `game/assets/kaykit/` (`gltf: 16`).
- Для каждого `uri` из скопированных `.gltf` файл рядом существует: `uri checked: 32 missing: 0`.

## Проба `--import`

Бинарник. По брифу путь `F:\WORK\Godot_v4.7.2-stable_win64.exe` — это **каталог**, внутри которого лежат
`Godot_v4.7.2-stable_win64.exe` (GUI) и `Godot_v4.7.2-stable_win64_console.exe`. Для захвата stdout/stderr и
кода возврата использован console-вариант той же версии (`v4.7.2.stable.official.ed1daf0bf`):

Команда:
```
& "F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe" --headless --path "F:\WORK\Dungeon2\game" --import
```

Первый прогон (проба до ревью, `game/` без `.gitignore`): реимпорт выполнился, `[ DONE ] import` по каждому из 17
ресурсов (16 `.gltf` и `dungeon_texture.png`), затем тот же `ERROR` по `level.tscn`, код **0**.
Полный вывод первого прогона — длинный поток прогресс-строк; в отчёт вынесены итоговые строки.

Повторный прогон (после ревью, с `game/.gitignore`), дословно (ANSI-коды убраны, прогресс-строки опущены):

```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org
[ DONE ] first_scan_filesystem
[ DONE ] loading_editor_layout
ERROR: Cannot open file 'res://level/level.tscn'.
   at: load (scene/resources/resource_format_text.cpp:1442)
ERROR: Failed loading resource: res://level/level.tscn.
   at: _load (core/io/resource_loader.cpp:317)
```

Код возврата повторного прогона: **0** (`$LASTEXITCODE`, вывод сохранён в `E:\Temp\opencode\t1_import_rerun.txt`).
В повторном прогоне нет шагов `reimport` и `[ DONE ] import`: `.import`-файлы и кэш `.godot/imported/` уже актуальны,
реимпорт не требовался. Поэтому подтверждение импорта — первый прогон (выше) и 17 `.import`-файлов на диске.

Строка `ERROR: ... res://level/level.tscn` относится к `run/main_scene`, которой пока нет (появится в задаче 3).
По брифу решение принимается по коду возврата; код 0. Текст stderr здесь зафиксирован дословно.

Побочный результат пробы (первый прогон): создано **17 файлов `*.import`** рядом с ресурсами (`*.gltf.import` ×16,
`dungeon_texture.png.import`), и каталог `game/.godot/` (кэш импорта и редактора: `imported/`, `editor/`,
`uid_cache.bin`, `global_script_class_cache.cfg`). Файлы `*.import` оставляем в git (по решению ведущего);
`game/.godot/` игнорируется `game/.gitignore`.

## Решения вопреки брифу

1. Бинарник запускался через `Godot_v4.7.2-stable_win64_console.exe`, а не `Godot_v4.7.2-stable_win64.exe`
   (см. выше: по пути из брифа лежит каталог, а не исполняемый файл). Движок тот же, версия та же.
2. `dungeon_texture.png` скопирован в плоскую раскладку `game/assets/kaykit/`, рядом с `.gltf`: в паке он лежит
   там же (`Assets/gltf/dungeon_texture.png`). В `Assets/textures/` тоже есть файл того же имени (17047 байт),
   но относительный `uri` из `.gltf` указывает на текстуру рядом, поэтому скопирован именно тот.
3. Layout: все файлы плоско в `game/assets/kaykit/`, подкаталогов нет (относительные `uri` это допускают).

## Исправления после ревью

1. **Счёт файлов.** Было «34», верно **51**: 16 `.gltf` + 16 `.bin` + `dungeon_texture.png` + `License.txt` + 17 `*.import`.
   Ошибка: `.import` не были учтены при первом подсчёте.
2. **`.import`-файлы.** Утверждение «Файлы `.import` Godot 4.7 не создал» было неверным. Пробой создано 17 файлов
   `*.import` с временем пробы (`09.10.2026 17:07:30`): `*.gltf.import` ×16 и `dungeon_texture.png.import`.
   Решение (по указанию ведущего): `.import` оставляем в git, они нужны для импорта.
3. **`game/.gitignore`** создан, одна строка: `.godot/`. Кэш `game/.godot/` из git исключён.
4. **Повторный прогон** `--import` после правок: код возврата **0**. Вывод — в разделе «Проба `--import`».
   В нём нет шагов реимпорта, потому что кэш актуален; подтверждение импорта — первый прогон.
5. **Строка «DONE» в разделе пробы** заменена полным текстом итогов первого и повторного прогонов.
   Прежний вариант с `...` не подтверждал импорт.

## Что заметил и не стал делать

- `game/.godot/` — кэш движка, появился от пробы. Закрыто в «Исправления после ревью»: `game/.gitignore` с `.godot/`.
- `project.godot` без `config/icon`: иконки нет. Не добавлял, чтобы не ссылаться на несуществующий файл.
- `Godot_v4.7.2-stable_win64.exe` в `F:\WORK\` — каталог. Для будущих брифов путь к бинарнику стоит поправить
  на `...\Godot_v4.7.2-stable_win64_console.exe` (или на вызов из каталога), иначе `Start-Process` падает с
  «Отказано в доступе».
- В `Assets/gltf/` есть и другие `.gltf` (не из списка брифа) — не копировались, по брифу не нужны.
