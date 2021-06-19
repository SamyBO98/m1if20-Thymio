import numpy as np
import cv2
from threading import Thread

import time


  
# Capturing video through webcam
webcam = cv2.VideoCapture(0)
   
        
def test():
    while(1):
        _, img = webcam.read()
    

        # Program Termination
        cv2.imshow("Multiple Color Detection in Real-TIme", img)
    
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    

if __name__ == "__main__":
    f1 = Thread(target=test)
    f1.start()
    

