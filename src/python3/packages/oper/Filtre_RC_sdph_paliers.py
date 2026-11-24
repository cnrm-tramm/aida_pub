#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    ADC : Opérateur Filtre_RC_sdph_paliers
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
def Filtre_RC_sdph_paliers(X, fc, typ, time_out):
    """
    Réalise numériquement un filtrage équivalent à un circuit électrique RC
    sans déphasage de phase, sur des périodes de temps définies en entrée.
    Cet opérateur est le petit frère de Filtre_RC_sdph et implémente le même
    algorithme de filtrage. Il est notamment utilisé pour le traitement de la 
    sonde turbulente sous ballon captif de GMEI/4M. 
    Le résulat est un vecteur de même fréquence que le vecteur d'entrée, qui 
    contient le signal filtré sur chaque palier et des valeurs manquantes en
    dehors des paliers.


    Input :
        X               any     donnée d'origine
        fc              Hz      fréquence de coupure
        typ             any     type de filtre (0 = passe bas, 1= passe haut)
        time_out        second  base de temps qui définit les paliers

    Output :
        X_out           any     donnée filtrée

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Déc 2022
    """
    logger.debug("Filtre_RC_sdph_paliers : debut")

    # récupération des arguments
    X_header     = X.attributes
    X_data       = X.data.data
    
    time_out_header = time_out.attributes
    time_out_data   = time_out.data.data
    
    #
    # préparation des arguments pour la fonction de calcul
    #
    # - récupération des time_bnds (bornes_temps) pour le vecteur time_out
    acqid     = time_out.acq_id
    bnds      = AIDA.time_to_data_bnds(acqid, time_out.name)
    if bnds is None:
        raise Exception ("opérateur Filtre_RC_sdph_paliers : problème de lecture " +
                         f"des bornes du vecteur '{time_out.name}'")
                         
    # - fréquence du signal d'entrée
    fe = float(X_header["freq_ech"])
    # - récupération des données du vecteur temps de X
    time_X_data   = X.timedata()
    
    #
    # appel de la fonction de calcul
    #
    X_out_data, codret = \
        calcul.Filtre_RC_sdph_paliers.Filtre_RC_sdph_paliers(X_data, time_X_data, fe, fc, typ, bnds)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    X_fr_name, X_en_name = X.get_names()

    X_out_header = default_out_header.copy()
    X_out_header['name']         = f"{X_fr_name} avec filtrage RC"
    X_out_header['english_name'] = f"{X_en_name} with RC filtering"
    X_out_header['unit']         = f"{X_header['unit']}"
    X_out_header['freq_ech']     = f"{X_header['freq_ech']}"
    X_out_header['ref_time']     = f"{X_header['ref_time']}"
    X_out_header['misval']       = f"{X_header['misval']}"
    X_out_header['dim_array']    = f"{X_header['dim_array']}"

    if codret == 0 :
        str_diagexec = "OK"
    elif codret == -1 :
        str_diagexec = " ERREUR : Fréquence de coupure négative."
    elif codret == -2 :
        str_diagexec = " ERREUR : Fréquence d'échantillonnage négative."
    elif codret == -3 :
        str_diagexec = " ERREUR :Type doit être égal à 0 (passe-bas) ou 1 (passe-haut)."
    else :
        str_diagexec = " ERREUR : erreur non identifiée."
    diag = {'CodeRet' : codret,
            'DiagExec': f"Filtre_RC_sdph_paliers : ({len(X_data)} ech.) : {str_diagexec}"
           }
    
    return [X_out_header], \
           [X_out_data  ], \
           diag
    
#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Filtre_RC_sdph_paliers': {
        'Args': [
           {'Id': 'X'           , 'categorie': 'VECTOR_IN'   },
           {'Id': 'fc'          , 'categorie': 'COEFFICIENT' },
           {'Id': 'typ'         , 'categorie': 'COEFFICIENT' },
           {'Id': 'time_out'    , 'categorie': 'VECTOR_IN'   },
           {'Id': 'X_out'       , 'categorie': 'VECTOR_OUT'  }
        ]
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


    acqid = 'Ce210205'
    logger.info(f'=== {acqid}')
    X        = AIDA.VectorMask(acqid, 'tpr_son_gillwp_combi_20')
    fc       = 1/(200*2*3.14159)
    typ      = 1
    time_out = AIDA.VectorMask(acqid, 'rft_time_seq_0')

    # appel de l'opérateur
    logger.info('*** appel de Filtre_RC_sdph_paliers')
    headers, datas, diag = Filtre_RC_sdph_paliers (X, fc, typ, time_out)

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
