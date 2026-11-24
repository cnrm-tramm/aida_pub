#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def Extract_subtab_fct(X_in, dimension, ax, bornes):
    """
    Extrait un sous tableau (ligne ou array en fonction de la dimension du vecteur d'origine)

    Input :
        X_in  : tableau d'entrée
        dimension : indice du tableau que l'on souhaite supprimer sur un axe ax
        ax : l'axe sur lequel on souhaite garder le tableau

    Output :
        X_out  : sous tableau extrait extraite


    
    Auteur :  CNRM/GMEI/TRAMM Août 2023         
    """
    fct_ret = 0
    try :
        dimension = int(dimension)
    except :
        fct_ret = -1

    try :
        ax = int(ax)
    except :
        fct_ret = -2
    
    if fct_ret != 0 :
        return X_in*np.nan, bornes, fct_ret
    

    X_out = np.take(X_in, dimension, axis = ax)

    # On trouve les bornes qui correspondent
    if X_in.ndim > 2 :
        bornes_out = "("+bornes.split('|')[ax][1:]
    else :
        bornes_out = bornes.split('((')[0]

    return X_out, bornes_out, fct_ret