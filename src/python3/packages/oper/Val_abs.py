#!/usr/bin/env python3

"""
    ADC : Opérateur Val_abs
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
def Val_abs(X_in):
    """
    Applique la valeur absolue

    Input :
        X_in     : Paramètre d'entrée 

    Output :
        X_out  : Paramètre d'entrée en valeur absolue
        
    Auteur :  CNRM/GMEI/TRAMM Mai 2024
    """
    logger.debug("Val_abs : debut")

    # récupération des arguments
    X_in_header = X_in.attributes
    X_in_data   = X_in.data.data

    # appel de la fonction de calcul
    X_filter = calcul.Val_abs.fct_Val_abs(X_in_data)


    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_in_fr_name, X_in_en_name = X_in.get_names()

    X_filter_header                    = default_out_header.copy() 
    X_filter_header['name']         = f"valeur absolue de {X_in_fr_name}"
    X_filter_header['english_name'] = f"absolute value of {X_in_en_name}"
    if X_filter.ndim > 1:
        X_filter_header['bornes']         = f"{X_in_header['bornes']}"
        X_filter_header['unit_bornes']    = f"{X_in_header['unit_bornes']}"
    X_filter_header['unit']         = f"{X_in_header['unit']}"
    X_filter_header['freq_ech']     = f"{X_in_header['freq_ech']}"
    X_filter_header['ref_time']     = f"{X_in_header['ref_time']}"

    msg_1 = f"select_data : ({X_filter.shape} ech.)"
    fct_ret = 0
    
    diag = {'CodeRet' : fct_ret,
        'DiagExec': f"{msg_1}"
        }

    return [X_filter_header], [X_filter], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Val_abs': {
        'Args': [
            {'Id': 'X_in'      , 'categorie': 'VECTOR_IN'},
            {'Id': 'X_out'     , 'categorie': 'VECTOR_OUT'},
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


    # cas 1D
    acqid = 'Tf240016'
    X_in        = AIDA.VectorMask(acqid, 'alt_hbn1_dso_cl31_Eti_%60')


    # cas 3D
    acqid = 'ju230150'
    X_in        = AIDA.VectorMask(acqid, 'lwc_cloud_water_profil_arome_seld_%3600')

    # appel de l'opérateur
    headers, datas, diag = Val_abs(X_in)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in { k:header[k] for k in sorted(header) }.items():
            logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data   = {data}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
