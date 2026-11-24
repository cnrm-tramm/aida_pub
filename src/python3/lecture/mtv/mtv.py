#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import logging
from logging.handlers import RotatingFileHandler
AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
import AIDA  # @UnresolvedImport
import readers
import temps
import datetime as dt
import re
import getpass
import locale

def header_from_infos(infos):
    """
        Construit un header de vecteur à partir des infos lues
    """
    header = {}
    # paramètres connus de la config qui ne sont pas dans l'en-tête du vecteur
    items_connus = ['instru', 'invval_in', 'invval_out', 'misval_in', 'misval_out', 'ignore', 'nom_variable']

    header["ref_time"] = infos["temps"]
    header["origine"] = "lecture"
    header["fct_origine"] = " ".join(sys.argv)
    for i in infos :
        if i != "temps" and i not in items_connus :
            header[i] = infos[i]
        
    return header

def vectorise_data(reader, param, value, args, start, end):
    """
        Vectorise un paramètre : on retourne le premier et dernier temps de la série,
        utiles pour la création du fichier INF.
    """
    data_temps = reader.datas[value["infos"]["temps"]]["data"]
    freq = reader.datas[value["infos"]["temps"]]["infos"]["freq_ech"]
    try :
        time_bnds = reader.datas[value["infos"]["temps"]]["infos"]["time_bnds"]
    except :
        time_bnds = None
    if value["infos"]["ignore"] == "False" :                
        if duree_vecteur == "acquisition" :
            if args.start == None and args.end == None :
                data = value["data"]
                start = data_temps[0]
                end = data_temps[-1]
            else :
                data = [ x for x,y in zip(value["data"], data_temps) if y>=start and y<end ]
                data_temps = [ x for x in data_temps if x>=start and x<end ]
        else :                
            start,end = temps.acqid2periode(a, freq, time_bnds)
            data = [ x for x,y in zip(value["data"], data_temps) if y>=start and y<end]
            data_temps = [ x for x in data_temps if x>=start and x<end ]
            if len(data) == 0 or len(data_temps) == 0 :
                return None,None
            
        # on contruit le nom du vecteur : ajout de _cal (sauf si _raw ou vecteur temps ou option -nc/--no-cal) et de la fréquence
        vec_name =param
        if vec_name[-4:] != "_raw" and value["infos"]["temps"] != param and args.no_cal != True :
            vec_name += "_cal"
        if freq < 1  and freq != 0 :
            vec_name = "{}_%{}".format(vec_name, int(round(1./freq)))
        else :
            vec_name = "{}_{}".format(vec_name, int(freq))
        # si on vectorise un temps, on le convertit en deltas de secondes
        if  value["infos"]["temps"] == param :
            data = temps.timedata2timeaida(data, start)
        
        # construction du header à partir de la structure infos
        
        # on modifie le nom du vecteur temps (on fait une copie sinon on a des soucis avec les vecteurs temps)
        infos = value["infos"].copy()
        if freq < 1 and freq != 0 :
            infos["temps"] = "{}_%{}".format(infos["temps"], int(round(1./freq)))
        else :
            infos["temps"] = "{}_{}".format(infos["temps"], int(freq))
        infos["temps"] =  re.sub(r'[^a-zA-Z0-9_%:@.!#,{}]', "_", infos["temps"])
     
        infos["freq_ech"] = freq
        
        try :
            famille = AIDA.AIDA_abrev_to_family(param[0:param.index('_')])
        except Exception as e :
            print(e)
            logger.warning("impossible de determiner la famille pour {}".format(param))
            famille = "inconnue"
        if "inconnue" in famille :
            infos["famille"] = "xxx"
            vec_name = "xxx_"+vec_name
        else :
            infos["famille"] = famille
        
        # on remplace les caractères interdits dans le nom des vecteurs par des "_"
        vec_name =  re.sub(r'[^a-zA-Z0-9_%:@.!#,{}]', "_",vec_name)
        shape = np.asarray(data).shape
        if len(shape) == 1 :
            infos["dim_array"] = "1"
        else :
            infos['dim_array'] = '|'.join([str(i) for i in shape[1:] ])
        
        # si on vectorise un temps, on positionne time_bnds et datation_convention
        if  value["infos"]["temps"] == param :
            if not "datation_convention" in  infos.keys() :
                datation_convention = temps.get_datation_convention(freq, time_bnds)
                if datation_convention is not None :
                    infos["datation_convention"] = "{:.1f}".format(datation_convention)
            if time_bnds is not None :
                infos["time_bnds"] = time_bnds
                
        # on ajoute date_vol (date de la première donnée) pour les acqid de type acquisition
        try :
            if duree_vecteur == "acquisition" :
                date_vol = dt.datetime.strftime(data_temps[0], "%d/%m/%y %H:%M:%S")
                infos["date_vol"] = date_vol
        except :
            pass              
        header = header_from_infos(infos)
        
        force = False
        if args.force :
            force = True
        try :   
            vect = AIDA.Vector (a, vec_name, header, np.asarray(data))        
            try :
                logger.info("{} : on vectorise {} entre {} et {} nb={}".format(a, vec_name, start, end, len(data)))
                if len(data) == 0 :
                    logger.debug("{} : pas de data pour {}".format(a, vec_name))
                else :    
                    logger.debug("{} : première data : {} dernière data : {}".format(a, data[0], data[len(data)-1]))                
                msg = vect.write(force=force)
                if msg != "" :
                    logger.info("{}".format(msg))
            except Exception as e :
                logger.error("{} échec de la vectorisation du paramètre {}".format(a,vec_name))
                logger.error(e)
        except Exception as e :
            logger.error("{} échec à la création du vecteur pour le paramètre {}".format(a,vec_name))
            logger.error(e)
    
        # on assure que data_temps contient au moins 2 valeurs (ut, même si on a rien vectorisé
        if len(data_temps) == 1 :# une seule valeur trouvée dans les datas pour cet acqid
            data_temps.append(end)      
        return data_temps[0],data_temps[-1]
    else : # ignore = True on ne vectorise pas
        return None,None
    
