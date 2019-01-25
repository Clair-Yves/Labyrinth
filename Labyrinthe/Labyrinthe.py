# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 10:17:20 2019

@author: The Cy
"""

import FrontEnd as FE
import os

nom=input("Quel est votre nom ?")
print("Bienvenue "+nom+"! Sortez du labyrinthe ou tapez Q pour enregistrer et quitter")
labi=FE.labi(nom)
print()
print(labi)

while not FE.Fin.getFin() :
    mvt=FE.nextMvt(nom,labi)
    if type(mvt) is not bool:
        FE.move(labi,mvt)
        print(labi)
        if FE.isWin(labi):
            FE.Fin.setFin(True)
            print("Bravo vous avez gagné !")
            FE.deleteGame(nom)
            os.system("pause")