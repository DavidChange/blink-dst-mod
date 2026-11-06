"""Previa: Wilson x BLINK com e sem chapeu, parado (frente/lado/costas).
Uso: python3 ver_chapeu.py <pecas blink> <pecas wilson (klei_read.py wilson.zip)> <player_idles.zip> <saida.png> [chapeu.zip ...]"""
import sys, zipfile, shutil, tempfile
from pathlib import Path
ART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ART)); sys.path.insert(0, str(ART / 'corpo'))
import compor
from klei_read import load_build
from PIL import Image
argv = sys.argv
TMP = Path(tempfile.mkdtemp())
def with_hat(parts_dir, hatzip, tag):
    d = TMP / f'{tag}_{Path(hatzip).stem}'; shutil.rmtree(d, ignore_errors=True); shutil.copytree(parts_dir, d)
    raw = d / 'raw'; zipfile.ZipFile(hatzip).extractall(raw)
    for k, v in load_build(raw).items():
        if k.lower() != 'swap_hat': continue
        for num, dur, im, p in v: im.save(d / f'swap_hat-{num}.png'); (d / f'swap_hat-{num}.txt').write_text(f'{p[0]} {p[1]} {dur}')
    shutil.rmtree(raw); return d
A = compor.read_anims(argv[3])
hide_hat = {compor.kh(s) for s in ('headbase', 'hair')}
hide_nohat = {compor.kh(s) for s in ('headbase_hat', 'hair_hat', 'swap_hat')}
rows = [(argv[2], 'w'), (argv[1], 'b')]
hats = argv[5:]
cols = [(None, f) for f in (8, 5, 2)] + [(h, f) for h in hats for f in (8, 5)]
out = Image.new('RGBA', (300 * len(cols), 380 * 2), (200, 190, 170, 255))
for r, (pd, tag) in enumerate(rows):
    for j, (hat, fac) in enumerate(cols):
        P = compor.Parts(with_hat(pd, hat, tag) if hat else pd)
        c = compor.compose(P, A[('idle_loop', fac)][0], size=520, origin=(260, 480), hide=hide_hat if hat else hide_nohat)
        out.alpha_composite(c.crop((110, 80, 410, 460)), (j * 300, r * 380))
out.save(argv[4])
