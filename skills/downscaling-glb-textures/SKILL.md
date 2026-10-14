---
name: downscaling-glb-textures
description: Use when a raw .glb model is too large to ship — big file (20–50 МБ), oversized textures (2048/4096), heavy Godot import — and needs compacting into a game-ready asset without changing geometry. Typical for Hunyuan3D outputs and other high-res model exports.
---

# Downscaling glb Textures

## Overview

Компактный glb = даунскейл **только текстур** до max-стороны 1024 px. Геометрия не трогается (никакого
декимейта, пересчёта нормалей) — поэтому треугольники до/после обязаны совпасть, скрипт это печатает и
сверяет. Проверено: арка 26.5 → 3.77 МиБ, статуя 42 → 5.1 МиБ при неизменных ~50 000 тр.

Типичный выигрыш — 6–10× по весу при потере качества, незаметной на игривой дистанции.

## Когда использовать

- Сырой glb из Hunyuan3D / блендера весит 20–50 МБ, текстуры 2048/4096.
- Godot импортирует модель тяжело, `game/assets/` раздувается.
- Нужен проп для сцены (пропсы `_1024` в `game/assets/props/` — это ровно такой пайплайн).

**Когда НЕ использовать:** если геометрия перегружена треугольниками (не текстурой) — даунскейл не поможет,
нужен декимейт (отдельный, более рискованный шаг: ломает UV/нормали, здесь его нет).

## Быстрый старт

Скрипт: `game/tools/glb_texture_downscale.py`. Аргументы скрипта идут **после `--`**:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python game/tools/glb_texture_downscale.py -- `
    [--max 1024] [--out-dir DIR] [--suffix _1024] [--out FILE.glb] вх1.glb [вх2.glb ...]
```

| Параметр | Дефолт | Что делает |
|---|---|---|
| `вх1.glb ...` | — | исходники (только чтение); можно пакетно несколько |
| `--max` | `1024` | целевая max-сторона текстуры |
| `--out-dir` | папка исходника | папка итогов |
| `--suffix` | `_1024` | суффикс имени итога (`<stem><suffix>.glb`) |
| `--out` | — | итоговый файл явно (только при одном входе) |

Код возврата: `0` успех, `1` были ошибки (в т.ч. изменилась геометрия), `2` невалидные аргументы.

## Пайплайн (прогон + проверка)

Путь к Godot 4.7.2 — **относительно корня проекта** (каталог `Godot/` локальный, в git не входит):
`Godot\Godot_v4.7.2-stable_win64_console.exe`. Все команды ниже запускать из корня проекта.

1. **Сжать.** Вызов выше на исходниках из `art/models/`. По умолчанию итог — рядом с исходником
   (`<stem><suffix>.glb`); при `--out-dir`/`--out` — в указанную папку/файл (см. таблицу параметров).
2. **Сверить stdout.** Ключевые строки: `TRIS (glb bytes before)` == `TRIS (glb bytes after)` (иначе скрипт
   сам печатает `ERROR: тр. до != после`), `SIZE before/after`, `SCALED COUNT`, `DONE: OK`, код 0.
3. **Проверить в Godot.** В `E:\Temp\opencode\<name>_check\` скопировать итоговый glb + `project.godot`
   (минимальный, `config/name=...`), **а также `check_glb.gd`** (иначе `res://check_glb.gd` не найдётся —
   `res://` указывает на папку `--path`), удалить `.godot`. Прогнать `--import` (код 0), затем канонический
   проверочный скрипт `check_glb.gd` (источник — рядом с этим SKILL.md; устойчив к headless-зависанию через watchdog):

   ```powershell
   # запускать из корня проекта
   $G = Join-Path $PWD 'Godot\Godot_v4.7.2-stable_win64_console.exe'
   & $G --headless --path E:\Temp\opencode\<name>_check --import
   & $G --headless --path E:\Temp\opencode\<name>_check --script res://check_glb.gd -- res://<model>.glb
   ```

   Канонический скрипт `check_glb.gd` (рядом с этим SKILL.md) устойчив к headless-специфике: тр. считает
   через `surface_get_arrays`, а не `calc_loop_triangles` (тот виснет), работает в первом `_process`, без
   `await`/`Timer` (дедлок). Ожидаемо: `MESHES`/`TRIANGLES` совпадают с исходником, `AABB` (пол на Y=0),
   все слоты `TEX ...: 1024x1024`, `RESULT: OK`, код 0. Корневой поворот +90° по X скрипт учитывает сам
   (в glTF меш лежит «по Z», в Godot высота — по Y).
4. **Убрать temp.** Папку `E:\Temp\opencode\<name>_check\` удалить после проверки.

## Рабочие ассеты

Готовый `_1024.glb` кладётся в `game/assets/props/` (там Godot создаёт `.import` и PNG); исходник в
`art/models/` не трогается. `art/**` Godot не импортирует автоматически. Паки в `art/` не редактировать.

## Типичные ошибки

| Ошибка | Причина / лечение |
|---|---|
| `тр. до != после` | Геометрия изменилась — не даунскейл это. Проверить, не запущен ли декимейт/ручные правки. |
| Headless Godot виснет навсегда | Причина — `calc_loop_triangles()` на импортированном glb виснет, либо `await process_frame` в наследнике `SceneTree` даёт дедлок (цикл ждёт сам себя). Обход/замер — в первом `_process`, тр. через `surface_get_arrays`. Timer-watchdog НЕ спасает (таймеру нужны кадры). Канонический `check_glb.gd` уже делает это правильно. |
| `!is_inside_tree()` при замере | `global_transform`/`get_aabb` брать до `add_child`/первого кадра. Добавляй узел в дерево в `_initialize`, а меряй в первом `_process` (не через `await` — это дедлок). |
| `print` в `_initialize` не виден | stdout буферизуется и теряется при раннем `quit()`. Печатай в первом `_process` перед `quit`. Ошибки (parse/runtime) при этом уходят в stderr и видны. |
| PowerShell `> file.log` нечитаем | `>` пишет UTF-16. Использовать `Out-File -Encoding utf8`. `Tee-Object` в PS 5.1 параметра `-Encoding` не имеет — не писать его туда. |
| `var arr := surface_get_arrays(...)` | GDScript не выводит тип → Parse Error. Объявлять `var arr: Array = ...`. |
| Итог тот же вес | Текстуры уже ≤ `--max` — сжимать нечего, `SCALED COUNT: 0`. |
| `--out` с несколькими входами | Невалидно (код 2): `--out` только при одном входном файле. |
