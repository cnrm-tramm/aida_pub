#!/usr/bin/env python3

"""
    ADC : Opérateur Extract_Closest_PointLatLonAlt
"""

import sys
import os
import logging
import numpy as np
import re

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
def Extract_Closest_PointLatLonAlt(X_in, alts, tgt_lat, tgt_lon, tgt_alt):
    """
    

    Input :


    Output :

    Auteur : @Météo-France CNRM/GMEI/TRAMM - April 2024
    """
    logger.debug("Extract_Closest_PointLatLonAlt : debut")

    # récupération des arguments
    X_in_data = X_in.data.data
    X_in_header = X_in.attributes

    # récupération des arguments
    alts_data = alts.data.data
    alts_data = [85.33097, 75.78337, 42.51276, 65.04237, 54.87577, 34.50908, 52.29393, 43.80265, 39.4988]

    # préparation des arguments pour la fonction de calcul
    str_bornes_arome = X_in_header['bornes']
    list_bornes = AIDA.strBornes_to_array(str_bornes_arome)[0][:,0]
    dimension_array_arome = AIDA.get_dim_array(X_in_header['dim_array'])

    # On suppose que la dimension de X est (lons, lats, niveaux)
    lons = list_bornes[0:(dimension_array_arome[0]*dimension_array_arome[1])]
    lats = list_bornes[(dimension_array_arome[0]*dimension_array_arome[1]):(dimension_array_arome[0]*dimension_array_arome[1]*2)]


    # appel de la fonction de calcul
    X_out_data = calcul.Extract_Closest_PointLatLonAlt.fct_Extract_Closest_PointLatLonAlt(X_in_data, lats, lons, alts_data, tgt_lat, tgt_lon, tgt_alt)
    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X_in.get_names()

    X_out_header                 = default_out_header.copy() 
    X_out_header['name']         = f"Extraction du tableau dont les coordonnées sont les plus proches du point à partir du tableau initial '{X_fr_name}'"
    X_out_header['english_name'] = f"Subarray which is the closest from a given point from '{X_en_name}'"
    if X_out_data.ndim > 1 :
        X_out_header['bornes']         = f"{X_in_header['bornes']}"
        X_out_header['unit_bornes']         = f"{X_in_header['unit_bornes']}"
    X_out_header['unit']         = f"{X_in_header['unit']}"
    X_out_header['freq_ech']     = f"{X_in_header['freq_ech']}"
    X_out_header['ref_time']     = f"{X_in_header['ref_time']}"
    X_out_header['misval']       = f"{X_in_header['misval']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"Extract_Closest_PointLatLonAlt : ({len(X_out_data)} ech.), "
           }

    return [X_out_header], [X_out_data], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Extract_Closest_PointLatLonAlt': {
        'Args': [
            {'Id': 'X_in'  , 'categorie': 'VECTOR_IN'              },
            {'Id': 'alt_hpa'  , 'categorie': 'VECTOR_IN'           },
            {'Id': 'tgt_lat'   , 'categorie': 'COEFFICIENT'        },
            {'Id': 'tgt_lon'   , 'categorie': 'COEFFICIENT'        },
            {'Id': 'tgt_alt'   , 'categorie': 'COEFFICIENT'        },
            {'Id': 'X_out'    , 'categorie': 'VECTOR_OUT'          },
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
    acqid = 'ju230150'
    X_in        = AIDA.VectorMask(acqid, 'tpr_air_profil_arome_ech01_Eti_%3600')
    alt_hpa     = AIDA.VectorMask(acqid, 'pre_surf_geopotentiel_arome_ech01_Eti_%3600')
    tgt_lon     = 2.38
    tgt_lat     = 48.82
    tgt_alt     = 35


    # appel de l'opérateur
    headers, datas, diag = Extract_Closest_PointLatLonAlt(X_in, alt_hpa, tgt_lat, tgt_lon, tgt_alt)

    # # résultat
    # logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    # for header, data in zip(headers, datas):
    #     logger.info("header : ")
    #     for key, value in { k:header[k] for k in sorted(header) }.items():
    #         logger.info(f"  - {key:15s} = {value}")
    #         if key == 'misval':
    #             logger.info(f"  - {key:15s} : type = {type(value)} ")

    #     logger.info(f"data   = {data}")

    # logger.info("Diagnostique :")
    # for key, value in diag.items():
    #     logger.info(f"  - {key} = {value}")
