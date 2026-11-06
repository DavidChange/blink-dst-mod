"""Monta as pecas do BLINK (arte nova, estilo Don't Starve) a partir das folhas geradas por IA.
Uso: python3 montar_v2.py <pasta folhas> <pecas base antigas (molde recolorido)> <molde wilson> <molde wolfgang> <saida>
Folhas: f1_cabecas (frente, perfil p/ esquerda, costas), f2_expr e f3_expr (12 rostos de frente cada),
f4_perfis (6 perfis p/ direita), f5_pecas (tronco x3, cintura x3, braco/antebraco/maos x5, pernas x2, botas x3)."""
import sys, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage
SRC, BASE, WIL, WOLF, OUT = map(Path, sys.argv[1:6])
OUT.mkdir(parents=True, exist_ok=True)

def A(im): return np.array(im).astype(np.float32)
def lum(a): return a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
def bbox(m): ys, xs = np.nonzero(m); return xs.min(), ys.min(), xs.max(), ys.max()

# ---------- recorte das folhas (fundo branco) ----------
def pieces(name, min_frac=0.0015):
    im = np.array(Image.open(SRC / f'{name}.jpg').convert('RGB')).astype(np.int32)
    fg = ndimage.binary_closing(im.min(2) < 222, iterations=2)
    fill = ndimage.binary_fill_holes(fg)
    lab, n = ndimage.label(fill); objs = ndimage.find_objects(lab)
    res = []
    for i, sl in enumerate(objs):
        if sl is None: continue
        m = lab[sl] == i + 1
        if m.sum() < min_frac * fill.size: continue
        sub = im[sl]
        # 0.9.3: bolsoes de fundo branco presos entre as pontas do cabelo (fechados pelo preenchimento)
        for _ in range(2):
            white = m & (sub.min(2) > 232)
            near_out = ndimage.binary_dilation(~m, iterations=6)
            wl, wn = ndimage.label(white)
            touch = np.unique(wl[near_out & white]); m = m & ~np.isin(wl, touch[touch > 0])
            lab2, n2 = ndimage.label(m)
            if n2 > 1: m = lab2 == 1 + np.argmax(ndimage.sum(m, lab2, range(1, n2 + 1)))
        rgba = np.zeros(m.shape + (4,), np.uint8); rgba[..., :3] = sub; rgba[..., 3] = m * 255
        # borda externa: o contorno do desenho e nanquim; pixels misturados com o branco do fundo viram
        # nanquim com transparencia proporcional (sem halo branco)
        band = m & ~ndimage.binary_erosion(m, iterations=3)
        L = sub[..., 0] * .3 + sub[..., 1] * .59 + sub[..., 2] * .11
        al = np.clip((235.0 - L) / (235.0 - 70.0), 0, 1)
        rgba[..., 3] = np.where(band, (al * 255).astype(np.uint8), rgba[..., 3])
        rgba[..., :3] = np.where(band[..., None], np.array([24, 22, 26], np.uint8), rgba[..., :3])
        res.append(((sl[0].start + sl[0].stop) / 2, (sl[1].start + sl[1].stop) / 2, Image.fromarray(rgba, 'RGBA')))
    res.sort(key=lambda r: r[0])                                 # agrupa em linhas pelo centro vertical
    rows, cur = [], [res[0]]
    for r in res[1:]:
        if r[0] - cur[-1][0] > 90: rows.append(cur); cur = [r]
        else: cur.append(r)
    rows.append(cur)
    return [[r[2] for r in sorted(row, key=lambda r: r[1])] for row in rows]
flat = lambda rows: [p for r in rows for p in r]

heads = flat(pieces('f1_cabecas'))
ex2 = flat(pieces('f2_expr')); ex3 = flat(pieces('f3_expr')); prof = flat(pieces('f4_perfis'))
parts = pieces('f5_pecas')
assert len(heads) == 3 and len(ex2) == 12 and len(ex3) == 12 and len(prof) == 6, (len(heads), len(ex2), len(ex3), len(prof))
assert [len(r) for r in parts] == [3, 3, 5, 5], [len(r) for r in parts]

