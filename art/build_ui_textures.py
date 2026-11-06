"""Encode generated concept art as uncompressed KTEX UI assets.
Format reference: nsimplex/ktools src/common/ktex (not copied implementation).
This does not build skeletal animations. Requires Pillow.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import struct, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import klei_anim
ROOT=Path(__file__).resolve().parents[1]
source=Image.open(ROOT/'art/BLINK_conceito.png').convert('RGBA')
def save(im,path,names):
 path=ROOT/'blink'/path;path.parent.mkdir(parents=True,exist_ok=True)
 # KTEX little endian: platform 0, RGBA 4, 2D 1, one mip, flags 3, fill 4095.
 # Alfa pre-multiplicado, como nas texturas do jogo (sem isso surgem halos claros nas bordas).
 path.with_suffix('.tex').write_bytes(klei_anim.ktex_rgba(im))
 elems='\n'.join(f'    <Element name="{n}.tex" u1="0" u2="1" v1="0" v2="1" />' for n in names)
 path.with_suffix('.xml').write_text(f'<Atlas>\n  <Texture filename="{path.name}.tex" />\n  <Elements>\n{elems}\n  </Elements>\n</Atlas>\n')
for path,size,names in [
 ('bigportraits/blink',(512,512),['blink','blink_none','blink_oval']),
 ('images/selectscreen_portraits/blink',(256,256),['blink']),
 ('images/selectscreen_portraits/blink_silho',(256,256),['blink_silho']),
 ('images/saveslot_portraits/blink',(128,128),['blink']),
 ('images/map_icons/blink',(64,64),['blink']),
 ('images/avatars/avatar_blink',(64,64),['avatar_blink']),
 ('images/avatars/avatar_ghost_blink',(64,64),['avatar_ghost_blink']),
 ('images/avatars/self_inspect_blink',(128,128),['self_inspect_blink']),
]:
 im=ImageOps.contain(source,size)
 canvas=Image.new('RGBA',size);canvas.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2))
 save(canvas,path,names)
for path in ['images/names_blink','images/names_gold_blink']:
 canvas=Image.new('RGBA',(256,64));d=ImageDraw.Draw(canvas)
 try: font=ImageFont.truetype('DejaVuSans-Bold.ttf',42)
 except OSError: font=ImageFont.load_default()
 d.text((128,32),'BLINK',anchor='mm',fill=(105,220,255,255),font=font)
 save(canvas,path,['blink'])
print('10 KTEX textures and 10 atlases created.')
