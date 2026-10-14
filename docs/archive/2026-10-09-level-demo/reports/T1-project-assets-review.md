# Ревью T1 — проект Godot и ассеты

Ревьюер: субагент (только проверка, ничего не правлено). Бриф: `briefs/T1-project-assets.md`. Отчёт: `reports/T1-project-assets-report.md`.

## Гейт (проба)

Команда: `F:\WORK\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe --headless --path F:\WORK\Dungeon2\game --import`
(путь из брифа — каталог; исполняемый файл внутри, тот же релиз 4.7.2).

- Код возврата: **0**.
- stderr (дословно, значимое): `ERROR: Cannot open file 'res://level/level.tscn'.` / `at: load (scene/resources/resource_format_text.cpp:1442)` / `ERROR: Failed loading resource: res://level/level.tscn.` / `at: _load (core/io/resource_loader.cpp:317)`. Ожидаемо: `run/main_scene` указывает на сцену задачи 3. По брифу вердикт — код 0.
- Счёт `[ DONE ] import` не воспроизведён (ANSI-коды в stdout мешают grep), поэтому опираюсь на код возврата и на число `*.import` на диске (17).
- Временные файлы пробы (`E:\Temp\opencode\T1-review-*`) удалены.

## Пункты брифа

1. `game/project.godot` — **ADDRESSED.** `game/project.godot:9` `config_version=5`; `:13` `config/name="Dungeon2"`; `:14` `config/features=PackedStringArray("4.7", "Forward Plus")`; `:15` `run/main_scene="res://level/level.tscn"`. Файл валиден (проба открыла проект без ошибок разбора).
2. Ровно 16 `.gltf` + `License.txt` — **ADDRESSED.** Сравнение `Compare-Object` со списком из брифа: расхождений 0, `.gltf` = 16, `License.txt` есть (`game/assets/kaykit/License.txt`). Дополнительно есть `dungeon_texture.png` (не в списке брифа, но требуется `uri`, это по брифу п.3, допустимо).
3. Все внешние `uri` существуют рядом — **ADDRESSED.** Проверка сам: через `ConvertFrom-Json` по всем 16 файлам, `buffers` и `images`: 32 `uri`, все `exists=True`. Все буферы свои (`<name>.bin`), все текстуры `dungeon_texture.png`.
4. `art/**` не изменён — **ADDRESSED.** В `art/` нет `*.import`, `*.godot`, `*.uid` (0). Самые свежие mtime в пакете — 16.07.2026 (`License.txt`, `Samples/*.png`), то есть ничего не менялось сегодня. Побайтовое сравнение с исходным паком не делал (эталона нет), вывод по mtime.
5. Проба `--import` код 0 — **ADDRESSED** (см. гейт).

Вопрос «`game/.godot/` — нужен ли `.gitignore`» и вопрос про `_console.exe` — см. ниже.

## Находки

- **Critical 0**
- **Important 1:** `reports/T1-project-assets-report.md:91-92` утверждает, что Godot «Файлы `.import` рядом с `.gltf` … не создал». Это неверно: в `game/assets/kaykit/` 17 файлов `*.gltf.import` и `dungeon_texture.png.import`, все с mtime 2026-10-09 17:07:30 (момент пробы). Из-за этого «Всего файлов в каталоге: 34» (`report.md:23`) тоже неверно: фактически 34 + 17 = 51. Код не сломан; исправить абзац и счёт в отчёте.
- **Minor 1:** `reports/T1-project-assets-report.md:76` — строка `[ DONE ] import` приведена в ответе, но в отчёте она усечена (`...`); счёт DONE не подтверждён. Не блокирует.
- **Minor 2:** отчёт (`:109-111`) советует поправить путь в брифах на `..._console.exe`; это верно, но сам путь из брифа (`F:\WORK\Godot_v4.7.2-stable_win64.exe`) в `constraints.md`/шаблонах тоже надо заменить, иначе следующий исполнитель повторит ту же развилку.

## Ответы на вопросы исполнителя

- **`_console.exe` той же версии 4.7.2 — допустимо.** Оба файла лежат в одном релизе (`Godot_v4.7.2-stable_win64.exe` и `..._console.exe`, одна сборка). Консольный вариант нужен для захвата stdout/stderr и кода возврата; GUI-вариант для headless-пробы не нужен. Рекомендую в брифах и `constraints.md` прямо указывать путь к `_console.exe`.
- **`game/.gitignore` с `.godot/` — рекомендую добавить.** `game/.godot/` — кэш движка и редактора, его не коммитим. Файлы `*.gltf.import` коммитить **нужно**: Godot 4 хранит в них настройки импорта и uid ресурса, без них импорт и ссылки на ресурсы поедут. Строку `.godot/` в `game/.gitignore` можно добавить отдельным коротким шагом (сейчас файла нет: `Test-Path` вернул False). Это не входит в «Можно править» брифа T1, поэтому решение за ведущим.

## Assessment

**С правками.** Проект, список ассетов, `uri`, `art/` и код возврата пробы соответствуют брифу и проверены на диске. Одна существенная неточность в отчёте (`.import` и счёт 34 vs 51) — исправить текст отчёта; код исполнителя править не нужно.

отчёт: F:\WORK\Dungeon2\docs\current\2026-10-09-level-demo\reports\T1-project-assets-review.md
