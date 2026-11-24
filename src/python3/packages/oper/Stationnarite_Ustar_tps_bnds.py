#!/usr/bin/env python3

"""
ADC :   Opérateur Stationnarite_Ustar_tps_bnds : calcul de la stationnarité
        de USTAR sur des intervalles de temps.

        Cette opérateur calcule le rapport suivant :
        Rapport = [ moyenne(USTAR sur T1) - USTAR sur T2 ] / ( USTAR sur T2 ) 
        avec T2=intervalle de temps de chaque time_bnds
             T1=T2/nsub
        Foken considère que si Rapport < 30 % les conditions sont stationnaires
        
        REFERENCES
            T. Foken, Micrometeorology, 2008 
            Ed Spinger, ISBN : 978-3-540-74665-2
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
def Stationnarite_Ustar_tps_bnds(U, V, W, nsub, tolerance_mnq, time_out):
    """
        Calcul de la stationnarité du ustar sur des périodes définies par 
        le time_bnds avec une tolérance sur le pourcentage de données présentes 
        sur les périodes et sous-périodes de calcul.
        nsub est le nombre de sous-périodes utilisé pour le calcul de la 
        stationnarité.
    """
    logger.debug("Stationnarite_Ustar_tps_bnds : debut")

    # récupération des arguments
    U_header = U.attributes
    U_data   = U.data #on utilise le maskedArray
    V_header = V.attributes
    V_data   = V.data #on utilise le maskedArray
    W_header = W.attributes
    W_data   = W.data #on utilise le maskedArray

    time_out_header = time_out.attributes
    time_out_data   = time_out.data.data

    # préparation des arguments pour la fonction de calcul
    # - récupération des données du vecteur temps de X
    time_in_data = U.timedata()

    # - récupération des time_bnds (bornes_temps) pour le vecteur time_out
    acqid     = time_out.acq_id
    bnds      = AIDA.time_to_data_bnds(acqid, time_out.name)
    if bnds is None:
        raise Exception ("opérateur Stationnarite_Ustar_tps_bnds : problème de lecture " +
                         f"des bornes du vecteur '{time_out.name}'")

    # contrairement à ce que dit la heredoc, AIDA.time_to_data_bnds retourne
    # soit un np.array soit un np.masked_array...
    if isinstance(bnds, np.ma.core.MaskedArray):
        time_bnds = bnds.data
    elif isinstance(bnds, np.ndarray):
        time_bnds = bnds

    # appel de la fonction de calcul
    VO_data, fct_ret, tab_stat = calcul.Stationnarite_Ustar_tps_bnds.fct_Stationnarite_Ustar_tps_bnds(
                                        U_data,
                                        V_data,
                                        W_data,
                                        time_in_data,
                                        nsub,
                                        tolerance_mnq,
                                        time_out_data,
                                        time_bnds)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    U_fr_name, U_en_name               = U.get_names()
    V_fr_name, V_en_name               = V.get_names()
    W_fr_name, W_en_name               = W.get_names()
    time_out_fr_name, time_out_en_name = time_out.get_names()

    VO_header                 = default_out_header.copy()
    VO_header['name']         = f"Stationnarité de Ustar calculé à partir de  {U_fr_name} et {V_fr_name} et {W_fr_name} synchronise sur {time_out_fr_name}"
    VO_header['english_name'] = f"Ustar stationnarity computed with {U_en_name} and {V_fr_name} and {W_fr_name} synchronised on {time_out_en_name}"
    VO_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO_header['unit']         = f"unitless"
    VO_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    VO_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO_header['misval']       = f"{U_header['misval']}"
    VO_header['format']       = f"{U_header['format']}"

    msg_1 =  "Stationnarite_Ustar_tps_bnds : "                      +\
            f"({len(U_data)} echant_x, {len(V_data)} echant_y, {len(W_data)} echant_w) "      +\
            f"time_orig in [{time_in_data[0]},{time_in_data[-1]}], "   +\
            f"time_dest in [{time_out_data[0]},{time_out_data[-1]}], " +\
            f"nb_resu:{len(VO_data)}"

    if fct_ret == -1:
        msg_2 =  "Les 2 periodes de temps ne se chevauchent pas. "          +\
	        f"Le dernier temps d'origine {time_in_data[-1]} est avant " +\
                f"le premier temps demandé {time_out_data[0]}"
    elif fct_ret == -2:
        msg_2 =  "Les 2 periodes de temps ne se chevauchent pas. "         +\
	        f"Le premier temps d'origine {time_in_data[0]} est apres " +\
                f"le dernier temps demandé {time_out_data[-1]}"
    else:
        msg_2 = f" Retour: {int(fct_ret)}. Valeurs en sortie : " +\
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
    'Stationnarite_Ustar_tps_bnds': {
        'Args': [
            {'Id': 'U'            , 'categorie': 'VECTOR_IN'               },
            {'Id': 'V'            , 'categorie': 'VECTOR_IN'               },
            {'Id': 'W'            , 'categorie': 'VECTOR_IN'               },
            {'Id': 'nsub'         , 'categorie': 'COEFFICIENT'             },
            {'Id': 'tolerance_mnq', 'categorie': 'COEFFICIENT'             },
            {'Id': 'time_out'     , 'categorie': 'VECTOR_IN'  , 'unit': 's'},
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
    acqid = 'Pl210226'
    logger.info(f'=== {acqid}')
    U             = AIDA.VectorMask(acqid, 'ven_u_gillh_Frc200_2D_20')
    V             = AIDA.VectorMask(acqid, 'ven_v_gillh_Frc200_2D_20')
    W             = AIDA.VectorMask(acqid, 'ven_w_gillh_Frc200_2D_20')
    nsub = 6
    tolerance_mnq = 50
    time_out      = AIDA.VectorMask(acqid, 'rft_time_REG_%1800')

    # appel de l'opérateur simplifié
    logger.info('*** opérateur simplifié : Stationnarite_Ustar_tps_bnds')
    headers, datas, diag = Stationnarite_Ustar_tps_bnds(U, V, W, nsub, tolerance_mnq, time_out)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in header.items():
            if key in ['bornes', 'obs_min', 'obs_max'] and len(value) > 60:
                logger.info(f"  - {key:15s} = {value[:60]}...")
            else:
                logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data = {data[:]}")
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
    input("...[ENTER] pour continuer ")
