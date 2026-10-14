# Ревью T18: ресурсы KayKit_Adventurers_2.0_FREE, MeshLibrary 408, level_check

Ревьюер: субагент (только проверка, файлы проекта не менялись). Вход: бриф `briefs/T18-adventurers.md`, отчёт `reports/T18-adventurers-report.md`, `game/tests/level_check.gd`, `game/assets/mesh_library.tres`, `game/level/level.tscn`, архив `E:\Temp\opencode\adventurers\KayKit_Adventurers_2.0_FREE`.

## Гейт (прогон сам)

Команда: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`

Вывод (дословно):

```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

ok: корень Level существует
ok: модулей 26, у каждого инстанс .gltf
ok: в корне есть Camera3D
ok: в корне есть WorldEnvironment
ok: Character есть, инстанс из kaykit_animations
ok: GridMapWall, mesh_library с 408 элементами, cell_size (4.0, 4.0, 4.0), ячеек 115
ok: GridMapFloor, mesh_library с 408 элементами, cell_size (4.0, 4.0, 4.0), ячеек 276
ok: GridUpper, mesh_library с 408 элементами, cell_size (4.0, 4.0, 4.0), ячеек 1
failed: 0
```

Код возврата: **0**. Совпадает с отчётом.

## Проверка по пунктам задания

1. **Ресурсы — ADDRESSED.**
   - `game/assets/kaykit_adventurers/`: 31 `.gltf`, 31 `.bin`, 5 `.png` (`*_texture.png`), `License.txt`. Все `.gltf`/`.bin` побайтно совпадают с `Assets\gltf` архива (SHA-сверка, расхождений 0). Имена 31 новой записи совпадают с basename архивных `.gltf` (diff 0).
   - `characters/`: 6 `.glb` и 5 `*_texture.png` из `Characters\gltf`, побайтно совпадают (расхождений 0). Плюс 6 png, созданных импортом Godot (`Barbarian_barbarian_texture.png` и т.п.) и 17 `.import` — см. Minor-2.
   - `kaykit_animations/animations/Rig_Medium/`: `Rig_Medium_MovementBasic.glb` уже есть, SHA256 = архив (`11422AFD…FA29E`). `Rig_Medium_General.glb` один экземпляр, SHA256 = архив (`5F725C0F…FDD7AD`). Дубля нет. Отклонение от брифа (файл не копировался) — обосновано, см. Minor-3.
   - Не должно быть obj/fbx: в `game/assets/**` по пути `adventurers` `.obj`/`.fbx` не найдено. ADDRESSED.
2. **mesh_library.tres — ADDRESSED.**
   - Заголовок: `[gd_resource type="MeshLibrary" format=4 uid="uid://cm7fsg1yj5qfl"]`, uid прежний (строка 1).
   - Элементов: 408 (`item/0…407/name`, id без пропусков и дублей). Имена уникальны (408 из 408). Конфликтов имён нет.
   - Элементов без меша: 0 (408 строк `item/N/mesh`, ни одной `null`).
   - Новые 31 имени (id 377…407) совпадают с basename архивных `.gltf` (diff 0).
   - `ext_resource` (97): все ссылки `ExtResource(...)` объявлены, все пути существуют на диске.
   - `.obj`-ссылок 90 (dungeon_pack), текстур `kaykit_adventurers` 5. Ссылок на `.gltf` в библиотеке нет.
   - Размер ~15.7 МБ (отчёт сообщает то же).
3. **level.tscn — ADDRESSED (с оговоркой).** Файл не менялся агентом: в отчёте сказано, что сцена сохранена пользователем 11.10.2026 21:28:58, mtime совпадает. Git нет, побайтовый diff не сделать; подтверждаю только состав узлов.
   - Узлы пользователя на месте: `ChainLink`, `ChainLink2`, `Book1`, `Book2`, `CarpetPlaneFlat`, `RChestGold`, `Cage1`, `Cage`, `Cage2`, `Crate2` (все `MeshInstance3D`, прямые дети `Level`, строки `[node name=...]`).
   - `GridMapWall`, `GridMapFloor`, `GridUpper` (GridMap) на месте, `Character` (Node3D) на месте. Камера, свет, WorldEnvironment на месте.
4. **level_check.gd — ADDRESSED (с оговоркой).**
   - Исключение узкое: `collect_modules`, строки 62–71, пропускается только прямой ребёнок `is_bare_mesh` (строки 177–178): `MeshInstance3D` с пустым `scene_file_path`. Node3D без инстанса, `MeshInstance3D` с инстансом сцены и инстансы `kaykit/*.gltf` проверяются как раньше (строки 75–93).
   - Сверка с T17 по смыслу: в T17 такие узлы попадали в проверку 2 как Node3D без `.gltf` и давали провал (T17 отчёт, строки 61–62). Теперь вне проверки остаются только bare MeshInstance3D. Модули-инстансы по-прежнему проверяются по `kind_of` и FileAccess.
   - Скрытие провала для kaykit-инстансов: инстанс из `kaykit/` всегда имеет `scene_file_path`, значит не bare и не исключается. Если такой инстанс удалить, число модулей станет 25 и сработает ассерт `MODULES_EXPECTED` (строки 89–92). Если заменить его bare-мешем, число останется 25 — провал тоже. Проверка не скрывает провал kaykit-инстансов.
   - Остальные проверки (камера, среда, Character, GridMap x3, размер ячейки, position.y у GridUpper, число элементов 408) не ослаблены: сравнить с T17 можно по строкам 97–173, изменена только константа `GRIDMAP_LIBRARY_ITEMS` (строка 12) и её комментарий (строка 11), как сказано в брифе.
   - Проверка счёта `MODULES_EXPECTED := 26` (строка 19) в отчёте сверена с 26 инстансами `kaykit/*.gltf` в level.tscn: я сверил список по ext_resource сцены, совпадает.
5. **Прогон — ADDRESSED.** `failed: 0`, код **0**, stderr пуст (см. гейт).
6. **t18_* в E:\Temp\opencode\ — ADDRESSED.** Рекурсивный поиск `t18_*` не нашёл ни одного файла. Папка `E:\Temp\opencode\adventurers\` осталась (не запрещено брифом).

## Находки

- **Critical 0.**
- **Important 1.** Решение об исключении bare MeshInstance3D из проверки модулей (`level_check.gd:62–71`, `is_bare_mesh` строки 177–178) зафиксировано только в отчёте T18, в `ledger.md` записи нет. Бриф запрещал ослаблять проверки, поэтому решение пользователя должно попасть в журнал/дизайн до перехода к следующей задаче.
- **Minor 4.**
  1. `MODULES_EXPECTED := 26` (`level_check.gd:19`) — единственный страж числа модулей; любое законное изменение `kaykit`-инстансов требует ручной правки константы (как и в T17).
  2. В `game/assets/kaykit_adventurers/characters/` лежат 6 png, созданных импортом Godot из встроенных текстур `.glb` (`Barbarian_barbarian_texture.png` и т.д.) и 17 `.import`. Это штатные артефакты, отчёт их упоминает; решить, коммитить ли их.
  3. Отклонение от брифа: `Rig_Medium_MovementBasic.glb` не копировался (уже есть, SHA совпадает), и `mesh_library.tres` достроен добавлением, а не полной пересборкой (мотивировано: id ячеек GridMap в `level.tscn`). Старые 377 элементов проверены только по именам (бэкап удалён), так что совпадение `mesh`-путей для id 0…376 на диске не подтверждено.
  4. `ext_resource` в `mesh_library.tres` без `uid` (отчёт упоминает); работает по `path`. Вместе с 15.7 МБ вершин текстом — кандидат на binary `.res` позже.

## Assessment

С правками. Ресурсы, библиотека (408, уникальные имена, uid прежний) и гейт зелёные, проверка не ослаблена сверх узкого исключения. Нужно зафиксировать решение об исключении bare MeshInstance3D в журнале задачи (Important-1).

отчёт: F:\WORK\Dungeon2\docs\current\2026-10-09-level-demo\reports\T18-adventurers-review.md
