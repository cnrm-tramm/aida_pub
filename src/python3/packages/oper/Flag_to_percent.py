#!/usr/bin/env python3

"""
    ADC : Opérateur Flag_to_percent
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
def Flag_to_percent(X, Tx, f, Ty):
    """
    A partir d'un vecteur de flags et de sa base de temps,
    calcule le pourcentage d'une valeur de flag donnée sur une base de temps
    donnée. 

    Input :
        X  : Variable flag d'entrée
        Tx : Variable temps associé à X
        f  : Valeur du flag à évaluer
        Ty : Variable temps associé à Y

    Output :
        Y  : Variable Y contenant le pourcentage de f sur chaque période

        
    Auteur : @Météo-France CNRM/GMEI/TRAMM - June 2020

    sources :
    Moncrieff and al 1997
    EddyPro : bpcf_cospectral_models.f90
    """
    logger.debug("Flag_to_percent : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    Tx_header = Tx.attributes
    Tx_data   = Tx.data.data

    Ty_header = Ty.attributes
    Ty_data   = Ty.data.data

    # attention : la fonction de calcul attent f sous forme indiçable
    f_list = [ f ]

    # appel de la fonction de calcul
    data = \
        calcul.Flag_to_percent.Flag_to_percent(X_data, Tx_data, f_list, Ty_data)

    # préparation du retour
    # les données retournées par la fonction de calcul ne sont pas en ATYC_I32
    np_char_format = 'i'
    Y_data = np.array(data, dtype=np_char_format)
    misval = np.iinfo(np_char_format).max

    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    Y_header                 = default_out_header.copy()
    Y_header['name']         = ''
    Y_header['english_name'] = ''
    Y_header['format']       = 'Int_32' ## f"{X_header['format']}"
    Y_header['unit']         = f"{X_header['unit']}"
    Y_header['freq_ech']     = f"{Ty_header['freq_ech']}"
    Y_header['ref_time']     = f"{Ty_header['#hdr_name']}"
    Y_header['misval']       = f"{misval}"


    diag = {'CodeRet' : 0,
            'DiagExec': f"Flag_to_percent : ({len(X_data)} ech.)"
           }

    return [Y_header], \
           [Y_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Flag_to_percent': {
        'Args': [
            {'Id': 'X'         , 'categorie': 'VECTOR_IN'                 },
            {'Id': 'Tx'        , 'categorie': 'VECTOR_IN'                 },
            {'Id': 'f'         , 'categorie': 'COEFFICIENT'               },
            {'Id': 'Ty'        , 'categorie': 'VECTOR_IN'                 },
            {'Id': 'Y'         , 'categorie': 'VECTOR_OUT'                },
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

    #Flag_to_percent (
    #   ctl_flag_invalid_pression_%60,
    #	rft_time_REG_%60,
    #	1,
    #	rft_time_REG_%1800,
    #	$Arg4.NbVal,
    #	ctl_flag_invalid_pression_Ftp_%1800
    #)

    # sur de vrais vecteurs
    acqid = 'Tf210001'
    logger.info(f'=== {acqid}')
    X          = AIDA.VectorMask(acqid, 'ctl_flag_invalid_pression_%60')
    Tx         = AIDA.VectorMask(acqid, 'rft_time_REG_%60')
    f          = 1
    Ty         = AIDA.VectorMask(acqid, 'rft_time_REG_%1800')

    # appel de l'opérateur
    logger.info('*** appel de Flag_to_percent')
    headers, datas, diag = Flag_to_percent (X, Tx, f, Ty)

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
