# T2r-c — даунскейл текстур четырёх пропсов (Hunyuan → `_1024.glb`)

Статус: **DONE**.

## 1. Что изменено

| Файл | Что |
|---|---|
| `game/tools/glb_texture_downscale.py` (новый, 201 строка) | параметризованный скрипт даунскейла: импорт glb → `img.scale` для `bpy.data.images` с max-стороной > `--max` → экспорт GLB |
| `art/models/founder_statue_1024.glb` (новый) | 5 147 524 Б |
| `art/models/stall_1024.glb` (новый) | 3 975 928 Б |
| `art/models/arc3_1024.glb` (новый) | 3 783 696 Б |
| `art/models/wall-torch_1024.glb` (новый) | 3 297 240 Б |

Исходники не тронуты — SHA256 до и после прогона совпадают (см. §4).

## 2. Как устроено решение

Скрипт запускается Blender headless, аргументы — после `--`:

```
blender -b --python game/tools/glb_texture_downscale.py -- [--max N] [--out-dir DIR] [--suffix S] [--out FILE.glb] вх1.glb ...
```

- Пути вход/выход полностью параметризованы (по умолчанию итог кладётся рядом с исходником как `<stem><suffix>.glb`); никаких имён из брифа в коде нет — станет основой скилла.
- На каждый файл: `read_factory_settings(use_empty=True)` → `import_scene.gltf` → печать всех изображений до → `img.scale` пропорционально для max-стороны > `--max` → `export_scene.gltf(export_format='GLB', export_image_format='AUTO', export_apply=True, export_yup=True)`. Геометрия не трогается (никакого декимейта/нормалей) — консистентно со всеми существующими `_1024`-пропсами.
- **Треугольники «до/после» меряются одним и тем же методом на байтах файлов**: в скрипт встроен мини-парсер GLB (12-байтовый заголовок → JSON-чанок → `primitives[].indices.count / 3`, mode=4). Кросс-чек — число loop-triangles импортированной сцены в Blender. Если «до ≠ после» — скрипт печатает `ERROR` и выходит с кодом 1.
- Пакетный режим: один запуск Blender на список файлов; ошибка одного файла не прерывает остальные, итоговый код = 1, если был хоть один сбой.

## 3. Доказательства (дословно)

### 3.1 Blender 5.2, headless — вывод скрипта (значимые строки)

`wall-torch` (отдельный прогон):

```
=== SRC: F:\WORK\Dungeon2\art\models\wall-torch.glb
DST: F:\WORK\Dungeon2\art\models\wall-torch_1024.glb
IMAGES BEFORE:
    texture_pbr_20250901 (4096, 4096) packed
    texture_pbr_20250901_metallic-texture_pbr_20250901_roughness (4096, 4096) packed
    texture_pbr_20250901_normal (4096, 4096) packed
SCALED:
    texture_pbr_20250901 (4096, 4096) -> (1024, 1024)
    texture_pbr_20250901_metallic-texture_pbr_20250901_roughness (4096, 4096) -> (1024, 1024)
    texture_pbr_20250901_normal (4096, 4096) -> (1024, 1024)
SCALED COUNT: 3; UNCHANGED (<= 1024): 0
TRIS (glb bytes before): 50000 (non-tri prims: 0)
TRIS (blender import):    50000
TRIS (glb bytes after):   50000 (non-tri prims: 0)
SIZE before: 23810788
SIZE after:  3297240
DONE: OK
```

Пакетный прогон (`founder_statue`, `stall`, `arc3`); у всех троих та же картина — 3 изображения 4096×4096 → 1024×1024, `UNCHANGED: 0`:

```
=== SRC: F:\WORK\Dungeon2\art\models\founder_statue.glb
DST: F:\WORK\Dungeon2\art\models\founder_statue_1024.glb
SCALED:
    texture_pbr_20250901 (4096, 4096) -> (1024, 1024)
    texture_pbr_20250901_metallic-texture_pbr_20250901_roughness (4096, 4096) -> (1024, 1024)
    texture_pbr_20250901_normal (4096, 4096) -> (1024, 1024)
TRIS (glb bytes before): 49984 ... TRIS (blender import): 49984 ... TRIS (glb bytes after): 49984
SIZE before: 42009860 / SIZE after: 5147524
=== SRC: ...stall.glb     TRIS 49980 = 49980 = 49980   SIZE 30012632 -> 3975928
=== SRC: ...arc3.glb      TRIS 50000 = 50000 = 50000   SIZE 27882368 -> 3783696
DONE: OK
```

