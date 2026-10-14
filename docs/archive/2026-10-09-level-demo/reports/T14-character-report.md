# T14 — манекен на сцене с анимацией idle: отчёт

## 1. Проба файлов (`E:\Temp\opencode\t14_probe.gd`, удалён)

Вывод пробы (дословно, без служебного шума Godot):

```
== res://assets/kaykit_animations/characters/Mannequin_Medium.glb загружен: true
MeshInstance3D: 6 [Mannequin_Medium_ArmLeft, Mannequin_Medium_ArmRight, Mannequin_Medium_Body, Mannequin_Medium_Head, Mannequin_Medium_LegLeft, Mannequin_Medium_LegRight]
Skeleton3D: 1
  bones 21: [root, hips, upperleg.l, lowerleg.l, foot.l, toes.l, spine, chest, upperarm.r, lowerarm.r, wrist.r, hand.r, head, upperarm.l, lowerarm.l, wrist.l, hand.l, upperleg.r, lowerleg.r, foot.r, toes.r]
AnimationPlayer: 0
== res://assets/kaykit_animations/animations/Rig_Medium/Rig_Medium_General.glb загружен: true
MeshInstance3D: 6 [Mannequin_ArmLeft, Mannequin_ArmRight, Mannequin_Body, Mannequin_Head, Mannequin_LegLeft, Mannequin_LegRight]
Skeleton3D: 1
  bones 23: [root, hips, upperleg.l, lowerleg.l, foot.l, toes.l, spine, chest, head, upperarm.l, lowerarm.l, wrist.l, hand.l, handslot.l, upperarm.r, lowerarm.r, wrist.r, hand.r, handslot.r, upperleg.r, lowerleg.r, foot.r, toes.r]
AnimationPlayer: 1
  root_node .., list [Death_A, Death_A_Pose, Death_B, Death_B_Pose, Hit_A, Hit_B, Idle_A, Idle_B, Interact, PickUp, Spawn_Air, Spawn_Ground, T-Pose, Throw, Use_Item]
  Idle_A loop_mode 0 length 1.0666667 tracks 54
    track 0 path Rig_Medium/Skeleton3D:hips
```

Выводы:
- `Mannequin_Medium.glb` содержит меш и скелет (21 кость), но **не содержит** `AnimationPlayer`.
- `Rig_Medium_General.glb` содержит меш (те же 6 частей, имена `Mannequin_*`), скелет (23 кости) и `AnimationPlayer` с 15 анимациями, включая `Idle_A` (длина 1.067 с).
- Набор костей манекена (21) — подмножество костей рига (23): рига добавляет `handslot.l` и `handslot.r`. Скелеты совместимы по именам.
- `Idle_A` импортирована с `loop_mode = 0` (LOOP_NONE). См. раздел 4.

## 2. Что изменено

Файл: `game/level/level.tscn`.
- строка 16: новый `ext_resource` `15_rmg` → `animations/Rig_Medium/Rig_Medium_General.glb`;
- в конце файла: узел `Character` (`Node3D`, дочерний корня `Level`, рядом с `Prototypes`), `transform` с позицией `(18, 0, 18)`;
- внутри `Character`: инстанс `Rig_Medium_General.glb` (имя узла `Rig_Medium_General`);
- override у `Character/Rig_Medium_General/AnimationPlayer`: `autoplay = "Idle_A"`.
  В прогоне (см. раздел 3) `autoplay` и `current_animation` равны `Idle_A`; сам узел в tscn записан с `index="1"` — это не проверено отдельно, парсер принял файл, и прогон прошёл.

## 3. Решения и отклонения от брифа

**3.1. Инстанс `Mannequin_Medium.glb` не добавлен, вместо него — `Rig_Medium_General.glb`.**
Бриф (п. 2) просит внутри `Character` инстанс `Mannequin_Medium.glb`, а (п. 3) допускает инстанс `Rig_*` с его собственным `AnimationPlayer`. Оба одновременно не сработают: `Rig_Medium_General.glb` уже содержит меш манекена, и два инстанса дали бы два наложенных тела. `AnimationPlayer` у манекена нет, а добавить туда анимацию без `AnimationLibrary`-ресурса вне `level.tscn` нельзя. Поэтому взят рига: одно тело, тот же скелет (подмножество костей), собственный плеер с `Idle_A`. Причина выбора видна в разделе 1.

