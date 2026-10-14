"""Сборка блока породы: зал, ворота-тоннель, световые колодцы, двор-яма
(задачи T2r-a1, T2r-a2, T2r-a3).

Запуск (headless):
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python game/tools/build_cave_gate.py

Что делает:
  1. Строит одним мешем сплошной блок породы с полостью зала внутри:
     - полость — купол-эллипсоид (r=7.2, apex 7.0) с радиальным шумом стен из
       T1; в секторе ворот стена заменена плоской «дрессированной» плоскостью
       x = X_FLAT (X_FLAT, T2r-a2), которая плавно выходит на купол;
     - нижняя грань блока = пол: одна плоскость y=0 на всём пятне блока
       (пол диска r=7.2 ровный, без выбоин и уступов);
     - внешние боковые/верхние грани — неровная скала: внутренний шум-дент
       (только внутрь базового бокса, чтобы габарит не прыгал), с радиальным
       клампом, гарантирующим толщину породы над полостью; в окне ворот
       зубец скалы сглажен (плоский фасад под тоннель);
     - порода между полостью и внешней поверхностью сплошная — замер SKIN.
  2. Ворота (T2r-a2): проём |y| <= OPEN_HALF, z 0..OPEN_TOP, тоннель сквозь
     породу глубиной YARD_WALL_X - X_FLAT, паз под решётку (борозда по высоте
     проёма) и ниша-дымоход над перемычкой (шире и выше проёма).
  3. Двор-яма и шахты света (T2r-a3): блок растянут в +X, плоскость x = 8.0
     стала внутренней стеной двора (YARD_WALL_X), двор вырублен в породе
     (x 8…15, |y| <= 4, пол z=0, потолок z=7.0), три колодца зала и одна
     крупная шахта двора — сквозные отверстия в породе до плоскости BLOCK_Z.
  4. Запекает процедурный гранит в растровые текстуры 1024x1024
     (альбедо DIFFUSE/COLOR, ROUGHNESS, NORMAL) — Cycles, CPU.
  5. Подключает запечённые текстуры и экспортирует
     game/assets/cave_gate.glb (GLB, export_apply=True).

Устройство ворот (решение T2r-a2, см. отчёт): стена зала в секторе ворот
плоская (x = X_FLAT) и несёт ПРЯМОУГОЛЬНЫЙ проём, вырезанный по сетке стены
(колонки |k| <= GATE_K, ряды z < OPEN_TOP). Лоб тоннеля сваривается с плоскостью
x = YARD_WALL_X (бывший фасад блока, ныне стена двора) по общим вершинам (vput),
без единой Т-точки. Меш при этом НЕ замкнут: замер MANIFOLD даёт открытые рёбра
только там, где камень обрывается на проходе (порог и верх устья, низ боковин
у стены зала, низ и щель борозды). Дыр в породе нет (FLOOR missing = 0, луч
сквозь тоннель проходит насквозь).

Ниша-дымоход (правка по ревью T2r-a2, решение ведущего 14.10.2026) глухая: её
передняя стенка теперь — стена двора на плоскости x = YARD_WALL_X (выше потолка
двора, z 7…8, строится отдельно). Снаружи блок читается сплошной скалой, свет из
двора в нишу не попадает.

Растяжка блока (T2r-a3, решение ведущего 14.10.2026): BLOCK_X 8.0 -> 16.0, то
есть пятно блока x ∈ [-8, +16]. Простая подстановка BLOCK_X = 16 уехала бы
(фасад, устье тоннеля, задняя стенка ниши) и сломала бы NICHE_BLIND, поэтому
плоскость, где кончается rock у ворот, вынесена в отдельную константу
YARD_WALL_X = 8.0, а BLOCK_X остался только габаритом наружной грани. Геометрия
T2r-a2 не тронута: X_FLAT, GROOVE_X0, NICHE_BACK, NICHE_TOP лежат в той же
полке rock толщиной 1.2 м.

Сетки (T2r-a3): купол остался кольцевым (ROWS по высоте, SEG по азимуту), а
боковины, крышка и пол перешли на ПРЯМОУУГОЛЬНУЮ сетку плана блока (GRID_STEP).
Так крышка может нести квадратные отверстия шахт (кольцевая сетка их не даёт:
шаг по радиусу там метры), а пол по-прежнему сваривается с основанием купола —
мостиком bridge_ring (луч из центра к ближайшей точке внешнего контура). Швов и
дыр на стыках нет: крышка и боковины делят одну граничную сетку, пол с боковинами
— те же вершины.

Грабли, сохранённые из T1/fix5a–5d:
  - процедурные ноды в glTF не переживают => до экспорта только растровые карты;
  - bake в headless даёт CANCELLED без выделенной ноды текстуры =>
    для каждой запеки создаётся своя Image Texture, node.select=True + nodes.active;
  - в плоскости y=0 (Godot) / z=0 (Blender, Z-up) нельзя класть вторую
    поверхность (z-fighting) — плоскость пола ровно одна;
  - UV развёртка бокс-проекцией по доминирующей оси нормали, координаты
    переводятся в [0..1] (bake не заворачивает отрицательные UV).

Устройство пола/дна (решение T2r-a1, см. отчёт): блок стоит на уровне ground
на y=0, поэтому полость внутри и поверхность снаружи сходятся в одной плоскости
z=0. Плоскость z=0 построена ОДНА (всё пятно блока) с нормалью вверх: это и пол
для игрока (level_check.gd требует нормали пола вверх у всех треугольников в
плоскости y=0), и нижняя грань блока. Толщина породы «под полом» = 0 по
построению (пол = нижняя грань); замер SKIN считает толщину породы по лучам
из центра полости, выход полости выше EXIT_Z_MIN (пол и прибрежная зона
кромки исключены — там порода сходит на нет конструкцией). Лучи, выходящие из
полости через проём/нишу, меряют не толщину породы, а глубину прохода: они
исключаются из минимума (замер GATE считает их отдельно).

Константы геометрии частично дублируются в game/tests/level_check.gd —
габариты/пол/колодцы пересматриваются шагом T2r (обновление проверок).
"""

import math
import os
import time

import bpy
import numpy as np

T0 = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.normpath(os.path.join(HERE, ".."))
OUT_GLB = os.path.join(GAME_DIR, "assets", "cave_gate.glb")
# Промежуточные PNG (в glb не попадают как файлы — встраиваются в контейнер).
# Только внутри проекта (constraints.md §2): папка задачи удаляется после прогона.
TEX_DIR = os.path.normpath(os.path.join(
    HERE, "..", "..", "docs", "current", "2026-10-14-gate-entrance-v2", "temp", "bake"))

# --- Полость зала (форма из T1, сохранена дословно) ---------------------------
A = 7.0                 # горизонтальный радиус купола на экваторе (диаметр 14 м)
ZC = 1.0                # высота экватора (центр эллипсоида)
B = 6.0                 # вертикальная полуось => вершина свода на 7.0 м
APEX_Z = ZC + B
FLOOR_R = 7.2           # контрольный радиус пола (замер FLOOR); пол — плоскость z=0
SEG = 192               # сегментов по азимуту (полость и блок)
FLOOR_RINGS = 12        # кольца пола от основания купола к центру
# Кольца купола по высоте; 0.0 — основание (вариант кольца сваривается с полом блока).
ROWS = (0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0, 4.4,
        4.8, 5.0, 5.2, 5.6, 6.0, 6.3, 6.4, 6.5, 6.55, 6.6, 6.65, 6.7, 6.75,
        6.8, 6.85, 6.9, 6.93, 6.96, 6.98)
NOISE_AMP = 0.30        # амплитуда радиального шума стен/свода (как в T1)

# --- Блок породы (T2r-a1; растяжка в +X — T2r-a3) ------------------------------
# T2r-a1: симметричный блок ±8 по X. T2r-a3 растянул блок в +X под двор-яму
# (design.md:65 — двор x 7…15, z −4…4): плоскость x = 8.0 стала ВНУТРЕННЕЙ
# стеной двора (YARD_WALL_X), наружный фасад уехал на x = 16.0.
BLOCK_X0 = -8.0          # -X грань блока (с T2r-a1 не менялась)
BLOCK_X = 16.0           # +X грань блока (двор занимает 8…15, дальше 1 м камня)
BLOCK_Y = 8.0            # полуширина блока по Y (Blender; Godot Z)
BLOCK_Z = 9.0            # высота блока (Blender Z; Godot Y). Верх свода 7.0 => запас 2.0
OUT_DENT = 0.45          # максимум внутреннего смещения скалы (наружу не выступает)
# Кламп радиуса внешних вершин от оси: измеренный максимум полости со шумом
# 7.2651 (z=1.2, phi=0, см. выше) + минимум породы 0.5 м. Значение в литере, а
# не суммой констант: сумма даёт 7.7651, то есть другой меш без нужды (ассерты
# чисел в отчёте — от буквальных значений).
OUT_R_MIN = 7.77
# Кольца боковин. До OPEN_TOP включительно повторяют ROWS: на этом участке
# боковины тоннеля должны попадать ровно в ряды стены двора (иначе на лобу
# тоннеля появляются Т-точки). При растяжке блока совпадение рядов больше не
# обязательно (лоб тоннеля сваривается с плоскостью YARD_WALL_X напрямую), но
# оставлено — сетка стен от этого не меняется.
OUT_ROWS = (0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0, 4.4,
            4.8, 5.0, 5.2, 5.6, 6.0, 6.4, 6.8, 7.2, 7.6, 8.0, 8.4, 8.8, 9.0)
CLAMP_Z = 7.0           # кламп радиуса действует до этой высоты (выше полости нет)
EXIT_Z_MIN = 0.5        # SKIN: учитываем лучи, чей выход из полости выше этой высоты
GATE_PASSAGE_MARGIN = 0.3   # SKIN: запас вокруг проёма/ниши для отсева лучей-проходов
GRID_STEP = 0.5         # шаг ПРЯМОУГОЛЬНОЙ сетки плана блока (боковины/крышка/пол)

# --- Ворота-тоннель (T2r-a2) --------------------------------------------------
# Сетка стены ворот: колонка k = азимут 2*pi*k/SEG, ряд = ROWS. Стена плоская
# (x = X_FLAT) в колонках |k| <= GATE_K и плавно (smoothstep) выходит на купол.
OPEN_HALF = 1.9         # половина ширины проёма => 3.8 м (требование >= 3)
OPEN_TOP = 5.0          # высота проёма (требование >= 5.0, под арку arc2_1024 и решётку)
GATE_K = 9              # колонка боковины проёма: R_REF*sin(GATE_PHI) = OPEN_HALF
NICHE_K = 11            # колонка боковины ниши: ниша шире проёма
YARD_K = 20             # колонка стены двора: R_REF*sin(YARD_PHI) ~ YARD_HALF
GATE_BLEND_K = 18       # колонка, где плоская стена полностью возвращается в купол
GATE_PHI = 2.0 * math.pi * GATE_K / SEG
NICHE_PHI = 2.0 * math.pi * NICHE_K / SEG
GATE_BLEND_PHI = 2.0 * math.pi * GATE_BLEND_K / SEG
# Опорный радиус колонок стены: подобран так, чтобы колонка GATE_K попала
# ровно на боковину проёма (OPEN_HALF), а колонки стены и двора совпали.
R_REF = OPEN_HALF / math.sin(GATE_PHI)            # 6.5452
NICHE_HALF = R_REF * math.sin(NICHE_PHI)          # 2.3057 м — ниша шире проёма
X_FLAT = 6.8            # плоскость стены ворот; глубина тоннеля = YARD_WALL_X - X_FLAT = 1.2
WALL_FADE_Z = 6.5       # высота, на которой плоская стена возвращается в купол
NICHE_BACK = 7.4        # задняя стенка ниши (перемычка над проёмом: 0.6 м камня)
NICHE_TOP = 8.0         # верх ниши-дымохода (ниша выше проёма на 3.0 м)
GROOVE_X0 = 7.40        # начало паза под решётку (в тоннеле от стены зала)
GROOVE_W = 0.14         # ширина паза по X (требование >= 0.10)
GROOVE_D = 0.06         # глубина паза по Y (требование >= 0.05)
GROOVE_INNER = OPEN_HALF - GROOVE_D   # 1.84 — стенка борозды
GROOVE_Z0 = 0.0        # борозда доходит до пола (нижняя планка решётки упирается в пол)
GATE_FLAT_Y = 2.7       # скала у ворот сглажена при |y| <= GATE_FLAT_Y ...
GATE_FLAT_Z = 8.4       # ... и z <= GATE_FLAT_Z (окно фасада под тоннель и нишу)
OPEN_ROW = ROWS.index(OPEN_TOP)   # ряд перемычки в сетке стены (13)
NICHE_ROW = OUT_ROWS.index(NICHE_TOP)