(`IMAGES BEFORE:` у пакетного прогона печатает те же три имени 4096×4096 packed — полный лог: `E:\Temp\opencode\props_downscale_batch.log`, `E:\Temp\opencode\props_downscale_walltorch.log`.)

### 3.2 Проверка в Godot 4.7.2 (дословный вывод `check.log`)

Подготовка: `E:\Temp\opencode\props_check\` ← копии четырёх `_1024.glb`, `project.godot`, `check_props.gd`; `.godot` удалён перед прогоном. `--import` → код 0, в логе импорта нет ни одной строки ERROR/WARNING. Затем `--script res://check_props.gd`:

```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

FILE: founder_statue_1024.glb
MESHES: 1 (instances: 1)
TRIANGLES: 49984 (expected 49984)
AABB_SIZE: (0.472936, 1.013907, 0.467368)
AABB_POS: (-0.229993, -0.000000, -0.259684)
MAT: Material.001
TEX Material.001 albedo: 1024x1024
TEX Material.001 metallic: 1024x1024
TEX Material.001 roughness: 1024x1024
TEX Material.001 normal: 1024x1024
FILE: stall_1024.glb
MESHES: 1 (instances: 1)
TRIANGLES: 49980 (expected 49980)
AABB_SIZE: (0.727764, 0.831833, 0.566279)
AABB_POS: (-0.362396, -0.000000, -0.272189)
MAT: Material.001
TEX Material.001 albedo: 1024x1024
TEX Material.001 metallic: 1024x1024
TEX Material.001 roughness: 1024x1024
TEX Material.001 normal: 1024x1024
FILE: arc3_1024.glb
MESHES: 1 (instances: 1)
TRIANGLES: 50000 (expected 50000)
AABB_SIZE: (0.677088, 1.031060, 0.196432)
AABB_POS: (-0.338135, -0.000000, -0.101296)
MAT: Material.001
TEX Material.001 albedo: 1024x1024
TEX Material.001 metallic: 1024x1024
TEX Material.001 roughness: 1024x1024
TEX Material.001 normal: 1024x1024
FILE: wall-torch_1024.glb
MESHES: 1 (instances: 1)
TRIANGLES: 50000 (expected 50000)
AABB_SIZE: (0.693110, 1.006260, 0.594406)
AABB_POS: (-0.288353, -0.000000, -0.298336)
MAT: Material.001
TEX Material.001 albedo: 1024x1024
TEX Material.001 metallic: 1024x1024
TEX Material.001 roughness: 1024x1024
TEX Material.001 normal: 1024x1024
FAILED: 0
```

Коды возврата: `--import` = **0**, `--script` = **0**, `FAILED: 0`. Все 16 текстур (4 модели × 4 слота) — 1024×1024; треугольники совпали с исходниками; пол у всех моделей на Y=0 (высота по Y) — корневой поворот glb +90° по X учтён (см. §6, находка 1).

## 4. Прогоны (команды и коды)

```
blender -b --python game\tools\glb_texture_downscale.py -- ...wall-torch.glb     → EXIT=0
blender -b --python game\tools\glb_texture_downscale.py -- ...founder_statue.glb ...stall.glb ...arc3.glb  → EXIT=0
Godot_v4.7.2-console.exe --headless --path E:\Temp\opencode\props_check --import → EXIT=0
Godot_v4.7.2-console.exe --headless --path E:\Temp\opencode\props_check --script res://check_props.gd → EXIT=0
```

Неизменность исходников, SHA256 до и после (совпали полностью):

```
founder_statue.glb  0E901CEAD04E9A419C5DC0A54AF61D99B4AEC9E9E41C34C138DB89E29EA7C7DB
stall.glb           A0498F1B9D3CDB805468425C12F6F90F0DC45A7ECE40895DE913E29BC4C3E5C9
arc3.glb            36C9B9BE6A1EC0931283303699EA9A1D5B08B88EC145D2506352CD9C628D6CB1
wall-torch.glb      E18EB8EFD04754423363A05441399D5618A6CD6A79BB018215A502B7BF8A0879
```

Копии `_1024.glb` в временной папке побайтово совпали с файлами в `art/models/` (SHA256-equality: True для всех четырёх) — проверял до удаления папки.