**3.2. Позиция.** Клетка `(18, 18)`. Пол `floor_tile_large_027` (18, 0, 18) есть. Мебели в клетке нет: мебель на `z = 18` стоит в `x = 6` (table_002), `10` (chair_002), `22` (table_003). Стены: вертикальные двери на `x = 12` и `x = 16` (`wall_doorway_004/005`), стена на `x = 28`, горизонтальных стен на `z = 18` нет. Клетка лежит в восточной части комнаты `x ∈ [16, 28]`, `z ∈ [14, 24]`, где свободны и `(18, 14)`, `(18, 22)`, `(26, 18)`. Рядом (справа) стоит `table_medium_003` в `(22, 18)`, оставлено как есть.

**3.3. Loop.** Не решено в рамках брифа — см. раздел 4.

## 4. Открытые проблемы

**4.1. Зацикливание не настроено (loop_mode = 0).** `Idle_A` в импорте `Rig_Medium_General.glb` без loop. Значит, после 1.067 с idle остановится на последней позе. Проверка `is_playing()` через 2 кадра проходит, но живой idle не выйдет.
Варианты без правки `game/assets/**` (вне области) не нашёл:
- настроить `loop_mode` для `Idle_A` в `.import`-файле рига (`_subresources`, `animations/Idle_A`, `loop_mode = 1`) — нужно разрешение на правку `game/assets`;
- скопировать `Idle_A` в `AnimationLibrary`-ресурс с `loop_mode = 1` — это новый файл вне `level.tscn`.
Решение ведущего.

**4.2. Гейт `level_check.gd` краснеет: `failed: 1`.** Вывод (дословно):
```
ПРОВАЛ модули без инстанса .gltf: Character
failed: 1
```
Причина: `collect_modules` считает модулями все `Node3D`-дети `Level` кроме `Prototypes` и требует у каждого инстанс `res://assets/kaykit/*.gltf`. `Character` — `Node3D` ребёнок `Level`, инстансом kaykit не является. Проверку не правил (по брифу). Исправление на стороне ведущего: либо исключить `Character` в `collect_modules` (правка `game/tests/**`, вне области T14), либо вынести персонажа из `Level` (бриф этого запрещает). Нужно решение.

**4.3. Скриншот.** Файл `T14-character-screenshot.png`, 1152×648. Персонаж на кадре, по моей оценке, — маленькая фигурка около `(695, 285)` в комнате справа от центра, рядом с красным баннером. Уверенности мало: размер фигурки в кадре очень мал, а камера смотрит издалека. Точной идентификации не сделано (нет крупного кадра). Прошу ведущего или ревьюера взглянуть.

## 5. Дословные выводы проверок

Проверка персонажа (`t14_check.gd`, удалён, 2 кадра после `add_child`):
```
ok: Character есть, позиция (18.0, 0.0, 18.0)
player Character/Rig_Medium_General/AnimationPlayer autoplay=Idle_A current=Idle_A playing=true
ok: Idle_A играет, is_playing истинно
failed: 0
код 0
```

Гейт `level_check.gd` (код возврата `1`):
```
ok: корень Level существует
ПРОВАЛ модули без инстанса .gltf: Character
ok: в Prototypes по одному инстансу на каждый kind (15)
ok: Prototypes вне плана, x = -40.0
ok: модули уровня не находятся в Prototypes
ok: в корне есть Camera3D
ok: в корне есть WorldEnvironment
failed: 1
код 1
```

Скриншот (`t14_capture.gd`, удалён, `--resolution 1152x648`): `сохранено: .../T14-character-screenshot.png, err 0, размер (1152, 648)`, код 0.

## 5a. Исправления после ревью ведущего

