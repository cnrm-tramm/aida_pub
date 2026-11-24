#!/usr/bin/env python3

"""
    ADC : Opérateur Cre_vect_sequences : Crée un vecteur des séquences déclarées dans le fichier INF
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

Code_palier = {"sondage" : "1",
            "palier" : "2",
            "sequence" : "3",
            "cercle" : "4",
            "zoom" : "5",
            "station" : "6",
            "avion_sol" : "-1"
            }
#==============================================================================
# Fonction Opérateur
#
# Les arguments sont ceux de la ligne d'instruction ADC lue dans le .fil
# ***SANS*** les noms des VECTOR/DIR_OUT
#
# Les arguments de type VECTOR/DIR_IN reçus sont des AIDA.VectorMask.
#
# L'opérateur :
#   - Récupère l'acqid dans le header du vecteur IN
#   - Récupère les séquences dans le fichier INF de l'acquisition
#   - prépare le(s) header(s) du/des vecteurs de retour.
#   - retourne : [headers], [data], {'CodeRet' : int()>= 0, 'DiagExec': str()}
#
# NOTE : AIDAcalc et AIDA.Vector mettront à jour les attributs :
#           #hdr_name, date_creation, fct_origine et vol...
#        des headers avant d'écrire les vecteurs.
#==============================================================================
def Cre_vect_sequences(X):
    """
    Cree un vecteur indiquant le type de séquence lors de l'acquisition
    """
    logger.debug(" Cre_vect_sequences : debut")

    seq_time = []

    # récupération des arguments
    X_header = X.attributes
    X_data   = X.data.data

    # récupération acqid
    acqid     = X.acq_id

    # Initialisation du vecteur avec des données averc -1
    seq_data = np.full(len(X_data), -1)

    acq_meta = AIDA.Inf(str(acqid))

    # Récupération heure decollage et atterrissage
    heure_dec = acq_meta.get_horaire('decollage')
    if heure_dec != None :
        sec_dec =  acq_meta.datetime_to_sec(heure_dec)
    else :
        sec_dec = X_data[0]
    heure_att = acq_meta.get_horaire('atterrissage')
    if heure_att != None :
        sec_att =  acq_meta.datetime_to_sec(heure_att)
    else :
        sec_att = X_data [-1]
        
    tab_seq = []

    for (typ, seq) in acq_meta.iter_items_str('SEQUENCES') :
        if typ in Code_palier.keys() :
            cod_typ =  Code_palier[typ]
        else :
            cod_typ = "9"

        str_seq =  cod_typ + "/" + seq 
        tab_seq.append(str_seq)

    seq_data, seq_name = calcul.Cre_vect_sequences.Cre_vect_sequences(tab_seq, X_data, acq_meta)

    VO_header                 = default_out_header.copy()
    VO_header['name']         = f"Type de sequence"
    VO_header['english_name'] = f"Sequence type"
    VO_header['ref_time']     = f"{X_header['ref_time']}"
    VO_header['freq_ech']         = f"{X_header['freq_ech']}"
    VO_header['unit']     = f"without"
    VO_header['format']       = f"Int_32"
    VO_header['misval']       = f"-1"
    VO_header['comment']      = f"sondage : 1, palier : 2, sequence : 3, cercle : 4, zoom : 5, station : 6, avion_sol : -1"

    V1_header                 = default_out_header.copy()
    V1_header['name']         = f"nom de la sequence"
    V1_header['english_name'] = f"Sequence name"
    V1_header['ref_time']     = f"{X_header['ref_time']}"
    V1_header['freq_ech']         = f"{X_header['freq_ech']}"
    V1_header['unit']     = f"without"
    V1_header['format']       = f"string32"
    V1_header['misval']       = f"?"
    V1_header['obs_min']       = f"Nan"
    V1_header['obs_max']       = f"nan"

    diag = {'CodeRet': 0,
            'DiagExec': f"Cre_vect_sequences : ({len(seq_data)} ech.)"
            }

    return [VO_header, V1_header], \
           [seq_data, seq_name], \
           diag

#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Cre_vect_sequences': {
        'Args': [
            {'Id': 'X'        , 'categorie': 'VECTOR_IN'  , 'unit': 's'},
            {'Id': 'X_out'    , 'categorie': 'VECTOR_OUT'              },
            {'Id': 'SEQ_out'  , 'categorie': 'VECTOR_OUT'              },
        ],
#        'control_reftime': 'off',
    },
}


