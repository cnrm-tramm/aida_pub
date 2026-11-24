#!/usr/bin/env python3

"""
    ADC : Opérateur Select_X_selon_Y1Y2Y3Y4
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
def Select_X_selon_Y1Y2Y3Y4(X_in, 
                            Y1, Y2, Y3, Y4, 
                            crit_min_1, crit_max_1, crit_min_2, crit_max_2, crit_min_3, crit_max_3, crit_min_4, crit_max_4):
    """
    Filtre des valeurs de X selon des seuils sur Y1, Y2, Y3 et Y4.
    On suppose que les bases de temps de X_in, Y1, Y2, Y3, Y4 sont identiques
    
    Input :
        X_in : Données d'entrée 
        Y1 : Vecteur de critère de sélection 1
        Y2 : Vecteur de critère de sélection 2
        Y3 : Vecteur de critère de sélection 3
        Y4 : Vecteur de critère de sélection 4
        crit_min_1 : valeur minimale sur le critère 1
        crit_max_1 : valeur maximale sur le critère 1
        crit_min_2 : valeur minimale sur le critère 2
        crit_max_2 : valeur maximale sur le critère 2
        crit_min_3 : valeur minimale sur le critère 3
        crit_max_3 : valeur maximale sur le critère 3
        crit_min_4 : valeur minimale sur le critère 4
        crit_max_4 : valeur maximale sur le critère 4
        

    Output :
        X_out  : Données d'entrées filtrées selon les 4 critères
        

    Auteur : @Météo-France CNRM/GMEI/TRAMM - July 2023
    """
    logger.debug("Select_X_selon_Y1Y2Y3Y4 : debut")

    # récupération des arguments
    X_in_header = X_in.attributes
    X_in_data   = X_in.data.data

    Y1_data   = Y1.data.data
    Y2_data   = Y2.data.data
    Y3_data   = Y3.data.data
    Y4_data   = Y4.data.data

    # appel de la fonction de calcul
    X_filter,code_ret,tab_stat = calcul.Select_X_selon_Y1Y2Y3Y4.fct_Select_X_selon_Y1Y2Y3Y4(X_in_data, 
                                                                                   Y1_data, Y2_data, Y3_data, Y4_data, 
                                                                                   crit_min_1, crit_max_1, crit_min_2, crit_max_2, 
                                                                                   crit_min_3, crit_max_3, crit_min_4, crit_max_4)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_in_fr_name, X_in_en_name = X_in.get_names()
    Y1_fr_name, Y1_en_name = Y1.get_names()
    Y2_fr_name, Y2_en_name = Y2.get_names()
    Y3_fr_name, Y3_en_name = Y3.get_names()
    Y4_fr_name, Y4_en_name = Y4.get_names()

    X_filter_header                    = default_out_header.copy() 
    X_filter_header['name']         = f"Variable {X_in_fr_name} filtree en fonction des critères fixés sur '{Y1_fr_name}','{Y2_fr_name}','{Y3_fr_name}','{Y4_fr_name}'"
    X_filter_header['english_name'] = f"Variable {X_in_en_name} filtered according the criteria set on '{Y1_en_name}','{Y2_en_name}','{Y3_en_name}','{Y4_en_name}'"
    if X_filter.ndim > 1:
        X_filter_header['bornes']         = f"{X_in_header['bornes']}"
        X_filter_header['unit_bornes']    = f"{X_in_header['unit_bornes']}"
    X_filter_header['unit']         = f"{X_in_header['unit']}"
    X_filter_header['freq_ech']     = f"{X_in_header['freq_ech']}"
    X_filter_header['ref_time']     = f"{X_in_header['ref_time']}"
    X_filter_header['misval']       = f"{X_in_header['misval']}"

    msg_1 = f"Select_X_selon_Y1Y2Y3Y4 : ({X_filter.shape} ech.), " +\
                        f"Nb donnees OK: {tab_stat[0]}; " +\
                        f"Nb donees non OK filtrees : {tab_stat[1]}"
    if code_ret == 0 :
        msg_2 = "OK"
    elif code_ret == -1 :
        msg_2 = " ERREUR : X, Y1, Y2, Y3 and Y4 do not have the same shape."


    diag = {'CodeRet' : code_ret,
            'DiagExec': f"{msg_1}.{msg_2}"
           }
    
    return [X_filter_header], [X_filter], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Select_X_selon_Y1Y2Y3Y4': {
        'Args': [
            {'Id': 'X_in'      , 'categorie': 'VECTOR_IN'},
            {'Id': 'Y1'        , 'categorie': 'VECTOR_IN'},
            {'Id': 'Y2'        , 'categorie': 'VECTOR_IN'},
            {'Id': 'Y3'        , 'categorie': 'VECTOR_IN'},
            {'Id': 'Y4'        , 'categorie': 'VECTOR_IN'},
            {'Id': 'crit_min_1', 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_max_1', 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_min_2', 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_max_2', 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_min_3', 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_max_3', 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_min_4', 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_max_4', 'categorie': 'COEFFICIENT'},
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


    # création de Vector en mémoire
    acqid = 'Ce210182'
    X_in             = AIDA.VectorMask(acqid, 'ven_ff_X_windcube0_Eti_%4')
    Y1               = AIDA.VectorMask(acqid, 'ray_cnr_windcube0_Eti_%4')
    Y2               = AIDA.VectorMask(acqid, 'ray_cnr_windcube90_Eti_%4')
    Y3               = AIDA.VectorMask(acqid, 'ray_cnr_windcube180_Eti_%4')
    Y4               = AIDA.VectorMask(acqid, 'ray_cnr_windcube270_Eti_%4')
    crit_min_1 = -23
    crit_max_1 = 100
    crit_min_2 = -23
    crit_max_2 = 100
    crit_min_3 = -23
    crit_max_3 = 100
    crit_min_4 = -23
    crit_max_4 = 100

    # appel de l'opérateur
    headers, datas, diag = Select_X_selon_Y1Y2Y3Y4(X_in, Y1, Y2, Y3, Y4, 
                                                   crit_min_1, crit_max_1,crit_min_2,crit_max_2,crit_min_3,crit_max_3,crit_min_4,crit_max_4)

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
