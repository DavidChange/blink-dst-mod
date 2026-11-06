import cv2,numpy as np
img=cv2.imread('/home/claude/rune/ref.png')
P=[(265,210),(380,185),(385,140),(410,110),(440,106),(462,122),(470,150),(458,172),(605,158),(632,190),(590,330),(600,360),(560,380),(540,420),(500,468),(690,463),(707,495),(640,620),(630,680),(565,760),(565,815),(595,830),(575,870),(520,905),(380,1050),(232,1127),(212,1105),(248,960),(238,880),(222,800),(248,742),(128,728),(118,712),(268,580),(238,562),(148,542),(138,520),(228,494),(268,470),(345,432),(298,428),(193,412),(198,383),(288,250)]
poly=np.array([(x/3,y/3) for x,y in P],np.int32)
mask=np.zeros(img.shape[:2],np.uint8);cv2.fillPoly(mask,[poly],1)
k=np.ones((5,5),np.uint8)
gc=np.full(img.shape[:2],cv2.GC_BGD,np.uint8)
gc[cv2.dilate(mask,k)==1]=cv2.GC_PR_BGD;gc[mask==1]=cv2.GC_PR_FGD;gc[cv2.erode(mask,np.ones((7,7),np.uint8))==1]=cv2.GC_FGD
b=np.zeros((1,65));f=np.zeros((1,65));cv2.grabCut(img,gc,None,b,f,6,cv2.GC_INIT_WITH_MASK)
fg=np.where((gc==1)|(gc==3),255,0).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(fg);big=1+np.argmax(st[1:,4]);fg=np.where(lab==big,255,0).astype(np.uint8)
fg=cv2.morphologyEx(fg,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
rgba=cv2.cvtColor(img,cv2.COLOR_BGR2BGRA);rgba[:,:,3]=fg
ys,xs=np.where(fg>0);rgba=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]
cv2.imwrite('/home/claude/rune/rune_cut.png',rgba);print('offset',xs.min(),ys.min(),rgba.shape)
prev=img.copy();prev[fg==0]=(255,0,255);ov=img.copy();cv2.polylines(ov,[poly],True,(0,0,255),1)
cv2.imwrite('/home/claude/rune/prev.png',cv2.resize(np.hstack([ov,prev]),None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST))
