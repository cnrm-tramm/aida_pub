#!/usr/bin/env python3

"""
    ADC : Opérateur Hauteur_CL_Lidar
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
def Hauteur_CL_Lidar(pr2, base_cld, width_wave,thr_cloud,zmin_bl,zmax_bl,zmax_tl):
    """
    Process Extinction and Backscatter coefficient for a standard molecular
    atmosphere.

    Input :

    Output :

    Auteur : @Météo-France CNRM/GMEI/TRAMM - febr-2018
             transcode de scilab en Python a partir de la filiere BASIC du LOA 
             fonction scilab originale : Std_Atm.sci
    """
    logger.debug("Hauteur_CL_Lidar : debut")

    # récupération des arguments
    X_header = pr2.attributes
    PR2_data   = pr2.data.data # les data de X ne sont utilisées que pour DiagExec

    base_cld_data   = base_cld.data.data


    # préparation des arguments pour la fonction de calcul
    X_str_bornes = X_header['bornes']
    range_gate   = AIDA.strBornes_to_array(X_str_bornes)[0]

    # appel de la fonction de calcul
    z_bl_data, z_tl_data = calcul.Hauteur_CL_Lidar.Hauteur_CL_Lidar(PR2_data, range_gate, 
                                                                    base_cld_data, width_wave,
                                                                    thr_cloud,zmin_bl,
                                                                    zmax_bl,zmax_tl)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    z_bl_header                      = default_out_header.copy()
    z_bl_header['name']              = "Hauteur de couche limite atmosphérique"
    z_bl_header['english_name']      = "Boundary layer height"
    z_bl_header['unit']              = 'm'
    z_bl_header['freq_ech']          = f"{X_header['freq_ech']}"
    z_bl_header['ref_time']          = f"{X_header['ref_time']}"
    z_bl_header['misval']            = f"{X_header['misval']}"

    z_tl_header                      = default_out_header.copy()
    z_tl_header['name']              = "Coefficient de retrodiffusion moleculaire"
    z_tl_header['english_name']      = "Top layer height"
    z_tl_header['unit']              = 'm'
    z_tl_header['freq_ech']          = f"{X_header['freq_ech']}"
    z_tl_header['ref_time']          = f"{X_header['ref_time']}"
    z_tl_header['misval']            = f"{X_header['misval']}"


    diag = {'CodeRet' : 0,
            'DiagExec': f"Hauteur_CL_Lidar : ({len(z_bl_data)} ech.)"
           }

    return [z_bl_header, z_tl_header], \
           [z_bl_data  , z_tl_data], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Hauteur_CL_Lidar': {
        'Args': [
            {'Id': 'pr2'        , 'categorie': 'VECTOR_IN'},
            {'Id': 'base_cld'   , 'categorie': 'VECTOR_IN'},
            {'Id': 'width_wave' , 'categorie': 'COEFFICIENT'},
            {'Id': 'thr_cloud'  , 'categorie': 'COEFFICIENT'},
            {'Id': 'zmin_bl'    , 'categorie': 'COEFFICIENT'},
            {'Id': 'zmax_bl'    , 'categorie': 'COEFFICIENT'},
            {'Id': 'zmax_tl'    , 'categorie': 'COEFFICIENT'},
            {'Id': 'z_bl'       , 'categorie': 'VECTOR_OUT'},
            {'Id': 'z_tl'       , 'categorie': 'VECTOR_OUT'},
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

    # sur de vrais vecteurs
    acqid = 'Tf240053'
    logger.info(f'=== {acqid}')
    pr2               = AIDA.VectorMask(acqid, 'opt_rcs_cl31_Eti_%30')
    base_cld          = AIDA.VectorMask(acqid, 'alt_cbh_cl31_Eti_%30')
    width_wave        = 210
    thr_cloud         = -10
    zmin_bl           = 100
    zmax_bl           = 3000
    zmax_tl           = 7000

    # appel de l'opérateur
    logger.info('*** appel de Hauteur_CL_Lidar')
    headers, datas, diag = Hauteur_CL_Lidar(pr2, base_cld, width_wave,thr_cloud,zmin_bl,zmax_bl,zmax_tl)

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
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
