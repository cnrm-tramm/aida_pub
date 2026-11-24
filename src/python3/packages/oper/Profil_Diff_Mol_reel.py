#!/usr/bin/env python3

"""
    ADC : Opérateur Profil_Diff_Mol_reel
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
def Profil_Diff_Mol_reel(X, Zlid, z, Tz, Pz, lambda0):
    """
    Process Extinction and Backscatter coefficient for a standard molecular
    atmosphere.

    Input :
        X          : lidar signal  (1D)
        Zlid       : altitude of lidar gate
        z          : altitude of the T,P profile
        Tz         : profil de température
        Pz         : profil de pression
        lambda0    : wavelength

    Output :
        amol       : profil du coefficient d’extinction moléculaire (m −1 )
        bmol       : profil du coefficient de rétro-diffusion moléculaire (m −1 )
        trayleigh  : profil du coefficient de Rayleigh
        pr2_mol    : signal moléculaire rétro-diffusé (Photons.m 2 )

    Auteur : @Météo-France CNRM/GMEI/TRAMM - octo-2010
    """
    logger.debug("Profil_Diff_Mol_reel : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data # les data de X ne sont utilisées que pour DiagExec

    Zlid_header = Zlid.attributes
    Zlid_data   = Zlid.data.data

    z_header = z.attributes
    z_data   = z.data.data

    Tz_header = Tz.attributes
    Tz_data   = Tz.data.data

    Pz_header = Pz.attributes
    Pz_data   = Pz.data.data


    # préparation des arguments pour la fonction de calcul
    X_str_bornes = X_header['bornes']
    range_gate   = AIDA.strBornes_to_array(X_str_bornes)[0]

    # appel de la fonction de calcul
    amol_data, bmol_data, trayleigh_data, pr2_mol_data = \
        calcul.Profil_Diff_Mol_reel.Profil_Diff_Mol_reel(range_gate,
                                                         Zlid_data,
                                                         z_data,
                                                         Tz_data,
                                                         Pz_data,
                                                         lambda0)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    amol_header                      = default_out_header.copy()
    amol_header['name']              = "Coefficient d'extinction moleculaire"
    amol_header['english_name']      = "Molecular extinction coefficient"
    amol_header['unit']              = 'm-1'
    amol_header['freq_ech']          = f"{X_header['freq_ech']}"
    amol_header['ref_time']          = f"{X_header['ref_time']}"
    amol_header['misval']            = f"{X_header['misval']}"
    amol_header['famille']           = 'optique'

    bmol_header                      = default_out_header.copy()
    bmol_header['name']              = "Coefficient de retrodiffusion moleculaire"
    bmol_header['english_name']      = "Molecular backscatter coefficient"
    bmol_header['unit']              = 'm-1'
    bmol_header['freq_ech']          = f"{X_header['freq_ech']}"
    bmol_header['ref_time']          = f"{X_header['ref_time']}"
    bmol_header['misval']            = f"{X_header['misval']}"
    bmol_header['famille']           = 'optique'

    trayleigh_header                 = default_out_header.copy()
    trayleigh_header['name']         = "Coefficient de retrodiffusion moleculaire rayleigh"
    trayleigh_header['english_name'] = "Rayleigh molecular backscatter profile coefficient"
    trayleigh_header['unit']         = 'unitless'
    trayleigh_header['freq_ech']     = f"{X_header['freq_ech']}"
    trayleigh_header['ref_time']     = f"{X_header['ref_time']}"
    trayleigh_header['misval']       = f"{X_header['misval']}"
    trayleigh_header['famille']      = 'optique'

    pr2_mol_header                   = default_out_header.copy()
    pr2_mol_header['name']           = "Signal moleculaire retrodiffuse"
    pr2_mol_header['english_name']   = "Molecular backscatter signal"
    pr2_mol_header['freq_ech']       = f"{X_header['freq_ech']}"
    pr2_mol_header['ref_time']       = f"{X_header['ref_time']}"
    pr2_mol_header['misval']         = f"{X_header['misval']}"
    pr2_mol_header['famille']        = 'optique'


    diag = {'CodeRet' : 0,
            'DiagExec': f"Profil_Diff_Mol_reel : ({len(X_data)} ech.)"
           }

    return [amol_header, bmol_header, trayleigh_header, pr2_mol_header], \
           [amol_data  , bmol_data  , trayleigh_data  , pr2_mol_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Profil_Diff_Mol_reel': {
        'Args': [
            {'Id': 'X'        , 'categorie': 'VECTOR_IN'                 , 'famille': ['optique']    },
            {'Id': 'Zlid'     , 'categorie': 'VECTOR_IN'  , 'unit': 'm'  , 'famille': ['altitude']   },
            {'Id': 'z'        , 'categorie': 'VECTOR_IN'  , 'unit': 'm'  , 'famille': ['altitude']   },
            {'Id': 'Tz'       , 'categorie': 'VECTOR_IN'  , 'unit': 'K'  , 'famille': ['temperature']},
            {'Id': 'Pz'       , 'categorie': 'VECTOR_IN'  , 'unit': 'hPa', 'famille': ['pression']   },
            {'Id': 'lambda0'  , 'categorie': 'COEFFICIENT'                                           },
            {'Id': 'amol'     , 'categorie': 'VECTOR_OUT'                                            },
            {'Id': 'bmol'     , 'categorie': 'VECTOR_OUT'                                            },
            {'Id': 'trayleigh', 'categorie': 'VECTOR_OUT'                                            },
            {'Id': 'pr2_mol'  , 'categorie': 'VECTOR_OUT'                                            },
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


    # Profil_Diff_Mol_reel (
    #   opt_dclid_raw_%60,
    #   $Arg1.bornes,
    #   alt_gate_lid_%60,
    #   $Arg1.array_dim,
    #   alt_profil_modele_Eti_%60,
    #   tpr_profil_modele_Eti_%60,
    #   pre_profil_modele_Eti_%60,
    #   $Arg5.array_dim,
    #   532,
    #   opt_amol_mod_%60, opt_bmol_mod_%60, opt_trayleygh_mod_%60, opt_pr2_mol_mod_%60 )


    # sur de vrais vecteurs
    acqid = 'PM200274'
    logger.info(f'=== {acqid}')
    X          = AIDA.VectorMask(acqid, 'opt_dclid_raw_%60')
    Zlib       = AIDA.VectorMask(acqid, 'alt_gate_lid_%60')
    z          = AIDA.VectorMask(acqid, 'alt_profil_modele_Eti_%60')
    Tz         = AIDA.VectorMask(acqid, 'tpr_profil_modele_Eti_%60')
    Pz         = AIDA.VectorMask(acqid, 'pre_profil_modele_Eti_%60')
    lambda0    = 532

    # appel de l'opérateur
    logger.info('*** appel de Profil_Diff_Mol_reel')
    headers, datas, diag = Profil_Diff_Mol_reel (X, Zlib, z, Tz, Pz, lambda0)

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
