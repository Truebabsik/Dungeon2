# Ревью T10: окружение и цвет

Ревьюер: субагент (только проверка, правок не вносил).
Бриф: `briefs/T10-environment-color.md`. Отчёт исполнителя: `reports/T10-environment-report.md`. Диф: `game/level/level.tscn`.

## 1. Значения Environment и WorldEnvironment — ADDRESSED

`game/level/level.tscn:5-12` (sub_resource `Environment`):
- `background_mode = 1` — ок (стр. 6).
- `background_color = Color(0.1, 0.06, 0.18, 1)` — ок (стр. 7).
- `ambient_light_source = 2` — ок (стр. 8).
- `ambient_light_color = Color(0.42, 0.34, 0.5, 1)` — ок (стр. 9).
- `ambient_light_energy = 0.8` — ок (стр. 10).
- `tonemap_mode = 2` — **отличается от брифа (`3`)**, см. пункт 7. Решение исполнителя обосновано.
- `tonemap_exposure = 1.0` — ок (стр. 12).
- `game/level/level.tscn:30-31` — `[node name="WorldEnvironment" type="WorldEnvironment" parent="."]`, `environment = SubResource("Environment_level")`. Узел дочерний `Level`, после `Camera3D`, как в брифе.
- `load_steps=3` (стр. 1): ext_resource ×1 + sub_resource ×1 + 1 = 3. Корректно.

## 2. DirectionalLight3D — ADDRESSED

`game/level/level.tscn:17-21`:
- `light_color = Color(1, 0.89, 0.72, 1)` — ок (стр. 18).
- `light_energy = 1.2` — ок (стр. 19).
- `shadow_enabled = true` — ок (стр. 20).
- `rotation_degrees = Vector3(-50, -30, 0)` — не менялся (стр. 21).

## 3. Camera3D не изменена относительно T9 — ADDRESSED

`game/level/level.tscn:23-28`: `position = (58.87, 40, 46.87)`, `rotation_degrees = (-45, 45, 0)`, `projection = 1`, `size = 48.5`, `current = true`. Совпадает со значениями T9 (`reports/T9-camera-pitch-report.md`, стр. 6–8). Порядок свойств переставлен, значения те же.

## 4. Другие файлы не менялись — ADDRESSED

Проверка по mtime (`Get-ChildItem`): после старта T10 (бриф 18:55:14) изменились только `level.tscn` (18:55:36), `T10-environment-report.md` (18:55:59), `T10-scene-screenshot.png` (18:55:44). Последние изменения прочих файлов: `level_map.gd` 17:51:53 (T7), `level_builder.gd` 18:01:08 (T8). `level_check.gd`, `project.godot` старше 17:21 — не менялись. Полного диффа без git нет, вывод по mtime.

## 5. Гейт — ADDRESSED

Команда: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --script res://tests/level_check.gd`
Вывод:
```
ok: карта не пуста, записей 285
ok: все kind имеют .gltf
ok: все rot валидны
ok: модулей 285 = записей карты
ok: повторный build() даёт 285 модулей
failed: 0
```
Код возврата: `0`. Счёт `285` совпадает с отчётом. Проверка 4 не посчитала `WorldEnvironment` (узел `Node`, не `Node3D`), как и ожидалось брифом.

## 6. Скриншот и оценка — ADDRESSED (оценка в целом честная, с одной неточностью)

Файл `reports/T10-scene-screenshot.png` (1152×648) открыт и сверен с `art/reference/reference.png` (1920×1080).
- **Фон:** в скриншоте плоский тёмно-фиолетовый, градиента нет. Отчёт (стр. 44) это указывает верно.
- **Пол:** в скриншоте насыщенный песочно-оранжевый. У референса пол светлее и серее. Отчёт (стр. 45) верен.
- **Тени:** в скриншоте мягкие, фиолетовые. У референса резче и контрастнее. Отчёт (стр. 46) верен.
- **Свет:** отчёт (стр. 47) пишет «совпадает по тону». Стены в скриншоте уходят в сине-фиолетовый, у референса серые и нейтральные. Отчёт сам это признаёт в той же строке, поэтому формулировка «совпадает» для света слегка завышена; корректнее «тёплый свет совпадает, стены — нет».
- Итог «средняя, не полная близость» (стр. 49) — адекватен.

## 7. tonemap_mode: Filmic = 2 — ADDRESSED

Проверено по официальной документации Godot 4.7 (class Environment, enum ToneMapper): `TONE_MAPPER_LINEAR=0`, `TONE_MAPPER_REINHARDT=1`, `TONE_MAPPER_FILMIC=2`, `TONE_MAPPER_ACES=3`, `TONE_MAPPER_AGX=4`. Значение `2` — Filmic. Бриф ошибочно указал `3 (Filmic)`, это ACES. Исполнитель отклонился от брифа правильно и задокументировал (отчёт стр. 53). Для ledger: в брифе ошибка, а не в исполнении.

## 8. Временные пробы — ADDRESSED

`E:\Temp\opencode\`: содержит только `t1_err.txt`, `t1_import_rerun.txt`, `t1_out.txt` (T1). Файлов `t10_*` нет. Временный скрипт захвата и проба тонмэппинга удалены.

## Находки

- **Critical 0.**
- **Important 0.**
- **Minor 1:** в отчёте стр. 47 «Свет — совпадает по тону» противоречит собственному описанию стен в той же строке. Переформулировать или оставить с пометкой в ledger.
- **Minor 2:** в брифе `tonemap_mode = 3 (Filmic)` — фактическая ошибка (3 это ACES). Записать в ledger, чтобы не повторялась в следующих брифах.
- **Minor 3:** бриф требовал «гейт = три команды» в ревью-формате, у проекта одна команда (`level_check.gd`). Это не дефект, отмечаю только для ledger.

## Assessment

**Да.** Все пункты брифа выполнены, гейт зелёный (`failed: 0`, код `0`), отклонение `tonemap_mode` от брифа корректно и задокументировано. Два Minor касаются формулировок и брифа, на код не влияют.

Отчёт: `F:\WORK\Dungeon2\docs\current\2026-10-09-level-demo\reports\T10-environment-review.md`
