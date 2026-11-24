#!/usr/bin/env python3

'''
Created on 7 mai 2019

@author: CNRM/GMEI/TRAMM
'''
from abc import ABC, abstractmethod

class element(ABC):

    # Met en mémoire la liste des éléments
    @abstractmethod
    def load(self):
        pass
    
    # Recherche ne liste d'element comportant le texte recherché 
    @abstractmethod
    def find(self, text):
        pass
    
    # True si l'element est présent
    @abstractmethod
    def exist(self, text):
        pass
