"""Uso: python3 corrigir_build_dagger.py <zip compilado pelas Mod Tools> <zip de saida>
Reescreve build.bin da Dagger: o simbolo da mao passa a cobrir os quadros que as
animacoes do jogador pedem (0-2, 5-8), como na swap_spear original."""
import struct,zipfile,sys
src,dst=sys.argv[1],sys.argv[2]
z=zipfile.ZipFile(src);b=z.read('build.bin');o=4
def u(fmt):
    global o;v=struct.unpack_from(fmt,b,o);o+=struct.calcsize(fmt);return v
def s():
    n,=u('<I');global o;r=b[o:o+n];o+=n;return r
ver,nsym,nfr=u('<III');name=s();na,=u('<I');atl=[s() for _ in range(na)]
syms=[]
for i in range(nsym):
    h,nf=u('<II');syms.append([h,[[*u('<II'),*u('<ffff'),*u('<II')] for _ in range(nf)]])
nv,=u('<I');verts=[u('<ffffff') for _ in range(nv)]
nh,=u('<I');hashes=[(u('<I')[0],s()) for _ in range(nh)]
assert o==len(b)
def kh(t):
    h=0
    for c in t.lower():h=(ord(c)+(h<<6)+(h<<16)-h)&0xffffffff
    return h
SWAP=kh('swap_blink_dagger')
out_syms=[];out_verts=[]
for h,frames in syms:
    nf=[]
    if h==SWAP:
        f=frames[0];quad=verts[f[6]:f[6]+f[7]]
        plan=[(0,3,1.0),(5,1,0.8),(6,1,1.0),(7,1,1.1),(8,1,1.0)]
    else:
        plan=None
    for f in frames if plan is None else [frames[0]]*len(plan):
        q=verts[f[6]:f[6]+f[7]]
        num,dur,k=(f[0],f[1],1.0) if plan is None else plan[len(nf)]
        q=[(v[0]*k,v[1]*k,*v[2:]) for v in q]   # escala em torno da empunhadura (pivo)
        nf.append([num,dur,f[2]*k,f[3]*k,f[4]*k,f[5]*k,len(out_verts),len(q)]);out_verts+=q
    out_syms.append((h,nf))
w=bytearray(b'BILD')
w+=struct.pack('<III',ver,len(out_syms),sum(len(f) for _,f in out_syms))
def ws(x):w.extend(struct.pack('<I',len(x))+x)
ws(name);w+=struct.pack('<I',len(atl));[ws(a) for a in atl]
for h,frames in out_syms:
    w+=struct.pack('<II',h,len(frames))
    for f in frames:w+=struct.pack('<II',f[0],f[1])+struct.pack('<ffff',*f[2:6])+struct.pack('<II',f[6],f[7])
w+=struct.pack('<I',len(out_verts))
for v in out_verts:w+=struct.pack('<ffffff',*v)
w+=struct.pack('<I',len(hashes))
for h,t in hashes:w+=struct.pack('<I',h);ws(t)
with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as out:
    for info in z.infolist():
        data=bytes(w) if info.filename=='build.bin' else z.read(info.filename)
        zi=zipfile.ZipInfo(info.filename,date_time=(1980,1,1,0,0,0));zi.compress_type=info.compress_type
        out.writestr(zi,data)
print('ok',len(w),'bytes')
