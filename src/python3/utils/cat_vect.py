#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concatenation de plusieurs vecteurs 
Utilisation :
 
cat_vect.py -a acqid -o vecteur_out -t vecteur_time_out  vecteur_in_1 vecteur_in_2 vecteur_in_3 ...

Option -F  : force l'écriture des vecteurs

Nom de vecteurs sans le .vbn

L'entete du premier vecteur est copié dans le vecteur de sortie
Attention il concatene dans l'ordre des fichiers et pas dans l'ordre du temps de chaque fichier
"""

import sys
import os
import getopt 
import pandas as pd

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA

#----------------------------------------------------------------------------
def ecrit_vecteur ( acqid, nom_vect, hdr, x, write_force=False, fersion=False ):
    """
    fonction unitaire pour ecrire un vecteur 
    """

    if  AIDA.vector_exists ( str(acqid), nom_vect) and not(write_force) and not(fersion)  :
        print(("-+- {} : vecteur {} existe !".format(acqid, nom_vect ) ))
        print("-+- on n'ecrase pas le vecteur")
        return(-1) 

    vect = AIDA.Vector (acqid,  nom_vect, hdr, x)
    try:
        vect.write(force = write_force, backup=fersion)
        print("--- Acqid {}, Ecriture {} OK".format(acqid, nom_vect ))
    except (AIDAError, IOError) as err:
        print("+++ ERREUR ecriture vecteur {}:{}".format(acqid, nom_vect))
        print("+++ {}".format(err))

    return(0)

#----------------------------------------------------------------------------
# Programme PRINCIPAL

# decodage des arguments

opt_force = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "Fha:o:t:" )
except getopt.GetoptError as err:
    print(err)
    print(__doc__) 
    sys.exit(-1)

for o, a in opts:
    if o == "-h":
        print(__doc__)
        sys.exit()
    elif o=="-F":
        opt_force=True
    elif o in ("-a"):
        acqid = a
    elif o in ("-o"):
        vec_data_out = a
    elif o in ("-t"):
        vec_time_out = a
    else : 
        print("+++ option inconnue.")
        sys.exit(-1)

liste_vec_in = args

if len(liste_vec_in) == 0 :
    print("+++ pas de vecteurs d'entree fournis")
    sys.exit(-1)


#----- lecture des vecteurs d'entrée

data = pd.Series()

for v in liste_vec_in :
    x = AIDA.Vector(acqid, v )
    time =  AIDA.Vector ( acqid, x.attributes['ref_time'] ) 
   
    data_temp = pd.Series ( x.data, index = time.data )

    print('--- Lecture {} : {} valeurs, time_deb : {}, time_fin : {}'.format(v, len(x.data), time.data[0], time.data[-1] ) ) 

    
    try : 
        #data.append(data_temp, verify_integrity = True )
        data = data.append(data_temp )
    except ValueError as e :
        print ("+++ Erreur : datation communes dans vecteur d'entrée" )
        print (e)
        sys.exit(-1)
        
# construction header

d = AIDA.Vector(acqid,  liste_vec_in[0], attributes_only=True )
t = AIDA.Vector(acqid, d.attributes['ref_time'], attributes_only=True )

# on reconstitue l'appel de la fonction

origine = 'traitement cat_vect.py'
fct_origine = 'cat_vect.py '
for o, a  in opts :
    fct_origine = fct_origine + '{} {} '.format(o, a) 
fct_origine = fct_origine + ' '.join(args)


# header des vecteurs de sortie

hdr_data = d.attributes 
hdr_data['origine'] = origine
hdr_data['fct_origine'] = fct_origine 
hdr_data['ref_time'] = vec_time_out 
hdr_time = t.attributes
hdr_time['name'] = vec_time_out 
hdr_time['ref_time'] = vec_time_out 
hdr_time['origine'] = origine
hdr_time['fct_origine'] = fct_origine 

# Ecriture vecteurs de sortie

ecrit_vecteur ( acqid, vec_data_out, hdr_data , data.values, write_force=opt_force )
ecrit_vecteur ( acqid, vec_time_out, hdr_time , data.index, write_force=opt_force )












