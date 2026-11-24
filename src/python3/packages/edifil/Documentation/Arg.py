#!/usr/bin/env python3

"""
Created on 9 mai 2019

@author: CNRM/GMEI/TRAMM
"""

import os
import sys
import logging

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
AL = os.path.join(AH, 'lib', PYTHON_X_Y)

class arg:
    """
    Gere les differents $arg disponibles
    """

    # Liste des constantes (String[]:String)
    arg_list = []
        
    # Nom du type d'argument de cette class (String)
    nomArgument = ""
    

    def __init__(self):
        '''
        Constructor
        '''
        self.load()
        
    def load(self):
        """
        Met en mémoire la liste des $arg
        """
        self.arg_list = []
        the_path = os.path.join(AL, 'edifil', 'ArgDoc.txt')
        fichierData = open(the_path, 'r', encoding='utf-8')
        try:
            # on prend chaques lignes du fichier
            text = fichierData.read().split("\n")
            for ligne in text:
                # on sépare le nom de sa description
                valeur = ligne.split(" : ",1)
                if len(ligne) != 0 and len(valeur) == 2:
                    # Si la ligne est correcte (pas vide par exemple), on l'ajoute
                    self.arg_list += [valeur[0].replace(" ","")]    
            
            fichierData.close()
        except:
            print("err chargement des $Arg : ArgDoc.txt")
            
    def find(self, nom):
        """
        Recherche une liste de $arg dont le nom commence par la
        chaine entree en parametre
        param :
            nom : String recherché dans arg_list
            
        return : 
            Liste des $arg correspondante (String[])
        """
        logging.debug(f":::: {'Documentation/Arg.py::find':25s} : ============ ")
        result_list = []
        for clee in self.arg_list:
            if clee.startswith(nom):
                result_list += [clee]
    
        return result_list
        
    def exist(self, nom):
        """
        Recherche un nom dans la liste et retourne True si
        il est present, False sinon
        """
        return self.arg_list.count(nom) != 0

