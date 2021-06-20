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
    ret, frame = cam.read()

    if not ret:
        break

    # 1. Grey scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("Escala de Grises sin filtro",gray)
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    #cv2.imshow("Escala de Grises",gray)

    # 2. Border Detection
    edged = cv2.Canny(gray, 50, 150)
    #cv2.imshow("Edged",edged)

    #3.Operaciones Morfologicas Cierre
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel, iterations = 2)
    #cv2.imshow("Closed",closed)
    
    #4.Encontrar contornos
    #_,cnts,_=cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #print "contornos",len(cnts)
    
    '''
    total = 0
    for c in cnts:
        area = cv2.contourArea(c)
        #print "area",area

        if area > 1700:
            #aproximacion de contorno
            peri = cv2.arcLength(c, True) #Perimetro
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            #Si la aproximacion tiene 4 vertices correspondera a un rectangulo (Libro)
            if len(approx) == 4:
                    cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3, cv2.LINE_AA)
                    total += 1
    
        #5.Poner texto en imagen
        letrero = 'Objetos: ' + str(total)
        cv2.putText(frame, letrero, (10,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0) ,2)
    '''

    
    for c in cnts:
        area = cv2.contourArea(c)
        #print "area",area

        if area > 1700:
            #aproximacion de contorno
            peri = cv2.arcLength(c, True) #Perimetro
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            #Si la aproximacion tiene 4 vertices correspondera a un rectangulo (Libro)
            if len(approx) == 4:
                cv2.drawContours(frame, cnts, -1, (0, 255, 0), 3, cv2.LINE_AA)
    
    cv2.imshow('frame',frame)
    #cv2.imshow('frame',expand_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    

cam.release()
cv2.destroyAllWindows()