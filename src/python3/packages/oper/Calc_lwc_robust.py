#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    ADC : Opérateur CalcLwcRobust
"""

import sys, os

PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

from oper.default_out_header import default_out_header
import calcul

"""==============================================================================
 Fonction Opérateur

 Les arguments sont ceux de la ligne d'instruction ADC lue dans le .fil
 ***SANS*** les noms des VECTOR/DIR_OUT

 Les arguments de type VECTOR/DIR_IN reçus sont des AIDA.VectorMask.

 L'opérateur :
   - prépare les arguments pour appeller la fonction de calcul
   - appelle la fonction de calcul
   - prépare le(s) header(s) du/des vecteurs de retour.
   - retourne : [headers], [data], {'CodeRet' : int()>= 0, 'DiagExec': str()}

 NOTE : AIDAcalc et AIDA.Vector mettront à jour les attributs :
           hdr_name, date_creation, fct_origine et vol...
        des headers avant d'écrire les vecteurs.
=============================================================================="""
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

    # récupération des arguments
    ps_header = ps.attributes
    ps_data = ps.data.data
    ts_data = ts.data.data
    tas_data = tas.data.data
    ptot_data = ptot.data.data
    tp_data = tp.data.data

    # appel de la fonction de calcul
    lwc_data = calcul.Calc_lwc_robust.Calc_lwc_robust(ps_data, ts_data, tas_data, ptot_data, tp_data, k1, k2)

    # préparation du retour
    lwc_header = default_out_header.copy()
    lwc_header['english_name'] = "LWC calculated from Robust probe data and SEA manual operations"
    lwc_header['unit'] = "g/m3"
    lwc_header['freq_ech'] = "1"
    lwc_header['ref_time'] = f"{ps_header['ref_time']}"
    lwc_header['misval'] = "nan"

    diag = {'CodeRet': 0,
            'DiagExec': f"Calc_lwc_robust : ({len(lwc_data)} ech.)"
            }

    return [lwc_header], [lwc_data], diag

#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Calc_lwc_robust': {
        'Args': [
            {'Id': 'ps',    'categorie': 'VECTOR_IN',   'unit': 'hPa'},
            {'Id': 'ts',    'categorie': 'VECTOR_IN',   'unit': 'Celsius'},
            {'Id': 'tas',   'categorie': 'VECTOR_IN',   'unit': 'm/s'},
            {'Id': 'ptot',  'categorie': 'VECTOR_IN',   'unit': 'W'},
            {'Id': 'tp',    'categorie': 'VECTOR_IN',   'unit': 'Celsius'},
            {'Id': 'k1',    'categorie': 'COEFFICIENT'},
            {'Id': 'k2',    'categorie': 'COEFFICIENT'},
            {'Id': 'lwc',   'categorie': 'VECTOR_OUT'},
        ],
    },
}