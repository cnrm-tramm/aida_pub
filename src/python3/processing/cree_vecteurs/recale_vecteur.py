#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recale un vecteur entre J 00H et J+1 00H sur le principe que la 1ère valeur de J+1 appartient à J :
  Pour cela on lit les 2 vecteurs (J et J+1) avec leurs vecteurs temps et on recrée une version du vecteur J avec son nouveau vecteur temps.
  On conserve pour première valeur de J la première date > 00H+1/2 période.
  On prend pour dernière valeur de J la première date < 00H+1/2 période de J+1.
  La fréquence est lue dans le vecteur J.
  On ajoute _rec_ avant la fréquence au nom du vecteur.
"""

import sys
import os
import argparse
import datetime
import numpy as np
AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
import AIDA
import AcqIdDoY


def readVecteur(acqId, param, refTime=None):
    """
        Lit un vecteur et son ref_time.
        Le ref_time sera exprimé en valeur numérique utilisé
        dans le module  "datetime" de python, matplotlib, etc.
        le ref_time est stocké dans l'attribut "time" du vecteur (vect.time)
        le nom du ref_time est stocké dans l'attribut "time_name" du vecteur

        :param acqId: identifiant d'acquisition
        :type param: str
        :param param: le paramètre à traiter
        :type param: str
        :param refTime: le nom du vecteur temps de référence
        :type param: str
        :return: le vecteur lu
        :rtype: Vector
    """
    try:
        vect = AIDA.Vector(acqId, param)
    except IOError as excpt:
        print("Jour vide pour {} de {}: {}".format(param, acqId, str(excpt)))
        return None
    except Exception as excpt:
        print( "coucou")
        print( excpt.message)

    if 'ref_time' not in vect.attributes:
        print("Pas de ref_time dans {} de {}" .format(param, acqId))
        return None
    if refTime is None:
        ref_time = vect.attributes['ref_time']
    time = AIDA.Vector(acqId, ref_time)
    if len(time.data) != len(vect.data):
        print("len({}) = {}, ref_time = {}, len={}".format( param, len(vect.data), ref_time, len(time.data)))
        return None
    # Conversion du temps du vecteur (secondes depuis 0h00 le jour du
    # démarrage de l'acquisition) en temps UTC numérique tel que
    # représenté par le module "datetime" de python, matplotlib, etc...
    # nombre de jour depuis le 01/01/0000  en calendrier grégorien
    # proleptique)
    try :
        date_acq = AIDA.Inf(acqId).get_date_acq()
    except Exception :
        print("Erreur de lecture du fichier INF pour {}.".format(acqId))
        return None
    vect.time = date_acq.toordinal() + time.data / 86400.0
    vect.time_name = ref_time
    vect.time_data = time.data
    return vect

#
# MAIN
#

# On parse la ligne de commande
parser = argparse.ArgumentParser()
parser.add_argument("-a","--acqid", required=True, help="acqid")
parser.add_argument("-p","--parametre", required=True, help="paramètre : si omis on traite tous les paramètres")
args = parser.parse_args()

# On lit le vecteur J correspondant à acqid
acqid = args.acqid
parametre = args.parametre
vect_J = readVecteur(acqid, parametre)
freq_ech = (float)(vect_J.attributes['freq_ech'])
demi_periode = 1/(2*freq_ech)

# On garde les data pour lesquelles demi_periode <= t <86400+demi_periode  
temps_valeur_J = np.array([ (t,v) for (t,v) in zip(vect_J.time_data, vect_J.data) if demi_periode<=t and t<(86400+demi_periode) ])
temps_J = temps_valeur_J[:,0]
data_J = temps_valeur_J[:,1]

# On lit le vecteur J+1 correspondant
a = AcqIdDoY.AcqIdDoY(acqid)
a = a+1
vect_J1 = readVecteur(str(a), parametre)

if vect_J1 != None :
    # On garde les data pour lesquelles demi_periode > t
    temps_valeur_J1 = np.array([ (t,v) for (t,v) in zip(vect_J1.time_data, vect_J1.data) if demi_periode>t ])
    temps_J1 = temps_valeur_J1[:,0]
    temps_J1 += 86400
    data_J1 = temps_valeur_J1[:,1]

    # On rajoute les datas de J+1 à J
    if len(temps_J1) != 0 :
        new_temps = np.concatenate((temps_J,temps_J1), axis=0)
        new_datas = np.concatenate((data_J,data_J1), axis=0)
else :
    new_temps = temps_J
    new_datas = data_J

# Ecriture du nouveau vecteur temps
vecteur_temps_split = vect_J.attributes['ref_time'].split('_')
new_vecteur_temps = "_".join(vecteur_temps_split[0:-1])+"_rec_"+vecteur_temps_split[-1]
vect_temps_J = AIDA.Vector(acqid, new_vecteur_temps, data=new_temps)
vect_temps_J.write(force=True)

# Ecriture du nouveau vecteur
storage_path = os.path.join (AIDA.ID_to_datapath(acqid), vect_J.name+'.vbn')
storage_path_split = storage_path.split('_')
new_storage_path = "_".join(storage_path_split[0:-1])+"_rec_"+storage_path_split[-1]
vect_J.storage_path = new_storage_path
parametre_split = parametre.split('_')
new_parametre = "_".join(parametre_split[0:-1])+"_rec_"+parametre_split[-1]
vect_J.name = new_parametre
vect_J.attributes['ref_time'] = new_vecteur_temps
vect_J.attributes['fct_origine'] = "recale_vecteur.py -a {} -p {}".format(acqid, parametre)
date_acq = AIDA.Inf(acqid).get_date_acq()
date_debut = datetime.datetime.fromordinal(date_acq.toordinal()) + datetime.timedelta(seconds=new_temps[0])
str_date_debut = datetime.datetime.strftime(date_debut,"%Y-%m-%d %H:%M:%S.%f")
date_fin = datetime.datetime.fromordinal(date_acq.toordinal()) + datetime.timedelta(seconds=new_temps[-1])
str_date_fin = datetime.datetime.strftime(date_fin,"%Y-%m-%d %H:%M:%S.%f")
vect_J.attributes['fct_comment'] = "debut : {}  fin : {}".format(datetime.datetime.strftime(date_debut,"%Y-%m-%d %H:%M:%S.%f"), datetime.datetime.strftime(date_fin,"%Y-%m-%d %H:%M:%S.%f"))
vect_J.data = new_datas
vect_J.write(force=True)

    



