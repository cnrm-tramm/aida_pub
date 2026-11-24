#!/usr/bin/env python3

"""
AITO
    fonctions...
"""

import sys
import os
import pandas as pd

from PyQt5.QtCore    import Qt

PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))


def get_index_filiation(index):
    """ Retourne l'arborescence de l'index reçu sous la forme d'un dictionnaire
        ordonné dans l'ordre naturel.
        Ex : filiation = {'model'     : 'campagne',
                          'campagne'  : 'COSMOS',
                          'plateforme': 'toulouse-meteo',
                          'year'      : '2009'}
        Ex : filiation = {'model'     : 'plateforme',
                          'plateforme': 'toulouse-meteo',
                          'year'      : '2021',
                          'num'       : '0001'}
        Ex : filiation = {'model'     : 'acqid',
                          'num'       : '0031',
                          'plateforme': 'atr',
                          'year'      : '2023'}
        Ex : filiation = {'model'     : 'by_date',
                          'day'       : '02',
                          'month'     : '01',
                          'year'      : '2024'}

        NOTE : la clé 'model' a été ajoutée tardivement => il y a sans doute
               des redondances dans le code.
    """
    back_filiation = dict()

    if not index:
        return back_filiation

    if not index.model():
        return None

    model = index.model().name
    data  = index.data()
    while data:
        role = index.model().data(index, Qt.UserRole)
        back_filiation[role] = data

        if role == 'plateforme':
            pltf = data
        elif role == 'year':
            year = data
        elif role == 'num':
            num = data

        index = index.parent()

        data = index.data()

    ###filiation = { key: back_filiation[key] for key in reversed(back_filiation) }
    filiation = {'model': model}
    filiation.update( { key: back_filiation[key] for key in reversed(back_filiation) } )

    return filiation


def string32_to_int(data):
    """ Retourne les données de format string32 sous la forme de int où
        chaque string32 est remplacée par son indice d'ordre d'apparition dans
        les data.
        Ex : si le vecteur contient   : ['z', 'z', 'a', 'b', 'b', 'z', 'a' ]
        les données retournées seront : [ 0 ,  0 ,  1 ,  2 ,  2 ,  0 ,  1  ]
          - 'z' apparait en premier  => les 'z' sont remplacé par 0
          - 'a' apparait en second   => les 'a' sont remplacé par 1
          - 'b' apparait en trosième => les 'b' sont remplacé par 2
        
        Retourne également les ticks correspondant ('z', 'a', 'b').
    """
    # data est un MaskedArray : les data 'initiales' sont dans data.data

    # convertir les données string32 en données "numéro d'ordre d'apparition"
    # de la string32"
    # - créer un DataFrame à partir des données aplaties
    df = pd.DataFrame({"strings": data.data.flatten()})
    
    # - ajouter une nouvelle colonne avec les index d'apparition des chaînes
    df['index'] = pd.factorize(df['strings'])[0]
    
    # - construire le np.array des int à partir de l'indexation obtenue en
    #   respectant le shape des données String32
    data_int = df['index'].to_numpy().reshape(data.data.shape)


    # - contruire les ticks à partir des string32
    ordered = { v: i for i, v in enumerate( pd.unique(data.data.flatten()) ) }
    ticks   = [ (idx, label) for idx, label in enumerate(ordered.keys()) ]

    return data_int, ticks
