#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    ADC : Opérateur TKE
"""

import sys
import os
import logging
import numpy as np

logger = logging.getLogger('adc')

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
from oper.default_out_header import default_out_header
import calcul

#==============================================================================
# Fonction Opérateur
#
# Les arguments sont ceux de la ligne d'instruction ADC lue dans le .fil
# ***SANS*** les noms des VECTOR/DIR_OUT
#
# Les arguments de type VECTOR/DIR_IN reçus sont des AIDA.VectorMask.
#
# L'opérateur :
#   - prépare les arguments pour appeller la fonction de calcul
#   - appelle la fonction de calcul
#   - prépare le(s) header(s) du/des vecteurs de retour.
#   - retourne : [headers], [data], {'CodeRet' : int()>= 0, 'DiagExec': str()}
#
# NOTE : AIDAcalc et AIDA.Vector mettront à jour les attributs :
#           #hdr_name, date_creation, fct_origine et vol...
#        des headers avant d'écrire les vecteurs.
#==============================================================================
def TKE(X, Y, Z, T_int, rap_mnq):
    """
    calcul de la TKE sur un temps de référence 
    """
    logger.debug("TKE : debut")

    # récupération des arguments
    X_header     = X.attributes
    X_data       = X.data.data
    Y_data       = Y.data.data
    Z_data       = Z.data.data
    
    #
    # préparation des arguments pour la fonction de calcul
    #        
    # - récupération des données du vecteur temps de X
    time_X_data   = X.timedata()

    #
    # appel de la fonction de calcul
    #
    var_out_data, cod_ret, tab_stat = calcul.TKE.fct_TKE(X_data, Y_data, Z_data, time_X_data, T_int, rap_mnq)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    X_out_header = default_out_header.copy()
    X_out_header['name']         = f"Energie Cinétique Turbulente"
    X_out_header['english_name'] = f"Turbulent Kinetic Energy"
    X_out_header['unit']         = f"m2.s-2"
    if var_out_data.ndim > 1 :
        X_out_header['bornes']         = f"{X_header['bornes']}"
        X_out_header['unit_bornes']         = f"{X_header['unit_bornes']}"
    X_out_header['freq_ech']     = f"{X_header['freq_ech']}"
    X_out_header['ref_time']     = f"{X_header['ref_time']}_Med_%{int(T_int)}"
    X_out_header['misval']       = f"{X_header['misval']}"
    X_out_header['dim_array']    = f"{X_header['dim_array']}"

    if cod_ret == -1 :
        msg_1 = f"ERREUR : Temps d'intégration négatif (T_int = {T_int})"
    elif cod_ret == -3 :
        msg_1 = f"ERREUR : rap_mnq non compris entre 0 et 1 (rap_mnq = {rap_mnq})"
    else :
        msg_1 = "OK"
        
        msg_1 = f" OK: {var_out_data.shape} valeurs en sortie. Valeurs en sortie : " +\
                f"OK:{tab_stat[0]}, pas_assez:{tab_stat[1]}"

    diag = {'CodeRet' : cod_ret,
            'DiagExec': f"{msg_1}"
           }
    
    return [X_out_header], \
           [var_out_data], \
           diag

#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'TKE': {
        'Args': [
           {'Id': 'X'          , 'categorie': 'VECTOR_IN'   },
           {'Id': 'Y'          , 'categorie': 'VECTOR_IN'   },
           {'Id': 'Z'          , 'categorie': 'VECTOR_IN'   },
           {'Id': 'T_int'      , 'categorie': 'COEFFICIENT' },
           {'Id': 'rap_mnq'    , 'categorie': 'COEFFICIENT' },
           {'Id': 'X_out'      , 'categorie': 'VECTOR_OUT'  }
        ],

    }
}


#==============================================================================
# Test de l'opérateur
#==============================================================================
if __name__ == '__main__':

    import AIDA


    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

    # Données 1D
    acqid = 'ls230242'
    logger.info(f'=== {acqid}')
    X        = AIDA.VectorMask(acqid, 'ven_u_metek_Frc200_2D_20')
    Y        = AIDA.VectorMask(acqid, 'ven_v_metek_Frc200_2D_20')
    Z        = AIDA.VectorMask(acqid, 'ven_w_metek_Frc200_2D_20')
    T_int    = 1800
    rap_mnq  = 0.5

    ##Données 2D
    acqid = 'Ce210185'
    logger.info(f'=== {acqid}')
    X        = AIDA.VectorMask(acqid, 'ven_u_windcube_Frc200_%4')
    Y        = AIDA.VectorMask(acqid, 'ven_v_windcube_Frc200_%4')
    Z        = AIDA.VectorMask(acqid, 'ven_w_windcube_Frc200_%4')
    T_int    = 1800
    rap_mnq  = 0.5



    # appel de l'opérateur
    logger.info('*** appel de TKE')
    headers, datas, diag = TKE(X, Y, Z, T_int, rap_mnq)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in header.items():
            logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data[0:5] = {data[0:5]}")
        logger.info(f"data[5:] = {data[-5:]}")
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
