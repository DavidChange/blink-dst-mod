"""Monta as pecas do BLINK a partir das folhas geradas por IA (arte do usuario).
Uso: python3 montar_ia.py <pasta das folhas> <pasta pecas base (gerar_corpo)> <saida>"""
import sys, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy import ndimage
SRC, BASE, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))

# ---------- recorte das folhas ----------
def pieces(name, rows):
    im = np.array(Image.open(SRC / f'{name}.jpg').convert('RGB')).astype(np.int32)
    fg = ndimage.binary_closing(im.min(2) < 225, iterations=2)
    fill = ndimage.binary_fill_holes(fg)
    lab, n = ndimage.label(fill); objs = ndimage.find_objects(lab)
    res = []
    for i, sl in enumerate(objs):
        if sl is None: continue
        m = lab[sl] == i + 1
        if m.sum() < 0.002 * fill.size: continue
        rgba = np.zeros(m.shape + (4,), np.uint8); rgba[..., :3] = im[sl]; rgba[..., 3] = m * 255
        # bordas: tira franja branca e suaviza
        a = rgba[..., 3].astype(np.float32); edge = m & ~ndimage.binary_erosion(m, iterations=1)
        white = edge & (im[sl].min(2) > 170); a[white] = 0
        rgba[..., 3] = a.astype(np.uint8)
        cy = (sl[0].start + sl[0].stop) / 2; cx = (sl[1].start + sl[1].stop) / 2
        res.append((int(cy // (im.shape[0] / rows)), cx, Image.fromarray(rgba, 'RGBA')))
    res.sort(key=lambda r: (r[0], r[1]))
    return [r[2] for r in res]

bald = pieces('f1_cabeca', 1)                 # frente, perfil (olha p/ direita), costas
hair = pieces('f2_cabelo', 2)                 # normal: frente, perfil, costas | achatado: idem
exp1 = pieces('f3_expr1', 4); exp2 = pieces('f4_expr2', 3)
prof = [ImageOps.mirror(p) for p in pieces('f5_perfis', 2)]   # gerados olhando p/ esquerda
cloth = pieces('f6_roupas', 2)
hair = [hair[0], ImageOps.mirror(hair[1]), hair[2], hair[3], ImageOps.mirror(hair[4]), hair[5]]
assert len(bald) == 3 and len(hair) == 6 and len(exp1) == 16 and len(exp2) == 12 and len(prof) == 4 and len(cloth) == 6

def A(im): return np.array(im).astype(np.float32)
def lum(a): return a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
def skin_mask(im):
    a = A(im); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (a[..., 3] > 128) & (r > 150) & (r > g + 10) & (g > b + 10)
def dark_mask(im):
    a = A(im); return (a[..., 3] > 128) & (lum(a) < 75)

# ---------- registro por sobreposicao (IoU) de mascaras ----------
def register(target, moving, smin=0.5, smax=2.0):
    """Acha escala s e deslocamento (dx,dy) que levam `moving` sobre `target` (mascaras bool)."""
    def small(m, k): return np.array(Image.fromarray(m.astype(np.uint8) * 255).resize((max(1, m.shape[1] // k), max(1, m.shape[0] // k)), Image.BILINEAR)) > 127
    k = 4; T = small(target, k); best = (-1, 1, 0, 0)
    tys, txs = np.nonzero(T); tc = (txs.mean(), tys.mean())
    for s in np.exp(np.linspace(np.log(smin), np.log(smax), 40)):
        M = small(moving, k); M = np.array(Image.fromarray(M.astype(np.uint8) * 255).resize((max(1, int(M.shape[1] * s)), max(1, int(M.shape[0] * s))), Image.NEAREST)) > 127
        mys, mxs = np.nonzero(M)
        if len(mxs) == 0: continue
        ox, oy = int(tc[0] - mxs.mean()), int(tc[1] - mys.mean())
        for dx in range(ox - 6, ox + 7, 2):
            for dy in range(oy - 6, oy + 7, 2):
                can = np.zeros_like(T)
                x0, y0 = max(0, dx), max(0, dy); x1, y1 = min(T.shape[1], dx + M.shape[1]), min(T.shape[0], dy + M.shape[0])
                if x1 <= x0 or y1 <= y0: continue
                can[y0:y1, x0:x1] = M[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
                iou = (can & T).sum() / max(1, (can | T).sum())
                if iou > best[0]: best = (iou, s, dx * k, dy * k)
    return best

def place(canvas_size, im, s, dx, dy):
    w, h = im.size; r = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    can = Image.new('RGBA', canvas_size); can.alpha_composite(r, (int(dx), int(dy)) if dx >= 0 and dy >= 0 else (0, 0)) if dx >= 0 and dy >= 0 else can.paste(r, (int(dx), int(dy)), r)
    return can

def warp(im, s, dx, dy, size):
    """Imagem `im` escalada por s e transladada (dx,dy) num canvas `size`."""
    w, h = im.size; r = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    can = Image.new('RGBA', size); can.paste(r, (int(round(dx)), int(round(dy))), r); return can

# ---------- cabeca: cabecas COMPLETAS desenhadas pela IA ----------
# frente = expressao neutra (folha 3); perfil = perfil neutro (folha 5); costas = cabeca de costas
# recortada do desenho de corpo inteiro (folha 0). O cabelo fica exatamente onde a IA desenhou.
def bbox(m): ys, xs = np.nonzero(m); return xs.min(), ys.min(), xs.max(), ys.max()
def back_head():
    im = np.array(Image.open(SRC / 'f0_corpo.jpg').convert('RGB')).astype(np.int32)
    H, W = im.shape[:2]; x0 = int(W * 0.66)
    fg = ndimage.binary_closing(im.min(2) < 225, iterations=2); fg[:, :x0] = False
    fill = ndimage.binary_fill_holes(fg)
    sk = (im[..., 0] > 150) & (im[..., 0] > im[..., 1] + 10) & (im[..., 1] > im[..., 2] + 10) & fill
    rows = np.nonzero(sk.any(1))[0]; nape = rows[rows < H * 0.45].max()   # fim da nuca (pele) acima do capuz
    fill[nape + 6:] = False
    lab, n = ndimage.label(fill); big = 1 + np.argmax(ndimage.sum(fill, lab, range(1, n + 1))); m = lab == big
    ys, xs = np.nonzero(m); sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    rgba = np.zeros(m[sl].shape + (4,), np.uint8); rgba[..., :3] = im[sl]; rgba[..., 3] = m[sl] * 255
    return Image.fromarray(rgba, 'RGBA')
PAD = 60
def padded(im):
    can = Image.new('RGBA', (im.width + 2 * PAD, im.height + 2 * PAD)); can.paste(im, (PAD, PAD), im); return can
HEAD = {0: padded(exp1[0]), 1: padded(prof[0]), 2: padded(back_head())}
def hair_mask_of(expr):
    d = dark_mask(expr); lab, n = ndimage.label(d)
    ids = set(np.unique(lab[: max(1, d.shape[0] // 3)])) - {0}
    return np.isin(lab, list(ids))
def hat_cut(head):
    """Versao para capacete: apara o topo do cabelo (fica escondido pelo chapeu)."""
    a = A(head); sk = skin_mask(head); x0, y0, x1, y1 = bbox(sk)
    cut = y0 + (y1 - y0) * 0.06
    Y = np.arange(a.shape[0])[:, None]
    hm = hair_mask_of(head) | (~sk & (Y < y0 + (y1 - y0) * 0.25) & (a[..., 3] > 0) & (lum(a) < 90))
    a[..., 3] = np.where(hm & (Y < cut), 0, a[..., 3])
    out = Image.fromarray(a.astype(np.uint8), 'RGBA'); d = ImageDraw.Draw(out)
    return out

# ---------- escala do jogo e pivos ----------
SKIN_W = 132.0     # largura da cabeca (orelha a orelha) em pixels do jogo; Wilson ~150 com cabelo maior
fsk = bbox(skin_mask(HEAD[0])); k = SKIN_W / (fsk[2] - fsk[0])
ksz = {0: k, 4: k}
# perfil e costas na mesma escala: compara a altura da pele (testa ao queixo) com a da frente
def skin_h(im): b = bbox(skin_mask(im)); return b[3] - b[1]
ksz[1] = k * skin_h(HEAD[0]) / skin_h(HEAD[1]) * 1.0
ksz[2] = k * (fsk[2] - fsk[0]) / (bbox(skin_mask(HEAD[2]))[2] - bbox(skin_mask(HEAD[2]))[0])
def head_pivot(head, view):
    sk = skin_mask(head); x0, y0, x1, y1 = bbox(sk)
    if view == 1:
        low = sk.copy(); low[: int(y1 - (y1 - y0) * 0.25)] = False; xs = np.nonzero(low)[1]
        return (xs.mean(), y1 - (y1 - y0) * 0.12)
    return ((x0 + x1) / 2, y1 - (y1 - y0) * 0.12)
PV = {v: head_pivot(HEAD[v], v) for v in (0, 1, 2)}
def to_game(im, pivot_src, kk):
    w, h = im.size; r = im.resize((max(1, round(w * kk)), max(1, round(h * kk))), Image.LANCZOS)
    box = r.getbbox(); r = r.crop(box)
    return r, (round(pivot_src[0] * kk - box[0]), round(pivot_src[1] * kk - box[1]))
frames = {}
def put(sym, num, im, pivot, dur=1): frames.setdefault(sym, []).append((num, dur, im, pivot))
EMPTY = (Image.new('RGBA', (2, 2)), (1, 1))
view_of = {0: 0, 1: 1, 2: 2, 4: 0}
for n in (0, 1, 2, 4):
    v = view_of[n]
    im, p = to_game(HEAD[v], PV[v], ksz[v]); put('headbase', n, im, p)
    im, p = to_game(hat_cut(HEAD[v]), PV[v], ksz[v]); put('headbase_hat', n, im, p)
for sym in ('headbase', 'headbase_hat'):   # caveira (raio-x do choque): mantida do molde
    q = BASE / f'{sym}-3.png'; px, py, d = map(int, q.with_suffix('.txt').read_text().split())
    put(sym, 3, Image.open(q).convert('RGBA'), (px, py))
for n in range(4):                           # o cabelo ja faz parte da cabeca
    put('hair', n, *EMPTY); put('hair_hat', n, *EMPTY)

# ---------- rostos: recortes alinhados sobre a cabeca neutra ----------
DELTA = {0: (5.4, -63.2), 1: (43.8, -63.2)}   # pivo do rosto - pivo da cabeca (animacao do jogo)
def align(expr, head):
    iou, s, dx, dy = register(A(head)[..., 3] > 128, A(expr)[..., 3] > 128, 0.85, 1.18)
    return warp(expr, s, dx, dy, head.size), iou
def face_patch(expr, view):
    head = HEAD[view]; reg, iou = align(expr, head)
    a = A(reg); al = a[..., 3] > 128
    sk_head = skin_mask(head); x0, y0, x1, y1 = bbox(sk_head); w = x1 - x0
    inside = ndimage.binary_erosion(ndimage.binary_fill_holes(al), iterations=6)
    mask = inside & ~ndimage.binary_dilation(hair_mask_of(reg), iterations=3)
    X = np.arange(mask.shape[1])[None, :]; Y = np.arange(mask.shape[0])[:, None]
    if view == 0: mask &= (X > x0 + w * 0.14) & (X < x1 - w * 0.14)
    else:
        ear = bbox(sk_head)[0] + w * 0.30; mask &= (X > ear)
    soft = ndimage.gaussian_filter(mask.astype(np.float32), 1.5 if view == 0 else 4.0) * 255
    a[..., 3] = np.minimum(a[..., 3], soft)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    im, p = to_game(out, PV[view], ksz[view])
    d = DELTA[view]
    return im, (round(p[0] + d[0]), round(p[1] + d[1])), iou
MAP = {0: exp1[0], 1: exp1[0], 2: exp1[1], 3: exp1[0], 8: exp1[2], 9: exp1[3], 10: exp1[4], 11: exp1[5],
       12: exp1[6], 13: exp1[7], 15: exp1[8], 16: exp1[9], 17: exp1[10], 18: exp1[11], 19: exp1[12],
       20: exp1[13], 21: exp1[14], 22: exp1[15], 23: exp2[0], 24: exp2[1], 25: exp2[2], 26: exp2[3],
       27: exp2[4], 28: exp2[5], 29: exp2[6], 30: exp2[7], 31: exp2[8], 32: exp2[9]}
PMAP = {4: prof[0], 5: prof[1], 6: prof[2], 7: prof[3]}
ious = []
for n in range(33):
    if n == 14:
        q = BASE / 'face-14.png'; px, py, d = map(int, q.with_suffix('.txt').read_text().split())
        put('face', 14, Image.open(q).convert('RGBA'), (px, py)); continue
    im, p, iou = face_patch(PMAP[n], 1) if n in PMAP else face_patch(MAP[n], 0)
    ious.append(round(iou, 2)); put('face', n, im, p)
print('alinhamento dos rostos (IoU) min/med', min(ious), sorted(ious)[len(ious) // 2])

# ---------- tronco e cintura (roupas da folha 6) nos quadros do molde ----------
def fit_cloth(piece, ref_path, widen, align):
    ref = Image.open(ref_path).convert('RGBA'); px, py, d = map(int, ref_path.with_suffix('.txt').read_text().split())
    rb = ref.getbbox(); rw, rh = rb[2] - rb[0], rb[3] - rb[1]
    s = rw * widen / piece.width; im = piece.resize((round(piece.width * s), round(piece.height * s)), Image.LANCZOS)
    cx = (rb[0] + rb[2]) / 2
    if align == 'bottom': ox, oy = cx - im.width / 2, rb[3] - im.height + rh * 0.12
    else: ox, oy = cx - im.width / 2, rb[1] - rh * 0.05
    return im, (round(px - ox), round(py - oy))
def no_patch(im):   # remove o remendo em X das costas (claro e pequeno)
    a = A(im); m = (lum(a) > 170) & (a[..., 3] > 0); a[..., :3] = np.where(m[..., None], np.array([72, 70, 72]), a[..., :3])
    return Image.fromarray(a.astype(np.uint8), 'RGBA')
torso_src = {0: cloth[0], 1: cloth[0], 2: cloth[0], 3: ImageOps.mirror(cloth[1]), 4: ImageOps.mirror(cloth[1]), 5: ImageOps.mirror(cloth[1]),
             6: no_patch(cloth[2]), 7: no_patch(cloth[2]), 8: no_patch(cloth[2])}
pelv_src = {0: cloth[3], 1: cloth[3], 2: cloth[3], 3: ImageOps.mirror(cloth[4]), 4: ImageOps.mirror(cloth[4]), 5: ImageOps.mirror(cloth[4]),
            6: cloth[5], 7: cloth[5], 8: cloth[5]}
for n in range(11):
    if n in torso_src:
        im, p = fit_cloth(torso_src[n], BASE / f'torso-{n}.png', 1.25, 'bottom'); put('torso', n, im, p)
        im, p = fit_cloth(pelv_src[n], BASE / f'torso_pelvis-{n}.png', 1.15, 'top'); put('torso_pelvis', n, im, p)
    else:
        for sym in ('torso', 'torso_pelvis'):
            q = BASE / f'{sym}-{n}.png'; px, py, d = map(int, q.with_suffix('.txt').read_text().split())
            put(sym, n, Image.open(q).convert('RGBA'), (px, py))

# ---------- demais pecas: do molde ja gerado (bracos, maos, pernas, pes, bochechas) ----------
done = set(frames)
for q in sorted(BASE.glob('*.png')):
    sym, num = q.stem.rsplit('-', 1)
    if sym in done: continue
    px, py, d = map(int, q.with_suffix('.txt').read_text().split())
    put(sym, int(num), Image.open(q).convert('RGBA'), (px, py), d)
man = []
for sym, frs in frames.items():
    for num, dur, im, p in frs:
        im.save(OUT / f'{sym}-{num}.png'); (OUT / f'{sym}-{num}.txt').write_text(f'{p[0]} {p[1]} {dur}')
    man.append(sym)
(OUT / 'manifesto.txt').write_text('\n'.join(man) + '\n')
print('ok', len(man), 'simbolos')
