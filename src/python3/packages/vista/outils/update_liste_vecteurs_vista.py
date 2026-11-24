#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Met à jour la liste des vecteurs utilisée par vista.
    Usage : update_liste_vecteurs_vista.py [ -p||--plateforme ]
"""

import os
import sys
import datetime as dt
import configparser
import collections
import re
import argparse
import glob

AIDA_HOME = os.getenv('AIDA_HOME')
AIDA_PROFIL = os.getenv('AIDA_PROFIL')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AIDA_HOME, 'lib', PYTHON_X_Y))
import AIDA
from AcqId import *
AIDA_META = AIDA.AIDA_getenv ('meta')
AIDA_INF = os.path.join(AIDA_META, "INF")


# On parse la ligne de commande
parser = argparse.ArgumentParser()
parser.add_argument("-p","--plateforme", help="nom de la plateforme à mettre à jour.")
parser.add_argument("-d","--date", help="date de la dernière mise à jour AAAAMMJJ.")
args = parser.parse_args()

print("####### {}\n".format(dt.datetime.now()))

#
# Lecture du fichier de config plate-formes
#
plateformes = collections.defaultdict(dict)
config = configparser.ConfigParser()
config.read(AIDA_HOME+"/profils/"+AIDA_PROFIL+"/plate-formes", encoding = "ISO-8859-1")
for section in  config.sections() :
    if section == "FORMAT" :
        continue
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
        print("La plateforme {} n'existe pas dans le fichier de config {}/profils/{}/plate-formes.".format(args.plateforme, AIDA_HOME, AIDA_PROFIL))
        sys.exit(1)
    abrev = plateformes[args.plateforme]["abrev"]
    plateformes = collections.defaultdict(dict)
    plateformes[args.plateforme]["abrev"] = abrev
    plateformes[args.plateforme]["liste_vecteurs"] = []
    
date_jour = dt.datetime.now()

#
# boucle sur les plateformes et mise à jour de la liste des vecteurs depuis le dernier update :
# la date du dernier update est la première ligne du fichier plateforme.txt
#
reg = re.compile('[a-zA-Z].*_[%0-9]+(\.v[1-9]+)*\.vbn$')
for plt in plateformes :
    print("Traitement de la plate-forme {} en cours ...".format(plt))
    date_last_update = None
    fic_liste_vecteurs = "{}/share/vista/vecteurs/{}/{}.txt".format(AIDA_HOME, AIDA_PROFIL, plt)
    try :
        with open(fic_liste_vecteurs) as f :
            date_last_update = f.readline()[0:-1]
            if args.date != None :
                date_last_update = args.date[0:8]
            date_debut = dt.datetime.strptime(date_last_update,"%Y%m%d")
            for line in f :
                plateformes[plt]["liste_vecteurs"].append(line[0:-1])
    except Exception as e :
        print("Le fichier {} n'existe pas, on va le créer.".format(fic_liste_vecteurs))
        print("La recherche se fait par défaut sur le dernier mois de donnés disponibles...\n")
        #on se prend une marge d'1 mois pour construire la liste des vecteurs
        #date_debut = date_jour - dt.timedelta(days=31)
        date_debut = None
        
    plateformes[plt]["liste_vecteurs"].sort()

    #
    # On récupère le dernier acqid pour cette plateforme dans la liste des fichiers INF
    #
    path_inf = '{}/{}*.inf'.format(AIDA_INF,(plateformes[plt]["abrev"]))
    list_acqid=[ l[l.rindex('/')+1: l.index('.inf')] for l in glob.glob(path_inf) ]
    list_acqid.sort(key=str.swapcase)
    try :
        acq_id = AcqId (list_acqid[-1])
        if date_debut is None :
            date_debut = acq_id.acqid_to_date() - dt.timedelta(days=31)
    except :
        if len(list_acqid) !=0 :
            continue
    new_liste_vec = plateformes[plt]["liste_vecteurs"][:]
    #
    # On récupère la liste des vecteurs pour chaque journée depuis le dernier update
    #
    try :
        while acq_id.acqid_to_date() >= date_debut :
            liste_vec = []
            datapath=AIDA.ID_to_datapath (str(acq_id))
            if os.path.isdir(datapath) :
                liste_vec_tmp = os.listdir(datapath)
                liste_vec = [ x for x in liste_vec_tmp if reg.match(x)!=None and x.endswith(".vbn") ]
            new_liste_vec += liste_vec
            new_liste_vec = list(set(new_liste_vec))
            acq_id = acq_id - 1
    except Exception as e :
        pass
    new_liste_vec.sort()
    
    fichier_txt = "{}/share/vista/vecteurs/{}/{}.txt".format(AIDA_HOME, AIDA_PROFIL, plt)
    if new_liste_vec ==  plateformes[plt]["liste_vecteurs"] :
        print("Pas de changement depuis le dernier update.")
        try :
            with open(fichier_txt, "r") as f :
                last_update = f.readline()
                last_update = "{:04d}{:02d}{:02d}\n".format(date_jour.year, date_jour.month, date_jour.day)
        except Exception :
            last_update = "{:04d}{:02d}{:02d}\n".format(date_jour.year, date_jour.month, date_jour.day)
        with open(fichier_txt, "w") as f : 
            f.write(last_update)
            for line in plateformes[plt]["liste_vecteurs"] :
                try :
                    f.write(line+"\n")
                except :
                    continue
            try :
                os.chmod(fichier_txt, 0o766)
            except :
                pass
    else :
        print("Nouveaux vecteurs depuis le dernier update.")
        with open(fichier_txt, "w") as f :
            f.write("{:04d}{:02d}{:02d}\n".format(date_jour.year, date_jour.month, date_jour.day))
            for line in new_liste_vec :
                f.write(line+"\n")
            try :
                os.chmod(fichier_txt, 0o766)
            except :
                pass
    print("Fin du traitement de la plate-forme {}.\n".format(plt))
        

