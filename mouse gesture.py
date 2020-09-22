import cv2
import numpy as np
import wx
from pynput.mouse import Button, Controller

mouse = Controller()
app= wx.App(False)
(sx,sy)= wx.GetDisplaySize()    #size of monitior
(comx,comy)=(320,240)       #cam resolution

lowerbound=np.array([33,80,40])
upperbound=np.array([102,255,255])

cam=cv2.VideoCapture(0)
cam.set(3,comx)
cam.set(4,comy)


kernalOpen=np.ones((5,5))
kernalClose=np.ones((20,20))

#mouse damping
mLocold=np.array([0,0])
mouseLoc=np.array([0,0])
DampingFactor= 2 # should be >1

pinchFlag=0


#mouseLoc= mLocold + (targetiLoc-mlocold)/DampingFactor more DampingFactor more smoohter the mouse moment will become aslo it becomes more slower


while True:
    ret, img= cam.read()
    imgHsv= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    mask= cv2.inRange(imgHsv,lowerbound,upperbound)

    maskopen= cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernalOpen)
    maskclose = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernalClose)

    finalmask= maskclose
    conts, h= cv2.findContours(finalmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if(len(conts)==2):
        if(pinchFlag==1):
            pinchFlag=0
            mouse.release(Button.left)
        x1, y1, w1, h1=cv2.boundingRect(conts[0])
        x2, y2, w2, h2 = cv2.boundingRect(conts[1])
        cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
        cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)
        cx1= x1+w1/2
        cy1= yi+h1/2 #center points of first box

        cx2 = x2 + w2 / 2
        cy2 = y2 + h2 / 2   #center box of 2nd box

        cv2.line(img,(cx1,cy1),(cx2,cy2),(255,0,0),2)   #drawing line from 1st to second

        cx= (cx1+cx2)/2
        cy= (cy1+cy2)/2
        cv2.circle(img, (cx, cy), 2, (0, 0, 255), 2)
        mouseLoc = mLocold + ((cx, cy) - mlocold) / DampingFactor
        mouse.position= (sx-(mouseLoc[0]*sx/comx), mouseLoc[1]*sy/comy)
        while mouse.position!=(sx-(mouseLoc[0]*sx/comx), mouseLoc[1]*sy/comy):
            pass
        mLocold=mouseLoc
        openx,openy,openw,openh= cv2.boundingRect(np.array([[[x1,y1], [x1+w1,y1+h1], [x2.y2], [x2+w2,y2+hw]]]))

        cv2.rectangle(img,(openx,openy), (openx+openw, openy+ openh),(255,0,0),2)
    elif(len(conts)==1):
        x, y, w, h=cv2.boundingRect(conts[0])
        if (pinchFlag == 0):
            if(abs((w*h-openw*openh)*100/(w*h))<20):
                pinchFlag = 1
                mouse.press(Button.left)
                openx, openy, openw, openh =(0,0,0,0)
        else:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cx = x + w / 2
            cy = y + h / 2
            cv2.circle(img, (cx, cy), (w+h)/4, (0, 0, 255), 2)

            mouseLoc = mLocold + ((cx, cy) - mlocold) / DampingFactor
            mouse.position= (sx-(mouseLoc[0]*sx/comx), mouseLoc[1]*sy/comy)
            while mouse.position!=(sx-(mouseLoc[0]*sx/comx), mouseLoc[1]*sy/comy):
                pass
            mLocold=mouseLoc

    #cv2.imshow("Mask close",maskclose)
    #cv2.imshow("Mask open",maskopen)
    #cv2.imshow("Mask ",mask)
    cv2.imshow("cam",img)
    cv2.waitKey(10)

