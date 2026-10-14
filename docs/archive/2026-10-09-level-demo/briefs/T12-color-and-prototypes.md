# Бриф: Задача 12 — цвет по ref3 и вынос прототипов из кадра

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`. Этот файл — только специфика задачи.
Коммит не делать. Субагентов не вызывай.

## Где это в проекте

Задача 11 переписала `game/level/level.tscn` в редактируемую сцену (285 инстансов модулей в `Level`, узел `Prototypes`
с 14 прототипами). Ревью T11 дало «С правками»: прототип `barrel_large` попадает в кадр камеры.
Пользователь дал эталон цвета и вида: `art/reference/ref3.png` (серый камень стен, светло-серый пол, без фиолетового). Текущие
фиолетовые стены и фон из T10 признаны неверными.

## Что сделать

1. **Прототипы.** У узла `Prototypes` в `game/level/level.tscn` установить `position = Vector3(-40, 0, 0)`.
   Остальное в `Prototypes` не менять. Проверить по расчёту, что все прототипы вне кадра камеры (`Camera3D`:
   `position (58.87, 40, 46.87)`, `rotation_degrees (-45, 45, 0)`, `size 48.5`).
2. **Цвет** (`WorldEnvironment`, `Environment`, `DirectionalLight3D` в `level.tscn`):
   - `Environment.ambient_light_color` — нейтральный серый, без фиолетового; `ambient_light_energy` подобрать так, чтобы
     тени не были чёрными. Ориентир: `ref3.png`, тени пола светло-серые.
   - `Environment.background_color` — светлый нейтральный серо-белый фон, близкий к белому фону `ref3.png`
     (если в `ref3` фон белый, использовать близкий к нему). Тёмный фиолетовый убрать.
   - `Environment.tonemap_mode` оставить `2` (Filmic); `tonemap_exposure` подобрать, не выше `1.2`.
   - `DirectionalLight3D.light_color`: тёплый, но умеренный (не сильнее текущего `(1, 0.89, 0.72)`). `light_energy` не выше `1.2`.
     `rotation_degrees` не менять.
   - Не менять узлы модулей, `Camera3D`, `Level`, `Prototypes` (кроме позиции из п. 1).
3. **Проверка.** `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`.
   Ожидаемо `failed: 0`, код `0`.
4. **Скриншот.** Скрипт `E:\Temp\opencode\t12_capture.gd` (как в T10: с окном, `--resolution 1152x648`), файл
   `docs/current/2026-10-09-level-demo/reports/T12-scene-screenshot.png`. Скрипт удалить после прогона.
5. **Сверка.** Открыть скриншот и `art/reference/ref3.png` через `read`. По пунктам записать: фон, стены, пол, тени, свет, тёплые
   предметы. Что совпало, что нет. Не завышать оценку. Отдельно: прототипы в кадре — да/нет.

## Область

**Можно править:** `game/level/level.tscn` (только `Prototypes.position`, `Environment`, `DirectionalLight3D`
`light_color`/`light_energy`), `docs/current/2026-10-09-level-demo/reports/T12-color-report.md`,
`docs/current/2026-10-09-level-demo/reports/T12-scene-screenshot.png`.
**Не трогать:** всё остальное в `game/`, `art/**`, `docs/**` кроме отчёта и скриншота.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T12-color-report.md`.
Содержание: дословные новые значения (`Environment`, свет, позиция `Prototypes`), расчёт, что прототипы вне кадра,
дословный вывод проверки, оценка скриншота по пунктам с `ref3`, решения вопреки брифу.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые файлы,
одну строку про прогон (`failed`, код, прототипы в кадре да/нет), открытые вопросы.
