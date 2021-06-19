import numpy as np
import cv2
from threading import Thread

import time


  
# Capturing video through webcam
webcam = cv2.VideoCapture(0)
cv2.namedWindow("Trackbars")

def nothing(x):
    pass

cv2.createTrackbar("L - H", "Trackbars", 48, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 0, 255, nothing)

colors = ["empty", "empty", "empty", "empty"]

def getContours(img,imgContour):
    contours , hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    count = 0
    global colors
    for cnt in contours:
        M = cv2.moments(cnt)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        approx = cv2.approxPolyDP(cnt, 0.01* cv2.arcLength(cnt, True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1] - 5
        area = cv2.contourArea(cnt)
        centroids = (cX,cY)
        if area > 0  and len(approx) == 4:
            count+=1
            x, y , w, h = cv2.boundingRect(approx)
            aspectRatio = float(w)/h
            if aspectRatio >= 0.90 and aspectRatio < 1.10:
                cv2.drawContours(imgContour, cnt, -1, (0,255,0),7)
                #cv2.circle(imgContour, (306,258), 7, (0, 255, 0), -1)
                #print(cY,cX)
                center = imgContour[cY,cX]
                #print(center)
                #Tout en haut de l'image
                if 270 < cY < 300:
                    if 80 < center[0] < 150 and 80 < center[2] < 95:
                        colors[0] = "blue"
                    elif center[1] > 100:
                        colors[0] = "white"
                    elif center[0] < 50 and center[2] < 50:
                        colors[0] = "black"
                    elif center[0] < 50 and center[2] > 90:
                        colors[0] = "red"
                if 200 < cY < 250:
                    if 100 < center[0] < 150 and center[2] < 20:
                        colors[1] = "blue"
                    elif center[1] > 100:
                        colors[1] = "white"
                    elif center[0] < 50 and center[2] < 50:
                        colors[1] = "black"
                    elif center[0] < 50 and center[2] > 90:
                        colors[1] = "red"
                if 110 < cY < 200:
                    if 100 < center[0] < 150 and center[2] < 20:
                        colors[2] = "blue"
                    elif center[1] > 100:
                        colors[2] = "white"
                    elif center[0] < 50 and center[2] < 50:
                        colors[2] = "black"
                    elif center[0] < 50 and center[2] > 90:
                        colors[2] = "red"
                if 25 < cY < 100:
                    if 100 < center[0] < 150 and center[2] < 20:
                        colors[3] = "blue"
                    elif center[1] > 100:
                        colors[3] = "white"
                    elif center[0] < 50 and center[2] < 50:
                        colors[3] = "black"
                    elif center[0] < 50 and center[2] > 90:
                        colors[3] = "red"
    if count != 4:
        colors = ["empty", "empty", "empty", "empty"]
    #print(colors)    
    if colors[0] != "empty" and colors[1] != "empty" and colors[2] != "empty" and colors[3] != "empty":
        print(colors)    
        
def test():
    while(1):
        _, img = webcam.read()
        imgContour = img.copy()
        imgBlur = cv2.GaussianBlur(img, (7,7), 1)
        imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((5,5))
    
        t1 = cv2.getTrackbarPos("L - H", "Trackbars")
        t2 = cv2.getTrackbarPos("U - V", "Trackbars")
    
        imgCanny = cv2.Canny(imgGray, t1, t2)
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
    

        getContours(imgDil,imgContour)
    

        # Program Termination
        cv2.imshow("Multiple Color Detection in Real-TIme", imgContour)
    
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    

if __name__ == "__main__":
    f1 = Thread(target=test)
    f1.start()
    
