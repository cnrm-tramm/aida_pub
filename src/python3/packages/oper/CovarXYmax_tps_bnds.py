#!/usr/bin/env python3

"""
    ADC : Opérateur CovarXYmax_tps_bnds
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
def CovarXYmax_tps_bnds(X, Y, tolerance_mnq, time_out, tlag_min, tlag_max):
    """
    Calcule le maximum de covariance entre X et Y sur des intervalles donnés
    par time_bnds, en appliquant un décalage variant entre tlag_min et tlagmax.
    X et Y sont sur la même base de temps time_in.

    Input :
        X             : premier vecteur
        Y             : second vecteur
        tolerance_mnq : nombre de valeurs manquantes au-dela duquel on ne fera
                        pas le calcul
        time_out      : variable temps de sortie
        tlag_min      : borne minimale de variation du décalage temporel pour
                        le calcul du maximum de covariance (s)
        tlag_max      : borne maximale de variation du décalage temporel pour
                        le calcul du maximum de covariance (s)
    Output :
        cov           : covariance XY
        corr          : correlation XY
        nbsec         : nombre de secondes valides sur lequel la covariance a
                        été calculée (s)
        tlag          : decalage temporel au maximum de covariance (s)
        code_ret      : code de retour
        stats         : tableau des statistiques

    Auteur : @Météo-France CNRM/GMEI/TRAMM - May  2021
    """
    logger.debug("CovarXYmax_tps_bnds : debut")

    # récupération des arguments
    X_header     = X.attributes
    X_data       = X.data.data

    Y_header     = Y.attributes
    Y_data       = Y.data.data

    time_out_header = time_out.attributes
    time_out_data   = time_out.data.data

    # préparation des arguments pour la fonction de calcul
    time_in_data = X.timedata()
    acqid        = time_out.acq_id
    bnds         = AIDA.time_to_data_bnds(acqid, time_out.name)
    if bnds is None:
        raise Exception ("opérateur CovarXYmax_tps_bnds : problème de lecture " +
                         f"des bornes du vecteur '{time_out.name}'")

    # contrairement à ce que dit la heredoc, AIDA.time_to_data_bnds retourne
    # soit un np.array soit un np.masked_array...
    if isinstance(bnds, np.ma.core.MaskedArray):
        time_bnds = bnds.data
    elif isinstance(bnds, np.ndarray):
        time_bnds = bnds


    # appel de la fonction de calcul
    cov_data, corr_data, nbsec_data, tlag_data, code_ret, stats = \
        calcul.CovarXYmax_tps_bnds.CovarXYmax_tps_bnds(X_data,
                                                       Y_data,
                                                       time_in_data,
                                                       tolerance_mnq,
                                                       time_out_data,
                                                       time_bnds,
                                                       tlag_min,
                                                       tlag_max)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X.get_names()
    Y_fr_name, Y_en_name = Y.get_names()

    cov_header = default_out_header.copy()
    cov_header['name']         = f"Covariance {X_fr_name} . {Y_fr_name}"
    cov_header['english_name'] = f"Covariance {X_en_name} . {Y_en_name}"
    cov_header['unit']         = f"{X_header['unit']}*{Y_header['unit']}"
    cov_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    cov_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    cov_header['misval']       = f"{X_header['misval']}"

    corr_header = default_out_header.copy()
    corr_header['name']         = f"Correlation {X_fr_name} . {Y_fr_name}"
    corr_header['english_name'] = f"Correlation {X_en_name} . {Y_en_name}"
    corr_header['unit']         = f"{X_header['unit']}*{Y_header['unit']}"
    corr_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    corr_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    corr_header['misval']       = f"{X_header['misval']}"

    nbsec_header = default_out_header.copy()
    nbsec_header['name']         = f"Nombre de secondes pour le calcul de la covariance :  {X_fr_name} . {Y_fr_name}"
    nbsec_header['english_name'] = f"Number of seconds in calculation of covariance : {X_en_name} . {Y_en_name}"
    nbsec_header['unit']         = 's'
    nbsec_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    nbsec_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    nbsec_header['misval']       = f"{X_header['misval']}"
    nbsec_header['famille']      = 'controle'

    tlag_header = default_out_header.copy()
    tlag_header['name']         = f"Decalage temporel au maximum de covarianc :  {X_fr_name} . {Y_fr_name}"
    tlag_header['english_name'] = f"Timelag to maximize covariance : {X_en_name} . {Y_en_name}"
    tlag_header['unit']         = 's'
    tlag_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    tlag_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    tlag_header['misval']       = f"{X_header['misval']}"
    tlag_header['famille']      = 'controle'


    msg1 = f"time_orig in [{time_in_data[0]:g}, {time_in_data[-1]:g}] "
    msg2 = f"time_dest in [{time_out_data[0]:g}, {time_out_data[-1]:g}] "
    msg3 = f"nb_resu = {len(time_bnds)} " ### TODO : ce que voulait faire OP_CovarXYmax_tps_bnds ?
    msg4 = ""

    if int(code_ret[0]) == -1:
        msg4 =  "Les 2 periodes de temps ne se chevauchent pas : " +\
               f"le dernier temps d'origine ({time_in_data[-1]:g}) est avant le premier temps demande ({time_out_data[0]:g})"
    elif int(code_ret[0]) == -2:
        msg4 =  "Les 2 periodes de temps ne se chevauchent pas : " +\
               f"le premier temps d'origine ({time_in_data[0]:g}) est apres le dernier temps demande ({time_out_data[-1]:g})"

    msg5 = f"code_ret:{int(code_ret[0])}. Statistiques s: OK:{int(stats[0])}, 0:{int(stats[1])}, pas_assez:{int(stats[2])})."

    diag = {'CodeRet' : int(code_ret[0]),
            'DiagExec': f"CovarXYmax_tps_bnds : ({len(X_data)} ech.) " + \
                        msg1 + msg2 + msg3 + msg4 + msg5
           }

    return [cov_header                 , corr_header                 , nbsec_header                 , tlag_header                 ], \
           [cov_data.astype(np.float32), corr_data.astype(np.float32), nbsec_data.astype(np.float32), tlag_data.astype(np.float32)], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'CovarXYmax_tps_bnds': {
        'Args': [
           {'Id': 'X'            , 'categorie': 'VECTOR_IN'               },
           {'Id': 'Y'            , 'categorie': 'VECTOR_IN'               },
           {'Id': 'tolerance_mnq', 'categorie': 'COEFFICIENT'             },
           {'Id': 'time_out'     , 'categorie': 'VECTOR_IN'  , 'unit': 's'},
           {'Id': 'tlag_min'     , 'categorie': 'COEFFICIENT'             },
           {'Id': 'tlag_max'     , 'categorie': 'COEFFICIENT'             },
           {'Id': 'cov'          , 'categorie': 'VECTOR_OUT'              },
           {'Id': 'corr'         , 'categorie': 'VECTOR_OUT'              },
           {'Id': 'nbsec'        , 'categorie': 'VECTOR_OUT'              },
           {'Id': 'tlag'         , 'categorie': 'VECTOR_OUT'              },
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

    # CovarXYmax_tps_bnds(
    #   ven_u_Frc200_20,
    #   hum_conh2o_g_famous_Frc200_20,
    #   rft_time_REG_20,
    #   0.,
    #   rft_time_seq_0,
    #   $Arg5.time_bnds,
    #   $Arg5.NbVal,
    #   -1,
    #   1,
    #   flx_cov_wh2o_NT_0, flx_cor_wh2o_NT_0, ctl_flx_nbsec_wh2o_NT_0, ctl_tlag_wh2o_NT_0
    # )

    # sur de vrais vecteurs
    acqid = 'Ce210208'
    logger.info(f'=== {acqid}')
    X        = AIDA.VectorMask(acqid, 'ven_u_Frc200_20')
    Y        = AIDA.VectorMask(acqid, 'hum_conh2o_g_famous_Frc200_20')
    toler    = 0.
    time_out = AIDA.VectorMask(acqid, 'rft_time_seq_0')
    tlag_min = -1
    tlag_max =  1

    # appel de l'opérateur
    logger.info('*** appel de CovarXYmax_tps_bnds')
    headers, datas, diag = CovarXYmax_tps_bnds (X, Y, toler, time_out, tlag_min, tlag_max)

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
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
