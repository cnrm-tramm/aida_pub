#!/usr/bin/env python3

"""
    ADC : Opérateur UV2ddff
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
def UV2ddff(U,V):
    """
    Calcul ddes composantes polaires du vent

    Input :
        U    : Composante méridienne du vent
        V    : Composante zonale du vent

    Output :
        DD  : Direction géographique du vent
        FF  : vitesse du vent

    Auteur : @Météo-France CNRM/GMEI/TRAMM - September 2019
    """
    logger.debug("UV2ddff : debut")

    # récupération des arguments
    U_header = U.attributes
    U_data   = U.data.data

    V_header = V.attributes
    V_data   = V.data.data


    # appel de la fonction de calcul
    dd,ff = calcul.UV2ddff.UV2ddff(U_data, V_data)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    #Header dd

    dd_header                 = default_out_header.copy() 
    dd_header['name']         = f"Direction du vent"
    dd_header['english_name'] = f"Wind direction"
    dd_header['unit']         = "degree"
    dd_header['freq_ech']     = f"{U_header['freq_ech']}"
    dd_header['ref_time']     = f"{U_header['ref_time']}"
    dd_header['misval']       = f"{U_header['misval']}"
    if dd.ndim > 1 :
        dd_header['bornes']       = f"{U_header['bornes']}"
        dd_header['unit_bornes']  = f"{U_header['unit_bornes']}"


    #Header ff
    ff_header                 = default_out_header.copy() 
    ff_header['name']         = f"Force du vent"
    ff_header['english_name'] = f"Wind speed"
    ff_header['unit']         = f"m.s-1"
    if ff.ndim > 1 :
        ff_header['bornes']       = f"{U_header['bornes']}"
        ff_header['unit_bornes']  = f"{U_header['unit_bornes']}"
    ff_header['freq_ech']     = f"{U_header['freq_ech']}"
    ff_header['ref_time']     = f"{U_header['ref_time']}"
    ff_header['misval']       = f"{U_header['misval']}"


    diag = {'CodeRet' : 0,
            'DiagExec': f"UV2ddff, NbVal = {len(dd)}"
           }

    return [dd_header,ff_header], [dd,ff], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'UV2ddff': {
        'Args': [
            {'Id': 'U'   , 'categorie': 'VECTOR_IN'                 },
            {'Id': 'V'   , 'categorie': 'VECTOR_IN'                 },
            {'Id': 'dd'  , 'categorie': 'VECTOR_OUT'                },
            {'Id': 'ff'  , 'categorie': 'VECTOR_OUT'                },
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


    # Données 1D
    acqid = 'ls230224'
    logger.info(f'=== {acqid}')
    U        = AIDA.VectorMask(acqid, 'ven_u_metek_Rot_50')
    V        = AIDA.VectorMask(acqid, 'ven_v_metek_Rot_50')

    # ##Données 2D
    # acqid = 'Ce210185'
    # logger.info(f'=== {acqid}')
    # U        = AIDA.VectorMask(acqid, 'ven_u_windcube_Frc200_%4')
    # V        = AIDA.VectorMask(acqid, 'ven_v_windcube_Frc200_%4')



    # appel de l'opérateur
    headers, datas, diag = UV2ddff(U,V)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in { k:header[k] for k in sorted(header) }.items():
            logger.info(f"  - {key:15s} = {value}")
            
        logger.info(f"data[0:5] = {data[0:5]}")
        logger.info(f"data[5:] = {data[-5:]}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
