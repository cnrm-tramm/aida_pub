#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Ce programme génère un fichier de type csv en utilisant un fichier de configuration de type ini passé en argument.
"""
import argparse
import configparser
import sys
import os
import datetime
import collections
AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
import AIDA
import AcqIdDoY
import numpy as np
import subprocess
import unicodedata


def read_config(file, start, end) :
    """
        Charge le fichier de config et fait quelques controles.
    """
    cfg = configparser.RawConfigParser()
    cfg.read(file)
    
    if not cfg.has_section('general') :
        sys.exit("Pas de section [general] dans le fichier de config ... on sort.")
    # valeurs par defaut
    if not cfg.has_option('general', 'format') :
        cfg.set('general', 'format', 'csv')
    if not cfg.has_option('general', 'entete') :
        cfg.set('general', 'entete', 'csv')
    if not cfg.has_option('general', 'fmt_date_heure') :
        cfg.set('general', 'fmt_date_heure', '%Y-%m-%dT%H:%M:%S')
    if not cfg.has_option('general', 'separateur') :
        cfg.set('general', 'separateur', ',')
    else :
        # separateur = espaces
        try :
            sep = cfg.get('general', 'separateur')
            if len(eval(sep).strip()) == 0 :
                cfg.set('general', 'separateur',eval(sep))
        except :
            pass
    if not cfg.has_option('general', 'missval') :
        cfg.set('general', 'missval', '3.4e+38')
    if not cfg.has_option('general', 'jours_manquants') :
        cfg.set('general', 'jours_manquants', 'oui')
    if not cfg.has_option('general', 'nasa_nom') :
        cfg.set('general', 'nasa_nom', 'Unknow,Unknown')
    if not cfg.has_option('general', 'nasa_organisme') :
        cfg.set('general', 'nasa_organisme', 'CNRM/GMEI')
    if not cfg.has_option('general', 'nasa_instrument') :
        cfg.set('general', 'nasa_instrument', 'Meteorological sensors')
    if not cfg.has_option('general', 'time_offset') :
        cfg.set('general', 'time_offset', '0')
    if not cfg.has_option('general', 'time_bounds') :
        cfg.set('general', 'time_bounds', 'False')    
    
    sections_attendues = cfg.get('general','champs').split(',')
    sections_presentes = [ x for x in sections_attendues if x in cfg.sections() ]
    if sections_presentes != sections_attendues :
        sys.exit("Tous les champs n'ont pas leur section  : {} on sort.".format([x for x in sections_attendues if x not in sections_presentes ]))
    sep = cfg.get('general', 'separateur').strip('"')
    cfg.str_format_datas = "{}" # date + séparateur
    for section in sections_presentes :        
        if not cfg.has_option(section, 'format') :
            cfg.set(section, 'format', 'E')
        cfg.str_format_datas += "{}{{}}".format(sep)
    
    # On détermine la frequence max des datas pour écrire les jours manquants :
    # - si l'attribut rft_time existe, on utilise le vecteur temps associé sinon 
    #   on utilise le vecteur temps qui a la fréquence la plus élevée
    # - le vecteur temps utilisé pour les données manquantes est stocké dans cfg.ref_time 
    def get_frequence(nom_vecteur) :
        str_rft_time = nom_vecteur.split('_')[-1]
        if str_rft_time[0] == '%' :
            return 1./float(str_rft_time[1:])
        else :
            return float(str_rft_time)
    
    cfg.ref_time = None    
    if  cfg.has_option('general', 'rft_time') :
        rft_time =  cfg.get('general', 'rft_time')
        cfg.ref_time, acqid = get_rft_time_ref(cfg, rft_time, start, end)
        cfg.frq_max = get_frequence(cfg.get(rft_time, 'vecteur'))
    else :
        frq_max = 0
        rft_time = None
        for section in sections_presentes :
            vecteur =  cfg.get(section, 'vecteur')
            frq = get_frequence(vecteur)
            if frq > frq_max :
                rft_time = section
                frq_max = frq
        cfg.ref_time, acqid = get_rft_time_ref(cfg, rft_time, start, end)
        cfg.frq_max = frq_max

    cfg.time_bnds = AIDA.time_to_data_bnds(acqid, cfg.ref_time.attributes["#hdr_name"])
    return cfg

def get_rft_time_ref(cfg, rft_time, start, end) :
    # on recherche le premier vecteur temps de référence disponible
    datedebut = datetime.datetime.strptime(start,"%Y%m%d")
    datefin = datetime.datetime.strptime(end,"%Y%m%d")
    dateencours = datedebut
    delta = datetime.timedelta(days=1)
    while dateencours <= datefin :
        # acqid
        try :
            plateforme = cfg.get(rft_time, 'plateforme')
        except :
            sys.exit("Pas de plateforme pour rft_time {} ... on sort.".format(rft_time))               
        if plateforme == "" :
            sys.exit("Pas de plateforme pour rft_time {} ... on sort.".format(rft_time))  
        acqid = "{}".format(AcqIdDoY.AcqIdDoY(plateforme=plateforme, date=dateencours))
        
        # lecture du vecteur
        try :        
            param = cfg.get(rft_time, 'vecteur')
        except NoOptionError :
            sys.exit("Pas de vecteur dans la section {} ... on sort.".format(rft_time))               
        if param == "" :
            sys.exit("Pas de vecteur dans la section {} ... on sort.".format(rft_time))           
      
        vect = readVecteur(acqid, param)
        if vect != None :
            vecteur_temps = AIDA.VectorMask(acqid, vect.attributes["ref_time"])
            if vecteur_temps != None :
                return vecteur_temps, acqid
        dateencours += delta
    sys.exit("Il n'existe aucun vecteur rft_time = {} sur la période.".format(rft_time))

def write_prod(cfg, debut, fin, output, append) :
    """
        Ecrit le fichier résultat
    """
    
    print("Lecture des vecteurs")
    datedebut = datetime.datetime.strptime(debut,"%Y%m%d")
    datefin = datetime.datetime.strptime(fin,"%Y%m%d")
    if datefin < datedebut :
        sys.exit("La date de fin est antérieure à la date de début ... on sort.")      
    delta = datetime.timedelta(days=1)
    vecteurs = collections.defaultdict(dict)
    big_time = [] # liste de l'ensemble des temps sur la période
    dict_time = {} # dictionnaire qui fait la correspondance entre le temps et les bornes de l'intervalle temporel
    vecteur_temps = None
    liste_data = [] # liste des datas de chaque paramètre
    liste_times = [] # liste des temps de chaque paramètre
    
   
    missval = cfg.get('general','missval')
    max_size_data = len(missval)
    #
    # Prise en compte du time_offset. Pour avoir toutes les données il faut :
    #  si time_offset>0 lire une journée avant le début de la période
    #  si time_offset<0 lire une journée après le début de la période 
    # On stocke la première et la dernière date pour ne conserver que les dates
    # qui nous interressent par la suite.
    #
    datedebut_avant_offset = datedebut
    datedefin_avant_offset = datefin
    if int(cfg.get('general','time_offset')) > 0 :
        datedebut = datedebut - delta
    if int(cfg.get('general','time_offset')) < 0 :
        datefin = datefin + delta
    time_debut = None
    time_fin = None

    dateencours = datedebut       
    while dateencours <= datefin :
        print("Lecture du {}".format(dateencours))
        for champ in cfg.get('general','champs').split(',') :
            # acqid
            try :
                plateforme = cfg.get(champ, 'plateforme')
            except NoOptionError :
                sys.exit("Pas de plateforme dans la section {} ... on sort.".format(champ))               
            if plateforme == "" :
                sys.exit("Pas de plateforme dans la section {} ... on sort.".format(champ))  
            acqid = "{}".format(AcqIdDoY.AcqIdDoY(plateforme=plateforme, date=dateencours))
            
            # lecture des vecteurs dans un dict avec pour clé le champ
            try :        
                param = cfg.get(champ, 'vecteur')
            except NoOptionError :
                sys.exit("Pas de vecteur dans la section {} ... on sort.".format(champ))               
            if param == "" :
                sys.exit("Pas de vecteur dans la section {} ... on sort.".format(champ))           
          
            vect = readVecteur(acqid, param)

            if vect is None:
                # on crée un vecteur vide de la taille de cfg.ref_time si jours_manquants = oui
                pseudo_data = np.empty(len(cfg.ref_time.data))
                pseudo_data[:] = np.nan
                vect = AIDA.VectorMask(acqid, cfg.get(champ, 'vecteur'), attributes={"misval":np.nan, "unit":"", "name":""}, data=pseudo_data)
                
                if cfg.get('general', 'jours_manquants') == "oui" :
                    vect.time = dateencours.toordinal() + cfg.ref_time.data / 86400.0
                    time_interval = (cfg.time_bnds / 86400.0) + dateencours.toordinal()
                    d_time = {}
                    for t,b in zip(vect.time, time_interval) :
                        d_time[ordinalToDate(t).strftime(cfg.get('general','fmt_date_heure'))] = b
                    dict_time.update(d_time)        
                else :
                    vect.data = np.ma.array([])
                    vect.time = np.array([])
            else :
                time_bnds = AIDA.time_to_data_bnds(acqid, cfg.ref_time.attributes["#hdr_name"])
                time_interval = (time_bnds / 86400.0) + dateencours.toordinal()
                d_time = {}
                for t,b in zip(vect.time, time_interval) :
                    d_time[ordinalToDate(t).strftime(cfg.get('general','fmt_date_heure'))] = b
                dict_time.update(d_time)
                # on récupère le vecteur temps si on ne l'a pas encore fait (utile pour entete nasa-ames)
                if vecteur_temps == None :
                    vecteur_temps = AIDA.VectorMask(acqid, vect.attributes["ref_time"])

            # on récupère time_debut et time_fin avant d'appliquer time_offset
            if dateencours == datedebut_avant_offset and time_debut is None :
                time_debut = list(vect.time)[0]
            if dateencours == datedefin_avant_offset and time_fin is None :
                time_fin = list(vect.time)[-1]
            vect.time += int(cfg.get('general','time_offset'))/86400
            try :
                vecteurs[champ].data = np.ma.concatenate([vecteurs[champ].data, vect.data])
                vecteurs[champ].time = np.ma.concatenate([vecteurs[champ].time, vect.time])
            except :
                vecteurs[champ] = vect
            
            # on récupère l'unité
            try :
                if vecteurs[champ].attributes["unit"] == "" :
                    if vect.attributes["unit"] != "" :
                        vecteurs[champ].attributes["unit"] = vect.attributes["unit"]
                    else :
                        vecteurs[champ].attributes["unit"] = 'unknown'
            except :
                vecteurs[champ].attributes["unit"] = 'unknown'

            try :
                if vecteurs[champ].attributes["name"] == "" :
                    vecteurs[champ].attributes["name"] = vect.attributes["name"]
            except :
                pass

            big_time += list(vect.time)

        dateencours += delta

    #print(big_time)
    #print(dict_time)
    # On séléctionne les données entre time_debut et time_fin
    # Pour éviter les erreur de comparaison de floats on défini une précision
    # qui vaut 1/4 période, qu'on utilise comme marge dans la comparaison
    precision = (1/(4*cfg.frq_max)) / 86400
    for champ, vect in vecteurs.items() :
        indexes = np.where((vect.time>=time_debut-precision)&(vect.time<=time_fin+precision))
        vecteurs[champ].time = vect.time[indexes]
        vecteurs[champ].data = vect.data[indexes]
        
    big_time = [ t for t in big_time if t>=time_debut-precision and t<=time_fin+precision ]

      
    #
    # Préparation des données pour l'écriture : forcage ou calcul.
    # Pour le forcage, on crée un tableau avec la string de forcage : le type du tableau
    # est S(tring) de taille=max(len(string_forcage), len(missval))
    #
    for champ in cfg.get('general','champs').split(',') :
        if len(vecteurs[champ].data) != 0 :
            try :
                if cfg.has_option(champ, 'valeur') :
                    valeur = cfg.get(champ, 'valeur')
                    if valeur == "missval" :
                        val_forcage = missval
                    else :
                        val_forcage = valeur
                    d = np.chararray(len(vecteurs[champ].data), max(len(val_forcage), len(missval)))
                    d[:] = val_forcage
                    if val_forcage == missval :
                        mask = len(vecteurs[champ].data)*[True]
                    else :
                        mask = vecteurs[champ].data.mask
                    dtype = "S{}".format(max(len(val_forcage), len(missval)))
                    vecteurs[champ].data = np.ma.array(list(d), mask=mask, dtype=dtype)
                else :
                    # opération sur les datas ?
                    try :
                        if cfg.has_option(champ, 'operation') :
                            def callback(x):
                                str_operation = "x{}".format(cfg.get(champ,'operation'))
                                return eval(str_operation)
                            d = list(map(callback, vecteurs[champ].data.data))
                            vecteurs[champ].data = np.ma.array(d, mask=vecteurs[champ].data.mask)
                    except Exception as e :
                        print("ERREUR : operation non reconnue = {} pour le champ {}.".format(cfg.get(champ,'operation'), champ))
                        print(e)
                        sys.exit(1)
            except Exception as e :
                print("ERREUR : valeur forcage = {} pour le champ {} incompatible avec le format {}".format(val_forcage, champ,cfg.get(champ,'format'))) 
                print(e)
                sys.exit(1)
                    
    # On transforme les datas en strings formattées sauf dans le cas d'un forcage ou on a déjà une chaine.
    # Le type des datas est S(tring) de taille=max(max(taille data), len(missval))
    for champ in cfg.get('general','champs').split(',') :
        if len(vecteurs[champ].data) != 0 :
            if not cfg.has_option(champ, 'valeur') :    
                mask = np.ma.getmaskarray(vecteurs[champ].data)
                data_string = "[\"{{:{}}}\".format(x) if m == False else \"{{}}\".format(x) for x,m in zip(vecteurs[champ].data.data, mask)]".format(cfg.get(champ,'format'))
                try :
                    d = eval(data_string)
                    size_type = max(max([len(v) for v in d]), len(missval))
                    if max_size_data < size_type :
                        max_size_data = size_type
                    dtype = "S{}".format(size_type)        
                    vecteurs[champ].data = np.ma.array(d, mask=np.ma.getmask(vecteurs[champ].data), dtype=dtype)
                except Exception as e :
                    print("ERREUR : format = {} incompatible avec les données pour le champ {}.".format(cfg.get(champ,'format'), champ))
                    print(e)
                    sys.exit(1)

    # on enregistre les datas et les times dans des listes        
    for champ in cfg.get('general','champs').split(',') :
        liste_data.append(vecteurs[champ].data)
        liste_times.append(vecteurs[champ].time)

    #
    # FIN de la lecture des vecteurs dans le tableau vecteurs.
    #

    
    # temps de reference ?
    if cfg.has_option('general', 'rft_time') :
        try :
            big_time = vecteurs[cfg.get('general', 'rft_time')].time
        except :
            sys.exit("Problème avec le rft_time de la section general ... on sort.")
    #
    # Ecriture dans le fichier output
    #
    print("début écriture ... {}".format(datetime.datetime.now()))
    mode = 'w'
    if append :
        mode = 'a'
    with open(output, mode) as output_file:
        # écriture de l'entete sauf en mode append
        if not append :
            if cfg.get('general','format') == "nasa-ames-1001" :
                write_header_nasa_ames(cfg, vecteurs, len(liste_data), big_time, vecteur_temps, output_file)            
            else :
                if cfg.get('general','entete') != "non" :
                    if cfg.get('general','entete') != "dygraphs" :
                        try :
                            output_file.write("#"+cfg.get('general', 'description')+"\n")
                        except :
                            pass                        
                        output_file.write("#Fichier produit le : {}\n#".format(datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y à %H:%M:%S UTC")))
                        for champ in cfg.get('general','champs').split(',') :
                            output_file.write(cfg.get(champ, "vecteur")+" ")
                        output_file.write("\n")
                    if cfg.get('general','time_bounds').lower() != "false" :
                        ligne_champs = "TIMESTAMP_START{}TIMESTAMP_END".format(cfg.get('general','separateur'))
                        ligne_unites = "{}{}{}".format(
                                                    cfg.get('general','fmt_date_heure'),
                                                    cfg.get('general','separateur'),
                                                    cfg.get('general','fmt_date_heure'))
                    else :
                        ligne_champs = "TIMESTAMP"
                        ligne_unites = cfg.get('general','fmt_date_heure')  
                    for champ in cfg.get('general','champs').split(',') :
                        ligne_champs = "{}{}{}".format(ligne_champs, cfg.get('general','separateur'), champ)
                        if cfg.has_option(champ,'unite') :
                            unite = cfg.get(champ,'unite')
                        elif vecteurs[champ] != None and 'unit' in list(vecteurs[champ].attributes.keys()) :
                            unite = vecteurs[champ].attributes['unit']
                        else :
                            unite = "unknown"
                        
                        ligne_unites = "{}{}{}".format(ligne_unites, cfg.get('general','separateur'), unite)
                    output_file.write(ligne_champs+'\n')
                    if cfg.get('general','entete') != "dygraphs" :
                        output_file.write(ligne_unites+'\n')
        #
        # écriture des datas
        #
        # conversion des dates en strings (fonction du format)
        t0 = time_debut
        full_time = list(set(big_time))
        full_time = np.asarray(sorted(full_time))
        try :
            if cfg.get('general','format') == "nasa-ames-1001" :
                full_time_string = [ "{}{}{}{}{}".format((ordinalToDate(t) - ordinalToDate(t0)).total_seconds(),cfg.get('general','separateur'),ordinalToDate(t).strftime("%Y%m%d"),cfg.get('general','separateur'),ordinalToDate(t).strftime("%H%M%S.%f")) for t in full_time ]
            else :                
                full_time_string = [ ordinalToDate(t).strftime(cfg.get('general','fmt_date_heure')) for t in full_time ]
                if cfg.get('general','time_bounds').lower() != "false" :  
                    full_time_string0 = [ ordinalToDate(dict_time[t][0]).strftime(cfg.get('general','fmt_date_heure')) for t in full_time_string ]
                    full_time_string1 = [ ordinalToDate(dict_time[t][1]).strftime(cfg.get('general','fmt_date_heure')) for t in full_time_string ]
                    full_time_string = ["{}{}{}".format(t0,cfg.get('general','separateur'),t1) for t0,t1 in zip(full_time_string0,full_time_string1)]
                    
        except Exception as e :
            print(e)
            print("ERREUR : impossible de convertir les dates en strings.")
            sys.exit(1)           
        full_data = np.chararray((len(full_time), len(vecteurs)), max_size_data)
        full_data [:] = missval
        
        if len(full_data) == 0 :
            print("\nAucune donnée à écrire... Positionner l'attribut de configuration 'jours_manquants = oui' pour écrire des lignes dans le fichier résultat.\n")
        else :
            idx_col = 0
            for data, time in zip (liste_data, liste_times):
                indexes = np.argwhere(np.in1d(full_time, time))
                indexes = indexes.T
                data = data.filled(missval)
                try :
                    full_data[indexes, idx_col] = np.asarray(data[:])
                except Exception as e :
                    print(e)
                    pass
                idx_col += 1
            # ajout de la date comme premiere colonne
            #print(full_data)
            full_data_string = np.c_[full_time_string, full_data]
            # écriture du tableau dans le fichier
            if mode == 'a' :
                output_file.write("\n")
            cmd_ecriture = "output_file.write(\"\\n\".join([\"{}\".format(*d) for d in full_data_string]))".format(cfg.str_format_datas)
            eval(cmd_ecriture)

        print("fin écriture ... {}".format(datetime.datetime.now()))
        
        
def write_header_nasa_ames(cfg, vecteurs, nb_champs, big_time, vecteur_temps, output_file) :
    """
        Ecriture de l'en-tete NASA-AMES
    """
    
    lignes = []
    # nom, prenom
    lignes.append(cfg.get('general','nasa_nom'))
    # organisme
    lignes.append(cfg.get('general','nasa_organisme'))
    # instrument
    lignes.append(cfg.get('general','nasa_instrument'))
    # campagne
    if not cfg.has_option('general', 'nasa_campagne') :
        sys.exit("Il manque le champ nasa_campagne pour pouvoir produire le format nasa-ames ... on sort.")
    else :
        lignes.append(cfg.get('general','nasa_campagne'))
    # number of files in dataset, file number (1,1)
    lignes.append("1 1")
    # date de la première mesure et date du jour
    date_debut = ordinalToDate(sorted(set(big_time))[0]).strftime("%Y %m %d")
    lignes.append("{} {}".format(date_debut, datetime.datetime.now().strftime("%Y %m %d")))
    # intervalle de temps (0 = non régulier)
    lignes.append("0")
    # description de la variable temps
    try :
        temps = vecteur_temps.attributes["name"]
    except :
        temps = "unknow"
    lignes.append("{} (seconds since {} 00:00:00 UTC)".format(temps, ordinalToDate(sorted(set(big_time))[0]).strftime("%Y-%m-%d")))
    # nombre de variables (+2 pour les champs date et time)
    lignes.append("{}".format(nb_champs + 2))
    # facteur d'échelle pour chaque champs (on met des 1)
    scale=""
    for i in range(nb_champs + 2) : #(+2 pour date et time)
        scale += "1 "
    lignes.append(scale)
    # valeurs manquantes pour chaque champs 
    mqt=""
    for i in range(nb_champs + 2) : #(+2 pour date et time)
        mqt += "{} ".format(cfg.get('general', 'missval'))
    lignes.append(mqt)
    # liste des variables
    lignes.append("date () : date (YYYYMMDD)")
    lignes.append("time (second) : UTC time (HHMMSS.sss)")
    for champ in cfg.get('general','champs').split(',') :
        pipe = subprocess.Popen(". $AIDA_HOME/lib/AIDA_shell_lib.sh; AIDA_to_CF_name {}".format(cfg.get(champ, 'vecteur')), stdout=subprocess.PIPE, shell=True)
        variable = pipe.communicate()[0][:-1]
        info_variable = ""
        if "name" in list(vecteurs[champ].attributes.keys()) :
            info_variable = to_ascii(vecteurs[champ].attributes["name"])
        
        if cfg.has_option(champ,'unite') :
            unite = cfg.get(champ,'unite')
        elif vecteurs[champ] != None and 'unit' in list(vecteurs[champ].attributes.keys()) :
            unite = vecteurs[champ].attributes['unit']
        else :
            unite = "unknown"
        lignes.append("{} ({}) : {}".format(variable, unite, info_variable))    
    # commentaires
    lignes.append("0")
    lignes_comments = ["--------------------------------"]
    if cfg.has_option('general', 'nasa_commentaire') :
        comments = to_ascii(cfg.get('general','nasa_commentaire')).split("##")
        lignes_comments += comments
    for champ in cfg.get('general','champs').split(',') :
        lignes_comments.append("{} : {}-{}".format(champ, cfg.get(champ, 'plateforme'), cfg.get(champ, 'vecteur')))
    lignes_comments.append("--------------------------------")
    
    lignes.append("{}".format(len(lignes_comments)))
    lignes += lignes_comments    
    lignes.insert(0,"{} {}".format(len(lignes)+1,1001))
    for l in lignes :
        output_file.write(l+"\n")

def readVecteur(acqId, param, refTime=None):
    """
        Lit un vecteur et son ref_time.
        Le ref_time sera exprimé en valeur numérique utilisé
        dans le module  "datetime" de python, matplotlib, etc.
        le ref_time est stocké dans l'attribut "time" du vecteur (vect.time)
        le nom du ref_time est stocké dans l'attribut "time_name" du vecteur
    """
    try:
        vect = AIDA.VectorMask(acqId, param)
    except IOError as excpt:
        print(("Jour vide pour %s de %s: " % (param, acqId), str(excpt)))
        return None

    if 'ref_time' not in vect.attributes:
        print(("Pas de ref_time dans %s de %s" % (param, acqId)))
        return None
    if refTime is None:
        ref_time = vect.attributes['ref_time']
    time = AIDA.Vector(acqId, ref_time)
    if len(time.data) != len(vect.data):
        print(("len(%s) = %d, ref_time = %s, len=%d" % (param, len(vect.data),
                              ref_time, len(time.data))))
        return None

    try :
        date_acq = AIDA.Inf(acqId).get_date_acq()
    except Exception :
        print(("Erreur de lecture du fichier INF pour {}.".format(acqId)))
        return None
    # Conversion du temps du vecteur en nombre de jour depuis le 01/01/0000 (calendrier grégorien proleptique)
    vect.time = date_acq.toordinal() + time.data / 86400.0
    vect.time_name = ref_time
    return vect

def ordinalToDate(ordinal) :
    """
        Retourne une date à partie d'un ordinal
    """
    nbsec = round((ordinal-int(ordinal)) * 86400, 3)
    #nbsec = (ordinal-int(ordinal)) * 86400
    date = datetime.datetime.fromordinal(int(ordinal))
    date += datetime.timedelta(seconds=nbsec)
    return date

def to_ascii(mystring) :
    """
        Supprime les accents.
    """
    try :
        s1 = str(mystring,'utf-8')
    except :
        try :
            s1 = str(mystring,'iso-8859-1')
        except Exception as e:
            sys.exit(e)
    s = unicodedata.normalize('NFD', s1).encode('ascii', 'ignore')
    return s


"""
    Main
