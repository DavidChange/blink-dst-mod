"""Gera as pecas do corpo do BLINK a partir do molde do jogo (metodo padrao de mods de personagem):
cabeca/cabelo/rosto no tamanho do Wilson + tronco/bracos/maos/pernas/pes do Wolfgang forte,
recoloridos/redesenhados conforme a ficha do BLINK.
Uso: python3 gerar_corpo.py <pasta wilson (build.bin+atlas)> <pasta wolfgang_mighty> <saida>
Saida: <saida>/<simbolo>-<quadro>.png + .txt (pivo) + manifesto.txt
Requer Pillow, numpy, scipy."""
import sys, struct, io
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

WIL, WOLF, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)

# ---------------- leitura do molde ----------------
def load_tex(path):
    b = path.read_bytes(); h, = struct.unpack_from('<I', b, 4); mips = (h >> 13) & 31
    w, hh, pitch, size = struct.unpack_from('<HHHI', b, 8); off = 8 + 10 * mips
    dds = b'DDS ' + struct.pack('<7I', 124, 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000, hh, w, size, 0, 1) + b'\0' * 44
    dds += struct.pack('<2I4s5I', 32, 0x4, b'DXT5', 0, 0, 0, 0, 0) + struct.pack('<5I', 0x1000, 0, 0, 0, 0)
    im = Image.open(io.BytesIO(dds + b[off:off + size])); im.load()
    a = np.array(im.transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert('RGBA')).astype(np.float32)
    al = a[:, :, 3:4]; a[:, :, :3] = np.where(al > 0, np.clip(a[:, :, :3] * 255 / np.maximum(al, 1), 0, 255), 0)  # desfaz pre-multiplicacao
    return Image.fromarray(a.astype(np.uint8), 'RGBA')

def kh(t):
    h = 0
    for c in t.lower(): h = (ord(c) + (h << 6) + (h << 16) - h) & 0xFFFFFFFF
    return h

def load_build(folder):
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

wil = load_build(WIL); wolf = load_build(WOLF)

# ---------------- paleta (ficha do BLINK) ----------------
INK = np.array([24, 22, 26]); SKIN = np.array([228, 186, 150]); SKIN_SH = np.array([188, 144, 112])
TUNIC = np.array([58, 56, 60]); TUNIC_SH = np.array([40, 38, 42]); HOOD = np.array([92, 88, 90])
BELT = np.array([124, 82, 46]); BUCKLE = np.array([176, 176, 168]); PANTS = np.array([58, 56, 58])
WRAP = np.array([40, 38, 42]); BOOT = np.array([62, 52, 44])
CYAN = np.array([30, 214, 255]); CYAN_HI = np.array([210, 252, 255])