def ecrit_fichier_inf(acqid, start, end):
    """
        Ecrit le fichier INF associé à acqid (sans écrasement)
    """
    if args.campagne == None :
        campagne = "inconnue"
    else :
        campagne = args.campagne
    if args.plateforme == None :
        plateforme, _annee, _num = AIDA.ID_to_full(acqid)            
    else :
        plateforme = args.plateforme
    
    dico_acq_meta = {
                     'FORMAT': {
                                'format_coord ' : 'C (D)DDdMM.X(X)  (C=Lettre (N, E, S ou W), (D)DD=degres 2 ou 3 chiffres, MM=minutes, (X)=fraction decimale de minutes)',
                                'format_date' : 'JJ/MM/AAAA/HHMMSS (JJ=jour, MM=mois, AAAA=annee, le tout en chiffres)',
                                'format_duree' : 'HH.D (HH=heure, D=dixiemes d''heure)',
                                'format_heure' : 'HHMMSS (HH=heures, MM=minutes,SS=secondes)'
                                }, 
                     'IDENTIFICATION': {
                                        'plate-forme':plateforme,
                                        'acq_id':acqid,
                                        'date':dt.datetime.strftime(start, "%d/%m/%Y"),
                                        'campagne':campagne
                                        },
                     'ACQUISITION': {
                                    'debut_acquisition':dt.datetime.strftime(start, "%d/%m/%Y/%H%M%S"),
                                    'fin_acquisition':dt.datetime.strftime(end, "%d/%m/%Y/%H%M%S")
                                     }
                     }
    
    AIDA.ecrit_inf (acqid, dico_acq_meta, force=False)
                        
def trace_datas(reader):
    """
        Quick-look très peu évolué des datas dont le champ ignore != True
    """
    params_plotted = [] 
    try :
        for param, value in list(reader.datas.items()) :   
            try :
                if value["infos"]["ignore"] == "False"  and (value["infos"]["temps"] != value["infos"]["name"]):
                    params_plotted.append(param)
            except :
                pass
    except :
        pass
    finally :
        if len(params_plotted) == 0 :
            reader.logger.info("Aucun pamètre à tracer")
            sys.exit(0)
    plt.figure(1)
    num_rows = int(len(params_plotted)/2) + len(params_plotted)%2
    pos=0
    for param in params_plotted :
        pos = pos+1
        plt.subplot(num_rows,2,pos)
        plt.title(""+param)
        temps = reader.datas[param]["infos"]["temps"]
        if reader.datas[param]["data"].size - np.count_nonzero(np.isnan(reader.datas[param]["data"])) != 0 :
            plt.plot(reader.datas[temps]["data"], reader.datas[param]["data"])
        else :
            plt.text(0.1, 0.5, "Pas de données")
        reader.logger.info("On trace {}.".format(param))
    plt.show()  





