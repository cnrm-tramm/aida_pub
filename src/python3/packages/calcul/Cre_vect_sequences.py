#!/usr/bin/env python3

"""
    ADC : Opérateur Cre_vect_sequences : Crée un vecteur des séquences déclarées dans le fichier INF
"""

import sys
import os
import numpy as np

def Cre_vect_sequences(str_seq, X_data, acqmeta):
    """
    Cree un vecteur indiquant le type de séquence lors de l'acquisition
    """
    
    seq_time = []
    seq_name = np.array(['??' for _ in range(len(X_data))], dtype='S32')
    seq_data = np.zeros(len(X_data))

    for (seq) in str_seq :
        champs = seq.split('/')
        if champs[1] != 'SEQUENCES' :
            heure_deb, heure_fin = acqmeta.get_sequence_times(champs[1])
            sdeb =  acqmeta.datetime_to_sec(heure_deb)
            sfin =  acqmeta.datetime_to_sec(heure_fin)

            seq_time.append([sdeb, sfin])  
            for i in  np.arange(len(X_data)) :
                if X_data[i] >= sdeb and X_data[i] < sfin :
                    seq_data[i] =  int(champs[0])
                    seq_name[i] = champs[1]

    return seq_data, seq_name