# --- Двор-яма (T2r-a3) ---------------------------------------------------------
YARD_WALL_X = 8.0       # стена двора = плоскость, где кончается rock у ворот
YARD_FAR_X = 15.0       # дальняя стена двора (скала 15…16 до фасада блока)
YARD_HALF = 4.0         # половина ширины двора по Y (Blender) = Godot Z
YARD_TOP = 7.0          # потолок двора; выше — rock до BLOCK_Z
# Ряды стены двора: до перемычки повторяют сетку стены (сварка с тоннелем),
# выше — редкие, до точного потолка YARD_TOP.
YARD_ROWS = tuple([0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0, 4.4,
                   4.8, 5.0, 5.2, 5.6, 6.0, 6.4, 6.8, YARD_TOP])

# --- Световые шахты (T2r-a3) ---------------------------------------------------
WELL_R = 0.8            # радиус выреза колодца в куполе (отверстие ~1.6 м)
WELL_RHO = 2.6          # радиус расположения колодцев от оси
WELL_PHIS = (90.0, 210.0, 330.0)   # азимуты центров, градусы (проём на 0)
WELL_FLARE = 0.4        # высота конуса-раствора шахты у самой крышки блока
WELL_SQ = 1.05          # полусторона квадрата отверстия в крышке (сетка крышки)
YARD_SHAFT_C = (11.0, 0.0)   # центр шахты двора — над статуей (design.md:68)
YARD_SHAFT_R = 1.6      # радиус в потолке двора (отверстие 3.2 м)
YARD_SHAFT_SQ = 1.8     # полусторона отверстия в крышке блока
SHAFT_FLAT_MARGIN = 0.8  # ширина зоны, где вокруг отверстия гасится зубец скалы
SHAFT_SEG = 20          # сегментов в окружности отверстий (общая точность)
RIM_EPS = 1e-6          # точность «вершина на полу»

# --- Текстуры -----------------------------------------------------------------
UV_SPAN = 18.0          # метров на 1 единицу UV; блок ±8 ложится в [0..1]
UV_OFF = 9.0            # сдвиг: координаты [-9..9] -> UV [0..1]
TEX_SIZE = 1024
# Шум считается по UV (не по позиции): бокс-проекция накладывает грани друг на
# друга, поэтому шум от позиции давал бы конфликт цветов в общих texels.
# Масштабы пересчитаны на UV_SPAN 18 (было 15), чтобы метрический размер
# пятен/зерна остался прежним.
NOISE_SCALE_BLOTCH = 12.0   # ~1.5 м
NOISE_SCALE_GRAIN = 120.0   # ~0.15 м
NOISE_SCALE_ROUGH = 6.0     # ~3 м
NOISE_SCALE_BUMP = 60.0     # ~0.3 м


# --- Процедурный гранит -----------------------------------------------------

