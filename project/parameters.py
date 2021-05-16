# coding: utf8
#!/usr/bin/python
class Parameters:

    '''
    Classe représentant les paramètres suivants:
    -> vitesse des moteurs des roues
    -> valeurs extremes du niveau de gris: valeur du blanc, valeur du noir
    '''

    ##################################################################################
    #######################         CLASS CONSTRUCTOR          #######################

    def __init__(self, speed, rangeWhite, rangeBlack):
        '''
        @summary: Création des paramètres
        @param speed: Vitesse des moteurs des roues
        @type speed: int
        @param rangeWhite: Valeur de la couleur blanche
        @type rangeWhite: int
        @param rangeBlack: Valeur de la couleur noire
        @type rangeBlack: int
        '''
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
        '''
        @summary: Affichage des informations de la classe (vitesse des moteurs des roues, valeurs extremes du niveau de gris)
        '''
        return "Parameters > Robot speed:", self.speed, "- Range Level[W | B]:", self.rangeWhite, "|", self.rangeBlack


    ##################################################################################
    #######################             FUNCTIONS              #######################