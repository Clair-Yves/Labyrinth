# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 08:31:21 2019

@author: The Cy
"""
import random

listDirection = ("N", "S", "E", "W")
listCommands = ("P", "M")

class position:
    '''a tuple x,y representing a position on the maze map'''
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
    '''A maze is a set of lists of positions objects :
        list of walls, list of doors, list of players, position of the Exit'''

    def __init__(self, mazeName):
        listOfLists=splitIntoList("cartes/"+mazeName+".txt")
        self._murs=[]
        self._doors=[]
        self._freeSpaces=[]
        self._playersDico={}  # dictionnary of keys : player name and value : player position
        self._exit=position(0, 0)
        self._maxX=len(listOfLists)
        self._maxY=len(listOfLists[0])

        for x,liste in enumerate(listOfLists):
            for y,char in enumerate(liste):
                pos=position(x,y)
                if char=="O":
                    self.Walls.append(pos)
                elif char==".":
                    self.Doors.append(pos)
                elif char=="U":
                    self.setExit(pos)
                else:
                    self.FreeSpaces.append(pos)

    def __str__(self):
        map=""
        for x in range(0,self.getMaxX()):
            line=''
            for y in range(0,self.getMaxY()):
                posi=position(x,y)
                if posi in self.Walls:
                    line+="O"
                elif posi in self.PlayersDico.values():
                    line+="x"
                elif posi in self.Doors:
                    line+="."
                elif posi==self.getExit():
                    line+="U"
                else:
                    line+=" "
            map+=line+"\n"
        return map

    def getWalls(self):
        return self._murs

    def listAsString(self, liste):
        a=""
        for i in liste:
            a+=str(i)+"/ "
        return a


    def getDoors(self):
        return self._doors

    def getExit(self):
        return self._exit

    def setExit(self, newExit):
        self._exit=newExit

    def getFreeSpaces(self):
        return self._freeSpaces

    def getPlayersDico(self):
        return self._playersDico

    def getPlayerPos(self, playerName):
        return self.PlayersDico[playerName]

    def setPlayer(self,playerName, newPos):
        if self.PlayersDico[playerName] not in self.Doors:
            self.FreeSpaces.append(self.PlayersDico[playerName])
        if newPos in self.FreeSpaces:
            self.FreeSpaces.remove(newPos)
        self.PlayersDico[playerName]=newPos

    def addPlayer(self, playerName):
        pos=random.choice(self.FreeSpaces)
        self.PlayersDico[playerName]=pos
        self.FreeSpaces.remove(pos)

    def removePlayer(self, playerName):
        if self.PlayersDico[playerName] not in self.Doors:
            self.FreeSpaces.append(self.PlayersDico[playerName])
        del self.PlayersDico[playerName]

    def delPlayer(self, playerName):
        del self.getPlayersDico()[playerName]

    def getMaxX(self):
        return self._maxX

    def getMaxY(self):
        return self._maxY

    Walls=property(getWalls)
    Doors=property(getDoors)
    FreeSpaces=property(getFreeSpaces)
    PlayersDico=property(getPlayersDico)
    Exit=property(getExit, setExit)
    maxX=property(getMaxX)
    maxY=property(getMaxY)

    def labi_to_LabiString_for_playerName(self, playerName):
        '''Return the LabiString specific for the player named playerName i.e. put 'X' for his position, 'x' for other players positions'''
        map = ""
        for x in range(0, self.getMaxX()):
            line = ''
            for y in range(0, self.getMaxY()):
                posi = position(x, y)
                if posi in self.Walls:
                    line += "O"
                elif posi in self.PlayersDico.values():
                    if self.getPlayerPos(playerName)==posi:
                        line+="X"
                    else:
                        line += "x"
                elif posi in self.Doors:
                    line += "."
                elif posi == self.getExit():
                    line += "U"
                else:
                    line += " "
            map += line + "\n"
        return map


def listCases(PlayerPos, mvt):
    '''Renvoie la liste des positions entre la position du joueur et la direction donnée en input'''
    listePosi=[]
    pas=1
    if mvt[0]=="N" or mvt[0]=="W":
        pas=-1
    for i in range(1,mvt[1]+1):
        if mvt[0]=="N" or mvt[0]=="S":
            posi=position(PlayerPos.getX() + pas * i, PlayerPos.getY())
            listePosi.append(posi)
        else:
            posi=position(PlayerPos.getX(), PlayerPos.getY() + pas * i)
            listePosi.append(posi)
    return listePosi

def getNextCase(PlayerPos, Direction):
    '''Returns the position of the next case of the player in the given Direction'''
    if Direction.upper()=='N':
        return position(PlayerPos.getX() -1,PlayerPos.getY())
    if Direction.upper()=='S':
        return position(PlayerPos.getX() +1,PlayerPos.getY())
    if Direction.upper()=='E':
        return position(PlayerPos.getX(),PlayerPos.getY() +1)
    if Direction.upper()=='W':
        return position(PlayerPos.getX(),PlayerPos.getY() -1)

def isMoveLegal(labi,playerName,mvt):
    '''Check if the movement or play is possible given his position and the state of the maze, returns True if yes, False if not'''
    PlayerPos=labi.getPlayerPos(playerName)

    if type(mvt[1]) is int:
        listeDesCases=listCases(PlayerPos, mvt)

        listeCaseMur=[posi for posi in listeDesCases if posi in labi.Walls]
        if len(listeCaseMur)>0:
            return False

        listeCasesOut=[posi for posi in listeDesCases if posi.getX()<0 or posi.getY()<0
                       or posi.getX()>labi.getMaxX()-1 or posi.getY()>labi.getMaxY()-1]
        if len(listeCasesOut)>0:
            return False

        listCasesOtherPlayers=[posi for posi in listeDesCases if posi in labi.PlayersDico.values()]
        if len(listCasesOtherPlayers)>0:
            return False
    else:
        CasePos=getNextCase(PlayerPos,mvt[1])
        if mvt[0].upper()=="P" and CasePos not in labi.Walls:
            return False
        if mvt[0].upper()=="M" and CasePos not in labi.Doors:
            return False
    return True

def makeMove(labi,playerName,mvt):
    '''Check if the player doesn't go out of the maze and doesn't go through a wall
    If not set the new labi state (new wall or new door or new player position)
    Note : Players have to stop on a Door before continuing'''
    if isMoveLegal(labi,playerName,mvt):
        PlayerPos = labi.getPlayerPos(playerName)
        if mvt[0].upper() in listDirection:
            listeDesCases=listCases(PlayerPos, mvt)
            newPlayerPos=listeDesCases[len(listeDesCases)-1]  # by default player goes the maximum input distance
            for pos in listeDesCases: #but the player stops if he gets through a door to "open it"
                if pos in labi.getDoors():
                    newPlayerPos=pos
                    break
            labi.setPlayer(playerName,newPlayerPos)
        elif  mvt[0].upper() in listCommands:
            posiCase=getNextCase(PlayerPos,mvt[1])
            if mvt[0].upper() == "P":
                labi.Walls.remove(posiCase)
                labi.Doors.append(posiCase)
            if mvt[0].upper() == "M":
                labi.Doors.remove(posiCase)
                labi.Walls.append(posiCase)

def splitIntoList(cheminCarte):
    '''return a list of lists of characters (each list is a line) from the string content of a file with the file path as argument'''
    with open(cheminCarte,"r") as file:
        content=file.read()
    listeOfListes=[]
    liste=[]
    for char in content:
        if char !='\n':
            liste.append(char)
        else:
            listeOfListes.append(liste)
            liste=[]
    listeOfListes.append(liste)
    return listeOfListes