**Пункт 1 — `level_check` и `Character`.**
- `game/tests/level_check.gd`: новые константы `CHARACTER_NAME := "Character"` и `CHARACTER_PREFIX := "res://assets/kaykit_animations/"`; `collect_modules` исключает узел `Character` по имени; проверка 2 (модули — инстансы kaykit) не ослаблена.
- Новая проверка 6 `check_character`: `Character` существует как `Node3D`, и среди его детей есть инстанс из `res://assets/kaykit_animations/`.
- Прогон (дословно):
```
ok: корень Level существует
ok: модулей 205, у каждого инстанс .gltf
ok: в Prototypes по одному инстансу на каждый kind (14)
ok: Prototypes вне плана, x = -40.0
ok: модули уровня не находятся в Prototypes
ok: в корне есть Camera3D
ok: в корне есть WorldEnvironment
ok: Character есть, инстанс из kaykit_animations: res://assets/kaykit_animations/animations/Rig_Medium/Rig_Medium_General.glb
failed: 0
код 0
```
- Замечание: раньше строка «в Prototypes… (15)» считала ключ `""` от `Character`; теперь `(14)` — число видов, без лишнего ключа.

**Пункт 2 — зацикливание `Idle_A`.**
- Выбран вариант через импорт, ровно один файл: `game/assets/kaykit_animations/animations/Rig_Medium/Rig_Medium_General.glb.import`, строка `_subresources`. Другие `.import` не тронуты; `--import` переимпортировал только `Rig_Medium_General.glb`.
- Первая попытка с вложенным ключом `"settings": {"loop_mode": 1}` не сработала: Godot оставил её как постороннюю запись, а `loop_mode` остался 0. Канонический ключ — плоский `"settings/loop_mode"`. Итоговая запись в файле: `"animations": {"Idle_A": {... "settings/loop_mode": 1, ...}}`.
- Проба (`E:\Temp\opencode\t14_loop_probe.gd`, удалён): `Idle_A loop_mode 1` (LOOP_LINEAR). До правки было `0`.
- Перезапуск `level.tscn` через `load` в пробе не нужен: анимация в сцене берётся из импортированного ресурса, поэтому loop действует сам.

**Скриншот.** Переснят `E:\Temp\opencode\t14_capture.gd` (`--resolution 1152x648`), файл `T14-character-screenshot.png` перезаписан (время 23:25:08). Скрипт удалён. Персонаж на кадре — та же фигурка около (695, 285), уверенность прежняя: низкая, мелкая.

**Статус прежних пунктов.** Разделы 4.1 (loop) и 4.2 (красный гейт) выше сняты исправлениями. Раздел 3.1 (рига вместо манекена) — без изменений, решение ведущего принято.

**Сужено исключение (ревью, Important 1).**
- Исключение `Character` из модулей теперь привязано к источнику: узел исключается, только если среди его детей есть инстанс с `scene_file_path`, начинающимся с `res://assets/kaykit_animations/`. Имя `Character` само по себе не исключает. Логика вынесена в `has_character_instance(node)` и используется и в `collect_modules`, и в проверке 6 (`check_character`), так что условие одно.
- Буквально «scene_file_path узла Character» не подходит: `Character` — обычный `Node3D` без сцены-источника, путь есть у его дочернего инстанса `Rig_Medium_General`. Поэтому условие проверяется по инстансу внутри `Character`.
- Прогон (дословно):
```
ok: корень Level существует
ok: модулей 205, у каждого инстанс .gltf
ok: в Prototypes по одному инстансу на каждый kind (14)
ok: Prototypes вне плана, x = -40.0
ok: модули уровня не находятся в Prototypes
ok: в корне есть Camera3D
ok: в корне есть WorldEnvironment
ok: Character есть, инстанс из kaykit_animations
failed: 0
код 0
```

## 6. Что заметил и не стал делать

