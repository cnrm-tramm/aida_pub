#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def fct_select_X_selon_Y(X_in,Y1,crit_min,crit_max,Yinval,misval):
    """
    Filtre des valeurs de X selon des seuils sur Y1
    On suppose que les bases de temps de X_in et Y1 sont identiques

    Input :
        X_in     : Paramètre à sélectionner 
        Y        : Paramètre selon lequel s'effectue la sélection
        crit_min : valeur minimale sur le critère Y
        crit_max : valeur maximale sur le critère Y
        Yinval   : valeur de Y qui permettra d'éliminer également des valeurs de X 
        misval   : valeur de remplacement de X lorsque Y ne correspond pas aux critères 

    Output :
        X_out  : X lorsque Y correspond aux critères
        
    Auteur :  CNRM/GMEI/TRAMM Juillet 2023         
    """

    ####
    # Pré-diagnostics 
    ####
    
    if X_in.ndim == 1 :
        tab_stat = np.array([0,0,0,0,0,0],dtype=np.int)
    else :
        tab_stat = np.zeros(([6]+list(X_in.shape)[1:]),dtype=np.int32)
    
    X_out = np.copy(X_in)

    # On teste également quand X n'est pas fini
    X_out[np.isfinite(X_in) == False] = misval
    tab_stat[4] = np.sum(np.isfinite(X_in) == False, axis = 0)

    # On teste les valeurs min et max
    X_out[Y1 < crit_min] = misval
    tab_stat[2] = np.sum(Y1 < crit_min, axis = 0)
    X_out[Y1 > crit_max] = misval
    tab_stat[1] = np.sum(Y1 > crit_max, axis = 0)

    # On teste également quand Y1 sont nan
    X_out[np.isnan(Y1)] = misval
    tab_stat[5] = np.sum(np.isnan(Y1), axis = 0)

    # On teste quand Y1 est égal à Yinval
    X_out[Y1 == Yinval] = misval
    tab_stat[3] = np.sum(Y1 == Yinval, axis = 0)

    tab_stat[0] = X_in.shape[0]
    tab_stat[0] = tab_stat[0] - tab_stat[1] - tab_stat[2] - tab_stat[3] - tab_stat[5]

    return X_out,tab_stat