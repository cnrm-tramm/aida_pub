#!/usr/bin/env python3

"""
Created on 7 mai 2019

@author: CNRM/GMEI/TRAMM
"""

import logging

from .Element import element
from .Arg     import arg
from .Chrono  import chrono
from .Const   import const


class gestArgSpe(element):
    """
    gestArgSpe
    """

    # liste des constantes (Const)
    constantes = None

    # liste des $Chrono (Chrono)
    argChrono = None

    # liste des $Arg (Arg)
    arguments = None

    # couleur représentant ce type d'élément (String)
    couleur = ""

    # nom définisant ce type d'élément (String)
    nom = ""


    def __init__(self):
        """
        Gère les différents arguments spécialisés disponibles (les $arg,
        $chrono, ... notament)
        """
        self.constantes = const()
        self.argChrono  = chrono()
        self.arguments  = arg()


    def load(self):
        """
        Met en mémoire la liste des arguments spécialisés (pas Chrono qui
        demande un acqid (de type string)).
        """
        self.constantes.load()
        self.arguments.load()


    def find(self, nom):
        """
        Recherche une liste d'arguments spécialisés dont le nom commence par la
        chaîne passée en paramètre.

        :param str() nom : chaîne recherchée dans les arguments spécialisés.

        :return: liste des arguments spécialisés correspondants.
        """
        logging.debug(f":::: {'Documentation/GestArgSpe.py::find':25s} : DEBUT ")
        return self.constantes.find(nom) + \
               self.argChrono.find(nom)  + \
               self.arguments.find(nom)



    def get_constante_tooltip(self, nom):
        """
        Retourne le tooltip de la constante 'nom' ou None.
        """
        logging.debug(f":::: {'Documentation/GestArgSpe.py::get_constante_tooltip':25s} : DEBUT ")
        if nom in self.constantes.tooltips.keys():
            return  self.constantes.tooltips[nom]
        else:
            return None

    def exist(self, nom):
        """
        Recherche un nom dans les listes d'arguments spécialisés.
        Retourne True si il est présent, False sinon.
        """
        return self.constantes.exist(nom) or \
               self.argChrono.exist(nom)  or \
               self.arguments.exist(nom)


    def exist_constante(self, nom):
        """
        Retourne True si 'nom' est le nom d'une constante, False sinon.
        Retourne True si il est présent, False sinon.
        """
        return self.constantes.exist(nom)

