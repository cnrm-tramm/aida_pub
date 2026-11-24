#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def fct_Select_X_selon_Y1Y2Y3Y4(X_in, 
                                Y1, Y2, Y3, Y4, 
                                crit_min_1, crit_max_1, crit_min_2, crit_max_2, crit_min_3, crit_max_3, crit_min_4, crit_max_4):
    """
    Filtre des valeurs de X selon des seuils sur Y1, Y2, Y3 et Y4.
    On suppose que les bases de temps de X_in, Y1, Y2, Y3, Y4 sont identiques

    Input :
        X_in : Données d'entrée 
        Y1 : Vecteur de critère de sélection 1
        Y2 : Vecteur de critère de sélection 2
        Y3 : Vecteur de critère de sélection 3
        Y4 : Vecteur de critère de sélection 4
        crit_min_1 : valeur minimale sur le critère 1
        crit_max_1 : valeur maximale sur le critère 1
        crit_min_2 : valeur minimale sur le critère 2
        crit_max_2 : valeur maximale sur le critère 2
        crit_min_3 : valeur minimale sur le critère 3
        crit_max_3 : valeur maximale sur le critère 3
        crit_min_4 : valeur minimale sur le critère 4
        crit_max_4 : valeur maximale sur le critère 4
        

    Output :
        X_out  : Données d'entrées filtrées selon les 4 critères
        
    Auteur :  CNRM/GMEI/TRAMM Juillet 2023         
    """
    # Initialisation des tableaux
    if X_in.ndim == 1 :
        tab_stat = np.array([0,0],dtype=np.int)
    else :
        tab_stat = np.zeros((2,X_in.shape[1]),dtype=np.int)
    
    X_out = np.ones(X_in.shape)*np.nan
    X_out[:] = X_in[:]

    ####
    # Pré-diagnostics 
    ####
    # Cette fonction ne marche que si X, Y1, Y2, Y3 et Y4 on les mêmes dimensions
    if X_in.shape == Y1.shape and X_in.shape == Y2.shape and X_in.shape == Y3.shape and X_in.shape == Y4.shape :
        code_ret = 0
    else :
        code_ret = -1
        return X_out,code_ret,tab_stat

   
    # On teste les valeurs 
    condition_Y1_min = np.array(Y1 > crit_min_1, dtype = int)
    condition_Y1_max = np.array(Y1 < crit_max_1, dtype = int)
    condition_Y2_min = np.array(Y2 > crit_min_2, dtype = int)
    condition_Y2_max = np.array(Y2 < crit_max_2, dtype = int)
    condition_Y3_min = np.array(Y3 > crit_min_3, dtype = int)
    condition_Y3_max = np.array(Y3 < crit_max_3, dtype = int)
    condition_Y4_min = np.array(Y4 > crit_min_4, dtype = int)
    condition_Y4_max = np.array(Y4 < crit_max_4, dtype = int)

    # On teste également quand Y1,Y2,Y3,Y4 sont nan
    condition_Y1_nan = np.array(np.isnan(Y1) == False, dtype = int)
    condition_Y2_nan = np.array(np.isnan(Y2) == False, dtype = int)
    condition_Y3_nan = np.array(np.isnan(Y3) == False, dtype = int)
    condition_Y4_nan = np.array(np.isnan(Y4) == False, dtype = int)

    # On addition les conditions
    combine_conditions = condition_Y1_min + condition_Y1_max + condition_Y2_min + condition_Y2_max + condition_Y3_min + condition_Y3_max +\
                         condition_Y4_min + condition_Y4_max + condition_Y1_nan + condition_Y2_nan + condition_Y3_nan + condition_Y4_nan

    X_out[np.where(combine_conditions != 12)] = np.nan

    tab_stat[1] = np.sum(combine_conditions != 12, axis = 0)
    tab_stat[0] = np.sum(combine_conditions == 12, axis = 0)

    return X_out,code_ret,tab_stat