"""Syntax + behavioral checks using liblua, no DST engine needed."""
import ctypes, ctypes.util, pathlib, struct, xml.etree.ElementTree as ET
root=pathlib.Path(__file__).resolve().parents[1]
lib=ctypes.CDLL(ctypes.util.find_library('lua5.4') or 'liblua5.4.so.0')
lib.luaL_newstate.restype=ctypes.c_void_p
L=lib.luaL_newstate()
lib.luaL_openlibs.argtypes=[ctypes.c_void_p];lib.luaL_openlibs(L)
lib.luaL_loadfilex.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p]
lib.luaL_loadstring.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
lib.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_longlong,ctypes.c_void_p]
lib.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p];lib.lua_tolstring.restype=ctypes.c_char_p
lib.lua_settop.argtypes=[ctypes.c_void_p,ctypes.c_int]
def check(code):
 if code:raise RuntimeError(lib.lua_tolstring(L,-1,None).decode())
for p in sorted((root/'blink').rglob('*.lua')):
 check(lib.luaL_loadfilex(L,str(p).encode(),None));lib.lua_settop(L,0)
print('PASS: all mod Lua files parse (Lua 5.4; DST uses Lua 5.1-compatible syntax).')
setup=f'package.path = "{root}/blink/scripts/?.lua;" .. package.path'
check(lib.luaL_loadstring(L,setup.encode()));check(lib.lua_pcallk(L,0,0,0,0,None))
check(lib.luaL_loadfilex(L,str(root/'tests/behavior.lua').encode(),None));check(lib.lua_pcallk(L,0,0,0,0,None))
atlases=0
for p in [*(root/'blink/images').rglob('*.xml'),*(root/'blink/bigportraits').rglob('*.xml')]:
 atlases+=1
 tree=ET.parse(p);tex=p.parent/tree.find('Texture').attrib['filename'];b=tex.read_bytes()
 assert b[:4]==b'KTEX'
 header,w,h,pitch,n=struct.unpack_from('<IHHHI',b,4)
 assert (header>>4)&31==4 and (header>>13)&31==1
 assert pitch==w*4 and n==w*h*4 and len(b)==18+n
 assert len(tree.findall('./Elements/Element'))>0
print(f'PASS: {atlases} atlas/KTEX pairs, header, dimensions, payload and references.')
from PIL import Image
for name in ['blink_dagger','blink_impeto']:
 b=(root/f'blink/images/inventoryimages/{name}.tex').read_bytes();w,h=struct.unpack_from('<HH',b,8)
 assert (w,h)==(64,64),name
 assert ET.parse(root/f'blink/images/inventoryimages/{name}.xml').find('./Elements/Element').attrib['name']==name+'.tex'
exp=root/'art/spriter/blink_dagger';scml=ET.parse(exp/'blink_dagger.scml').getroot()
folders={f.attrib['name']:f for f in scml.findall('folder')}
assert set(folders)=={'blink_dagger','swap_blink_dagger'}
for fname,f in folders.items():
 for file in f.findall('file'):
  a=file.attrib;assert a['name'].startswith(fname+'/'+fname+'-')
  im=Image.open(exp/a['name']);assert im.mode=='RGBA' and im.size==(int(a['width']),int(a['height']))
  assert 0<=float(a['pivot_x'])<=1 and 0<=float(a['pivot_y'])<=1
  assert im.getpixel((int(float(a['pivot_x'])*im.width),int((1-float(a['pivot_y']))*im.height)))[3]>0 or fname=='blink_dagger'
ent=scml.find('entity');assert ent.attrib['name']=='blink_dagger'
anims={a.attrib['name'] for a in ent.findall('animation')};assert 'idle' in anims
for an in ent.findall('animation'):
 for o in an.iter('object'):assert int(o.attrib['folder'])<len(folders)
import zipfile
z=zipfile.ZipFile(root/'blink/anim/blink_dagger.zip');assert {'build.bin','anim.bin','atlas-0.tex'}<=set(z.namelist())
bb=z.read('build.bin');assert bb[:4]==b'BILD' and b'swap_blink_dagger' in bb and b'blink_dagger' in bb
ab=z.read('anim.bin');assert ab[:4]==b'ANIM' and b'idle' in ab
def kh(t):
 h=0
 for c in t.lower():h=(ord(c)+(h<<6)+(h<<16)-h)&0xffffffff
 return h
o=4
def rd(fmt):
 global o;v=struct.unpack_from(fmt,bb,o);o+=struct.calcsize(fmt);return v
def rs():
 global o;n,=rd('<I');o+=n
