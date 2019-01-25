# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 08:31:21 2019

@author: The Cy
"""
import os

def createSession(nomJoueur):
    '''cherche la partie à partir du nom et renvoie le chemin
    Si le joueur n'a pas de partie, demande quelle carte, crée le fichier et renvoie le chemin'''
    listeParties=os.listdir("cartes/parties")
    trouve=False
    for fic in listeParties:
        nom=fic[::-1]
        nom=nom[:nom.index("_"):-1]
        if nomJoueur == nom :
            trouve=True
            return "cartes/parties/"+fic
            break
    if not trouve:
        print("Choisir une map:")
        listeCartes=os.listdir("cartes")
        listeCartes.remove("parties")
        for i,fic in enumerate(listeCartes):
            print(str(i)+": "+fic)
        choix=int(input())
        with open("cartes/parties/"+nomJoueur+"_"+listeCartes[choix],'w') as newFic:
            with open("cartes/"+listeCartes[choix],'r') as carteVierge:
                contenuCarteVierge=carteVierge.read()
                newFic.write(contenuCarteVierge)
        return "cartes/parties/"+nomJoueur+"_"+listeCartes[choix]


def splitIntoList(cheminCarte):
    '''prend le chemin vers la carte selctionée et renvoie une liste de listes de charactère'''
    with open(cheminCarte,"r") as fichier:
        contenu=fichier.read()

        listeOfListes=[]
        liste=[]
        for char in contenu:
            if char !='\n':
                liste.append(char)
            else:
                listeOfListes.append(liste)
                liste=[]
        listeOfListes.append(liste)

    return listeOfListes

def saveLabi(nomJoueur, carte):
    '''Save the game in a .txt file'''
    cheminCarte=createSession(nomJoueur)
    with open(cheminCarte,'w') as savedGame:
        savedGame.write(carte)

def deleteGame(nomJoueur):
    cheminCarte=createSession(nomJoueur)
    os.remove(cheminCarte)

def unitTest():  #fction de test du  module, jamais appelé
    nom=input("Donnez nom du joueur : ")
    chemin=createSession(nom)
    Listes=splitIntoList(chemin)
    print(Listes)


#unitTest()