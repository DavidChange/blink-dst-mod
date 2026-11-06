import random, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
random.seed(7);S=256
def layer():return Image.new('RGBA',(S,S))
OUT=(24,24,30,255)
stone=[(128,22),(188,52),(214,118),(196,186),(140,230),(80,214),(42,152),(52,82),(86,40)]
base=layer();d=ImageDraw.Draw(base)
d.polygon(stone,fill=OUT)
inner=[(int(128+(x-128)*0.9),int(128+(y-128)*0.9)) for x,y in stone]
# moonrock body with painterly noise
body=layer();ImageDraw.Draw(body).polygon(inner,fill=(150,160,175,255))
noise=np.random.default_rng(3).normal(0,14,(S,S,1)).repeat(3,2)
arr=np.array(body).astype(float);arr[:,:,:3]+=noise;arr=np.clip(arr,0,255).astype(np.uint8)
body=Image.fromarray(arr).filter(ImageFilter.GaussianBlur(1.2))
mask=layer();ImageDraw.Draw(mask).polygon(inner,fill=(255,255,255,255));body.putalpha(mask.split()[3])
# shading: darker lower-right
shade=layer();sd=ImageDraw.Draw(shade)
sd.polygon([(196,120),(214,118),(196,186),(140,230),(110,222),(170,170)],fill=(40,50,70,110))
sd.polygon([(86,40),(128,22),(150,40),(100,70),(66,88),(52,82)],fill=(255,255,255,70))
shade=shade.filter(ImageFilter.GaussianBlur(6));shade.putalpha(ImageChops.multiply(shade.split()[3],mask.split()[3]))
base.alpha_composite(body);base.alpha_composite(shade)
d=ImageDraw.Draw(base)
# gold band across the stone
band=[(48,128),(208,108),(212,132),(50,152)]
d.polygon(band,fill=(205,160,60,255),outline=OUT,width=5)
d.line([(56,134),(204,116)],fill=(250,215,120,255),width=3)
# three gems set in the band
for cx,cy,col in [(84,136,(70,120,235)),(128,128,(220,55,60)),(172,122,(150,70,200))]:
    gem=[(cx,cy-17),(cx+14,cy),(cx,cy+17),(cx-14,cy)]
    d.polygon(gem,fill=col+(255,),outline=OUT,width=4)
    d.polygon([(cx,cy-12),(cx+6,cy-3),(cx-4,cy-2)],fill=(255,255,255,170))
# electric crack (cyan) with glow
crack=[(118,34),(104,70),(126,82),(108,104)]
crack2=[(150,150),(136,176),(158,186),(140,220)]
glow=layer();gd=ImageDraw.Draw(glow)
for c in (crack,crack2): gd.line(c,fill=(80,230,255,255),width=14,joint='curve')
glow=glow.filter(ImageFilter.GaussianBlur(7))
base.alpha_composite(glow)
for c in (crack,crack2):
    d.line(c,fill=OUT,width=9,joint='curve');d.line(c,fill=(150,245,255,255),width=5,joint='curve')
# outer cyan aura
aura=base.split()[3].filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10)).point(lambda v:int(v*0.45))
al=Image.new('RGBA',(S,S),(90,220,255,0));al.putalpha(aura)
final=Image.alpha_composite(al,base)
bbox=final.getbbox();final=final.crop(bbox)
sc=60/max(final.size);final=final.resize((round(final.width*sc),round(final.height*sc)),Image.LANCZOS)
icon=Image.new('RGBA',(64,64));icon.alpha_composite(final,((64-final.width)//2,(64-final.height)//2))
icon.save('/home/claude/art/out_icon_blink_impeto.png')
prev=Image.new('RGBA',(400,200),(110,170,110,255))
prev.alpha_composite(icon.resize((192,192),Image.NEAREST),(4,4));prev.alpha_composite(icon,(250,68))
dag=Image.open('/home/claude/art/out_icon_blink_dagger.png');prev.alpha_composite(dag,(320,68))
prev.save('/home/claude/art/stone_prev.png')
