#!/usr/bin/env python3

"""
    ADC : Opérateur Filtre_spectral_1D
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
def Filtre_spectral_1D(PrB, A, zmin, extrap_typ):
    """
    Fonction de filtrage des fréquences pour le traitement des données du
    lidar Cimel.

    Input :
        PrB        : signal du lidar
        A          : % des fréquences filtrées
                     [0, 1] : 0 correspond à aucun filtrage.
        zmin       : Altitude fin extrapolation
        extrap_typ : type d'exprapolation
                     ['cst', 'lin']
        flux       : flux to be corrected

    Output :
        X_f        : donnée  lidar filtrées et extrapolées.

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Febr 2018

    sources :
    script scilab ecrit par le LOA.
    """
    logger.debug("Filtre_spectral_1D : debut")

    # récupération des arguments
    PrB_header     = PrB.attributes
    PrB_data       = PrB.data.data


    # préparation des arguments pour la fonction de calcul
    #  str_bornes : $Arg1.bornes
    str_bornes = PrB_header['bornes']

    # appel de la fonction de calcul
    X_f_data = \
        calcul.Filtre_spectral_1D.Filtre_spectral_1D(PrB_data, A, str_bornes, zmin, extrap_typ)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    X_f_header = default_out_header.copy()
    X_f_header['name']         = ''
    X_f_header['english_name'] = ''
    X_f_header['unit']         = f"{PrB_header['unit']}"
    X_f_header['freq_ech']     = f"{PrB_header['freq_ech']}"
    X_f_header['ref_time']     = f"{PrB_header['ref_time']}"
    X_f_header['misval']       = f"{PrB_header['misval']}"
    X_f_header['dim_array']    = f"{PrB_header['dim_array']}"
    X_f_header['bornes']       = f"{PrB_header['bornes']}"
    X_f_header['unit_bornes']  = f"{PrB_header['unit_bornes']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"Filtre_spectral_1D : ({len(PrB_data)} ech.)"
           }

    return [X_f_header], \
           [X_f_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Filtre_spectral_1D': {
        'Args': [
           {'Id': 'PrB'       , 'categorie': 'VECTOR_IN'   },
           {'Id': 'A'         , 'categorie': 'COEFFICIENT' },
           {'Id': 'zmin'      , 'categorie': 'COEFFICIENT' },
           {'Id': 'extrap_typ', 'categorie': 'COEFFICIENT' },
           {'Id': 'X_f'       , 'categorie': 'VECTOR_OUT'  },
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

    # Filtre_spectral_1D (
    #   opt_dclid_raw_%60,
    #   $Arg1.array_dim,
    #   0.7,
    #   $Arg1.bornes,
    #   300,
    #   "lin",
    #   opt_pr2_lid_filtre_%60
    #)

    # sur de vrais vecteurs
    acqid = 'fs200013'
    logger.info(f'=== {acqid}')
    PrB        = AIDA.VectorMask(acqid, 'opt_dclid_raw_%60')
    A          = 0.7
    zmin       = 300
    extrap_typ = 'lin'

    # appel de l'opérateur
    logger.info('*** appel de Filtre_spectral_1D')
    headers, datas, diag = Filtre_spectral_1D (PrB, A, zmin, extrap_typ)

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
