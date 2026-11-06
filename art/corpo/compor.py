"""Monta um quadro de animacao do jogador com as pecas de uma pasta (simbolo-quadro.png + pivo)."""
import struct,zipfile,sys
from pathlib import Path
import numpy as np
from PIL import Image
def kh(t):
    h=0
    for c in t.lower():h=(ord(c)+(h<<6)+(h<<16)-h)&0xffffffff
    return h
def read_anims(zpath):
    b=zipfile.ZipFile(zpath).read('anim.bin');o=[4]
    def u(fmt):
        v=struct.unpack_from(fmt,b,o[0]);o[0]+=struct.calcsize(fmt);return v
    def s():
        n,=u('<I');r=b[o[0]:o[0]+n].decode(errors='replace');o[0]+=n;return r
    ver,ne,nf,nev,na=u('<IIIII');anims={}
    for i in range(na):
        name=s();fac,=u('<B');root,fr=u('<If');n,=u('<I');frames=[]
        for j in range(n):
            u('<ffff');ev,=u('<I');u('<'+'I'*ev);el,=u('<I');els=[]
            for k in range(el):
                sym,frame,layer=u('<III');m=u('<fffffff');els.append((sym,frame,m))
            frames.append(els)
        anims[(name,fac)]=frames
    return anims
class Parts:
    def __init__(self,folder):
        self.f=Path(folder);self.idx={}
        for p in self.f.glob('*.png'):
            sym,num=p.stem.rsplit('-',1);px,py,dur=map(int,p.with_suffix('.txt').read_text().split())
            self.idx.setdefault(kh(sym),[]).append((int(num),dur,p,(px,py)))
    def get(self,h,frame):
        for num,dur,p,pv in sorted(self.idx.get(h,[])):
            if num<=frame<num+dur:return Image.open(p).convert('RGBA'),pv
        return None
def compose(parts,frame_els,scale=1.0,size=420,origin=(210,330),hide=()):
    canvas=Image.new('RGBA',(size,size))
    els=list(frame_els)
    for sym,frame,(a,b,c,d,tx,ty,z) in reversed(els):
        if sym in hide:continue
        got=parts.get(sym,frame)
        if not got:continue
        im,(px,py)=got
        # ponto da imagem (u,v) -> local (u-px, v-py) -> mundo (a*x+c*y+tx, b*x+d*y+ty)
        M=np.array([[a,c,tx],[b,d,ty]])
        A=np.array([[a,c],[b,d]])*scale
        inv=np.linalg.inv(A)
        ox,oy=origin
        # mundo->imagem: x_img = inv*(P - (t*scale+origin)) + pivot
        T=np.array([tx*scale+ox,ty*scale+oy])
        coeffs=(inv[0,0],inv[0,1],-(inv[0,0]*T[0]+inv[0,1]*T[1])+px, inv[1,0],inv[1,1],-(inv[1,0]*T[0]+inv[1,1]*T[1])+py)
        layer=im.transform(canvas.size,Image.AFFINE,coeffs,resample=Image.BICUBIC)
        canvas.alpha_composite(layer)
    return canvas
