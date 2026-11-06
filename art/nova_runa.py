"""0.12.0: Runa Eletrica com a arte nova do usuario (pedra-raio com gemas, corda e corrente) e Dagger menor.
Uso: python3 nova_runa.py <frente.png> <folha.png> <pasta de arte atual (v063)> <saida>
Gera os mesmos arquivos que art/gerar_arte.py (consumidos por art/compilar_anim.py)."""
import math, sys, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
FR, FOLHA, OLD, OUT = map(Path, sys.argv[1:5]); OUT.mkdir(parents=True, exist_ok=True)
INK = (24, 22, 26, 255); ROPE = (104, 70, 44, 255)
DAGGER_SCALE = 0.88                       # Dagger ~12% menor (pedido: "o minimo possivel")

def pieces(path):
    im = np.array(Image.open(path).convert('RGB')).astype(int)
    fg = ndimage.binary_fill_holes(ndimage.binary_closing(im.min(2) < 215, iterations=3))
    lab, k = ndimage.label(fg); sz = ndimage.sum(fg, lab, range(1, k + 1))
    objs = [(s, i + 1) for i, s in enumerate(ndimage.find_objects(lab)) if sz[i] > 2000]
    objs.sort(key=lambda o: (o[0][0].start // 200, o[0][1].start))
    out = []
    for s, l in objs:
        m = lab[s] == l; rgba = np.zeros(m.shape + (4,), np.uint8); rgba[..., :3] = im[s]
        L = im[s].min(2); a = np.where(m, 255, 0).astype(np.float32)
        edge = m & ~ndimage.binary_erosion(m, iterations=2)
        a[edge] = np.clip((245 - L[edge]) / 120.0, 0, 1) * 255          # borda sem halo branco
        rgba[..., 3] = a.astype(np.uint8); out.append(Image.fromarray(rgba))
    return out
front = pieces(FR)[0]
P = pieces(FOLHA)
side = P[2]; ground_src = P[9]

def fit(im, longest):
    s = longest / max(im.size); return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
def outline(im, px):
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0)
    grown = a.filter(ImageFilter.MaxFilter(2 * px + 1)); base = Image.new('RGBA', im.size, INK); base.putalpha(grown)
    return Image.alpha_composite(base, im)
def pad(im, p):
    c = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p)); c.paste(im, (p, p)); return c

# icone 64x64: desenha em 2x e reduz
big = outline(pad(fit(front.rotate(-32, resample=Image.BICUBIC, expand=True), 124), 6), 3); small = fit(big, 62)
icon = Image.new('RGBA', (64, 64)); icon.alpha_composite(small, ((64 - small.width) // 2, (64 - small.height) // 2))
icon.save(OUT / 'icon_blink_impeto.png')

def rope(d, pts, w=5):
    d.line(pts, fill=INK, width=w + 4, joint='curve')
    for x, y in pts: d.ellipse((x - (w + 4) / 2, y - (w + 4) / 2, x + (w + 4) / 2, y + (w + 4) / 2), fill=INK)
    d.line(pts, fill=ROPE, width=w, joint='curve')
    for x, y in pts: d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=ROPE)

def pendant_img(view, h, rot):
    src = front if view == 'front' else side
    p = fit(src, h)
    return p.rotate(-rot, resample=Image.BICUBIC, expand=True)

def frame(pendant=None, cords=(), arc=None):
    C = 160; S = 2 * C
    im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im); top = None
    if pendant:
        (px, py), rot, view, h = pendant
        p = pendant_img(view, h, rot)
        a = math.radians(rot); top = (C + px + math.sin(a) * h * 0.40, C + py - math.cos(a) * h * 0.40)
    for sx, sy in cords:
        rope(d, [(C + sx, C + sy), ((C + sx + top[0]) / 2, (C + sy + top[1]) / 2 + 3), top])
    if arc: rope(d, [(C + x, C + y) for x, y in arc])
    if pendant: im.alpha_composite(p, (round(C + px - p.width / 2), round(C + py - p.height / 2)))
    box = im.getbbox(); im = im.crop(box)
    return im, (C - box[0], C - box[1])

H_F, H_S = 92, 88
frames = {
    0: frame(((-1, 0), 0, 'front', H_F), [(-22, -80), (20, -80)]),
    1: frame(((-5, 3), -12, 'front', H_F), [(-31, -70), (8, -80)]),
    2: frame(((1, 4), 12, 'front', H_F), [(-11, -80), (36, -70)]),
    3: frame(((24, 4), 20, 'side', H_S), [(-16, -86)]),
    4: frame(((30, 16), 5, 'side', H_S), [(7, -84)]),
    5: frame(((24, -3), 30, 'side', H_S), [(-28, -84)]),
    6: frame(arc=[(-32, -58), (-15, -78), (15, -78), (32, -60)]),
    7: frame(arc=[(-44, -55), (-25, -80), (5, -84), (20, -70)]),
    8: frame(arc=[(-18, -70), (5, -82), (30, -78), (46, -50)]),
    14: frame(((-1, 22), 0, 'front', 98)),
    15: frame(arc=[(1, -63), (2, -30), (0, 4)]),
}
for n, (im, pv) in frames.items():
    im.save(OUT / f'impeto_torso_{n}.png'); (OUT / f'impeto_torso_{n}.txt').write_text(f'{pv[0]} {pv[1]}')

g = fit(ground_src, 105); g = g.crop(g.getbbox())
g.save(OUT / 'impeto_ground.png'); (OUT / 'impeto_ground.txt').write_text(f'{round(g.width * 0.55)} {round(g.height * 0.6)}')

# Dagger: mesma arte, menor (mao), pivo escalado junto
sw = Image.open(OLD / 'dagger_swap.png').convert('RGBA'); px, py = map(int, (OLD / 'dagger_swap.txt').read_text().split())
sw2 = sw.resize((round(sw.width * DAGGER_SCALE), round(sw.height * DAGGER_SCALE)), Image.LANCZOS)
sw2.save(OUT / 'dagger_swap.png'); (OUT / 'dagger_swap.txt').write_text(f'{round(px * DAGGER_SCALE)} {round(py * DAGGER_SCALE)}')
for f in ('dagger_ground.png', 'dagger_ground.txt', 'icon_blink_dagger.png'): shutil.copy(OLD / f, OUT / f)
print('ok dagger', sw.size, '->', sw2.size)
