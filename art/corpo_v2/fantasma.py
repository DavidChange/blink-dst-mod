"""Fantasma do BLINK: copia o fantasma do jogo (corpo, cauda, efeitos, olhos) e troca so a silhueta
do cabelo (ghost_Hat) pela do BLINK, tirada da cabeca de frente da folha 1.
Uso: python3 fantasma.py <ghost_wilson_build.zip do jogo (data/anim)> <folha f1_cabecas.jpg> <saida anim/ghost_blink_build.zip> <previa.png>"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import klei_anim
from klei_read import load_build
G = load_build(Path(sys.argv[1]))

im = np.array(Image.open(sys.argv[2]).convert('RGB')).astype(np.int32)
W = im.shape[1]; part = im[:, : W // 3]                         # cabeca de frente
fg = ndimage.binary_fill_holes(ndimage.binary_closing(part.min(2) < 222, iterations=2))
lab, n = ndimage.label(fg); big = 1 + np.argmax(ndimage.sum(fg, lab, range(1, n + 1))); head = lab == big
lum = part[..., 0] * .3 + part[..., 1] * .59 + part[..., 2] * .11
pale = head & (lum > 165)
pl, pn = ndimage.label(pale); face = pl == 1 + np.argmax(ndimage.sum(pale, pl, range(1, pn + 1)))
f = ndimage.binary_fill_holes(face); dk = (f & ~face) & (lum < 70)
el, en = ndimage.label(dk); esz = ndimage.sum(dk, el, range(1, en + 1)); eyes = np.argsort(esz)[::-1][:2] + 1
eye_y = np.mean([ndimage.center_of_mass(el == i)[0] for i in eyes])
# 0.9.5: como o fantasma do Wilson, o "chapeu" e a silhueta CHEIA do alto da cabeca (cabelo + testa),
# simplificada (so as pontas grandes), contorno grosso no topo e base em arco sem contorno, que se funde ao corpo.
ys, xs = np.nonzero(head); top, x0, x1 = ys.min(), xs.min(), xs.max()
cut = top + (eye_y - top) * float(sys.argv[5] if len(sys.argv) > 5 else 1.0)
X = np.arange(head.shape[1])[None, :]; Y = np.arange(head.shape[0])[:, None]
cx, half = (x0 + x1) / 2, (x1 - x0) / 2
arc = cut + 0.10 * (x1 - x0) * (1 - ((X - cx) / half) ** 2).clip(0, 1)      # base curva para baixo
shape = head & (Y < arc)
shape = ndimage.binary_opening(ndimage.binary_closing(shape, iterations=4), iterations=3)
lab, n = ndimage.label(shape); shape = lab == 1 + np.argmax(ndimage.sum(shape, lab, range(1, n + 1)))
import cv2
EPS = float(sys.argv[6]) if len(sys.argv) > 6 else 0.010
cs, _ = cv2.findContours(shape.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cs, key=cv2.contourArea)
poly = cv2.approxPolyDP(c, EPS * cv2.arcLength(c, True), True)[:, 0, :].astype(float)   # so as pontas grandes, retas
_, _, tim, tpv = G['ghost_Hat'][0]
ta = np.array(tim)[..., 3] > 100; tb = Image.fromarray(ta.astype(np.uint8)).getbbox()
cream = tuple(int(v) for v in np.median(np.array(tim)[..., :3][ta & (np.array(tim)[..., :3].min(2) > 150)], 0))
px0, py0 = poly.min(0); pw = poly[:, 0].max() - px0
s = (tb[2] - tb[0]) * 1.08 / pw
SS = 4; P = 12
pts = [((x - px0) * s * SS + P * SS, (y - py0) * s * SS + P * SS) for x, y in poly]
Wc = int((pw * s + 2 * P) * SS); Hc = int(((poly[:, 1].max() - py0) * s + 2 * P) * SS)
base_y = ((cut - py0) * s + P) * SS                                   # abaixo disto: base sem contorno
from PIL import ImageDraw
fill = Image.new('L', (Wc, Hc), 0); ImageDraw.Draw(fill).polygon(pts, fill=255)
line = Image.new('L', (Wc, Hc), 0); dl = ImageDraw.Draw(line); LW = 6 * SS
for i in range(len(pts)):
    p, q = pts[i], pts[(i + 1) % len(pts)]
    if p[1] < base_y and q[1] < base_y:
        dl.line([p, q], fill=255, width=LW); dl.ellipse((p[0] - LW / 2, p[1] - LW / 2, p[0] + LW / 2, p[1] + LW / 2), fill=255)
la = np.array(line).astype(np.float32) / 255 * (np.array(fill) > 0 if False else 1)
fa = np.array(fill).astype(np.float32) / 255
Yc = np.arange(Hc)[:, None]
fade = np.clip((Hc - P * SS - Yc) / (2.0 * SS), 0, 1)                 # base opaca (mesma cor do corpo), so 2px de suavizacao
fa = fa * np.where(Yc > base_y, fade, 1)
rgb = np.zeros((Hc, Wc, 3), np.float32) + np.array(cream)
rgb = rgb * (1 - la[..., None]) + np.array([24, 22, 26]) * la[..., None]
alpha = np.maximum(fa, la)
hat = Image.fromarray(np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
hat = hat.resize((Wc // SS, Hc // SS), Image.LANCZOS); hat = hat.crop(hat.getbbox())
print('pontos do contorno simplificado:', len(poly))
ox = (tb[0] + tb[2]) / 2 - hat.width / 2; oy = tb[3] - hat.height + 2
hat_pv = (round(tpv[0] - ox), round(tpv[1] - oy))

symbols = []
for name, frs in G.items():
    if name == 'ghost_Hat': frs = [(0, 1, hat, hat_pv)]
    symbols.append((name, [(num, dur, img, pv) for num, dur, img, pv in frs]))
klei_anim.build_zip(sys.argv[3], 'ghost_blink_build', symbols)

# previa: corpo + cauda + chapeu + olhos, montados pelos pivos (sem animacao: posicoes aproximadas)
can = Image.new('RGBA', (900, 420), (120, 120, 135, 255))
for k, (hname, himg, hpv) in enumerate([('wilson', tim, tpv), ('blink', hat, hat_pv)]):
    cx, cy = 220 + k * 450, 260
    _, _, bimg, bpv = G['ghost_body'][0]; can.alpha_composite(bimg, (cx - bpv[0], cy - bpv[1]))
    can.alpha_composite(himg, (cx - hpv[0], cy - hpv[1]))
    _, _, eimg, epv = G['ghost_eyes'][0]; can.alpha_composite(eimg, (cx - epv[0], cy - epv[1]))
can.save(sys.argv[4])
print('ok', hat.size, hat_pv, 'molde', tim.size, tpv)
