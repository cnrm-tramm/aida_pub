#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from readers import csv_like
import configparser
import sys
import re
import numpy as np
from readers.abstract_reader import ReaderError

class Reader(csv_like.Reader) :
    """
        Reader pour le type ce376 (Lidar Cimel CE376)

    """
    reader_type = "ce376"


    def read_config(self) :
        """
            Si un fichier de config existe on appelle la méthode de la classe mère sinon on fait rien.
        """
        if self.config_file is None :
            return
        else :
            csv_like.Reader.read_config(self)
        return
    
    def check_config(self) :
        """
            Méthode muette : 
                le check sera fait dans read_file par appel de la méthode check_config de la classe mère.
        """
        return True   
    
    def read_file(self, the_file, encoding='utf-8'):
        """
            Lecture d'un fichier de données :
             1- on construit la config à partir du fichier de données
             
             2- on appelle la méthode check_config de la classe mère (csv_like.Reader)
             
             3- on appelle la méthode read_file de la classe mère (csv_like.Reader)
            
            :param the_file: le fichier de données
            :type the_file: str
        """
        
        # 1- Lecture de la config contenue dans le fichier (on lit l'en-tête)
        desc_config = []
        with open(the_file, 'r', encoding="ISO-8859-1") as f :
            for line in f :
                line=line.strip("\r\n")
                if line.startswith("DP") or line.startswith("DM") or line.startswith("DI"):
                    break
                else :
                    desc_config.append(line)
        
        header_size = len(desc_config)        
        
        # on construit la config (cf doc cimel)
        if self.config is None :
            self.config = configparser.RawConfigParser()
            self.config.optionxform = str # pour conserver les majuscules sur les options
        if not self.config.has_section("structure") :
            self.config.add_section("structure")
        self.set_config("structure", "nb_lignes_entete", str(header_size))
        self.set_config("structure", "separateurs_colonnes", ";")
        self.set_config("structure", "colonne_msg_id", "col_2")
        self.set_config("structure", "temps", "col_3")
        self.set_config("structure", "format_temps", "%Ci")
        self.set_config("structure", "traite_doublons", "False")
        self.set_config("structure", "nom_variable_temps", "rft_time_cd376")
        
        # la section EVENT (msg_0) ne dépend pas de len-tête, elle est toujours présente.
        section = "msg_0"
        if not self.config.has_section(section) :
            self.config.add_section(section)
        self.set_config(section, "nb_colonnes", "5")
        self.set_config(section, "nom_variable_temps", "rft_time_event")
        self.set_config(section, "freq_ech", "0")

        section = "col_5@msg_0"
        if not self.config.has_section(section) :
            self.config.add_section(section)
            self.set_config(section, "format", "string")
            self.set_config(section, "nom_variable", "ctl_event")
            self.set_config(section, "name", "event")
            self.set_config(section, "unit", "empty")

        # config des autres paramètres (dépendant de l'en-tête)
        for l in desc_config :
            if l.startswith("DCLID") :
                dclid = l.split(';')
                num_trame = dclid[1]
                doors_number = int(dclid[4])
                one_door_range = float(dclid[9])
                offset_range = float(dclid[11])
                section = "msg_"+ num_trame
                if not self.config.has_section(section) :
                    self.config.add_section(section)
                self.set_config(section, "nb_colonnes", str(doors_number+9))
                self.set_config(section, "nom_variable_temps", "rft_time_dclid")
                self.set_config(section, "freq_ech", "0.016666667")

                section = "col_1@msg_"+ num_trame
                self.config.add_section(section)
                if not self.config.has_section(section) :
                    self.set_config(section, "controle", "<egal>:'DP'")
                self.set_config(section, "format", "string")
                self.set_config(section, "ignore", "True")

                section = "col_8:col_"+str(doors_number+7)+"@msg_"+num_trame
                if not self.config.has_section(section) :
                    self.config.add_section(section)
                self.set_config(section, "nom_variable", "opt_"+"dclid"+num_trame)
                self.set_config(section, "name", "data lidar")
                self.set_config(section, "unit", "unitless")
                self.set_config(section, "law", "<clip_and_log>:1e-6")
                str_bornes = ""
                for b in range(0, doors_number) :
                    str_bornes += "({},{});".format(b*one_door_range+offset_range, b*one_door_range+offset_range)
                self.set_config(section, "bornes", str_bornes[:-1])
                self.set_config(section, "unit_bornes", "m")

            elif l.startswith("DCMON") :
                dcmon = l.split(';')
                num_trame = dcmon[1]
                section = "msg_"+ num_trame
                nb_param = int(dcmon[4])
                if not self.config.has_section(section) :
                    self.config.add_section(section)
                self.set_config(section, "nb_colonnes", str(nb_param+5))
                self.set_config(section, "nom_variable_temps", "rft_time_dcmon")
                self.set_config(section, "freq_ech", "1")

                section = "col_4@msg_"+num_trame
                if not self.config.has_section(section) :
                    self.config.add_section(section)
                self.set_config(section, "nom_variable", "ctl_"+"dm_warningmap")
                self.set_config(section, "name", "DCMON WarningMap")
                self.set_config(section, "unit", "empty")

                section = "col_5@msg_"+num_trame
                if not self.config.has_section(section) :
                    self.config.add_section(section)
                self.set_config(section, "nom_variable", "ctl_"+"dm_errormap")
                self.set_config(section, "name", "DCMON ErrorMap")
                self.set_config(section, "unit", "empty")

                for p in range(nb_param) :
                    section = "col_"+str(p+6)+"@msg_"+num_trame
                    if not self.config.has_section(section) :
                        self.config.add_section(section)
                    self.set_config(section, "nom_variable", "opt_"+dcmon[5+p*3])
                    self.set_config(section, "name", dcmon[6+p*3])
                    self.set_config(section, "unit", dcmon[7+p*3])

            elif l.startswith("DCIMU") :
                dcimu = l.split(';')
                num_trame = dcimu[1]
                section = "msg_"+ num_trame
                nb_param = int(dcimu[3])
                if not self.config.has_section(section) :
                    self.config.add_section(section)
                self.set_config(section, "nb_colonnes", str(nb_param+3))
                self.set_config(section, "nom_variable_temps", "rft_time_dcimu")
                self.set_config(section, "freq_ech", "5")

                for p in range(nb_param) :
                    section = "col_"+str(p+4)+"@msg_"+num_trame
                    if not self.config.has_section(section) :
                        self.config.add_section(section)
                    self.set_config(section, "nom_variable", dcimu[4+p])
                    self.set_config(section, "name", dcimu[4+p])
                    self.set_config(section, "unit", "")

        #for s in self.config.sections() :
        #    print("[{}]".format(s))
        #    for o in self.config.options(s) :
        #        print("{} = {}".format(o, self.config.get(s, o)))
        
        # 2- Vérification de la config (appel de la méthode check_config de la classe mère)
        if not csv_like.Reader.check_config(self) :        
            raise ReaderError ("La syntaxe de la config {} n'est pas valide".format(self.config_file))
        
        # 3- appel la méthode read_file de la classe mère (csv_like.Reader)
        csv_like.Reader.read_file(self, the_file, encoding="ISO-8859-1")

    def set_config(self, section, option, value) :
        """
            Positionne un élément de la config si ce n'est pas déjà fait.
        """
        if not self.config.has_option(section, option) :
            self.config.set(section, option, value)

    def help_config(self, required=True):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = csv_like.Reader.help_config(self, required=False)
        return str_help
        
