#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    ADC : Opérateur Filtre_RC_sdph
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
def Filtre_RC_sdph(X, fc, typ):
    """ Réalise numériquement un filtrage équivalent à un circuit électrique RC
        sans déphasage de phase, sur des périodes de temps définies en entrée.

    Input :
        X               any     donnée d'origine
        fc              Hz      fréquence de coupure
        typ             any     type de filtre (0 = passe bas, 1= passe haut)
        time_out        second  base de temps qui définit les paliers

    Output :
        X_out           any     donnée filtrée

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Déc 2022
    """

    logger.debug("Filtre_RC_sdph : debut")

    # récupération des arguments
    X_header     = X.attributes
    X_data       = X.data.data

    # - fréquence du signal d'entrée
    fe = float(X_header["freq_ech"])

    # appel de la fonction de calcul
    X_out_data, fct_ret = calcul.Filtre_RC_sdph.Filtre_RC_sdph(X_data, fe, fc, typ)


    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X.get_names()

    X_out_header = default_out_header.copy()
    X_out_header['name']         = f"la variable {X_fr_name} avec filtrage RC"
    X_out_header['english_name'] = f"the variable {X_en_name} with RC filtering"
    X_out_header['unit']         = f"{X_header['unit']}"
    if X_out_data.ndim > 1 :
        X_out_header['bornes']       = f"{X_header['bornes']}"
        X_out_header['unit_bornes']  = f"{X_header['unit_bornes']}"
    X_out_header['freq_ech']     = f"{X_header['freq_ech']}"
    X_out_header['ref_time']     = f"{X_header['ref_time']}"
    X_out_header['misval']       = f"{X_header['misval']}"
    X_out_header['dim_array']    = f"{X_header['dim_array']}"

    msg_1 = f"Filtre_RC_sdph : ({X_data.shape} ech.)"
    if fct_ret == 0 :
        msg_2 = " OK"
    elif fct_ret == -1 :
        msg_2 = " ERREUR : Fréquence de coupure négative."
    elif fct_ret == -2 :
        msg_2 = " ERREUR : Fréquence d'échantillonnage négative."
    elif fct_ret == -4 :
        msg_2 = " ERREUR : Type doit être égal à 0 (passe-bas) ou 1 (passe-haut)."
    else :
        msg_2 = " ERREUR : erreur non identifiée."

    diag = {'CodeRet' : fct_ret,
            'DiagExec': f"{msg_1}.{msg_2}"
           }

    return [X_out_header], \
           [X_out_data  ], \
           diag

#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Filtre_RC_sdph': {
        'Args': [
           {'Id': 'X'           , 'categorie': 'VECTOR_IN'   },
           {'Id': 'fc'          , 'categorie': 'COEFFICIENT' },
           {'Id': 'typ'         , 'categorie': 'COEFFICIENT' },
           {'Id': 'X_out'       , 'categorie': 'VECTOR_OUT'  },
        ],
        'control_reftime': 'off',
    }
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

    # Données 1D
    acqid = 'Ce210205'
    logger.info(f'=== {acqid}')
    X        = AIDA.VectorMask(acqid, 'ven_w_gillv3_50m_combi_2D_20')
    fc       = 0
    typ      = 1

    # #Données 2D
    # acqid = 'Ce210182'
    # logger.info(f'=== {acqid}')
    # X        = AIDA.VectorMask(acqid, 'ven_ff_windcube0_Eti_%4')
    # fc       = 1/(200*2*3.14159)
    # typ      = 1

    # appel de l'opérateur
    logger.info('*** appel de Filtre_RC_sdph')
    headers, datas, diag = Filtre_RC_sdph(X, fc, typ)

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