###################################################
#
# MAIN
#
###################################################

#
# logger
#
       
# création d'un premier handler de type console
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
try :
    mtv_level = os.getenv("MTV_LEVEL")
    eval("stream_handler.setLevel(logging.{})".format(mtv_level))
except :
    stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s :: %(process)s :: %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
   
#
# controle des arguments
#
parser = argparse.ArgumentParser()
parser.add_argument("source", nargs="*", help="fichier(s) ou répertoire(s)")
parser.add_argument("-a", "--acqid", help="acqid.")
parser.add_argument("-p", "--plateforme", help="nom long de la plateforme.")
parser.add_argument("-c", "--campagne", help="campagne(utile pour renseigner le fichier INF).")
parser.add_argument("-f", "--file", help="fichier de config.")
parser.add_argument("-t", "--type", help="type de fichier à lire.")
parser.add_argument("-s", "--start", help="début (inclus) : AAAA[MMJJHHMMSS.sss]")
parser.add_argument("-e", "--end", help="fin (exclus) : AAAA[MMJJHHMMSS.sss]")
parser.add_argument("-n", "--dry-run", help="pas d'écriture.", action="store_true")
parser.add_argument("-F", "--force", help="écrase les fichiers vecteurs existants.", action="store_true")
parser.add_argument("-g", "--graphic", help="trace les données.", action="store_true")
parser.add_argument("-C", "--config", help="aide sur la config du reader CONFIG")
parser.add_argument("-k", "--keep", help="conserver les valeurs hors_normes", action="store_true")
parser.add_argument("-L", "--log_dir", help="répertoire des logs (fichier mtv.log).")
parser.add_argument("-l", "--logger", help="fichier de log (chemin complet) dans lequel mtv rajoute ses logs.")
parser.add_argument("-nc", "--no-cal", help="pas de suffixe cal.", action="store_true")
parser.add_argument("-nk", "--no-checksum", help="pas de checksum.", action="store_true")
parser.add_argument("-r", "--readers", help="liste des readers.", action="store_true")

args = parser.parse_args()

# logger : création d'un second handler de type fichier avec rotation sur taille (100Mo) 
#          et une profondeur de 10 fichiers, par défaut sous /tmp/username.mtv.log
username = getpass.getuser()
log_file = username+".mtv.log"
log_dir = "/tmp"
if  args.log_dir != None :
    log_dir = args.log_dir
logger.setLevel(logging.DEBUG)
        