ver,ns,nf=rd('<III');rs();na,=rd('<I');[rs() for _ in range(na)]
cover={}
for _ in range(ns):
 h,n=rd('<II');cover[h]=set()
 for _ in range(n):
  (num,dur),bbox,(ai,ac)=rd('<II'),rd('<ffff'),rd('<II');assert ac>0 and ac%6==0
  cover[h]|=set(range(num,num+dur))
# Quadros de swap_object pedidos pelas animacoes do jogador (lidos de player_idles/basic/attacks/actions).
assert {0,1,2,5,6,7,8}<=cover[kh('swap_blink_dagger')],cover
assert 0 in cover[kh('blink_dagger')]
assert not (root/'blink/exported').exists(),'exported/ faria o autocompiler sobrescrever a correcao'
print('PASS: anim/blink_dagger.zip: mao cobre quadros 0-2 e 5-8 (como a lanca original); chao no quadro 0.')
def build_cover(zpath):
 global bb,o
 zz=zipfile.ZipFile(zpath);bb=zz.read('build.bin');o=4
 ver,ns,nf=rd('<III');rs();na,=rd('<I');[rs() for _ in range(na)]
 cov={}
 for _ in range(ns):
  h,n=rd('<II');cov[h]=set()
  for _ in range(n):
   (num,dur),bbox,(ai,ac)=rd('<II'),rd('<ffff'),rd('<II');assert ac>0 and ac%6==0;cov[h]|=set(range(num,num+dur))
 nv,=rd('<I');o+=nv*24;nh,=rd('<I')
 for _ in range(nh):rd('<I');rs()
 assert o==len(bb),'build.bin com bytes sobrando'
 t=zz.read('atlas-0.tex');assert t[:4]==b'KTEX'
 hdr,=struct.unpack_from('<I',t,4);mips=(hdr>>13)&31;assert (hdr>>4)&31==2 and mips>1,'atlas DXT5 com mipmaps'
 heads=[struct.unpack_from('<HHHI',t,8+10*i) for i in range(mips)]
 assert heads[-1][:2]==(1,1) and len(t)==8+10*mips+sum(h[3] for h in heads)
 return cov
cov=build_cover(root/'blink/anim/blink_impeto.zip')
# Quadros do amuleto original no corpo (0-8, 14, 15); 9-10 sao costas, onde o pingente some de proposito.
assert cov[kh('swap_blink_impeto')]=={0,1,2,3,4,5,6,7,8,14,15},cov
assert 0 in cov[kh('blueamulet')]
assert {0,1,2,5,6,7,8}<=build_cover(root/'blink/anim/blink_dagger.zip')[kh('swap_blink_dagger')]
fc=build_cover(root/'blink/anim/blink_dagger_float.zip')
assert 2 in fc[kh('blink_dagger_float')],'quadro 2 pedido pelo item boiando (floating_items.zip)'
# O jogo pode indexar quadros pela posicao na lista: toda peca precisa de entradas suficientes
# para o maior quadro pedido (mao/agua: ate a posicao 2 como a swap_spear de 5 quadros; corpo da Pedra: 11 como o amuleto).
import struct as _st
def counts(zpath):
 b2=zipfile.ZipFile(zpath).read('build.bin');q=[4]
 def r2(fmt):
  v=_st.unpack_from(fmt,b2,q[0]);q[0]+=_st.calcsize(fmt);return v
 def s2():
  n,=r2('<I');q[0]+=n
 _,ns,_=r2('<III');s2();na,=r2('<I');[s2() for _ in range(na)]
 out={}
 for _ in range(ns):
  h,n=r2('<II');[r2('<IIffffII') for _ in range(n)];out[h]=n
 return out
dc=counts(root/'blink/anim/blink_dagger.zip');ic=counts(root/'blink/anim/blink_impeto.zip')
fl=counts(root/'blink/anim/blink_dagger_float.zip')
assert dc[kh('swap_blink_dagger')]>=5 and kh('blink_dagger_float') not in dc and fl=={kh('blink_dagger_float'):2},(dc,fl)
assert fc[kh('blink_dagger_float')]>={0,1,2,5,6,7},'agua cobre os quadros como a swap_ham_bat'
assert ic[kh('swap_blink_impeto')]==11,ic
print('PASS: peca da agua em build separado como a swap_ham_bat (quadros 0-2 e 5-7); mao 5 quadros; corpo da Pedra 11.')
mm=(root/'blink/modmain.lua').read_text()
assert 'AddRecipe2("blink_impeto"' in mm and 'G.TECH.MAGIC_THREE' in mm.split('AddRecipe2("blink_impeto"')[1].split('AddRecipe2')[0]
dg=mm.split('AddRecipe2("blink_dagger"')[1].split('AddRecipe2')[0]
assert 'G.TECH.SCIENCE_TWO' in dg and '"goldnugget",1' in dg and '"flint",2' in dg and '"nitre",1' in dg
rn=mm.split('AddRecipe2("blink_impeto"')[1].split('AddRecipe2')[0]
assert all(x in rn for x in ('"purplegem",1','"moonrocknugget",3','"goldnugget",4','"nightmarefuel",2'))
import re as _re
info=(root/'blink/modinfo.lua').read_text()
assert _re.findall(r'name="(\w+)"',info)==['language'],'menu do mod: so idioma'
assert 'GetModConfigData("language")' in mm and mm.count('GetModConfigData')==1
assert 'BLINK_HEALTH = 125' in mm and 'BLINK_SANITY = 250' in mm and 'stone_uses=30' in mm
bc=build_cover(root/'blink/anim/blink.zip')
need={'headbase':range(5),'headbase_hat':range(5),'hair':range(4),'hair_hat':range(4),'face':range(33),'cheeks':range(2),
 'torso':range(11),'torso_pelvis':range(11),'arm_lower':range(7),'arm_upper_skin':range(3),'hand':range(20),'leg':range(11),'foot':range(8)}