def make_granite():
    """Тёмно-серый гранит с холодным оттенком: пятна + зерно + бамп + шероховатость."""
    mat = bpy.data.materials.new("Granite")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tc = nt.nodes.new("ShaderNodeTexCoord")

    # крупные пятна породы
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = NOISE_SCALE_BLOTCH
    noise.inputs["Detail"].default_value = 7.0
    noise.inputs["Roughness"].default_value = 0.62
    nt.links.new(tc.outputs["UV"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (0.070, 0.075, 0.092, 1.0)
    ramp.color_ramp.elements[1].position = 0.76
    ramp.color_ramp.elements[1].color = (0.300, 0.320, 0.370, 1.0)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])

    # мелкое зерно, умножается на пятна
    grain = nt.nodes.new("ShaderNodeTexNoise")
    grain.inputs["Scale"].default_value = NOISE_SCALE_GRAIN
    grain.inputs["Detail"].default_value = 5.0
    nt.links.new(tc.outputs["UV"], grain.inputs["Vector"])
    grain_ramp = nt.nodes.new("ShaderNodeValToRGB")
    grain_ramp.color_ramp.elements[0].position = 0.35
    grain_ramp.color_ramp.elements[0].color = (0.62, 0.63, 0.66, 1.0)
    grain_ramp.color_ramp.elements[1].position = 0.72
    grain_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(grain.outputs["Fac"], grain_ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], mix.inputs[6])
    nt.links.new(grain_ramp.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])

    # шероховатость 0.82..0.97
    rough = nt.nodes.new("ShaderNodeTexNoise")
    rough.inputs["Scale"].default_value = NOISE_SCALE_ROUGH
    rough.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["UV"], rough.inputs["Vector"])
    rough_map = nt.nodes.new("ShaderNodeMapRange")
    rough_map.inputs["From Min"].default_value = 0.0
    rough_map.inputs["From Max"].default_value = 1.0
    rough_map.inputs["To Min"].default_value = 0.82
    rough_map.inputs["To Max"].default_value = 0.97
    nt.links.new(rough.outputs["Fac"], rough_map.inputs["Value"])
    nt.links.new(rough_map.outputs["Result"], bsdf.inputs["Roughness"])

    # мелкий рельеф
    bump_noise = nt.nodes.new("ShaderNodeTexNoise")
    bump_noise.inputs["Scale"].default_value = NOISE_SCALE_BUMP
    bump_noise.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["UV"], bump_noise.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.10
    nt.links.new(bump_noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Metallic"].default_value = 0.0
    return mat, nt, bsdf


# --- Полость зала (как в T1) -------------------------------------------------

def rho_at(z):
    """Горизонтальный радиус купола на высоте z (эллипсоид, экватор на ZC)."""
    t = (z - ZC) / B
    if abs(t) >= 1.0:
        return 0.0
    return A * math.sqrt(1.0 - t * t)


def noise_at(x, y, z):
    """Детерминированный шум [-1..1] для неровности стен полости."""
    n = (math.sin(0.95 * x + 0.7) * math.cos(0.85 * y - 0.4)
         + 0.6 * math.sin(1.6 * y + 1.1 * z + 0.3)
         + 0.4 * math.sin(2.1 * z + 0.9 * x - 1.2))
    return n * 0.5


def amp_at(z):
    """Амплитуда шума полости: 0 на полу (основание = точная окружность), полная выше 0.8 м."""
    return NOISE_AMP * min(max(z / 0.8, 0.0), 1.0)


def smoothstep(a, b, x):
    """Гладкий переход 0 -> 1 на отрезке [a, b] (детерминированно)."""
    if b <= a:
        return 0.0 if x < b else 1.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def gate_blend(phi):
    """Доля плоской стены ворот: 1 в колонках проёма и ниши, 0 на куполе.

    phi приходит из build_dome/perimeter_ring как угол в [0, 2*pi), поэтому угол
    сворачивается в [-pi, pi]: сектор ворот двусторонний (|y| <= NICHE_HALF).
    Плоская зона обязана накрывать колонку NICHE_K: иначе боковины ниши не
    совпадут с колонками фасада.
    """
    a = abs(phi)
    if a > math.pi:
        a = 2.0 * math.pi - a
    if a <= NICHE_PHI:
        return 1.0
    return 1.0 - smoothstep(NICHE_PHI, GATE_BLEND_PHI, a)


def wall_z_blend(z):
    """Плоская стена держится до перемычки (OPEN_TOP) и гаснет к куполу (WALL_FADE_Z)."""
    return 1.0 - smoothstep(OPEN_TOP, WALL_FADE_Z, z)


def build_dome():
    """Купол-полость: кольца по высоте + веер к вершине. Возвращает (verts, faces, base_ring).

    base_ring — индексы кольца основания (z=0, r=rho_at(0), шума нет): пол блока
    сваривается с ним, чтобы полость снизу была закрыта (замкнутый меш).
    В секторе ворот (gate_blend > 0) кольцо идёт по плоскости x = X_FLAT с
    колонками y = R_REF*sin(phi) — на этой плоскости проём вырезается по сетке.
    """
    verts = []
    faces = []
    shell_rings = []
    for z in ROWS:
        r0 = rho_at(z)
        amp = amp_at(z)
        base = len(verts)
        for k in range(SEG):
            phi = 2.0 * math.pi * k / SEG
            dx = math.cos(phi)
            dy = math.sin(phi)
            r = r0 + amp * noise_at(r0 * dx, r0 * dy, z)
            w = gate_blend(phi) * wall_z_blend(z)
            px = r * dx + (X_FLAT - r * dx) * w
            py = r * dy + (R_REF * dy - r * dy) * w
            verts.append((px, py, z))
        shell_rings.append(base)
    apex = len(verts)
    verts.append((0.0, 0.0, APEX_Z))
    for i in range(len(shell_rings) - 1):
        for k in range(SEG):
            k2 = (k + 1) % SEG
            a = shell_rings[i] + k
            b = shell_rings[i] + k2
            c = shell_rings[i + 1] + k2
            d = shell_rings[i + 1] + k
            faces.append([a, d, c, b])
    for k in range(SEG):
        k2 = (k + 1) % SEG
        faces.append([shell_rings[-1] + k, apex, shell_rings[-1] + k2])
    return verts, faces, shell_rings


def face_center(verts, face):
    n = len(face)
    sx = sy = sz = 0.0
    for k in face:
        sx += verts[k][0]
        sy += verts[k][1]
        sz += verts[k][2]
    return sx / n, sy / n, sz / n


# --- Световые колодцы зала (T2r-a3) --------------------------------------------
# Колодец — вертикальная шахта в породе: в куполе вырезается пятно граней,
# стенка шахты идёт от кромки пятна вертикально вверх и растворяется конусом
# к квадратному отверстию в крышке блока. Пятно вырезается по центрам граней,
# поэтому его кромка «ступенчатая» — но с шагом 0.05…0.09 м (плотные ряды ROWS
# у вершины и SEG=192 по азимуту) это читается как круглое отверстие, а не как
# дырка. Выталкивать вершины на окружность НЕ нужно и нельзя: у купола в
# ступеньках появляются вертикальные пары с одинаковой XY, от которых
# вырождаются грани.


def well_centers():
    """Центры колодцев зала в плоскости XY (Blender): rho * (cos phi, sin phi)."""
    return [(WELL_RHO * math.cos(math.radians(p)),
             WELL_RHO * math.sin(math.radians(p))) for p in WELL_PHIS]


def rim_loop(faces, removed):
    """Замкнутое кольцо вершин по границе вырезанного пятна граней.

    Граница = рёбра, встречающиеся ровно один раз среди удалённых граней;
    обход идёт по соседям (у каждой вершины кромки их ровно два)."""
    count = {}
    for i in removed:
        f = faces[i]
        n = len(f)
        for k in range(n):
            a, b = f[k], f[(k + 1) % n]
            key = (a, b) if a < b else (b, a)
            count[key] = count.get(key, 0) + 1
    adj = {}
    for (a, b), c in count.items():
        if c == 1:
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    if not adj:
        return []
    start = min(adj)
    loop = [start]
    prev = None
    cur = start
    while True:
        nxt = None
        for cand in adj[cur]:
            if cand != prev:
                nxt = cand
                break
        if nxt is None or nxt == start or len(loop) > 4 * SEG:
            break
        loop.append(nxt)
        prev = cur
        cur = nxt
    return loop


def cut_wells(verts, faces, removed):
    """Вырезает пятна колодцев в куполе; возвращает кромки (список (центр, кольцо)).

    Индексы граней купола — i*SEG + k, как в build_dome/cut_opening, поэтому
    пятно режется до любых других операций над faces."""
    rims = []
    for wx, wy in well_centers():
        patch = set()
        for i in range(len(faces)):
            if i in removed:
                continue
            cx, cy, cz = face_center(verts, faces[i])
            if (cx - wx) ** 2 + (cy - wy) ** 2 < WELL_R * WELL_R:
                patch.add(i)
        if not patch:
            raise RuntimeError("колодец (%.2f, %.2f): не вырезано ни одной грани" % (wx, wy))
        removed |= patch
        loop = rim_loop(faces, patch)
        if len(loop) < 8:
            raise RuntimeError("колодец (%.2f, %.2f): кромка не замкнута (%d)"
                               % (wx, wy, len(loop)))
        rims.append(((wx, wy), loop))
    return rims


# --- Общие примитивы плана блока (T2r-a3) ------------------------------------


def grid_lines(lo, hi, step, extra):
    """Координаты линий сетки на [lo, hi] с шагом step плюс обязательные extra."""
    n = int(round((hi - lo) / step))
    lines = [lo + i * step for i in range(n + 1)]
    lines.extend(extra)
    return sorted(set(round(v, 6) for v in lines if lo - 1e-9 <= v <= hi + 1e-9))


def block_loop(xs, ys):
    """Граница пятна блока по сетке: замкнутый контур против часовой стрелки."""
    loop = []
    for x in xs:
        loop.append((x, ys[0]))
    for y in ys[1:]:
        loop.append((xs[-1], y))
    for x in reversed(xs[:-1]):
        loop.append((x, ys[-1]))
    for y in reversed(ys[1:-1]):
        loop.append((xs[0], y))
    return loop


def rect_loop(x0, x1, y0, y1):
    """Прямоугольный контур против часовой стрелки (нижняя левая первой)."""
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def grid_loop(xs, ys, x0, x1, y0, y1):
    """Контур прямоугольника по ЛИНИЯМ сетки (без повторов).

    Нужен там, где контур сетки должен совпасть с клетками другой поверхности
    (отверстие шахты в крышке блока): иначе кромка стыка дала бы Т-точки на
    всей длине ребра."""
    bot = [round(x, 6) for x in xs if x0 - 1e-9 <= x <= x1 + 1e-9]
    side = [round(y, 6) for y in ys if y0 - 1e-9 <= y <= y1 + 1e-9]
    loop = [(x, y0) for x in bot]
    loop += [(x1, y) for y in side[1:]]
    loop += [(x, y1) for x in reversed(bot[:-1])]
    loop += [(x0, y) for y in reversed(side[1:-1])]
    return loop


def cap_loop(xs, ys, x0, x1, y0, y1):
    """Контур отверстия в крышке блока: точки сетки, уже сдвинутые rock_point.

    Крышка неровная (зубец скалы), поэтому её вершины берутся теми же
    rock_point, что и при построении клеток: иначе конус шахты повис бы на
    второй копии кольца и не сварился бы с клетками."""
    return [rock_point(p[0], p[1], BLOCK_Z)
            for p in grid_loop(xs, ys, x0, x1, y0, y1)]


TAU = 2.0 * math.pi


def _ang(p, center):
    a = math.atan2(p[1] - center[1], p[0] - center[0])
    return a + TAU if a < 0.0 else a


def _angle_order(loop, center, ref=0.0):
    """Контур, обходящийся по возрастанию угла вокруг center и начинающийся
    с точки под направлением ref (общий старт для обоих контуров!)."""
    order = sorted(range(len(loop)), key=lambda i: _ang(loop[i], center))
    angs = [_ang(loop[i], center) for i in order]
    k = 0
    while k < len(order) and angs[k] < ref - 1e-12:
        k += 1
    order = order[k:] + order[:k]
    angs = angs[k:] + [a + TAU for a in angs[:k]]
    return order, angs


def bridge_ring(verts, faces, cache, inner, outer, center):
    """Замостивает кольцо между двумя звёздными контурами вокруг center.

    Оба контура — готовые трёхмерные точки; обходятся по углу от ОДНОГО
    направления, шаг за шагом сравнивается абсолютный угол следующей вершины,
    и добавляется треугольник от того контура, чей угол идёт раньше. Получается
    ровно len(inner) + len(outer) граней и, главное, замощение ТОЛЬКО вершинами
    исходных контуров: ни одной новой точки на чужом ребре, то есть ни одной
    Т-точки. Для этого нужны контуры разной чётности (сетка плана блока против
    кольцевой сетки купола), поэтому «мостик лучом» с добавлением точек на
    внешнем контуре не годится — он и дал бы разрыв пола."""
    n = len(outer)
    m = len(inner)
    oi, oa = _angle_order(outer, center)
    ii, ia = _angle_order(inner, center)

    def out_pt(k):
        return vput(verts, cache, outer[oi[k % n]])

    def in_pt(j):
        return vput(verts, cache, inner[ii[j % m]])

    k = j = 0
    while k < n or j < m:
        no = oa[k + 1] if k + 1 < n else (oa[0] + TAU if k < n else float("inf"))
        ni = ia[j + 1] if j + 1 < m else (ia[0] + TAU if j < m else float("inf"))
        if k < n and no <= ni:
            faces.append([out_pt(k), out_pt(k + 1), in_pt(j)])
            k += 1
        else:
            faces.append([out_pt(k), in_pt(j), in_pt(j + 1)])
            j += 1


# --- Ворота-тоннель (T2r-a2) --------------------------------------------------
# Всё строится на общей сетке стены и фасада: колонка k = азимут 2*pi*k/SEG,
# ряд = ROWS (стена) = OUT_ROWS (фасад) до OPEN_TOP. Поэтому проём — точный
# прямоугольник, а лоб тоннеля сваривается с клетками фасада без Т-точек.

def cut_opening(verts, faces):
    """Вырезает в стене зала проём ворот: только проём, стена двора строится
    отдельно (build_yard) и тоже с проёмом.

    Грани купола строятся сеткой: грань ряда i и колонки k имеет индекс i*SEG + k
    (грань накрывает колонки k..k+1). Проём вырезается ДО любых других операций
    над faces, пока индексы совпадают с сеткой build_dome.

    Ниша-дымоход (правка по ревью T2r-a2, решение ведущего 14.10.2026) наружу
    НЕ открывается: её передняя стенка — стена двора на плоскости x =
    YARD_WALL_X (build_yard плюс заглушка z YARD_TOP…NICHE_TOP), отдельные
    грани-заглушки в плоскости фасада не строятся: любая новая грань на той же
    плоскости дала бы второй слой (z-fighting) либо шов по контуру окна.
    Замеры «ниша снаружи/изнутри» — в gate_probe (NICHE_BLIND).
    """
    removed = set()
    for i in range(OPEN_ROW):
        for k in range(-GATE_K, GATE_K):
            removed.add(i * SEG + (k % SEG))       # проём в стене зала
    return removed


def vkey(p):
    """Ключ дедупликации вершин (округление 1e-5: сварка с уже построенным мешем)."""
    return (round(p[0], 5), round(p[1], 5), round(p[2], 5))


def index_cache(verts):
    """Карта «координаты -> индекс» по уже построенным вершинам."""
    cache = {}
    for i, p in enumerate(verts):
        cache.setdefault(vkey(p), i)
    return cache


def vput(verts, cache, p):
    """Вершина в точке p: уже существующая или новая (общая точка = общий индекс)."""
    key = vkey(p)
    i = cache.get(key)
    if i is None:
        i = len(verts)
        verts.append(p)
        cache[key] = i
    return i


def add_grid(faces, rows):
    """Квады между соседними рядами сетки (rows — ряд к ряду, индексы вершин)."""
    n = 0
    for r in range(len(rows) - 1):
        a = rows[r]
        b = rows[r + 1]
        for j in range(len(a) - 1):
            faces.append([a[j], a[j + 1], b[j + 1], b[j]])
            n += 1
    return n


def build_gate(verts, faces, dome_rows, cache):
    """Проём, тоннель с пазом под решётку, перемычка и ниша-дымоход.

    dome_rows — начала колец сетки стены зала (индекс вершины = начало кольца
    + колонка k). Лоб тоннеля и передняя стенка ниши свариваются с плоскостью
    x = YARD_WALL_X по общим вершинам (vput) — раньше это был фасад блока на
    кольцах боковин, после растяжки блока (T2r-a3) фасад уехал на x = 16.0, а
    эту плоскость стала стена двора. Возвращает границы групп граней для
    ориентации: (start_tunnel, start_niche, end).

    Топология: каждая новая грань сварена с уже построенной по общим вершинам
    (vput), поэтому лоб тоннеля, уступы и стенки ниши не дают ни щелей, ни
    Т-точек. Открытые рёбра (замер MANIFOLD) остаются ровно там, где порода
    обрывается на проходе: порог и верх устья (x = YARD_WALL_X, z = 0 и
    z = OPEN_TOP), низ боковин у стены зала, низ и верх борозды.
    """
    niche_x = (NICHE_BACK, GROOVE_X0 + GROOVE_W, YARD_WALL_X)
    col_y = lambda k: R_REF * math.sin(2.0 * math.pi * k / SEG)
    y_gate = [col_y(k) for k in range(-NICHE_K, NICHE_K + 1)]
    y_open = [col_y(k) for k in range(-GATE_K, GATE_K + 1)]

    start_tunnel = len(faces)

    # 1. Боковины тоннеля |y| = OPEN_HALF с бороздой под решётку. Борозда
    #    шириной GROOVE_W по x и глубиной GROOVE_D по y идёт по всей высоте
    #    проёма от пола и выходит в нишу-дымоход через перемычку: её нижняя
    #    кромка лежит на сплошном полу тоннеля (туда упирается нижняя планка).
    for s in (1.0, -1.0):
        col = int(round(s * GATE_K)) % SEG
        rows = []
        for i in range(OPEN_ROW + 1):
            z = ROWS[i]
            row = [dome_rows[i] + col] + [vput(verts, cache, (x, s * y, z)) for x, y in
                                           ((GROOVE_X0, OPEN_HALF),
                                            (GROOVE_X0, GROOVE_INNER),
                                            (GROOVE_X0 + GROOVE_W, GROOVE_INNER),
                                            (GROOVE_X0 + GROOVE_W, OPEN_HALF))]
            row.append(vput(verts, cache, (YARD_WALL_X, col_y(col), z)))
            rows.append(row)
        add_grid(faces, rows)

    # 2. Перемычка (свод тоннеля): камень над проёмом от стены зала до ниши.
    rows = []
    for y in y_open:
        rows.append([vput(verts, cache, (X_FLAT, y, OPEN_TOP)),
                     vput(verts, cache, (NICHE_BACK, y, OPEN_TOP))])
    add_grid(faces, rows)

    start_niche = len(faces)

    # 3. Уступы по бокам ниши (z = OPEN_TOP, OPEN_HALF < |y| <= NICHE_HALF):
    #    камень под нишей шире проёма — по нему решётка едет в подъёме.
    for s in (1.0, -1.0):
        rows = []
        for k in range(GATE_K, NICHE_K + 1):
            y = s * col_y(k)
            rows.append([vput(verts, cache, (x, y, OPEN_TOP)) for x in niche_x])
        add_grid(faces, rows)

    # 4. Задняя стенка ниши (x = NICHE_BACK) — камнем от перемычки отделана.
    rows = []
    for j in range(OPEN_ROW, NICHE_ROW + 1):
        rows.append([vput(verts, cache, (NICHE_BACK, y, OUT_ROWS[j])) for y in y_gate])
    add_grid(faces, rows)

    # 5. Боковины ниши |y| = NICHE_HALF от задней стенки до фасада. Передние
    #    рёбра на x = BLOCK_X свариваются с клетками фасада (ниша глухая).
    for s in (1.0, -1.0):
        rows = []
        for j in range(OPEN_ROW, NICHE_ROW + 1):
            rows.append([vput(verts, cache, (x, s * NICHE_HALF, OUT_ROWS[j]))
                         for x in niche_x])
        add_grid(faces, rows)

    # 6. Верх ниши. Переднее ребро (x = BLOCK_X, z = NICHE_TOP) тоже
    #    сваривается с фасадом: карман закрыт со всех сторон, кроме щели паза.
    rows = []
    for y in y_gate:
        rows.append([vput(verts, cache, (x, y, NICHE_TOP)) for x in niche_x])
    add_grid(faces, rows)

    return start_tunnel, start_niche, len(faces)


# --- Блок породы (T2r-a1; сетка плана и растяжка — T2r-a3) ---------------------


def shaft_holes():
    """Квадратные отверстия шахт в крышке блока: (x0, x1, y0, y1).

    Квадраты (а не круги) потому, что крышка — прямоугольная сетка: отверстие
    обязано совпасть с её линиями, иначе появились бы Т-точки по всей длине
    кромки. Круглая шахта получается конусом от отверстия вниз (build_wells).
    Грани округлены до 6 знаков — ровно с той точностью, с какой grid_lines
    держит линии сетки: иначе крайняя линия отверстия выпадает из фильтра и
    контур теряет угол."""
    holes = []
    for wx, wy in well_centers():
        holes.append((round(wx - WELL_SQ, 6), round(wx + WELL_SQ, 6),
                      round(wy - WELL_SQ, 6), round(wy + WELL_SQ, 6)))
    cx, cy = YARD_SHAFT_C
    holes.append((cx - YARD_SHAFT_SQ, cx + YARD_SHAFT_SQ,
                  cy - YARD_SHAFT_SQ, cy + YARD_SHAFT_SQ))
    return holes


def block_grid():
    """Линии сетки плана блока: шаг GRID_STEP плюс линии отверстий шахт."""
    holes = shaft_holes()
    xs = grid_lines(BLOCK_X0, BLOCK_X, GRID_STEP, [c for h in holes for c in h[:2]])
    ys = grid_lines(-BLOCK_Y, BLOCK_Y, GRID_STEP, [c for h in holes for c in h[2:]])
    return xs, ys


def rock_noise(x, y, z):
    """Детерминированный шум [-1..1] для внешней скалы (другая частота, чем у стен)."""
    n = (math.sin(0.62 * x - 0.4) * math.cos(0.55 * y + 1.1)
         + 0.7 * math.sin(0.9 * y - 0.7 * z + 2.0)
         + 0.5 * math.sin(1.1 * z + 0.5 * x + 0.3)
         + 0.45 * math.sin(1.7 * x + 1.3 * y - 1.2))
    return n / (1.0 + 0.7 + 0.5 + 0.45)


def shaft_flat(x, y):
    """0..1: насколько внешний зубец скалы подавлен вокруг отверстий шахт.

    Отверстие в крышке обязано быть ЧИСТЫМ многоугольником сетки: конус
    шахты замыкается на него кольцом замощения, а зубец (rock_point) сдвигает
    вершины по-разному и ломает порядок обхода контура. Подавляем зубец в
    окрестности отверстия (с плавным краем) — это верх блока, в игре не видно.
    """
    f = 0.0
    m = SHAFT_FLAT_MARGIN
    for h in shaft_holes():
        fx = min(smoothstep(h[0] - m, h[0], x), 1.0 - smoothstep(h[1], h[1] + m, x))
        fy = min(smoothstep(h[2] - m, h[2], y), 1.0 - smoothstep(h[3], h[3] + m, y))
        f = max(f, max(fx, 0.0) * max(fy, 0.0))
    return f


def rock_point(x, y, z):
    """Внешняя вершина скалы: смещение внутрь по лучу из центра блока.

    Смещение только внутрь (d в [-OUT_DENT, 0]) — габарит AABB остаётся базовым
    боксом. В окне ворот (|y| <= GATE_FLAT_Y, z <= GATE_FLAT_Z) и вокруг
    отверстий шахт зубец скалы сглажен: первый — чтобы камень за воротами
    читался стеной, второй — чтобы отверстие в крышке было плоским
    многоугольником сетки (см. shaft_flat). Затем радиальный кламп (только до
    высоты CLAMP_Z, где есть полость) держит породу не ближе OUT_R_MIN к оси —
    это и есть гарантия толщины SKIN.
    """
    cx = cy = 0.0
    cz = BLOCK_Z / 2.0
    vx = x - cx
    vy = y - cy
    vz = z - cz
    length = math.sqrt(vx * vx + vy * vy + vz * vz)
    flat = max(min(1.0 - smoothstep(GATE_FLAT_Y, GATE_FLAT_Y + 1.0, abs(y)),
                   1.0 - smoothstep(GATE_FLAT_Z, GATE_FLAT_Z + 0.8, z)),
               shaft_flat(x, y))
    d = -OUT_DENT * (0.5 + 0.5 * rock_noise(x, y, z)) * (1.0 - flat)
    fade = min(z / 0.8, 1.0)
    s = d * fade / length
    px = x + vx * s
    py = y + vy * s
    pz = z + vz * s
    if z <= CLAMP_Z:
        r = math.hypot(px, py)
        if 1e-9 < r < OUT_R_MIN:
            sc = OUT_R_MIN / r
            px *= sc
            py *= sc
    return (px, py, pz)


def build_rock_tube(verts, faces, cache, loop):
    """Боковины блока: замкнутая лента из контура пятна (z=0, без смещения) вверх.

    Контур пятна — общая граница сетки крышки и пола (block_loop), поэтому
    верхнее кольцо ленты есть внешний контур крышки, а нижнее — внешний контур
    плоскости пола: сварка без шва и без Т-точек. Все вершины идут через vput:
    общий cache держит одну вершину на точку, иначе крышка и пол получили бы
    вторые копии граничных вершин боковин."""
    rows = []
    n = len(loop)
    for z in OUT_ROWS:
        row = []
        for i in range(n):
            x, y = loop[i]
            row.append(vput(verts, cache, (x, y, 0.0) if z <= 0.0 else rock_point(x, y, z)))
        rows.append(row)
    for k in range(len(rows) - 1):
        a = rows[k]
        b = rows[k + 1]
        for i in range(n):
            i2 = (i + 1) % n
            faces.append([a[i], a[i2], b[i2], b[i]])
    return rows


def build_rock_cap(verts, faces, cache, xs, ys):
    """Верхняя крышка блока: прямоугольная сетка плана с отверстиями шахт.

    Граница сетки — верхнее кольцо боковин (те же вершины), отверстия шахт —
    квадраты shaft_holes(): клетки внутри квадрата не строятся, их кромку
    закрывает конус шахты (build_wells). Все вершины крышки выше полости
    (апекс 7.0, крышка не ниже BLOCK_Z - OUT_DENT), кламп не нужен.
    """
    grid = {}

    def at(i, j):
        key = (i, j)
        idx = grid.get(key)
        if idx is None:
            idx = vput(verts, cache, rock_point(xs[i], ys[j], BLOCK_Z))
            grid[key] = idx
        return idx

    holes = shaft_holes()
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            xc = 0.5 * (xs[i] + xs[i + 1])
            yc = 0.5 * (ys[j] + ys[j + 1])
            if any(h[0] < xc < h[1] and h[2] < yc < h[3] for h in holes):
                continue
            faces.append([at(i, j), at(i + 1, j), at(i + 1, j + 1), at(i, j + 1)])
    return len(faces)


def build_bottom(verts, faces, cache, outer_ring, dome_base):
    """Плоскость пола/дна блока: всё пятно, z=0, нормаль вверх (единая поверхность).

    Снаружи внутрь: контур пятна (outer_ring — те же вершины, что и нижнее
    кольцо боковин, сварка без шва), кольцо основания купола (те же вершины, что
    и полость: полость снизу закрыта), затем кольца пола FLOOR_R к центру и
    веер. Полоса «контур → основание купола» замощается bridge_ring: у
    контура блока и у основания купола разное число вершин (сетка плана против
    кольцевой сетки купола), и замощение строится только их вершинами."""
    inner = [verts[dome_base + k] for k in range(SEG)]
    bridge_ring(verts, faces, cache, inner, outer_ring, (0.0, 0.0))
    rings = [dome_base]
    for j in range(FLOOR_RINGS - 1, 0, -1):
        r = FLOOR_R * j / FLOOR_RINGS
        base = len(verts)
        for k in range(SEG):
            phi = 2.0 * math.pi * k / SEG
            verts.append((r * math.cos(phi), r * math.sin(phi), 0.0))
        rings.append(base)
    for j in range(len(rings) - 1):
        for i in range(SEG):
            i2 = (i + 1) % SEG
            faces.append([rings[j] + i, rings[j] + i2,
                          rings[j + 1] + i2, rings[j + 1] + i])
    center = len(verts)
    verts.append((0.0, 0.0, 0.0))
    last = rings[-1]
    for i in range(SEG):
        i2 = (i + 1) % SEG
        faces.append([center, last + i, last + i2])
    return len(faces)


# --- Двор-яма и шахты света (T2r-a3) ------------------------------------------
# Двор — глухая яма в породе: пол на z=0 (часть общей плоскости пола блока),
# стены по периметру x YARD_WALL_X…YARD_FAR_X, |y| <= YARD_HALF до потолка
# YARD_TOP, выше — rock до BLOCK_Z. Изнутри через арку видно камень и статую,
# а не фон (design.md:65-67). Свет — одна крупная шахта в потолке двора над
# статуей (design.md:68), растворяющаяся конусом к отверстию в крышке блока.


def yard_angles():
    """Направления лучей из центра шахты двора, по которым строится потолок.

    Кроме равномерных направлений добавлены углы к углам двора (иначе потолок
    срезал бы углы), к бокам проёма ворот (|y| = OPEN_HALF — стена двора должна
    получить колонку ровно на боковине проёма) и к бокам ниши (|y| = NICHE_HALF
    — там, где ниша выходит в стену двора)."""
    cx, cy = YARD_SHAFT_C
    marks = [(YARD_WALL_X, -YARD_HALF), (YARD_FAR_X, -YARD_HALF),
             (YARD_FAR_X, YARD_HALF), (YARD_WALL_X, YARD_HALF),
             (YARD_WALL_X, -OPEN_HALF), (YARD_WALL_X, OPEN_HALF)]
    for k in range(-YARD_K, YARD_K + 1):
        marks.append((YARD_WALL_X, R_REF * math.sin(2.0 * math.pi * k / SEG)))
    angs = [2.0 * math.pi * i / SHAFT_SEG for i in range(SHAFT_SEG)]
    angs.extend(math.atan2(y - cy, x - cx) for x, y in marks)
    return sorted(set(round(a, 9) % (2.0 * math.pi) for a in angs))


def yard_sides():
    """Четыре стороны двора в плане; углы сторон — общие точки.

    Сторона у ворот (x = YARD_WALL_X) поделена на колонки сетки стены T2r-a2:
    там стена двора должна совпасть с тоннелем (|y| = OPEN_HALF) и с заглушкой
    ниши (|y| = NICHE_HALF), иначе на кромке появились бы Т-точки."""
    near = sorted(set(round(R_REF * math.sin(2.0 * math.pi * k / SEG), 6)
                      for k in range(-YARD_K, YARD_K + 1))
                  | {-YARD_HALF, YARD_HALF})
    return [
        [(YARD_WALL_X, y) for y in near],
        [(x, YARD_HALF) for x in (YARD_WALL_X, 9.5, 11.5, 13.5, YARD_FAR_X)],
        [(YARD_FAR_X, y) for y in (YARD_HALF, 3.0, 1.0, -1.0, -3.0, -YARD_HALF)],
        [(x, -YARD_HALF) for x in (YARD_FAR_X, 13.5, 11.5, 9.5, YARD_WALL_X)],
    ]


def yard_loop():
    """Контур двора для потолка: конкатенация сторон без повторов на углах."""
    loop = []
    for pts in yard_sides():
        for p in pts:
            if not loop or loop[-1] != p:
                loop.append(p)
    if loop[0] == loop[-1]:
        loop.pop()
    return loop


def build_yard(verts, faces, cache, xs, ys):
    """Двор-яма: стены, потолок с отверстием шахты и заглушка ниши.

    Потолок строится кольцом от окружности шахты к контуру двора (bridge_ring),
    поэтому верхнее ребро стен и кромка потолка — одни и те же точки (vput):
    ни щелей, ни Т-точек на стыке. Стены построены сеткой (колонки × YARD_ROWS)
    всеми четырьмя: вертикальные рёбра на углах тогда совпадают по рядам.
    Возвращает группы граней для ориентации."""
    cx, cy = YARD_SHAFT_C
    groups = []
    start = len(faces)
    rim3 = [(p[0], p[1], YARD_TOP) for p in yard_loop()]
    circle = [(cx + YARD_SHAFT_R * math.cos(a), cy + YARD_SHAFT_R * math.sin(a),
               YARD_TOP) for a in yard_angles()]
    bridge_ring(verts, faces, cache, circle, rim3, (cx, cy))
    # Стены по периметру. Верхнее ребро стены — точки потолка (общие вершины),
    # нижнее лежит на плоскости пола блока: отдельной грани пола двора не
    # строим (иначе z-fighting с общей плоскостью пола).
    for si, pts in enumerate(yard_sides()):
        grid = []
        for z in YARD_ROWS:
            grid.append([vput(verts, cache, (p[0], p[1], z)) for p in pts])
        for r in range(len(YARD_ROWS) - 1):
            z1 = YARD_ROWS[r + 1]
            for c in range(len(pts) - 1):
                pa = pts[c]
                pb = pts[c + 1]
                if (si == 0 and z1 <= OPEN_TOP + 1e-9
                        and pa[1] >= -OPEN_HALF - 1e-9 and pb[1] <= OPEN_HALF + 1e-9):
                    continue      # проём ворот
                faces.append([grid[r][c], grid[r][c + 1],
                              grid[r + 1][c + 1], grid[r + 1][c]])
    # Заглушка ниши: стена двора кончается потолком (z = 7.0), а карман ниши
    # поднимается до NICHE_TOP = 8.0 — глухую стенку над потолком строим здесь.
    rows = []
    for k in range(-NICHE_K, NICHE_K + 1):
        y = R_REF * math.sin(2.0 * math.pi * k / SEG)
        rows.append([vput(verts, cache, (YARD_WALL_X, y, YARD_TOP)),
                     vput(verts, cache, (YARD_WALL_X, y, NICHE_TOP))])
    add_grid(faces, rows)
    groups.append((start, len(faces), (0.5 * (YARD_WALL_X + YARD_FAR_X), 0.0,
                                       0.5 * YARD_TOP)))

    # Шахта двора: от окружности в потолке конусом к отверстию в крышке блока.
    start = len(faces)
    bridge_ring(verts, faces, cache, circle,
                cap_loop(xs, ys, cx - YARD_SHAFT_SQ, cx + YARD_SHAFT_SQ,
                         cy - YARD_SHAFT_SQ, cy + YARD_SHAFT_SQ),
                (cx, cy))
    # Опорная точка для нормалей — над срезом блока: пустота шахты продолжается
    # наружу через отверстие в крышке. Точка ВНУТРИ породы (например у пола
    # шахты) дала бы для конуса нормаль, направленную внутрь-вниз, и переворачивала
    # бы его грань наизнанку (угол между нормалью конуса и вектором к опорной
    # точке близок к 90°, знак неустойчив).
    groups.append((start, len(faces), (cx, cy, BLOCK_Z + 0.5)))
    return groups


def build_well_shafts(verts, faces, cache, rims, xs, ys):
    """Шахты колодцев зала: стенка от купола вверх и конус к отверстию в крышке.

    Кромка выреза — кольцо вершин купола (cut_wells). Стена идёт строго
    вертикально (та же XY, z = BLOCK_Z - WELL_FLARE), дальше конус к контуру
    отверстия в крышке блока, взятому по ЛИНИЯМ сетки (grid_loop), поэтому
    конус сваривается с клетками крышки без Т-точек. Возвращает группы граней."""
    groups = []
    z_flare = BLOCK_Z - WELL_FLARE
    for (wx, wy), loop in rims:
        start = len(faces)
        top = [(verts[v][0], verts[v][1], z_flare) for v in loop]
        n = len(loop)
        for i in range(n):
            faces.append([vput(verts, cache, verts[loop[i]]),
                          vput(verts, cache, verts[loop[(i + 1) % n]]),
                          vput(verts, cache, top[(i + 1) % n]),
                          vput(verts, cache, top[i])])
        bridge_ring(verts, faces, cache, top,
                    cap_loop(xs, ys, round(wx - WELL_SQ, 6), round(wx + WELL_SQ, 6),
                             round(wy - WELL_SQ, 6), round(wy + WELL_SQ, 6)),
                    (wx, wy))
        groups.append((start, len(faces), (wx, wy, BLOCK_Z + 0.5)))
    return groups


# --- Замеры -------------------------------------------------------------------

def tri_area(verts, f):
    """Площадь первого треугольника n-gon (для отсева вырожденных граней)."""
    a, b, c = verts[f[0]], verts[f[1]], verts[f[2]]
    e1 = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    e2 = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    nx = e1[1] * e2[2] - e1[2] * e2[1]
    ny = e1[2] * e2[0] - e1[0] * e2[2]
    nz = e1[0] * e2[1] - e1[1] * e2[0]
    return 0.5 * math.sqrt(nx * nx + ny * ny + nz * nz)


def edge_stats(faces):
    """Статистика рёбер: незамкнутые (дыры), не-манifold (>2 граней), конфликты обхода."""
    seen = {}
    for f in faces:
        n = len(f)
        for k in range(n):
            a, b = f[k], f[(k + 1) % n]
            key = (a, b) if a < b else (b, a)
            sign = 1 if a < b else -1
            e = seen.get(key)
            if e is None:
                seen[key] = [1, sign]
            else:
                e[0] += 1
                e[1] += sign
    boundary = 0
    nonmanifold = 0
    winding = 0
    for count, sign in seen.values():
        if count == 1:
            boundary += 1
        elif count > 2:
            nonmanifold += 1
        elif sign == 2 or sign == -2:
            winding += 1
    return len(seen), boundary, nonmanifold, winding


def dist_point_seg(p, a, b):
    d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    w = (p[0] - a[0], p[1] - a[1], p[2] - a[2])
    dd = d[0] * d[0] + d[1] * d[1] + d[2] * d[2]
    if dd <= 1e-18:
        return math.sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2])
    t = (w[0] * d[0] + w[1] * d[1] + w[2] * d[2]) / dd
    t = min(1.0, max(0.0, t))
    dx = d[0] * t - w[0]
    dy = d[1] * t - w[1]
    dz = d[2] * t - w[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def floor_probe(verts, faces, x0, x1, y0, y1, step_x, step_y, r_max=None):
    """Проба пола на плоскости z=0 по сетке (шаг step_x/step_y).

    Собирает треугольники, целиком лежащие в плоскости пола (max z <= RIM_EPS),
    и проверяет покрытие каждой точки сетки (опционально — только точек с
    радиусом <= r_max). Возвращает (точек, промахов, min запас до края
    покрывающего треугольника, min_y, max_y, max уступ от z=0).
    Ускорено пространственной сеткой по XY (иначе диск r=7.2 с шагом 0.1
    не просчитывается честной пробой по всем треугольникам).
    """
    tris = []
    for f in faces:
        n = len(f)
        if max(verts[k][2] for k in f) > RIM_EPS:
            continue
        for k in range(n - 2):
            t = (f[0], f[k + 1], f[k + 2])
            xs = [verts[v][0] for v in t]
            ys = [verts[v][1] for v in t]
            tris.append((t, min(xs), max(xs), min(ys), max(ys)))
    cell = 0.5
    grid = {}
    for ti, (t, tx0, tx1, ty0, ty1) in enumerate(tris):
        for ix in range(int(math.floor((tx0 - x0) / cell)), int(math.floor((tx1 - x0) / cell)) + 1):
            for iy in range(int(math.floor((ty0 - y0) / cell)), int(math.floor((ty1 - y0) / cell)) + 1):
                grid.setdefault((ix, iy), []).append(ti)
    total = 0
    missing = 0
    margin = float("inf")
    min_y = float("inf")
    max_y = -float("inf")
    max_step = 0.0
    x = x0
    while x <= x1 + 1e-9:
        y = y0
        while y <= y1 + 1e-9:
            if r_max is None or math.hypot(x, y) <= r_max + 1e-9:
                total += 1
                hit = None
                for ti in grid.get((int(math.floor((x - x0) / cell)),
                                    int(math.floor((y - y0) / cell))), ()):
                    t, tx0, tx1, ty0, ty1 = tris[ti]
                    if not (tx0 - 1e-9 <= x <= tx1 + 1e-9 and ty0 - 1e-9 <= y <= ty1 + 1e-9):
                        continue
                    a, b, c = verts[t[0]], verts[t[1]], verts[t[2]]
                    d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
                    if abs(d) < 1e-12:
                        continue
                    l1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / d
                    l2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / d
                    if l1 < -1e-9 or l2 < -1e-9 or (1.0 - l1 - l2) < -1e-9:
                        continue
                    hit = (t, a, b, c)
                    break
                if hit is None:
                    missing += 1
                else:
                    t, a, b, c = hit
                    zmin = min(a[2], b[2], c[2])
                    zmax = max(a[2], b[2], c[2])
                    min_y = min(min_y, zmin)
                    max_y = max(max_y, zmax)
                    max_step = max(max_step, zmax)
                    margin = min(margin, min(dist_point_seg((x, y, 0.0), hit[1], hit[2]),
                                             dist_point_seg((x, y, 0.0), hit[2], hit[3]),
                                             dist_point_seg((x, y, 0.0), hit[3], hit[1])))
            y = round(y + step_y, 6)
        x = round(x + step_x, 6)
    if min_y == float("inf"):
        min_y = max_y = max_step = 0.0
    return total, missing, margin, min_y, max_y, max_step


def tris_of(verts, faces):
    """Треугольники меша (каждый n-gon разбивается веером) как массив (N,3,3)."""
    tris = []
    for f in faces:
        for k in range(len(f) - 2):
            tris.append((f[0], f[k + 1], f[k + 2]))
    V = np.empty((len(tris), 3, 3), dtype=np.float64)
    for i, t in enumerate(tris):
        V[i, 0] = verts[t[0]]
        V[i, 1] = verts[t[1]]
        V[i, 2] = verts[t[2]]
    return V


def ray_hits(V, O, D):
    """Отсортированные параметры t пересечений луча (O, D) с треугольниками (Мёллер–Трамбор)."""
    V0 = V[:, 0]
    E1 = V[:, 1] - V[:, 0]
    E2 = V[:, 2] - V[:, 0]
    Pv = np.cross(D, E2)
    det = np.einsum("ij,ij->i", E1, Pv)
    ok = np.abs(det) > 1e-12
    inv = np.zeros_like(det)
    inv[ok] = 1.0 / det[ok]
    Tv = O - V0
    u = np.einsum("ij,ij->i", Tv, Pv) * inv
    Qv = np.cross(Tv, E1)
    v = (Qv @ D) * inv
    t = np.einsum("ij,ij->i", E2, Qv) * inv
    hit = ok & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1.0 + 1e-9) & (t > 1e-6)
    return np.sort(t[hit])


