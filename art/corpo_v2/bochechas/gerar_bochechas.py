"""Bochechas cheias ao comer: as do Wilson repintadas com a pele do BLINK.
Uso: python3 gerar_bochechas.py <escala> <dx> <dy> <pecas wilson> <pecas blink (destino)> <player_actions_eat.zip> <previa.png>
Valores usados na 0.10.3: escala 1.0, dx 0, dy 12."""
import sys
from pathlib import Path
ART = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ART / 'corpo')); import compor
from PIL import Image
import numpy as np
S=float(sys.argv[1]); DX=float(sys.argv[2]); DY=float(sys.argv[3])
WIL=Path(sys.argv[4]); P=Path(sys.argv[5]); EAT=sys.argv[6]; out=sys.argv[7]
head=np.array(Image.open(P/'headbase-0.png').convert('RGB')).astype(float)
L=head[...,0]*.3+head[...,1]*.59+head[...,2]*.11
SKIN=np.median(head[L>200],0)
for n in (0,1):
    im=Image.open(WIL/f'cheeks-{n}.png').convert('RGBA'); px,py=map(int,(WIL/f'cheeks-{n}.txt').read_text().split()[:2])
    a=np.array(im).astype(float); l=a[...,0]*.3+a[...,1]*.59+a[...,2]*.11
    w=np.clip((l-60)/150,0,1)[...,None]          # branco -> pele, preto -> nanquim
    a[...,:3]=np.array([24,22,26])*(1-w)+SKIN*w
    sh=np.clip((235-l)/60,0,1)[...,None]*(l[...,None]>120)   # sombras cinza do desenho viram pele sombreada
    a[...,:3]=a[...,:3]*(1-0.12*sh)
    im=Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA')
    im=im.resize((round(im.width*S),round(im.height*S)),Image.LANCZOS)
    (P/f'cheeks-{n}.txt').write_text(f'{round(px*S-DX)} {round(py*S-DY)} 1'); im.save(P/f'cheeks-{n}.png')
A=compor.read_anims(EAT); fr=A[('eat',255)]
hide={compor.kh(s) for s in ('headbase_hat','hair_hat')}
o=Image.new('RGBA',(300*3,360),(70,62,45,255)); Pp=compor.Parts(P)
for j,i in enumerate([20,40,60]):
    c=compor.compose(Pp,fr[i],size=560,origin=(280,520),hide=hide).crop((130,200,430,560)); o.alpha_composite(c,(j*300,0))
o.save(out)
