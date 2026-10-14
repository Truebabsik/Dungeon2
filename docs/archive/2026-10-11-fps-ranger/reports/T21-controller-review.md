# Ревью T21: контроллер, движение, мышь, виды

Ревьюер: отдельный поток, код не правился, субагенты не вызывались.
Проверено по: `docs/agents/review-checklist.md`, `briefs/T21-controller.md`, `reports/T21-controller-report.md`, `design.md` (п. 3–7), `plan.md` (T21), `game/level/character_controller.gd`, `game/level/level.tscn`, `game/level/grid_collision_builder.gd`, `game/tests/level_check.gd`, `reports/T19-ranger-idle-report.md`.

## 1. Гейт

Команда: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`

- Код возврата (проверен через `Start-Process ... -PassThru`, `ExitCode`): **0**.
- Вывод: 8 строк `ok:`, `failed: 0`. Строка `ok: Character есть, инстанс из kaykit_animations` — проверка остаётся зелёной по временному совпадению (в T22 её надо переписать, это ожидаемо).
- Исходный код `level_check.gd` не менялся (сверено с брифом T20/T21: правки в T22).

## 2. Пробa ревьюера (временная, удалена)

Файл `E:\Temp\opencode\t21_review.gd`, прогон с кодом возврата **0**. Вывод дословно:

```
type CharacterBody3D pos (66.0, 2.329956, 34.0) gpos (66.0, 2.329956, 34.0)
capsule gpos (66.0, 3.229956, 34.0) r 0.34999999403954 h 1.79999995231628
fps gpos (66.0, 3.929956, 33.85) parent Character
editor false
floor top 2.29279255867004 floor under start true
box hits within capsule 0 first []
min xz distance to box (y overlap) 2.0
yaw delta after dx=100 -0.30000001192093 expected -0.3
pitch after huge up 1.39626336097717 limit 1.39626340159546
pitch after huge down -1.39626336097717
start fps true top false
anim /root/Level/Character/Rig_Medium_General/AnimationPlayer current Idle_A playing true
after V1 fps false top true
after V2 fps true top false
```

Что это подтверждает:
- Тип `Character` = `CharacterBody3D`; `FPSCamera` — дочерний `Character`.
- Старт: вид от первого лица (`FPSCamera.current = true`, `Camera3D.current = false`).
- `V` переключает `current` в обе стороны.
- Мышь вправо: `yaw` −0.3 при dx=100 (ожидалось −0.3). Знак верный: вправо = −yaw при взгляде в −Z.
- Pitch ограничен ±80° (1.396263 рад) при огромных смещениях в обе стороны.
- `Idle_A` играет на `AnimationPlayer` внутри `Character/Rig_Medium_General` (путь найден через `find_child`).
- Стартовая точка (66, 34): ни одна коробка коллизий (стены, модули) не попадает в капсулу (0 попаданий), ближайшая коробка по XZ на расстоянии 2.0 м от центра; пол под стартом есть.

## 3. Пункты задания

| # | Пункт | Статус | Где |
|---|---|---|---|
| 1a | WASD относительно yaw тела | ADDRESSED | `character_controller.gd:29-38` (направление поворачивается на `rotation.y`) |
| 1b | Скорость 3 м/с | ADDRESSED | `character_controller.gd:3`, `:39` |
| 1c | `velocity.y = 0`, `move_and_slide()` | ADDRESSED | `character_controller.gd:39-40` |
| 1d | Мышь: yaw тела, pitch камеры | ADDRESSED | `character_controller.gd:61-63` (yaw на `self`, pitch на `fps_camera`) |
| 1e | Pitch −80…+80° | ADDRESSED | `character_controller.gd:5`, `:63` (`clampf`), проба: ±1.396263 |
| 1f | Чувствительность — константа | ADDRESSED | `character_controller.gd:4` |
| 1g | Esc → VISIBLE | ADDRESSED по коду, не проверено в headless | `character_controller.gd:55-56`, `:70-71`; см. п. 8 |
| 1h | Клик → CAPTURED | ADDRESSED по коду, не проверено в headless | `character_controller.gd:48-51`, `:66-67` |
| 1i | V переключает `current` | ADDRESSED по коду и в пробе; раскладка — см. I1 | `character_controller.gd:57-58`, `:74-80` |
| 1j | Старт — вид от первого лица | ADDRESSED | `character_controller.gd:25` (`set_fps_view(true)`), проба: `start fps true top false` |
| 1k | `Engine.is_editor_hint()` | ADDRESSED | `character_controller.gd:13-16` |
| 1l | Без лишней логики, DRY, комментарии | ADDRESSED | Комментариев нет; по правилу «where the code has none, add none» это допустимо. Дублей нет. |
| 2a | `character_idle.gd` удалён | ADDRESSED | В `game/level/` файла нет (glob); `level.tscn:17` ext_resource заменён на `16_ctrl` |
| 2b | Idle_A запускается | ADDRESSED | Проба: `current Idle_A playing true`; `character_controller.gd:19-23` |
| 2c | Путь устойчив | ADDRESSED | `character_controller.gd:19` — `find_child("AnimationPlayer", true, false)`, жёсткого пути нет. Единственный оставшийся жёсткий элемент — `level.tscn:107` `root_node = "../../Ranger"` (T19), не блокирует. |
| 3a | `Character` = `CharacterBody3D`, имя сохранено | ADDRESSED | `level.tscn:87-88` |
| 3b | Капсула r 0.35, h 1.8 | ADDRESSED | `level.tscn:41-43` (sub_resource), `:96-98`; проба: `r 0.35 h 1.8` |
| 3c | Смещение y = 0.9, не уводит под пол | ADDRESSED | `level.tscn:97`. Нижняя точка капсулы = origin = 2.33; верх пола 2.293 → капсула на 0.037 над полом. Без смещения уходила бы на 0.9 под пол — решение обосновано. |
| 3d | Визуал Ranger не сдвинулся | ADDRESSED | `level.tscn:94-95`: `Ranger` без `transform` (identity); меш центрирован на origin по отчёту T21 §3 (AABB не перепроверен ревьюером). Сдвиг 1.55 — у скрытого `Rig_Medium_General` (`level.tscn:92`), не у видимого тела. |
| 3e | `FPSCamera` дочерний `Character`, z = −0.15 | ADDRESSED по брифу, см. I2 | `level.tscn:100-101`: локально (0, 1.6, −0.15), глобально (66, 3.93, 33.85) |
| 4 | Стартовая точка не внутри стены | ADDRESSED | `level.tscn:88`: (66, 2.33, 34). Проба: 0 коробок в капсуле, ближайшая на 2.0 м, пол под стартом. Отклонение от брифа (18,18) записано в отчёте §2 и §7.2. Бриф (18,18) не совпадает с координатами сцены (клетка GridMap (16, 8)) — зафиксировать в `design.md`. |
| 5 | Модули, GridMap*, Camera3D, пользовательские узлы не изменены | ADDRESSED с оговоркой | Узлов `[node` в `level.tscn`: **51** (было 49 по T20). Разница +2: `CollisionShape3D` (`level.tscn:96`) и `FPSCamera` (`level.tscn:100`). Удаления Rig-узлов нет: `Rig_Medium_General`, `Rig_Medium`, `AnimationPlayer` на месте (`:91`, `:103`, `:106`). Camera3D `:53-59` — параметры те же (`current = true`, `size = 15.287`). Побайтного сравнения с pre-T21 нет (git нет), сравнение по числам и именам. |
| 6 | Гейт | ADDRESSED | Раздел 1: код 0, `failed: 0` |
| 7 | В `E:\Temp\opencode\` нет `t21_*` | ADDRESSED | Проверено после удаления пробы ревьюера: 0 файлов `t21*` |
| 8 | Esc и захват мыши не проверены в headless — ожидаемо | ADDRESSED (ожидаемо) | Headless `Input.mouse_mode` остаётся 0 даже после прямой установки (отчёт §6.3). Проверка — T23 в редакторе. |

## 4. Находки

Critical: 0.

Important: 2.

- I1. **`V` и `Esc` привязаны к `key.keycode` (логическая раскладка), WASD — к физическим клавишам.** `character_controller.gd:57` (`key.keycode == KEY_V`). Пользователь пишет по-русски: на русской раскладке физическая клавиша V даёт не `KEY_V`, и переключение вида не сработает. Рекомендация: `key.physical_keycode == KEY_V` (и для `KEY_ESCAPE` для единообразия с WASD). Правка одна строка. Для T23 — проверить на русской раскладке.
- I2. **`FPSCamera` (y 1.6, z −0.15) лежит внутри AABB меша Ranger.** Меш Ranger высотой ≈2.27 м, по Z [−0.514, 0.535] (по отчёту T21 §8); камера — в торсе, не у головы. Из-за отсечения задних граней (backface culling) вид от первого лица может показывать «сквозь» тело или быть перекрыт мешем. Бриф задаёт 1.6 м, поэтому это не нарушение брифа, но расхождение с реальным мешем. Решение нужно принять до T23: поднять камеру к голове (≈2.0–2.2 м) или отодвинуть вперёд, либо подтвердить, что вид устраивает. Не блокирует T21, но требует решения пользователя.

Minor (записано отдельным списком, решения фиксируются):

- M1. Капсула 1.8 м, меш 2.27 м: голова меша вне коллизии. Решение брифа, отмечено в отчёте §8. Решение: оставить, проверить в T23.
- M2. Движение WASD работает и при отпущенном курсоре (после Esc): `_physics_process` не смотрит на `mouse_mode`. Не требование спеки. Решение: оставить, отметить для T23.
- M3. `top_camera = get_parent().get_node("Camera3D")` — жёсткое имя узла уровня. Допустимо. Решение: оставить.
- M4. `game/level/node_3d.tscn` (103 байта, 09.10.2026 23:30) — не создан в T21 (дата раньше). Вне области T21. Решение: ведущему проверить, не мусор ли.
- M5. Ссылки на `character_idle.gd` в `design.md` (строки 15, 35) и в `.godot/editor/*` — документы и кэш, уже отмечено в отчёте T21 §8. Решение: обновить `design.md` ведущим при сведении.
- M6. Стартовая точка в брифе (18,18) не соответствует координатам сцены — записать в `design.md`/`plan.md` как корректировку. Решение: зафиксировать.

## 5. Итог

**assessment: С правками.** Контроллер соответствует брифу и `design.md` (п. 3–7), гейт зелёный (код 0, `failed: 0`), `Idle_A` играет через устойчивый поиск по имени, стартовая точка проверена по коллизиям. Правка I1 — одна строка; I2 требует решения пользователя (камера в торсе Ranger) до T23.

Отчёт: `F:\WORK\Dungeon2\docs\current\2026-10-11-fps-ranger\reports\T21-controller-review.md`

## 6. Что проверено и не проверено

- Проверено в headless: тип, капсула, FPSCamera, стартовый вид, `V`, поворот мышью, pitch-клэмп, `Idle_A`, стартовая точка по коллизиям, гейт (код и вывод).
- Не проверено: Esc, клик, режим курсора (headless не отражает), визуальная высота камеры относительно меша, AABB меша Ranger (взят из отчёта T21, не перепроверен), побайтная неизменность узлов.
