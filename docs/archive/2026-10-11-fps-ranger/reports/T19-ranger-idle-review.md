# Ревью T19: Рейнджер на сцене, idle на его скелете

Ревьюер: отдельный субагент. Код не правился. Проба и гейт прогнаны самостоятельно.

## Гейт

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

Код возврата: 0. stderr: пусто. Проверка не менялась (`level_check.gd` не трогался). Числа 26 / 408 / 115 / 276 / 1 совпадают с T18-отчётом.

## Проба анимации (headless, `E:\Temp\opencode\t19_review.gd`, удалена)

Вывод (дословно):

```
current_animation: Idle_A
is_playing: true
root_node resolved: /root/Level/Character/Ranger
tracks: 54 unresolved: 0 unique bones: 23
ranger bones: 23
bones from tracks missing in Ranger: []
Rig_Medium visible: false
Ranger visible: true
```

Код возврата: 0. Дерево `Ranger` (проба №2): `Ranger` → `Rig_Medium` → `Skeleton3D` → 8 мешей `Ranger_*` (`mesh=true`, `skin=true`, `vis=true`). `Character.script = res://level/character_idle.gd`. Ожидание `Idle_A` / `true` выполнено.

## Пункты задания

1. Сцена: ADDRESSED. Инстанс Ranger: `level.tscn:89`. Скрыт меш-узел манекена: `level.tscn:90-92` (`Rig_Medium` с `visible = false`, узел и `AnimationPlayer` сохранены). `root_node = NodePath("../../Ranger")`: `level.tscn:94-95`, от `AnimationPlayer` через `..`/`../..` даёт `Character/Ranger`, проверено пробой. Количество `[node` в файле: 48. В T18 было 45 узлов, плюс Ranger и два override (`Rig_Medium`, `AnimationPlayer`) = 48, то есть других изменений по числу узлов нет. Модули, GridMap*, Camera3D, WorldEnvironment, DirectionalLight3D, MeshInstance3D пользователя (ChainLink, ChainLink2, Book1, Book2, CarpetPlaneFlat, RChestGold, Cage1, Cage, Cage2, Crate2): `level.tscn:118-206`, по счётам совпадают с T18. Побайтного сравнения с pre-T19 снимком нет (снимка нет, git нет), поэтому неизменность строк не доказана, только по числам и узлам. Размер файла 18146 → 18584 байт, дельта +438 объясняется добавленными строками.
2. Анимация: ADDRESSED. `current_animation = Idle_A`, `is_playing = true`, проба выше.
3. Кости: ADDRESSED. 54 трека, 0 нерезолвящихся, 23 уникальных кости, все 23 есть в скелете Ranger. Число «54» подтверждено; «23» подтверждено.
4. `character_idle.gd`: ADDRESSED (оценка, см. ниже).
5. Гейт: ADDRESSED. `failed: 0`, код 0.
6. Нет `t19_*` в `E:\Temp\opencode\`: ADDRESSED. Мои временные файлы тоже удалены.
7. Замечания в отчёте: ADDRESSED. Отчёт статус `DONE_WITH_CONCERNS`, и замечания перечислены в §5 «Что заметил и не стал делать» (4 пункта плюс временные файлы). Я нашёл и свои, см. «Находки».

## Оценка пункта 4 (character_idle.gd)

Допустимо как временное решение. Скрипт остаётся на `Character` и вызывает `get_node("Rig_Medium_General/AnimationPlayer").play("Idle_A")`. Путь к `AnimationPlayer` валиден, `Idle_A` проигрывается (проба). Скрипт `extends Node3D`, а `CharacterBody3D` тоже наследник `Node3D`, так что при переходе в T21 он продолжит работать. Риск: скрипт жёстко завязан на имя узла `Rig_Medium_General`; при переходе в T21 имя менять не стоит, либо T21 переносит `play` в контроллер. Это решение плана, не дефект T19.

## Гейт / проверка по плану

`level_check.gd` прошёл: проверка `Character` идёт по инстансу из `kaykit_animations/` (`Rig_Medium_General`), и он остаётся. Ожидаемой поломки из-за смены `Character` нет (T22 её ещё не требует).

## Находки

- Critical 0
- Important 0
- Minor 5:
  - M1. Видимое тело сдвинулось: `Ranger` стоит в origin `Character`, а `Rig_Medium_General` стоит с `x = 1.5525303` (`level.tscn:87`). Тело теперь на 1.55 м левее прежнего манекена. Документировано в отчёте §2, но в `design.md` не отражено. Решение: зафиксировать в ledger, при T21 учесть при размещении капсулы.
  - M2. Скрыт весь `Rig_Medium` (вместе со `Skeleton3D`), а не только меш. Функционально верно (скелет манекена не анимируется, т.к. треки пишут в Ranger), но скелет манекена остаётся в дереве. Решение: оставить, как и в отчёте §5; удалить при T21/T23.
  - M3. Визуальной проверки нет: нет скриншота, поза и масштаб Ranger в уровне не просмотрены. Проверено только числовое. Решение: проверить в T23 приёмке в редакторе.
  - M4. Проба печатает `имена костей совпадают: false` (сравнение массивов с учётом порядка). Отчёт это объясняет, в проверках сравнивать множества. Исправлять нечего (проба удалена).
  - M5. `character_idle.gd:7` содержит жёсткий путь `Rig_Medium_General/AnimationPlayer`; при T21 путь надо сохранить или перенести `play` (см. пункт 4).

## Итоговый вердикт

assessment: Да. Acceptance плана T19 выполнен (`current_animation == "Idle_A"`, `is_playing() == true`, дословный вывод пробы в отчёте, 54/54 треков резолвятся на скелет Ranger, гейт `failed: 0`, код 0). Находки только Minor.

отчёт: F:\WORK\Dungeon2\docs\current\2026-10-11-fps-ranger\reports\T19-ranger-idle-review.md
