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
def select_X_selon_Y(X_in,Y, crit_min, crit_max,Yinval,misval):
    """
    Filtre des valeurs de X selon des seuils sur Y1

    Input :
        X_in     : Paramètre à sélectionner 
        Y        : Paramètre selon lequel s'effectue la sélection
        crit_min : valeur minimale sur le critère Y
        crit_max : valeur maximale sur le critère Y
        Yinval   : valeur de Y qui permettra d’éliminer également des valeurs de X
        Inv_val  : valeur de remplacement de X lorsque Y ne correspond pas aux critères
        

    Output :
        X_filter  : X lorsque Y correspond aux critères

    Auteur : @Météo-France CNRM/GMEI/TRAMM - July 2023
    """
    logger.debug("select_X_selon_Y : debut")

    # récupération des arguments
    X_in_header = X_in.attributes
    X_in_data   = X_in.data.data

    Y_data   = Y.data.data

    # appel de la fonction de calcul
    X_filter,tab_stat = calcul.select_X_selon_Y.fct_select_X_selon_Y(X_in_data,Y_data, crit_min, crit_max,Yinval,misval)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_in_fr_name, X_in_en_name = X_in.get_names()
    Y_fr_name, Y_en_name = Y.get_names()

    X_filter_header                    = default_out_header.copy() 
    X_filter_header['name']         = f"la variable {X_in_fr_name} lorsque {Y_fr_name} est entre {crit_min} et {crit_max}"
    X_filter_header['english_name'] = f"the variable named {X_in_en_name} when {Y_en_name} is between {crit_min} et {crit_max}"
    if X_filter.ndim > 1:
        X_filter_header['bornes']         = f"{X_in_header['bornes']}"
        X_filter_header['unit_bornes']    = f"{X_in_header['unit_bornes']}"
    X_filter_header['unit']         = f"{X_in_header['unit']}"
    X_filter_header['freq_ech']     = f"{X_in_header['freq_ech']}"
    X_filter_header['ref_time']     = f"{X_in_header['ref_time']}"
    X_filter_header['misval']       = f"{misval}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"select_X_selon_Y : ({X_filter.shape} ech.), " +
                        f"{crit_min}<Y<{crit_max}," +
                        f"{tab_stat[0]} valeurs acceptée(s)" +
                        f"-et- {tab_stat[1] + tab_stat[2] + tab_stat[3] + tab_stat[5]} valeurs (sur {X_filter.shape}) rejetée(s)"+
                        f"[sup:{tab_stat[1]},inf : {tab_stat[2]}, mnq_Y : {tab_stat[3]}, nan_Y:{tab_stat[5]}]"
           }

    return [X_filter_header], [X_filter], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'select_X_selon_Y': {
        'Args': [
            {'Id': 'X_in'      , 'categorie': 'VECTOR_IN'},
            {'Id': 'Y'         , 'categorie': 'VECTOR_IN'},
            {'Id': 'crit_min'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'crit_max'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'Yinval'    , 'categorie': 'COEFFICIENT'},
            {'Id': 'misval'    , 'categorie': 'COEFFICIENT'},
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
    acqid = 'Ce210183'
    X_in        = AIDA.VectorMask(acqid, 'ven_w_gillv3_50m_coFrc200_2D_20')
    Y1          = AIDA.VectorMask(acqid, 'ctl_flag_combi_ven_w_gillv3_50m_Rot2D_20')
    crit_min_1 = -0.1
    crit_max_1 = 0.1
    Y_mnq = np.nan
    misval = np.nan

    # cas 2D
    acqid = 'Ce210183'
    X_in             = AIDA.VectorMask(acqid, 'ven_radial_ff_windcube0_Eti_%4')
    Y1               = AIDA.VectorMask(acqid, 'ctl_wip_windcube90_Eti_%4')
    crit_min_1 = -0.5
    crit_max_1 = 0.5

    # # cas 3D
    # acqid = 'pa230324'
    # X_in        = AIDA.VectorMask(acqid, 'tpr_TB_BLB_MWRL1_Eti_%600')
    # Y1          = AIDA.VectorMask(acqid, 'ctl_rainflag_BLB_MWRL1_Eti_%600')
    # crit_min_1 = -0.5
    # crit_max_1 = 0.5
    # Y_mnq = -99999
    # misval = np.nan

    # # création de Vector en mémoire
    # acqid = 'Ce210185'
    # logger.info(f'=== {acqid}')
    # header = dict()
    # header['name']         = 'pseudo variable pre_air_gillwp_stv4_sflg_20'
    # header['english_name'] = 'pseudo variable pre_air_gillwp_stv4_sflg_20'
    # header['format']       = 'Ieeefloat_32'
    # header['dimension']    = '4'
    # header['bornes']       = "(0,0);(1,1)"
    # header['unit_bornes']  = "m"
    # header['dim_array']    = '1'
    # header['ref_time']     = 'rft_time_PSEUDO_REG_20'
    # header['misval']       = 3.40282347e+38
    # header['freq_ech']     = 20
    # header['unit']         = 'hPa'
    # header['famille']      = 'pression'
    # header['origine']      = 'pseudo donnees de test'


    # X_in = AIDA.VectorMask(acqid, 'X_in', attributes=header, data=np.array([[1, np.nan], [3, 4],[5,6]],dtype = float))
    # Y1 = AIDA.VectorMask(acqid, 'Y1', attributes=header, data=np.array([[np.nan, -30], [-3, -40],[-5,-6]],dtype = float))
    # crit_min_1 = -23
    # crit_max_1 = 0
    # Y_mnq = -24
    # misval = np.nan


    # appel de l'opérateur
    headers, datas, diag = select_X_selon_Y(X_in, Y1, crit_min_1, crit_max_1,Y_mnq,misval)

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
