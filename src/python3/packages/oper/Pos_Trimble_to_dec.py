#!/usr/bin/env python3

"""
    ADC : Opérateur Pos_Trimble_to_dec
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
def Pos_Trimble_to_dec(pos, pos_dir):
    """
    Calcul de la latitude / longitude issue du Trimble au format decimale standard (degree_north / degree_east).

    Input :
        pos    : position de la plateforme (latitude ou longitude).
        pos_dir    : axe de projection de la position (Nord/Sud/Est/Ouest).

    Output :
        pos_dd  : position de la plateforme calculee selon l'axe de projection.

    Auteur : @Safire ITD/TAD - Mai 2023"""

    logger.debug("Pos_Trimble_to_dec : debut")

    # récupération des arguments
    pos_header = pos.attributes
    pos_data   = pos.data.data
    pos_dir_data   = pos_dir.data.data

    # appel de la fonction de calcul
    pos_dd_data = calcul.Pos_Trimble_to_dec.Pos_Trimble_to_dec(pos_data, pos_dir_data)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    pos_fr_name, pos_en_name = pos.get_names()

    pos_dd_header                 = default_out_header.copy()
    pos_dd_header['english_name'] = f"Position computed with '{pos_en_name}'"
    if 'N' in pos_dir_data or 'S' in pos_dir_data:
        pos_dd_header['unit'] = "degree_north"
    elif 'E' in pos_dir_data or 'W' in pos_dir_data:
        pos_dd_header['unit'] = "degree_east"
    pos_dd_header['freq_ech']     = f"{pos_header['freq_ech']}"
    pos_dd_header['ref_time']     = f"{pos_header['ref_time']}"
    pos_dd_header['misval']       = f"{pos_header['misval']}"
    pos_dd_header['format']       = f"{pos_header['format']}"

    diag = {'CodeRet' : 0,
            'DiagExec': f"Pos_Trimble : ({len(pos_data)} ech.)"
           }

    return [pos_dd_header], [pos_dd_data], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Pos_Trimble_to_dec': {
        'Args': [
            {'Id': 'pos'    , 'categorie': 'VECTOR_IN' },
            {'Id': 'pos_dir', 'categorie': 'VECTOR_IN' },
            {'Id': 'pos_dd' , 'categorie': 'VECTOR_OUT'},
        ],
    },
}