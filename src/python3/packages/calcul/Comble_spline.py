#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np
from scipy import interpolate

def Comble_spline(X, lissage):
    """
    Remplacement des valeurs manquantes en utilisant une interpolation par spline

    Input :
        X       : data paramètre à combler
        lissage : lissage (>=0, préconisé = 5)

    Output :
        Xc : data X comblées
        Flag_Xc : Flag valant 1 pour les valeurs de X qui ont été remplacées, 0 pour les autres. 
        
    Auteur :  CNRM/GMEI/TRAMM septembre 2019         
    """

    #lissage = np.ones(len(l), dtype=int)
    #lissage[:] = l
    
    flag_datas = np.zeros(len(X))
    datas = np.ones(len(X))
    datas[:] = X
    if np.isnan(datas).all() :
        print("-+- Le vecteur ne contient que des nans, pas d'interpolation possible") 
        return datas,flag_datas 
    if not np.isnan(datas).any() :
        print("-+- Le vecteur ne contient pas de nans, pas d'interpolation") 
        return datas,flag_datas

    all_index = range(len(X))
    nan_index = np.where(np.isnan(datas))[0]
    not_nan_index = np.where(~np.isnan(datas))[0]
    not_nan_datas = datas[not_nan_index]
    tck = interpolate.splrep(not_nan_index, not_nan_datas, s=lissage)
    new_datas = interpolate.splev(nan_index, tck, der=0)
    datas[nan_index] = new_datas
    flag_datas[nan_index] = 1.0

    return datas, flag_datas

