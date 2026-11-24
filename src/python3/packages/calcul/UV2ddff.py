#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def UV2ddff(U, V):
    """
    Calcul des composantes du vent

    Input :
        U    : Composante méridienne du vent
        V    : Composante zonale du vent

    Output :
        DD  : Direction géographique du vent
        FF  : vitesse du vent

        
    Auteur :  CNRM/GMEI/TRAMM septembre 2019         
    """

    ff = np.sqrt(U*U+V*V,dtype = "f")

    dd = np.copy(ff)*np.nan
    # V == 0
    dd[ (U>0) & (V == 0) ] = -np.pi/2
    dd[ (U<0) & (V == 0) ] = np.pi/2
    dd[ (U == 0) & (V == 0) ] = 0

    # V > 0
    dd[ V>0 ] = np.arctan(U[ V>0 ]/V[ V>0 ]) + np.pi

    # V < 0
    dd[ V<0 ] = np.arctan(U[ V<0 ]/V[ V<0 ])

    #Passage de [-pi:pi] à [0:2*pi]
    dd[ dd<0 ] = dd[ dd<0 ]+2*np.pi

    #Conversion en degrés
    dd = dd*180/np.pi
    
        
    return dd,ff

