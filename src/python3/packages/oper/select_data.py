#!/usr/bin/env python3

"""
    ADC : Opérateur Select_data
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
def select_data(X_in,crit1_min,crit1_max,crit2_min,crit2_max,val):
    """
    Filtre des valeurs de X selon des seuils crit1_min, crit2_min, crit1_max, crit2_max

    Input :
        X_in     : Paramètre à sélectionner 
        crit1_min : valeur minimale pour le 1e critère
        crit1_max : valeur maximale pour le 1e critère
        crit2_min : valeur minimale pour le 2e critère
        crit2_max : valeur maximale pour le 2e critère
        val : valeur à remplacer

    Output :
        X_out  : X filtré
        
    Auteur :  CNRM/GMEI/TRAMM Mai 2024
    """
    logger.debug("select_data : debut")

    # récupération des arguments
    X_in_header = X_in.attributes
    X_in_data   = X_in.data.data

    # appel de la fonction de calcul
    try :
        crit2_min = float(crit2_min)
        crit2_max = float(crit2_max)
        X_filter,fct_ret,tab_stat = calcul.select_data.fct_select_data(X_in_data,crit1_min,crit1_max,val,crit2_min,crit2_max)
    except ValueError:
        X_filter,fct_ret,tab_stat = calcul.select_data.fct_select_data(X_in_data,crit1_min,crit1_max,val)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_in_fr_name, X_in_en_name = X_in.get_names()

    X_filter_header                    = default_out_header.copy() 
    X_filter_header['name']         = f"la variable {X_in_fr_name} est entre {crit1_min} et {crit1_max}"
    X_filter_header['english_name'] = f"the variable named {X_in_en_name} is between {crit1_min} et {crit1_max}"
    if X_filter.ndim > 1:
        X_filter_header['bornes']         = f"{X_in_header['bornes']}"
        X_filter_header['unit_bornes']    = f"{X_in_header['unit_bornes']}"
    X_filter_header['unit']         = f"{X_in_header['unit']}"
    X_filter_header['freq_ech']     = f"{X_in_header['freq_ech']}"
    X_filter_header['ref_time']     = f"{X_in_header['ref_time']}"

    if fct_ret == -1:
        msg_1 =  f"crit1_min must be inferior to crit1_max" 

    elif fct_ret == -2:
        msg_1 =  f"crit2_min must be inferior to crit2_max" 

    else:
        msg_1 = f"select_data : ({X_filter.shape} ech.), " +\
                f"et {tab_stat[0]+tab_stat[1]+tab_stat[2]+tab_stat[3]} valeurs (sur {X_filter.shape}) rejetée(s)"
        fct_ret = 0 
    
    diag = {'CodeRet' : fct_ret,
        'DiagExec': f"{msg_1}"
        }

    return [X_filter_header], [X_filter], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'select_data': {
        'Args': [
            {'Id': 'X_in'      , 'categorie': 'VECTOR_IN'},
            {'Id': 'crit1_min'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'crit1_max'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'crit2_min'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'crit2_max'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'val'    , 'categorie': 'COEFFICIENT'},
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
    crit1_min = 0
    crit1_max = 7799
    crit2_min = 0
    crit2_max = 7799
    val = np.nan

    # # cas 2D
    # acqid = 'Ce210183'
    # X_in             = AIDA.VectorMask(acqid, 'ven_radial_ff_windcube0_Eti_%4')
    # Y1               = AIDA.VectorMask(acqid, 'ctl_wip_windcube90_Eti_%4')
    # crit_min_1 = -0.5
    # crit_max_1 = 0.5

    # cas 3D
    acqid = 'ju230150'
    X_in        = AIDA.VectorMask(acqid, 'lwc_cloud_water_profil_arome_Eti_%3600')
    crit1_min = +0
    crit1_max = 999999
    crit2_min = '0./0.'
    crit2_max = '0./0.'
    val = 0

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
    headers, datas, diag = select_data(X_in,crit1_min,crit1_max,crit2_min,crit2_max,val)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in { k:header[k] for k in sorted(header) }.items():
            logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data   = {data[0]}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
