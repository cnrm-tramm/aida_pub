#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def fct_select_data(X_in,crit1_min,crit1_max,val,crit2_min = None,crit2_max = None):
    """
    Filtre des valeurs de X selon des seuils crit1_min, crit2_min, crit1_max, crit2_max

    Input :
        X_in     : Paramètre à sélectionner 
        crit1_min : valeur minimale pour le 1e critère
        crit1_max : valeur maximale pour le 1e critère
        crit2_min : valeur minimale pour le 2e critère
        crit2_max : valeur maximale pour le 2e critère
        val : valeur à remplacer

    Output :
        X_out  : X filtré
        
    Auteur :  CNRM/GMEI/TRAMM Mai 2024
    """

    ####
    # Pré-diagnostics 
    ####
    
    if X_in.ndim == 1 :
        tab_stat = np.array([0,0,0,0],dtype=np.int)
    else :
        tab_stat = np.zeros(([6]+list(X_in.shape)[1:]),dtype=np.int32)
    cod_ret = 0

    X_out = np.copy(X_in)

    # On v�rifie que crit1_min < crit1_max
    if crit1_min > crit1_max :
        cod_ret = -1

    # On v�rifie que crit2_min < crit2_max
    if crit2_min is not None :
        if crit2_min > crit2_max :
            cod_ret = -2

    if cod_ret != 0 :
        return X_out, cod_ret, tab_stat
    
    # Filtrage des données
    tab_stat[0] = np.nansum(X_out < crit1_min)
    tab_stat[1] = np.nansum(X_out > crit1_max)

    X_out[X_out < crit1_min] = val
    X_out[X_out > crit1_max] = val

    if crit2_min is not None :
        tab_stat[2] = np.nansum(X_out < crit2_min)
        tab_stat[3] = np.nansum(X_out > crit2_max)
        X_out[X_out < crit2_min] = val
        X_out[X_out > crit2_max] = val

    return X_out,cod_ret,tab_stat