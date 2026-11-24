#!/usr/bin/env python3

"""
    ADC : Opérateur WFR
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
def WFR(X1, X2, angle):
    """
    Calcul du champ de vent WFR (Wind Field Reconstruction) à partir des composantes radiales

    Input :
        X1     : Vecteur 1 de vitesse de vent
        X2     : Vecteur 2 de vitesse de vent
        angle  : Angle entre la verticale et l'impulsion lumineuse

    Output :
        X_out  : Vent WFR reconstitué

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Juillet 2023
    """
    logger.debug("WFR : debut")

    # récupération des arguments
    X1_header = X1.attributes
    X1_data   = X1.data.data

    X2_data   = X2.data.data

    # appel de la fonction de calcul
    X_data = calcul.WFR.fct_WFR(X1_data, X2_data, angle)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X1_fr_name, X1_en_name = X1.get_names()
    X2_fr_name, X2_en_name = X2.get_names()

    X_header                 = default_out_header.copy() 
    X_header['name']         = f"Champ de vent calculé à partir de '{X1_fr_name}' et '{X2_fr_name}'"
    X_header['english_name'] = f"Wind field computed with '{X1_en_name}' et '{X2_en_name}'"
    if X_data.ndim > 1 :
        X_header['bornes']         = f"{X1_header['bornes']}"
        X_header['unit_bornes']    = f"{X1_header['unit_bornes']}"
    X_header['unit']         = f"{X1_header['unit']}"
    X_header['freq_ech']     = f"{X1_header['freq_ech']}"
    X_header['ref_time']     = f"{X1_header['ref_time']}"
    X_header['misval']       = f"{X1_header['misval']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"WFR : ({X_data.shape} ech.)"
           }

    return [X_header], [X_data], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'WFR': {
        'Args': [
            {'Id': 'X1'       , 'categorie': 'VECTOR_IN'},
            {'Id': 'X2'       , 'categorie': 'VECTOR_IN'},
            {'Id': 'angle'    , 'categorie': 'COEFFICIENT'},
            {'Id': 'X_out'    , 'categorie': 'VECTOR_OUT'},
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


    # création de Vector en mémoire
    acqid = 'Ce210182'
    X_in_1              = AIDA.VectorMask(acqid, 'ven_ff_windcube0_Eti_%4')
    X_in_2              = AIDA.VectorMask(acqid, 'ven_ff_windcube180_Eti_%4')
    angle = 28

    # appel de l'opérateur
    headers, datas, diag = WFR(X_in_1, X_in_2, angle)

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
