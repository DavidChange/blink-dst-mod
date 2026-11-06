# Uso: python3 compilar_anim.py art/v063 blink/anim <zip antigo da Dagger (fornece anim.bin do chao)>
import sys,zipfile
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent))
import klei_anim
A=Path(sys.argv[1]);DST=Path(sys.argv[2]);OLD=sys.argv[3]
def img(n):
    im=Image.open(A/f'{n}.png').convert('RGBA');px,py=map(int,(A/f'{n}.txt').read_text().split());return im,(px,py)
def scaled(im,pv,k):
    if k==1:return im,pv
    s=im.resize((round(im.width*k),round(im.height*k)),Image.LANCZOS);return s,(round(pv[0]*k),round(pv[1]*k))
sw,swp=img('dagger_swap');gr,grp=img('dagger_ground')
small=scaled(sw,swp,0.8);big=scaled(sw,swp,1.1)
anim=zipfile.ZipFile(OLD).read('anim.bin')
klei_anim.build_zip(DST/'blink_dagger.zip','blink_dagger',[
    ('blink_dagger',[(0,1,gr,grp)]),
    ('swap_blink_dagger',[(0,3,sw,swp),(5,1,small[0],small[1]),(6,1,sw,swp),(7,1,big[0],big[1]),(8,1,sw,swp)]),
],anim_bin=anim)
# Item boiando: o banco nativo "floating_item" desenha "swap_spear" (quadro 2) girado 90 graus.
# Como TODAS as armas do jogo (ex.: swap_ham_bat), a peca fica num build SEPARADO do item:
# a substituicao a partir do proprio build do item nao apareceu no jogo (0.6.8/0.6.9).
# Pivo escolhido para o centro cair onde fica o da Lanca (centro x=9, y=0 antes do giro).
fpv=(round(sw.width/2-9),round(sw.height/2))
klei_anim.build_zip(DST/'blink_dagger_float.zip','blink_dagger_float',[
    ('blink_dagger_float',[(0,3,sw,fpv),(5,3,sw,fpv)]),   # mesma estrutura da swap_ham_bat
])
ig,igp=img('impeto_ground')
torso=[]
for n in [0,1,2,3,4,5,6,7,8,14,15]:
    im,pv=img(f'impeto_torso_{n}');torso.append((n,1,im,pv))
klei_anim.build_zip(DST/'blink_impeto.zip','blink_impeto',[
    ('blueamulet',[(0,1,ig,igp)]),            # nome exigido pela animacao 'blueamulet' do banco nativo 'amulets'
    ('swap_blink_impeto',torso),
])
print('ok')
