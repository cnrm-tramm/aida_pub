#!/usr/bin/env python3

"""
    ADC : Opérateur Comble_spline
"""

import sys
import os
import logging
import numpy as np

logger = logging.getLogger('adc')

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

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
def Comble_spline(X, lissage):
    """
    Remplacement des valeurs manquantes en utilisant une interpolation par
    spline.

    Input :
        X       : data paramètre à combler
        lissage : lissage (>=0, préconisé = 5)

    Output :
        Xc      : data X comblées
        Flag_Xc : Flag valant 1 pour les valeurs de X qui ont été remplacées,
                  0 pour les autres. 

    Auteur : @Météo-France CNRM/GMEI/TRAMM - September 2019
    """
    logger.debug("Comble_spline : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    # appel de la fonction de calcul
    Xc_data, Flag_Xc_data = \
        calcul.Comble_spline.Comble_spline(X_data, lissage)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X.get_names()

    Xc_header                      = default_out_header.copy()
    Xc_header['name']              = f"{X_fr_name}"
    Xc_header['english_name']      = f"{X_en_name}"
    Xc_header['unit']              = f"{X_header['unit']}"
    Xc_header['freq_ech']          = f"{X_header['freq_ech']}"
    Xc_header['ref_time']          = f"{X_header['ref_time']}"
    Xc_header['misval']            = f"{X_header['misval']}"

    Flag_Xc_header                 = default_out_header.copy()
    Flag_Xc_header['name']         = f"{X_fr_name}"
    Flag_Xc_header['english_name'] = f"{X_en_name}"
    Flag_Xc_header['unit']         = 'unitless'
    Flag_Xc_header['freq_ech']     = f"{X_header['freq_ech']}"
    Flag_Xc_header['ref_time']     = f"{X_header['ref_time']}"
    Flag_Xc_header['misval']       = f"{X_header['misval']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"Comble_spline : ({len(X_data)} ech.)"
           }

    return [Xc_header, Flag_Xc_header], \
           [Xc_data  , Flag_Xc_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Comble_spline': {
        'Args': [
            {'Id': 'X'      , 'categorie': 'VECTOR_IN'  },
            {'Id': 'lissage', 'categorie': 'COEFFICIENT'},
            {'Id': 'Xc'     , 'categorie': 'VECTOR_OUT' },
            {'Id': 'Flag_Xc', 'categorie': 'VECTOR_OUT' },
        ],
    },
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


    # Comble_spline (
    #   hum_abs_wvss_rs_sync_1,
    #   5,
    #   hum_abs_wvss_rs_sync_com_spline_1,
    #   ctl_flag_sync_comspline_1)

    # sur de vrais vecteurs
    acqid = 'as210033'
    logger.info(f'=== {acqid}')
    X          = AIDA.VectorMask(acqid, 'hum_abs_wvss_rs_sync_1')
    lissage    = 5

    # appel de l'opérateur
    logger.info('*** appel de Comble_spline')
    headers, datas, diag = Comble_spline (X, lissage)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in header.items():
            logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data[0:5] = {data[0:5]}")
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
