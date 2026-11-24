#!/usr/bin/env python3

"""
    ADC : Opérateur Covar_XY_max
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
def Covar_XY_max(X, Y, Tint, tlag_min, tlag_max):
    """
    Compute maximum covariance between X and Y with timelag varying in
    tlag_min, tlagmax.

    Input :
        rsurg : "constante" r/g.
        X        : premier vecteur
        Y        : second vecteur
        Tint     : Temps d'intégration pour le calcul du flux (s)
        tlag_min : Borne minimale de variation du décalage temporel pour le
                   calcul du maximum de covariance
        tlag_max : Borne maximale de variation du décalage temporel pour le
                   calcul du maximum de covariance

    Output :
        Cov_xy      : Covariance.
        Cor_xy      : Correlation.
        Nbsec_valid : nombre de secondes valides sur lequel la covariance a
                      été calculée (s).
        tlag        : decalage temporel au maximum de covariance (s).

    Auteur : @Météo-France CNRM/GMEI/TRAMM
    W. Maurel
    le 13/08/2020
    """
    logger.debug("Covar_XY_max : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    Y_header = Y.attributes
    Y_data   = Y.data.data


    # préparation des arguments pour la fonction de calcul
    # Fe : fréquence d'échantillonnage des données (Hz)
    Fe        = float(X_header['freq_ech'])

    # appel de la fonction de calcul
    cov_data, corr_data, nbsec_data, tlag_data = \
        calcul.Covar_XY_max.Covar_XY_max(X_data, Y_data, Fe, Tint, tlag_min, tlag_max)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X.get_names()
    Y_fr_name, Y_en_name = Y.get_names()

    if Tint >0.:
        ref_time = f"{X_header['ref_time']}_Med_%{int(Tint)}"
    else:
        ref_time = f"{X_header['ref_time']}_Med_{int(round(1/Tint))}"
    logger.warning(f"le vecteur temps '{ref_time}' existe-t-il ?")

    freq_ech = f"{1./Tint}"

    cov_header                  = default_out_header.copy()
    cov_header['name']          = f"Covariance {X_fr_name} . {Y_fr_name}"
    cov_header['english_name']  = f"Covariance {X_en_name} . {Y_en_name}"
    cov_header['unit']          = f"{X_header['unit']}.{Y_header['unit']}"
    cov_header['freq_ech']      = freq_ech
    cov_header['ref_time']      = ref_time
    cov_header['misval']        = f"{X_header['misval']}"

    corr_header                 = default_out_header.copy()
    corr_header['name']         = f"Correlation {X_fr_name} . {Y_fr_name}"
    corr_header['english_name'] = f"Correlation {X_en_name} . {Y_en_name}"
    corr_header['unit']         = f"{X_header['unit']}.{Y_header['unit']}"
    corr_header['freq_ech']     = freq_ech
    corr_header['ref_time']     = ref_time
    corr_header['misval']       = f"{X_header['misval']}"

    nbsec_header                = default_out_header.copy()
    nbsec_header['name']        = f"Nombre de secondes pour le calcul de la covariance : " +\
                                  f"{X_fr_name} . {Y_fr_name}"
    nbsec_header['english_name']= f"Number of seconds in calculation of covariance : " +\
                                  f"Correlation {X_en_name} . {Y_en_name}"
    nbsec_header['unit']        =  "s"
    nbsec_header['freq_ech']    = freq_ech
    nbsec_header['ref_time']    = ref_time
    nbsec_header['misval']      = f"{X_header['misval']}"
    nbsec_header['famille']     =  "controle"

    tlag_header                 = default_out_header.copy()
    tlag_header['name']         = f"Decalage temporel au maximum de covariance : " +\
                                  f"{X_fr_name} . {Y_fr_name}"
    tlag_header['english_name'] = f"Timelag to maximize covariance : " +\
                                  f"Correlation {X_en_name} . {Y_en_name}"
    tlag_header['unit']         =  "s"
    tlag_header['freq_ech']     = freq_ech
    tlag_header['ref_time']     = ref_time
    tlag_header['misval']       = f"{X_header['misval']}"
    tlag_header['famille']      =  "controle"


    diag = {'CodeRet' : 0,
            'DiagExec': f"Covar_XY_max : ({len(X_data)} ech.)"
           }

    return [cov_header, corr_header, nbsec_header, tlag_header], \
           [cov_data  , corr_data  , nbsec_data  , tlag_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Covar_XY_max': {
        'Args': [
            {'Id': 'X'       , 'categorie': 'VECTOR_IN'  },
            {'Id': 'Y'       , 'categorie': 'VECTOR_IN'  },
            {'Id': 'Tint'    , 'categorie': 'COEFFICIENT'},
            {'Id': 'tlag_min', 'categorie': 'COEFFICIENT'},
            {'Id': 'tlag_max', 'categorie': 'COEFFICIENT'},
            {'Id': 'Cov'     , 'categorie': 'VECTOR_OUT' },
            {'Id': 'Corr'    , 'categorie': 'VECTOR_OUT' },
            {'Id': 'NbSec'   , 'categorie': 'VECTOR_OUT' },
            {'Id': 'Tlag'    , 'categorie': 'VECTOR_OUT' },
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


    # Covar_XY_max ( ven_w_gill_Frc200_2D_20, hum_conh2o_licor_Frc200_20, 1800,
    #               -0.5, 0.5, flx_cov_wconh2o_2D_%1800,
    #                flx_corr_wconh2o_2D_%1800, ctl_flx_nbsec_wconh2o_2D_%1800,
    #                ctl_flx_tlag_wconh2o_2D_%1800 )

    # sur de vrais vecteurs
    acqid = 'Tf210001'
    logger.info(f'=== {acqid}')
    X          = AIDA.VectorMask(acqid, 'ven_w_gill_Frc200_2D_20')
    Y          = AIDA.VectorMask(acqid, 'hum_conh2o_licor_Frc200_20')
    Tint       = 1800
    tlag_min   = -0.5
    tlag_max   = 0.5

    # appel de l'opérateur
    logger.info('*** appel de Covar_XY_max')
    headers, datas, diag = Covar_XY_max (X, Y, Tint, tlag_min, tlag_max)

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
