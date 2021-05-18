import numpy as np
import cv2

#On importe notre image
img = cv2.imread('chemin.png')
#On convertit tout en gris pour pas se casser la tete avec les couleurs
imgGry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#On fait une approximation des contours
ret , thrash = cv2.threshold(imgGry, 240 , 255, cv2.CHAIN_APPROX_NONE)
contours , hierarchy = cv2.findContours(thrash, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

#On regarde combien de carré il détecte
detectedObject = 0
#Tableau qui va stocker tout les centres de nos contours
centers = []
#Tableau de nos couleurs
colors = []


for contour in contours:
    M = cv2.moments(contour)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    #C'est nos centres ici
    centroid = (cX,cY)
    approx = cv2.approxPolyDP(contour, 0.01* cv2.arcLength(contour, True), True)
    x = approx.ravel()[0]
    y = approx.ravel()[1] - 5
    if len(approx) == 4 :
        x, y , w, h = cv2.boundingRect(approx)
        aspectRatio = float(w)/h
        if aspectRatio >= 0.95 and aspectRatio < 1.05:
            #Si c'est un carré on draw les contours
            cv2.drawContours(img, [approx], 0, (255, 0, 0), 5)
            #On cale les centre sous forme de tuple cY,cX (l'inverse fait planter le programme)
            centers.append(tuple((cY,cX)))
            #cv2.circle(img, centroid, 7, (0, 255, 0), -1)    

#Fait +1 quand il voit un carré blanc
print("Nombre d'objets détectés : " + str(len(centers)))

#Du bas vers le haut
#Tableau de tout nos centres
print("Avant doublon : " + str(centers))
#Tableau qui va nous servir à savoir quels éléments sont en double (les blancs ici)
toDelete = []
#On boucle pour savoir quels sont les tuples en double
for i in range(0,len(centers)-1):
    if(centers[i][0]-centers[i+1][0]) < 10 :
        toDelete.append(tuple((centers[i][0],centers[i][1])))


#On les delete
for i in range (len(toDelete)):
    centers.remove(toDelete[i])

#On a notre tableau de centre sans doublons
print("Après enlever les doublons blancs : " + str(centers))

#On fait avec la couleur (à mettre plus tard avec des >= <=) pour la luminosité
for i in range(len(centers)):
    if (img[centers[i]] == [0,0,0]).all():
        colors.append("noir")
    elif (img[centers[i]] == [255,255, 255]).all():   
        colors.append("blanc")
    elif (img[centers[i]] == [36,28,237]).all():
        colors.append("rouge") 
    elif (img[centers[i]] == [232,162,0]).all(): 
        colors.append("bleu")      
print(colors)

cv2.imshow('Color Detection', img)
#Ne pas quitter le programme à la main 
#Toujours appuyer sur q pour bien tout couper
cv2.waitKey(0)
cv2.destroyAllWindows()

#Connecter le raspberry pi en ssh avec la co de la fac 
#Faire exécuter le code du robot par le raspberry en ssh 