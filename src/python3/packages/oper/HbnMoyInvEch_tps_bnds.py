#!/usr/bin/env python3

"""
    ADC : Opérateur HbnMoyInvEch_tps_bnds
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
def HbnMoyInvEch_tps_bnds(X1, X2, X3, tolerance_mnq, time_out, val_inv, val_repl, toler_invalid):
    """
    """
    logger.debug("HbnMoyInvEch_tps_bnds : debut")

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
    chaine_arg_sup = f"{val_inv}:{val_repl}:{toler_invalid}"
    time_in_data   = X1.timedata()

    # - récupération des time_bnds (bornes_temps) pour le vecteur time_out
    acqid     = time_out.acq_id
    bnds      = AIDA.time_to_data_bnds(acqid, time_out.name)
    if bnds is None:
        raise Exception ("opérateur HbnMoyInvEch_tps_bnds : problème de lecture " +
                         f"des bornes du vecteur '{time_out.name}'")

    # contrairement à ce que dit la heredoc, AIDA.time_to_data_bnds retourne
    # soit un np.array soit un np.masked_array...
    if isinstance(bnds, np.ma.core.MaskedArray):
        time_bnds = bnds.data
    elif isinstance(bnds, np.ndarray):
        time_bnds = bnds

    # appel de la fonction de calcul
    fct_calcul = calcul.HbnMoyInvEch_tps_bnds.fait_calcul_tps_bnds_3couches
    VO1_data , VO2_data , VO3_data, \
    fct_ret, \
    tab_stat1, tab_stat2, tab_stat3  = fct_calcul(X1_data,
                                                  X2_data,
                                                  X3_data,
                                                  time_in_data,
                                                  tolerance_mnq,
                                                  time_out_data,
                                                  time_bnds,
                                                  np.array(list('calcule_moy_3couches')),
                                                  np.array(list(chaine_arg_sup)))
    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X1_fr_name, X1_en_name = X1.get_names()
    X2_fr_name, X2_en_name = X2.get_names()
    X3_fr_name, X3_en_name = X3.get_names()

    time_out_fr_name = f"{time_out_header.get('name'        , None)}"
    time_out_en_name = f"{time_out_header.get('english_name', None)}"

    VO1_header                 = default_out_header.copy()
    VO1_header['name']         = f"Moyenne hors valeurs invalides de {X1_fr_name} synchronise sur {time_out_fr_name} sans changement de couches"
    VO1_header['english_name'] = f"Mean by period without invalid values of {X1_en_name} synchronised on {time_out_en_name} without change of layers"
    VO1_header['unit']         = f"{X1_header['unit']}"
    VO1_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    VO1_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO1_header['misval']       = f"{X1_header['misval']}"
    VO1_header['format']       = f"{X1_header['format']}"
    VO1_header['famille']      = f"{X1_header['famille']}"

    VO2_header                 = default_out_header.copy()
    VO2_header['name']         = f"Moyenne hors valeurs invalides de {X2_fr_name} synchronise sur {time_out_fr_name} sans changement de couches"
    VO2_header['english_name'] = f"Mean without invalid values of {X2_en_name} synchronised on {time_out_en_name} without change of layers"
    VO2_header['unit']         = f"{X2_header['unit']}"
    VO2_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    VO2_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO2_header['misval']       = f"{X2_header['misval']}"
    VO2_header['format']       = f"{X2_header['format']}"
    VO2_header['famille']      = f"{X2_header['famille']}"

    VO3_header                 = default_out_header.copy()
    VO3_header['name']         = f"Moyenne hors valeurs invalides de {X3_fr_name} synchronise sur {time_out_fr_name} sans changement de couches"
    VO3_header['english_name'] = f"Mean without invalid values of {X3_en_name} synchronised on {time_out_en_name} without change of layers"
    VO3_header['unit']         = f"{X3_header['unit']}"
    VO3_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    VO3_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO3_header['misval']       = f"{X3_header['misval']}"
    VO3_header['format']       = f"{X3_header['format']}"
    VO3_header['famille']      = f"{X3_header['famille']}"


    msg_1 =  "HbnMoyInvEch_tps_bnds : "                              +\
            f"({len(X1_data)} ech.), "                               +\
            f"time_orig in [{time_in_data[0]},{time_in_data[-1]}], " +\
            f"time_dest in [{time_bnds[0][0]},{time_bnds[-1][1]}], " +\
            f"nb_resu:{len(VO1_data)}"

    if fct_ret == -1:
        msg_2 =  "Les 2 periodes de temps ne se chevauchent pas. "          +\
	        f"Le dernier temps d'origine {time_in_data[-1]} est avant " +\
                f"le premier temps demandé {time_bnds[0][0]}"
    elif fct_ret == -2:
        msg_2 =  "Les 2 periodes de temps ne se chevauchent pas. "         +\
	        f"Le premier temps d'origine {time_in_data[0]} est apres " +\
                f"le dernier temps demandé {time_bnds[-1][1]}"
    else:
        msg_2 = f" OK: {int(fct_ret[0])} valeurs en sortie. Valeurs en sortie : "                       +\
                f"(OK1:{int(tab_stat1[0])}, zeros:{int(tab_stat1[1])}, pas_assez:{int(tab_stat3[2])}) " +\
                f"(OK2:{int(tab_stat2[0])}, zeros:{int(tab_stat2[1])}, pas_assez:{int(tab_stat3[2])}) " +\
                f"(OK3:{int(tab_stat3[0])}, zeros:{int(tab_stat3[1])}, pas_assez:{int(tab_stat3[2])})"
        fct_ret = 0

    diag = {'CodeRet' : fct_ret,
            'DiagExec': f"{msg_1}.{msg_2}"
           }

    return [VO1_header                 , VO2_header                 , VO3_header                  ], \
           [VO1_data.astype(np.float32), VO2_data.astype(np.float32), VO3_data.astype(np.float32) ], \
           diag




#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'HbnMoyInvEch_tps_bnds': {
        'Args': [
            {'Id': 'X1'            , 'categorie': 'VECTOR_IN'  },
            {'Id': 'X2'            , 'categorie': 'VECTOR_IN'  },
            {'Id': 'X3'            , 'categorie': 'VECTOR_IN'  },
            {'Id': 'tolerance_mnq' , 'categorie': 'COEFFICIENT'},
            {'Id': 'time_out'      , 'categorie': 'VECTOR_IN'  , 'unit': 's'},
            {'Id': 'val_inv'       , 'categorie': 'COEFFICIENT'},
            {'Id': 'val_repl'      , 'categorie': 'COEFFICIENT'},
            {'Id': 'toler_invalid' , 'categorie': 'COEFFICIENT'},
            {'Id': 'X1_out'        , 'categorie': 'VECTOR_OUT' },
            {'Id': 'X2_out'        , 'categorie': 'VECTOR_OUT' },
            {'Id': 'X3_out'        , 'categorie': 'VECTOR_OUT' },
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
    # HbnMoyInvEch_tps_bnds (
    #   alt_hbn1_dso_cl31_Eti_%60,
    #   alt_hbn2_dso_cl31_Eti_%60,
    #   alt_hbn3_dso_cl31_Eti_%60,
    #   rft_time_REG_%60,
    #   0.5*1800/60.,
    #   rft_time_bnds_reg_%1800,
    #   $Arg6.time_bnds,
    #   $Arg6.NbVal,
    #   7800.,
    #   -99.,
    #   0.5,
    #   alt_hbn1_dso_cl31_%60_Mhbn_%1800, alt_hbn2_dso_cl31_%60_Mhbn_%1800, alt_hbn3_dso_cl31_%60_Mhbn_%1800)


    acqid = 'Tf220123'
    logger.info(f'=== {acqid}')
    X1            = AIDA.VectorMask(acqid, 'alt_hbn1_dso_cl31_Eti_%60')
    X2            = AIDA.VectorMask(acqid, 'alt_hbn2_dso_cl31_Eti_%60')
    X3            = AIDA.VectorMask(acqid, 'alt_hbn3_dso_cl31_Eti_%60')
    tolerance_mnq = 0.5*1800/60.
    time_out      = AIDA.VectorMask(acqid, 'rft_time_bnds_reg_%1800')
    val_inv       = 7800.
    val_repl      = -99.
    toler_invalid = 0.5

    # appel de l'opérateur simplifié
    logger.info('*** opérateur simplifié : HbnMoyInvEch_tps_bnds')
    headers, datas, diag = HbnMoyInvEch_tps_bnds(X1, X2, X3, tolerance_mnq, time_out, val_inv, val_repl, toler_invalid)

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
