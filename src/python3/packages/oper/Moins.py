#!/usr/bin/env python3

"""
    ADC : Opérateur Moins
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
def Moins(X, Y):
    """
    calcul la soustraction entre deux vecteurs
    """
    logger.debug("Moins : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    Y_header = Y.attributes
    Y_data   = Y.data.data

    # appel de la fonction de calcul
    Z_data = calcul.Moins.fct_Moins(X_data,Y_data)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name               = X.get_names()
    Y_fr_name, Y_en_name               = Y.get_names()

    Z_header                 = default_out_header.copy()
    Z_header['name']         = f"Soustraction de {X_fr_name} et {Y_fr_name}"
    Z_header['english_name'] = f"Soustraction of {X_en_name} and {Y_en_name}"
    Z_header['ref_time']     = f"{X_header['ref_time']}"
    Z_header['unit']         = f"{X_header['unit']}"
    if Z_data.ndim > 1 :
        Z_header['bornes']       = f"{X_header['bornes']}"
        Z_header['unit_bornes']  = f"{X_header['unit_bornes']}"
    Z_header['freq_ech']     = f"{X_header['freq_ech']}"
    Z_header['misval']       = f"{X_header['misval']}"
    Z_header['format']       = f"{X_header['format']}"


    msg_1 =  f"Moins : {Z_data.shape} ech."
    fct_ret = 0

    diag = {'CodeRet' : fct_ret,
            'DiagExec': f"{msg_1}"
           }

    return [Z_header], \
           [Z_data.astype(np.float32)  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Moins': {
        'Args': [
            {'Id': 'X'            , 'categorie': 'VECTOR_IN'               },
            {'Id': 'Y'            , 'categorie': 'VECTOR_IN'               },
            {'Id': 'Z'            , 'categorie': 'VECTOR_OUT'              },
        ],
    },
}


#==============================================================================
# Test de l'opérateur
#==============================================================================
if __name__ == '__main__':

    from fct_messages import wait_user

    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')


    # OPERATEUR SIMPLIFIÉ : sur de vrais vecteurs
    acqid = 'ju230150'
    logger.info(f'=== {acqid}')
    X             = AIDA.VectorMask(acqid, 'tpr_TB_BLB_MWRL1_SXb_%600')
    Y             = AIDA.VectorMask(acqid, 'tpr_brill_RTTOV_ground_Eti_%600')
    
    # appel de l'opérateur simplifié
    logger.info('*** opérateur simplifié : Moins')
    headers, datas, diag = Moins(X, Y)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in header.items():
            if key in ['bornes', 'obs_min', 'obs_max'] and len(value) > 60:
                logger.info(f"  - {key:15s} = {value[:60]}...")
            else:
                logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data[0:5] = {data[0:5]}")
        logger.info(f"data[-5:] = {data[-5:]}")
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
    input("...[ENTER] pour continuer ")
