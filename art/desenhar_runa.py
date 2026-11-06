"""Runa Eletrica: variantes A/B/C (o mod usa a B, escolhida pelo usuario) e corrente dourada."""
import math
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
INK=(22,20,26,255)
BOLT=[(90,72),(203,53),(211,64),(183,128),(168,155),(230,155),(235,165),(188,253),(78,375),(84,300),(83,247),(42,240),(80,167),(115,143),(65,137)]
GEMS=[((143,104),(215,55,55)),((136,198),(155,70,215)),((118,282),(55,120,235))]
GOLD=(226,178,58,255);GOLD_HI=(255,226,130,255);GOLD_LO=(150,104,30,255)
STYLES={
 'A':dict(face=(196,198,196),side=(112,114,120),lines=(90,94,104),glow=False,rim=False,twine=True,settings=False,specks=False),
 'B':dict(face=(84,94,114),side=(42,46,60),lines=(110,230,255),glow=True,rim=True,twine=False,settings=True,specks=False),
 'C':dict(face=(186,204,222),side=(98,116,140),lines=(70,190,235),glow=True,rim=True,twine=False,settings=False,specks=True),
}
def gem_shape(d,P,gx,gy,r,col,ow):
    dia=[(gx,gy-r),(gx+r,gy),(gx,gy+r),(gx-r,gy)]
    d.polygon(P(dia),fill=INK);d.line(P(dia)+[P(dia)[0]],fill=INK,width=int(ow),joint='curve')
    k=0.78;dark=tuple(int(c*0.6) for c in col)+(255,)
    d.polygon(P([(gx,gy-r*k),(gx+r*k,gy),(gx,gy+r*k),(gx-r*k,gy)]),fill=dark)
    d.polygon(P([(gx,gy-r*k),(gx+r*k,gy),(gx,gy),(gx-r*k,gy)]),fill=col+(255,))
    lc=tuple(min(255,int(c+0.5*(255-c))) for c in col)+(255,)
    d.polygon(P([(gx-r*k,gy),(gx,gy-r*k),(gx-r*0.1,gy-r*0.1)]),fill=lc)
    d.polygon(P([(gx-r*0.42,gy-r*0.22),(gx-r*0.12,gy-r*0.52),(gx-r*0.02,gy-r*0.36),(gx-r*0.32,gy-r*0.06)]),fill=(255,255,255,240))
