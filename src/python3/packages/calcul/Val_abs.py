#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def fct_Val_abs(X_in):
    """
    Applique la valeur absolue

    Input :
        X_in     : Paramètre d'entrée 

    Output :
        X_out  : Paramètre d'entrée en valeur absolue
        
    Auteur :  CNRM/GMEI/TRAMM Mai 2024
    """
    
    X_out = np.absolute(X_in)

    return X_out