#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from readers import csv_like
import configparser
import sys
import re
from readers.abstract_reader import ReaderError

class Reader(csv_like.Reader) :
    """
        Reader pour le type pads.

    """
    reader_type = "pads"

    def read_config(self) :
        """
            Si un fichier de config existe on appelle la méthode de la classe mère sinon on fait rien.
        """
        self.config_deja_lue = False
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
    
    def read_file(self, the_file, encoding='iso-8859-1'):
        """
            Lecture d'un fichier de données :
             1- on lit la config contenue dans le 1er fichier de données
             
             2- on appelle la méthode check_config de la classe mère (csv_like.Reader)
             
             3- on appelle la méthode read_file de la classe mère (csv_like.Reader)
            
            :param the_file: le fichier de données
            :type the_file: str
        """
        
        # 1- Lecture de la config contenue dans le fichier
        desc_config = []
        fin_entete = False
        with open(the_file, 'r', encoding=encoding, errors='replace') as f :
            for line in f :
                if fin_entete :
                    ligne_noms = line
                    break
                if line.strip() == '****':
                    fin_entete = True
                else :
                    desc_config.append(line)
        
        header_size = len(desc_config)+2 # la ligne '****' + la ligne des description des paramètres
        noms = ["col_"+n for n in ligne_noms.split(',')[0:3]] # nom des 3 colonnes temps
        
        if not self.config_deja_lue :
            # on construit la config
            if self.config is None :
                self.config = configparser.RawConfigParser()
                self.config.optionxform = str # pour conserver les majuscules sur les options
            if not self.config.has_section("structure") :
                self.config.add_section("structure")
            self.config.set("structure", "nb_lignes_entete", str(header_size))
            self.config.set("structure", "numero_ligne_nom", str(header_size))
            self.config.set("structure", "numero_ligne_unit", str(header_size))
            self.config.set("structure", "separateurs_colonnes", ",")
            self.config.set("structure", "temps", ",".join(noms[0:3]))
            self.config.set("structure", "format_temps", "%DS,%j,%Y")
            self.config.set("structure", "nom_variable_temps", "rft_time_pads")
            
            # 2- Vérification de la config (appel de la méthode check_config de la classe mère)
            if not csv_like.Reader.check_config(self) :        
                raise ReaderError ("La syntaxe de la config {} n'est pas valide".format(self.config_file))
            self.config_deja_lue = True
        # 3- appel la méthode read_file de la classe mère (csv_like.Reader)
        csv_like.Reader.read_file(self, the_file)
        
        
    def parse_unit(self, unit):
        """
            On récupère l'unité entre parenthèses dans le nom de la colonne sauf si elle a été définie
            dans un fichier de config.
        """
        try :
            unit = self.config.get("col_"+unit, "unit")
        except :
            res=re.search(r'\((.*)\)', unit)
            if res != None :                
                    unit = res.group(1)
            else :
                unit = self.def_config["col_defaut"]["unit"]["default"]
        return unit
    
    def help_config(self, required=True):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = csv_like.Reader.help_config(self, required=False)
        return str_help
        
        
