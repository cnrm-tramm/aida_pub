#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""

import numpy as np

def Calc_lwc_robust(ps, ts, tas, ptot, tp, k1, k2):
    """Calcul du lwc de la robust a partir des donnees des arguments ci-dessous.
    Entrees :
        ps  : pression statique.
        ts  : temperature statique.
        tas : vitesse air.
        ptot: puissance totale robust.
        tp  : temperature sonde robust.
        k1  : coefficient de calcul de la puissance seche robust.
        k2  : coefficient de calcul de la puissance seche robust.

    Sortie :
        lwc : lwc calculee a partir des donnees robust.

    Auteur : @Safire ITD/TAD - Fevrier 2023"""
    lp, wp = 22.733, 3.632  # dimensions sonde robust en mm
    
    data_ps = np.ones(len(ps), dtype=float)
    data_ps[:] = ps
    data_ts = np.ones(len(ts), dtype=float)
    data_ts[:] = ts
    data_tas = np.ones(len(tas), dtype=float)
    data_tas[:] = tas
    data_ptot = np.ones(len(ptot), dtype=float)
    data_ptot[:] = ptot
    data_tp = np.ones(len(tp), dtype=float)
    data_tp[:] = tp

    # calcul d'estimation de la Pdry
    data_pdry = k1 * (data_tp - data_ts) * np.power((data_ps * data_tas), k2)

    # calculs de Tevap (Celsuis) et Levap (cal/g)
    # note: calculs ok pour 100hPa < Ps < 1050hPa
    data_tevap = 32.16 + .1801 * data_ps - 2.391E-4 * np.power(data_ps, 2) + \
                 1.785E-7 * np.power(data_ps, 3) - 5.19E-11 * np.power(data_ps, 4)
    data_levap = 594.4 - .484 * data_tevap - 7.0E-4 * np.power(data_tevap, 2)

    # calcul de LWC (g/m3) avec numerateur Pwet = Ptot - Pdry
    data_lwc = 2.389E5 * (data_ptot - data_pdry) / \
               (data_tas * lp * wp * (data_levap + data_tevap - data_ts))

    return data_lwc