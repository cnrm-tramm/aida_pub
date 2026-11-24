#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaire pour créer des vecteurs rft_time et rft_bnds associés
correspondant à des séquences du fichier .inf d'un acqid
donné.

Ce programme fait appel à la fonction de calcul 
Cre_time_sequences.py du package oper.

Cette fonction a vocation a devenir un operateur 
appelable avec adc.

Pour avoir l'aide :

creer_vect_time_sequences.py -h 


@Maurel William
le 25/02/2022
"""

import os
import sys
import datetime as dt
import numpy as np
import argparse 

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python{:d}.{:d}".format(sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA
import oper

#-----------------------------------------------------------------
def ecrit_un_vecteur ( acqid, nom_vect, hdr, x, write_force, fersion):
    """
    fonction unitaire pour ecrire un vecteur 
    """

    vect = AIDA.Vector (acqid,  nom_vect, hdr, x)
    try:
        vect.write(force = write_force, backup=fersion)
        print("--- Acqid {}, Ecriture {} OK".format(acqid, nom_vect ))
    except (AIDAError, IOError) as err:
        print("+++ ERREUR ecriture vecteur {}:{}".format(acqid, nom_vect))
        print("+++ {}".format(err))


#------------- PROG PRINCIPAL ------------
parser = argparse.ArgumentParser()
parser.add_argument("acqid", help="acqid")
parser.add_argument("type_seq", help="type de sequence a utiliser (palier, sequence, ...)")
parser.add_argument("nom_reftime", help="nom du vecteur reftime à creer")
group = parser.add_mutually_exclusive_group()
group.add_argument('-F', '--force', required = False, action='store_true', help='option force ecriture si vecteur existe' )
group.add_argument('-f', '--fersion', required = False, action='store_true', help='option cree une nouvelle version si vecteur existe' )
parser.add_argument("-c", "--conv", required = False, dest='conv', default=1, help="Convention de datation (1 par defaut)")

args=parser.parse_args()

codret, time, time_bnds = oper.Cre_time_sequences.Cre_time_sequences ( args.acqid, args.type_seq, conv=args.conv ) 

if codret != 0 :
    print("+++ Erreur : pas de fichier créé")
    sys.exit(-1)

# ecriture des vecteurs temps

tab = args.nom_reftime.split("_")
if tab[0] != "rft" :
    print("+++ ERREUR : la famille dans le nom du reftime {} doit être rft".format(args.nom_reftime ))
    sys.exit(-1)

str_origine = "traitement creer_vect_time_sequences.py"
nom_time_bnds = "rft_bnds_"+"_".join(tab[1:])

hdr_time = {"name":"temps sequence",
          "english_name":"sequence time",
          "unit":"s",
          "famille":"temps",
          "format": "ieeefloat_64",
          "freq_ech": 0.0, "dimension": '8',
          "dim_array": '1', "type_ech": 'irregulier',
          "ref_time":  args.nom_reftime,
          "datation_convention":"1",
          "bnds_convention":"],]", 
          "time_bnds": 'vector:'+nom_time_bnds,
          "origine": str_origine,
	  }


hdr_time_bnds = {"name":"bornes temps sequences",
          "english_name":"sequences time bounds",
          "unit":"s",
          "famille":"temps",
          "format": "ieeefloat_64",
          "freq_ech": 0.0, "dimension": '8',
          "dim_array": '2', "type_ech": 'irregulier',
          "origine": str_origine,
          }


ecrit_un_vecteur ( args.acqid, args.nom_reftime, hdr_time, time, args.force, args.fersion)
ecrit_un_vecteur ( args.acqid, nom_time_bnds, hdr_time_bnds, time_bnds, args.force, args.fersion)