def in_gate(x, y, z, margin):
    """Точка внутри объёма ворот (проём + тоннель + ниша) с запасом margin."""
    if x >= X_FLAT - margin:
        if abs(y) <= OPEN_HALF + margin and -margin <= z <= NICHE_TOP + margin:
            return True
        if abs(y) <= NICHE_HALF + margin and OPEN_TOP - margin <= z <= NICHE_TOP + margin:
            return True
    return False


def in_shaft(x, y, z, margin):
    """Точка внутри бура шахты (колодец зала или шахта двора) с запасом margin.

    Лучи SKIN, выходящие из полости через шахту, меряют не толщину породы, а
    стенку бура: их надо отсекать так же, как лучи-проходы ворот (in_gate)."""
    for wx, wy in well_centers():
        if (x - wx) ** 2 + (y - wy) ** 2 < (WELL_R + margin) ** 2:
            return True
    cx, cy = YARD_SHAFT_C
    if z >= YARD_TOP - margin and (x - cx) ** 2 + (y - cy) ** 2 < (YARD_SHAFT_SQ + margin) ** 2:
        return True
    return False


def skin_probe(verts, faces, origin, n_elev=25, n_az=96):
    """Минимальная толщина породы: лучи из центра полости (numpy, Мёллер–Трамбор).

    Для каждого луча: t1 — первый выход из полости, t2 — выход из блока,
    толщина = t2 - t1. В минимум НЕ входят лучи, чей выход из полости ниже
    EXIT_Z_MIN (пол и прибрежная зона кромки: там порода сходит на нет
    конструкцией пол=дно), и лучи, выходящие через ворота: они меряют глубину
    прохода, а не толщину камня (замер GATE считает их отдельно). Лучи без
    второго пересечения тоже не участвуют, но считаются.
    """
    V = tris_of(verts, faces)
    O = np.array(origin, dtype=np.float64)
    total = 0
    skipped = 0
    passage = 0
    skins = []
    best = None
    for ie in range(n_elev):
        elev = math.pi * (ie + 0.5) / n_elev
        se = math.sin(elev)
        ce = math.cos(elev)
        for ia in range(n_az):
            az = 2.0 * math.pi * ia / n_az
            D = np.array((se * math.cos(az), se * math.sin(az), ce))
            ts = ray_hits(V, O, D)
            total += 1
            if ts.size == 0:
                skipped += 1
                continue
            t1 = float(ts[0])
            rest = ts[ts > t1 + 1e-6]
            exit_p = O + t1 * D
            if in_gate(exit_p[0], exit_p[1], exit_p[2], GATE_PASSAGE_MARGIN) \
                    or in_shaft(exit_p[0], exit_p[1], exit_p[2], GATE_PASSAGE_MARGIN):
                passage += 1
                continue
            if rest.size == 0 or exit_p[2] < EXIT_Z_MIN:
                skipped += 1
                continue
            s = float(rest[0]) - t1
            skins.append(s)
            if best is None or s < best[0]:
                best = (s, tuple(float(x) for x in D),
                        (float(exit_p[0]), float(exit_p[1]), float(exit_p[2])))
    return total, len(skins), skipped, passage, skins, best