def pale(im):
    a = A(im); return (a[..., 3] > 128) & (lum(a) > 165)
def dark(im):
    a = A(im); return (a[..., 3] > 128) & (lum(a) < 80)

# ---------- registro por sobreposicao (IoU) ----------
def register(target, moving, smin=0.85, smax=1.18):
    def small(m, k): return np.array(Image.fromarray(m.astype(np.uint8) * 255).resize((max(1, m.shape[1] // k), max(1, m.shape[0] // k)), Image.BILINEAR)) > 127
    k = 4; T = small(target, k); best = (-1, 1, 0, 0)
    tys, txs = np.nonzero(T); tc = (txs.mean(), tys.mean())
    for s in np.exp(np.linspace(np.log(smin), np.log(smax), 30)):
        M = small(moving, k); M = np.array(Image.fromarray(M.astype(np.uint8) * 255).resize((max(1, int(M.shape[1] * s)), max(1, int(M.shape[0] * s))), Image.NEAREST)) > 127
        mys, mxs = np.nonzero(M)
        ox, oy = int(tc[0] - mxs.mean()), int(tc[1] - mys.mean())
        for dx in range(ox - 4, ox + 5):
            for dy in range(oy - 4, oy + 5):
                can = np.zeros_like(T)
                x0, y0 = max(0, dx), max(0, dy); x1, y1 = min(T.shape[1], dx + M.shape[1]), min(T.shape[0], dy + M.shape[0])
                if x1 <= x0 or y1 <= y0: continue
                can[y0:y1, x0:x1] = M[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
                iou = (can & T).sum() / max(1, (can | T).sum())
                if iou > best[0]: best = (iou, s, dx * k, dy * k)
    return best
def warp(im, s, dx, dy, size):
    w, h = im.size; r = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    can = Image.new('RGBA', size); can.paste(r, (int(round(dx)), int(round(dy))), r); return can

PAD = 110
def padded(im):
    can = Image.new('RGBA', (im.width + 2 * PAD, im.height + 2 * PAD)); can.paste(im, (PAD, PAD), im); return can
HEAD = {0: padded(ex2[0]), 1: padded(prof[0]), 2: padded(heads[2])}

# ---------- escala e pivos ----------
import os
SKIN_W = 132.0 * float(os.environ.get('HEAD', '1.09'))   # orelha a orelha (px do jogo); tamanho da 0.9.2 (aprovado), agora medido nas orelhas de verdade
def face_comp(im):
    """Interior do rosto: maior area clara + buracos (olhos, boca, sobrancelhas)."""
    p = pale(im); lab, n = ndimage.label(p)
    big = 1 + np.argmax(ndimage.sum(p, lab, range(1, n + 1)))
    return lab == big
fb = bbox(pale(HEAD[0])); k0 = SKIN_W / (fb[2] - fb[0])
ab = lambda im: bbox(A(im)[..., 3] > 128)
h_front = ab(HEAD[0])[3] - ab(HEAD[0])[1]
# perfil: mesma altura cabelo->ponta do cavanhaque; costas: mesma largura do cabelo que a frente da folha 1
KS = {0: k0, 1: k0 * h_front / (ab(HEAD[1])[3] - ab(HEAD[1])[1])}
f1f = padded(heads[0]); KS[2] = k0 * (ab(HEAD[0])[2] - ab(HEAD[0])[0]) / (ab(f1f)[2] - ab(f1f)[0])
fc = face_comp(HEAD[0]); cb = bbox(fc)
# 0.9.3: o rosto de frente da IA tem o queixo deslocado para o lado (cabeca 'torta'). Corrige com um
# cisalhamento horizontal: olhos ficam onde estao e o queixo vem para baixo do meio dos olhos.
def eyes_and_chin(im):
    f = face_comp(im); fl = ndimage.binary_fill_holes(f); dk = (fl & ~f) & (lum(A(im)) < 70)
    lab, n = ndimage.label(dk); sz = ndimage.sum(dk, lab, range(1, n + 1)); idx = np.argsort(sz)[::-1][:2] + 1
    cs = [ndimage.center_of_mass(lab == i) for i in idx]
    ys, xs = np.nonzero(fl); cy = ys.max(); cx = xs[ys >= cy - 3].mean()
    return (cs[0][1] + cs[1][1]) / 2, (cs[0][0] + cs[1][0]) / 2, cx, cy
EX, EY, CX, CY = eyes_and_chin(HEAD[0]); SHK = (CX - EX) / (CY - EY)
print('cisalhamento frente k=%.3f (queixo %.0f px fora do meio dos olhos)' % (SHK, CX - EX))
def shear0(im):
    return im.transform(im.size, Image.AFFINE, (1, SHK, -SHK * EY, 0, 1, 0), resample=Image.BICUBIC)
piv_front = (EX, cb[3] - (cb[3] - cb[1]) * 0.12)
top_to_piv = (piv_front[1] - ab(HEAD[0])[1]) * k0           # em pixels do jogo
def pivot(view):
    if view == 0: return piv_front
    im = HEAD[view]; b = ab(im); py = b[1] + top_to_piv / KS[view]
    if view == 1:
        f = face_comp(im); xs = np.nonzero(f[int(py) - 10:int(py) + 10])[1]
        return (xs.mean() if len(xs) else (b[0] + b[2]) / 2, py)
    return ((b[0] + b[2]) / 2, py)
PV = {v: pivot(v) for v in (0, 1, 2)}
def to_game(im, pv, kk, view=None):
    if view == 0: im = shear0(im)
    w, h = im.size; r = im.resize((max(1, round(w * kk)), max(1, round(h * kk))), Image.LANCZOS)
    box = r.getbbox(); r = r.crop(box)
    return r, (round(pv[0] * kk - box[0]), round(pv[1] * kk - box[1]))

frames = {}
def put(sym, num, im, pivot, dur=1): frames.setdefault(sym, []).append((num, dur, im, pivot))
def keep(sym, num, folder):
    q = folder / f'{sym}-{num}.png'; px, py, d = map(int, q.with_suffix('.txt').read_text().split()[:3])
    put(sym, num, Image.open(q).convert('RGBA'), (px, py), d)
EMPTY = (Image.new('RGBA', (2, 2)), (1, 1))

def hat_cut(head, view):
    """Para chapeus: corta tudo acima da linha da testa (o chapeu cobre). A linha fica na mesma altura
    (em relacao ao pivo do queixo) nas 3 vistas, medida na testa da vista de frente."""
    a = A(head); Y = np.arange(a.shape[0])[:, None]
    cut = PV[view][1] - HAT_ABOVE / KS[view]
    a[..., 3] = np.where(Y < cut, 0, a[..., 3])
    out = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return out
HAT_ABOVE = (PV[0][1] - (bbox(face_comp(HEAD[0]))[1] + 4)) * KS[0]
for n, v in ((0, 0), (1, 1), (2, 2), (4, 0)):
    im, p = to_game(HEAD[v], PV[v], KS[v], v); put('headbase', n, im, p)
    im, p = to_game(hat_cut(HEAD[v], v), PV[v], KS[v], v); put('headbase_hat', n, im, p)
for sym in ('headbase', 'headbase_hat'): keep(sym, 3, WIL)        # caveira do choque: original do jogo
for n in range(4): put('hair', n, *EMPTY); put('hair_hat', n, *EMPTY)

# ---------- rostos: interior do rosto de cada expressao, alinhado sobre a cabeca base ----------
DELTA = {0: (5.4, -63.2), 1: (43.8, -63.2)}
def face_patch(expr, view):
    head = HEAD[view]
    iou, s, dx, dy = register(A(head)[..., 3] > 128, A(padded(expr))[..., 3] > 128)
    reg = warp(padded(expr), s, dx, dy, head.size)
    a = A(reg); al = a[..., 3] > 128
    region = face_comp(reg) | face_comp(head)
    region = ndimage.binary_fill_holes(ndimage.binary_closing(region, iterations=6)) & al
    region = ndimage.binary_dilation(region, iterations=1) & al
    soft = ndimage.gaussian_filter(region.astype(np.float32), 1.2) * 255
    a[..., 3] = np.minimum(a[..., 3], soft)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    im, p = to_game(out, PV[view], KS[view], view); d = DELTA[view]
    return im, (round(p[0] + d[0]), round(p[1] + d[1])), iou, out
a2, a3 = ex2, ex3
MAP = {0: a2[0], 1: a2[0], 2: a2[1], 3: a2[0], 8: a2[3], 9: a2[4], 10: a2[4], 11: a2[2], 12: a2[8], 13: a3[7],
       15: a2[5], 16: a2[9], 17: a2[2], 18: a2[11], 19: a2[10], 20: a2[9], 21: a3[2], 22: a3[11], 23: a3[1],
       24: a2[7], 25: a3[3], 26: a3[5], 27: a3[9], 28: a3[8], 29: a3[0], 30: a2[6], 31: a3[6], 32: a3[4]}
PMAP = {4: prof[0], 5: prof[1], 6: prof[2], 7: prof[3]}
ious, checks = [], []
for n in range(33):
    if n == 14: put('face', 14, *EMPTY); continue
    im, p, iou, full = face_patch(PMAP[n], 1) if n in PMAP else face_patch(MAP[n], 0)
    ious.append(round(iou, 2)); put('face', n, im, p); checks.append((n, full))
print('alinhamento dos rostos (IoU) min/med', min(ious), sorted(ious)[len(ious) // 2])

# ---------- corpo: pecas da folha 5 encaixadas nos quadros molde do jogo ----------
def load(folder, sym, num):
    q = folder / f'{sym}-{num}.png'; px, py, d = map(int, q.with_suffix('.txt').read_text().split()[:3])
    return Image.open(q).convert('RGBA'), (px, py), d
def axis(im, ref=None):
    """Eixo principal (unitario), centro, comprimento. Sentido: de `ref` (ponto de encaixe) para longe."""
    ys, xs = np.nonzero(A(im)[..., 3] > 100); P = np.stack([xs, ys], 1).astype(float); c = P.mean(0)
    w, v = np.linalg.eigh(np.cov((P - c).T)); u = v[:, 1]
    if ref is None: ref = (c[0], -1e9)                          # peca da folha: encaixe no topo
    if np.dot(c - np.array(ref), u) < 0: u = -u
    pr = (P - c) @ u
    return u, c, pr.max() - pr.min()
def crop_bracer(im):
    """Tira a bracadeira do topo da mao (ela ja esta no antebraco)."""
    a = A(im); al = a[..., 3] > 100; dk = al & (lum(a) < 90)
    ratio = dk.sum(1) / np.maximum(1, al.sum(1)); ys = np.nonzero(al.any(1))[0]; y0, y1 = ys.min(), ys.max()
    rows = [y for y in range(y0, int(y0 + (y1 - y0) * 0.65)) if ratio[y] > 0.45]
    cut = (max(rows) + 2) if rows else y0
    c = im.crop((0, cut, im.width, im.height)); return c.crop(c.getbbox())
def fit_axis(piece, sym, num, folder, scale=1.0, by_area=False):
    tim, tpv, d = load(folder, sym, num)
    if tim.getbbox() is None: return EMPTY[0], EMPTY[1], d
    tu, tc, tl = axis(tim, tpv); pu, pc, pl = axis(piece)
    ang = math.degrees(math.atan2(pu[1], pu[0]) - math.atan2(tu[1], tu[0]))
    s = (math.sqrt((A(tim)[..., 3] > 100).sum() / max(1, (A(piece)[..., 3] > 100).sum())) if by_area else tl / pl) * scale
    r = piece.resize((max(1, round(piece.width * s)), max(1, round(piece.height * s))), Image.LANCZOS)
    r = r.rotate(ang, resample=Image.BICUBIC, expand=True)
    box = r.getbbox(); r = r.crop(box)
    _, rc, _ = axis(r)
    ox, oy = tc[0] - rc[0], tc[1] - rc[1]                      # centro da peca sobre o centro do molde
    return r, (round(tpv[0] - ox), round(tpv[1] - oy)), d
def fit_box(piece, sym, num, folder, widen, align, hfit=0.5):
    tim, tpv, d = load(folder, sym, num); rb = tim.getbbox(); rw, rh = rb[2] - rb[0], rb[3] - rb[1]
    sw = rw * widen / piece.width; sh = rh / piece.height; s = sw ** (1 - hfit) * sh ** hfit
    im = piece.resize((round(piece.width * s), round(piece.height * s)), Image.LANCZOS)
    cx = (rb[0] + rb[2]) / 2
    if align == 'bottom': ox, oy = cx - im.width / 2, rb[3] - im.height - rh * 0.10
    elif align == 'top': ox, oy = cx - im.width / 2, rb[1] - rh * 0.05
    else: ox, oy = cx - im.width / 2, (rb[1] + rb[3]) / 2 - im.height / 2
    return im, (round(tpv[0] - ox), round(tpv[1] - oy)), d
def crop_rows(im, f0, f1):
    a = A(im)[..., 3] > 0; ys = np.nonzero(a.any(1))[0]; h = ys.max() - ys.min()
    c = im.crop((0, int(ys.min() + h * f0), im.width, int(ys.min() + h * f1))); return c.crop(c.getbbox())

tor, pel, arms, legs = parts
mir = ImageOps.mirror
torso_src = [tor[0]] * 3 + [mir(tor[1])] * 3 + [tor[2]] * 3
pelv_src = [pel[0]] * 3 + [mir(pel[1])] * 3 + [pel[2]] * 3
for n in range(9):
    put('torso', n, *fit_box(torso_src[n], 'torso', n, WIL, 1.25, 'bottom'))
    put('torso_pelvis', n, *fit_box(pelv_src[n], 'torso_pelvis', n, WIL, 1.12, 'top'))
for n in (9, 10): keep('torso', n, BASE); keep('torso_pelvis', n, BASE)

upper, fore, hopen, hfist, hside = arms
hopen, hfist, hside = crop_bracer(hopen), crop_bracer(hfist), crop_bracer(hside)
for n in range(3): put('arm_upper_skin', n, *fit_axis(upper, 'arm_upper_skin', n, WOLF))
for sym in ('arm_lower', 'arm_lower_narrow'):
    for n in range(7): put(sym, n, *fit_axis(fore, sym, n, WOLF))
# Maos: as 20 poses do jogo sao desenhos especificos (punho de lado, de cima, apontando...). Encaixar uma
# mao generica deixava varias viradas ao contrario. Agora cada quadro usa o PROPRIO desenho do Wilson
# (a luva), repintado como a mao palida do BLINK: contorno de nanquim, pele marfim, dobras dos dedos escuras.
SKIN = np.median(A(HEAD[0])[..., :3][face_comp(HEAD[0]) & (lum(A(HEAD[0])) > 200)], 0)
INK = np.array([24, 22, 26])
def skin_hand(tim):
    a = A(tim); al = a[..., 3] > 90; L = lum(a)
    inner = ndimage.binary_erosion(al, iterations=3 if al.sum() > 700 else 2)   # contorno mais grosso nas maos grandes
    lines = inner & (L > 120)                                   # tracos claros da luva = dobras dos dedos
    lines = ndimage.binary_erosion(lines, iterations=0) if lines.sum() == 0 else lines
    out = np.zeros_like(a)
    out[..., :3] = INK; out[..., 3] = np.where(al, 255, 0)
    sk = inner & ~lines
    out[sk, :3] = SKIN
    sh = sk & ~ndimage.binary_erosion(sk, iterations=3)          # leve sombra junto ao contorno
    out[sh, :3] = SKIN * 0.86
    out[..., 3] = np.maximum(out[..., 3], 0) * (a[..., 3] / 255.0 > 0.35)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
for n in range(20):
    if n == 15: keep('hand', 15, BASE); continue
    tim, tpv, d = load(WIL, 'hand', n); put('hand', n, skin_hand(tim), tpv, d)
leg_straight, leg_bent, boot_f, boot_s, boot_b = legs
def leg_only(im, fmax):
    """Perna ate logo acima do punho da bota (corta antes da linha larga do punho)."""
    a = A(im)[..., 3] > 100; ys = np.nonzero(a.any(1))[0]; y0, y1 = ys.min(), ys.max(); w = a.sum(1)
    ref = np.median(w[y0 + 5:int(y0 + (y1 - y0) * 0.25)])
    cut = int(y0 + (y1 - y0) * fmax)
    for y in range(int(y0 + (y1 - y0) * 0.25), cut):
        if w[y] > ref * 1.25: cut = y - 4; break
    c = A(im.crop((0, y0, im.width, cut)))
    keepm = ndimage.binary_opening(c[..., 3] > 100, iterations=7)          # tira tracos finos soltos
    c[..., 3] = np.where(ndimage.binary_dilation(keepm, iterations=1), c[..., 3], 0)
    c = Image.fromarray(c.astype(np.uint8), 'RGBA'); return c.crop(c.getbbox())
leg_s = leg_only(leg_straight, 0.42); leg_b = leg_only(leg_bent, 0.52)
for n in range(11):
    tim, tpv, d = load(WIL, 'leg', n); b = tim.getbbox()
    bent = (b[2] - b[0]) > 0.8 * (b[3] - b[1])
    put('leg', n, *fit_axis(leg_b if bent else leg_s, 'leg', n, WIL))
shoe = boot_s                                                    # bota de lado com o punho
for n in range(8):
    tim, tpv, d = load(WIL, 'foot', n); b = tim.getbbox(); cx = (b[0] + b[2]) / 2
    src = mir(shoe) if cx > tpv[0] else shoe                     # bota da folha tem o bico p/ a esquerda; espelha se o molde aponta p/ a direita
    put('foot', n, *fit_box(src, 'foot', n, WIL, 1.45, 'center', 0.0))
for n in range(2): keep('cheeks', n, Path(__file__).resolve().parent / 'bochechas')   # bochechas cheias ao comer (Wilson repintado)

man = []
for sym, frs in frames.items():
    for num, dur, im, p in frs:
        im.save(OUT / f'{sym}-{num}.png'); (OUT / f'{sym}-{num}.txt').write_text(f'{p[0]} {p[1]} {dur}')
    man.append(sym)
(OUT / 'manifesto.txt').write_text('\n'.join(man) + '\n')

# conferencia: 33 rostos completos (patch sobre a cabeca base) lado a lado
W = 170; sheet = Image.new('RGBA', (W * 11, W * 3), (200, 190, 170, 255))
for i, (n, full) in enumerate(checks):
    base = HEAD[1 if n in PMAP else 0].copy(); base.alpha_composite(full)
    base.thumbnail((W - 6, W - 6)); sheet.alpha_composite(base, ((i % 11) * W + 3, (i // 11) * W + 3))
sheet.save(OUT.parent / 'conferencia_rostos.png')
print('ok', len(man), 'simbolos', sum(len(v) for v in frames.values()), 'quadros')
