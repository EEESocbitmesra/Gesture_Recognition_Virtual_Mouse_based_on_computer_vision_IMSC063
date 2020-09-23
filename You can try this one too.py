import cv2
import numpy as np
from pynput.mouse import Button, Controller

mouse=Controller()

from AppKit import NSScreen

sx=NSScreen.mainScreen().frame().size.width
sy=NSScreen.mainScreen().frame().size.height

(camx,camy)=(480,320)

lowerbound=np.array([22,0,148])
upperbound=np.array([86,244,242])

cam=cv2.VideoCapture(0)
cam.set(3,camx)
cam.set(4,camy)

kernalopen=np.ones((4,4))
kernalclose=np.ones((17,17))


mLocold=np.array([0,0])
mouseLoc=np.array([0,0])
DampingFactor= 1.5


pinchFlag=0


openx, openy, openw, openh =(0,0,0,0)


while True:
    ret,img=cam.read()
    
    imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    
    mask=cv2.inRange(imgHSV,lowerbound,upperbound)
    
    maskopen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernalopen)
    maskclose=cv2.morphologyEx(maskopen,cv2.MORPH_CLOSE,kernalclose)
    
    maskfinal=maskclose
    
    conts, h= cv2.findContours(maskfinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
    
    if(len(conts)==2):
        if(pinchFlag==1):
            pinchFlag=0
            mouse.release(Button.left)

        x1,y1,w1,h1=cv2.boundingRect(conts[0])
        x2,y2,w2,h2=cv2.boundingRect(conts[1])
        
        #cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
        #cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)
        
        cx1=x1+int(w1/2)
        cy1=y1+int(h1/2)
        
        cx2=x2+int(w2/2)
        cy2=y2+int(h2/2)
        
        #cv2.line(img,(cx1,cy1),(cy1,cy2),(255,0,0),2)
        
        cx=(cx1+cx2)/2
        cy=(cy1+cy2)/2
        
        cv2.circle(img,(int(cx),int(cy)),2,(0,0,255),2)
        
        mouseLoc = mLocold + ((cx, cy) - mLocold) / DampingFactor
        mouse.position= (sx-(mouseLoc[0]*sx/camx), mouseLoc[1]*sy/camy)
        while mouse.position!=(sx-(mouseLoc[0]*sx/camx), mouseLoc[1]*sy/camy):
            pass
        mLocold=mouseLoc
         
        openx,openy,openw,openh= cv2.boundingRect(np.array([[[x1,y1], [x1+w1,y1+h1], [x2,y2], [x2+w2,y2+h2]]]))
        
        cv2.rectangle(img,(openx,openy), (openx+openw, openy+ openh),(255,0,0),2)

    elif(len(conts)==1):
        x, y, w, h=cv2.boundingRect(conts[0])
        if (pinchFlag == 0):
            if(abs((w*h-openw*openh)*100/(w*h))<20):
                pinchFlag = 1
                mouse.press(Button.left)
                openx, openy, openw, openh =(0,0,0,0)
        
        else:
            cx=x+w/2
            cy=y+h/2
            
            mouseLoc = mLocold + ((cx, cy) - mLocold) / DampingFactor
            mouse.position= (sx-(mouseLoc[0]*sx/camx), mouseLoc[1]*sy/camy)
            while mouse.position!=(sx-(mouseLoc[0]*sx/camx), mouseLoc[1]*sy/camy):
                pass
            mLocold=mouseLoc
        

        
        
    cv2.imshow("CAM",img)   
    cv2.waitKey(10)