def fmt_x(v):
    """Печать замера луча: число с точностью до миллиметра либо прочерк."""
    return "-" if v is None else "%.3f" % v


def gate_probe(verts, faces):
    """Замеры ворот лучами по готовому мешу (не по константам).

    Ширина/высота проёма — свободный отрезок по y/z на луче, пущенном из зала
    наружу через ось тоннеля; глубина тоннеля — от плоскости фасада до стены
    зала; паз — насколько стенка тоннеля втянута внутрь; ниша — размеры
    свободного объёма над перемычкой плюс проверка, что ниша глухая (снаружи
    лучи упираются в фасад, изнутри — тоже, а связь с тоннелем идёт через щель
    паза). Все числа — из лучей по готовому мешу, не из констант.
    """
    V = tris_of(verts, faces)
    out = {}

    def first(O, D):
        ts = ray_hits(V, np.array(O, dtype=np.float64), np.array(D, dtype=np.float64))
        return float(ts[0]) if ts.size else None

    # Луч замера идёт между стеной зала и пазом (GROOVE_X0), где боковины
    # тоннеля ещё плоские.
    x_probe = (X_FLAT + GROOVE_X0) * 0.5

    # Ширина проёма: свободный отрезок по y вокруг оси тоннеля на высотах
    # от 0.5 до OPEN_TOP-0.5 (берётся самое узкое место).
    widths = []
    h = 0.5
    while h <= OPEN_TOP - 0.5 + 1e-9:
        t_right = first((x_probe, 0.0, h), (0.0, 1.0, 0.0))
        t_left = first((x_probe, 0.0, h), (0.0, -1.0, 0.0))
        if t_right is not None and t_left is not None:
            widths.append((t_right + t_left, h))
        h += 0.5
    # Высота проёма: от пола тоннеля вверх до перемычки.
    t_up = first((x_probe, 0.0, 0.0), (0.0, 0.0, 1.0))

    # Глубина тоннеля: от плоскости стены двора до стены зала. Лучи бьют по
    # стенке (y > OPEN_HALF): в проёме стены нет — там проход, и луч ушёл бы
    # насквозь. Борозда (y = GROOVE_INNER…OPEN_HALF) — паз в стенке, не проход.
    depths = []
    for yy in (OPEN_HALF + 0.05, 0.5 * (OPEN_HALF + NICHE_HALF)):
        for zz in (0.5, 2.5, 4.5):
            t = first((YARD_WALL_X - 0.05, yy, zz), (-1.0, 0.0, 0.0))
            if t is not None:
                depths.append((t + 0.05, yy, zz))

    # Паз под решётку: стенка втянута на GROOVE_D только внутри борозды (по x),
    # рядом с ней стенка плоская на y = OPEN_HALF.
    groove = {}
    for label, xx in (("wall", GROOVE_X0 - 0.3),
                      ("groove", GROOVE_X0 + 0.5 * GROOVE_W)):
        hits = []
        for zz in (GROOVE_Z0 + 0.1, 2.5, 4.7):
            t = first((xx, 0.0, zz), (0.0, 1.0, 0.0))
            if t is not None:
                hits.append(t)
        groove[label] = hits

    # Ниша-дымоход: свободный объём над перемычкой (ширина по y, высота по z).
    # Высоту меряем по оси y = OPEN_HALF + 0.1 (внутри ниши, но вне проёма:
    # над проёмом свободный объём продолжается в тоннель, луч прошёл бы насквозь).
    x_niche = (NICHE_BACK + YARD_WALL_X) * 0.5
    y_niche = OPEN_HALF + 0.1
    t_niche_y = first((x_niche, 0.0, OPEN_TOP + 0.3), (0.0, 1.0, 0.0))
    t_niche_down = first((x_niche, y_niche, NICHE_TOP - 0.1), (0.0, 0.0, -1.0))
    t_niche_back = first((YARD_WALL_X - 0.05, 0.0, OPEN_TOP + 0.3), (-1.0, 0.0, 0.0))

    # --- Ниша глухая (правка по ревью T2r-a2) --------------------------------
    # Со стороны двора (x = YARD_WALL_X + 2, высотами ниже потолка двора) луч в
    # -X обязан упереться в стену двора на x = YARD_WALL_X. Пока ниша была
    # открыта, он проходил в альков и упирался в заднюю стенку x = NICHE_BACK
    # (= 7.40) — это и есть ассерт «снаружи нет проёма». Высоты берём не на
    # границах рядов, чтобы луч не скользил по ребру клетки стены. После
    # растяжки блока (T2r-a3) высоты ограничены потолком двора YARD_TOP: выше
    # него точка старта лежит в породе, и луч из породы ничего не доказывает.
    out_x = []
    for yy in (0.0, -1.0, 1.0, -2.0, 2.0):
        for zz in (OPEN_TOP + 0.1, 5.7, 6.3, 6.6, YARD_TOP - 0.1):
            t = first((YARD_WALL_X + 2.0, yy, zz), (-1.0, 0.0, 0.0))
            out_x.append((YARD_WALL_X + 2.0 - t if t is not None else None, yy, zz))
    hits = [p[0] for p in out_x if p[0] is not None]
    # Стена кармана изнутри: луч из ниши в +X обязан упереться в стену двора,
    # иначе ниша открыта наружу и свет из двора попадал бы внутрь.
    t_cap = first((x_niche, 0.0, OPEN_TOP + 0.3), (1.0, 0.0, 0.0))
    # Связь тоннель <-> ниша: щель паза наверху (GROOVE_X0…+GROOVE_W по x,
    # GROOVE_INNER…OPEN_HALF по y). Луч вниз из ниши проходит её и упирается в
    # пол тоннеля на z = 0 — паз по-прежнему выходит в нишу снизу.
    t_slit = first((GROOVE_X0 + 0.5 * GROOVE_W, GROOVE_INNER + 0.5 * GROOVE_D,
                    NICHE_TOP - 0.1), (0.0, 0.0, -1.0))

    out["width"] = min(widths)
    out["height"] = t_up if t_up is not None else 0.0
    out["depth"] = min(depths)
    out["depth_max"] = max(d[0] for d in depths)
    out["groove"] = groove
    out["niche_w"] = 2.0 * t_niche_y if t_niche_y is not None else 0.0
    out["niche_h"] = (t_niche_down + 0.1) if t_niche_down is not None else 0.0
    out["niche_d"] = (t_niche_back + 0.05) if t_niche_back is not None else 0.0
    out["niche_out"] = out_x
    out["niche_out_x"] = hits
    out["niche_cap_x"] = (YARD_WALL_X - x_niche) if t_cap is not None else None
    out["niche_slit_z"] = (NICHE_TOP - 0.1 - t_slit) if t_slit is not None else None
    return out


