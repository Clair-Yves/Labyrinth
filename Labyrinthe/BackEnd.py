# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 08:31:21 2019

@author: The Cy
"""

import Storage as S

class position:
    '''un tuple x,y de positon sur la carte'''
    def __init__(self,x,y):
       self._x=x
       self._y=y

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def setX(self,newX):
        self._x=newX

    def setY(self,newY):
        self._y=newY

    x=property(getX,setX)
    y=property(getY,setY)

    def __eq__(self,pos):
        return self.getX()==pos.getX() and self.getY()==pos.getY()

    def __str__(self):
        return "(X:"+str(self.getX())+" , Y:"+str(self.getY())+")"

class Labyrinthe:
    '''listes des positions des murs, portes, joueur et sortie et fonctions de manipulation'''


    def __init__(self, nomJoueur):
        cheminCarte=S.createSession(nomJoueur)
        listeOfListes=S.splitIntoList(cheminCarte)
        self._murs=[]
        self._portes=[]
        self._joueur=position(0,0)
        self._sortie=position(0,0)
        self._maxX=len(listeOfListes)
        self._maxY=len(listeOfListes[0])

        for x,liste in enumerate(listeOfListes):
            for y,char in enumerate(liste):
                pos=position(x,y)
                if char=="O":
                    self.getMurs().append(pos)
                elif char==".":
                    self.getPortes().append(pos)
                elif char=="X":
                    self.setJoueur(pos)
                elif char=="U":
                    self.setSortie(pos)
                elif char=="Y": # au cas où la partie a été enregistrée avec un joueur sur une porte, on enregistrera la charactère Y
                    self.setJoueur(pos)
                    self.getPortes().append(pos)

    def __str__(self):
        '''renvoie le string à printer pour une instance de Labyrinthe'''
        carte=""
        for x in range(0,self.getMaxX()):
            ligne=''
            for y in range(0,self.getMaxY()):
                posi=position(x,y)
                if posi in self.getMurs():
                    ligne+="O"
                elif posi==self.getJoueur(): # on test la position du joueur avant celui de la porte car il peuvent être superposés et on veut afficher le joueur dans ce cas
                    ligne+="X"
                elif posi in self.getPortes():
                    ligne+="."
                elif posi==self.getSortie():
                    ligne+="U"
                else:
                    ligne+=" "
            carte+=ligne+"\n"
        return carte

    def getMurs(self):
        return self._murs

    def getPortes(self):
        return self._portes

    def getJoueur(self):
        return self._joueur

    def getSortie(self):
        return self._sortie

    def setJoueur(self,newJoueur):
        self._joueur=newJoueur

    def setSortie(self,newSortie):
        self._sortie=newSortie

    def getMaxX(self):
        return self._maxX

    def getMaxY(self):
        return self._maxY

    murs=property(getMurs)
    portes=property(getPortes)
    joueur=property(getJoueur,setJoueur)
    sortie=property(getSortie,setSortie)
    maxX=property(getMaxX)
    maxY=property(getMaxY)

def validInput(inpu):
    '''Renvoie True si input joueur est OK
    Renvoie False et print un msg d'erreur sinon'''
    listDirection=("N","S","E","W")
    try:
        int(inpu[1:])
    except ValueError:
         print("Mouvement non valide, veuillez siuvre la nommenclature suivante : \nDirection (N,S,W,E)" \
               +" et nombre de pas \nexemples: N3, E1, S2")
         return False
    if inpu[0] in listDirection:
        return True
    else:
        print("Directions possibles : (N,S,W,E)")
        return False

def listeCases(posiJoueur,mvt):
    '''Renvoie la liste des positions entre la position du joueur et la direction donnée en input'''
    listePosi=[]
    pas=1
    if mvt[0]=="N" or mvt[0]=="W":
        pas=-1
    for i in range(1,mvt[1]+1):
        if mvt[0]=="N" or mvt[0]=="S":
            posi=position(posiJoueur.getX()+pas*i,posiJoueur.getY())
            listePosi.append(posi)
        else:
            posi=position(posiJoueur.getX(),posiJoueur.getY()+pas*i)
            listePosi.append(posi)
    return listePosi

def isMoveLegal(labi,mvt):
    '''Renvoie True si le mvt est possible
    print un msg de pourquoi c'est pas possible et renvoie False sinon'''
    joueur=labi.getJoueur()
    listeDesCases=listeCases(joueur,mvt)

    listeCaseMur=[posi for posi in listeDesCases if posi in labi.getMurs()]
    if len(listeCaseMur)>0:
        print("Vous allez dans un mur !!  -> O")
        return False

    listeCasesOut=[posi for posi in listeDesCases if posi.getX()<0 or posi.getY()<0
                   or posi.getX()>labi.getMaxX()-1 or posi.getY()>labi.getMaxY()-1]
    if len(listeCasesOut)>0:
        print("Vous allez trop loin, veuillez sortir du labyrinthe par la sortie : U")
        return False

    return True

def makeMove(labi,mvt):
    '''Vérifie si on sort pas du labyrinthe ou si on va dans un mur
    Si Ok on séplace le X (position du joueur) dans l'objet Laby (on s'arrête sur un porte)'''
    if isMoveLegal(labi,mvt):
        joueur=labi.getJoueur()
        listeDesCases=listeCases(joueur,mvt)
        newPosJoueur=listeDesCases[len(listeDesCases)-1]  # par défaut le joueur va au bout du mouvement
        for pos in listeDesCases: #mais on s'arrête si le joueur tombe sur une porte
            if pos in labi.getPortes():
                newPosJoueur=pos
                break #on sort de la boucle après la premi_re porte trouvée
        labi.setJoueur(newPosJoueur)


def saveGame(nomJoueur,labi):
        '''Crée le string à sauvegarder'''
        carte=""
        for x in range(0,labi.getMaxX()):
            for y in range(0,labi.getMaxY()):
                pos=position(x,y)
                if pos in labi.getMurs():
                    carte+="O"
                    continue
                if pos in labi.getPortes():
                    if pos == labi.getJoueur():
                        carte+="Y"
                        continue
                    else:
                        carte+="."
                        continue
                if pos == labi.getJoueur():
                    carte+="X"
                    continue
                if pos == labi.getSortie():
                    carte+="U"
                    continue
                carte+=" "
            carte+="\n"

        S.saveLabi(nomJoueur, carte)

def deleteGame(nomJoueur):
    S.deleteGame(nomJoueur)

def unitTest(): #fction de test du  module, jamais appelé
    nomJoueur="Bob"
    labi=Labyrinthe(nomJoueur)
    print(labi)
    mvt=("S",3)
    makeMove(labi,mvt)
    print(labi)
    saveGame(nomJoueur,labi)


#unitTest()
