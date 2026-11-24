#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import math
import sys
import numpy as np


def fct_WFR(X1, X2, A):
    """
    Calcul du champ de vent à partir du vent mesuré serlon un angle A par rapport à la verticale

    Input :
        X1 : 1e composante radiale du vent
        X2 : 2e composante radiale du vent
        A : angle entre le tir et la verticale

    Output :
        var_out : champ de vent reconstitué


        
    Auteur :  CNRM/GMEI/TRAMM juillet 2023      
    """

    var_out = (X1-X2)/(2*math.sin(math.radians(A)))

    return var_out

