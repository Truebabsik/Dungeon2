# Бриф: Задача 14 — манекен на сцене с анимацией idle

Ты — исполнитель. Читай **сначала** `docs/agents/constraints.md`. Этот файл — только специфика задачи.
Коммит не делать. Субагентов не вызывай.

## Где это в проекте

Уровень — редактируемая сцена `game/level/level.tscn` (корень `Level`, модули — дети `Level`, узел `Prototypes` в `x = -40`).
Ассеты анимаций и манекенов лежат в `game/assets/kaykit_animations/`:
- `characters/Mannequin_Medium.glb`, `characters/Mannequin_Large.glb` — модели персонажа;
- `animations/Rig_Medium/Rig_Medium_*.glb` (8 шт.), `animations/Rig_Large/Rig_Large_*.glb` (6 шт.) — анимации.

## Что сделать

1. **Выяснить, как устроены файлы.** Временный headless-скрипт в `E:\Temp\opencode\t14_probe.gd` (`extends SceneTree`), который
   загружает `Mannequin_Medium.glb` и `Rig_Medium_General.glb` через `load`, инстансирует и выводит: есть ли у них меш
   (`MeshInstance3D`), есть ли `AnimationPlayer`, и полный список имён анимаций (`get_animation_list()`).
   Выбрать имя idle-анимации из списка (ожидается что-то вроде `Idle_A` в `Rig_Medium_General`). Если idle нет ни в одном
   файле — `NEEDS_CONTEXT` с перечнем анимаций. Скрипт удалить после прогона.
2. **Добавить персонажа в `game/level/level.tscn`.** Узел `Character` (`Node3D`), дочерний корня сцены (как `Prototypes`),
   не внутри `Level`. Внутри — инстанс `Mannequin_Medium.glb` (или `Large`, выбрать `Medium`, записать в отчёт).
   Позиция: центр клетки внутри большой комнаты пола, свободной от мебели и стен, в мировых координатах `y = 0`.
   Выбрать клетку по `level.tscn`: позиции узлов `floor_tile_large` дают полы; проверить, что на клетке нет другого
   модуля (сравнить позиции). Координаты и обоснование — в отчёт.
3. **Анимация idle.** Чтобы анимация проигрывалась, нужен `AnimationPlayer`, у которого в библиотеке есть idle-анимация
   из `Rig_*_General.glb` (способ — по результатам пробы п. 1: либо инстанс `Rig_*` с его собственным `AnimationPlayer`
   и скелетом, совместимым с манекеном, либо анимация, импортированная в библиотеку). Выбрать вариант, который работает
   с тем же скелетом, что манекен; записать, какой выбран и почему. Установить автозапуск idle (`autoplay` = имя анимации)
   и зацикливание (loop mode по умолчанию для idle — проверить).
4. **Проверка.** Временный скрипт `E:\Temp\opencode\t14_check.gd`: загрузить `res://level/level.tscn`, добавить в дерево,
   дождаться 2 кадров (`await process_frame` дважды), проверить: узел `Character` есть; внутри есть `AnimationPlayer`;
   `current_animation` или `autoplay` равен idle-имени; `is_playing()` истинно после кадров. Вывод `failed: N`.
   Скрипт удалить.
   Затем `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd` —
   ожидаемо `failed: 0`, код `0`. Если краснеет из-за нового узла — записать причину; не править проверку ради зелёного.
5. **Скриншот.** `E:\Temp\opencode\t14_capture.gd` (с окном, `--resolution 1152x648`, как в T13), файл
   `docs/current/2026-10-09-level-demo/reports/T14-character-screenshot.png`. Скрипт удалить. Посмотреть через `read`:
   персонаж виден в кадре, стоит внутри комнаты. Если не виден — записать.

## Область

**Можно править:** `game/level/level.tscn` (добавить узел `Character` и его детей; больше ничего),
`docs/current/2026-10-09-level-demo/reports/T14-character-report.md`,
`docs/current/2026-10-09-level-demo/reports/T14-character-screenshot.png`.
**Не трогать:** `game/tests/**`, `game/assets/**`, `art/**`, остальные `docs/**` кроме отчёта и скриншота.

## Отчёт

Файл: `docs/current/2026-10-09-level-demo/reports/T14-character-report.md`.
Содержание: результаты пробы (что внутри glb, список анимаций), выбранные файлы и способ подключения idle, позиция
персонажа с обоснованием, дословные выводы проверок, оценка скриншота.

**В ответ вернуть только:** статус (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`), изменённые файлы,
одну строку про прогон (имя idle, `is_playing`, `failed`, код, позиция), открытые вопросы.
