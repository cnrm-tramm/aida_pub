#!/usr/bin/env python3

"""
    ADC : Opérateur Select_X_selon_Y
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

import AIDA
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
def select_X_selon_bornes(X_in,crit_min, crit_max,axe):
    """
    Filtre des valeurs de X_in selon des seuils sur les bornes de X_in

    Input :
        X_in     : Paramètre à sélectionner 
        crit_min : valeur minimale 
        crit_max : valeur maximale
        axe : axe sur lequel s'effectue la sélection
        

    Output :
        X_filter  : X lorsque Y correspond aux critères

    Auteur : @Météo-France CNRM/GMEI/TRAMM - July 2023
    """
    logger.debug("select_X_selon_Y : debut")

    # récupération des arguments
    X_in_header = X_in.attributes
    X_in_data   = X_in.data.data
    X_str_bornes = X_in_header['bornes']
    range_gate   = AIDA.strBornes_to_array(X_str_bornes)[0]
    dim_array = AIDA.get_dim_array(X_in_header['dim_array'])

    # appel de la fonction de calcul
    X_filter,new_bornes, code_ret = calcul.select_X_selon_bornes.fct_select_X_selon_bornes(X_in_data,range_gate, crit_min, crit_max, axe,dim_array)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_in_fr_name, X_in_en_name = X_in.get_names()

    X_filter_header                    = default_out_header.copy() 
    X_filter_header['name']         = f"la variable {X_in_fr_name} lorsque ses bornes sont sur l'axe {axe} entre {crit_min} et {crit_max}"
    X_filter_header['english_name'] = f"the variable named {X_in_en_name} when its bounds over the axis {axe} are between {crit_min} et {crit_max}"
    if X_filter.ndim > 1:
        X_filter_header['bornes']         = f"{new_bornes}"
        X_filter_header['unit_bornes']    = f"{X_in_header['unit_bornes']}"
    X_filter_header['unit']         = f"{X_in_header['unit']}"
    X_filter_header['dim_array']         = f"{len(X_filter.shape)}"
    X_filter_header['freq_ech']     = f"{X_in_header['freq_ech']}"
    X_filter_header['ref_time']     = f"{X_in_header['ref_time']}"

    if code_ret == -1:
        diag = {'CodeRet' : -1,
            'DiagExec': "crit_min must be an int"}
    if code_ret == -2:
        diag = {'CodeRet' : -2,
            'DiagExec' : 'crit_max must be an int'}
    if code_ret == -3:
        diag = {'CodeRet' : -3,
            'DiagExec' : 'axe must be an int'}
    if code_ret == 0 :
        diag = {'CodeRet' : 0,
            'DiagExec': f"select_X_selon_bornes : ({X_filter.shape} ech.)"}

    return [X_filter_header], [X_filter], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'select_X_selon_bornes': {
        'Args': [
            {'Id': 'X_in'      , 'categorie': 'VECTOR_IN'},
            {'Id': 'crit_min'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_max'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'axe'       , 'categorie': 'COEFFICIENT'},
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

    # cas 2D
    acqid = 'CG230188'
    X_in             = AIDA.VectorMask(acqid, 'tpr_air_profiles_TPB_MWRL2_SXY_%1200')
    crit_min_1 = 0
    crit_max_1 = 2000
    axe = 1

    # cas 3D
    acqid = 'ju230150'
    X_in             = AIDA.VectorMask(acqid, 'tpr_TB_BLB_MWRL1_Eti_%1200')
    crit_min_1 = 5
    crit_max_1 = 40
    axe = 2


    # appel de l'opérateur
    headers, datas, diag = select_X_selon_bornes(X_in, crit_min_1, crit_max_1,axe)

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
