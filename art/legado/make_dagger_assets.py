import math, numpy as np
from PIL import Image, ImageFilter
src=Image.open('/home/claude/art/dagger_clean.png').convert('RGBA')  # cropped, offset (ox,oy) from original
# Grip point = middle of the handle in reference coords, converted to crop coords.
OX,OY=7,37
grip=(410-OX,95-OY)
def glow(im,color=(90,220,255),radius=6,strength=0.55):
    a=im.split()[3]
    g=a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(radius))
    g=g.point(lambda v:int(v*strength))
    layer=Image.new('RGBA',im.size,color+(0,));layer.putalpha(g)
    return Image.alpha_composite(layer,im)
def pad(im,p):
    c=Image.new('RGBA',(im.width+2*p,im.height+2*p));c.paste(im,(p,p));return c
# 1) Inventory icon 64x64 with subtle electric glow.
icon=pad(src,40);icon=glow(icon,radius=12,strength=0.6)
bbox=icon.getbbox();icon=icon.crop(bbox)
s=60/max(icon.size);icon=icon.resize((max(1,round(icon.width*s)),max(1,round(icon.height*s))),Image.LANCZOS)
canvas=Image.new('RGBA',(64,64));canvas.alpha_composite(icon,((64-icon.width)//2,(64-icon.height)//2))
canvas.save('/home/claude/art/out_icon_blink_dagger.png')
# 2) Ground image (lying item), longest side 120 px.
g=src.copy();s=120/max(g.size);g=g.resize((round(g.width*s),round(g.height*s)),Image.LANCZOS)
g.save('/home/claude/art/out_ground.png')
# 3) Held image: rotate so pommel points down from the grip and blade rises.
pommel=(500-OX,60-OY);guard=(300-OX,150-OY)
ang=math.degrees(math.atan2(pommel[1]-guard[1],pommel[0]-guard[0]))  # screen coords, y down
rot=-(90-ang)   # PIL rotates counter-clockwise visually
marker=Image.new('L',src.size,0);marker.putpixel(grip,255)
big=pad(src,200);bm=pad(marker.convert('RGBA'),200)
r=big.rotate(rot,resample=Image.BICUBIC,expand=True)
rm=Image.new('L',big.size,0);rm.paste(marker,(200,200));rm=rm.rotate(rot,resample=Image.BILINEAR,expand=True)
bbox=r.getbbox();r=r.crop(bbox);rm=rm.crop(bbox)
s=150/max(r.size);w,h=round(r.width*s),round(r.height*s)
r=r.resize((w,h),Image.LANCZOS);rm=rm.resize((w,h),Image.BILINEAR)
arr=np.array(rm,dtype=float);yy,xx=np.unravel_index(arr.argmax(),arr.shape)
r.save('/home/claude/art/out_swap.png')
open('/home/claude/art/out_swap_pivot.txt','w').write(f"{w} {h} {xx} {yy}\n")
print('rot',rot,'swap',w,h,'grip',xx,yy,'ground',g.size)
# preview sheet
prev=Image.new('RGBA',(520,240),(110,170,110,255))
prev.alpha_composite(canvas.resize((192,192),Image.NEAREST),(10,24))
prev.alpha_composite(g,(215,60));sw=r.copy();prev.alpha_composite(sw,(360,40))
from PIL import ImageDraw;d=ImageDraw.Draw(prev);d.ellipse((360+xx-4,40+yy-4,360+xx+4,40+yy+4),outline=(255,0,0),width=2)
prev.save('/home/claude/art/assets_prev.png')
