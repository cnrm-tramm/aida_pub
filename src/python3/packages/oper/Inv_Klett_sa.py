#!/usr/bin/env python3

"""
    ADC : Opérateur Inv_Klett_sa
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
def Inv_Klett_sa(X, Z, beta_mol, flg_cloud, alt_max,
                 dist_min, beta_a_init, Sa, extrap_typ):
    """
    Klett Inversion Constrained by SA.

    Input :
        X           : backscatter lidar signal
        Z           : altitude of lidar measurements
        beta_mol    : molecular diffusion
        flg_cld     : cloud flag (0 : no flag, !=0 : altitude of cloud )
        alt_max     : max ref altitude
        dist_min    : minimal distance of the lidar to take in account
        beta_a_init : valeur initiale de Beta
        Sa          : value of Sa
        extrap_typ  : type extrapolation proche du lidar 'cst' or 'lin'

    Output :
        Beta        : aerosol backscatterring coefficient (profil 1D)
        aod         : aerosol optical depth

    Auteur : @Météo-France CNRM/GMEI/TRAMM - febr 2018
             transcodage de scilab en Python a partir de la filiere BASIC du
             LOA fonction scilab originale : Inv_Klett_sa.sci
    """
    logger.debug("Inv_Klett_sa : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    Z_header = Z.attributes
    Z_data   = Z.data.data

    beta_mol_header = beta_mol.attributes
    beta_mol_data   = beta_mol.data.data

    flg_cloud_header = flg_cloud.attributes
    flg_cloud_data   = flg_cloud.data.data

    alt_max_header = alt_max.attributes
    alt_max_data   = alt_max.data.data


    # préparation des arguments pour la fonction de calcul
    X_str_bornes = X_header['bornes']
    range_gate   = AIDA.strBornes_to_array(X_str_bornes)[0]

    # appel de la fonction de calcul
    Beta_data, aod_data = \
        calcul.Inv_Klett_sa.Inv_Klett_sa(X_data, range_gate,
                                         Z_data,
                                         beta_mol_data,
                                         flg_cloud_data,
                                         alt_max_data,
                                         dist_min, beta_a_init, Sa, extrap_typ)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

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

    aod_header                  = default_out_header.copy()
    aod_header['name']          = 'Epaisseur optique des Aerosols'
    aod_header['english_name']  = 'Aerosol optical depth'
    aod_header['unit']          = 'unitless'
    aod_header['freq_ech']      = f"{X_header['freq_ech']}"
    aod_header['ref_time']      = f"{X_header['ref_time']}"
    aod_header['misval']        = f"{X_header['misval']}"
    aod_header['famille']       = 'optique'
    aod_header['dim_array']     = '1'

    diag = {'CodeRet' : 0,
            'DiagExec': f"Inv_Klett_sa : ({len(X_data)} ech.)"
           }


    return [Beta_header, aod_header], \
           [Beta_data  , aod_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Inv_Klett_sa': {
        'Args': [
            {'Id': 'X'          , 'categorie': 'VECTOR_IN'               , 'famille': ['optique'] },
            {'Id': 'Z'          , 'categorie': 'VECTOR_IN'               , 'famille': ['altitude']},
            {'Id': 'beta_mol'   , 'categorie': 'VECTOR_IN'               , 'famille': ['optique'] },
            {'Id': 'flg_cloud'  , 'categorie': 'VECTOR_IN'                                        },
            {'Id': 'alt_max'    , 'categorie': 'VECTOR_IN'  , 'unit': 'm', 'famille': ['altitude']},
            {'Id': 'dist_min'   , 'categorie': 'COEFFICIENT'                                      },
            {'Id': 'beta_a_init', 'categorie': 'COEFFICIENT'                                      },
            {'Id': 'Sa'         , 'categorie': 'COEFFICIENT'                                      },
            {'Id': 'extrap_typ' , 'categorie': 'COEFFICIENT'                                      },
            {'Id': 'Beta'       , 'categorie': 'VECTOR_OUT'                                       },
            {'Id': 'aod'        , 'categorie': 'VECTOR_OUT'                                       },
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


    # Inv_Klett_sa (
    #   opt_pr2_lid_filtre_%300,
    #   $Arg1.array_dim,
    #   $Arg1.bornes,
    #   alt_gate_lid_%300,
    #   opt_bmol_%300,
    #   alt_nuage1_base_%300,
    #   alt_zref_lid_%300,
    #   300,
    #   5.e-8,
    #   50.,
    #   "cst",
    #   opt_blid_%300,
    #   opt_aod_lid_%300)

    # sur de vrais vecteurs
    acqid = 'PM200274'
    logger.info(f'=== {acqid}')
    X           = AIDA.VectorMask(acqid, 'opt_pr2_lid_filtre_%300')
    Z           = AIDA.VectorMask(acqid, 'alt_gate_lid_%300')
    beta_mol    = AIDA.VectorMask(acqid, 'opt_bmol_%300')
    flg_cloud   = AIDA.VectorMask(acqid, 'alt_nuage1_base_%300')
    alt_max     = AIDA.VectorMask(acqid, 'alt_zref_lid_%300')
    dist_min    = 300
    beta_a_init = 5.e-8
    Sa          = 50.
    extrap_typ  = 'cst'

    # appel de l'opérateur
    logger.info('*** appel de Inv_Klett_sa')
    headers, datas, diag = Inv_Klett_sa(X, Z, beta_mol, flg_cloud, alt_max,
                                        dist_min, beta_a_init, Sa, extrap_typ)

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
