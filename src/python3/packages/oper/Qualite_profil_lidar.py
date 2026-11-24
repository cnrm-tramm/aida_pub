#!/usr/bin/env python3

"""
    ADC : Opérateur Qualite_profil_lidar
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
def Qualite_profil_lidar(pr2, pr2_mol, z, zref):
    """
    Check quality of rcs slope % molecular slope around reference altitude.

    Input :
        pr2       : the Pr2 signal from the LIDAR remote sensing
        pr2_mol   : the Pr2 signal from the molecular model
        z         : altitude above the ground level (in meters)
        zref      : reference altitude for molecular signal 

    Output :
        qualindex : quality index for each profiles

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Febr 2018

    sources :
    transcodage d'un script scilab ecrit par le LOA.
    """
    logger.debug("Qualite_profil_lidar : debut")

    # récupération des arguments
    pr2_header     = pr2.attributes
    pr2_data       = pr2.data.data

    pr2_mol_header = pr2_mol.attributes
    pr2_mol_data   = pr2_mol.data.data

    z_header       = z.attributes
    z_data         = z.data.data

    zref_header    = zref.attributes
    zref_data      = zref.data.data


    # préparation des arguments pour la fonction de calcul

    # appel de la fonction de calcul
    qualindex_data = \
        calcul.Qualite_profil_lidar.Qualite_profil_lidar(pr2_data,
                                                         pr2_mol_data,
                                                         z_data,
                                                         zref_data)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    qualindex_header = default_out_header.copy()
    qualindex_header['name']         = 'Qualite du signal lidar'
    qualindex_header['english_name'] = 'Quality of lidar signal'
    qualindex_header['unit']         = 'unitless'
    qualindex_header['freq_ech']     = f"{pr2_header['freq_ech']}"
    qualindex_header['ref_time']     = f"{pr2_header['ref_time']}"
    qualindex_header['misval']       = f"{pr2_header['misval']}"
    qualindex_header['famille']      = 'controle'
    qualindex_header['dim_array']    = 1


    diag = {'CodeRet' : 0,
            'DiagExec': f"Qualite_profil_lidar : ({len(pr2_data)} ech.)"
           }

    return [qualindex_header], \
           [qualindex_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Qualite_profil_lidar': {
        'Args': [
           {'Id': 'pr2'         , 'categorie': 'VECTOR_IN'              },
           {'Id': 'pr2_mol'     , 'categorie': 'VECTOR_IN'              },
           {'Id': 'z'           , 'categorie': 'VECTOR_IN'              },
           {'Id': 'zref'        , 'categorie': 'VECTOR_IN' , 'unit': 'm'},
           {'Id': 'qualindex'   , 'categorie': 'VECTOR_OUT'             },
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

    # Qualite_profil_lidar (
    #   opt_pr2_lid_filtre_%60,
    #   opt_pr2_mol_mod_%60,
    #   $Arg1.array_dim,
    #   alt_gate_lid_%60,
    #   alt_zref_lid_%60,
    #   flg_qualite_slope_lid_mod_%60
    #   )

    # sur de vrais vecteurs
    acqid = 'PM200274'
    logger.info(f'=== {acqid}')
    pr2     = AIDA.VectorMask(acqid, 'opt_pr2_lid_filtre_%60')
    pr2_mol = AIDA.VectorMask(acqid, 'opt_pr2_mol_mod_%60')
    z       = AIDA.VectorMask(acqid, 'alt_gate_lid_%60')
    zref    = AIDA.VectorMask(acqid, 'alt_zref_lid_%60')

    # appel de l'opérateur
    logger.info('*** appel de Qualite_profil_lidar')
    headers, datas, diag = Qualite_profil_lidar (pr2, pr2_mol, z, zref)

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
