#!/usr/bin/env python3

'''
Created on 10 mai 2019

@author: CNRM/GMEI/TRAMM
'''
from edifil.Documentation.GestOper import gestOper
from edifil.Documentation.GestArgSpe import gestArgSpe
from edifil.Documentation.GestVecteur import gestVecteur

class model(object):
    
    def __init__(self):
        
        # Chargement des données
        self.gest_oper = gestOper()
        self.gest_arg_spe = gestArgSpe()
        self.gest_vecteur = gestVecteur()
        
        
    def find_description (self, nom):
        list = []
        list_oper = self.gest_oper.find(nom)
        for oper in list_oper:
            list += [oper.description]
        return list