def yard_probe(verts, faces):
    """Замеры двора-ямы и шахт лучами по готовому мешу (не по константам).

    Двор читается как яма, если: дальняя стена стоит на YARD_FAR_X, стена у
    ворот — на YARD_WALL_X (вне проёма), боковые стены — на ±YARD_HALF,
    потолок выше YARD_TOP − 0.1 и не пробит (кроме самой шахты), а за дальней
    стеной есть порода (второе пересечение луча). Диаметр шахты двора идёт по
    лучу вверх на уровне края отверстия в потолке, верхний радиус — по лучу
    на уровне BLOCK_Z (раствор конуса)."""
    V = tris_of(verts, faces)

    def hits(O, D):
        return ray_hits(V, np.array(O, dtype=np.float64), np.array(D, dtype=np.float64))

    def chord(center, d):
        """Ширина отверстия: два луча из точки center в противоположные стороны.

        Точка берётся ВНУТРИ отверстия (на оси шахты): лучи упираются в стенку
        конуса и меряют его радиус на данной высоте. Луч, пущенный снаружи,
        цепляет зубец крышки и меряет не то."""
        ts = hits(center, d)
        tb = hits(center, (-d[0], -d[1], -d[2]))
        if not ts.size or not tb.size:
            return None
        return float(ts[0]) + float(tb[0])

    mid_y = 0.0
    hz = 3.0
    ts = hits((0.5 * (YARD_WALL_X + YARD_FAR_X), mid_y, hz), (1.0, 0.0, 0.0))
    far_x = 0.5 * (YARD_WALL_X + YARD_FAR_X) + float(ts[0]) if ts.size else -1.0
    # Толщина породы за дальней стеной: второе пересечение, отличное от первого
    # (грань стены состоит из двух треугольников, оба дают одно и то же t).
    rock = 0.0
    if ts.size:
        rest = ts[ts > float(ts[0]) + 0.05]
        rock = float(rest[0]) - float(ts[0]) if rest.size else 0.0
    ts = hits((0.5 * (YARD_WALL_X + YARD_FAR_X), 3.0, hz), (-1.0, 0.0, 0.0))
    near_x = 0.5 * (YARD_WALL_X + YARD_FAR_X) - float(ts[0]) if ts.size else -1.0
    ts = hits((YARD_SHAFT_C[0], 0.0, hz), (0.0, 1.0, 0.0))
    side_y = float(ts[0]) if ts.size else -1.0
    # Потолок двора: луч вверх в стороне от отверстия шахты (y = 0 идёт в шахту).
    ts = hits((YARD_SHAFT_C[0], 0.5 * (YARD_HALF + YARD_SHAFT_R + 0.4), hz),
              (0.0, 0.0, 1.0))
    ceil_z = hz + float(ts[0]) if ts.size else -1.0
    # Потолок в самой шахте: луч вверх из центра двора обязан выйти наружу
    # (отверстие в крышке блока настоящее, а не заглушка) — пересечений нет.
    ts = hits((YARD_SHAFT_C[0], 0.0, hz), (0.0, 0.0, 1.0))
    ceil_shaft_z = hz + float(ts[0]) if ts.size else -1.0
    # Диаметр отверстия в потолке (уровень на 0.05 выше потолка — внутри конуса)
    # и раствор шахты у самой крышки.
    w_shaft = chord((YARD_SHAFT_C[0], 0.0, YARD_TOP + 0.05), (1.0, 0.0, 0.0))
    w_top = chord((YARD_SHAFT_C[0], 0.0, BLOCK_Z - 0.05), (1.0, 0.0, 0.0))
    out = {
        "far_x": far_x, "near_x": near_x, "side_y": side_y,
        "ceil_z": ceil_z, "ceil_shaft_z": ceil_shaft_z, "rock_thick": rock,
        "shaft_r": 0.5 * w_shaft if w_shaft else -1.0,
        "shaft_top_r": 0.5 * w_top if w_top else -1.0,
    }
    out["ok"] = (abs(far_x - YARD_FAR_X) < 0.15
                 and abs(near_x - YARD_WALL_X) < 0.15
                 and abs(side_y - YARD_HALF) < 0.15
                 and ceil_z > YARD_TOP - 0.15
                 and rock >= 0.2
                 and out["shaft_r"] > 1.0)
    return out


