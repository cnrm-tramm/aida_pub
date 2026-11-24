#!/usr/bin/env python3

import sys
import numpy as np
import warnings
import math


def fct_Puissance_flt (X_data,p) :

    """
    Calcule le tableau X_data à  la puissance p
    
    Input :
        X_data        : variable de départ à échantillonner
        p             : puissance
        
    Output :
        var_out : X_data à la puissance p

    """
    cod_ret = 0
    var_out = np.copy(X_data)
    
    # Pré-diagnostics
    if np.isnan(p) :
        cod_ret = -1
    if cod_ret != 0 :
        return var_out, cod_ret
    
    # Calcul du vecteur à la puissance p
    var_out = X_data**p

    return np.array(var_out, dtype = np.float), cod_ret
