#!/usr/bin/env python3

"""
Created on 9 mai 2019

@author: CNRM/GMEI/TRAMM
"""

import os
import sys
import re

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA


class chrono:
    """
    Gere les differents $chrono disponibles
    """

    # Liste des constantes (String[]:String)
    arg_list = []
        
    # Nom du type d'argument de cette class (String)
    nomArgument = ""
    

    def __init__(self):
        """
        Constructor
        """
        
    def load(self,nom):
        """
        Met en mémoire la liste des $chrono
        argument :
            - nom, acqid (String)
        return :
            True si acqid valide
            False Sinon
        """
        self.arg_list = []
        # Recherche du nom complet de la plateforme
        try :
            nom = AIDA.ID_to_full(nom)[0]
        except :
            return False

        try :
            aida_profil = os.getenv('AIDA_PROFIL')
            path_chrono = os.path.join (AH, 'profils', aida_profil, 'chrono', nom + '.chrono')

            fichierData = open(path_chrono, "r", encoding="utf-8")
            # on prend chaques lignes du fichier
            text = fichierData.read()
            parenthese = re.compile("(\[(.*?)\])")
            text = parenthese.findall(text)
            for x in text:
                # Si la ligne est correcte (pas vide par exemple), on l'ajoute
                self.arg_list += [x[1]]    
              
            fichierData.close()
        except :
            print("Pas de fichier chrono pour la plateforme "+nom)
        
        return True
    
    def find(self, nom): 
        """
        Recherche une liste de $chrono dont le nom commence par la
        chaine entree en parametre
        param :
            nom : String recherché dans arg_list
            
        return : 
            Liste des $chrono correspondante (String[])
        """
    
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

