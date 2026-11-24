#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def PressAltiVect(P0, Tv, CtoK, Z0, Z, rsurg):
    """
    Calcul de la pression aux altitudes Z à partir des pressions P0 mesurées aux altitudes Z0. 

    Input :
        P0 : Pressions au niveau Z0
        Tv : Tempé virtuelle moyenne de la couche
        CtoK : Valeur à ajouter pour convertir en °K
        Z0 : Altitudes correpondantes à P0
        Z  : Altitudes pour lesquelles on calcule P
        rsurg : "constante" r/g

    Output :
        P  : Pressions aux altitude Z

        
    Auteur :  CNRM/GMEI/TRAMM septembre 2019         
    """
    data_P0 = np.ones(len(P0), dtype=float)
    data_P0[:] = P0

    data_Tv = np.ones(len(Tv), dtype=float)
    data_Tv[:] = Tv + CtoK
    
    data_Z0 = np.ones(len(Z0), dtype=float)
    data_Z0[:] = Z0

    data_Z = np.ones(len(Z), dtype=float)
    data_Z[:] = Z

    # Calcul des pressions
    P = data_P0 / np.exp ( ( data_Z - data_Z0 ) / ( rsurg * data_Tv ) );

    return P

