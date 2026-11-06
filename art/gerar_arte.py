"""Uso: python3 gerar_arte.py art/v063 <pasta com dagger_recorte.png renomeado para dagger_clean.png>
Arte da Dagger e da Pedra (desde a 0.6.3; lamina para baixo desde a 0.6.4): Dagger (mao/chao/icone) e Pedra do Impeto (corpo/chao/icone).
Saida em OUT (pasta), consumida pelo empacotador. Requer Pillow e numpy."""
import math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
SRC = Path(sys.argv[2])            # pasta com dagger_clean.png (recorte da referencia)
INK = (24, 22, 26, 255)

def outline(im, px):
    """Contorno escuro solido (estilo DST) de px pixels ao redor do alfa."""
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0)
    k = 2 * px + 1
    grown = a.filter(ImageFilter.MaxFilter(k if k % 2 else k + 1))
    base = Image.new('RGBA', im.size, INK); base.putalpha(grown)
    return Image.alpha_composite(base, im)

def pad(im, p):
    c = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p)); c.paste(im, (p, p)); return c

def punch(im, contrast=1.3, color=1.2, bright=0.97):
    rgb, a = im.convert('RGB'), im.split()[3]
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Color(rgb).enhance(color)
    rgb = ImageEnhance.Brightness(rgb).enhance(bright)
    out = rgb.convert('RGBA'); out.putalpha(a); return out

def fit(im, longest):
    s = longest / max(im.size)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS), s

# ---------------- Dagger ----------------
dag = Image.open(SRC / 'dagger_clean.png').convert('RGBA')
OX, OY = 7, 37                                  # deslocamento do recorte na referencia
GRIP = (410 - OX, 95 - OY)
pommel, guard = (500 - OX, 60 - OY), (300 - OX, 150 - OY)
ang = math.degrees(math.atan2(pommel[1] - guard[1], pommel[0] - guard[0]))
rot = -(90 - ang) + 180   # 0.6.4: lamina para baixo, cabo na mao (pegada normal de faca); fio voltado para frente

def held(height):
    big = pad(punch(dag), 200)
    marker = Image.new('L', big.size, 0); marker.putpixel((GRIP[0] + 200, GRIP[1] + 200), 255)
    r = big.rotate(rot, resample=Image.BICUBIC, expand=True)
    m = marker.rotate(rot, resample=Image.BILINEAR, expand=True)
    box = r.getbbox(); r, m = r.crop(box), m.crop(box)
    s = height / r.height
    size = (round(r.width * s), round(r.height * s))
    r = r.resize(size, Image.LANCZOS); m = m.resize(size, Image.BILINEAR)
    r = outline(pad(r, 4), 2)
    arr = np.array(m, dtype=float); yy, xx = np.unravel_index(arr.argmax(), arr.shape)
    return r, (int(xx) + 4, int(yy) + 4)

swap, swap_pivot = held(175)                    # 0.6.5: ~17% menor que a 0.6.3/0.6.4 (210 px)
swap.save(OUT / 'dagger_swap.png')
ground, _ = fit(punch(dag), 130)
ground = outline(pad(ground, 4), 2)
ground.save(OUT / 'dagger_ground.png')