def draw(style,height,xscale=1.0,gem=60,ss=4):
    S=STYLES[style]
    xs=[p[0] for p in BOLT];ys=[p[1] for p in BOLT]
    x0,y0=min(xs)-30,min(ys)-60
    W=int((max(xs)-x0+40)*ss);H=int((max(ys)-y0+30)*ss)
    P=lambda pts,dx=0,dy=0:[((x-x0+dx)*ss,(y-y0+dy)*ss) for x,y in pts]
    im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im);ow=7*ss
    cx,cy=150,46
    d.ellipse(P([(cx-16,cy-19),(cx+16,cy+13)]),outline=INK,width=ow+4*ss)
    d.ellipse(P([(cx-16,cy-19),(cx+16,cy+13)]),outline=GOLD,width=5*ss)
    side=P(BOLT,9,9);d.polygon(side,fill=INK);d.line(side+[side[0]],fill=INK,width=ow*2,joint='curve')
    d.polygon(P(BOLT),fill=INK);d.line(P(BOLT)+[P(BOLT)[0]],fill=INK,width=ow*2,joint='curve')
    s2=Image.new('RGBA',(W,H));ImageDraw.Draw(s2).polygon(P(BOLT,7,7),fill=S['side']+(255,));im.alpha_composite(s2)
    d=ImageDraw.Draw(im);d.polygon(P(BOLT),fill=INK)
    mask=Image.new('L',(W,H));ImageDraw.Draw(mask).polygon(P(BOLT),fill=255)
    facemask=mask.filter(ImageFilter.MinFilter(4*ss+1))
    face=Image.new('RGBA',(W,H),S['face']+(255,))
    yy,xx=np.mgrid[0:H,0:W];t=(xx/W)*0.4+(yy/H)*0.6
    arr=np.array(face).astype(float);shade=(0.55-t)[...,None]*60;arr[:,:,:3]=np.clip(arr[:,:,:3]+shade,0,255)
    if S['specks']:
        rng=np.random.default_rng(5)
        for _ in range(26):
            px,py=rng.integers(40*ss,(W-40*ss)),rng.integers(60*ss,H-40*ss);r=rng.integers(4,11)*ss
            m=(xx-px)**2+(yy-py)**2<r*r;arr[m,:3]=arr[m,:3]*0.82
            m2=((xx-px+ss*2)**2+(yy-py+ss*2)**2<(r*0.7)**2);arr[m2,:3]=np.clip(arr[m2,:3]*1.08,0,255)
    face=Image.fromarray(arr.astype(np.uint8));face.putalpha(facemask);im.alpha_composite(face)
    d=ImageDraw.Draw(im)
    if S['rim']:
        rim=facemask.filter(ImageFilter.MinFilter(5*ss+1))
        ring=Image.fromarray((np.array(facemask)>0).astype(np.uint8)*255-(np.array(rim)>0).astype(np.uint8)*255)
        gl=Image.new('RGBA',(W,H),GOLD);gl.putalpha(ring);im.alpha_composite(gl)
        inner=rim.filter(ImageFilter.MinFilter(2*ss+1))
        ring2=Image.fromarray(((np.array(rim)>0)&~(np.array(inner)>0)).astype(np.uint8)*255)
        ik=Image.new('RGBA',(W,H),INK);ik.putalpha(ring2);im.alpha_composite(ik)
        d=ImageDraw.Draw(im)
    for line in [[(100,92),(118,84)],[(176,72),(186,68),(182,82)],[(95,213),(108,206),(104,222)],[(176,182),(192,176)],[(152,236),(170,226),(162,242)],[(96,322),(104,312)]]:
        if S['glow']:
            d.line(P(line),fill=(28,40,60,255),width=5*ss,joint='curve')
        d.line(P(line),fill=S['lines']+(255,),width=int(2.4*ss),joint='curve')
    if S['twine']:
        for a,b in [((52,236),(232,170)),((70,150),(205,120)),((80,300),(196,262))]:
            d.line(P([a,b]),fill=INK,width=8*ss);d.line(P([a,b]),fill=(126,88,58,255),width=4*ss)
    r=gem/2
    for (gx,gy),col in GEMS:
        if S['settings']:
            R=r*1.32;dia=[(gx,gy-R),(gx+R,gy),(gx,gy+R),(gx-R,gy)]
            d.polygon(P(dia),fill=INK);d.line(P(dia)+[P(dia)[0]],fill=INK,width=ow,joint='curve')
            R2=r*1.18;d.polygon(P([(gx,gy-R2),(gx+R2,gy),(gx,gy+R2),(gx-R2,gy)]),fill=GOLD)
            d.polygon(P([(gx-R2,gy),(gx,gy-R2),(gx,gy-R2*0.8),(gx-R2*0.8,gy)]),fill=GOLD_HI)
        gem_shape(d,P,gx,gy,r,col,ow*1.2)
    im=im.crop(im.getbbox())
    w=max(1,round(im.width*height/im.height*xscale))
    return im.resize((w,height),Image.LANCZOS)
def chain(d,pts,link=7):
    """Corrente dourada: elos alternados ao longo do caminho."""
    seg=[]
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
        L=math.hypot(x2-x1,y2-y1);n=max(1,int(L/(link*0.95)))
        for i in range(n):
            t=(i+0.5)/n;seg.append((x1+(x2-x1)*t,y1+(y2-y1)*t,math.atan2(y2-y1,x2-x1),len(seg)))
    for x,y,a,i in seg:
        hl,hw=link*0.62,(link*0.38 if i%2==0 else link*0.2)
        ca,sa=math.cos(a),math.sin(a)
        poly=[(x+ca*hl*math.cos(t)-sa*hw*math.sin(t),y+sa*hl*math.cos(t)+ca*hw*math.sin(t)) for t in np.linspace(0,2*math.pi,14)]
        d.polygon(poly,fill=INK)
    for x,y,a,i in seg:
        hl,hw=link*0.5,(link*0.26 if i%2==0 else link*0.1)
        ca,sa=math.cos(a),math.sin(a)
        poly=[(x+ca*hl*math.cos(t)-sa*hw*math.sin(t),y+sa*hl*math.cos(t)+ca*hw*math.sin(t)) for t in np.linspace(0,2*math.pi,14)]
        d.polygon(poly,fill=GOLD if i%2==0 else GOLD_HI)
