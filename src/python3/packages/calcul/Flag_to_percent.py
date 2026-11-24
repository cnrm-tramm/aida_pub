#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np
from scipy import interpolate

def Flag_to_percent(X, Tx, f, Ty):
    """
    A partir d'un vecteur de flags et de sa base de temps,
    calcule le pourcentage d'une valeur de flag donnée sur une base de temps donnée. 

    Input :
        X : Variable flag d'entrée
        Tx : Variable temps associé à X
        f  : Valeur du flag à évaluer
        Ty : Variable temps associé à Y

    Output :
        Y : Variable Y contenant le pourcentage de f sur chaque période

        
    Auteur :  CNRM/GMEI/TRAMM septembre 2019         
    """
    #print("Flag à traiter : {}".format(f))
    data_X = np.ones(len(X), dtype=int)
    data_X[:] = X
    data_Tx = np.ones(len(Tx), dtype=float)
    data_Tx[:] = Tx

    data_Ty = np.ones(len(Ty), dtype=float)
    data_Ty[:] = Ty

    flag = f[0]

    count = np.zeros(len(data_Ty), dtype=int)
    count_f = np.zeros(len(data_Ty), dtype=int)
    i = 0
    for x,tx in zip(data_X, data_Tx) :
        if tx <= data_Ty[i] :
            count[i] += 1
            if x == flag :
                count_f[i] += 1
            if tx == data_Ty[i] :
                i += 1
        else :
            i += 1
    flags_pct = np.array((count_f/count)*100, dtype=float)

    return flags_pct

