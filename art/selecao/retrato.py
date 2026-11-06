"""Retrato da tela de selecao (oval, estilo Klei) e nome dourado do BLINK.
Uso: python3 retrato.py <arte do personagem (png/jpg, fundo branco ou ja com cenario)> <saida dir> [modo]
modo 'mestre': recorta a vista de frente da folha mestre e pinta um fundo cinza de floresta.
modo 'cena'  : a imagem ja traz o cenario (gerada no estilo dos retratos); so encaixa no oval.
Gera: bigportraits/blink.tex/.xml, images/names_gold_blink.*, images/names_blink.*, previa.png"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); import klei_anim
HERE = Path(__file__).resolve().parent
src, OUT = Path(sys.argv[1]), Path(sys.argv[2]); mode = sys.argv[3] if len(sys.argv) > 3 else 'mestre'
(OUT / 'bigportraits').mkdir(parents=True, exist_ok=True); (OUT / 'images').mkdir(parents=True, exist_ok=True)
frame = Image.open(HERE / 'frame.png').convert('RGBA'); inner = np.load(HERE / 'inner.npy')
ys, xs = np.nonzero(inner); ix0, ix1, iy0, iy1 = xs.min(), xs.max(), ys.min(), ys.max()
W, H = frame.size

def forest_bg(rng=np.random.default_rng(7)):
    """Fundo cinza tipo retrato Klei: ceu claro, pinheiros cinza esboçados, chao claro."""
    bg = Image.new('RGBA', (W, H), (150, 150, 150, 255)); d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H; c = int(176 - 50 * t); d.line((0, y, W, y), fill=(c, c, c, 255))
    hz = iy0 + (iy1 - iy0) * 0.62
    for k in range(26):
        x = rng.uniform(ix0 - 20, ix1 + 20); h = rng.uniform(70, 190); w = h * rng.uniform(0.22, 0.32)
        g = int(rng.uniform(96, 128))
        d.polygon([(x, hz - h), (x - w, hz + 8), (x + w, hz + 8)], fill=(g, g, g, 255))
        for j in range(5):                                        # tracos de nanquim nos galhos
            yy = hz - h + h * (j + 1) / 6; ww = w * (j + 1) / 6
            d.line((x - ww, yy + 6, x, yy - 2, x + ww, yy + 6), fill=(g - 30, g - 30, g - 30, 255), width=2)
    d.rectangle((0, hz, W, H), fill=(178, 178, 176, 255))
    for k in range(120):                                          # grama esboçada
        x = rng.uniform(ix0, ix1); y = rng.uniform(hz + 5, iy1)
        d.line((x, y, x + rng.uniform(-4, 4), y - rng.uniform(6, 14)), fill=(120, 120, 120, 255), width=1)
    bg = bg.filter(ImageFilter.GaussianBlur(0.6))
    noise = rng.normal(0, 7, (H, W, 1)).repeat(3, 2)
    a = np.array(bg).astype(float); a[..., :3] += noise
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def cut_white(im):
    a = np.array(im.convert('RGB')).astype(int)
    fg = ndimage.binary_fill_holes(ndimage.binary_closing(a.min(2) < 225, iterations=2))
    lab, n = ndimage.label(fg); sz = ndimage.sum(fg, lab, range(1, n + 1))
    return a, lab, sz

inner_img = Image.fromarray((inner * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
canvas = Image.new('RGBA', (W, H))
if mode == 'mestre':
    a, lab, sz = cut_white(Image.open(src))
    objs = ndimage.find_objects(lab); big = [i for i in np.argsort(sz)[::-1][:3]]
    first = min(big, key=lambda i: objs[i].__getitem__(1).start)    # vista de frente (mais a esquerda)
    sl = objs[first]; m = lab[sl] == first + 1
    rgba = np.zeros(m.shape + (4,), np.uint8); rgba[..., :3] = a[sl]; rgba[..., 3] = m * 255
    char = Image.fromarray(rgba)
    # borda branca de "recorte de papel", como nos retratos da Klei
    al = np.array(char)[..., 3] > 0; ring = ndimage.binary_dilation(al, iterations=4) & ~al
    pad = Image.new('RGBA', (char.width + 12, char.height + 12)); pad.paste(char, (6, 6))
    r = np.array(pad); al2 = r[..., 3] > 0; ring = ndimage.binary_dilation(al2, iterations=4) & ~al2
    r[ring] = (236, 232, 222, 255); char = Image.fromarray(r)
    s = (iy1 - iy0) * 1.02 / char.height; char = char.resize((round(char.width * s), round(char.height * s)), Image.LANCZOS)
    bg = forest_bg(); scene = Image.new('RGBA', (W, H)); scene.paste(bg, (0, 0))
    cx = (ix0 + ix1) // 2
    scene.alpha_composite(char, (cx - char.width // 2, iy0 + 6))
else:
    scene_src = Image.open(src).convert('RGBA')
    # largura do oval coberta; topo ancorado (cabelo inteiro visivel), o excesso sai por baixo
    top = float(sys.argv[4]) if len(sys.argv) > 4 else 0.04      # fracao da imagem cortada no topo
    zoom = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    s = (ix1 - ix0 + 16) / scene_src.width * zoom
    sc = scene_src.resize((round(scene_src.width * s), round(scene_src.height * s)), Image.LANCZOS)
    scene = Image.new('RGBA', (W, H)); scene.paste(sc, ((ix0 + ix1) // 2 - sc.width // 2, iy0 - round(sc.height * top)))
canvas.paste(scene, (0, 0), inner_img)
canvas.alpha_composite(frame)
klei_anim_tex = klei_anim.ktex_rgba(canvas)
(OUT / 'bigportraits' / 'blink.tex').write_bytes(klei_anim_tex)
u2 = 0.958984375; v1 = 0.361328125
(OUT / 'bigportraits' / 'blink.xml').write_text(
    '<Atlas><Texture filename="blink.tex" /><Elements>' +
    ''.join(f'<Element name="{n}" u1="0.0" u2="{u2}" v1="{v1}" v2="1.0" />' for n in ('blink.tex', 'blink_none.tex', 'blink_oval.tex', 'blink_none_oval.tex')) +
    '</Elements></Atlas>')
name = Image.open(HERE / 'blink_name.png').convert('RGBA')
for f in ('names_gold_blink', 'names_blink'):
    (OUT / 'images' / f'{f}.tex').write_bytes(klei_anim.ktex_rgba(name))
    (OUT / 'images' / f'{f}.xml').write_text(f'<Atlas><Texture filename="{f}.tex" /><Elements><Element name="blink.tex" u1="0.00048828125" u2="0.85009765625" v1="0.1962890625" v2="0.9990234375" /></Elements></Atlas>')
# previa aproximada da tela (escalas do jogo: nome .28, retrato .5)
pv = Image.new('RGBA', (700, 760), (36, 28, 24, 255))
nm = name.crop((0, 0, 870, 412)); nm = nm.resize((int(870 * .56), int(412 * .56)), Image.LANCZOS)
pv.alpha_composite(nm, (20, 0))
pr = canvas.crop((0, 0, 491, 654)); pr = pr.resize((int(491 * .82), int(654 * .82)), Image.LANCZOS)
pv.alpha_composite(pr, (10, 200))
pv.save(OUT / 'previa.png')
print('ok')
