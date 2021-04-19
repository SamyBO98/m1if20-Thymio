#!/usr/bin/python
import gobject
import movement as Movement
import parameters as Parameters
import position as Position


class Robot:

    ##################################################################################
    #######################   EXPLANATIONS ABOUT THIS CLASS    #######################

    """

    """

    ##################################################################################
    #######################         CLASS CONSTRUCTOR          #######################

    def __init__(self, parameters, movement, network, resetTimer):
        self.parameters = parameters
        self.movement = movement
        self.network = network
        self.resetTimer = resetTimer
        self.position = Position.Position.MIDDLE
        self.extreme = 0

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

    """
        Remet a 0 le robot: vitesse de daplacement
    """
    def resetRobot(self):
        self.network.SetVariable("thymio-II", "motor.right.target", [0])
        self.network.SetVariable("thymio-II", "motor.left.target", [0])

    """
        Permet de faire interagir le robot: fonction principale => permet de boucler l'appel aux fonctions pour le deplacement du robot
    """
    def startSimulation(self):
        loop = gobject.MainLoop()

        handle = gobject.timeout_add(self.resetTimer, self.madeDecision)

        try:
            loop.run()
        except KeyboardInterrupt:
            self.resetRobot()
            loop.quit()

    """
        Mouvement du robot
    """
    def move(self, motorLeft, motorRight):
        # Get the values of the sensors
        deltaL = self.network.GetVariable("thymio-II", "prox.ground.delta")[0]
        deltaR = self.network.GetVariable("thymio-II", "prox.ground.delta")[1]

        """
            Selon la position, il faudrait remettre le robot rapidement a sa place
            Par exemple lorsqu'il est positionne a gauche il ne peut pas passer de gauche a droite sans aller au milieu
        """
        # Cas de base: capteur droit dans la marge et capteur gauche au dessus de la marge blanche
        if self.extreme != -1:
            if deltaR < self.parameters.getRangeWhite() and deltaR > self.parameters.getRangeBlack():
                print("Robot is centered", self.parameters.getRangeBlack(), "<", deltaR, "<", self.parameters.getRangeWhite())
                center = self.parameters.getRangeWhite() - self.parameters.getRangeBlack()
                if deltaR > center:
                    self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft * 1.1])
                    self.network.SetVariable("thymio-II", "motor.right.target", [motorRight])
                else:
                    self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft])
                    self.network.SetVariable("thymio-II", "motor.right.target", [motorRight * 1.1])
                self.position = Position.Position.MIDDLE
            else:
                # Si le robot est place au milieu, on fera une analyse classique: il commence a se diriger vers la droite ou vers la gauche
                if deltaR < self.parameters.getRangeBlack() or (deltaR > self.parameters.getRangeWhite() and deltaL > self.parameters.getRangeWhite()):
                    print("Robot is on the left")
                    self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft * 1.5])
                    self.network.SetVariable("thymio-II", "motor.right.target", [motorRight])
                    self.position = Position.Position.LEFT
                else:
                    print("Robot is on the right")
                    self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft])
                    self.network.SetVariable("thymio-II", "motor.right.target", [motorRight * 1.5])
                    self.position = Position.Position.RIGHT
            
            if self.position == Position.Position.LEFT:
                    self.extreme = self.extreme + 1
            elif self.position == Position.Position.RIGHT:
                    self.extreme = self.extreme + 1

            # On passe en mode recalibration (seulement dans le cas ou le plateau n'est pas parfaitement imprime avec la detection du noir / blanc)
            if self.extreme == 15:
                self.extreme = -1
                print("==== RECALIBRATE MODE ====")
        else:
            if self.position == Position.Position.LEFT:
                print("RECALIBRATE (LEFT): TURN ON THE RIGHT")
                self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft * 1.5])
                self.network.SetVariable("thymio-II", "motor.right.target", [motorRight * 0.75])
            elif self.position == Position.Position.RIGHT:
                print("RECALIBRATE (RIGHT): TURN ON THE LEFT")
                self.network.SetVariable("thymio-II", "motor.left.target", [motorLeft * 0.75])
                self.network.SetVariable("thymio-II", "motor.right.target", [motorRight * 1.5])

            if deltaR < self.parameters.getRangeWhite() and deltaR > self.parameters.getRangeBlack() and deltaL > self.parameters.getRangeWhite():
                print("==== RECALIBRATE DONE ====")
                self.position = Position.Position.MIDDLE
                self.extreme = 0
        
            

    """
        Fonction qui permet au robot de s'adapter selon la situation
    """
    def madeDecision(self):
        # Mouvement donna au robot selon les codes datectas
        if self.movement == Movement.Movement.STOPPED:
            # Rien, on trouvera un truc a faire
            print("Movement >", self.movement)

        elif self.movement == Movement.Movement.STRAIGHT:
            # Tout droit
            self.move(self.parameters.getSpeed(), self.parameters.getSpeed())

        elif self.movement == Movement.Movement.LEFTTIGHT:
            # A gauche serre
            self.move(self.parameters.getSpeed() * 0.25, self.parameters.getSpeed())
        elif self.movement == Movement.Movement.LEFT:
            # A gauche
            self.move(self.parameters.getSpeed() * 0.5, self.parameters.getSpeed())
        elif self.movement == Movement.Movement.LEFTWIDE:
            # A gauche large
            self.move(self.parameters.getSpeed() * 0.75, self.parameters.getSpeed())

        elif self.movement == Movement.Movement.RIGHTTIGHT:
            # A droite serre
            self.move(self.parameters.getSpeed(), self.parameters.getSpeed() * 0.25)
        elif self.movement == Movement.Movement.RIGHT:
            # A droite
            self.move(self.parameters.getSpeed(), self.parameters.getSpeed() * 0.5)
        elif self.movement == Movement.Movement.RIGHTWIDE:
            # A droite large
            self.move(self.parameters.getSpeed(), self.parameters.getSpeed() * 0.75)

        elif self.movement == Movement.Movement.DEBUG:
            # MODE DEBUG
            self.debug()

        return True

    """
        Debug: affichage des informations du robot
    """
    def debug(self):
        sensorR = self.network.GetVariable("thymio-II", "prox.ground.delta")[1]
        sensorL = self.network.GetVariable("thymio-II", "prox.ground.delta")[0]
        print("Debug > Sensors [L | R]:", sensorL, "|", sensorR)
