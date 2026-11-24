#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from readers import abstract_reader
import IMCtermite
import numpy as np
import datetime as dt
import collections



class Reader(abstract_reader.Reader) :
    """
        Reader pour le type imc monoparametre
    """
    reader_type = "imc"
    
    def __init__(self, source, config_file=None, logger=None, start=None, end=None, keep_normal=False, no_checksum=False) :
        """
            Appelle le constructeur de la classe parente puis positionne ses attributs.
        """
        abstract_reader.Reader.__init__(self, source, config_file, logger, start, end, keep_normal, no_checksum)
        self.freq = 200 
        self.periode = 1/self.freq
        
    def read_config(self) :
        """
            Pas de fichier de config, méthode muette.
        """
        return True 
    
    def read_file(self, the_file, encoding='utf-8'):
        """
            Lecture du fichier de données
         
            Pour lire le fichier on utilise le module IMCtermite
            On lit les données dans des list que l'on concatène ensuite dans la structure datas : c'est bien
            plus performant que de concaténer des np.array
            Pour le temps, on stocke des timestamps et on convertit an datetime le plus tard possible.
        """
        famille = {
            "acceleration" : "acc",
            "altitude" : "alt",
            "attitude" : "att",
            "chimie" : "chm",
            "controle" : "ctl",
            "eau_liquide" : "lwc",
            "eau_vapeur" : "hum",
            "microphysique" : "mic",
            "navigation" : "nav",
            "physicochimie" : "chm",
            "position_horizontale" : "pos",
            "pression" : "pre",
            "rayonnement" : "ray",
            "temperature" : "tpr",
            "vitesse" : "vit"
            }
        fam = "xxx"

        self.logger.info("Lecture du fichier IMC {}".format(str(the_file)))
        self.datas = collections.defaultdict(dict)

        try :
           imcraw = IMCtermite.imctermite(the_file.encode())
        except RuntimeError as e :
            self.logger.info(("failed to load/parse " + the_file + " : " + str(e)))

# Récupération des métadonnées utiles pour l'entête du vecteur
        metadonnees = imcraw.get_channels(False)
    # Date du début du temps
        dto = dt.datetime.strptime(metadonnees[0]['trigger-time'], '%Y-%m-%dT%H:%M:%S')
        date_deb_data = dto.strftime('%d/%m/%y %H:%M:%S')

    # English_name et famille (dans le champs comment des métadonnées IMC
        comment =  metadonnees[0]['comment']
        comment_split = comment.split(";")
        comment_dict={}
        for i in range(len(comment_split)) :
            meta = comment_split[i].split("=")
            comment_dict[meta[0].replace(' ','')] = meta[1]
        abrv_famille = famille[comment_dict["famille"].replace(' ','')]

    # nom du vecteur résultat sans le prefixe de la famille
        v = abrv_famille + "_" + metadonnees[0]["name"]

        self.datas[v]['data'] = np.array([])
        self.datas[v]['infos'] = {}
        rft_time = "rft_" + v
        self.datas[v]['infos']["temps"] = rft_time
        self.datas[v]['infos']["freq_ech"] = self.freq
        self.datas[v]['infos']["date_vol"] = date_deb_data
        self.datas[v]['infos']["ignore"] = "False"
        self.datas[v]['infos']["unit"] =  metadonnees[0]["yunit"]
        self.datas[v]['infos']["english_name"] =  comment_dict["english_name"]
        self.datas[v]['infos']["bloc"] = "iena"
        self.datas[v]['infos']["type_ech"] = "regulier"
        self.datas[v]['infos']["format"] = "Ieeefloat_32"

        date_jour = dt.datetime.strptime(metadonnees[0]['trigger-time'],"%Y-%m-%dT%H:%M:%S" )
        ts_jour = date_jour.timestamp()
        datas_final = [] # stockage des datas
        ts_final = [] # stockage des timestamp
        index_time_final = [] # stockage des index permettant de recalculer un temps (voir doc constructeur)
        count = 0

        self.datas[rft_time]['data'] = np.array([])
        self.datas[rft_time]['infos'] = {}
        self.datas[rft_time]['infos']["temps"] = rft_time
        self.datas[rft_time]['infos']["freq_ech"] = self.freq
        self.datas[rft_time]['infos']["ignore"] = "False"
                    
        #
        # Remplissage des listes finales :
        #  datas_final = les datas
        #  ts_final = les timestamp
        #
        # d'abord les datas
        #

        datas = imcraw.get_channels(True)
        datas_final = datas[0]['ydata']

        #
        # Puis le temps
        #

        second = np.array(datas[0]['xdata'],dtype=float)
        ts_final =  [ date_jour + dt.timedelta(seconds=i) for i in second]

        #
        # Remplissage de la structure datas
        #
        self.datas[v]["data"] = datas_final
        #dates_result = [ dt.datetime.fromtimestamp(t) for t in ts_final ]
        #dates_result = [ dt.datetime.fromtimestamp(t) for t in ts_final ]
        #self.datas[rft_time]["data"] = dates_result
        self.datas[rft_time]["data"] = ts_final
        
    def read_data(self):
        abstract_reader.Reader.read_data(self) 
        return True

    def help_config(self):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = "\n\nLe reader {} n'utilise pas de fichier de configuration\n".format(self.reader_type)
        
        return str_help
