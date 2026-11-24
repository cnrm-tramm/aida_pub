#!/usr/bin/env python3

"""
Created on 7 mai 2019

@author: CNRM/GMEI/TRAMM
"""

import os   
import sys
import configparser   

from .Element import element

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA


class gestVecteur(element):
    """
    Gere les differente familles de vecteur disponibles
    """

    # Liste des familles disponibles (String[])
    vect_list_famille = []
    
    # List des vecteur (selon l'acquid passé a self.load())
    vect_list = [ ]
    
    # Couleur représentant ce type d'element (String)
    couleur = ""
    
    # Nom definisant ce type d'element (String)
    nom = ""

    def __init__(self):
        '''
        Constructor
        '''
        # Met en mémoire la liste des éléments (familles des vecteurs )
        #Prend la liste des abrégés des vecteurs 
        self.vect_list_famille = []
        # lecture du fichier cfg contenant les vecteurs
        config_operations = configparser.ConfigParser(delimiters='=')
        the_path = os.path.join(AH, 'config', 'familles')
        config_operations.read(the_path)
        list_section = config_operations.sections()
          
        for section in list_section:
            self.vect_list_famille += [config_operations.get(section, "acronyme")]
        self.vect_list_famille += ["time"]
        
        #suppr des .vbn
        for i in range(len(self.vect_list_famille)):
            self.vect_list_famille[i] = self.vect_list_famille[i].replace(".vbn","")

    def load(self,acqid):
        """
        Met en mémoire la liste des éléments (abrégés des vecteurs)
        param : acqid (String)
        """
        try:
            path = AIDA.ID_to_datapath(acqid)
            self.vect_list = [f for f in os.listdir(path) if f.endswith('.vbn')]
        except:
            self.vect_list = []
        
        # effacer les extensions des noms des fichiers vecteur
        for i in range(len(self.vect_list)):
            self.vect_list[i] = self.vect_list[i].replace(".vbn","")
        
    def find(self, nom):
        """
        Recherche une list de vecteur dont le nom commence par la
        chaine entree en parametre
        param :
            nom : String recherché dans vect_list
            
        return : 
            Liste des noms des vecteurs correspondant (String[])
        """
        result_list = []
        for clee in self.vect_list:
            if clee.startswith(nom):
                result_list += [clee]
    
        return result_list
        
    def exist(self, nom):
        """
        Recherche un nom dans la liste et retourne True si
        il est present, False sinon
        """
        return self.vect_list.count(nom) != 0
    
    def is_vect(self, nom):
        for famille in self.vect_list_famille:
            if nom.startswith(famille):
                return True
        
        return False
    
    def add(self, nom):
        """
        Ajoute un nouveau vecteur a la liste
        Param :
            nom - Nom du nouveau vecteur
        
        """
        self.vect_list += nom