"""
print(datetime.datetime.now())
parser = argparse.ArgumentParser()
parser.add_argument("-a","--append", help="ouvre le fichier de sortie en mode ajout(suppression automatique des lignes d'en-tête)", action="store_true")
parser.add_argument("-f","--file", required="True", help="fichier de configuration")
parser.add_argument("-s","--start", required="True",help="date de début : AAAAMMJJ")
parser.add_argument("-e","--end", required="True", help="date de fin : AAAAMMJJ")
parser.add_argument("-o","--output", required="True", help="fichier de sortie")


try :
    args = parser.parse_args()
except :
    if sys.exc_info()[1].code == 0 :
        str_config =   "\nDescription du fichier de config (avec les valeurs par défaut) :\n"
        str_config +=  "[general]\n"
        str_config +=  "format = csv                       // format du fichier de sortie : csv ou nasa-ames-1001\n"
        str_config +=  "entete = csv                       // écriture d''une ligne d''entete (csv, dygraphs ou non)\n"
        str_config +=  "description =                      // première ligne de l'en-tête\n"
        str_config +=  "fmt_date_heure = %Y-%m-%dT%H:%M:S  // format de type strftime\n"
        str_config +=  "separateur = ,                     // séparateur des colonnes\n"
        str_config +=  "champs =                           // liste des parametres qui donneront lieu à une section\n"   
        str_config +=  "missval = 3.4e+38                  // valeur manquante\n"
        str_config +=  "rft_time =                         // parametre de reference pour le temps\n"
        str_config +=  "jours_manquants = oui              // ajoute des lignes pour les jours manquants\n"
        str_config +=  "time_offset = 0                    // permet de gérer des décalages de dates : si >0 on lit la journée précédente, si<0 on lit la journée suivante pour récupérer les dates dont on a besoin.\n"
        str_config +=  "time_bounds = False                // si true écrit l'intervalle de dates en début de chaque ligne au lieu d'une simple date.\n\n"
        str_config +=  "# paramètres pour l'en-tete nasa-ames: \n"
        str_config +=  "nasa_nom = unknown, unknown        // nom, prenom\n"
        str_config +=  "nasa_organisme = CNRM/GMEI         // organisme\n"
        str_config +=  "nasa_instrument = Meteorological sensors      // instrument\n"
        str_config +=  "nasa_campagne =                    // nom de la campagne ou du projet\n"
        str_config +=  "nasa_commentaire =                // commentaire de fin d''entete : séparateur pour retour à la ligne = ##\n"
        str_config +=  "\n"
        str_config +=  "# Viennent ensuite une section par champ, par exemple :\n"
        str_config +=  "[hum_sol -5cm]\n"
        str_config +=  "plateforme =        // nom abrégé de la plateforme ex : Tf, Py, ...\n"
        str_config +=  "vecteur =           // nom du fichier vecteur sans extension correspondant ex : hum_sol_5cm_Eti\n"
        str_config +=  "format = E          // ex : 6.2f sur 6 caracteres dont 2 decimales.  0=6.2f complète avec des 0 à gauche.\n" 
        str_config +=  "                       (selon la syntaxe de la methode format https://www.python.org/dev/peps/pep-3101/)\n"
        str_config +=  "unite =             // unité : si non précisée on prend celle du vecteur\n"
        str_config +=  "operation =         // opération (simple) à effectuer sur les valeurs ex : *100\n"
        str_config +=  "valeur =            // valeur de forcage ou missval : le type doit être compatible avec le format"
        sys.exit(str_config)
    else :
        sys.exit(1)

cfg = read_config(args.file, args.start, args.end)
write_prod(cfg, args.start, args.end, args.output, args.append)

