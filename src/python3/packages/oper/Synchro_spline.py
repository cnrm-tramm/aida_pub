#!/usr/bin/env python3

"""
    ADC : Opérateur Synchro_spline
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
def Synchro_spline(X, time_dest, decal, unit):
    """
    Synchroniser un parametre sur une autre base de temps par interpolation
    par spline.

    Input :
        X         : variable à interpoler
        time_dest : temps destination
        decal     : decalage temporel (s)
        unit      : Unité de X (vaut "radians", "degres" pour un angle)

    Output :
        X_sync    : X synchronisé sur time_dest 


    Auteur : @Météo-France CNRM/GMEI/TRAMM
    W. Maurel
    le 06/03/2020
    """
    logger.debug("Synchro_spline : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    time_dest_header = time_dest.attributes
    time_dest_data   = time_dest.data.data


    # préparation des arguments pour la fonction de calcul
    # - récupération des données du vecteur temps de X_in
    time_data = X.timedata()
    # unit doit être fourni par l'utilisateur (celle du vecteur peut-être
    # degree qui n'est pas considéré de typ = "angle" (cf. doc de l'opérateur)
    ##unit      = X_header['unit']


    # appel de la fonction de calcul
    X_sync_data = \
        calcul.Synchro_spline.Synchro_spline(X_data, time_data, time_dest_data, decal, unit)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X.get_names()

    logger.warning("dans ID_Synchro_spline : name = $Arg1.name : il faudrait au moins ajouter Synchro ?")
    X_sync_header                 = default_out_header.copy()
    X_sync_header['name']         = f"{X_fr_name}"
    X_sync_header['english_name'] = f"{X_en_name}"
    X_sync_header['unit']         = f"{X_header['unit']}"
    X_sync_header['freq_ech']     = f"{time_dest_header['freq_ech']}"
    X_sync_header['ref_time']     = f"{time_dest_header['#hdr_name']}" 
    X_sync_header['misval']       = f"{X_header['misval']}"
    X_sync_header['dim_array']    = f"{time_dest_header['dim_array']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"Synchro_spline : ({len(X_data)} ech.)"
           }

    return [X_sync_header], \
           [X_sync_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Synchro_spline': {
        'Args': [
            {'Id': 'X'        , 'categorie': 'VECTOR_IN'                                     },
            {'Id': 'time_dest', 'categorie': 'VECTOR_IN'  , 'unit': 's', 'famille': ['temps']},
            {'Id': 'decal'    , 'categorie': 'COEFFICIENT'                                   },
            {'Id': 'unit'     , 'categorie': 'COEFFICIENT'                                   },
            {'Id': 'X_sync'   , 'categorie': 'VECTOR_OUT'                                    },
        ],
        'control_reftime': 'off',
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


    # Synchro_spline (
    #   vit_r_X_xsens_sflg_20,
    #   rft_time_xsens_20,
    #   rft_time_gillwp_20,
    #   -0.08,
    #   "",
    #   $Arg3.NbVal,
    #   vit_r_X_xsens_syncGill_dm08_20)

    # sur de vrais vecteurs
    acqid = 'Ce210208'
    logger.info(f'=== {acqid}')
    X          = AIDA.VectorMask(acqid, 'vit_r_X_xsens_sflg_20')
    time_dest  = AIDA.VectorMask(acqid, 'rft_time_gillwp_20')
    decal      = -0.08
    unit       = 'raidans'

    # appel de l'opérateur
    logger.info('*** appel de Synchro_spline')
    headers, datas, diag = Synchro_spline (X, time_dest, decal, unit)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in header.items():
            logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data[0:5] = {data[0:5]}")
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
