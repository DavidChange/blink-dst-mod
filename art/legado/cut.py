import cv2, numpy as np
img=cv2.imread('/home/claude/art/dagger_ref.png')
poly_disp=[(1015,95),(900,82),(770,108),(690,168),(610,228),(540,288),(490,330),(460,400),(460,470),(480,540),(495,600),(455,650),(445,700),(400,760),(330,792),(260,790),(240,760),
(120,800),(5,875),(130,962),(250,1012),(340,1042),(450,1048),(560,1032),(665,1000),(755,930),(825,840),(872,740),(885,650),(880,600),(830,530),(790,485),(740,450),(700,410),(672,350),
(705,302),(770,300),(850,235),(925,232),(962,252),(978,292),(992,240),(1022,180),(1032,110)]
poly=np.array([(x/2,y/2) for x,y in poly_disp],np.int32)
mask=np.zeros(img.shape[:2],np.uint8)
cv2.fillPoly(mask,[poly],1)
k=np.ones((9,9),np.uint8)
inner=cv2.erode(mask,k,iterations=1)
outer=cv2.dilate(mask,k,iterations=1)
gc=np.full(img.shape[:2],cv2.GC_BGD,np.uint8)
gc[outer==1]=cv2.GC_PR_BGD
gc[mask==1]=cv2.GC_PR_FGD
gc[inner==1]=cv2.GC_FGD
bgd=np.zeros((1,65),np.float64);fgd=np.zeros((1,65),np.float64)
cv2.grabCut(img,gc,None,bgd,fgd,6,cv2.GC_INIT_WITH_MASK)
fg=np.where((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD),255,0).astype(np.uint8)
# keep largest component
n,lab,st,_=cv2.connectedComponentsWithStats(fg)
big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]);fg=np.where(lab==big,255,0).astype(np.uint8)
fg=cv2.morphologyEx(fg,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
cv2.imwrite('/home/claude/art/dagger_mask.png',fg)
rgba=cv2.cvtColor(img,cv2.COLOR_BGR2BGRA);rgba[:,:,3]=cv2.GaussianBlur(fg,(3,3),0)
cv2.imwrite('/home/claude/art/dagger_cut.png',rgba)
# preview on magenta and the polygon overlay
prev=img.copy();prev[fg==0]=(255,0,255)
ov=img.copy();cv2.polylines(ov,[poly],True,(0,0,255),2)
cv2.imwrite('/home/claude/art/preview.png',np.hstack([ov,prev]))
