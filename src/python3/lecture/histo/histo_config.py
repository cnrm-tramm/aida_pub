#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# DATE : 09/11/2016
# AUTEUR : J. Couzinier CNRM/GMEI/TRAMM
# ROLE : Lit un fichier de type histo et retourne le fichier de config à utiliser pour
#        le coupleur et la date donnés. 
# USAGE : histo_config.py [-h] [-d date] -f fic_histo coupleur
#
# ATTENTION : on utilise python3 afin de pouvoir forcer le delimiter du Configparser
#

import sys
import argparse
import configparser
import datetime as dt

def str2datetime(str_time):
    """
        Convertit une chaine de caractère AAAAMMJJHHMMSS.sss en datetime.
        
        :param str_time: la chaîne à convertir
        :type str_time: str
        :return : un datetime ou None si la chaîne n'a pas pu être convertie
        :rtype : datetime
    """
    
    try :
        n = len(str_time)
        if n > 14 :
            time = dt.datetime.strptime(str_time,"%Y%m%d%H%M%S.%f")
        elif n == 14 :
            time = dt.datetime.strptime(str_time,"%Y%m%d%H%M%S")
        elif n == 12 :
            time = dt.datetime.strptime(str_time,"%Y%m%d%H%M")
        elif n == 10 :
            time = dt.datetime.strptime(str_time,"%Y%m%d%H")
        elif n == 8 :
            time = dt.datetime.strptime(str_time,"%Y%m%d")
        elif n == 6 :
            time = dt.datetime.strptime(str_time,"%Y%m")
        elif n == 4 :
            time = dt.datetime.strptime(str_time,"%Y")    
    except :
        time = None
    return time

#
# controle des arguments
#
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", required=True, help="fichier de configuration histo.")
parser.add_argument("-d", "--date", help="date YYYYMMDDHHMISS (défaut = maintenant).")
parser.add_argument("coupleur", help="coupleur.")

args = parser.parse_args()

#
# Traitement de la date
#
if args.date == None :
    # maintenant
    the_date = dt.datetime.now()
else :
    the_date = str2datetime(args.date)
if the_date == None :
    print("Erreur : l'argument -d/--date n'as pas le bon format.")
    sys.exit(1)

#
# Lecture du fichier de config
#
# Lecture du fichier de config
config = configparser.ConfigParser(delimiters=('='))
config.optionxform = str # pour conserver les majuscules sur les options
try :
    if len(config.read(args.file)) == 0 :
        print("Erreur : le fichier de config {} n'existe pas...".format(args.file))
        sys.exit(1)
except Exception as e :
    print("Erreur : erreur à la lecture du fichier {}".format(args.file))
    print(e)
    sys.exit(1)
    
#
# On cherche le fichier de config correspondant à la date et au coupleur
#
if not config.has_section(args.coupleur) :
    print("Erreur : le coupleur {} n'est pas décrit dans le fichier de config {}.".format(args.coupleur, args.file))
    sys.exit(1)
the_file = None
for interval in config.options(args.coupleur) :
    try :
        dates = interval.split(' ')
        date0 = dt.datetime.strptime(dates[0].strip(), "%Y-%m-%dT%H:%M:%S")
        date1 = dt.datetime.strptime(dates[1].strip(), "%Y-%m-%dT%H:%M:%S")
    except Exception as e :
        print("Erreur : erreur à la lecture des dates dans le fichier {}.".format(args.file))
        print(e)
        sys.exit(1)
    if the_date >= date0 and the_date <= date1 :
        the_file = config.get(args.coupleur, interval)
        break
if the_file == None :
    print("Erreur : pas de fichier de config trouvé pour le coupleur {} à la date {}".format(args.coupleur, dt.datetime.strftime(the_date, "%Y-%m-%dT%H:%M:%S")))
    sys.exit(1)
else :
    print(the_file)
    
sys.exit(0)
        
        
        