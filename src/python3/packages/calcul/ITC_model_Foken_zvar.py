#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def ITC_model_Foken_zvar(Ustar, LMO, Z, Hc, Lat):
    """
    Calcule la caracteristique integrale de la turbulence
    (Integral Turbulent Characteristis en anglais) à partir 
    des modèles fournis par Foken, avec une hauteur de mesure variable.

    Input :
        Ustar  : Vitesse de frottement
        LMO    : Longueur de Monin-Obukhov
        Z      : Hauteur de mesure (m)
        Hc     : Hauteur de la canopée (m)
        Lat    : Latitude (degres decimal)

    Output :
        ITCm_U : Caracteristique integrale de la turbulence selon U 
        ITCm_W : Caracteristique integrale de la turbulence selon W 
        ITCm_T : Caracteristique integrale de la turbulence selon T

        
    Auteur :  CNRM/GMEI/TRAMM avril 2023       
    """
    ITCm_U = np.ma.ones(len(Ustar))*np.nan
    ITCm_U.mask = np.ones(len(Ustar))
    ITCm_W = np.ma.ones(len(Ustar))*np.nan
    ITCm_W.mask = np.ones(len(Ustar))
    ITCm_T = np.ma.ones(len(Ustar))*np.nan
    ITCm_T.mask = np.ones(len(Ustar))
    
    # Calcul du paramètre de Coriolis
    f = abs( 2. * (2.*np.pi/(24.*60.*60.)) * np.sin(np.pi*Lat/180.) )

    for i in range(len(Ustar)) :
        # Z/L
        if Z.mask[i] or LMO.mask[i] or LMO[i]==0 :
            continue
        else :
            ZL = Z[i] / LMO[i]
            
        #
        # calcul de ITCm_U
        #
        if abs(ZL) < 0.032 :
            c1 = 2.7
            c2 = 0.0
        elif abs(ZL) >= 0.032 :
            c1 = 4.15
            c2 = 1./8.
        ITCm_U.data[i] = c1*pow(abs(ZL), c2 )
        ITCm_U.mask[i] = 0
             
        # after Thomas und Foken 2002 under near neutral conditions
        if -0.2 < ZL and ZL < 0.4 :
            if Ustar.mask[i] == 0 :
                ITCm_U.data[i]  = 0.44 * np.log(1. * f / Ustar[i]) + 6.3
                ITCm_U.mask[i] = 0
            else :
                ITCm_U.data[i] = np.nan
                ITCm_U.mask[i] = 1
                
        #
        # calcul de ITCm_W
        #
        if abs(ZL) < 0.032 :
            c1 = 1.3
            c2 = 0.0
        elif abs(ZL) >= 0.032 :
            c1 = 2.0
            c2 = 1./8.
        ITCm_W.data[i] = c1*pow(abs(ZL), c2 )
        ITCm_W.mask[i] = 0
             
        # after Thomas und Foken 2002 under near neutral conditions
        if -0.2 < ZL and ZL < 0.4 :
            if Ustar.mask[i] == 0 :
                ITCm_W.data[i]  = 0.21 * np.log(1. * f / Ustar[i]) + 3.1
                ITCm_W.mask[i] = 0
            else :
                ITCm_W.data[i] = np.nan
                ITCm_W.mask[i] = 1
                
        #                    
        # calcul de ITCm_T
        #
        if 0.02 <= ZL and ZL < 1. :  #stable
            c1 = 1.4
            c2 = -1./4.
        elif 0.02 > ZL and ZL >= -0.062 : #near neutral
            c1 = 0.5
            c2 = -1./2.
        elif -0.062 > ZL and ZL >= -1. : #unstable
            c1 = 1.0
            c2 = -1./4.
        elif -1. > ZL : #very unstable
           c1 = 1.0
           c2 = -1./3.
        elif ZL >= 1. : #very stable
            c1 = 1.4
            c2 = -1./3.
           
        ITCm_T.data[i] = c1*pow(abs(ZL), c2 )
        ITCm_T.mask[i] = 0
                    
    return ITCm_U, ITCm_W, ITCm_T
