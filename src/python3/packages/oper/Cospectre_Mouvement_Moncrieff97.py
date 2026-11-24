#!/usr/bin/env python3

"""
    ADC : Opérateur Cospectre_Mouvement_Moncrieff97
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
def Cospectre_Mouvement_Moncrieff97(nfreq, z, d, L, u_moy):
    """
    Compute analytic of wu cospectrum by Moncrieff 97

    Input :
        nfreq : number of frequency of cospectrum
        z     : measurement height
        d     : displacement height
        L     : Monin-Obhukov length
        u_moy : wind speed

    Output :
        nf         : frequency of cospectrum
        cospectrum : Heat cospectrum

    Auteur : @Météo-France CNRM/GMEI/TRAMM - June 2020

    sources :
    Moncrieff and al 1997
    EddyPro : bpcf_cospectral_models.f90
    """
    logger.debug("Cospectre_Mouvement_Moncrieff97 : debut")

    # récupération des arguments
    L_header = L.attributes
    L_data   = L.data.data

    u_moy_header = u_moy.attributes
    u_moy_data   = u_moy.data.data


    # appel de la fonction de calcul
    nf, cospectrum_data = \
        calcul.Cospectre_Mouvement_Moncrieff97.Cospectre_Mouvement_Moncrieff97(nfreq, z, d, L_data, u_moy_data)

    # prépartation des bornes à partir de 'nf'
    list_bornes = [ f"({d:.6e},{d:.6e});" for d in nf ]
    str_bornes = ''.join(list_bornes)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    cospectrum_header                 = default_out_header.copy()
    cospectrum_header['name']         = "Cospectre analytique WU selon Moncrieff 1997"
    cospectrum_header['english_name'] = "WU analytic cospectrum Moncrieff 1997"
    cospectrum_header['unit']         = "unitless"
    cospectrum_header['freq_ech']     = f"{L_header['freq_ech']}"
    cospectrum_header['ref_time']     = f"{L_header['ref_time']}"
    cospectrum_header['misval']       = f"{L_header['misval']}"
    cospectrum_header['famille']      = "turbulence"
    cospectrum_header['bornes']       = str_bornes[0:-1]


    diag = {'CodeRet' : 0,
            'DiagExec': f"Cospectre_Mouvement_Moncrieff97 : ({len(L_data)} ech.)"
           }

    return [cospectrum_header], \
           [cospectrum_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Cospectre_Mouvement_Moncrieff97': {
        'Args': [
            {'Id': 'nfreq'     , 'categorie': 'COEFFICIENT'                                          },
            {'Id': 'z'         , 'categorie': 'COEFFICIENT'                                          },
            {'Id': 'd'         , 'categorie': 'COEFFICIENT'                                          },
            {'Id': 'L'         , 'categorie': 'VECTOR_IN'  , 'unit': 'm'  , 'famille': ['turbulence']},
            {'Id': 'u_moy'     , 'categorie': 'VECTOR_IN'  , 'unit': 'm/s', 'famille': ['vent']      },
            {'Id': 'cospectrum', 'categorie': 'VECTOR_OUT'                                           },
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


    #Cospectre_Mouvement_Moncrieff97 (
    #   500,
    #   3.70,
    #   0.4*0.6700,
    #   trb_lmon_tson_gill_Moa_%1800,
    #   ven_ff_gill_UV_%1800,
    #   trb_cosp_mvt_Moncrieff97_%1800
    #)

    # sur de vrais vecteurs
    acqid = 'Tf210001'
    logger.info(f'=== {acqid}')
    nfreq      = 500
    z          = 3.70
    d          = 0.4*0.6700
    L          = AIDA.VectorMask(acqid, 'trb_lmon_tson_gill_Moa_%1800')
    u_moy      = AIDA.VectorMask(acqid, 'ven_ff_gill_UV_%1800')

    # appel de l'opérateur
    logger.info('*** appel de Cospectre_Mouvement_Moncrieff97')
    headers, datas, diag = Cospectre_Mouvement_Moncrieff97 (nfreq, z, d, L, u_moy)

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
