#!/usr/bin/env python3

"""
    ADC : Opérateur Module_2D_flt
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
def Module_2D_flt(C1, C2, nom_francais, eng_name):
    """
    Calcul du module (norme euclidienne) d'une quantité vectorielle à deux dimensions

    Input :
        C1          : Première composante du vecteur
        C2          : Deuxième composante du vecteur
        name        : Description du résultat
        eng_name    : Description du résultat en anglais
    Output :
        M  : Module du vecteur

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Juillet 2023
    """
    logger.debug("Module_2D_flt : debut")

    # récupération des arguments
    C1_header = C1.attributes
    C1_data   = C1.data.data

    C2_data   = C2.data.data

    # appel de la fonction de calcul
    M = calcul.Module_2D_flt.fct_Module_2D_flt(C1_data, C2_data)

    # préparation du retour

    M_header                 = default_out_header.copy() 
    M_header['name']         = f"{nom_francais}"
    M_header['english_name'] = f"{eng_name}"
    if M.ndim > 1 :
        M_header['bornes']         = f"{C1_header['bornes']}"
        M_header['unit_bornes']    = f"{C1_header['unit_bornes']}"
    M_header['unit']         = f"{C1_header['unit']}"
    M_header['freq_ech']     = f"{C1_header['freq_ech']}"
    M_header['ref_time']     = f"{C1_header['ref_time']}"
    M_header['misval']       = f"{C1_header['misval']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"Module_2D_fit : ({M.shape} ech.)"
           }

    return [M_header], [M], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Module_2D_flt': {
        'Args': [
            {'Id': 'C1'       , 'categorie': 'VECTOR_IN'},
            {'Id': 'C2'       , 'categorie': 'VECTOR_IN'},
            {'Id': 'name'     , 'categorie': 'COEFFICIENT'},
            {'Id': 'eng_name' , 'categorie': 'COEFFICIENT'},
            {'Id': 'M'        , 'categorie': 'VECTOR_OUT'},
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


    # OPERATEUR SIMPLIFIÉ : sur de vrais vecteurs
    acqid = 'Ce210182'
    logger.info(f'=== {acqid}')
    C1             = AIDA.VectorMask(acqid, 'ven_ff_X_windcube_WFR_%4')
    C2             = AIDA.VectorMask(acqid, 'ven_ff_Y_windcube_WFR_%4')
    french_name    = "Vitesse du vent"
    english_name   = "Wind speed"

    # appel de l'opérateur
    headers, datas, diag = Module_2D_flt(C1, C2, french_name, english_name)

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
