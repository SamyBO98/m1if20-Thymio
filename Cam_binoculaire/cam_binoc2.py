import numpy as np
import cv2
import shlex
import subprocess
import time


# Create our body classifier
car_classifier = cv2.CascadeClassifier('haarcascade_car.xml')

cam_id = 2
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
    time.sleep(.05)
    ret, frame = cam.read()
    expand_frame = cv2.resize(frame, None, fx=1, fy=0.5)
    gray = cv2.cvtColor(expand_frame, cv2.COLOR_BGR2GRAY)

    # Pass frame to our car classifier
    cars = car_classifier.detectMultiScale(gray, 1.4, 2)

    # Extract bounding boxes for any bodies identified
    for (x,y,w,h) in cars:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.imshow('frame',expand_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()