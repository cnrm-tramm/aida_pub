#!/usr/bin/env python3

"""
    ADC : Opérateur FT_analytique_Moncrieff
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
def FT_analytique_Moncrieff(nfreq, hp_lp, fe, tint, type1, type2, hsep, vsep, type_hp, tauf, u_moy):
    """
    Compute analytic transfert function of the eddy-covariance measuremnt system

    Input :
        nfreq   : number of frequency for transfert function
        hp_lp   : type analaytic FT :
                  - 'HP'   : high-pass only,
                  - 'LP'   : low-pass only,
                  - 'HPLP' : high-pass and low-pass
        fe      : sample frequency (Hz)
        tint    : integration duration (s)
        type 1  : type of instrument 1
        type 2  : type of instrument 2
        hsep    : horizontal separation between instruments 1 and 2 (m)
        vsep    : vertical separation between instruments 1 and 2 (m)
        type_hp : type of fluctuation computing method :
                  - 'ba' : block average,
                  - 'rm' : moyenne glissante
        tauf    : time constant of running-mean
        u_moy   : wind speed

    Output :
        nf      : frequency
        TF      : Tranfert function


    Auteur : @Météo-France CNRM/GMEI/TRAMM - June 2020

    sources :
    Moncrieff an al 2004
    Moncrieff an al 1997
    EddyPro : bpcf_moncrieff_97.f90
    """
    logger.debug("FT_analytique_Moncrieff : debut")

    # récupération des arguments
    u_moy_header = u_moy.attributes
    u_moy_data   = u_moy.data.data


    # appel de la fonction de calcul
    nf, TF_data = \
        calcul.FT_analytique_Moncrieff.FT_analytique_Moncrieff(nfreq, hp_lp, fe, tint, type1, type2, hsep, vsep, type_hp, tauf, u_moy_data)

    # prépartation des bornes à partir de 'nf'
    list_bornes = [ f"({d:.6e},{d:.6e});" for d in nf ]
    str_bornes = ''.join(list_bornes)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    TF_header                 = default_out_header.copy()
    TF_header['name']         = "Fonction de transfert analytique du systeme selon Moncrieff 1997"
    TF_header['english_name'] = "Transfert function of measrement system from Moncrieff 1997"
    TF_header['unit']         = "unitless"
    TF_header['freq_ech']     = f"{u_moy_header['freq_ech']}"
    TF_header['ref_time']     = f"{u_moy_header['ref_time']}"
    TF_header['misval']       = f"{u_moy_header['misval']}"
    TF_header['famille']      = "controle"
    TF_header['bornes']       = str_bornes[0:-1]


    diag = {'CodeRet' : 0,
            'DiagExec': f"FT_analytique_Moncrieff : ({len(u_moy_data)} ech.)"
           }

    return [TF_header], \
           [TF_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'FT_analytique_Moncrieff': {
        'Args': [
            {'Id': 'nfreq'     , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'hp_lp'     , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'fe'        , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'tint'      , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'type1'     , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'type2'     , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'hsep'      , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'vsep'      , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'type_hp'   , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'tauf'      , 'categorie': 'COEFFICIENT'                                    },
            {'Id': 'u_moy'     , 'categorie': 'VECTOR_IN'  , 'unit': 'm/s', 'famille': ['vent']},
            {'Id': 'cospectrum', 'categorie': 'VECTOR_OUT'                                     },
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


    #FT_analytique_Moncrieff (
    #   500,
    #   "HPLP",
    #   20,
    #   1800,
    #   "r3_50",
    #   "li7500a",
    #   0.15,
    #   0.,
    #   "rm",
    #   200,
    #   ven_ff_gill_UV_%1800,
    #   ctl_FT_Moncrieff_gill_licor_%1800
    #)

    # sur de vrais vecteurs
    acqid = 'Tf210001'
    logger.info(f'=== {acqid}')
    nfreq   = 500
    hp_lp   = "HPLP"
    fe      = 20
    tint    = 1800
    type1   = "r3_50"
    type2   = "li7500a"
    hsep    = 0.15
    vsep    = 0.
    type_hp = "rm"
    tauf    = 200
    u_moy      = AIDA.VectorMask(acqid, 'ven_ff_gill_UV_%1800')

    # appel de l'opérateur
    logger.info('*** appel de FT_analytique_Moncrieff')
    headers, datas, diag = FT_analytique_Moncrieff(nfreq, hp_lp, fe, tint, type1, type2, hsep, vsep, type_hp, tauf, u_moy)

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