def icon_from(im):
    big, _ = fit(im, 120)                       # desenha em 2x e reduz: contorno nitido
    big = outline(pad(big, 6), 4)
    small, _ = fit(big, 60)
    c = Image.new('RGBA', (64, 64)); c.alpha_composite(small, ((64 - small.width) // 2, (64 - small.height) // 2))
    return c
icon_from(punch(dag, 1.15, 1.1, 1.0)).save(OUT / 'icon_blink_dagger.png')

# ---------------- Pedra do Impeto ----------------
def stone(S=256, xscale=1.0):
    """Pedra lunar com faixa de ouro, gemas azul/vermelha/roxa e rachadura eletrica. Sem aura."""
    im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    k = S / 256
    P = lambda pts: [(128 * k + (x - 128) * k * xscale, y * k) for x, y in pts]
    shape = [(128, 22), (188, 52), (214, 118), (196, 186), (140, 230), (80, 214), (42, 152), (52, 82), (86, 40)]
    d.polygon(P(shape), fill=INK)
    inner = [(128 + (x - 128) * 0.88, 128 + (y - 128) * 0.88) for x, y in shape]
    body = Image.new('RGBA', (S, S)); ImageDraw.Draw(body).polygon(P(inner), fill=(150, 160, 178, 255))
    noise = np.random.default_rng(3).normal(0, 12, (S, S, 1)).repeat(3, 2)
    arr = np.array(body).astype(float); arr[:, :, :3] += noise
    body = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0 * k))
    mask = Image.new('L', (S, S)); ImageDraw.Draw(mask).polygon(P(inner), fill=255); body.putalpha(mask)
    shade = Image.new('RGBA', (S, S)); sd = ImageDraw.Draw(shade)
    sd.polygon(P([(196, 120), (214, 118), (196, 186), (140, 230), (110, 222), (170, 170)]), fill=(40, 50, 75, 120))
    sd.polygon(P([(86, 40), (128, 22), (150, 40), (100, 70), (66, 88), (52, 82)]), fill=(255, 255, 255, 60))
    shade = shade.filter(ImageFilter.GaussianBlur(5 * k)); shade.putalpha(ImageChops.multiply(shade.split()[3], mask))
    im.alpha_composite(body); im.alpha_composite(shade)
    d = ImageDraw.Draw(im); w = max(2, round(5 * k))
    d.polygon(P([(48, 128), (208, 108), (212, 132), (50, 152)]), fill=(210, 162, 58, 255), outline=INK, width=w)
    d.line(P([(58, 134), (202, 116)]), fill=(250, 215, 120, 255), width=max(1, round(3 * k)))
    for cx, cy, col in [(84, 136, (60, 110, 230)), (128, 128, (215, 50, 55)), (172, 122, (145, 65, 200))]:
        d.polygon(P([(cx, cy - 17), (cx + 14, cy), (cx, cy + 17), (cx - 14, cy)]), fill=col + (255,), outline=INK, width=max(2, round(4 * k)))
        d.polygon(P([(cx, cy - 12), (cx + 6, cy - 3), (cx - 4, cy - 2)]), fill=(255, 255, 255, 170))
    for c in ([(118, 34), (104, 70), (126, 82), (108, 104)], [(150, 150), (136, 176), (158, 186), (140, 220)]):
        d.line(P(c), fill=INK, width=max(3, round(9 * k)), joint='curve')
        d.line(P(c), fill=(120, 235, 255, 255), width=max(1, round(5 * k)), joint='curve')
    return im.crop(im.getbbox())

# 0.6.15: Runa Eletrica redesenhada no estilo do jogo (art/desenhar_runa.py), fiel a referencia
# do usuario (art/referencias/runa_eletrica_referencia.png) mas legivel em ~70 px: pedra mais
# escura que a pele, contorno grosso, gemas grandes, gravacoes ciano.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import desenhar_runa
def stone(S=256, xscale=1.0):
    """Runa Eletrica, versao B escolhida pelo usuario (moldura e engastes dourados).
    Alta resolucao, reduzida depois. xscale<1 = vista de lado."""
    return desenhar_runa.draw('B', 420, xscale)
icon_from(stone(256)).save(OUT / 'icon_blink_impeto.png')

def cord(d, pts, w=5):
    """0.6.16: corrente dourada (remete ao ouro da receita) no lugar do cordao de couro."""
    desenhar_runa.chain(d, pts, 10)
    return
    d.line(pts, fill=INK, width=w + 4, joint='curve')
    d.line(pts, fill=(96, 62, 38, 255), width=w, joint='curve')
    for x, y in pts:
        d.ellipse((x - (w + 4) / 2, y - (w + 4) / 2, x + (w + 4) / 2, y + (w + 4) / 2), fill=INK)
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=(96, 62, 38, 255))

