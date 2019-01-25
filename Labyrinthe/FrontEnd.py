# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 08:31:21 2019

@author: The Cy
"""

import BackEnd as BE

class Fin:
    def __init__(self):
        self._fin=False

    def getFin(self):
        return self._fin

    def setFin(self,newFin):
        self._fin=newFin

    fin=property(getFin,setFin)

Fin=Fin()


def nextMvt(nomJoueur,labi):
    '''Demande au joueur son prochain mvt
    Test la validité de l'input via la fct validInput de BackEnd
    Renvoie un tuple de mvt ex : (N,3)'''

    inputJoueur=input("Next move : ")
    if inputJoueur=="Q":
        BE.saveGame(nomJoueur,labi)
        Fin.setFin(True)
        return True
    while not BE.validInput(inputJoueur):
        inputJoueur=input("Next move : ")
    return (inputJoueur[0],int(inputJoueur[1:]))


def labi(nomJoueur):
    return BE.Labyrinthe(nomJoueur)

def move(labi,mvt):
    BE.makeMove(labi,mvt)

def isWin(labi):
    return labi.getJoueur()==labi.getSortie()

def deleteGame(nomJoueur):
    BE.deleteGame(nomJoueur)

def uniTest(): #fction de test du  module, jamais appelé
    nom="Bob"
    labi=BE.Labyrinthe(nom)
    print(labi)
#    print(afficher(labi))
#    mvt=nextMvt()
#    print(mvt)


#uniTest()