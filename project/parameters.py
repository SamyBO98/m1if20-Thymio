#!/usr/bin/python
class Parameters:

    ##################################################################################
    #######################   EXPLANATIONS ABOUT THIS CLASS    #######################

    """
        Les parametres vont contenir plusieurs choses.
        -> Plage de niveau de gris: pour que le robot se repere au sol
        -> Vitesse du robot: constante.
    """

    ##################################################################################
    #######################         CLASS CONSTRUCTOR          #######################

    def __init__(self, speed, rangeWhite, rangeBlack):
        self.speed = speed
        self.rangeWhite = rangeWhite
        self.rangeBlack = rangeBlack


    ##################################################################################
    #######################              GETTERS               #######################

    def getSpeed(self):
        return self.speed

    def getRangeWhite(self):
        return self.rangeWhite

    def getRangeBlack(self):
        return self.rangeBlack


    ##################################################################################
    #######################              SETTERS               #######################

    def setSpeed(self, speed):
        self.speed = speed

    def setRangeWhite(self, rangeWhite):
        self.rangeWhite = rangeWhite

    def setRangeBlack(self, rangeBlack):
        self.rangeBlack = rangeBlack


    ##################################################################################
    #######################       CLASS STRING FOR DEBUG       #######################

    def toString(self):
        return "Parameters > Robot speed:", self.speed, "- Range Level[W | B]:", self.rangeWhite, "|", self.rangeBlack


    ##################################################################################
    #######################             FUNCTIONS              #######################