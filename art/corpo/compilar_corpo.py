"""Compila as pecas geradas por gerar_corpo.py em anim/blink.zip (build "blink").
Uso: python3 compilar_corpo.py <pasta das pecas> <saida anim/blink.zip>"""
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import klei_anim
src = Path(sys.argv[1]); order = [l.split()[0] for l in (src / 'manifesto.txt').read_text().split('\n') if l.strip()]
symbols = []
for sym in order:
    frames = []
    for p in sorted(src.glob(f'{sym}-*.png'), key=lambda p: int(p.stem.rsplit('-', 1)[1])):
        if p.stem.rsplit('-', 1)[0] != sym: continue
        px, py, dur = map(int, p.with_suffix('.txt').read_text().split())
        frames.append((int(p.stem.rsplit('-', 1)[1]), dur, Image.open(p).convert('RGBA'), (px, py)))
    symbols.append((sym, frames))
atlas = klei_anim.build_zip(sys.argv[2], 'blink', symbols)
print('simbolos', len(symbols), 'quadros', sum(len(f) for _, f in symbols), 'atlas', atlas.size)
