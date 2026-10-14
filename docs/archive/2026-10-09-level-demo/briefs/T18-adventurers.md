# Бриф: Задача 18 — ресурсы из KayKit_Adventurers_2.0_FREE

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`, затем `docs/agents/report-contract.md`.
Коммит не делать. Субагентов не вызывай.

## Источник

Архив `art/KayKit_Adventurers_2.0_FREE.zip` распаковать во временную папку `E:\Temp\opencode\adventurers\`
(уже распакован; при необходимости распаковать заново). В `art/` ничего не менять.
Внутри: `KayKit_Adventurers_2.0_FREE\`:
- `Assets\gltf\` — 31 статичная модель `.gltf` + `.bin` (оружие, щиты, инвентарь), текстуры `*_texture.png` (5 шт.);
- `Assets\obj\` — 31 `.obj` (дубликаты gltf, **не брать**);
- `Assets\fbx\`, `Assets\fbx(unity)\` — **не брать**;
- `Characters\gltf\` — 6 персонажей `.glb` (`Barbarian`, `Knight`, `Mage`, `Ranger`, `Rogue`, `Rogue_Hooded`) и 5 текстур `*_texture.png`;
- `Animations\gltf\Rig_Medium\` — `Rig_Medium_General.glb` (**уже есть** в проекте, побайтно совпадает: не копировать) и `Rig_Medium_MovementBasic.glb` (**новый**);
- `Characters\fbx`, `Animations\fbx`, `Samples\`, `*.png` превью, `*.url` — **не брать**;
- `License.txt` — взять, если есть.

## Что сделать

1. **Статичные модели.** Скопировать `Assets\gltf\*.gltf`, `*.bin` и 5 текстур `*_texture.png` в
   `game/assets/kaykit_adventurers/` (папка новая). Импорт: `--import`.
2. **Персонажи.** Скопировать `Characters\gltf\*.glb` и текстуры персонажей в `game/assets/kaykit_adventurers/characters/`.
   Не ставить их на сцену.
3. **Анимация.** Скопировать `Rig_Medium_MovementBasic.glb` в `game/assets/kaykit_animations/animations/Rig_Medium/`.
   Файл `Rig_Medium_General.glb` не трогать. `License.txt` положить в `game/assets/kaykit_adventurers/`.
4. **MeshLibrary.** Пересобрать `game/assets/mesh_library.tres` из всех наборов: прежние 377 элементов
   (211 kaykit + 90 obj + 76 resourcebits) плюс 31 новый из `kaykit_adventurers`. Ожидаемо **408**.
   Способ сборки и имена — как в T16/T17 (имя = имя файла без расширения). Если имя совпадает с уже существующим элементом,
   взять префикс `adv_` для нового и записать в отчёт. Одна ошибка на файле не глушится, записывается в отчёт.
   Сохранить через `ResourceSaver`, скрипт `E:\Temp\opencode\t18_build_lib.gd`, удалить после прогона.
   Uid в заголовке `mesh_library.tres` должен остаться прежним (`uid://cm7fsg1yj5qfl`), иначе `level.tscn` потеряет ссылку.
5. **Проверка.** `game/tests/level_check.gd`: число элементов библиотеки 377 → 408 (по составу на диске: сверь
   число `.gltf` в трёх папках kaykit, kaykit_resourcebits и kaykit_adventurers). Не ослаблять проверки, остальное не трогать.
   Прогон: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`
   — `failed: 0`, код 0.
6. **Не трогать:** `game/level/level.tscn` (сцена сейчас в пользовательской структуре: `GridMapWall`, `GridMapFloor`, `GridUpper`),
   камеру, свет, среду, `Character`, `project.godot`, `art/**`.
7. Проверить, что в `E:\Temp\opencode\` не осталось `t18_*` скриптов.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T18-adventurers-report.md`.
Содержание: что скопировано (число файлов по папкам), что пропущено и почему, число элементов библиотеки по наборам,
размер `mesh_library.tres`, конфликты имён, ошибки по файлам, дословные выводы `--import` и проверки.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые и созданные файлы,
одну строку: число элементов библиотеки, `failed`, код `--import`, код проверки, открытые вопросы.