## 5. Решения вопреки брифу

1. **`project.godot` во временной папке — минимальный, не копия игрового.** Первый прогон шёл с точной копией `game/project.godot`: коды 0/0, но в логе импорта была строка `ERROR: Failed loading resource: res://level/level.tscn` (наш `run/main_scene` указывает на уровень, которого во временной папке нет). Это шум моей же подготовки, а не артефактов, но зелёный код с ERROR в логе — ровно тот класс ложных зелёных, что описан в `constraints.md` §1. Переделал как в T2-arc2 (минимальный `project.godot` c `config/name="props_check"`) — лог чистый. Повторный `--import` на удалённом `.godot`, оба кода 0.
2. **«Тр. до/после» меряется парсером байтов glb, а не только Blender'ом.** Бриф требовал «замерить тр. ДО/ПО» — замерить только через Blender значило бы сравнивать импорт исходника с импортом итога двумя проходами одного движка. Парсер JSON-чанка считает одинаково на байтах обоих файлов и заодно работает без Blender; Blender-счёт оставлен кросс-чеком (числа совпали во всех четырёх случаях: 49984/49980/50000/50000).

## 6. Что заметил и не стал делать

1. **Находка (важная для ревью и гейта): зелёный Godot-прогон при неверном AABB.** Первая версия `check_props.gd` брала `mi.global_transform` в `_init` — в `_init` дерево ещё не инициализировано, `global_transform` вернул identity и напечатал в stderr `ERROR: Condition "!is_inside_tree()"`. Код возврата при этом был **0**, `FAILED: 0` — то есть ложнозелёный прогон с AABB без корневого поворота (высота меша «лежала» по Z, ровно та ошибка, которую T2-arc2 описал словами «первая попытка без учёта корневого преобразования»). Исправил: трансформ собирается вручную из локальных `transform` от меша до корня сцены (`_world()`), AABB — через 8 углов (`_xform_aabb()`). После правки stderr чистый, пол у всех четырёх на Y=0. **Вывод для процесса:** stderr в головном прогоне — не «шум», а единственный сигнал о том, что здесь проверка считала не то; вердикт «код 0» тут ничего не доказывал. Возможно, стоит в `review-checklist.md` добавить класс дефекта «зелёный прогон при ERROR в логе» — это решение ведущего, я файлы `docs/agents/*` не трогал.
2. Все четыре модели — типичный вывод Hunyuan3D: ровно 3 текстуры с одинаковыми именами (`texture_pbr_20250901*`, все 4096×4096) и ~50 000 треугольников (49984/49980/50000/50000). Металлик и роугнес — одна упакованная карта `..._metallic-..._roughness`; идентичность двух слотов в Godot не проверял (как и в T2-arc2).
3. AABB осмысленный по форме: `arc3` — 0.677 × **1.031** × 0.196 (арка выше и глубже arc2: 0.836 × 0.871 × 0.121), `wall-torch` — 0.693 × **1.006** × 0.594, `stall` — 0.728 × **0.832** × 0.566, `founder_statue` — 0.473 × **1.014** × 0.467. Это размеры в метрах glTF (до постановочного масштаба) — расставить пропорции в сцене предстоит ведущему.
4. `game/tools/__pycache__/` содержит `.pyc` от `build_cave_gate.py` (не мой файл) — не трогал; мой скрипт там не компилился.
5. Согласно `AGENTS.md`, «`game/` нет» — устарело: `game/` есть (level, tests, tools, assets), это уже зафиксировано в самих указаниях, дополнительно правил не вносил.

## 7. Уборка

`E:\Temp\opencode\props_check\` (копии glb, `project.godot`, `check_props.gd`, `.godot`, `import.log`, `check.log`) — **удалена** после проверки; текст `check.log` сохранён дословно в §3.2. Логи прогона даунскейла оставлены разрешённым брифом местом: `E:\Temp\opencode\props_downscale_walltorch.log`, `E:\Temp\opencode\props_downscale_batch.log`.

## 8. Открытые вопросы

1. Нет блокирующих.
2. Процессные (решение ведущего): (а) добавить ли в `review-checklist.md` класс дефекта «зелёный код при ERROR в логе» — по находке §6.1; (б) посадочные масштабы/позиции четырёх пропсов — геометрия в метрах glTF дана в §6.3, решения за ведущим.