file_handler = RotatingFileHandler(log_dir+"/"+log_file, maxBytes=100000000, backupCount=10)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# création éventuelle d'un handler de type fichier en mode append
if args.logger != None :
    file_handler = logging.FileHandler(args.logger, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

logger.info("-----------------")
logger.info("Lancement de MTV ")
logger.info("-----------------")

if args.readers :
    readers_list = ""
    for m in readers.module_list :
        if m.Reader.reader_type != "abstract" :
            readers_list += "{} ".format(m.Reader.reader_type)
    logger.info("Liste des readers connus par mtv : {}".format(readers_list))
    sys.exit(0)
    
if args.config != None :
    mtv_type = args.config
    reader = readers.get_reader(mtv_type, args.source, None, logger=logger)
    logger.info(reader.help_config())
    sys.exit(0)

if len(args.source) == 0 :
    logger.critical("Erreur : aucun fichier source dans la ligne de commande\n.")
    parser.print_help()
    sys.exit(1)

keep_normal = False    
if args.keep :
    keep_normal = True
    
no_checksum = False    
if args.no_checksum :
    no_checksum = True

#
# on decode start et end
#
if args.start!= None and args.end != None and args.start>args.end :
    logger.critical("La date de fin {} est antérieure à la date de début {}.".format(args.end, args.start))
    sys.exit(1)
start = None
if args.start != None :
    start = temps.str2datetime(args.start)
    if start == None :
        logger.critical("Le paramètre start = {} n'est pas valide.".format(args.start))
        sys.exit(1)
end = None
if args.end != None :
    end = temps.str2datetime(args.end)
    if end == None :
        logger.critical("Le paramètre end = {} n'est pas valide.".format(args.end))
        sys.exit(1)

    
#
# peut-on déterminer un acqid ?
#
if args.acqid == None and args.plateforme == None :
    logger.critical("Ni acqid, ni plateforme : mtv ne sait pas faire.".format(end, start))
    sys.exit(1)
if args.acqid == None :
    try :
        duree_vecteur = temps.duree_vecteur_from_plateforme(args.plateforme)
    except :
        logger.critical("impossible de determiner duree_vecteur pour la plateforme {}.".format(args.plateforme))
        sys.exit(1)
    if duree_vecteur == "acquisition" :
        logger.critical("plateforme de type acquisition sans acqid : mtv ne sait pas faire.".format(end, start))
        sys.exit(1)
else :
    try :
        duree_vecteur = temps.duree_vecteur_from_acqid(args.acqid)
    except :
        logger.critical("impossible de determiner duree_vecteur pour l'acqid {}.".format(args.acqid))
        sys.exit(1)

#
# on contruit un reader et on lit
#   
mtv_type = args.type #TODO : le type doit être déduit de la source s'il n'est pas en argument.
reader = readers.get_reader(mtv_type, args.source, args.file, logger, start, end, keep_normal, no_checksum)
try :
    reader.read()
except Exception as e :
    logger.critical(str(e))
    logger.critical("Arret de la vectorisation")
    sys.exit(1)
    

#
# on vectorise
#
nb_vecteurs = 0
if args.dry_run != True :
    # on vérifie qu'on a des données à vactoriser
    if reader.datas == {} :
        if args.acqid != None :
            str_log = args.acqid
        else :
            str_log = args.plateforme
        if start != None :
            str_log += " début:{}".format(start)
        if end != None :
            str_log += " fin:{}".format(end)
        logger.warning("Pas de données trouvées pour {} : pas de vectorisation.".format(str_log))
        sys.exit(0)
        
    # si start et end existent on les utilise sinon on prend la période des datas
    try :
        _min, _max = reader.get_periode_datas()
    except :
        if start == None or end == None :
            logger.critical("MTV ne peut pas déterminer la période à vectoriser à partir des données.")
            logger.critical("Cela signifie que les datas des vecteurs sont probablement vides.")            
            logger.critical("-----------------------------------------------")
            logger.critical("MTV se termine sur un ECHEC")
            logger.critical("-----------------------------------------------")
            sys.exit(-1)
        
    if start == None :
        start = _min
    if end == None :
        fin_incluse = True
        end = _max
    else :
        fin_incluse = False
    
    # on cherche la liste des acqid concernés
    if args.acqid != None :
        liste_acqid = [args.acqid]
    else :
        liste_acqid = temps.periode2acqid(start, end, args.plateforme, fin_incluse)
        
    logger.info("liste des acqid candidats à la vectorisation : {}".format(liste_acqid))
    
    # on boucle sur les acqid et les parametres à vectoriser
    for a in liste_acqid :
        start_inf = None
        end_inf = None
        for param, value in list(reader.datas.items()) :
            start_i,end_i = vectorise_data(reader, param, value, args, start, end)
            if start_i != None and end_i != None :
                nb_vecteurs += 1
                if start_inf is None or start_i < start_inf :
                    start_inf = start_i
                if end_inf is None or end_i>end_inf :
                    end_inf = end_i
                    
        # Ecriture du fichier INF
        # TODO : on écrit un fichier inf minimal par acqid avec des informations génériques.
        #       Il faudra par la suite crééer ou modifier le fichier inf pour chaque paramètre vectorisé.
        #       En attendant, on prend le plus petit start et le plus grand end vectorisés pour les champs date.
        if start_inf != None and end_inf != None :
            ecrit_fichier_inf(a, start_inf, end_inf)
        else :
            logger.info("{} : Aucun vecteur créé (pas de données) pour cet acqid.".format(a))
        
logger.info("-----------------------------------------------")
logger.info("MTV a terminé avec succès : {} vecteurs créés.".format(nb_vecteurs))
logger.info("-----------------------------------------------")
#
# Tracé des data lues
#
if args.graphic :
    trace_datas(reader)

sys.exit(nb_vecteurs)