def arr(im): return np.array(im).astype(np.float32)
def img(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
def lum(a): return a[:, :, 0] * .3 + a[:, :, 1] * .59 + a[:, :, 2] * .11

def recolor_light(im, base, shade, thresh=150):
    """Troca as areas claras (pele/tecido claro do molde) por `base`, preservando o sombreado e a tinta escura."""
    a = arr(im); L = lum(a); m = (a[:, :, 3] > 0) & (L > thresh)
    t = np.clip((L - thresh) / (255 - thresh), 0, 1)[..., None]
    col = shade + (base - shade) * t
    a[:, :, :3] = np.where(m[..., None], col, a[:, :, :3]); return img(a)

def recolor_by(im, fn):
    a = arr(im); a[:, :, :3] = fn(a); return img(a)

def save(sym, num, dur, im, pv):
    im.save(OUT / f'{sym}-{num}.png'); (OUT / f'{sym}-{num}.txt').write_text(f'{pv[0]} {pv[1]} {dur}')

manifest = []
def emit(sym, frames):
    for num, dur, im, pv in frames:
        save(sym, num, dur, im, pv)
    manifest.append(f'{sym} ' + ','.join(str(f[0]) for f in frames))

# ---------------- cabeca (Wilson) ----------------
def goatee(im, pv, side=False):
    """Cavanhaque pequeno no queixo (pivo do headbase fica no queixo)."""
    d = ImageDraw.Draw(im); x, y = pv
    if side:
        pts = [(x - 8, y - 14), (x + 4, y - 16), (x + 2, y - 2), (x - 4, y + 8), (x - 10, y - 2)]
    else:
        pts = [(x - 12, y - 16), (x + 12, y - 16), (x + 7, y - 4), (x, y + 10), (x - 7, y - 4)]
    d.polygon(pts, fill=(28, 24, 22, 255), outline=(10, 10, 12, 255))
    for k in range(3):
        d.line([(x - 6 + k * 6, y - 12), (x - 4 + k * 4, y + 2)], fill=(70, 62, 58, 255), width=1)
    return im

def fringe(im, num):
    """Franja/linha do cabelo no alto da cabeca (o cabelo fica atras da cabeca de frente)."""
    a = arr(im); al = a[:, :, 3] > 0; ys, xs = np.nonzero(al)
    top, bot = ys.min(), ys.max(); h = bot - top; x0, x1 = xs.min(), xs.max(); w = x1 - x0
    Y, X = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    if num == 1:   # perfil: cabelo no alto e na nuca (lado esquerdo)
        line = top + h * 0.16 + (np.clip((x0 + w * 0.55 - X) / (w * 0.55), 0, 1)) * h * 0.30
    else:
        line = top + h * 0.15 + np.where(np.abs(X - (x0 + x1) / 2) > w * 0.36, h * 0.10, 0)
    teeth = (np.abs(((X - x0) % 14) - 7) / 7.0) * 7          # pontas da franja
    m = al & (Y < line + teeth)
    inner = ndimage.binary_erosion(al, iterations=3)
    a[:, :, :3] = np.where((m & inner)[..., None], np.array([30, 28, 32]), a[:, :, :3])
    edge = m & inner & ~ndimage.binary_erosion(m, iterations=1)
    a[:, :, :3] = np.where(edge[..., None], np.array([12, 10, 12]), a[:, :, :3])
    rng = np.random.default_rng(3); out = img(a); d = ImageDraw.Draw(out)
    for _ in range(26):
        x = rng.uniform(x0 + 8, x1 - 8); y = rng.uniform(top + 4, top + h * 0.14)
        if m[int(y), int(x)]: d.line([(x, y), (x + rng.uniform(-3, 3), y + 7)], fill=(72, 70, 78, 255), width=1)
    return out
for sym in ['headbase', 'headbase_hat']:
    fr = []
    for num, dur, im, pv in wil[sym]:
        im = recolor_light(im, SKIN, SKIN_SH, 140)
        if sym == 'headbase' and num in (0, 1, 4): im = fringe(im, num)
        if num in (0, 4): im = goatee(im, pv)
        if num == 1: im = goatee(im, pv, side=True)
        fr.append((num, dur, im, pv))
    emit(sym, fr)
emit('cheeks', [(n, d, recolor_light(im, SKIN, SKIN_SH, 140), pv) for n, d, im, pv in wil['cheeks']])
# Cabelo: o do Wilson e enorme e marcante; o BLINK tem cabelo CURTO e espetado.
# Encurta verticalmente em direcao ao pivo (base da cabeca) e estreita um pouco.
def short_hair(im, pv, sy=0.62, sx=0.86):
    w, h = im.size
    nw, nh = max(1, round(w * sx)), max(1, round(h * sy))
    out = im.resize((nw, nh), Image.LANCZOS)
    return out, (round(pv[0] * sx), round(pv[1] * sy))
def hair_frames(src, sy):
    fr = []
    for n, d, im, pv in src:
        im2, pv2 = short_hair(im, pv, sy)
        fr.append((n, d, im2, pv2))
    return fr
def blink_hair(im, pv, view):
    """Cabelo proprio do BLINK: so a base do molde (garante o encaixe na cabeca) + mechas curtas
    espetadas desenhadas por cima: leque na frente, varridas para tras no perfil, radiais nas costas."""
    rng = np.random.default_rng(11 + view)
    base = np.array(im.split()[3]) > 40
    ys, xs = np.nonzero(base); top, bot = ys.min(), ys.max(); h = bot - top
    cut = top + int(h * (0.50 if view != 1 else 0.46))
    cap = base & (np.arange(base.shape[0])[:, None] >= cut)
    cap = ndimage.binary_closing(cap, iterations=3)
    PAD = 40
    W, H = im.width + 2 * PAD, im.height + 2 * PAD
    can = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(can)
    capim = Image.fromarray((cap * 255).astype(np.uint8)); mask = Image.new('L', (W, H)); mask.paste(capim, (PAD, PAD))
    cxs = np.nonzero(cap.any(0))[0]; x0, x1 = cxs.min() + PAD, cxs.max() + PAD; ytop = cut + PAD
    cx = (x0 + x1) / 2
    spikes = []
    n = 9 if view == 0 else (8 if view == 2 else 7)
    for i in range(n):
        t = (i + 0.5) / n; bx = x0 + 6 + (x1 - x0 - 12) * t
        rows = np.nonzero(np.array(mask)[:, int(bx)] > 0)[0]
        by = rows.min() + 4 if len(rows) else ytop
        if view == 1:   # perfil: varridas para tras (esquerda), mais longas atras
            ang = np.radians(-150 + 40 * t + rng.uniform(-6, 6)); L = 26 + 22 * (1 - t) + rng.uniform(-4, 4)
        elif view == 2: # costas: radiais
            ang = np.radians(-90 + (t - 0.5) * 110 + rng.uniform(-6, 6)); L = 22 + rng.uniform(0, 12)
        else:           # frente: leque para cima/fora, topete central mais alto
            ang = np.radians(-90 + (t - 0.5) * 120 + rng.uniform(-7, 7)); L = 40 + 26 * (1 - abs(t - 0.5) * 2) + rng.uniform(-4, 5)
        bw = (22 if view == 0 else 15) + rng.uniform(-2, 3)
        nx, ny = np.cos(ang), np.sin(ang); px, py = -ny, nx
        tip = (bx + nx * L, by + ny * L)
        spikes.append([(bx - px * bw / 2, by - py * bw / 2 + 4), tip, (bx + px * bw / 2, by + py * bw / 2 + 4)])
    sp = Image.new('L', (W, H)); sd = ImageDraw.Draw(sp)
    for tri in spikes: sd.polygon(tri, fill=255)
    full = np.maximum(np.array(mask), np.array(sp))
    full = ndimage.binary_closing(full > 0, iterations=2)
    outline = ndimage.binary_dilation(full, iterations=3)
    a = np.zeros((H, W, 4), np.float32)
    a[outline] = (12, 10, 12, 255); a[full] = (30, 28, 32, 255)
    out = img(a); od = ImageDraw.Draw(out)
    for tri in spikes:   # fios: linhas da base ate a ponta
        (ax_, ay_), (tx, ty), (bx_, by_) = tri
        for k in range(3):
            f = (k + 1) / 4; sx, sy = ax_ + (bx_ - ax_) * f, ay_ + (by_ - ay_) * f + 6
            od.line([(sx, sy), (tx + (sx - tx) * 0.15, ty + (sy - ty) * 0.15)], fill=(78, 76, 84, 255), width=1)
    for _ in range(40):  # textura de fios na base
        x = rng.uniform(x0 + 4, x1 - 4); y = rng.uniform(ytop + 2, ytop + 26)
        if full[int(min(H - 1, y + 8)), int(x)] and full[int(y), int(x)]:
            od.line([(x, y), (x + rng.uniform(-4, 4), y + 8)], fill=(70, 68, 76, 255), width=1)
    box = out.getbbox(); out = out.crop(box)
    return out, (pv[0] + PAD - box[0], pv[1] + PAD - box[1])
hair = []
for n, d, im, pv in hair_frames(wil['hair'], 0.62):
    im2, pv2 = blink_hair(im, pv, {0: 0, 1: 1, 2: 2, 3: 0}[n])
    if n == 3:   # quadro especial do molde (com realces brancos): mesmo cabelo com brilho
        a = arr(im2); m = (a[:, :, 3] > 0) & (lum(a) > 40) & (lum(a) < 90)
        a[:, :, :3] = np.where(m[..., None], np.array([220, 220, 228]), a[:, :, :3]); im2 = img(a)
    hair.append((n, d, im2, pv2))
emit('hair', hair); emit('hair_hat', wil['hair_hat'])

# ---------------- rosto: olhos ciano ----------------
def cyan_eyes(im):
    a = arr(im); al = a[:, :, 3] > 30; L = lum(a)
    sat = a[:, :, :3].max(2) - a[:, :, :3].min(2)
    gray = al & (L > 95) & (L < 215) & (sat < 30)          # "orbita" cinza do molde
    if gray.sum() < 30: return im
    dark = al & (L < 80)
    pupil = np.zeros_like(dark)
    socks, n = ndimage.label(ndimage.binary_dilation(gray, iterations=2))
    for i in range(1, n + 1):
        sock = socks == i
        if (sock & gray).sum() < 40: continue
        filled = ndimage.binary_fill_holes(sock)
        ys, xs = np.nonzero(filled); y0, y1 = ys.min(), ys.max()
        inner = dark & filled & (np.arange(dark.shape[0])[:, None] > y0 + (y1 - y0) * 0.22)
        lab, m = ndimage.label(inner)
        if m == 0: continue
        sizes = ndimage.sum(inner, lab, range(1, m + 1)); best = 1 + int(np.argmax(sizes))
        comp = lab == best
        if comp.sum() > 0.6 * filled.sum(): continue
        pupil |= comp
    # 2a rodada: orbita vira esclera clara com contorno fino (nao parece olheira);
    # iris ciano grande e saturada; centro quase branco (brilho). O prefab ainda faz o
    # simbolo "face" ignorar parte da escuridao (SetSymbolLightOverride).
    edge = gray & ~ndimage.binary_erosion(gray, iterations=1)
    a[:, :, :3] = np.where(gray[..., None], np.array([236, 240, 244]), a[:, :, :3])
    a[:, :, :3] = np.where(edge[..., None], np.array([120, 124, 136]), a[:, :, :3])
    iris = ndimage.binary_dilation(pupil, iterations=3) & (gray | pupil)
    a[:, :, :3] = np.where(iris[..., None], CYAN, a[:, :, :3])
    ring = iris & ~ndimage.binary_erosion(iris, iterations=1)
    a[:, :, :3] = np.where(ring[..., None], np.array([10, 110, 150]), a[:, :, :3])
    core = ndimage.binary_erosion(pupil, iterations=1)
    a[:, :, :3] = np.where(core[..., None], CYAN_HI, a[:, :, :3])
    return img(a)
def side_skin(im):
    """No perfil, o nariz/realce branco do molde vira pele."""
    a = arr(im); L = lum(a); sat = a[:, :, :3].max(2) - a[:, :, :3].min(2)
    m = (a[:, :, 3] > 0) & (L > 215) & (sat < 25)
    a[:, :, :3] = np.where(m[..., None], SKIN, a[:, :, :3]); return img(a)
emit('face', [(n, d, side_skin(cyan_eyes(im)) if n in (4, 5, 6, 7) else cyan_eyes(im), pv) for n, d, im, pv in wil['face']])

# ---------------- tronco (Wolfgang): tunica rasgada + capuz ----------------
def tunic(im, pv, num):
    a = arr(im); al = a[:, :, 3] > 0; L = lum(a)
    light = al & (L > 150)
    # regata listrada (Wolfgang normal): listras vermelhas tambem viram tunica
    red = al & (a[:, :, 0] > a[:, :, 1] + 40) & (L > 50)
    light = light | red
    L = np.where(red, 170.0, L)
    hoodm = al & (L > 110) & (L <= 200) & (a[:, :, :3].max(2) - a[:, :, :3].min(2) < 25) & (np.arange(a.shape[0])[:, None] < a.shape[0] * 0.45)
    t = np.clip((L - 150) / 105, 0, 1)[..., None]
    a[:, :, :3] = np.where(light[..., None], TUNIC_SH + (TUNIC - TUNIC_SH) * t, a[:, :, :3])
    if num not in (6, 7, 8, 9, 10):
        a[:, :, :3] = np.where(hoodm[..., None], HOOD, a[:, :, :3])
    im = img(a)
    if num in (9, 10): return im
    # barra rasgada: dentes recortados na borda de baixo
    w, h = im.size; m = Image.new('L', im.size, 255); d = ImageDraw.Draw(m)
    ys = np.where(np.array(im.split()[3]).max(1) > 0)[0]; bottom = ys.max() if len(ys) else h - 1
    step = max(8, w // 6)
    for i, x in enumerate(range(0, w, step)):
        depth = 7 if i % 2 == 0 else 4
        d.polygon([(x, bottom + 2), (x + step / 2, bottom - depth), (x + step, bottom + 2)], fill=0)
    alpha = np.minimum(np.array(im.split()[3]), np.array(m))
    out = arr(im); out[:, :, 3] = alpha
    edge = (alpha > 0) & ~ndimage.binary_erosion(alpha > 0, iterations=2)
    lower = np.arange(h)[:, None] > bottom - 12
    out[:, :, :3] = np.where((edge & lower)[..., None], INK, out[:, :, :3])
    # costura/remendo em X (detalhe da ficha), so na frente
    im = img(out)
    if num in (0, 1, 2):
        dd = ImageDraw.Draw(im); cx, cy = int(w * 0.68), int(h * 0.42)
        dd.line([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=(150, 146, 140, 255), width=2)
        dd.line([(cx - 4, cy + 4), (cx + 4, cy - 4)], fill=(150, 146, 140, 255), width=2)
    return im
def hood(im, pv, num):
    """Capuz abaixado: rolo de tecido em volta do pescoco/ombros (frente/lado) e caido nas costas."""
    if num in (9, 10): return im, pv
    PAD = 14
    can = Image.new('RGBA', (im.width + 2 * PAD, im.height + 2 * PAD)); can.alpha_composite(im, (PAD, PAD))
    al = np.array(im.split()[3]) > 0; ys, xs = np.nonzero(al)
    top, x0, x1 = ys.min() + PAD, xs.min() + PAD, xs.max() + PAD; w = x1 - x0; cx = (x0 + x1) / 2
    lay = Image.new('RGBA', can.size); d = ImageDraw.Draw(lay)
    ink = tuple(INK) + (255,); hc = tuple(HOOD) + (255,); fold = (64, 60, 64, 255)
    if num in (6, 7, 8):     # costas: capuz caido
        shape = [(x0 + w * 0.12, top + 2), (x1 - w * 0.12, top + 2), (x1 - w * 0.22, top + 26), (cx, top + 44), (x0 + w * 0.22, top + 26)]
        d.polygon(shape, fill=ink); d.line(shape + [shape[0]], fill=ink, width=5, joint='curve')
        inner = [(x0 + w * 0.16, top + 4), (x1 - w * 0.16, top + 4), (x1 - w * 0.25, top + 24), (cx, top + 39), (x0 + w * 0.25, top + 24)]
        d.polygon(inner, fill=hc)
        d.line([(cx, top + 8), (cx, top + 34)], fill=fold, width=2); d.line([(x0 + w * 0.3, top + 10), (cx - 4, top + 30)], fill=fold, width=2)
    else:
        side = num in (3, 4, 5)
        ex0 = x0 - (6 if not side else 10); ex1 = x1 + (6 if not side else 2)
        d.rounded_rectangle((ex0, top - 7, ex1, top + 15), 10, fill=ink)
        d.rounded_rectangle((ex0 + 3, top - 4, ex1 - 3, top + 12), 8, fill=hc)
        for k in range(1, 5):
            fx = ex0 + (ex1 - ex0) * k / 5
            d.line([(fx, top - 2), (fx + 3, top + 10)], fill=fold, width=2)
        if not side:   # decote em V da tunica abaixo do capuz
            d.polygon([(cx - 9, top + 12), (cx + 9, top + 12), (cx, top + 24)], fill=ink)
            d.polygon([(cx - 5, top + 13), (cx + 5, top + 13), (cx, top + 20)], fill=tuple(SKIN) + (255,))
    can.alpha_composite(lay)
    return can, (pv[0] + PAD, pv[1] + PAD)
torso = []
for n, d, im, pv in wolf['torso']:
    im2, pv2 = hood(tunic(im, pv, n), pv, n); torso.append((n, d, im2, pv2))
emit('torso', torso)

# ---------------- cintura (Wolfgang): saia da tunica + cinto ----------------
def pelvis(im, pv, num):
    a = arr(im); al = a[:, :, 3] > 0; L = lum(a)
    body = al & ((L > 70) | (a[:, :, 0] > a[:, :, 1] + 40))
    a[:, :, :3] = np.where(body[..., None], TUNIC, a[:, :, :3])
    im = img(a)
    if num in (9, 10): return im
    w, h = im.size; ys = np.where(np.array(im.split()[3]).max(1) > 0)[0]
    top = ys.min() if len(ys) else 0
    band = Image.new('RGBA', im.size); d = ImageDraw.Draw(band)
    y0, y1 = top + 3, top + 13
    d.rectangle((0, y0 - 1, w, y1 + 1), fill=tuple(INK) + (255,)); d.rectangle((0, y0, w, y1), fill=tuple(BELT) + (255,))
    d.line([(0, y0 + 3), (w, y0 + 3)], fill=(150, 104, 64, 255), width=1)
    if num in (0, 1, 2):
        cx = w // 2; d.rectangle((cx - 9, y0 - 2, cx + 9, y1 + 2), fill=tuple(INK) + (255,)); d.rectangle((cx - 7, y0, cx + 7, y1), fill=tuple(BUCKLE) + (255,)); d.rectangle((cx - 3, y0 + 3, cx + 3, y1 - 3), fill=tuple(BELT) + (255,))
    if num in (3, 4, 5):   # bolsa de couro na lateral (ficha)
        d.rounded_rectangle((w // 2 - 8, y1, w // 2 + 8, y1 + 14), 3, fill=tuple(BELT) + (255,), outline=tuple(INK) + (255,), width=2)
    band.putalpha(Image.fromarray(np.minimum(np.array(band.split()[3]), np.array(im.split()[3]))))
    im.alpha_composite(band); return im
emit('torso_pelvis', [(n, d, pelvis(im, pv, n), pv) for n, d, im, pv in wolf['torso_pelvis']])

# ---------------- bracos/maos (Wolfgang): pele + faixas no punho ----------------
def wrist_wrap(im, pv):
    a = arr(im); al = a[:, :, 3] > 0
    yy, xx = np.nonzero(al)
    if len(xx) == 0: return im
    d2 = (xx - pv[0]) ** 2 + (yy - pv[1]) ** 2; far = np.argmax(d2)
    ax, ay = xx[far] - pv[0], yy[far] - pv[1]; L = np.hypot(ax, ay) or 1
    Y, X = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    proj = ((X - pv[0]) * ax + (Y - pv[1]) * ay) / (L * L)
    band = al & (proj > 0.55) & (proj < 0.93) & (lum(a) > 90)
    a[:, :, :3] = np.where(band[..., None], WRAP, a[:, :, :3])
    for p in (0.66, 0.76, 0.86):
        line = al & (np.abs(proj - p) < 0.025) & band
        a[:, :, :3] = np.where(line[..., None], np.array([90, 88, 96]), a[:, :, :3])
    return img(a)
for sym in ['arm_lower', 'arm_lower_narrow']:
    emit(sym, [(n, d, wrist_wrap(recolor_light(im, SKIN, SKIN_SH, 120), pv), pv) for n, d, im, pv in wolf[sym]])
emit('arm_upper_skin', [(n, d, recolor_light(im, SKIN, SKIN_SH, 120), pv) for n, d, im, pv in wolf['arm_upper_skin']])
emit('hand', [(n, d, im if n == 15 else recolor_light(im, SKIN, SKIN_SH, 120), pv) for n, d, im, pv in wolf['hand']])

# ---------------- pernas/pes (Wolfgang): calca escura + botas ----------------
def boot_cuff(im, pv):
    a = arr(im); al = a[:, :, 3] > 0
    a[:, :, :3] = np.where((al & (lum(a) > 90))[..., None], PANTS + 20, a[:, :, :3])
    yy, xx = np.nonzero(al)
    if len(xx) == 0: return img(a)
    d2 = (xx - pv[0]) ** 2 + (yy - pv[1]) ** 2; far = np.argmax(d2)
    ax, ay = xx[far] - pv[0], yy[far] - pv[1]; L = np.hypot(ax, ay) or 1
    Y, X = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    proj = ((X - pv[0]) * ax + (Y - pv[1]) * ay) / (L * L)
    cuff = al & (proj > 0.72) & (lum(a) > 30)
    a[:, :, :3] = np.where(cuff[..., None], BOOT + 22, a[:, :, :3])
    fold = al & (np.abs(proj - 0.74) < 0.035)
    a[:, :, :3] = np.where(fold[..., None], INK, a[:, :, :3])
    return img(a)
emit('leg', [(n, d, boot_cuff(im, pv), pv) for n, d, im, pv in wolf['leg']])
emit('foot', [(n, d, recolor_by(im, lambda a: np.where((lum(a) > 90)[..., None], BOOT + 30, np.where((lum(a) > 20)[..., None], BOOT, a[:, :, :3]))), pv) for n, d, im, pv in wolf['foot']])

(OUT / 'manifesto.txt').write_text('\n'.join(manifest) + '\n')
print('\n'.join(manifest))
