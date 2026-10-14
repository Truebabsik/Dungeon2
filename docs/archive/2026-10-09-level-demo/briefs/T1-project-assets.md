# Бриф: Задача 1 — проект Godot и ассеты

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`. Этот файл — только специфика задачи.
Коммит не делать. Субагентов не вызывай.

## Где это в проекте

Этап — демо-уровень в Godot 4.7. Это первая задача: создаём проект `game/` и копируем используемые ассеты.
Спецификация: `docs/current/2026-10-09-level-demo/design.md`. План: `docs/current/2026-10-09-level-demo/plan.md`, раздел «Задача 1».
Оригинал пака `art/KayKit_Dungeon_Pack_1.1_FREE/` не меняем.

## Что сделать

1. Создать `game/project.godot`: версия Godot 4.7, `config/name="Dungeon2"`, главная сцена `res://level/level.tscn`.
   Сцены ещё нет, это ожидаемо (появится в задаче 3). Файл `project.godot` должен быть валидным для Godot 4.7.
2. Скопировать в `game/assets/kaykit/` из `art/KayKit_Dungeon_Pack_1.1_FREE/Assets/gltf/` **точно** такие файлы:
   `floor_tile_large.gltf`, `wall.gltf`, `wall_corner.gltf`, `wall_doorway.gltf`, `wall_archedwindow_open.gltf`,
   `stairs.gltf`, `pillar.gltf`, `table_medium.gltf`, `chair.gltf`, `barrel_large.gltf`, `bed_frame.gltf`,
   `chest.gltf`, `shelves.gltf`, `coin_stack_small.gltf`, `torch_mounted.gltf`, `banner_patternA_red.gltf`.
   Также скопировать `License.txt` из корня пака.
3. Для каждого скопированного `.gltf` открыть файл, найти все поля `"uri"` в JSON, скопировать на эти относительные
   пути все внешние `.bin` и текстуры. Внешние ресурсы, которые не нашлись на диске, — ошибка: отчитаться.
4. Пути в `game/assets/kaykit/` сохранить как в паке (относительные `uri` должны остаться рабочими).

## Область

**Можно править:** `game/project.godot`, `game/assets/kaykit/**`, `docs/current/2026-10-09-level-demo/reports/T1-project-assets-report.md`.
**Не трогать:** всё в `art/**`, `docs/**` кроме отчёта, `skills/**`.

## Доказательство

Проба: `Godot_v4.7.2-stable_win64.exe --headless --path F:\WORK\Dungeon2\game --import`.
Ожидаемо: код возврата `0`. Текст в stderr вердиктом не является: зафиксировать его в отчёте дословно, но решать по коду.

Дополнительно: проверка, что число файлов `.gltf` в `game/assets/kaykit/` равно 16, и что для каждого `uri` из JSON
существует файл рядом. Числа записать в отчёт.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T1-project-assets-report.md`.
Содержание: список скопированных файлов, список внешних ресурсов по каждому `.gltf`, дословный вывод пробы
с кодом возврата, решения вопреки брифу (если были).

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`),
изменённые файлы, одну строку про прогон (код возврата `--import` и числа проверок), открытые вопросы.
