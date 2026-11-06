"""Leitura de builds do Don't Starve Together (build.bin + atlas-0.tex) para peças PNG com pivô.
Uso como módulo: load_build(pasta) -> {simbolo: [(quadro, duracao, imagem RGBA, (pivo_x, pivo_y))]}
Uso na linha de comando: python3 klei_read.py <build.zip ou pasta extraida> <saida>
   (grava <simbolo>-<quadro>.png e .txt "pivo_x pivo_y duracao", o formato usado pelo pipeline)."""
import io, struct, sys, zipfile, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

def load_tex(path):
    b = Path(path).read_bytes(); h, = struct.unpack_from('<I', b, 4); mips = (h >> 13) & 31
    w, hh, pitch, size = struct.unpack_from('<HHHI', b, 8); off = 8 + 10 * mips
    dds = b'DDS ' + struct.pack('<7I', 124, 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000, hh, w, size, 0, 1) + b'\0' * 44
    dds += struct.pack('<2I4s5I', 32, 0x4, b'DXT5', 0, 0, 0, 0, 0) + struct.pack('<5I', 0x1000, 0, 0, 0, 0)
    im = Image.open(io.BytesIO(dds + b[off:off + size])); im.load()
    a = np.array(im.transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert('RGBA')).astype(np.float32)
    al = a[:, :, 3:4]; a[:, :, :3] = np.where(al > 0, np.clip(a[:, :, :3] * 255 / np.maximum(al, 1), 0, 255), 0)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')

def load_build(folder):
    folder = Path(folder)
    if folder.suffix == '.zip':
        tmp = Path(tempfile.mkdtemp()); zipfile.ZipFile(folder).extractall(tmp); folder = tmp
    b = (folder / 'build.bin').read_bytes(); o = [4]
    def u(fmt):
        v = struct.unpack_from(fmt, b, o[0]); o[0] += struct.calcsize(fmt); return v
    def s():
        n, = u('<I'); r = b[o[0]:o[0] + n].decode(); o[0] += n; return r
    _, ns, _ = u('<III'); s(); na, = u('<I'); [s() for _ in range(na)]
    syms = []
    for _ in range(ns):
        h, n = u('<II'); syms.append((h, [(u('<II'), u('<ffff'), u('<II')) for _ in range(n)]))
    nv, = u('<I'); V = [u('<ffffff') for _ in range(nv)]
    nh, = u('<I'); names = dict((u('<I')[0], s()) for _ in range(nh))
    atlas = load_tex(folder / 'atlas-0.tex'); W, H = atlas.size
    out = {}
    for h, frs in syms:
        lst = []
        for (num, dur), bb, (ai, ac) in frs:
            xs = [V[ai + i][0] for i in range(ac)]; ys = [V[ai + i][1] for i in range(ac)]
            x0, y0 = min(xs), min(ys)
            c = Image.new('RGBA', (max(1, round(max(xs) - x0)), max(1, round(max(ys) - y0))))
            for t in range(0, ac, 6):
                q = V[ai + t:ai + t + 6]; qx = [v[0] for v in q]; qy = [v[1] for v in q]; us = [v[3] for v in q]; vs = [v[4] for v in q]
                crop = atlas.crop((round(min(us) * W), round((1 - max(vs)) * H), round(max(us) * W), round((1 - min(vs)) * H)))
                crop = crop.resize((max(1, round(max(qx) - min(qx))), max(1, round(max(qy) - min(qy)))), Image.LANCZOS)
                c.alpha_composite(crop, (round(min(qx) - x0), round(min(qy) - y0)))
            lst.append((num, dur, c, (round(-x0), round(-y0))))
        out[names.get(h, hex(h))] = lst
    return out

def export(build, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    for k, v in load_build(build).items():
        for num, dur, im, p in v:
            im.save(out / f'{k}-{num}.png'); (out / f'{k}-{num}.txt').write_text(f'{p[0]} {p[1]} {dur}')

if __name__ == '__main__':
    export(sys.argv[1], sys.argv[2])
