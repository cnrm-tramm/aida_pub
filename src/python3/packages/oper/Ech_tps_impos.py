#!/usr/bin/env python3

"""
    ADC : Operateur Ech_tps_impos: echantillonnage d'une variable sur une base de temps reguliere
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
# Fonction Operateur
#
# Les arguments sont ceux de la ligne d'instruction ADC lue dans le .fil
# ***SANS*** les noms des VECTOR/DIR_OUT
#
# Les arguments de type VECTOR/DIR_IN recus sont des AIDA.VectorMask.
#
# L'operateur :
#   - prepare les arguments pour appeller la fonction de calcul
#   - appelle la fonction de calcul
#   - prepare le(s) header(s) du/des vecteurs de retour.
#   - retourne : [headers], [data], {'CodeRet' : int()>= 0, 'DiagExec': str()}
#
# NOTE : AIDAcalc et AIDA.Vector mettront a jour les attributs :
#           #hdr_name, date_creation, fct_origine et vol...
#        des headers avant d'ecrire les vecteurs.
#==============================================================================



def Ech_tps_impos (X, ecart_max, time_out) :

    """
    Echantillonnage d'une variable sur une base de temps reguliere

    Input :
        X         : Vecteur sur une base de temps d'entree
        ecart_max : ecart temporel maximum tolere (s)
        time_out  : base de temps reguliere de sortie
    """
    #recuperation des arguments
    X_header = X.attributes
    X_data = X.data.data
    
    time_out_header = time_out.attributes
    time_out_data   = time_out.data.data
    
    #Preparation des arguments pour la fonction de calcul
    # - recuperation des donnees du vecteur de X
    time_in_data = X.timedata()
                             
    #Appel de la fonction de calcul
    VO_data, fct_ret = calcul.Ech_tps_impos.fct_Ech_tps_impos(X_data,
                                                     time_in_data,
                                                     ecart_max,
                                                     time_out_data)
    
    # preparation du retour
    # ATTENTION : les champs 'name' et 'english name' ne sont pas obligatoires
    # => passer par la methode 'get_names' des vecteurs
    X_fr_name, X_en_name               = X.get_names()
    
    VO_header                 = default_out_header.copy()
    VO_header['name']         = f"{X_fr_name} synchronise sur temps regulier"
    VO_header['english_name'] = f"{X_en_name} sampled on regular time"
    VO_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO_header['unit']         = f"{X_header['unit']}"
    if VO_data.ndim > 1 :
        VO_header['bornes']       = f"{X_header['bornes']}"
        VO_header['unit_bornes']  = f"{X_header['unit_bornes']}"
    VO_header['freq_ech']     = f"{time_out_header['freq_ech']}"
    VO_header['ref_time']     = f"{time_out_header['#hdr_name']}"
    VO_header['misval']       = f"{X_header['misval']}"
    VO_header['format']       = f"{X_header['format']}"

    msg_1 =  "Ech_tps_impos : "                                        +\
            f"({X_data.shape} ech.), "                                  +\
            f"time_orig in [{time_in_data[0]},{time_in_data[-1]}], "   +\
            f"time_dest in [{time_out_data[0]},{time_out_data[-1]}], " +\
            f"nb_resu:{VO_data.shape}"

    if fct_ret == -1:
        msg_2 =  f"ecart_max < 0 (ecart_max = {ecart_max}). " +\
                 f"Ca n'a pas de sens."
    else:
        msg_2 = f"OK"
        fct_ret = 0

    diag = {'CodeRet' : fct_ret,
            'DiagExec': f"{msg_1}.{msg_2}"
           }

    return [VO_header], \
           [VO_data.astype(np.float32)  ], \
           diag

#==============================================================================
# Description des arguments attendus par l'operateur.
#==============================================================================
desc_oper = {
    'Ech_tps_impos': {
        'Args': [
            {'Id': 'X'            , 'categorie': 'VECTOR_IN'               },
            {'Id': 'ecart_max'    , 'categorie': 'COEFFICIENT'             },
            {'Id': 'time_out'     , 'categorie': 'VECTOR_IN'               },
            {'Id': 'X_out'        , 'categorie': 'VECTOR_OUT'              },
        ],
        'control_reftime': 'off',
    },
}


#==============================================================================
# Test de l'operateur
#==============================================================================
if __name__ == '__main__':

    from fct_messages import wait_user

    # ici, on est en direct, et non pas importe par adc
    # => le logger 'adc' n'existe pas
    # => on definit un logger basic
    if len(logger.handlers) == 0:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')


    # OPERATEUR SIMPLIFIE : sur de vrais vecteurs
    # 1D data
    acqid = 'Ce210183'
    logger.info(f'=== {acqid}')
    X             = AIDA.VectorMask(acqid, 'ven_w_gillv3_cal_50')
    ecart_max     = 1/50
    time_out      = AIDA.VectorMask(acqid, 'rft_time_REG_50')
    
    # 2D data
    acqid = 'Ce210185'
    logger.info(f'=== {acqid}')
    X             = AIDA.VectorMask(acqid, 'ven_dd_windcube180_cal_%4')
    ecart_max     = 0.5*4
    time_out      = AIDA.VectorMask(acqid, 'rft_time_REG_%4')
    

    # 3D data
    acqid = 'pa230324'
    logger.info(f'=== {acqid}')
    X             = AIDA.VectorMask(acqid, 'tpr_TB_BLB_MWRL1_cal_%600')
    ecart_max     = 0.5*600
    time_out      = AIDA.VectorMask(acqid, 'rft_time_REG_%600')


    # appel de l'operateur simplifie
    logger.info('*** operateur simplifie : Ech_tps_impos')

    headers, datas, diag = Ech_tps_impos(X, ecart_max, time_out)

    # resultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise a jour par ADC et AIDA.py *** \n")
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
