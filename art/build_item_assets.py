"""Gera atlas/KTEX dos icones de inventario e o projeto Spriter (exported/) da Dagger.
Os PNG de origem ficam em art/ e exported/; o anim/blink_dagger.zip e gerado pelo
autocompiler das Don't Starve Mod Tools (Steam) ao abrir o jogo. Requer Pillow."""
from pathlib import Path
from PIL import Image
import struct, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import klei_anim
ROOT=Path(__file__).resolve().parents[1]
def save_ktex(im,path,name):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.with_suffix('.tex').write_bytes(klei_anim.ktex_rgba(im))  # alfa pre-multiplicado
    path.with_suffix('.xml').write_text(f'<Atlas>\n  <Texture filename="{path.name}.tex" />\n  <Elements>\n    <Element name="{name}.tex" u1="0" u2="1" v1="0" v2="1" />\n  </Elements>\n</Atlas>\n')
for name in ['blink_dagger','blink_impeto']:
    im=Image.open(ROOT/f'art/icon_{name}.png').convert('RGBA');assert im.size==(64,64)
    save_ktex(im,ROOT/f'blink/images/inventoryimages/{name}',name)
# Spriter: pivot da imagem da mao = ponto do cabo (empunhadura).
exp=ROOT/'art/spriter/blink_dagger'
ground=Image.open(exp/'blink_dagger/blink_dagger-0.png');swap=Image.open(exp/'swap_blink_dagger/swap_blink_dagger-0.png')
GRIP=(81,122)
px,py=GRIP[0]/swap.width,1-GRIP[1]/swap.height
def anim(aid,name,folder,timeline):
    return f'''        <animation id="{aid}" name="{name}" length="100" interval="100">
            <mainline>
                <key id="0" time="0">
                    <object_ref id="0" timeline="0" key="0" z_index="0"/>
                </key>
            </mainline>
            <timeline id="0" name="{timeline}">
                <key id="0" time="0" spin="1">
                    <object folder="{folder}" file="0" x="0" y="0" angle="0"/>
                </key>
            </timeline>
        </animation>
'''
scml=f'''<?xml version="1.0" encoding="UTF-8"?>
<spriter_data scml_version="1.0" generator="BrashMonkey Spriter" generator_version="b5">
    <folder id="0" name="blink_dagger">
        <file id="0" name="blink_dagger/blink_dagger-0.png" width="{ground.width}" height="{ground.height}" pivot_x="0.5" pivot_y="0.25"/>
    </folder>
    <folder id="1" name="swap_blink_dagger">
        <file id="0" name="swap_blink_dagger/swap_blink_dagger-0.png" width="{swap.width}" height="{swap.height}" pivot_x="{px:.4f}" pivot_y="{py:.4f}"/>
    </folder>
    <entity id="0" name="blink_dagger">
{anim(0,'idle',0,'blink_dagger')}{anim(1,'swap_preview',1,'swap_blink_dagger')}    </entity>
</spriter_data>
'''
(exp/'blink_dagger.scml').write_text(scml)
print('2 icones KTEX e exported/blink_dagger/blink_dagger.scml gerados.')
