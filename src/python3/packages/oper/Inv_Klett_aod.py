#!/usr/bin/env python3

"""
    ADC : Opérateur Inv_Klett_aod
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
def Inv_Klett_aod(X, Z, beta_mol, flg_cloud, AOD_photo, alt_max,
                  dist_min, beta_a_init, extrap_typ):
    """
    Klett Inversion Constrained by AOD.

    Input :
        X           : backscatter lidar signal
        Z           : altitude of lidar measurements
        beta_mol    : molecular diffusion
        flg_cld     : cloud flag (0 : no flag, !=0 : altitude of cloud )
        AOD_photo   : Aerosol optical depth
        alt_max     : max ref altitude
        dist_min    : minimal distance from lidar of signal use
        beta_a_init : valeur initiale de Beta
        sa          : value of Sa
        extrap_typ  : type extrapolation proche du lidar 'cst' or 'lin'

    Output :
        Sigma       : aerosol extinction coefficient (profil 1D) 
        Beta        : aerosol backscatterring coefficient (profil 1D)
        SA          : lidar ratio

    Auteur : @Météo-France CNRM/GMEI/TRAMM - juil 2019
             transcodage Python a partir de la filiere BASIC du LOA en Scilab
             fonction scilab originale : Inv_Klett_aod.sci
    """
    logger.debug("Inv_Klett_aod : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    Z_header = Z.attributes
    Z_data   = Z.data.data

    beta_mol_header = beta_mol.attributes
    beta_mol_data   = beta_mol.data.data

    flg_cloud_header = flg_cloud.attributes
    flg_cloud_data   = flg_cloud.data.data

    AOD_photo_header = AOD_photo.attributes
    AOD_photo_data   = AOD_photo.data.data

    alt_max_header = alt_max.attributes
    alt_max_data   = alt_max.data.data


    # préparation des arguments pour la fonction de calcul
    X_str_bornes = X_header['bornes']
    range_gate   = AIDA.strBornes_to_array(X_str_bornes)[0]

    # appel de la fonction de calcul
    Sigma_data, Beta_data, SA_data = \
        calcul.Inv_Klett_aod.Inv_Klett_aod(X_data, range_gate,
                                           Z_data,
                                           beta_mol_data,
                                           flg_cloud_data,
                                           AOD_photo_data,
                                           alt_max_data,
                                           dist_min, beta_a_init,
                                           extrap_typ)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    Sigma_header                 = default_out_header.copy()
    Sigma_header['name']         = "Coefficient d'extinction des aerosols"
    Sigma_header['english_name'] = "Aerosol extinction coefficient"
    Sigma_header['unit']         = 'm-1'
    Sigma_header['freq_ech']     = f"{X_header['freq_ech']}"
    Sigma_header['ref_time']     = f"{X_header['ref_time']}"
    Sigma_header['misval']       = f"{X_header['misval']}"
    Sigma_header['famille']      = 'optique'
    Sigma_header['bornes']       = f"{X_header['bornes']}"
    Sigma_header['unit_bornes']  = f"{X_header['unit_bornes']}"

    Beta_header                 = default_out_header.copy()
    Beta_header['name']         = 'Coefficient de retrodiffusion des aerosols'
    Beta_header['english_name'] = 'Aerosol backscatter coefficient'
    Beta_header['unit']         = 'm-1'
    Beta_header['freq_ech']     = f"{X_header['freq_ech']}"
    Beta_header['ref_time']     = f"{X_header['ref_time']}"
    Beta_header['misval']       = f"{X_header['misval']}"
    Beta_header['famille']      = 'optique'
    Beta_header['bornes']       = f"{X_header['bornes']}"
    Beta_header['unit_bornes']  = f"{X_header['unit_bornes']}"

    SA_header                   = default_out_header.copy()
    SA_header['name']           = 'Rapport lidar'
    SA_header['english_name']   = 'Lidar ratio'
    SA_header['dim_array']      = '1'
    SA_header['unit']           = 'unitless'
    SA_header['freq_ech']       = f"{X_header['freq_ech']}"
    SA_header['ref_time']       = f"{X_header['ref_time']}"
    SA_header['misval']         = f"{X_header['misval']}"
    SA_header['famille']        = 'optique'

    diag = {'CodeRet' : 0,
            'DiagExec': f"Inv_Klett_aod : ({len(X_data)} ech.)"
           }


    return [Sigma_header, Beta_header, SA_header], \
           [Sigma_data  , Beta_data  , SA_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Inv_Klett_aod': {
        'Args': [
            {'Id': 'X'          , 'categorie': 'VECTOR_IN'               , 'famille': ['optique'] },
            {'Id': 'Z'          , 'categorie': 'VECTOR_IN'  , 'unit': 'm', 'famille': ['altitude']},
            {'Id': 'beta_mol'   , 'categorie': 'VECTOR_IN'               , 'famille': ['optique'] },
            {'Id': 'flg_cloud'  , 'categorie': 'VECTOR_IN'                                        },
            {'Id': 'AOD_photo'  , 'categorie': 'VECTOR_IN'               , 'famille': ['optique'] },
            {'Id': 'alt_max'    , 'categorie': 'VECTOR_IN'  , 'unit': 'm', 'famille': ['altitude']},
            {'Id': 'dist_min'   , 'categorie': 'COEFFICIENT'                                      },
            {'Id': 'beta_a_init', 'categorie': 'COEFFICIENT'                                      },
            {'Id': 'extrap_typ' , 'categorie': 'COEFFICIENT'                                      },
            {'Id': 'Sigma'      , 'categorie': 'VECTOR_OUT'                                       },
            {'Id': 'Beta'       , 'categorie': 'VECTOR_OUT'                                       },
            {'Id': 'SA'         , 'categorie': 'VECTOR_OUT'                                       },
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


    # Inv_Klett_aod (
    #   opt_pr2_lid_filtre_%60,
    #   $Arg1.array_dim,
    #   $Arg1.bornes,
    #   alt_gate_lid_%60,
    #   opt_bmol_mod_%60,
    #   alt_nuage1_base_%60,
    #   opt_aod532_plasma_Met_%60,
    #   alt_zref_lid_%60,
    #   700,
    #   5.e-8,
    #   "cst",
    #   opt_sigma_lid_kaod_mod_%60,
    #   opt_beta_lid_kaod_mod_%60,
    #   opt_sa_lid_kaod_mod_%60)


    # sur de vrais vecteurs
    acqid = 'PM200274'
    logger.info(f'=== {acqid}')
    X           = AIDA.VectorMask(acqid, 'opt_pr2_lid_filtre_%60')
    Z           = AIDA.VectorMask(acqid, 'alt_gate_lid_%60')
    beta_mol    = AIDA.VectorMask(acqid, 'opt_bmol_mod_%60')
    flg_cloud   = AIDA.VectorMask(acqid, 'alt_nuage1_base_%60')
    AOD_photo   = AIDA.VectorMask(acqid, 'opt_aod532_plasma_Met_%60')
    alt_max     = AIDA.VectorMask(acqid, 'alt_zref_lid_%60')
    dist_min    = 700
    beta_a_init = 5.e-8
    extrap_typ  = 'cst'

    # appel de l'opérateur
    logger.info('*** appel de Inv_Klett_aod')
    headers, datas, diag = Inv_Klett_aod(X, Z, beta_mol, flg_cloud, AOD_photo,
                                         alt_max, dist_min, beta_a_init,
                                         extrap_typ)

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
