#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Creation d'un vecteur FLAG Int_32 qui vaut la valeur spécifiée en 4eme
colonne, dans les périodes de temps définies dans le fichier et 0 ailleurs 

Usage :

creer_vect_flag_periode.py <-f|-F> ACQID FIC_PERIODE VEC_TIME VEC_FLAG

avec :

  ACQID : acqid de l'aquisition à traiter
  <-F> : option FORCE écrase le vecteur existant
  <-f> : option BACKUP sauvegarde le vecteur dans une nouvelle version
  FIC_PERIODE : nom du fichier contenant les periodes de temps au format

exemple :
  # AcqId,HHMMSS_deb,HHMMSS_fin, valeur_flag
  Tf130020,070000,073000,1
  Tf130072,030000,043000,2    
  Tf130072,080000,100000,1
  Tf130332,041500,080000,1
  Tf130338,080000,094000,1
  Tf130331,070000,090000,1

  VEC_TIME : nom du vecteur temps de référence (sans extension .vbn)
  VEC_FLAG : nom du vecteur FLAG résultat (sans extension .vbn)

ATTENTION : si dans le fichier il n'y a pas de sequence correspondant à
l'ACQID demandé, on crée un vecteur remplit de 0.

"""

import os
import sys
import datetime as dt
import numpy as np
import getopt
import math
#import pylab as plt
from decimal import * 

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python{:d}.{:d}".format(sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA

del AH


# ------------------- PROG PRINCIPAL ---------------------

OPT_FORCE= False
OPT_BACKUP= False
# ----------- décodage des arguments d'entrée ------------
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "hFf", ["help"])
except getopt.error as msg:
   print(msg)
   print(__doc__)
   sys.exit(1)

# process options
for o, a in opts:
    if o in ("-h", "--help"):
       print(__doc__)
       sys.exit(0)
    if o in ("-F"):
       OPT_FORCE=True
    if o in ("-f"):
       OPT_BACKUP=True
   
if OPT_FORCE and OPT_BACKUP :
    print("+++ ERREUR : les options -f et -F ne peuvent pas être utilisées en même temps.")
    print(__doc__)
    sys.exit(0)

if len(args) != 4:
    print("+++ ERREUR : Nombre d'arguments incorrects (il y en a {})" .format(  len(args) ))
    print(__doc__)
    sys.exit(0)
else:
    acq_id = args[0]
    nomfic_periodes = args[1]
    nomfic_time= args[2]
    nomfic_flag= args[3]

if not os.path.isfile(nomfic_periodes):
    print("+++ ERREUR : {} n'est pas un fichier" .format(nomfic_periodes))
    sys.exit(0)



# lecture du fichier des periodes

periodes = []

ligne=""
try : 
   fichier_periodes=open(nomfic_periodes, "r")

# lecture des lignes de périodes 
   for ligne in fichier_periodes:
      if ligne[0] != "#":
         #periodes.append(ligne.strip().rstrip('\n\r').split(","))
         seq=''.join(ligne.split()).split(",")

         if len(seq) > 4 or len(seq) < 3:
            print("-+- ATTENTION ligne {} nombre de champs incorrects !".format(ligne))
         else :
            periodes.append(seq)

   fichier_periodes.close

except IOError as err :
   print("+++ ERREUR : Echec lecteur fichier periode {}, {} ".format( nomfic_periodes,err ))
   sys.exit(0)

   

nb_periodes=len(periodes)

if nb_periodes > 0 :
   print("--- Lecture fichier periodes : {} OK".format(nomfic_periodes))
   print("--- Nombre de periodes trouvees : {}".format(nb_periodes))
else :
   print("-+- ATTENTION : Pas de periodes dans le fichier : {}".format(nomfic_periodes ))


# Lecture du vecteur temps de référence 
try : 
   vect_time = AIDA.Vector(acq_id, nomfic_time)
except AIDA.AidaError as err:
   print("+++ ERREUR : Acqid {}, Echec lecture reftime {}".  format(acq_id, nomfic_time))
   sys.exit(0)

print("--- Acqid : {}, Lecture fichier reftime OK : ".format(acq_id, nomfic_time ))

# Construction du vecteur FLAG 

flag_data =  np.zeros(len(vect_time.data))
nb_acqid_in_seq = 0

periodes_a_traiter = [ seq for seq in periodes if seq[0]==acq_id ] 
acqid_in_seq = len(periodes_a_traiter)

if acqid_in_seq ==0 :
   print("--- Aucune sequence correspondant a AcqID : {}" .format( acq_id  ))
else:
   print("{} sequences trouvees".format(acqid_in_seq))

for seq in periodes_a_traiter :
   hdeb=seq[1]
   hfin=seq[2]
   time_deb= 3600.*float(hdeb[0:2])+60.*float(hdeb[2:4])+float(hdeb[4:6])
   time_fin= 3600.*float(hfin[0:2])+60.*float(hfin[2:4])+float(hfin[4:6])
   print("--- Debut, fin sequence (secondes) : {}, {}".format (time_deb, time_fin))
   idx=np.where((vect_time.data >= time_deb) & (vect_time.data <= time_fin))

   if len(seq) == 4 :
        flag_data[idx]=int(seq[3]) 
   else :
        flag_data[idx]= 1

flag_hdr = {"name": "Flag periodes temporelles", "english_name": "Time laps flag",
		"unit": "unitless", "format": "Int_32",
             "freq_ech": vect_time.attributes["freq_ech"], "dimension": '4',
             "dim_array": '1', "type_ech": 'regulier',
             "misval": -9999, "ref_time": nomfic_time,
             "origine": "cree_flag_periodes.py ",
             "famille": "controle",
             "fct_origine": "cree_flag_periodes " + acq_id +" "+nomfic_periodes,
              }


try:
   vect_flag = AIDA.Vector (acq_id, nomfic_flag, attributes=flag_hdr, data=flag_data)
   cr=vect_flag.write(backup=OPT_BACKUP, force=OPT_FORCE)
   print(cr)

except (AIDA.AidaError, IOError) as err:
	
   print("+++ ERREUR : Acqid {}, Echec ecriture resultat {}".format  (acq_id, nomfic_flag))
   AIDA.report_error("+++ Erreur: {} ".format(err.msg ))
   sys.exit(0)

print("--- Acqid {}, Ecriture resultat {} OK".format(acq_id, nomfic_flag))

# DEBUG
#plt.plot ( vect_time.data, flag_data)

#plt.show()



