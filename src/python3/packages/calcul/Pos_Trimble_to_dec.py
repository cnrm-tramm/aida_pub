#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""

import numpy as np

def Pos_Trimble_to_dec(pos, pos_dir):
    """Calcul de la position decimale en fonction des donnees brutes Trimble
    et de l'axe de projection.
    Entrees :
        pos  : position de la plateforme (latitude ou longitude).
        pos_dir  : axe de projection de la position (Nord/Sud/Est/Ouest).

    Sortie :
        pos_dd : position de la plateforme calculee selon l'axe de projection.

    Auteur : @Safire ITD/TAD - Mai 2023"""

    frac, intnum = np.modf(pos / 100)
    pos_dd = intnum + frac * 5 / 3
    if 'S' in pos_dir:
        pos_dd[pos_dir == 'S'] *= -1
    elif 'W' in pos_dir:
        pos_dd[pos_dir == 'W'] *= -1

    return pos_dd