def well_probe(verts, faces, rims):
    """Замеры колодцев зала: диаметр отверстия в куполе и в крышке блока.

    Диаметр в куполе берётся по кромке выреза (сама кромка и есть граница
    отверстия — точнее не измерить: грань купола у кромки наклонная, и
    горизонтальный луч на её высоте меряет ширину всей полости). Диаметр в
    крышке — двумя лучами из оси шахты на уровне BLOCK_Z - 0.05: они упираются
    в стенку конуса. Плюс контроль сквозности: луч вверх из центра колодца
    обязан выйти из блока (в пересечениях пусто) — отверстия в куполе и в
    крышке связаны одной шахтой, а не двумя дырками."""
    V = tris_of(verts, faces)
    rows = []
    for (wx, wy), loop in rims:
        radii = [math.hypot(verts[v][0] - wx, verts[v][1] - wy) for v in loop]
        ts = ray_hits(V, np.array((wx, wy, 5.0)), np.array((0.0, 0.0, 1.0)))
        tb = ray_hits(V, np.array((wx, wy, BLOCK_Z - 0.05)), np.array((1.0, 0.0, 0.0)))
        tb2 = ray_hits(V, np.array((wx, wy, BLOCK_Z - 0.05)), np.array((-1.0, 0.0, 0.0)))
        top_w = float(tb[0]) + float(tb2[0]) if tb.size and tb2.size else -1.0
        rows.append("w=(%.2f,%.2f) dome_d=%.3f..%.3f top_d=%.3f up_ray=%s"
                    % (wx, wy, 2.0 * min(radii), 2.0 * max(radii), top_w,
                       "сквозная" if not ts.size else fmt_x(5.0 + float(ts[0]))))
    return rows


# --- Ориентация и UV ----------------------------------------------------------

def orient_group(verts, faces, start, end, ref, toward):
    """Разворот граней [start, end): toward=True — нормаль к точке ref, иначе — от неё."""
    flipped = 0
    for i in range(start, end):
        f = faces[i]
        v0 = verts[f[0]]
        v1 = verts[f[1]]
        v2 = verts[f[2]]
        e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
        nx = e1[1] * e2[2] - e1[2] * e2[1]
        ny = e1[2] * e2[0] - e1[0] * e2[2]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        cx, cy, cz = face_center(verts, f)
        dot = nx * (ref[0] - cx) + ny * (ref[1] - cy) + nz * (ref[2] - cz)
        if (toward and dot < 0.0) or ((not toward) and dot > 0.0):
            faces[i] = list(reversed(f))
            flipped += 1
    return flipped


def orient_block(verts, faces, dome_end, outer_end, bottom_end):
    """Нормали: полость — внутрь пещеры, внешние грани — наружу, пол — вверх.

    Внимание: пол (нормаль вверх) и внешняя лента боковин (нормаль наружу)
    встречаются по кольцу пятна с конфликтом обхода — это осознанно: пол
    обязан смотреть вверх (level_check.gd), а нижняя грань стен «наружу»
    внизу отсутствует, потому что пол = дно блока. См. отчёт T2r-a1.
    Грани ворот (bottom_end и дальше) ориентируются отдельно — см. build_rock.
    """
    flipped = 0
    flipped += orient_group(verts, faces, 0, dome_end, (0.0, 0.0, 2.0), True)
    flipped += orient_group(verts, faces, dome_end, outer_end,
                            (0.0, 0.0, BLOCK_Z / 2.0), False)
    flipped += orient_group(verts, faces, outer_end, bottom_end, (0.0, 0.0, 10.0), True)
    return flipped


def box_uv(me):
    """Бокс-развёртка по доминирующей оси нормали.

    Координаты [-9..9] м переводятся в UV [0..1]: bake в Blender 5.2 не
    заворачивает отрицательный UV, иначе больше половины карты остаётся
    незапечённой (чёрный альбедо).
    """
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        n = poly.normal
        ax = 0 if abs(n.x) >= max(abs(n.y), abs(n.z)) else (1 if abs(n.y) >= abs(n.z) else 2)
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            if ax == 0:
                uv.data[li].uv = ((v.z + UV_OFF) / UV_SPAN, (v.y + UV_OFF) / UV_SPAN)
            elif ax == 1:
                uv.data[li].uv = ((v.x + UV_OFF) / UV_SPAN, (v.z + UV_OFF) / UV_SPAN)
            else:
                uv.data[li].uv = ((v.x + UV_OFF) / UV_SPAN, (v.y + UV_OFF) / UV_SPAN)
    uv.active = True
    uv.active_render = True
    return uv


# --- Bake -------------------------------------------------------------------

def new_image(name, srgb):
    img = bpy.data.images.new(name, TEX_SIZE, TEX_SIZE, alpha=False)
    img.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
    return img


def bake_to(mat, image, bake_type, **kwargs):
    """Запекать в image. Грабль 5.2: без выделенной+активной ноды — CANCELLED."""
    nt = mat.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    for n in nt.nodes:
        n.select = False
    tex.select = True
    nt.nodes.active = tex
    res = bpy.ops.object.bake(type=bake_type, margin=16, use_clear=True, **kwargs)
    nt.nodes.remove(tex)
    return res


def save_image(img, filename):
    path = os.path.join(TEX_DIR, filename)
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    return path


