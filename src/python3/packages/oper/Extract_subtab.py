#!/usr/bin/env python3

"""
    ADC : Opérateur Extract_subtab
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
def Extract_subtab(X_in, dimension,ax):
    """
    Extrait un sous tableau (ligne ou array en fonction de la dimension du vecteur d'origine)

    Input :
        X_in  : tableau d'entrée
        dimension : indice du tableau que l'on souhaite supprimer sur un axe ax
        ax : l'axe sur lequel on souhaite garder le tableau

    Output :
        X_out  : sous tableau extrait extraite

    
    Auteur :  CNRM/GMEI/TRAMM Août 2023
    """
    logger.debug("Extract_subtab : debut")

    # récupération des arguments
    X_header = X_in.attributes
    X_data   = X_in.data.data
    bornes = X_header['bornes']

    # appel de la fonction de calcul
    X_data_out,bornes_out,fct_ret = calcul.Extract_subtab.Extract_subtab_fct(X_data, dimension, ax, bornes)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X_in.get_names()
    

    X_out_header                         = default_out_header.copy()
    X_out_header['name']             = f"Sous tableau de '{X_fr_name}' de dimension '{X_data_out.shape}'"
    X_out_header['english_name']     = f"'Sub array from '{X_en_name}' with dimensions of '{X_data_out.shape}'"
    X_out_header['bornes']                 = bornes_out
    # X_out_header['unit_bornes']                 = X_header['unit_bornes'].split(",")[ax]
    X_out_header['unit']                 = f"{X_header['unit']}"
    X_out_header['freq_ech']             = f"{X_header['freq_ech']}"
    X_out_header['ref_time']             = f"{X_header['ref_time']}"
    X_out_header['misval']              = f"{X_header['misval']}"

    if fct_ret == -1 :
        msg_1 = f"ERREUR : dimension must be an integer"
    elif fct_ret == -2 :
        msg_1 = f"ERREUR : ax must be an integer"
    else : 
        msg_1 = f"Extract_subtab : ({X_data.shape} ech.), " +\
                f"Size of X_out = {X_data_out.shape}. OK."
        fct_ret = 0

    diag = {'CodeRet' : fct_ret,
            'DiagExec': f"{msg_1}"
           }
    
    return [X_out_header], [X_data_out], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Extract_subtab': {
        'Args': [
            {'Id': 'X_in'   , 'categorie': 'VECTOR_IN'    },
            {'Id': 'type'   , 'categorie': 'COEFFICIENT'  },
            {'Id': 'index'  , 'categorie': 'COEFFICIENT'  },
            {'Id': 'X_out'  , 'categorie': 'VECTOR_OUT'   },
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


    # # création de Vector en mémoire
    # acqid = 'Ce210183'
    # logger.info(f'=== {acqid}')
    # header = dict()
    # header['name']         = 'vitesse de vent'
    # header['english_name'] = 'wind speed'
    # header['format']       = 'Ieeefloat_32'
    # header['dimension']    = '4'
    # header['dim_array']    = '1'
    # header['ref_time']     = 'rft_time_PSEUDO_REG_20'
    # header['misval']       = np.nan
    # header['freq_ech']     = 20
    # header['unit']         = 'hPa'


    # X = AIDA.VectorMask(acqid, 'X', attributes=header, data=np.array([[1, np.nan], [3, 4],[5,6]]))
    # dimension = 0
    # ax = 1

    #Vrai cas
    acqid = 'ju230150'
    logger.info(f'=== {acqid}')
    X          = AIDA.VectorMask(acqid, 'tpr_diff_MWR_arome_%600')
    dimension       = 0
    ax              = 1

    #     #Vrai cas
    # acqid = 'pa230317'
    # logger.info(f'=== {acqid}')
    # X          = AIDA.VectorMask(acqid, 'tpr_TB_MWR_Eti_%600')
    # dimension = 0
    # ax = 1

    # appel de l'opérateur
    headers, datas, diag = Extract_subtab(X, dimension, ax)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in { k:header[k] for k in sorted(header) }.items():
            logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data   = {data}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
