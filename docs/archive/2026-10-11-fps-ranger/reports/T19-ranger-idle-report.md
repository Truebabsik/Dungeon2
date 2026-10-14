# Отчёт T19: Рейнджер на сцене, idle на его скелете

Статус: DONE_WITH_CONCERNS (см. «Что заметил»: порядок костей и лишние имена в выводе Godot).

## 1. Проба (временная, удалена)

Скрипт `E:\Temp\opencode\t19_probe.gd`, прогон `Godot_v4.7.2-stable_win64_console.exe --headless --path game --script ...`, код 0.

Вывод (сокращён; трек-список полный по смыслу, см. ниже):

```
кости Ranger: 23, кости Rig_Medium_General: 23
имена костей совпадают: false
Ranger кости: ["root", "hips", "upperleg.l", "lowerleg.l", "foot.l", "toes.l", "upperleg.r", "lowerleg.r", "foot.r", "toes.r", "spine", "chest", "head", "upperarm.r", "lowerarm.r", "wrist.r", "hand.r", "handslot.r", "upperarm.l", "lowerarm.l", "wrist.l", "hand.l", "handslot.l"]
Rig кости: ["root", "hips", "upperleg.l", "lowerleg.l", "foot.l", "toes.l", "spine", "chest", "head", "upperarm.l", "lowerarm.l", "wrist.l", "hand.l", "handslot.l", "upperarm.r", "lowerarm.r", "wrist.r", "hand.r", "handslot.r", "upperleg.r", "lowerleg.r", "foot.r", "toes.r"]
root_node AnimationPlayer: ..
трек 0: Rig_Medium/Skeleton3D:hips (тип 1)
... (54 трека, все вида Rig_Medium/Skeleton3D:<кость>, типы 1/2/3)
треков: 54, путей без кости в Ranger: 0
```

Вывод по пробе:
- **Множества имён костей совпадают** (23 и 23 одинаковых имени). Строка «имена костей совпадают: false» — побочный эффект сравнения массивов с учётом порядка: порядок костей в файлах разный. Треки адресуются по имени кости, порядок не важен.
- Все 54 трека `Idle_A` адресуют `Rig_Medium/Skeleton3D:<кость>`; ни одна кость из треков не отсутствует в скелете Ranger.
- Дерево узлов: `Ranger.glb` → `Ranger` / `Rig_Medium` / `Skeleton3D` (меши `Ranger_*`). `Rig_Medium_General.glb` → `Rig_Medium_General` / `Rig_Medium` / `Skeleton3D` (меши `Mannequin_*`) + `AnimationPlayer`.

Вывод: пути совпадают, принят вариант из брифа (п. 2 «Если все пути совпадают»).

## 2. Что сделано в сцене

Файл: `F:\WORK\Dungeon2\game\level\level.tscn`.

1. Строка 30 (новая, после последнего ext_resource): `[ext_resource ... uid="uid://cmbrydvpn74wy" path="res://assets/kaykit_adventurers/characters/Ranger.glb" id="28_ranger"]` (uid взят из `Ranger.glb.import`).
2. Строки ~87–96 (после блока `Rig_Medium_General`):
   - `[node name="Ranger" parent="Character" unique_id=1100000210 instance=ExtResource("28_ranger")]` — видимый персонаж, без трансформации (identity внутри `Character`).
   - override `Character/Rig_Medium_General/Rig_Medium`: `visible = false` — меш манекена скрыт, узел и `AnimationPlayer` сохранены.
   - override `Character/Rig_Medium_General/AnimationPlayer`: `root_node = NodePath("../../Ranger")` — треки `Rig_Medium/Skeleton3D:*` теперь резолвятся от `Character/Ranger`.
3. `character_idle.gd`, `.import`, `level_check.gd`, `mesh_library.tres`, `project.godot`, `art/**` не менялись.

Решение (почему так): `root_node` — минимальная правка; треки `Idle_A` не переписываются, `.import` не трогается. Трансформация `Rig_Medium_General` (x = 1.55) оставлена как есть; `Ranger` размещён в начале `Character`. Если в T21 понадобится сместить тело, это делается на `Character`/`Ranger`.

## 3. Проверка анимации (headless)

Скрипт `E:\Temp\opencode\t19_anim.gd` (удалён). Вывод:

```
current_animation: Idle_A
is_playing: true
root_node -> /root/Level/Character/Ranger
track0 resolves: true
```

Код возврата: 0. Дополнительно (до удаления скрипта): `Character/Ranger/Rig_Medium/Skeleton3D` существует; `Character/Rig_Medium_General/Rig_Medium.visible == false`.

## 4. level_check.gd

Команда: `Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`, код возврата 0 (проверено перенаправлением в файл, без конвейера).

```
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

В выводе нет `SCRIPT ERROR`, `WARNING`, `ERROR` в области сцены. Ворота: `failed: 0`, код 0.

Проверка не подгонялась: `level_check.gd` не менялся. Она проходит, потому что `Character` по-прежнему содержит инстанс из `kaykit_animations/` (`Rig_Medium_General`). Это временно: в T22 проверка должна будет проверять `CharacterBody3D` и `FPSCamera`.

## 5. Что заметил и не стал делать

- Строка «имена костей совпадают: false» в пробе — ложная из-за порядка; по множеству совпадение полное. В будущих проверках сравнивать множества (`sort()` или `has` по каждому имени).
- Тело манекена `Rig_Medium_General` осталось в дереве сцены (скрыт только меш). Удалять его нельзя без переноса `AnimationPlayer` в другой узел; оставлено намеренно.
- Инстанс `Ranger` добавлен в `Character` с `index`-оверрайдами. Godot 4.7 загрузил сцену без предупреждений, но при ручной правке в редакторе возможна переупаковка `index` — это безвредно.
- Вне области: `character_idle.gd` всё ещё делает `get_node("Rig_Medium_General/AnimationPlayer")`; работает, но при T21 (переход `Character` на `CharacterBody3D`) проверить, что путь остаётся валидным.
- Временные файлы в `E:\Temp\opencode\` (`t19_*`) удалены.
