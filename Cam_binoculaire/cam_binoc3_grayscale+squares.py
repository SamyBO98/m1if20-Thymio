import numpy as np
import cv2
import shlex
import subprocess


cam_id = 0
cam = cv2.VideoCapture(cam_id)

object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=60)

cam_mode_dict = {
    'LEFT_EYE_MODE': 1, # monoculaire gauche
    'RIGHT_EYE_MODE': 2, # monoculaire droit
    'RED_BLUE_MODE': 3, # rouge bleu
    'BINOCULAR_MODE': 4, # binoculaire
}
# La valeur par defaut est le mode binoculaire
cam_mode = cam_mode_dict['BINOCULAR_MODE']
command_list = [
    "uvcdynctrl -d /dev/video{cam_id} -S 6:8 '(LE)0x50ff'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:15 '(LE)0x00f6'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:8 '(LE)0x2500'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:8 '(LE)0x5ffe'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:15 '(LE)0x0003'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:15 '(LE)0x0002'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:15 '(LE)0x0012'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:15 '(LE)0x0004'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:8 '(LE)0x76c3'",
    "uvcdynctrl -d /dev/video{cam_id} -S 6:10 '(LE)0x0{cam_mode}00'",
]
for command in command_list:
    # Executer l'instruction
    print(shlex.split(command.format(cam_id=cam_id, cam_mode=cam_mode)))
    subprocess.Popen(shlex.split(command.format(cam_id=cam_id, cam_mode=cam_mode)))

while(True):
    ret, iniframe = cam.read()
    frame = cv2.resize(iniframe, None, fx=1, fy=0.5)
    if not ret:
        break
  
    # 1. Filters
    # Grey filter
    gray0 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Grayscale without filter", gray0)
    # 2D blur filter
    kernel = np.ones((5,5),np.float32)/25
    gray1 = cv2.filter2D(gray0,-1,kernel)
    cv2.imshow("Grayscale with 2D blur filter",gray)
    gray = cv2.medianBlur(gray1,15)
    
    # 2. Border Detection
    edged = cv2.Canny(gray, 50, 150)

    # 3.Simplify image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel, iterations = 2)
    
    # 4.Find contours
    cnts, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 5. Show borders
    frame2 = frame.copy()
    cv2.drawContours(frame2, cnts, -1, (0, 255, 0), 3, cv2.LINE_AA)
    cv2.imshow("all edges",frame2)

    # 6. Filter borders
    for c in cnts:
        area = cv2.contourArea(c)
        
        if area > 1700:
            # rectangles filter
            peri = cv2.arcLength(c, True) #Perimeter
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            #If the aproximation has 4 apex is a rectangle
            if len(approx) == 4:
                # show borders
                cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3, cv2.LINE_AA)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cam.release()
cv2.destroyAllWindows()