def frame(pendant=None, cords=(), arc=None):
    """Monta um quadro num canvas com o pivo em (C, C); devolve imagem recortada e pivo."""
    C = 160; S = 2 * C
    im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    top = None
    if pendant:
        (px, py), rot, xs, h = pendant
        p = stone(256, xs); p, _ = fit(p, h)
        p = p.rotate(-rot, resample=Image.BICUBIC, expand=True)
        a = math.radians(rot); top = (C + px + math.sin(a) * h * 0.45, C + py - math.cos(a) * h * 0.45)
    for sx, sy in cords:
        cord(d, [(C + sx, C + sy), ((C + sx + top[0]) / 2, (C + sy + top[1]) / 2 + 3), top])
    if arc:
        cord(d, [(C + x, C + y) for x, y in arc])
    if pendant:
        im.alpha_composite(p, (round(C + px - p.width / 2), round(C + py - p.height / 2)))
    box = im.getbbox(); im = im.crop(box)
    return im, (C - box[0], C - box[1])

# Disposicao baseada nas extensoes dos quadros do amuleto original (posicoes apenas; arte propria).
frames = {
    0: frame(((-1, -16), 0, 1.0, 76), [(-22, -80), (20, -80)]),
    1: frame(((-5, -13), -12, 1.0, 76), [(-31, -70), (8, -80)]),
    2: frame(((1, -12), 12, 1.0, 76), [(-11, -80), (36, -70)]),
    3: frame(((24, -12), 20, 0.62, 72), [(-16, -86)]),
    4: frame(((30, 0), 5, 0.62, 72), [(7, -84)]),
    5: frame(((24, -19), 30, 0.62, 72), [(-28, -84)]),
    6: frame(arc=[(-32, -58), (-15, -78), (15, -78), (32, -60)]),
    7: frame(arc=[(-44, -55), (-25, -80), (5, -84), (20, -70)]),
    8: frame(arc=[(-18, -70), (5, -82), (30, -78), (46, -50)]),
    14: frame(((-1, 8), 0, 1.0, 82)),
    15: frame(arc=[(1, -63), (2, -30), (0, 4)]),
}
for n, (im, pv) in frames.items():
    im.save(OUT / f'impeto_torso_{n}.png')
    (OUT / f'impeto_torso_{n}.txt').write_text(f'{pv[0]} {pv[1]}')

# Chao: runa deitada, presa pelo aro a um cordao em laco.
g = Image.new('RGBA', (360, 220)); d = ImageDraw.Draw(g)
loop = [(205 + 62 * math.cos(t), 120 + 22 * math.sin(t)) for t in np.linspace(math.pi * 1.02, math.pi * 2.98, 28)]
cord(d, loop, 5)
st, _ = fit(stone(256), 120)
st = st.rotate(-78, resample=Image.BICUBIC, expand=True)        # aro (topo) aponta para a direita
bx = max(x for x, y in [(x, y) for y in range(st.height) for x in range(st.width) if st.getpixel((x, y))[3] > 128 and abs(y - st.height // 2) < 12])
g.alpha_composite(st, (round(loop[0][0] - bx + 8), round(120 - st.height / 2)))
box = g.getbbox(); g = g.crop(box)
g.save(OUT / 'impeto_ground.png')
(OUT / 'impeto_ground.txt').write_text(f'{round(g.width * 0.55)} {round(g.height * 0.6)}')
(OUT / 'dagger_swap.txt').write_text(f'{swap_pivot[0]} {swap_pivot[1]}')
(OUT / 'dagger_ground.txt').write_text(f'{ground.width // 2} {round(ground.height * 0.75)}')
print('ok', 'swap', swap.size, swap_pivot, 'ground', ground.size)
