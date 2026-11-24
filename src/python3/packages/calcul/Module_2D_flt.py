#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def fct_Module_2D_flt(X_in_1,X_in_2):
    """
    Calcul du module du vecteur à partir des 2 composantes X_in_1 et X_in_2 

    Input :
        X_in_1 : 1e composante du vecteur
        X_in_2 : 2e composante du vecteur

    Output :
        X_out  : Module du vecteur

        
    Auteur :  CNRM/GMEI/TRAMM Juillet 2023         
    """

    X_out = np.sqrt(X_in_1 * X_in_1 + X_in_2 * X_in_2)

    return X_out

