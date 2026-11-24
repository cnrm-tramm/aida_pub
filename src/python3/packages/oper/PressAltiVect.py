#!/usr/bin/env python3

"""
    ADC : Opérateur PressAltiVect
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
def PressAltiVect(P0, Tv, Z0, Z, rsurg):
    """
    Calcul de la pression aux altitudes Z à partir des pressions P0 mesurées
    aux altitudes Z0.

    Input :
        P0    : Pressions au niveau Z0.
        Tv    : Tempé virtuelle moyenne de la couche.
        CtoK  : Valeur à ajouter pour convertir en °K.
        Z0    : Altitudes correpondantes à P0.
        Z     : Altitudes pour lesquelles on calcule P.
        rsurg : "constante" r/g.

    Output :
        P  : Pressions aux altitudes Z.

    Auteur : @Météo-France CNRM/GMEI/TRAMM - September 2019
    """
    logger.debug("PressAltiVect : debut")

    # récupération des arguments
    P0_header = P0.attributes
    P0_data   = P0.data.data

    Tv_header = Tv.attributes
    Tv_data   = Tv.data.data

    Z0_header = Z0.attributes
    Z0_data   = Z0.data.data

    Z_header = Z.attributes
    Z_data   = Z.data.data

    # préparation des arguments pour la fonction de calcul
    CtoK  = calcul.unit.auto_tempe_unit(Tv_data.data)
    if CtoK == 0:
        unit_msg = "Unite Temperature reconnue : Kelvin"
    else:
        unit_msg = "Unite Temperature reconnue : Degres Celsius"

    # appel de la fonction de calcul
    P_data = calcul.PressAltiVect.PressAltiVect(P0_data, Tv_data, CtoK, Z0_data, Z_data, rsurg)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    P0_fr_name, P0_en_name = P0.get_names()

    P_header                 = default_out_header.copy() 
    P_header['name']         = f"Pression calculee a partir de '{P0_fr_name}'"
    P_header['english_name'] = f"Pressure computed with '{P0_en_name}'"
    P_header['unit']         = f"{P0_header['unit']}"
    P_header['freq_ech']     = f"{P0_header['freq_ech']}"
    P_header['ref_time']     = f"{P0_header['ref_time']}"
    P_header['misval']       = f"{P0_header['misval']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"PressAltiVect : ({len(P0_data)} ech.), " +
                        f"Z0 = {Z0_data[0]}, Z = {Z_data[0]}, R/g = {rsurg}, " +
                        f"{unit_msg}"
           }

    return [P_header], [P_data], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'PressAltiVect': {
        'Args': [
            {'Id': 'P0'   , 'categorie': 'VECTOR_IN'  , 'unit': 'hPa' },
            {'Id': 'Tv'   , 'categorie': 'VECTOR_IN'  , 'unit': 'K'   },
            {'Id': 'Z0'   , 'categorie': 'VECTOR_IN'  , 'unit': 'm'   },
            {'Id': 'Z'    , 'categorie': 'VECTOR_IN'  , 'unit': 'm'   },
            {'Id': 'rsurg', 'categorie': 'COEFFICIENT'                },
            {'Id': 'P'    , 'categorie': 'VECTOR_OUT'                 },
        ],
    },
}


#==============================================================================
# Test de l'opérateur
#==============================================================================
if __name__ == '__main__':

    import AIDA
    from   Misval import AIDA_type_misval as AIDA_type_misval


    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')


    # création de Vector en mémoire
    acqid = 'ch229999'
    logger.info(f'=== {acqid}')
    header = dict()
    header['name']         = 'pseudo variable pre_air_gillwp_stv4_sflg_20'
    header['english_name'] = 'pseudo variable pre_air_gillwp_stv4_sflg_20'
    header['format']       = 'Ieeefloat_32'
    header['dimension']    = '4'
    header['dim_array']    = '1'
    header['ref_time']     = 'rft_time_PSEUDO_REG_20'
    header['misval']       = AIDA_type_misval[ header['format'] ]
    header['freq_ech']     = 20
    header['unit']         = 'hPa'
    header['famille']      = 'pression'
    header['origine']      = 'pseudo donnees de test'


    misval = float(header['misval'])
    P0 = AIDA.VectorMask(acqid, 'P0', attributes=header, data=np.array([np.nan,  2.,  3.,  4.,  5.]))
    Tv = AIDA.VectorMask(acqid, 'Tv', attributes=header, data=np.array([np.nan, 12., 13., 14., 15.]))
    Z0 = AIDA.VectorMask(acqid, 'Z0', attributes=header, data=np.array([misval, 22., 23., 24., 25.]))
    Z  = AIDA.VectorMask(acqid, 'Z' , attributes=header, data=np.array([np.inf, 32., 33., 34., 35.]))

    # appel de l'opérateur
    headers, datas, diag = PressAltiVect(P0, Tv, Z0, Z, 29.27)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in { k:header[k] for k in sorted(header) }.items():
            logger.info(f"  - {key:15s} = {value}")
            if key == 'misval':
                logger.info(f"  - {key:15s} : type = {type(value)} ")

        logger.info(f"data   = {data}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
