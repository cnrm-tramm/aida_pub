#!/usr/bin/env python3

"""
    ADC : Opérateur PresenceNuageEch_tps_bnds
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
def PresenceNuageEch_tps_bnds(X1, X2, X3, tolerance_mnq, time_out, val_inv):
    """
    """
    logger.debug("PresenceNuageEch_tps_bnds : debut")

    # récupération des arguments
    X1_header = X1.attributes
    X1_data   = X1.data.data

    X2_header = X2.attributes
    X2_data   = X2.data.data

    X3_header = X3.attributes
    X3_data   = X3.data.data

    time_out_header = time_out.attributes
    time_out_data   = time_out.data.data

    # préparation des arguments pour la fonction de calcul
    # - récupération des données du vecteur temps de X1
    chaine_arg_sup = f"{val_inv}"
    time_in_data   = X1.timedata()

    # - récupération des time_bnds (bornes_temps) pour le vecteur time_out
    acqid     = time_out.acq_id
    bnds      = AIDA.time_to_data_bnds(acqid, time_out.name)
    if bnds is None:
        raise Exception ("opérateur PresenceNuageEch_tps_bnds : problème de lecture " +
                         f"des bornes du vecteur '{time_out.name}'")

    # contrairement à ce que dit la heredoc, AIDA.time_to_data_bnds retourne
    # soit un np.array soit un np.masked_array...
    if isinstance(bnds, np.ma.core.MaskedArray):
        time_bnds = bnds.data
    elif isinstance(bnds, np.ndarray):
        time_bnds = bnds

    # appel de la fonction de calcul
    fct_calcul = calcul.PresenceNuageEch_tps_bnds.fait_calcul_pres_nuage_tps_bnds
    VO_data, fct_ret, tab_stat = fct_calcul(X1_data,
                                            X2_data,
                                            X3_data,
                                            time_in_data,
                                            tolerance_mnq,
                                            time_out_data,
                                            time_bnds,
                                            np.array(list('calcule_presence_nuage')),
                                            # TODO : les fonctions de calcul attendent des trucs pourris à cause des appels C
                                            # MINE : 'calcule_moy',
                                            np.array(list(chaine_arg_sup)))
    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X1_fr_name, X1_en_name = X1.get_names()
    X2_fr_name, X2_en_name = X2.get_names()
    X3_fr_name, X3_en_name = X3.get_names()

    VO_header                 = default_out_header.copy()
    VO_header['name']         = f"Pourcentage de presence d'au moins une valeur de {X1_fr_name} ou {X2_fr_name} ou {X3_fr_name} et inferieure a un seuil sur la periode"
    VO_header['english_name'] = f"Percent of presence at least one value of {X1_en_name} or {X2_en_name} or {X3_en_name} inferior at a threhold during the periode"
    VO_header['unit']         = 'percent'
    VO_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    VO_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO_header['misval']       = f"{X1_header['misval']}"
    VO_header['format']       = f"{X1_header['format']}"
    VO_header['famille']      = f"{X1_header['famille']}"


    msg_1 =  "PresenceNuageEch_tps_bnds : "                          +\
            f"({len(X1_data)} ech.), "                               +\
            f"time_orig in [{time_in_data[0]},{time_in_data[-1]}], " +\
            f"time_dest in [{time_bnds[0][0]},{time_bnds[-1][1]}], " +\
            f"nb_resu:{len(VO_data)}"

    if fct_ret == -1:
        msg_2 =  "Les 2 periodes de temps ne se chevauchent pas. "          +\
	        f"Le dernier temps d'origine {time_in_data[-1]} est avant " +\
                f"le premier temps demandé {time_bnds[0][0]}"
    elif fct_ret == -2:
        msg_2 =  "Les 2 periodes de temps ne se chevauchent pas. "         +\
	        f"Le premier temps d'origine {time_in_data[0]} est apres " +\
                f"le dernier temps demandé {time_bnds[-1][1]}"
    else:
        msg_2 = f" OK: {int(fct_ret[0])} valeurs en sortie. Valeurs en sortie : " +\
                f"(OK:{int(tab_stat[0])}, zeros:{int(tab_stat[1])}, pas_assez:{int(tab_stat[2])})"
        # TODO MINE : msg_2 = f" OK: {fct_ret} valeurs en sortie. Valeurs en sortie : " +\
        # TODO MINE :         f"(OK:{tab_stat[0]}, zeros:{tab_stat[1]}, pas_assez:{tab_stat[2]})"
        # adc attend 0 si tout est OK
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
    'PresenceNuageEch_tps_bnds': {
        'Args': [
            {'Id': 'X1'           , 'categorie': 'VECTOR_IN'               },
            {'Id': 'X2'           , 'categorie': 'VECTOR_IN'               },
            {'Id': 'X3'           , 'categorie': 'VECTOR_IN'               },
            {'Id': 'tolerance_mnq', 'categorie': 'COEFFICIENT'             },
            {'Id': 'time_out'     , 'categorie': 'VECTOR_IN'  , 'unit': 's'},
            {'Id': 'val_inv'      , 'categorie': 'COEFFICIENT'             },
            {'Id': 'X_out'        , 'categorie': 'VECTOR_OUT'              },
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
    # PresenceNuageEch_tps_bnds (
    #   alt_hbn1_dso_cl31_Eti_%60,
    #   alt_hbn2_dso_cl31_Eti_%60,
    #   alt_hbn3_dso_cl31_Eti_%60,
    #   rft_time_REG_%60,
    #   0.5*1800/60.,
    #   rft_time_bnds_reg_%1800,
    #   $Arg6.time_bnds,
    #   $Arg6.NbVal,
    #   7800.,
    # alt_hbn_nuage_dso_cl31_%60_per_%1800)

    acqid = 'Tf220123'
    logger.info(f'=== {acqid}')
    X1            = AIDA.VectorMask(acqid, 'alt_hbn1_dso_cl31_Eti_%60')
    X2            = AIDA.VectorMask(acqid, 'alt_hbn2_dso_cl31_Eti_%60')
    X3            = AIDA.VectorMask(acqid, 'alt_hbn3_dso_cl31_Eti_%60')
    tolerance_mnq = 0.5*1800/60. 
    time_out      = AIDA.VectorMask(acqid, 'rft_time_bnds_reg_%1800')
    val_inv       = 7800.

    # appel de l'opérateur simplifié
    logger.info('*** opérateur simplifié : PresenceNuageEch_tps_bnds')
    headers, datas, diag = PresenceNuageEch_tps_bnds(X1, X2, X3, tolerance_mnq, time_out, val_inv)

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
