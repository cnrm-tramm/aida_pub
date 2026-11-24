#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import numpy as np


AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python{:d}.{:d}".format(sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA


def Cre_time_sequences ( acqid, type_seq, conv=1.0 ) :
    """ 
    Creation d'un vecteur temps et ses time_bounds à partir
    des sequences du fichier .inf
    Créastion de :
         - un vecteur ref_time contenant un temps par sequence en fonction de
   la convention de datation donnée 
         - un vecteur time_bnds contenant les bornes de debut et fin de sequence

    IN:
        acqid       acqid à utiliser 
        type_seq    Type de sequences à utiliser dans le fichier .inf (palier, sequence, sondage, ....)
        conv        Convention de datation (1 par defaut, dans AIDA on date les  vecteurs en fin de periode par defaut
    OUTPUT 

        time        temps de reference des sequences 
        time_bnds   bornes de debut et fin de sequences 

    @Météo-France CNRM/GMEI/TRAMM
    W. Maurel 
    le 01/03/2022

    """


    # lecture des fichiers .inf pour 
    # constituer de la liste des paliers à traiter

    liste_paliers = []

    time = np.empty(0)
    time_bnds = np.empty((0,2))
    s_seq =  None
    dict_seq={}


    acq_meta = AIDA.Inf(str(acqid))

    for t_seq in type_seq.split(" ") :
        l_seq = acq_meta.get_field_value("SEQUENCES", t_seq)
        if l_seq is None : 
            print("-+- Aucune sequence de type {} trouvée".format(type_seq) )  
            return( -1, time, time_bnds )
        
        if s_seq is None :
            s_seq = l_seq
        else :
            s_seq = s_seq  + ";" + l_seq

    for seq in s_seq.split(";") :
        decoupe_seq = seq.split("/")

        dict_seq[decoupe_seq[0]] = decoupe_seq[1]
        nom_seq = decoupe_seq[0]
        deb_seq= decoupe_seq[1]
        
        keys = list(dict_seq.keys())
        values=list(dict_seq.values())
        sorted_value_index = np.argsort(values)
        sorted_seq = [keys[i] for i in sorted_value_index]

    for nom_seq in sorted_seq :

        heure_deb, heure_fin = acq_meta.get_sequence_times(nom_seq)

        sdeb = acq_meta.datetime_to_sec(heure_deb)
        sfin = acq_meta.datetime_to_sec(heure_fin)

        time = np.append(time, sdeb + (sfin -sdeb) * float(conv) )  
        time_bnds = np.concatenate( (time_bnds, [[sdeb, sfin]]) )

    print ( "--- {} sequences de type {} trouvées".format(len(time), type_seq) )

    print(time, time_bnds)

    return ( 0, time, time_bnds)

# ----------- main -------------
#acqid = "P2240008"
#codret, time, time_bnds = Cre_time_sequences ( acqid, "palier sondage",  conv=0.5 ) 
#print(time)
#print(time_bnds)


