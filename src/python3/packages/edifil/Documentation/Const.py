#!/usr/bin/env python3

"""
Gestion des constantes disponibles.
"""

import os
import sys

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import Constantes

class const:
    """
    Gere les differentes constantes disponibles.
    """

    # Liste des constantes (String[]:String)
    arg_list = []

    # dictionnaire des tooltips des constantes
    tooltips = dict()

    # Nom du type d'argument de cette class (String)
    nomArgument = ""


    def __init__(self):
        """
        Constructor
        """
        self.load()


    def load(self):
        """
        Met en mémoire la liste des constantes
        """
        self.arg_list = list(Constantes.AIDA_Csts.keys())
        self.tooltips = Constantes.AIDA_Csts_desc


    def find(self, nom):
        """
        Recherche une liste de constantes dont le nom commence par la
        chaine entree en parametre
        param :
            nom : String recherché dans arg_list

        return :
            Liste des operations correspondante (String[])
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


if __name__ == '__main__':
    constantes = const()

    print("\n=== liste des constantes")
    for c in constantes.arg_list:
        print(f"  - {c}")


    # recherche de constante
    word = 'ieee'
    print(f"\n=== recherche de '{word}' dans les constantes :")
    print(f"  - {constantes.find(word)}\n")


    # les tooltips
    for k, v in constantes.tooltips.items():
        print(f"  - {k}i : {v}")

