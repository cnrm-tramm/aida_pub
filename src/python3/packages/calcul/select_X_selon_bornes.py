#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import numpy as np


def fct_select_X_selon_bornes(X_in,bornes,crit_min,crit_max,axe,dim_array):
    """
    Filtre des valeurs de X_in selon des seuils sur les bornes de X_in

    Input :
        X_in     : Paramètre à sélectionner 
        crit_min : valeur minimale 
        crit_max : valeur maximale
        axe : axe sur lequel s'effectue la sélection
        dim_array : dimension du tableau

    Output :
        X_out  : X lorsque Y correspond aux critères
        
    Auteur :  CNRM/GMEI/TRAMM Juillet 2023         
    """
    ####
    # Diagnostiques d'entrée
    ####
    cod_ret = 0
    try : 
        crit_min = float(crit_min)
    except : 
        cod_ret = -1
    try : 
        crit_max = float(crit_max)
    except : 
        cod_ret = -2
    try : 
        axe = int(axe)
    except : 
        cod_ret = -3

    if cod_ret != 0 :
        return X_filter*np.nan, bornes, cod_ret
    ####
    # Selection des valeurs en fonction des bornes
    ####

    bornes_num = bornes[:,0]
    dim_array = list(dim_array)
    dim_array = [0] + dim_array
    index_dim_array = np.cumsum(dim_array)
    
    # On créé une liste avec les bornes
    list_bornes = []
    for d in range(len(index_dim_array)-1) :
        list_bornes.append(list(bornes_num[index_dim_array[d]:index_dim_array[d+1]]))
       
    bornes_ok = [x for x in list_bornes[axe-1] if crit_min <= x <= crit_max]
    bornes_nok = [x for x in list_bornes[axe-1] if crit_min > x or x > crit_max]
    index_bornes_ok = [list_bornes[axe-1].index(x) for x in bornes_ok]

    X_filter = np.take(X_in,index_bornes_ok,axis = axe)

    ####
    # Calcul des nouvelles bornes
    ####
    # On supprime les bornes qu'on a enlevé dans la liste des bornes 
    for b in bornes_nok :
        list_bornes[axe-1].remove(b)
    str_bornes = ""
    for i in range(len(list_bornes)) :
        for j in range(len(list_bornes[i])) :
            str_bornes = str_bornes + "(" + str(list_bornes[i][j]) + "," + str(list_bornes[i][j])+ ");"
        str_bornes = str_bornes[:-1] + "|"
    # On enlève le pip de fin et la virgule de début
    str_bornes = str_bornes[:-1]

    return X_filter, str_bornes, cod_ret