from enum import Enum
class Movement(Enum):
    STRAIGHT = "STRAIGHT" # Tout droit
    LEFTTIGHT = "LEFTTIGHT" # A gauche serre
    LEFT = "LEFT" # A gauche
    LEFTWIDE = "LEFTWIDE" # A gauche large
    RIGHTTIGHT = "RIGHTTIGHT" # A droite serre
    RIGHT = "RIGHT" # A droite
    RIGHTWIDE = "RIGHTWIDE" # A droite large
    DEBUG = "DEBUG"
    STOPPED = None # Par defaut: a l'arret