- `level_check.gd` предполагает, что все `Node3D`-дети корня — модули уровня. Любой не-модуль (персонаж, маркер, триггер) будет валить гейт. Это ограничение проверки, а не сцены; стоит решить до следующих задач с не-модульными узлами.
- Во время пробы Godot выводит `ERROR: Cannot get path of node as it is not in a scene tree` при вызове `get_path()` вне дерева. Это моя ошибка в пробе (исправлена), на результат не влияет.
- Меш манекена в `Rig_Medium_General.glb` имеет имена `Mannequin_*` (без `_Medium`) и другой набор частей, чем `Mannequin_Medium.glb` (`Mannequin_Medium_*`). Визуальная идентичность двух мешей не проверялась — возможно, это разные версии; для T14 не критично, так как используется только рига.

## Исправление после сохранения в редакторе

**Что было.** После сохранения `level.tscn` редактором (23:29) override `autoplay = "Idle_A"` на `AnimationPlayer` инстанса `Character/Rig_Medium_General` пропал. Анимация не запускалась.

**Что проверено.**
- В `level.tscn` нет `autoplay` ни в каком виде (grep по файлу).
- Имя `AnimationPlayer` внутри рига: `AnimationPlayer`, путь от корня рига `AnimationPlayer`. Анимаций 15, включая `Idle_A` (проба `E:\Temp\opencode\t14b_probe.gd`, удалён).
- Пересохранение через `PackedScene.pack` (headless, во временный файл) тоже отбрасывает override: в выходном файле нет ни `autoplay`, ни узла `AnimationPlayer`. Значит, одной строки в tscn мало: редактор её снова сотрёт.

**Что сделано.**
1. В `game/level/level.tscn` добавлены секция `[node name="AnimationPlayer" parent="Character/Rig_Medium_General" unique_id=1100000207]` с `autoplay = "Idle_A"` (восстановление по ТЗ, п. 2).
2. Надёжный способ, который переживает сохранение: скрипт `game/level/character_idle.gd` (`extends Node3D`), подключён к `Character` через `ext_resource` `16_idle` и `script = ExtResource("16_idle")`. В `_ready` вызывает `get_node("Rig_Medium_General/AnimationPlayer").play("Idle_A")`.
3. Строка `autoplay` оставлена: она запускает `Idle_A`, если переопределение уцелело, а скрипт гарантирует запуск, если нет. Зацикливание `Idle_A` (`loop_mode = 1` в `.import` рига) не трогал.
4. Проверено отдельно: с `autoplay = ""` на инстансе скрипт сам запускает `Idle_A` (см. пункт 4 ниже).
5. `.uid` для скрипта не создавался (Godot при headless-прогоне его не сгенерировал). Редактор создаст его при открытии сцены.

**Пункт 3. Целостность сцены — дословно:**
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

ok: корень Level существует
ok: модулей 205, у каждого инстанс .gltf
ok: в Prototypes по одному инстансу на каждый kind (14)
ok: Prototypes вне плана, x = -40.0
ok: модули уровня не находятся в Prototypes
ok: в корне есть Camera3D
ok: в корне есть WorldEnvironment
ok: Character есть, инстанс из kaykit_animations
failed: 0
exit=0
```
Камера: `size = 48.5` (grep по `level.tscn`). `WorldEnvironment` на месте.

**Пункт 4. Проба анимации — дословно:**
```
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

current_animation: Idle_A
is_playing: true
no_autoplay current_animation: Idle_A
no_autoplay is_playing: true
exit=0
```
Первые две строки — сцена как есть (`autoplay` + скрипт). Последние две — с `autoplay = ""` на инстансе, то есть только скрипт.

**Временные файлы.** `E:\Temp\opencode\t14b_probe.gd`, `t14b_anim.gd`, `t14b_resave.gd`, `t14b_resaved.tscn` удалены.

**Что не сделано.** Пересохранение редактором не воспроизводилось напрямую (только через `PackedScene.pack` headless). Проверка «в редакторе после сохранения» остаётся за пользователем: открыть `level.tscn`, сохранить, убедиться, что `Idle_A` играет (скрипт должен сработать в любом случае).
