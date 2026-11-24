#!/usr/bin/env python3

"""
    ADC : Opérateur ProfilMobile2geo_1D
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
def ProfilMobile2geo_1D(X, vert_direction, roulis, tangage, altitude):
    """
    Convertit les coordonnées (altitude) d'un profil exprimées dans un
    repère mobile en coordonnées géographiques.

    Input :
        X              : signal mesuré.
        vert_direction : 1 si mesure vers le haut, -1 si mesure vers le bas.
        roulis         : roulis (degrés).
        tangage        : tangage (degrés).
        altitude       : altitude de la plateforme (m).

    Output :
        altitude_x     : altitude des mesures X (m).

    Auteur : @Météo-France CNRM/GMEI/TRAMM
    """
    logger.debug("ProfilMobile2geo_1D : debut")

    # récupération des arguments
    X_header        = X.attributes # pour les bornes seulement
    X_data          = X.data.data  # pour DiagExec

    roulis_header   = roulis.attributes
    roulis_data     = roulis.data.data

    tangage_header  = tangage.attributes
    tangage_data    = tangage.data.data

    altitude_header = altitude.attributes
    altitude_data   = altitude.data.data


    # préparation des arguments pour la fonction de calcul
    X_str_bornes = X_header['bornes']
    range_gate   = AIDA.strBornes_to_array(X_str_bornes)[0]

    # appel de la fonction de calcul
    altitude_x_data = \
        calcul.ProfilMobile2geo_1D.ProfilMobile2geo_1D(range_gate,
                                                       vert_direction,
                                                       roulis_data,
                                                       tangage_data,
                                                       altitude_data)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X.get_names()

    altitude_x_header                 = default_out_header.copy()
    altitude_x_header['name']         = f"{X_fr_name}"
    altitude_x_header['english_name'] = f"{X_en_name}"
    altitude_x_header['unit']         = 'm'
    altitude_x_header['freq_ech']     = f"{X_header['freq_ech']}"
    altitude_x_header['ref_time']     = f"{X_header['ref_time']}"
    altitude_x_header['misval']       = f"{X_header['misval']}"
    altitude_x_header['famille']      = 'altitude'
    altitude_x_header['dim_array']    = f"{X_header.get('dim_array', 1)}"
    altitude_x_header['bornes']       = f"{X_header['bornes']}"
    altitude_x_header['unit_bornes']  = f"{X_header['unit_bornes']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"ProfilMobile2geo_1D : ({len(X_data)} ech.)"
           }

    return [altitude_x_header], \
           [altitude_x_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'ProfilMobile2geo_1D': {
        'Args': [
            {'Id': 'X'             , 'categorie': 'VECTOR_IN'                    },
            {'Id': 'vert_direction', 'categorie': 'COEFFICIENT'                  },
            {'Id': 'roulis'        , 'categorie': 'VECTOR_IN'  , 'unit': 'degree', 'famille': ['attitude']},
            {'Id': 'tangage'       , 'categorie': 'VECTOR_IN'  , 'unit': 'degree', 'famille': ['attitude']},
            {'Id': 'altitude'      , 'categorie': 'VECTOR_IN'  , 'unit': 'm'     , 'famille': ['altitude']},
            {'Id': 'altitude_x'    , 'categorie': 'VECTOR_OUT'                   },
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


    # ProfilMobile2geo_1D (
    #   opt_dclid1_raw_%60,
    #   $Arg1.bornes,
    #   $Arg1.array_dim,
    #   1,
    #   att_rollaipov_Met_%60,
    #   att_pitchaipov_Met_%60,
    #   alt_altaipov_Met_%60,
    #   alt_gate_lid_%60)

    # sur de vrais vecteurs
    acqid = 'fs200013'
    logger.info(f'=== {acqid}')
    X              = AIDA.VectorMask(acqid, 'opt_dclid1_raw_%60')
    roulis         = AIDA.VectorMask(acqid, 'att_rollaipov_Met_%60')
    tangage        = AIDA.VectorMask(acqid, 'att_pitchaipov_Met_%60')
    altitude       = AIDA.VectorMask(acqid, 'alt_altaipov_Met_%60')
    vert_direction = 1

    # appel de l'opérateur
    logger.info('*** appel de ProfilMobile2geo_1D')
    headers, datas, diag = ProfilMobile2geo_1D (X, vert_direction, roulis, tangage, altitude)

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
