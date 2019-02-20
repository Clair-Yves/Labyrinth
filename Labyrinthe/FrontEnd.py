# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 08:31:21 2019

@author: The Cy
"""

import BackEnd as BE

def nextMvt(inputJoueur):
    '''Takes the string input and returns a mvt tuple if the input is valid,
     return False if not'''
    if validInput(inputJoueur):
        if len(inputJoueur)==1:
            inputJoueur+="1" # if input is either N,S,W or E we continue with an N1, S1, W1 or E1 ofr the rest of the code
        try:
            int(inputJoueur[1:])
            return (inputJoueur[0].upper(),int(inputJoueur[1:]))
        except ValueError:
            return (inputJoueur[0].upper(),inputJoueur[1].upper())
    else:
        return False


def validInput(inputin):
    '''Return True is the input has a valid form, return False if not'''
    listDirection=BE.listDirection #("N","S","E","W")
    listCommands=BE.listCommands #("P","M")
    if len(inputin)==1 and inputin[0].upper() in listDirection:
        return True
    if len(inputin) > 1 and inputin[0].upper() in listDirection:
        try:
            int(inputin[1:])
            return True
        except ValueError:
            return False
    if inputin[0].upper() in listCommands:
        if len(inputin)==2 and inputin[1].upper() in listDirection:
            return True
        else:
            return False

def labi(nomJoueur):
    return BE.Labyrinthe(nomJoueur)

def move(labi,playerName,mvt):
    BE.makeMove(labi,playerName,mvt)


