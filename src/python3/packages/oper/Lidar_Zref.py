#!/usr/bin/env python3

"""
    ADC : Opérateur Lidar_Zref
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
def Lidar_Zref(x, z, z1, z2, step):
    """
    Calcul des altitudes de reference Lidar 

    Input :
        x    : the Pr2 signal from the LIDAR remote sensing
        z    : altitudes above the ground level (m)
        z1   : minimal altitude above z for reference altitude (m)
        z2   : maximal altitude above z for reference altitude (m)
        step : nombre de points de la moyenne glissante de x

    Output :
        zref : minimum altitude wher there is only molecular diffusion  

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Febr 2018

    sources :
    transcodage de scilab en Python à partir de la filiere BASIC du LOA 
    fonction scilab originale : f_Zref.sci
    """
    logger.debug("Lidar_Zref : debut")

    # récupération des arguments
    x_header  = x.attributes
    x_data    = x.data.data

    z_header  = z.attributes
    z_data    = z.data.data


    # préparation des arguments pour la fonction de calcul

    # appel de la fonction de calcul
    zref_data = \
        calcul.Lidar_Zref.Lidar_Zref(x_data, z_data, z1, z2, step)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    zref_header = default_out_header.copy()
    zref_header['name']         = 'Altitude de reference maximale'
    zref_header['english_name'] = 'Max reference altitude'
    zref_header['unit']         = 'm'
    zref_header['freq_ech']     = f"{x_header['freq_ech']}"
    zref_header['ref_time']     = f"{x_header['ref_time']}"
    zref_header['misval']       = f"{x_header['misval']}"
    zref_header['famille']      = 'altitude'
    zref_header['dim_array']    = 1


    diag = {'CodeRet' : 0,
            'DiagExec': f"Lidar_Zref : ({len(x_data)} ech.)"
           }

    return [zref_header], \
           [zref_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Lidar_Zref': {
        'Args': [
           {'Id': 'x'   , 'categorie': 'VECTOR_IN'                , 'famille': ['optique'] },
           {'Id': 'z'   , 'categorie': 'VECTOR_IN'  , 'unit': 'm' , 'famille': ['altitude']},
           {'Id': 'z1'  , 'categorie': 'COEFFICIENT'                                       },
           {'Id': 'z2'  , 'categorie': 'COEFFICIENT'                                       },
           {'Id': 'step', 'categorie': 'COEFFICIENT'                                       },
           {'Id': 'zref', 'categorie': 'VECTOR_OUT'                                        },
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

    # Lidar_Zref (
    #   opt_pr2_lid_filtre_%60,
    #   alt_gate_lid_%60,
    #   $Arg1.array_dim,
    #   5000,
    #   6000,
    #   5,
    #   alt_zref_lid_%60
    #)

    # sur de vrais vecteurs
    acqid = 'PM200274'
    logger.info(f'=== {acqid}')
    x         = AIDA.VectorMask(acqid, 'opt_pr2_lid_filtre_%60')
    z         = AIDA.VectorMask(acqid, 'alt_gate_lid_%60')
    z1        = 5000
    z2        = 6000
    step      = 5

    # appel de l'opérateur
    logger.info('*** appel de Lidar_Zref')
    headers, datas, diag = Lidar_Zref (x, z, z1, z2, step)

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
