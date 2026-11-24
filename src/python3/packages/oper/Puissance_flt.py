#!/usr/bin/env python3

"""
    ADC : Opérateur Ech_tps_impos: échantillonnage d'une variable sur une base de temps régulière
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


def Puissance_flt (X, p, units,nom_francais,english_name) :

    """
    Mise à la puissance p du vecteur X
    """
    #récupération des arguments
    X_header = X.attributes
    X_data = X.data.data
    
    
    #Appel de la fonction de calcul
    VO_data, fct_ret = calcul.Puissance_flt.fct_Puissance_flt(X_data, p)
    
    # préparation du retour
    # ATTENTION : les champs 'name' et 'english name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    
    VO_header                 = default_out_header.copy()
    VO_header['name']         = f"{nom_francais}"
    VO_header['english_name'] = f"{english_name}"
    VO_header['ref_time']     = f"{X_header['ref_time']}"
    VO_header['unit']         = f"{units}"
    if VO_data.ndim > 1 :
        VO_header['bornes']          = f"{X_header['bornes']}"
        VO_header['unit_bornes']     = f"{X_header['unit_bornes']}"
    VO_header['freq_ech']     = f"{X_header['freq_ech']}"
    VO_header['misval']       = f"{X_header['misval']}"
    VO_header['format']       = f"{X_header['format']}"


    if fct_ret == -1:
        msg_1 =  f"La puissance ne peut pas être un nan" 

    else:
        msg_1 = f" OK" 
        fct_ret = 0

    diag = {'CodeRet' : fct_ret,
            'DiagExec': f"{msg_1}"
           }

    return [VO_header], \
           [VO_data.astype(np.float32)  ], \
           diag

#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Puissance_flt': {
        'Args': [
            {'Id': 'X'            , 'categorie': 'VECTOR_IN'               },
            {'Id': 'p'            , 'categorie': 'COEFFICIENT'             },
            {'Id': 'units'        , 'categorie': 'COEFFICIENT'             },
            {'Id': 'nom_francais' , 'categorie': 'COEFFICIENT'             },
            {'Id': 'english_name' , 'categorie': 'COEFFICIENT'             },
            {'Id': 'X_out'        , 'categorie': 'VECTOR_OUT'              },
        ],
    },
}


#==============================================================================
# Test de l'opérateur
#==============================================================================
if __name__ == '__main__':

    from fct_messages import wait_user

    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')


    # OPERATEUR SIMPLIFIÉ : sur de vrais vecteurs
    # 1D data
    acqid = 'ls230140'
    logger.info(f'=== {acqid}')
    X             = AIDA.VectorMask(acqid, 'tpr_air_2m_cal_%60')
    p             = 2
    units         = "m2/s2"
    nom_francais  = "carré de la vitesse du vent"
    english_name  = "square of wind speed"
    
    # 2D data
    acqid = 'Ce210182'
    logger.info(f'=== {acqid}')
    X             = AIDA.VectorMask(acqid, 'ven_ff_windcube0_Eti_%4')
    p             = 2
    units         = "m2/s2"
    nom_francais  = "carré de la vitesse du vent"
    english_name  = "square of wind speed"
    
    # appel de l'opérateur simplifié
    logger.info('*** opérateur simplifié : Puissance_flt')

    headers, datas, diag = Puissance_flt(X, p, units, nom_francais, english_name)

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
        logger.info(f"data[-5:] = {data[-5:]}")
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
    input("...[ENTER] pour continuer ")