def assign_baked_material(obj, albedo, rough, normal):
    mat = bpy.data.materials.new("GraniteBaked")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    t_a = nt.nodes.new("ShaderNodeTexImage")
    t_a.image = albedo
    nt.links.new(t_a.outputs["Color"], bsdf.inputs["Base Color"])
    t_r = nt.nodes.new("ShaderNodeTexImage")
    t_r.image = rough
    nt.links.new(t_r.outputs["Color"], bsdf.inputs["Roughness"])
    t_n = nt.nodes.new("ShaderNodeTexImage")
    t_n.image = normal
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(t_n.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Metallic"].default_value = 0.0
    mat.use_backface_culling = False
    obj.data.materials.clear()
    obj.data.materials.append(mat)


# --- Сборка -----------------------------------------------------------------

def build_rock():
    """Геометрия блока с воротами, двором и шахтами + все замеры.

    Печатает GEOM…NICHE, YARD, SHAFT, возвращает замеры."""
    t = time.time()
    verts, faces, dome_rows = build_dome()
    dome_end = len(faces)
    cache = index_cache(verts)
    # Проём и пятна колодцев вырезаются по сетке купола ДО любых других
    # операций над faces: индексы граней считаются как i*SEG + k.
    removed = cut_opening(verts, faces)
    rims = cut_wells(verts, faces, removed)
    xs, ys = block_grid()
    loop = block_loop(xs, ys)
    tube_rows = build_rock_tube(verts, faces, cache, loop)
    outer_end_tube = len(faces)
    build_rock_cap(verts, faces, cache, xs, ys)
    outer_end = len(faces)
    build_bottom(verts, faces, cache, [verts[v] for v in tube_rows[0]], dome_rows[0])

    def kept_before(boundary):
        """Сколько граней осталось до исходного индекса boundary после выреза."""
        return sum(1 for i in range(boundary) if i not in removed)

    faces = [f for i, f in enumerate(faces) if i not in removed]
    dome_end = kept_before(dome_end)
    outer_end_tube = kept_before(outer_end_tube)
    outer_end = kept_before(outer_end)
    bottom_end = len(faces)
    gate_lo, gate_niche, gate_end = build_gate(verts, faces, dome_rows, cache)
    yard_groups = build_yard(verts, faces, cache, xs, ys)
    well_groups = build_well_shafts(verts, faces, cache, rims, xs, ys)
    flipped = orient_block(verts, faces, dome_end, outer_end, bottom_end)
    flipped += orient_group(verts, faces, bottom_end, gate_niche,
                            ((X_FLAT + YARD_WALL_X) * 0.5, 0.0, OPEN_TOP * 0.5), True)
    flipped += orient_group(verts, faces, gate_niche, gate_end,
                            ((NICHE_BACK + YARD_WALL_X) * 0.5, 0.0,
                             (OPEN_TOP + NICHE_TOP) * 0.5), True)
    for start, end, ref in yard_groups + well_groups:
        flipped += orient_group(verts, faces, start, end, ref, True)
    print("GEOM verts=%d faces=%d dome_faces=%d gate_faces=%d yard_faces=%d "
          "shaft_faces=%d flipped=%d build_s=%.2f"
          % (len(verts), len(faces), dome_end, gate_end - gate_lo,
             sum(e - s for s, e, _ in yard_groups),
             sum(e - s for s, e, _ in well_groups), flipped, time.time() - t))

    # --- Замеры геометрии -----------------------------------------------------
    edges, boundary, nonmanifold, winding = edge_stats(faces)
    print("MANIFOLD edges=%d boundary=%d nonmanifold=%d winding_conflicts=%d"
          % (edges, boundary, nonmanifold, winding))

    outer_verts = set()
    for f in faces[dome_end:outer_end]:
        outer_verts.update(f)
    oxs = [verts[v][0] for v in outer_verts]
    oys = [verts[v][1] for v in outer_verts]
    ozs = [verts[v][2] for v in outer_verts]
    print("BLOCK x=[%.3f..%.3f] y=[%.3f..%.3f] z=[%.3f..%.3f] outer_verts=%d "
          "outer_faces=%d (Blender Z-up; порода от полости: кламп R>=%.2f)"
          % (min(oxs), max(oxs), min(oys), max(oys), min(ozs), max(ozs),
             len(outer_verts), outer_end - dome_end, OUT_R_MIN))
    print("BLOCK_GODOT x=[%.3f..%.3f] y=[%.3f..%.3f] z=[%.3f..%.3f] (Y-up: Godot Y = Blender Z)"
          % (min(oxs), max(oxs), min(ozs), max(ozs), min(oys), max(oys)))

    zero_mesh = sum(1 for f in faces if tri_area(verts, f) < 1e-9)
    print("ZERO_AREA degenerate_faces=%d" % zero_mesh)

    total_pts, miss_pts, margin, min_y, max_y, max_step = floor_probe(
        verts, faces, BLOCK_X0, BLOCK_X, -BLOCK_Y, BLOCK_Y, 0.1, 0.1, r_max=FLOOR_R)
    print("FLOOR probe=disk r=%.1f step=0.1 pts=%d missing=%d min_y=%.3f max_y=%.3f "
          "max_step=%.3f min_margin_to_tri_edge=%.3f"
          % (FLOOR_R, total_pts, miss_pts, min_y, max_y, max_step, margin))

    t = time.time()
    rays, counted, skipped, passage, skins, best = skin_probe(verts, faces, (0.0, 0.0, 3.5))
    if best is None:
        print("SKIN rays=%d counted=0 — нет лучей с выходом полости выше %.1f (ПРОВАЛ)"
              % (rays, EXIT_Z_MIN))
    else:
        print("SKIN rays=%d counted=%d floor_or_graze=%d passage=%d exit_z>=%.1f "
              "min=%.3f mean=%.3f max=%.3f min_at_exit=(%.2f,%.2f,%.2f) "
              "min_dir=(%.2f,%.2f,%.2f) probe_s=%.1f"
              % (rays, counted, skipped, passage, EXIT_Z_MIN, min(skins),
                 sum(skins) / len(skins), max(skins),
                 best[2][0], best[2][1], best[2][2],
                 best[1][0], best[1][1], best[1][2], time.time() - t))

    g = gate_probe(verts, faces)
    print("GATE opening_w=%.3f (узкое место на высоте %.2f) opening_h=%.3f "
          "tunnel_depth_min=%.3f (y=%.2f z=%.2f) tunnel_depth_max=%.3f wall_x=%.2f"
          % (g["width"][0], g["width"][1], g["height"], g["depth"][0],
             g["depth"][1], g["depth"][2], g["depth_max"], YARD_WALL_X))
    g_wall = max(g["groove"]["wall"])
    g_groove = min(g["groove"]["groove"])
    print("GROOVE wall_y=%.3f groove_y=%.3f depth=%.3f width_x=%.3f "
          "z=%.3f..%.3f samples=%d" % (g_wall, g_groove, g_wall - g_groove,
                                       GROOVE_W, GROOVE_Z0, OPEN_TOP,
                                       len(g["groove"]["groove"])))
    print("NICHE w_const=%.3f open_w=%.3f (порыв проёма %.3f) h_above_lintel=%.3f "
          "depth_x=%.3f back_x=%.2f top_z=%.2f"
          % (2.0 * NICHE_HALF, g["niche_w"], g["niche_w"] - 2.0 * OPEN_HALF,
             g["niche_h"], g["niche_d"], NICHE_BACK, NICHE_TOP))
    # Ниша глухая: каждый луч со стороны двора обязан остановиться на стене
    # двора. Иначе первым он встретит заднюю стенку кармана (NICHE_BACK <
    # YARD_WALL_X) — это и означало бы открытый наружу альков (Important 1 по
    # ревью T2r-a2).
    ox = g["niche_out_x"]
    blind = (len(ox) == len(g["niche_out"]) and bool(ox)
             and max(abs(x - YARD_WALL_X) for x in ox) < 1e-3
             and g["niche_cap_x"] is not None)
    print("NICHE_BLIND outside_rays=%d/%d first_hit_x=[%.3f..%.3f] wall_x=%.2f "
          "cap_from_inside=%s slit_down_to_z=%s — %s"
          % (len(ox), len(g["niche_out"]), min(ox), max(ox), YARD_WALL_X,
             fmt_x(g["niche_cap_x"]), fmt_x(g["niche_slit_z"]),
             "ГЛУХАЯ" if blind else "ОТКРЫТА НАРУЖУ (ПРОВАЛ)"))

    y = yard_probe(verts, faces)
    print("YARD far_wall_x=%.3f (в плюс %.3f) near_wall_x=%.3f side_y=%.3f "
          "ceiling_z=%.3f up_ray_in_shaft=%s rock_behind_wall=%.3f "
          "shaft_d=%.3f shaft_top_d=%.3f — %s"
          % (y["far_x"], YARD_FAR_X - y["far_x"], y["near_x"], y["side_y"],
             y["ceil_z"], fmt_x(y["ceil_shaft_z"]), y["rock_thick"],
             2.0 * y["shaft_r"], 2.0 * y["shaft_top_r"],
             "ГЛУХОЙ" if y["ok"] else "ПРОВАЛ"))
    for row in well_probe(verts, faces, rims):
        print("WELL %s" % row)

    me = bpy.data.meshes.new("CaveGate")
    me.from_pydata(verts, [], faces)
    me.update()
    box_uv(me)
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    print("MESH polys=%d tris=%d aabb=(%.2f..%.2f, %.2f..%.2f, %.2f..%.2f)"
          % (len(me.polygons), tris, min(xs), max(xs), min(ys), max(ys),
             min(zs), max(zs)))
    return {"verts": verts, "faces": faces, "mesh": me, "tris": tris, "gate": g,
            "skins": skins, "aabb": (xs, ys, zs)}


def main():
    os.makedirs(TEX_DIR, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out = build_rock()
    verts, faces, me, tris = out["verts"], out["faces"], out["mesh"], out["tris"]
    xs, ys, zs = out["aabb"]
    skins, g = out["skins"], out["gate"]

    obj = bpy.data.objects.new("CaveGate", me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    mat, nt, bsdf = make_granite()
    me.materials.append(mat)

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 8
    scene.cycles.use_denoising = False

    times = []
    img_a = new_image("granite_albedo", srgb=True)
    t = time.time()
    res = bake_to(mat, img_a, 'DIFFUSE', pass_filter={'COLOR'})
    times.append(("albedo", time.time() - t, str(res)))
    img_r = new_image("granite_roughness", srgb=False)
    t = time.time()
    res = bake_to(mat, img_r, 'ROUGHNESS')
    times.append(("roughness", time.time() - t, str(res)))
    img_n = new_image("granite_normal", srgb=False)
    t = time.time()
    res = bake_to(mat, img_n, 'NORMAL')
    times.append(("normal", time.time() - t, str(res)))

    # Статистика альбедо: незапечённые (чёрные) texels ловим здесь же.
    px = list(img_a.pixels)
    n = len(px) // 4
    step = max(1, n // 20000)
    vals = []
    black = 0
    for i in range(0, n, step):
        r = px[4 * i]
        if r == 0.0 and px[4 * i + 1] == 0.0 and px[4 * i + 2] == 0.0:
            black += 1
        else:
            vals.append(r)
    print("BAKE %s nonblack_mean=%.4f min=%.4f max=%.4f black_pct=%.1f"
          % (["%s:%.2fs:%s" % t for t in times],
             sum(vals) / len(vals), min(vals), max(vals),
             100.0 * black / max(1, black + len(vals))))

    save_image(img_a, "granite_albedo.png")
    save_image(img_r, "granite_roughness.png")
    save_image(img_n, "granite_normal.png")
    print("TEX albedo_bytes=%d rough_bytes=%d normal_bytes=%d"
          % (os.path.getsize(os.path.join(TEX_DIR, "granite_albedo.png")),
             os.path.getsize(os.path.join(TEX_DIR, "granite_roughness.png")),
             os.path.getsize(os.path.join(TEX_DIR, "granite_normal.png"))))

    assign_baked_material(obj, img_a, img_r, img_n)

    bpy.ops.export_scene.gltf(
        filepath=OUT_GLB,
        export_format="GLB",
        use_selection=False,
        export_apply=True,
    )
    print("RESULT glb=%s bytes=%d tris=%d verts=%d block=%.1fx%.1fx%.1f "
          "dome_apex=%.1f floor_r=%.1f skin_min=%.3f "
          "opening=%.1fx%.1f tunnel=%.2f niche=%.1fx%.1f total_s=%.1f"
          % (OUT_GLB, os.path.getsize(OUT_GLB), tris, len(verts),
             max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs),
             APEX_Z, FLOOR_R,
             min(skins) if skins else -1.0,
             g["width"][0], g["height"], g["depth"][0],
             g["niche_w"], g["niche_h"] + OPEN_TOP, time.time() - T0))


if __name__ == "__main__":
    main()
