#!/usr/bin/env python3

"""
Created on 7 mai 2019

@author: CNRM/GMEI/TRAMM
"""


class operation:

    # Nom de l'opération (String)
    nom = ""

    # Arguments de l'opérateur dans l'ordre [String[]]
    args = list()

    # Arguments optionnels de l'opérateur dans l'ordre { opt_name: str(type) }
    args_opt = dict()

    # Description de l'opérateur (String)
    description = ""

    def __init__(self, nom, args, args_opt, description, nb_vectors_in=1):
        """
        Constructor

        nb_vectors_in : nombre d'argument de type "Vecteur d'entrée" (sera
                        utilisé pour inscrire les $ArgX.yyy dans les lignes
                        de commande)
        """
        self.nom         = nom
        self.args        = args
        self.args_opt    = args_opt
        self.description = description

        self.nb_vectors_in = nb_vectors_in


