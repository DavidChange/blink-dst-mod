import cv2,numpy as np,sys
img=cv2.imread('/home/claude/art/dagger_cut.png',cv2.IMREAD_UNCHANGED)
m=(img[:,:,3]>127).astype(np.uint8)*255
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
def outline(m):
    o=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)));ys,xs=np.where(o>0);return xs.min(),ys.min()
ox,oy=outline(m);print('offset',ox,oy)
erase=[(x/1.5,y/1.5) for x,y in [(600,226),(690,200),(790,472),(745,465),(690,422),(635,367),(590,312),(585,255)]]
pts=np.array([(x/1.2+ox,y/1.2+oy) for x,y in erase],np.int32)
if len(sys.argv)>1: cv2.fillPoly(m,[pts],0)
n,lab,st,_=cv2.connectedComponentsWithStats(m);big=1+np.argmax(st[1:,4]);m=np.where(lab==big,255,0).astype(np.uint8)
outl=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
out=np.zeros_like(img);out[outl>0]=(22,24,28,255)
src=img.copy();src[:,:,3]=cv2.GaussianBlur(m,(3,3),0);a=src[:,:,3:4]/255.0
out[:,:,:3]=(src[:,:,:3]*a+out[:,:,:3]*(1-a)).astype(np.uint8)
out[:,:,3]=np.maximum(out[:,:,3],src[:,:,3]);out[:,:,3]=cv2.GaussianBlur(out[:,:,3],(3,3),0)
ys,xs=np.where(out[:,:,3]>0);out=out[ys.min():ys.max()+1,xs.min():xs.max()+1]
cv2.imwrite('/home/claude/art/dagger_clean.png',out)
bg=np.full((out.shape[0],out.shape[1],3),(120,200,120),np.uint8);a=out[:,:,3:4]/255.0
prev=(out[:,:,:3]*a+bg*(1-a)).astype(np.uint8)
cv2.imwrite('/home/claude/art/clean_prev.png',cv2.resize(prev,None,fx=1.2,fy=1.2))
