#!/usr/bin/env python3

"""
    ADC : Opérateur CorFlux_spectral
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
def CorFlux_spectral(cospectre, fct_transfert, flux):
    """
    Compute spectral correction and corrected flux
    with cospectra and transfer function of the measurements system

    Input :
        cospectre     : ideal cospectrum
        fct_transfert : transfer function of the measurement system
        flux          : flux to be corrected

    Output :
        flux_cor      : corrected flux
        cor_spectrale : spectral correction

    @ CNRM/GMEI/TRAMM - June 2020
    """
    logger.debug("CorFlux_spectral : debut")

    # récupération des arguments
    cospectre_header     = cospectre.attributes
    cospectre_data       = cospectre.data.data

    fct_transfert_header = fct_transfert.attributes
    fct_transfert_data   = fct_transfert.data.data

    flux_header          = flux.attributes
    flux_data            = flux.data.data


    # préparation des arguments pour la fonction de calcul
    #  freq : frequencies ($Arg1.bornes)
    str_bornes_in = cospectre_header['bornes']
    arr_bornes_in = AIDA.strBornes_to_array(str_bornes_in)
    freq  = arr_bornes_in[0]

    # appel de la fonction de calcul
    flux_cor_data, cor_spectrale_data = \
        calcul.CorFlux_spectral.CorFlux_spectral(freq, cospectre_data, fct_transfert_data, flux_data)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    flux_fr_name, flux_en_name = flux.get_names()

    flux_cor_header                 = default_out_header.copy()
    flux_cor_header['name']         = f"{flux_fr_name} avec correction spectrale"
    flux_cor_header['english_name'] = f"{flux_en_name} with spectral correction"
    flux_cor_header['unit']         = f"{flux_header['unit']}"
    flux_cor_header['freq_ech']     = f"{flux_header['freq_ech']}"
    flux_cor_header['ref_time']     = f"{flux_header['ref_time']}"
    flux_cor_header['misval']       = f"{flux_header['misval']}"

    cor_spectrale_header                 = default_out_header.copy()
    cor_spectrale_header['name']         = f"Correction spectrale de {flux_fr_name}"
    cor_spectrale_header['english_name'] = f"Spectral correction of {flux_en_name}"
    cor_spectrale_header['unit']         =  "unitless"
    cor_spectrale_header['famille']      =  "controle"
    cor_spectrale_header['freq_ech']     = f"{flux_header['freq_ech']}"
    cor_spectrale_header['ref_time']     = f"{flux_header['ref_time']}"
    cor_spectrale_header['misval']       = f"{flux_header['misval']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"CorFlux_spectral : ({len(cospectre_data)} ech.)"
           }

    return [flux_cor_header, cor_spectrale_header], \
           [flux_cor_data  , cor_spectrale_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'CorFlux_spectral': {
        'Args': [
            {'Id': 'cospectre'    , 'categorie': 'VECTOR_IN'                     },
            {'Id': 'fct_transfert', 'categorie': 'VECTOR_IN'                     },
            {'Id': 'flux'         , 'categorie': 'VECTOR_IN', 'famille': ['flux']},
            {'Id': 'flux_cor'     , 'categorie': 'VECTOR_OUT'                    },
            {'Id': 'cor_spectrale', 'categorie': 'VECTOR_OUT'                    },
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

    # CorFlux_spectral (
    #   trb_cosp_Moncrieff97_%1800,
    #   ctl_FT_Moncrieff_gill_licor_%1800,
    #   flx_cov_wconh2o_2D_Eti_%1800,
    #   flx_cov_wconh2o_2D_csp_%1800,
    #   ctl_cor_Moncrieff_wh2o_%1800
    #)

    # sur de vrais vecteurs
    acqid = 'Tf210001'
    logger.info(f'=== {acqid}')
    cospectre     = AIDA.VectorMask(acqid, 'trb_cosp_Moncrieff97_%1800')
    fct_transfert = AIDA.VectorMask(acqid, 'ctl_FT_Moncrieff_gill_licor_%1800')
    flux          = AIDA.VectorMask(acqid, 'flx_cov_wconh2o_2D_Eti_%1800')

    # appel de l'opérateur
    logger.info('*** appel de CorFlux_spectral')
    headers, datas, diag = CorFlux_spectral (cospectre, fct_transfert, flux)

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