for n,rg in need.items():
 assert set(rg)<=bc[kh(n)],(n,sorted(bc.get(kh(n),[])))
pb=(root/'blink/scripts/prefabs/blink.lua').read_text();pn=(root/'blink/scripts/prefabs/blink_none.lua').read_text()
assert 'SetBuild("blink")' in pb and 'anim/blink.zip' in pb and 'wolfgang_mighty' not in pb
assert 'SetSymbolLightOverride("face"' not in pb  # 0.8.0: o rosto inclui pele; brilho criaria mascara a noite
assert 'normal_skin="blink"' in pn and 'build_name_override = "blink"' in pn and 'wolfgang_mighty' not in pn
assert 'ghost_blink_build' in pb and 'ghost_wilson_build' not in pb
assert 'ghost_skin="ghost_blink_build"' in pn and 'ghost_wilson_build' not in pn,'a skin decide o fantasma (skinner usa skin_data antes de ghostbuild)'
gz=zipfile.ZipFile(root/'blink/anim/ghost_blink_build.zip');gb=gz.read('build.bin')
assert b'ghost_blink_build' in gb[:64],'nome interno do build do fantasma'
gc=counts(root/'blink/anim/ghost_blink_build.zip')
assert all(gc.get(kh(n),0)>=c for n,c in {'ghost_Hat':1,'ghost_body':1,'ghost_tail':16,'ghost_eyes':4,'ghost_FX':39}.items()),gc
print('PASS: fantasma proprio (ghost_blink_build): todas as pecas do fantasma do jogo, cabelo do BLINK.')
print('PASS: corpo do BLINK: build proprio com todas as pecas/quadros pedidos pelas animacoes do jogador; prefab e skin apontam para "blink".')
for zp in sorted((root/'blink/anim').glob('*.zip')):
 zb=zipfile.ZipFile(zp).read('build.bin');q=[4]
 def r3(fmt):
  v=_st.unpack_from(fmt,zb,q[0]);q[0]+=_st.calcsize(fmt);return v
 def s3():
  n,=r3('<I');q[0]+=n
 _,ns,_=r3('<III');s3();na,=r3('<I');[s3() for _ in range(na)];hs=[]
 for _ in range(ns):
  h,n=r3('<II');hs.append(h);[r3('<IIffffII') for _ in range(n)]
 assert hs==sorted(hs),zp.name+': simbolos fora de ordem de hash (o jogo nao os encontra)'
print('PASS: todos os builds com simbolos em ordem crescente de hash, como os do jogo.')
print('PASS: receitas: Runa (gema roxa, 3 lunares, 4 ouros, 2 pesadelo) no Manipulador das Sombras; Dagger (2 silex, 1 salitre, 1 ouro) no Motor de Alquimia; vida 125, sanidade 250, Runa 30 usos.')
print('PASS: anim/blink_impeto.zip: corpo nos quadros do amuleto original, chao no banco nativo; atlas DXT5 com mipmaps.')
import numpy as np
bad=[]
for p in [*(root/'blink/images').rglob('*.tex'),*(root/'blink/bigportraits').rglob('*.tex')]:
 b=p.read_bytes();w,h=struct.unpack_from('<HH',b,8);a=np.frombuffer(b[18:18+w*h*4],np.uint8).reshape(h,w,4).astype(int)
 if (a[:,:,:3].max(axis=2)>a[:,:,3]+1).any():bad.append(p.name)
assert not bad,bad
print('PASS: todas as texturas de interface com alfa pre-multiplicado (sem halo claro nas bordas).')
print('PASS: 2 icones de inventario 64x64 e projeto Spriter da Dagger (pastas, imagens, pivos, banco e animacao idle).')
print('NOT RUN: DST startup, rendering, Mod Tools autocompiler, real combat, multiplayer and caves.')
