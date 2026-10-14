"""Сборка блока породы с полостью зала и воротами-тоннелем (задачи T2r-a1, T2r-a2).

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
     породу глубиной BLOCK_X - X_FLAT, паз под решётку (борозда по высоте
     проёма) и ниша-дымоход над перемычкой (шире и выше проёма).
  3. Запекает процедурный гранит в растровые текстуры 1024x1024
     (альбедо DIFFUSE/COLOR, ROUGHNESS, NORMAL) — Cycles, CPU.
  4. Подключает запечённые текстуры и экспортирует
     game/assets/cave_gate.glb (GLB, export_apply=True).

Устройство ворот (решение T2r-a2, см. отчёт): стена зала в секторе ворот
плоская (x = X_FLAT) и несёт ПРЯМОУГОЛЬНЫЙ проём, вырезанный по сетке стены
(колонки |k| <= GATE_K, ряды z < OPEN_TOP). Благодаря общей сетке стены и
фасада (колонки y = R_REF*sin(phi), ряды OUT_ROWS повторяют ROWS до OPEN_TOP)
лоб тоннеля сваривается с клетками фасада без единой Т-точки. Меш при этом НЕ
замкнут: замер MANIFOLD текущей сборки даёт boundary = 54 открытых ребра, все —
там, где камень обрывается на проходе: 18 порог у фасада (x = BLOCK_X, z = 0),
18 верх устья тоннеля (x = BLOCK_X, z = OPEN_TOP), 2 низ боковин у стены зала,
8 низ борозды, 8 щель борозды в нишу. Дыр в породе нет (FLOOR missing = 0, луч
сквозь тоннель проходит насквозь); до закрытия ниши было 36. Плоская стена нужна
ещё и потому, что порода по оси +X тоньше метра (SKIN базовой сборки: 0.625 м).

Ниша-дымоход (правка по ревью T2r-a2, решение ведущего 14.10.2026) глухая:
фасад в её окне НЕ вырезается, и клетки фасада сами образуют стенку кармана на
плоскости x = BLOCK_X. Снаружи фасад читается сплошной скалой, свет из двора в
нишу не попадает, объём кармана внутри породы прежний (|y| <= NICHE_HALF,
OPEN_TOP <= z <= NICHE_TOP, NICHE_BACK <= x <= BLOCK_X).

Шахты света и яма двора НЕ строятся — это шаг T2r-a3 (функция cut_wells в
файле сохранена и будет адаптирована под эту же сетку).

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
        4.8, 5.0, 5.2, 5.6, 6.0, 6.3, 6.55, 6.75, 6.9, 6.97)
NOISE_AMP = 0.30        # амплитуда радиального шума стен/свода (как в T1)

# --- Блок породы (T2r-a1) -----------------------------------------------------
# Габарит по брифу «~x −8…+7, y 0…+9, z −8…+8 (уточни замером)». Замер полости:
# макс. радиус со шумом 7.2651 (z=1.2, phi=0), пол-диск r=7.2 => передняя грань
# x=+7 не вмещает полость. Зафиксировано симметрично ±8 (см. отчёт T2r-a1).
BLOCK_X = 8.0           # полуширина блока по X (Blender)
BLOCK_Y = 8.0           # полуширина блока по Y (Blender; Godot Z)
BLOCK_Z = 9.0           # высота блока (Blender Z; Godot Y). Верх свода 7.0 => запас 2.0
OUT_DENT = 0.45         # максимум внутреннего смещения скалы (наружу не выступает)
# Кламп радиуса внешних вершин от оси: измеренный максимум полости со шумом
# 7.2651 (z=1.2, phi=0, см. выше) + минимум породы 0.5 м. Значение в литере, а
# не суммой констант: сумма даёт 7.7651, то есть другой меш без нужды (ассерты
# чисел в отчёте — от буквальных значений).
OUT_R_MIN = 7.77
# Кольца боковин. До OPEN_TOP включительно повторяют ROWS: на этом участке
# боковины тоннеля должны попадать ровно в ряды фасада (иначе на лобу тоннеля
# появляются Т-точки и меш перестаёт быть замкнутым).
OUT_ROWS = (0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0, 4.4,
            4.8, 5.0, 5.2, 5.6, 6.0, 6.4, 6.8, 7.2, 7.6, 8.0, 8.4, 8.8, 9.0)
CLAMP_Z = 7.0           # кламп радиуса действует до этой высоты (выше полости нет)
CAP_SCALES = (0.75, 0.5, 0.25)   # кольца верхней крышки (s=1 — кольцо боковин)
EXIT_Z_MIN = 0.5        # SKIN: учитываем лучи, чей выход из полости выше этой высоты
GATE_PASSAGE_MARGIN = 0.3   # SKIN: запас вокруг проёма/ниши для отсева лучей-проходов

# --- Ворота-тоннель (T2r-a2) --------------------------------------------------
# Сетка стены ворот: колонка k = азимут 2*pi*k/SEG, ряд = ROWS. Стена плоская
# (x = X_FLAT) в колонках |k| <= GATE_K и плавно (smoothstep) выходит на купол.
OPEN_HALF = 1.9         # половина ширины проёма => 3.8 м (требование >= 3)
OPEN_TOP = 5.0          # высота проёма (требование >= 5.0, под арку arc2_1024 и решётку)
GATE_K = 9              # колонка боковины проёма: R_REF*sin(GATE_PHI) = OPEN_HALF
NICHE_K = 11            # колонка боковины ниши: ниша шире проёма
GATE_BLEND_K = 18       # колонка, где плоская стена полностью возвращается в купол
GATE_PHI = 2.0 * math.pi * GATE_K / SEG
NICHE_PHI = 2.0 * math.pi * NICHE_K / SEG
GATE_BLEND_PHI = 2.0 * math.pi * GATE_BLEND_K / SEG
# Опорный радиус колонок стены: подобран так, чтобы колонка GATE_K попала
# ровно на боковину проёма (OPEN_HALF), а колонки стены и фасада совпали.
R_REF = OPEN_HALF / math.sin(GATE_PHI)            # 6.5452
NICHE_HALF = R_REF * math.sin(NICHE_PHI)          # 2.3057 м — ниша шире проёма
X_FLAT = 6.8            # плоскость стены ворот; глубина тоннеля = BLOCK_X - X_FLAT = 1.2
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
CLIFF_FACE0 = len(ROWS) * SEG     # индекс первой грани боковин блока после купола

# --- Колодцы света (T2r-a3, сейчас не строятся) ------------------------------
WELL_R = 0.7            # радиус светового колодца (отверстие 1.4 м)
WELL_RHO = 2.6          # радиус расположения колодцев от оси
WELL_PHIS = (90.0, 210.0, 330.0)   # азимуты центров, градусы (проём на 0)
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


# --- Световые колодцы и двор-яма: ШАГ T2r-a3, в этой сборке НЕ вызываются -----
# Функция cut_wells ниже — заготовка шага T2r-a3, а не мёртвый мусор: её вызовет
# build_rock() этого же файла, когда a3 перепишет её под общую сетку стены и
# фасада (сейчас она режет по центрам граней и выталкивает вершины, а на
# плоской стене ворот так делать нельзя — см. отчёт T2r-a2 §6.3). Помечена явно,
# чтобы её не приняли за забытый код; до a3 не вызывается.


def cut_wells(verts, faces, removed):
    """Круглые световые колодцы: грани с центром внутри окружности удаляются,
    вершины внутри окружности выталкиваются на её границу (кроме пола)."""
    wells = [(WELL_RHO * math.cos(math.radians(p)),
              WELL_RHO * math.sin(math.radians(p))) for p in WELL_PHIS]
    for i, f in enumerate(faces):
        if i in removed:
            continue
        cx, cy, cz = face_center(verts, f)
        if cz <= 0.0:
            continue
        for wx, wy in wells:
            if (cx - wx) ** 2 + (cy - wy) ** 2 < WELL_R * WELL_R:
                removed.add(i)
                break
    for i, v in enumerate(verts):
        x, y, z = v
        if z <= 0.0:
            continue
        for wx, wy in wells:
            d2 = (x - wx) ** 2 + (y - wy) ** 2
            if d2 < WELL_R * WELL_R:
                d = math.sqrt(d2)
                if d > 1e-9:
                    s = WELL_R / d
                    verts[i] = (wx + (x - wx) * s, wy + (y - wy) * s, z)
                break
    return removed


# --- Ворота-тоннель (T2r-a2) --------------------------------------------------
# Всё строится на общей сетке стены и фасада: колонка k = азимут 2*pi*k/SEG,
# ряд = ROWS (стена) = OUT_ROWS (фасад) до OPEN_TOP. Поэтому проём — точный
# прямоугольник, а лоб тоннеля сваривается с клетками фасада без Т-точек.

def cut_opening(verts, faces):
    """Вырезает ворота из стены зала и из фасада: только проём.

    Грани строятся сеткой: грань ряда i и колонки k имеет индекс i*SEG + k
    (грань накрывает колонки k..k+1). Купол занимает первые len(ROWS)*SEG граней,
    боковины блока — следующие. Возвращает множество индексов удалённых граней.

    Ниша-дымоход (правка по ревью T2r-a2, решение ведущего 14.10.2026) наружу
    НЕ открывается: ряды фасада OPEN_ROW..NICHE_ROW в колонках |k| < NICHE_K
    остаются целыми и сами образуют глухую стенку кармана на плоскости
    x = BLOCK_X. Отдельные грани-заглушки не строятся намеренно:
      - в окне ворот (|y| <= GATE_FLAT_Y, z <= GATE_FLAT_Z) rock_point даёт
        OUT_DENT = 0, поэтому фасад там — ровно плоскость x = BLOCK_X, и клетки
        свариваются с боковинами и верхом ниши (build_gate) по общим вершинам;
      - любая новая грань на той же плоскости дала бы второй слой поверх
        существующего (z-fighting) либо шов по контуру окна.
    Замеры «ниша снаружи/изнутри» — в gate_probe (NICHE_BLIND).
    """
    removed = set()
    for i in range(OPEN_ROW):
        for k in range(-GATE_K, GATE_K):
            removed.add(i * SEG + (k % SEG))                  # проём в стене зала
            removed.add(CLIFF_FACE0 + i * SEG + (k % SEG))   # проём в фасаде
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


def build_gate(verts, faces, dome_rows, cliff_rows):
    """Проём, тоннель с пазом под решётку, перемычка и ниша-дымоход.

    dome_rows/cliff_rows — начала колец сетки стены зала и колец фасада (индекс
    вершины = начало кольца + колонка k; высоты до OPEN_TOP включительно совпадают).
    Возвращает границы групп граней для ориентации: (start_tunnel, start_niche, end).

    Топология: каждая новая грань сварена с уже построенной по общим вершинам
    (vput), поэтому лоб тоннеля, уступы и стенки ниши не дают ни щелей, ни
    Т-точек. Открытые рёбра (замер MANIFOLD: boundary = 54) остаются ровно там,
    где порода обрывается на проходе: порог и верх устья у фасада (x = BLOCK_X,
    z = 0 и z = OPEN_TOP), низ боковин у стены зала, низ и верх борозды.
    """
    cache = index_cache(verts)
    niche_x = (NICHE_BACK, GROOVE_X0 + GROOVE_W, BLOCK_X)
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
            row.append(cliff_rows[i] + col)
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


# --- Блок породы (T2r-a1) -----------------------------------------------------

def perimeter_ring():
    """Базовое кольцо пятна блока (прямоугольник ±BLOCK_X/±BLOCK_Y) по азимутам SEG.

    Углы квадрата попадают в точки кольца точно (SEG кратно 8), координаты
    прижимаются к боксу, чтобы габарит AABB был ровно ±8.0 (замер MESH не
    улетает за диаметр 16 м в level_check.gd). На грани +X в окне ворот
    колонки сдвинуты на y = R_REF*sin(phi) — чтобы совпасть с колонками стены
    (иначе лоб тоннеля не сварится с фасадом).
    """
    ring = []
    for i in range(SEG):
        phi = 2.0 * math.pi * i / SEG
        dx = math.cos(phi)
        dy = math.sin(phi)
        tx = BLOCK_X / abs(dx) if abs(dx) > 1e-12 else float("inf")
        ty = BLOCK_Y / abs(dy) if abs(dy) > 1e-12 else float("inf")
        t = min(tx, ty)
        x = min(BLOCK_X, max(-BLOCK_X, t * dx))
        y = min(BLOCK_Y, max(-BLOCK_Y, t * dy))
        if dx > 0.0 and x >= BLOCK_X - 1e-9:
            w = gate_blend(phi)
            if w > 0.0:
                y = y + (R_REF * dy - y) * w
        ring.append((x, y))
    return ring


def rock_noise(x, y, z):
    """Детерминированный шум [-1..1] для внешней скалы (другая частота, чем у стен)."""
    n = (math.sin(0.62 * x - 0.4) * math.cos(0.55 * y + 1.1)
         + 0.7 * math.sin(0.9 * y - 0.7 * z + 2.0)
         + 0.5 * math.sin(1.1 * z + 0.5 * x + 0.3)
         + 0.45 * math.sin(1.7 * x + 1.3 * y - 1.2))
    return n / (1.0 + 0.7 + 0.5 + 0.45)


def rock_point(x, y, z):
    """Внешняя вершина скалы: смещение внутрь по лучу из центра блока.

    Смещение только внутрь (d в [-OUT_DENT, 0]) — габарит AABB остаётся базовым
    боксом. В окне ворот (|y| <= GATE_FLAT_Y, z <= GATE_FLAT_Z) зубец скалы
    сглажен: лоб тоннеля и ниши должен быть плоскостью x = BLOCK_X, иначе клетки
    фасада не совпадут с ячейками свода. Затем радиальный кламп (только до высоты
    CLAMP_Z, где есть полость) держит породу не ближе OUT_R_MIN к оси — это и
    есть гарантия толщины SKIN.
    """
    cx = cy = 0.0
    cz = BLOCK_Z / 2.0
    vx = x - cx
    vy = y - cy
    vz = z - cz
    length = math.sqrt(vx * vx + vy * vy + vz * vz)
    flat = min(1.0 - smoothstep(GATE_FLAT_Y, GATE_FLAT_Y + 1.0, abs(y)),
               1.0 - smoothstep(GATE_FLAT_Z, GATE_FLAT_Z + 0.8, z))
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


def build_rock_tube(verts, faces, ring):
    """Боковины блока: замкнутая лента из кольца пятна (z=0, без смещения) вверх.

    Углы прямоугольника входят в кольцо, лента проходит через них без скоса.
    Возвращает список индексов начал колец (rows[0] — кольцо пятна, оно же
    внешнее кольцо плоскости пола).
    """
    rows = []
    for z in OUT_ROWS:
        base = len(verts)
        for i in range(SEG):
            x, y = ring[i]
            if z <= 0.0:
                verts.append((x, y, 0.0))
            else:
                verts.append(rock_point(x, y, z))
        rows.append(base)
    for k in range(len(rows) - 1):
        for i in range(SEG):
            i2 = (i + 1) % SEG
            faces.append([rows[k] + i, rows[k] + i2, rows[k + 1] + i2, rows[k + 1] + i])
    return rows


def build_rock_cap(verts, faces, rows, ring):
    """Верхняя крышка блока: концентрические кольца к центру + веер.

    Внешнее кольцо крышки — верхнее кольцо боковин (s=1, те же вершины),
    дальше кольца масштабируются к оси. Все вершины крышки выше полости
    (апекс 7.0, крышка не ниже BLOCK_Z - OUT_DENT), кламп не нужен.
    """
    prev = rows[-1]
    for s in CAP_SCALES:
        base = len(verts)
        for i in range(SEG):
            x, y = ring[i]
            verts.append(rock_point(x * s, y * s, BLOCK_Z))
        for i in range(SEG):
            i2 = (i + 1) % SEG
            faces.append([prev + i, prev + i2, base + i2, base + i])
        prev = base
    apex = len(verts)
    verts.append(rock_point(0.0, 0.0, BLOCK_Z))
    for i in range(SEG):
        i2 = (i + 1) % SEG
        faces.append([prev + i, prev + i2, apex])
    return len(faces)


def build_bottom(verts, faces, peri, dome_base):
    """Плоскость пола/дна блока: всё пятно, z=0, нормаль вверх (единая поверхность).

    Кольца снаружи внутрь: периметр (peri, тот же индекс-массив, что и у
    боковин — сварка без шва), кольцо основания купола (dome_base — те же
    вершины, что и полость: полость снизу закрыта, меш замкнут), затем кольца
    пола FLOOR_R к центру и веер.
    """
    rings = [dome_base]
    for j in range(FLOOR_RINGS - 1, 0, -1):
        r = FLOOR_R * j / FLOOR_RINGS
        base = len(verts)
        for k in range(SEG):
            phi = 2.0 * math.pi * k / SEG
            verts.append((r * math.cos(phi), r * math.sin(phi), 0.0))
        rings.append(base)
    # полоса «периметр → основание купола» (проходит под породой)
    for i in range(SEG):
        i2 = (i + 1) % SEG
        faces.append([peri + i, peri + i2, rings[0] + i2, rings[0] + i])
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
            if in_gate(exit_p[0], exit_p[1], exit_p[2], GATE_PASSAGE_MARGIN):
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

    # Глубина тоннеля: от плоскости фасада до стены зала. Лучи бьют по стенке
    # (y > OPEN_HALF): в проёме стены нет — там проход, и луч ушёл бы насквозь.
    # Борозда (y = GROOVE_INNER…OPEN_HALF) — паз в стенке, не проход.
    depths = []
    for yy in (OPEN_HALF + 0.05, 0.5 * (OPEN_HALF + NICHE_HALF)):
        for zz in (0.5, 2.5, 4.5):
            t = first((BLOCK_X - 0.05, yy, zz), (-1.0, 0.0, 0.0))
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
    x_niche = (NICHE_BACK + BLOCK_X) * 0.5
    y_niche = OPEN_HALF + 0.1
    t_niche_y = first((x_niche, 0.0, OPEN_TOP + 0.3), (0.0, 1.0, 0.0))
    t_niche_down = first((x_niche, y_niche, NICHE_TOP - 0.1), (0.0, 0.0, -1.0))
    t_niche_back = first((BLOCK_X - 0.05, 0.0, OPEN_TOP + 0.3), (-1.0, 0.0, 0.0))

    # --- Ниша глухая (правка по ревью T2r-a2) --------------------------------
    # Снаружи блока (x >= 10) луч в -X на высотах 5…8 м обязан упереться в
    # фасад x = BLOCK_X. Пока ниша была открыта, он проходил в альков и упирался
    # в заднюю стенку x = NICHE_BACK (= 7.40) — это и есть ассерт «снаружи нет
    # проёма». Высоты берём не на границах рядов OUT_ROWS, чтобы луч не скользил
    # по ребру клетки фасада.
    out_x = []
    for yy in (0.0, -1.0, 1.0, -2.0, 2.0):
        for zz in (OPEN_TOP + 0.1, 5.7, 6.3, 7.1, NICHE_TOP - 0.1):
            t = first((BLOCK_X + 2.0, yy, zz), (-1.0, 0.0, 0.0))
            out_x.append((BLOCK_X + 2.0 - t if t is not None else None, yy, zz))
    hits = [p[0] for p in out_x if p[0] is not None]
    # Стена кармана изнутри: луч из ниши в +X обязан упереться в фасад, иначе
    # ниша открыта наружу и свет из двора попадал бы внутрь.
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
    out["niche_cap_x"] = (BLOCK_X - x_niche) if t_cap is not None else None
    out["niche_slit_z"] = (NICHE_TOP - 0.1 - t_slit) if t_slit is not None else None
    return out


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
    """Геометрия блока с воротами + все замеры. Печатает GEOM…NICHE, возвращает замеры."""
    t = time.time()
    verts, faces, dome_rows = build_dome()
    dome_end = len(faces)
    ring = perimeter_ring()
    rows = build_rock_tube(verts, faces, ring)
    outer_end_tube = len(faces)
    build_rock_cap(verts, faces, rows, ring)
    outer_end = len(faces)
    build_bottom(verts, faces, rows[0], dome_rows[0])
    # Проём вырезается по сетке стены ДО сварки с фасадом: индексы граней
    # считаются как i*SEG + k, поэтому режем до любых других операций.
    removed = cut_opening(verts, faces)

    def kept_before(boundary):
        """Сколько граней осталось до исходного индекса boundary после выреза."""
        return sum(1 for i in range(boundary) if i not in removed)

    faces = [f for i, f in enumerate(faces) if i not in removed]
    dome_end = kept_before(dome_end)
    outer_end_tube = kept_before(outer_end_tube)
    outer_end = kept_before(outer_end)
    bottom_end = len(faces)
    gate_lo, gate_niche, gate_end = build_gate(verts, faces, dome_rows, rows)
    flipped = orient_block(verts, faces, dome_end, outer_end, bottom_end)
    flipped += orient_group(verts, faces, bottom_end, gate_niche,
                            ((X_FLAT + BLOCK_X) * 0.5, 0.0, OPEN_TOP * 0.5), True)
    flipped += orient_group(verts, faces, gate_niche, gate_end,
                            ((NICHE_BACK + BLOCK_X) * 0.5, 0.0,
                             (OPEN_TOP + NICHE_TOP) * 0.5), True)
    print("GEOM verts=%d faces=%d dome_faces=%d gate_faces=%d flipped=%d build_s=%.2f"
          % (len(verts), len(faces), dome_end, gate_end - gate_lo, flipped,
             time.time() - t))

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
        verts, faces, -BLOCK_X, BLOCK_X, -BLOCK_Y, BLOCK_Y, 0.1, 0.1, r_max=FLOOR_R)
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
          "tunnel_depth_min=%.3f (y=%.2f z=%.2f) tunnel_depth_max=%.3f facade_x=%.2f"
          % (g["width"][0], g["width"][1], g["height"], g["depth"][0],
             g["depth"][1], g["depth"][2], g["depth_max"], BLOCK_X))
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
    # Ниша глухая: каждый луч снаружи обязан остановиться на фасаде. Иначе
    # первым он встретит заднюю стенку кармана (NICHE_BACK < BLOCK_X) — это и
    # означало бы открытый наружу альков (Important 1 по ревью T2r-a2).
    ox = g["niche_out_x"]
    blind = (len(ox) == len(g["niche_out"]) and bool(ox)
             and max(abs(x - BLOCK_X) for x in ox) < 1e-3
             and g["niche_cap_x"] is not None)
    print("NICHE_BLIND outside_rays=%d/%d first_hit_x=[%.3f..%.3f] facade_x=%.2f "
          "cap_from_inside=%s slit_down_to_z=%s — %s"
          % (len(ox), len(g["niche_out"]), min(ox), max(ox), BLOCK_X,
             fmt_x(g["niche_cap_x"]), fmt_x(g["niche_slit_z"]),
             "ГЛУХАЯ" if blind else "ОТКРЫТА НАРУЖУ (ПРОВАЛ)"))

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
