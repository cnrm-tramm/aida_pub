#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""
import sys
import numpy as np


def Test_and_demo(T, CtoK, OPT=None):
    """
    Cette fonction de calcul sert à faire des tests de ADC.
    ELLE NE DOIT PAS ÊTRE UTILISÉE POUR FAIRE DE LA PRODUCTION DE DONNÉES.

    Input :
        T        : température
        CtoK     : coef de passage de Celsius à Kelvin

    Output :
        P  : valeurs de retour


    Auteur :  CNRM/GMEI/TRAMM septembre 2022
    """
    data_T = np.ones(len(T), dtype=float)
    data_T[:] = T

    coef = CtoK
    if OPT:
        coef = CtoK - int(OPT)

    # Calcul des pressions
    P = data_T + coef

    return P

