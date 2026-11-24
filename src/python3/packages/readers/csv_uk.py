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
        Reader pour le type csv_uk.
        Sans fichier de config, les méta données sont lues dans l'en-tête du premier fichier
        de données et tous les paramètres sont vectorisés.
        Concrètement, un fichier de config ne devrait contenir que ce qui suit :       
          [structure]
          liste_param = HTEMP_50m, UTOT_50mB
        afin de ne vectoriser qu'une sélection de paramètres (310 au total ...)
    """
    reader_type = "csv_uk"


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
        with open(the_file, 'r', encoding="ASCII") as f :
            for line in f :
                line=line.strip("\r\n")
                if not line.startswith('!'):
                    break
                else :
                    line_split = line.split(':')
                    if len(line_split) >= 3 and line_split[0][1:].strip() != "time" :
                        desc_config.append(line_split)
        
        header_size = len(desc_config)        
        
        # on construit la config
        if self.config is None :
            self.config = configparser.RawConfigParser()
            self.config.optionxform = str # pour conserver les majuscules sur les options
        if not self.config.has_section("structure") :
            self.config.add_section("structure")
        self.set_config("structure", "debut_ligne_a_ignorer", "!")
        self.set_config("structure", "nb_colonnes", len(desc_config)*2+2)
        self.set_config("structure", "separateurs_colonnes", "ESPACE")
        self.set_config("structure", "separateurs_multiples_ignores", "ESPACE")
        self.set_config("structure", "temps", "NOMFIC[6:14], col_2")
        self.set_config("structure", "format_temps", "%Y%m%d,%DH")
        self.set_config("structure", "traite_doublons", "False")
        self.set_config("structure", "nom_variable_temps", "rft_time_csv_uk")
        self.set_config("structure", "freq_ech", "0.000555556")
        self.set_config("structure", "time_bnds", "-900,900")         

        required_param = []
        if self.config.has_option("structure", "liste_param") :
            liste_param = self.config.get("structure", "liste_param").split(',')
            for p in liste_param :
                split_p = p.split('_')
                fam = self.get_famille(split_p[0].strip())
                param = fam+"_"+ split_p[0].strip().lower()+"_"+split_p[1].strip().lower()
                required_param.append(param)
        # config des paramètres décrits dans l'en-tête ainsi que du paramètre flag associé
        i_col = 3 # première colonne de data ( == flag HTEMP )
        for l in desc_config :
            fam = self.get_famille(l[1].strip()) 
            param = fam+"_"+l[1].strip().lower()+"_"+l[0][1:].strip().lower()
            unit = self.unit_from_string(l[2])
            param_flag = "ctl_flag_"+param
            desc_param = l[2]
            if len(required_param) == 0 or param in required_param :
                # paramètre flag
                section = "col_{}".format(i_col)
                if not self.config.has_section(section) :
                    self.config.add_section(section)
                self.set_config(section, "nom_variable", param_flag)
                self.set_config(section, "name", "quality flag of "+desc_param)
                self.set_config(section, "format", "String")
                self.set_config(section, "unit", "unitless")
                self.set_config(section, "law", "<string2flag>:0")
                # paramètre
                section = "col_{}".format(i_col+1)
                if not self.config.has_section(section) :
                    self.config.add_section(section)
                self.set_config(section, "nom_variable", param)
                self.set_config(section, "name", desc_param)
                self.set_config(section, "unit", unit)
            i_col += 2
           
        # 2- Vérification de la config (appel de la méthode check_config de la classe mère)
        if not csv_like.Reader.check_config(self) :        
            raise ReaderError ("La syntaxe de la config {} n'est pas valide".format(self.config_file))
        
        # 3- appel la méthode read_file de la classe mère (csv_like.Reader)
        csv_like.Reader.read_file(self, the_file, encoding="ASCII")

    def read_data(self):
        """
           Appelle la méthode mère puis converti les flags de string en float32.
        """
        csv_like.Reader.read_data(self)
        for p in self.datas :
            if p.startswith("ctl_flag_") and not p.endswith("_raw") :
                self.datas[p]["data"] = list(np.asarray(self.datas[p]["data"], dtype='f'))
                self.datas[p]["infos"]["format"] = "Ieeefloat_32"       
        return True

    def set_config(self, section, option, value) :
        """
            Positionne un élément de la config si ce n'est pas déjà fait.
        """
        if not self.config.has_option(section, option) :
            self.config.set(section, option, value)

        
    def get_famille(selfself, param):
        """
            Retourne la famille correspondant au paramètre
        """
        famille = {
            "tpr" : ["HTEMP", "DEWP", "TEMP", "ST01", "ST04", "ST10", "ST17", "ST35", "TGRAA", "TGRAB"],
            "hum" : ["RHUM", "RHO", "RHGRA", "RHGRB", "SM10", "SM20", "SM30", "SM40", "SM60", "SM1M"],
            "ven" : ["UTOT", "USCL", "UMAX", "DIR"],
            "trb" : ["UU", "VV", "WW", "TT"],
            "flx" : ["UW", "VW", "UV", "WT", "UT", "WQ", "SFLXA", "SFLXB"],
            "ray" : ["SWDN", "SWMX", "SWUP", "LWDN", "LWUP", "RDUP", "RDDN", "IRTA", "IRTB"],
            "pre" : ["PRES"],
            "prp" : ["RAIN"],
            "opt" : ["VIS2", "VIS25", "VIS50"]
            }
        fam = "xxx"
        for k,v in iter(famille.items()) :
            if param in v :
                fam = k
                break
        return fam
    
    def unit_from_string(self, str_unit):
        """
            Retourne l'unité donnée dans la chaîne en entrée
        """
        parenthesis = re.findall('\(.*?\)',str_unit)
        if len(parenthesis) == 0 :
            return "unitless"
        else :
            return parenthesis[-1][1:-1].replace('^', '')
        
    def help_config(self, required=True):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = "\n\nDescription du fichier de configuration du type {} :\n".format(self.reader_type)
        str_help += "-"*(len(str_help)-3)
        str_help += "\n\n Le fichier de configuration n'est pas obligatoire :\n"
        str_help += "en son absence, le reader {} vectorise tous les paramètres décrits dans l'en-tête du fichier de données.\n".format(self.reader_type)
        str_help += "\nLe fichier de configuration est de type .ini : il est composé de sections entre crochets à l'intérieur \ndesquelles sont définis des attributs sous la forme \n  attribut = valeur.\n"
        str_help += "La structure du fichier de configuration est la même que celle du reader csv_like (pour avoir la description : mtv.py -C csv_like)\n"
        str_help += "Concrètement, le fichier de configuration n'est utilisé que pour préciser la liste des paramètres à vectoriser.\n"
        str_help += "Pour cela il suffit de renseigner l'option liste_param dans la section structure :\n"
        str_help += "   liste_param = HTEMP_50m, UTOT_50mB\n"
        str_help += "Cette option est spécifique au reader {}.\n".format(self.reader_type)
        str_help += "En résumé, un fichier de config pour le reader {} ne devrait contenir que :\n".format(self.reader_type)
        str_help += "   [structure]\n"
        str_help += "   liste_param = HTEMP_50m, UTOT_50mB\n"
        str_help += "\nATTENTION : le fichier de configuration n'est PAS OBLIGATOIRE pour le reader {}\n".format(self.reader_type)

        return str_help
