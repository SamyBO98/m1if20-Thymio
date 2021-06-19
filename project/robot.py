# coding: utf8
#!/usr/bin/python
#import gobject
from gi.repository import GObject as gobject
from . import movement as Movement
from . import parameters as Parameters
from . import position as Position
import time

import numpy as np
import cv2
from threading import Thread


webcam = cv2.VideoCapture(0)
cv2.namedWindow("Trackbars")

def nothing(x):
    pass

cv2.createTrackbar("L - H", "Trackbars", 48, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 0, 255, nothing)

colors = ["empty", "empty", "empty", "empty"]


class Robot:

    """
        Classe principale du robot: permet le déplacement du robot
    """

    ##################################################################################
    #######################         CLASS CONSTRUCTOR          #######################

    def __init__(self, parameters, movement, network, resetTimer):
        '''
        @summary: Création d'un neurone
        @param parameters: Paramètres du robot
        @type parameters: Parameters Class
        @param movement: Situation actuelle
        @type movement: Movement Class
        @param network: Robot dbus
        @type network: dbus Class
        @param resetTimer: timer pour boucler l'appel des fonctions
        @type resetTimer: int
        '''
        self.parameters = parameters
        self.movement = movement
        self.network = network
        self.resetTimer = resetTimer
        self.position = Position.Position.MIDDLE
        self.extreme = 0
        self.rangeRoadValues = []
        self.rangeRoadBlack = None
        self.rangeRoadWhite = None
        self.center = None
        self.globalIndex = 0
        # Capturing video through webcam

    ##################################################################################
    #######################              GETTERS               #######################

    #

    ##################################################################################
    #######################              SETTERS               #######################

    #

    ##################################################################################
    #######################       CLASS STRING FOR DEBUG       #######################

    def toString(self):
        return None

    ##################################################################################
    #######################             FUNCTIONS              #######################

    def resetRobot(self):
        '''
        @summary: Stoppe la vitesse des moteurs des roues
        '''
        self.network.SetVariable("thymio-II", "motor.right.target", [0])
        self.network.SetVariable("thymio-II", "motor.left.target", [0])

    def startSimulation(self):
        '''
        @summary: Lance la simulation en faisant bouger le robot
        '''
        # Call move
        moveLoop = gobject.MainLoop()
        handle = gobject.timeout_add(1000, self.madeDecision)
        try:
            moveLoop.run()
        except KeyboardInterrupt:
            self.resetRobot()
            moveLoop.quit()

    def initialiseRangeAndCenter(self):
        '''
        @summary: Met les valeurs des ranges mais aussi celui du centre pour permettre au robot de se déplacer le plus précisemment possible
        '''
        print("===================== STARTING THE INITIALIZATION =====================")
        print("========= GET THE RANGE OF THE BLACK COLOR")

        autoRoadRangeDetectionLoop = gobject.MainLoop()
        handle = gobject.timeout_add(self.resetTimer / 10, self.autoRoadRangeDetection, self.parameters.getSpeed() / 10, autoRoadRangeDetectionLoop)

        try:
            autoRoadRangeDetectionLoop.run()
        except KeyboardInterrupt:
            self.resetRobot()
            autoRoadRangeDetectionLoop.quit()

        

    def autoRoadRangeDetection(self, motorRight, loop):
        '''
        @summary: Met les valeurs des ranges mais aussi celui du centre pour permettre au robot de se déplacer le plus précisemment possible
        @param motorRight: Vitesse du moteur de la roue droite
        @type motorRight: int
        @param loop: Boucle de la fonction
        @type loop: Gobject Loop
        '''
        deltaR = self.network.GetVariable("thymio-II", "prox.ground.delta")[1]

        if self.rangeRoadValues != [] and deltaR > 1.15 * min(self.rangeRoadValues):
            # Cas ou le robot est sur la partie gauche de la route: on a trouve la valeur noire la plus basse
            self.network.SetVariable("thymio-II", "motor.right.target", [0])
            print("DETECTION STOP: [", deltaR, ">", self.parameters.getRangeBlack(), "] => min is", min(self.rangeRoadValues))
            # on récupère l'index du robot de la marge blanche et la marge noire pour trouver le centre de la route
            self.rangeRoadBlack = self.rangeRoadValues.index(min(self.rangeRoadValues))
            whiteValue = 0.9 * self.rangeRoadValues[0]

            for i in range(len(self.rangeRoadValues)):
                if self.rangeRoadValues[i] <= whiteValue:
                    self.rangeRoadWhite = i
                    break

            self.parameters.setRangeWhite(self.rangeRoadValues[self.rangeRoadWhite])
            self.parameters.setRangeBlack(self.rangeRoadValues[self.rangeRoadBlack])

            print("INDEX BLACK:", self.rangeRoadBlack)
            print("INDEX WHITE:", self.rangeRoadWhite)
            if abs(self.rangeRoadBlack - self.rangeRoadWhite) % 2 == 0:
                self.center = self.rangeRoadValues[abs(self.rangeRoadBlack - self.rangeRoadWhite)]
            else:
                x1 = self.rangeRoadValues[int(abs(self.rangeRoadBlack - self.rangeRoadWhite) / 2 + 1)]
                x2 = self.rangeRoadValues[int(abs(self.rangeRoadBlack - self.rangeRoadWhite) / 2 + 2)]

                x = abs(x1 + x2) / 2
                self.center = x 

            print("Center:", self.center)

            time.sleep(3)
            loop.quit()

            # Call robotPlacement
            robotPlacementLoop = gobject.MainLoop()
            handle = gobject.timeout_add(10, self.robotPlacement, motorRight, robotPlacementLoop)
            try:
                robotPlacementLoop.run()
            except KeyboardInterrupt:
                self.resetRobot()
                robotPlacementLoop.quit()
        else:
            # Cas ou le robot continue sa detection
            print("DETECTION CONTINUE: [", deltaR, "<=", self.parameters.getRangeBlack(), "] =>", self.globalIndex)
            self.globalIndex = self.globalIndex + 1
            self.rangeRoadValues.append(deltaR)
            self.network.SetVariable("thymio-II", "motor.right.target", [motorRight])

        return True

    def autoRoadRangeDetectionReplacement(self, motorRight, autoRoadRangeDetectionReplacementLoop):
        if self.rangeRoadBlack < len(self.rangeRoadValues):
            print("DETECTION REPLACEMENT IN PROCESS...")
            self.rangeRoadBlack = self.rangeRoadBlack + 1
            self.network.SetVariable("thymio-II", "motor.right.target", [-motorRight])
        else:
            print("DETECTION REPLACEMENT DONE!")
            self.network.SetVariable("thymio-II", "motor.right.target", [0])
            time.sleep(5)
            autoRoadRangeDetectionReplacementLoop.quit()

            # Call robotPlacement
            robotPlacementLoop = gobject.MainLoop()
            handle = gobject.timeout_add(10, self.robotPlacement, motorRight, robotPlacementLoop)
            try:
                robotPlacementLoop.run()
            except KeyboardInterrupt:
                self.resetRobot()
                robotPlacementLoop.quit()

        return True
    
    '''
        LA CAM DEBUT
    '''
    
    
    
    '''
        LA CAM FIN
    '''
            

        
    def robotPlacement(self, motorRight, loop):
        deltaR = self.network.GetVariable("thymio-II", "prox.ground.delta")[1]
        #placementRange = 0.6 * (self.parameters.getRangeWhite() - self.parameters.getRangeBlack())

        if deltaR > 1.15 * self.center:
            # Le placement est bon
            print("ROBOT PLACEMENT STOP: [", deltaR, ">", 1.15 * self.center, "]")
            self.network.SetVariable("thymio-II", "motor.right.target", [0])
            # Pour faire en sorte que le robot soit encore mieux place, on augmente legerement la range de la couleur noire
            #self.parameters.setRangeBlack(self.parameters.getRangeBlack() * 1.65)
            time.sleep(3)
            loop.quit()
            
            

            # Call move
            moveLoop = gobject.MainLoop()
            handle = gobject.timeout_add(1000, self.madeDecision)
            try:
                moveLoop.run()
            except KeyboardInterrupt:
                self.resetRobot()
                moveLoop.quit()
        else:
            # On continue de le faire bouger
            print("ROBOT PLACEMENT CONTINUE: [", deltaR, "<=", 1.15 * self.center, "]")
            self.network.SetVariable("thymio-II", "motor.right.target", [-motorRight])
        return True
        
    def move(self, motorLeft, motorRight):
        deltaL = self.network.GetVariable("thymio-II", "prox.ground.delta")[0]
        deltaR = self.network.GetVariable("thymio-II", "prox.ground.delta")[1]

        speedR = motorRight
        speedL = motorLeft
        
        if deltaR > self.center:
            print("Robot is on the right:", deltaR, ">", self.center)
            speedR = motorRight + (1.5 * abs(deltaR - self.center)) / 100
            speedL = 0.8 * motorLeft
        elif deltaR < self.center:
            print("Robot is on the left", deltaR, "<", self.center)
            speedR = 0.8 * motorRight
            speedL = motorLeft + (1.5 * abs(deltaR - self.center)) / 100
        else:
            print("Robot is perfectly placed in the middle", deltaR, "=", self.center)
            speedR = motorRight
            speedL = motorLeft
        

        self.network.SetVariable("thymio-II", "motor.right.target", [speedR])
        self.network.SetVariable("thymio-II", "motor.left.target", [speedL])
        


    """
        Mouvement du robot
    """
    def moveL(self, motorLeft, motorRight):
        # Get the values of the sensors
        deltaL = self.network.GetVariable("thymio-II", "prox.ground.delta")[0]
        deltaR = self.network.GetVariable("thymio-II", "prox.ground.delta")[1]

        """
            Selon la position, il faudrait remettre le robot rapidement a sa place
            Par exemple lorsqu'il est positionne a gauche il ne peut pas passer de gauche a droite sans aller au milieu
        """
        # Cas de base: capteur droit dans la marge et capteur gauche au dessus de la marge blanche
        if self.extreme != -1:
            center = self.parameters.getRangeWhite() - self.parameters.getRangeBlack()
            if deltaR < self.parameters.getRangeWhite() and deltaR > self.parameters.getRangeBlack():
                print("Robot is centered", self.parameters.getRangeBlack(), "<", deltaR, "<", self.parameters.getRangeWhite())
                if deltaR > center:
                    self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft * (1 + 1 *((deltaR - center) / 100))])
                    self.network.SetVariable("thymio-II", "motor.right.target", [motorRight])
                else:
                    self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft])
                    self.network.SetVariable("thymio-II", "motor.right.target", [motorRight * (1 + 1 *((center - deltaR) / 100))])
                self.position = Position.Position.MIDDLE
            else:
                # Si le robot est place au milieu, on fera une analyse classique: il commence a se diriger vers la droite ou vers la gauche
                if deltaR < self.parameters.getRangeBlack() or (deltaR > self.parameters.getRangeWhite() and deltaL > self.parameters.getRangeWhite()):
                    print("Robot is on the left", deltaR, "<", self.parameters.getRangeBlack(), "<", self.parameters.getRangeWhite())
                    self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft * (1 + 2 *((deltaR - center) / 100))])
                    self.network.SetVariable("thymio-II", "motor.right.target", [motorRight])
                    self.position = Position.Position.LEFT
                else:
                    print("Robot is on the right", self.parameters.getRangeBlack(), "<", self.parameters.getRangeWhite(), "<", deltaR)
                    self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft])
                    self.network.SetVariable("thymio-II", "motor.right.target", [motorRight * (1 + 2 *((center - deltaR) / 100))])
                    self.position = Position.Position.RIGHT
            
            if self.position == Position.Position.LEFT:
                    self.extreme = self.extreme + 1
            elif self.position == Position.Position.RIGHT:
                    self.extreme = self.extreme + 1

            # On passe en mode recalibration (seulement dans le cas ou le plateau n'est pas parfaitement imprime avec la detection du noir / blanc)
            if self.extreme == 5:
                self.extreme = -1
                print("==== RECALIBRATE MODE ====")
        else:
            if self.position == Position.Position.LEFT:
                print("RECALIBRATE (LEFT): TURN ON THE RIGHT")
                self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft * 2])
                self.network.SetVariable("thymio-II", "motor.right.target", [motorRight * 0.75])
            elif self.position == Position.Position.RIGHT:
                print("RECALIBRATE (RIGHT): TURN ON THE LEFT")
                self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft * 0.75])
                self.network.SetVariable("thymio-II", "motor.right.target", [motorRight * 2])

            if deltaR < self.parameters.getRangeWhite() and deltaR > self.parameters.getRangeBlack() and deltaL > self.parameters.getRangeWhite():
                print("==== RECALIBRATE DONE ====")
                self.position = Position.Position.MIDDLE
                self.extreme = 0
    """

    def move(self, motorLeft, motorRight):
        # Get the values of the sensors
        deltaL = self.network.GetVariable("thymio-II", "prox.ground.delta")[0]
        deltaR = self.network.GetVariable("thymio-II", "prox.ground.delta")[1]

        
            Lorsqu'il se trouve a droite / a gauche de la range (noire), on definit une position a GAUCHE/DROITE.
            Quand il est a droite, il va faire que de tourner a gauche jusqu a se retrouver en dessous de la range.
            Quand il est a gauche, il va faire que de tourner a droite jusqu a se retrouver au dessus de la range.
            La vitesse des roues change selon la distance entre ce qu a detecte le capteur et la range noire
        
        if self.position == Position.Position.RIGHT:
            # Cas quand il est a droite
            if deltaR < self.parameters.getRangeBlack() or (deltaR >= self.parameters.getRangeBlack() and deltaL >= self.parameters.getRangeBlack()):
                # Cas quand il est en dessous de la range: on remet la position a GAUCHE
                self.position = Position.Position.LEFT
                motorLeft = 1.5 * motorLeft
                print("ROBOT IS NOW LEFT")
            else:
                motorRight = 1.5 * motorRight
                print("ROBOT STILL RIGHT")
        elif self.position == Position.Position.LEFT:
            # Cas quand il est a gauche
            if deltaR > self.parameters.getRangeBlack() or (deltaR >= self.parameters.getRangeBlack() and deltaL < self.parameters.getRangeBlack()):
                # Cas quand il est au dessus de la range: on remet la position a DROITE
                self.position = Position.Position.RIGHT
                motorRight = 1.5 * motorRight
                print("ROBOT IS NOW RIGHT")
            else:
                motorLeft = 1.5 * motorLeft
                print("ROBOT STILL LEFT")
        else:
            if deltaR > self.parameters.getRangeBlack():
                self.position = Position.Position.RIGHT
                motorRight = 1.5 * motorRight
                print("ROBOT CENTERED IS NOW RIGHT")
            elif deltaR < self.parameters.getRangeBlack():
                self.position = Position.Position.LEFT
                motorLeft = 1.5 * motorLeft
                print("ROBOT CENTERED IS NOW LEFT")

        self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft])
        self.network.SetVariable("thymio-II", "motor.right.target", [motorRight])
    """
        
    def getContours(self,img,imgContour):
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
            
    def test(self):
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
            
            self.getContours(imgDil,imgContour)

        # Program Termination
            cv2.imshow("Multiple Color Detection in Real-TIme", imgContour)
            
    
            if cv2.waitKey(10) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    """
        Fonction qui permet au robot de s'adapter selon la situation
    """
    def madeDecision(self):
        speed = self.parameters.getSpeed()
        print(speed)
        # Mouvement donna au robot selon les codes datectas
        if self.movement == Movement.Movement.STOPPED:
            # Rien, on trouvera un truc a faire
            print("Movement >", self.movement)

        elif self.movement == Movement.Movement.STRAIGHT:
            # Tout droit
            self.move(speed, speed)

        elif self.movement == Movement.Movement.LEFTTIGHT:
            # A gauche serre
            self.move(speed * 0.25, speed)
        elif self.movement == Movement.Movement.LEFT:
            # A gauche
            self.move(speed * 0.75, speed)
        elif self.movement == Movement.Movement.LEFTWIDE:
            # A gauche large
            self.move(speed * 0.9, speed)

        elif self.movement == Movement.Movement.RIGHTTIGHT:
            # A droite serre
            self.move(speed, speed * 0.25)
        elif self.movement == Movement.Movement.RIGHT:
            # A droite
            self.move(speed, speed * 0.75)
        elif self.movement == Movement.Movement.RIGHTWIDE:
            # A droite large
            self.move(speed, speed * 0.75)

        elif self.movement == Movement.Movement.DEBUG:
            # MODE DEBUG
            self.debug()
        self.test()
        return True

    """
        Debug: affichage des informations du robot
    """
    def debug(self):
        sensorR = self.network.GetVariable("thymio-II", "prox.ground.delta")[1]
        sensorL = self.network.GetVariable("thymio-II", "prox.ground.delta")[0]
        center = (self.parameters.getRangeWhite() - self.parameters.getRangeBlack())
        print("Debug > Sensors [L | R]:", sensorL, "|", sensorR, "center: ", center)
        '''
        if sensorR < center:
            print(">>> Robot is on the left")
        elif sensorR > center:
            if sensorL > center:
                print(">>> Robot is on the left")
            else:
                print(">>> Robot is on the right")
        else:
            print(">>> Robot is perfectly centered")
        '''

