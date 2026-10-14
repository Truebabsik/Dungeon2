"""Даунскейл текстур glb до заданной max-стороны (задача T2r-c, основа скилла).

Только текстуры: импорт glb -> масштабирование bpy.data.images с max-стороной
> MAX_SIZE пропорционально до MAX_SIZE -> экспорт GLB. Геометрия не трогается
(никакого декимейта, пересчёта нормалей) — поэтому тр. до/после обязаны совпасть,
скрипт печатает оба числа и сверяет их.

Запуск (headless, аргументы скрипта после "--"):
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python game/tools/glb_texture_downscale.py -- \
      [--max 1024] [--out-dir DIR] [--suffix _1024] [--out FILE.glb] вх1.glb [вх2.glb ...]

Пути вход/выход — параметры:
  по умолчанию итог кладётся рядом с исходником как <stem><suffix>.glb;
  --out-dir меняет папку вывода, --out задаёт итоговый файл явно (ровно 1 вход);
  --suffix "" (пусто) и --out-dir != папка входа — тоже валидный вариант.
"""

import argparse
import json
import os
import struct
import sys

import bpy

# Пути/файлы ниже не захардкожены — берутся из аргументов после "--".


def parse_args():
	argv = sys.argv
	argv = argv[argv.index("--") + 1:] if "--" in argv else []
	p = argparse.ArgumentParser(
		description="Downscale glb textures to --max px on the longest side.")
	p.add_argument("inputs", nargs="+", help="пути к исходным .glb (читаются только чтением)")
	p.add_argument("--max", type=int, default=1024,
		help="целевая max-сторона текстуры (по умолчанию 1024)")
	p.add_argument("--out-dir", default=None,
		help="папка итогов (по умолчанию — папка исходника)")
	p.add_argument("--suffix", default="_1024",
		help="суффикс имени итога (по умолчанию _1024)")
	p.add_argument("--out", default=None,
		help="итоговый файл явно (только при одном входе)")
	return p.parse_args(argv)


def out_path_for(src, args):
	if args.out:
		return os.path.abspath(args.out)
	d = args.out_dir if args.out_dir else os.path.dirname(os.path.abspath(src))
	stem = os.path.splitext(os.path.basename(src))[0]
	return os.path.join(os.path.abspath(d), stem + args.suffix + ".glb")


def glb_triangle_stats(path):
	"""Треугольники и общий размер из байтов glb (парсер JSON-чанка, без Blender).

	Возвращает (tris, non_triangle_prims). Считает одинаково для исходника и итога,
	поэтому сравнение «до/после» — один и тот же метод на байтах файла.
	"""
	with open(path, "rb") as f:
		data = f.read()
	magic, _version, _length = struct.unpack_from("<III", data, 0)
	if magic != 0x46546C67:
		raise ValueError("%s: не glb (magic=0x%08X)" % (path, magic))
	chunk_len, chunk_type = struct.unpack_from("<II", data, 12)
	if chunk_type != 0x4E4F534A:  # 'JSON'
		raise ValueError("%s: первый чанк не JSON" % path)
	g = json.loads(data[20:20 + chunk_len].decode("utf-8"))
	tris = 0
	non_tri = 0
	for mesh in g.get("meshes", []):
		for prim in mesh.get("primitives", []):
			mode = prim.get("mode", 4)  # 4 = TRIANGLES (по умолчанию в glTF)
			acc_i = prim.get("indices")
			if acc_i is not None:
				count = g["accessors"][acc_i]["count"]
			else:
				count = g["accessors"][prim["attributes"]["POSITION"]]["count"]
			if mode == 4:
				if count % 3 != 0:
					raise ValueError("%s: индексов/вершин не кратно 3 (%d)" % (path, count))
				tris += count // 3
			else:
				# STRIP/FAN/LINE/POINT — в этих моделях не ожидаются, но считаем честно.
				non_tri += max(0, count - 2) if mode in (5, 6) else count
	return tris, non_tri


def scene_triangle_count():
	"""Треугольники по loop-triangles уникальных мешей сцены (кросс-чек импорта)."""
	total = 0
	seen = set()
	for ob in bpy.data.objects:
		if ob.type != 'MESH':
			continue
		me = ob.data
		if me.name in seen:
			continue
		seen.add(me.name)
		me.calc_loop_triangles()
		total += len(me.loop_triangles)
	return total


def texture_images():
	"""(имя, w, h, packed) по bpy.data.images, кроме служебных узлов рендера."""
	out = []
	for img in bpy.data.images:
		if img.name in ("Render Result", "Viewer Node"):
			continue
		w, h = img.size[0], img.size[1]
		if w <= 0 or h <= 0:
			continue
		out.append((img, w, h))
	return out


def process(src, args):
	dst = out_path_for(src, args)
	print("=== SRC: %s" % os.path.abspath(src))
	print("DST: %s" % dst)
	if not os.path.isfile(src):
		raise FileNotFoundError(src)

	size_before = os.path.getsize(src)
	tris_before, non_tri_before = glb_triangle_stats(src)

	bpy.ops.wm.read_factory_settings(use_empty=True)
	bpy.ops.import_scene.gltf(filepath=os.path.abspath(src))

	print("IMAGES BEFORE:")
	imgs = texture_images()
	for img, w, h in imgs:
		print("    %s (%d, %d)%s" % (img.name, w, h, " packed" if img.packed_file else ""))

	print("SCALED:")
	scaled = 0
	for img, w, h in imgs:
		if max(w, h) <= args.max:
			continue
		if w >= h:
			nw, nh = args.max, max(1, int(round(h * args.max / w)))
		else:
			nw, nh = max(1, int(round(w * args.max / h))), args.max
		img.scale(nw, nh)
		print("    %s (%d, %d) -> (%d, %d)" % (img.name, w, h, img.size[0], img.size[1]))
		scaled += 1
	print("SCALED COUNT: %d; UNCHANGED (<= %d): %d" % (scaled, args.max, len(imgs) - scaled))

	tris_import = scene_triangle_count()

	os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
	bpy.ops.export_scene.gltf(
		filepath=dst,
		export_format='GLB',
		export_image_format='AUTO',
		export_apply=True,
		export_yup=True,
	)

	tris_after, non_tri_after = glb_triangle_stats(dst)
	size_after = os.path.getsize(dst)

	print("TRIS (glb bytes before): %d (non-tri prims: %d)" % (tris_before, non_tri_before))
	print("TRIS (blender import):    %d" % tris_import)
	print("TRIS (glb bytes after):   %d (non-tri prims: %d)" % (tris_after, non_tri_after))
	print("SIZE before: %d" % size_before)
	print("SIZE after:  %d" % size_after)
	if tris_before != tris_after:
		print("ERROR: тр. до != после — геометрия изменилась!")
		return False
	if non_tri_before != non_tri_after:
		print("ERROR: не-треугольные примитивы до != после!")
		return False
	return True


def main():
	args = parse_args()
	if args.out and len(args.inputs) != 1:
		print("ERROR: --out допустим только с одним входным файлом")
		sys.exit(2)
	if args.max <= 0:
		print("ERROR: --max должен быть > 0")
		sys.exit(2)

	ok = True
	for src in args.inputs:
		try:
			if not process(src, args):
				ok = False
		except SystemExit:
			raise
		except Exception as e:  # не прерываем пакет: остальные файлы всё равно обработать
			ok = False
			print("ERROR: %s: %r" % (src, e))
	print("DONE: %s" % ("OK" if ok else "FAILURES"))
	sys.exit(0 if ok else 1)


main()
