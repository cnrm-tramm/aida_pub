#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Crée la liste des vecteurs utilisée par vista.
    Usage : make_liste_vecteurs_vista.py [ -p|--plateforme ]
"""

import os
import sys
import datetime as dt
import configparser
import collections
import re
import argparse

aida_home = os.getenv('AIDA_HOME')
aida_profil = os.getenv('AIDA_PROFIL')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(aida_home, 'lib', PYTHON_X_Y))
import AIDA
from AcqId import *
AIDA_META = AIDA.AIDA_getenv ('meta')
AIDA_INF = os.path.join(AIDA_META, "INF")

date_jour = dt.datetime.now()

def ecrit_fichier(plateforme, liste_vecteurs):
    """
        Ecriture du fichier dans ${AIDA_HOME}/share/vista/vecteurs
    """
    fichier_txt = "{}/share/vista/vecteurs/{}/{}.txt".format(aida_home, aida_profil, plt)
    with open(fichier_txt, "w") as f :
        f.write("{:04d}{:02d}{:02d}\n".format(date_jour.year, date_jour.month, date_jour.day))
        for line in liste_vecteurs :
            try :
                f.write(line+"\n")
            except :
                continue
        try :
            os.chmod(fichier_txt, 0o766)
        except :
            pass


# On parse la ligne de commande
parser = argparse.ArgumentParser()
parser.add_argument("-p","--plateforme", help="nom de la plateforme à mettre à jour.")
args = parser.parse_args()

print("####### {}\n".format(dt.datetime.now()))

#
# Lecture du fichier de config plate-formes
#
plateformes = collections.defaultdict(dict)
config = configparser.ConfigParser()
config.read(aida_home+"/profils/"+aida_profil+"/plate-formes", encoding='ISO-8859-1')
for section in  config.sections() :
    if config.has_option(section, "abrev") :
        plateformes[section]["abrev"] = config.get(section, "abrev")
    else :
        plateformes[section]["abrev"] = None
    plateformes[section]["liste_vecteurs"] = []
#
# Si une plate-forme est passée en argument on l'utilise
#
if args.plateforme != None :
    if not args.plateforme in plateformes :
        print("La plateforme {} n'existe pas dans le fichier de config {}/profils/{}/plate-formes.".format(args.plateforme,aida_home, aida_profil))
        sys.exit(1)
    abrev = plateformes[args.plateforme]["abrev"]
    plateformes = collections.defaultdict(dict)
    plateformes[args.plateforme]["abrev"] = abrev
    plateformes[args.plateforme]["liste_vecteurs"] = []

#
# boucle sur les plateformes et mise à jour de la liste des vecteurs depuis le dernier update :
# la date du dernier update est la première ligne du fichier plateforme.txt
#
reg = re.compile('[a-zA-Z].*_[%0-9]+(\.v[1-9]+)*\.vbn$')
for plt in plateformes :
    print("Traitement de la plate-forme {} en cours ...".format(plt))

    rep_data = os.path.join (AIDA.AIDA_getenv('data'), plt)
    if not os.path.isdir(rep_data) :
        print("Le répertoire des data {} n'existe pas, on passe.".format(rep_data))
        print("Fin du traitement de la plate-forme {}.\n".format(plt))
        ecrit_fichier(plt, [])       
        continue

    #
    # On récupère le premier acqid existant pour cette plateforme dans la liste des fichiers INF
    #
    path_inf = '{}/{}*.inf'.format(AIDA_INF,(plateformes[plt]["abrev"]))
    list_acqid=[ l[l.rindex('/')+1: l.index('.inf')] for l in glob.glob(path_inf) ]
    list_acqid.sort(key=str.swapcase)
    if len(list_acqid) == 0 :
        print("Aucun acqid pour cette plate-forme")
        continue
    acq_id = AcqId (list_acqid[0])
    new_liste_vec = []
    #
    # On récupère la liste des vecteurs pour chaque journée depuis la date de début
    #
    try :
        while acq_id.acqid_to_date() <= date_jour :
            print("processing {} ...".format(str(acq_id)))
            liste_vec = []
            datapath=AIDA.ID_to_datapath (str(acq_id))
            if os.path.isdir(datapath) :
                liste_vec_tmp = os.listdir(datapath)
                liste_vec = [ x for x in liste_vec_tmp if reg.match(x)!=None ]
            new_liste_vec += liste_vec
            new_liste_vec = list(set(new_liste_vec))
            acq_id = acq_id + 1
    except Exception as e :
        pass

    new_liste_vec.sort()
    
    #
    # Ecriture du fichier
    #
    ecrit_fichier(plt, new_liste_vec)
    print("Fin du traitement de la plate-forme {}.\n".format(plt))
        
print("####### {} Traitement terminé.".format(dt.datetime.now()))
