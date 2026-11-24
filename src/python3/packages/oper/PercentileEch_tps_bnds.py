#!/usr/bin/env python3

"""
    ADC : Opérateur PercentileEch_tps_bnds: calcul du percentile avec le taux passé en parametre  sur un time_bnds
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

def PercentileEch_tps_bnds(X, tolerance_mnq, time_out, percentile):
    """
    calcul du percentile d'un vecteur sur un time_bnd donné
    il faut que le vecteur temps final ait un time bound 
    """
    logger.debug("PercentileEch_tps_bnds : debut")

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    time_out_header = time_out.attributes
    time_out_data   = time_out.data.data

    # préparation des arguments pour la fonction de calcul
    # - récupération des données du vecteur temps de X
    chaine_arg_sup = f"{percentile}"
    time_in_data   = X.timedata()

    # - récupération des time_bnds (bornes_temps) pour le vecteur time_out
    acqid     = time_out.acq_id
    bnds      = AIDA.time_to_data_bnds(acqid, time_out.name)
    if bnds is None:
        raise Exception ("opérateur PercentileEch_tps_bnds : problème de lecture " +
                         f"des bornes du vecteur '{time_out.name}'")

    # contrairement à ce que dit la heredoc, AIDA.time_to_data_bnds retourne
    # soit un np.array soit un np.masked_array...
    if isinstance(bnds, np.ma.core.MaskedArray):
        time_bnds = bnds.data
    elif isinstance(bnds, np.ndarray):
        time_bnds = bnds

    # appel de la fonction de calcul
    VO_data, fct_ret, tab_stat = calcul.PercentileEch_tps_bnds.fct_PercentileEch_tps_bnds(X_data,
                                            time_in_data,
                                            tolerance_mnq,
                                            time_out_data,
                                            time_bnds,
                                            chaine_arg_sup)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name               = X.get_names()
    time_out_fr_name, time_out_en_name = time_out.get_names()

    VO_header                 = default_out_header.copy()
    VO_header['name']         = f"Percentile par periode de {X_fr_name} synchronise sur {time_out_fr_name}"
    VO_header['english_name'] = f"Percentile by period of {X_en_name} synchronised on {time_out_en_name}"
    VO_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO_header['unit']         = f"{X_header['unit']}"
    VO_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    VO_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO_header['misval']       = f"{X_header['misval']}"
    VO_header['format']       = f"{X_header['format']}"

    msg_1 =  "PercentileEch_tps_bnds : "                                    +\
            f"({len(X_data)} ech.), "                             +\
            f"time_orig in [{time_in_data[0]},{time_in_data[-1]}], " +\
            f"time_dest in [{time_out_data[0]},{time_out_data[-1]}], " +\
            f"nb_resu:{len(VO_data)}"

    if fct_ret == -1:
        msg_2 =  "Les 2 periodes de temps ne se chevauchent pas. "     +\
	        f"Le dernier temps d'origine {time_in_data[-1]} est avant " +\
                f"le premier temps demandé {time_out_data[0]}"
    elif fct_ret == -2:
        msg_2 =  "Les 2 periodes de temps ne se chevauchent pas. "    +\
	        f"Le premier temps d'origine {time_in[0]} est apres " +\
                f"le dernier temps demandé {time_out_data[-1]}"
    else:
        msg_2 = f" OK: {int(fct_ret[0])} valeurs en sortie. Valeurs en sortie : " +\
                f"(OK:{int(tab_stat[0])}, zeros:{int(tab_stat[1])}, pas_assez:{int(tab_stat[2])})"
        fct_ret = 0

    diag = {'CodeRet' : fct_ret,
            'DiagExec': f"{msg_1}.{msg_2}"
           }

    return [VO_header], \
           [VO_data.astype(np.float32)  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'PercentileEch_tps_bnds': {
        'Args': [
            {'Id': 'X'            , 'categorie': 'VECTOR_IN'               },
            {'Id': 'tolerance_mnq', 'categorie': 'COEFFICIENT'             },
            {'Id': 'time_out'     , 'categorie': 'VECTOR_IN'  , 'unit': 's'},
            {'Id': 'percentile'   , 'categorie': 'COEFFICIENT'             },
            {'Id': 'X_out '       , 'categorie': 'VECTOR_OUT'              },
        ],
        'control_reftime': 'off',
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
    # PercentileEch_tps_bnds (
    #  opt_pom_dso_tr30_Eti_%60,
    #  rft_time_REG_%60,
    #  0.,
    #  rft_time_bnds_reg_%1800,
    #  $Arg4.time_bnds,
    #  $Arg4.NbVal,
    #   25.,
    #  opt_pom_dso_tr30_%60_p25_2_%1800)
    acqid = 'Tf220100'
    logger.info(f'=== {acqid}')
    X             = AIDA.VectorMask(acqid, 'opt_pom_dso_tr30_Eti_%60')
    tolerance_mnq = 0.
    time_out      = AIDA.VectorMask(acqid, 'rft_time_bnds_reg_%1800')
    percentile    = 25.

    # appel de l'opérateur simplifié
    logger.info('*** opérateur simplifié : PercentileEch_tps_bnds')
    headers, datas, diag = PercentileEch_tps_bnds(X, tolerance_mnq, time_out, percentile)

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
    input("...[ENTER] pour continuer ")
