#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from readers import csv_like
import configparser
import sys
from readers.abstract_reader import ReaderError

class Reader(csv_like.Reader) :
    """
        Reader pour le type licor_as2.

    """
    reader_type = "licor_as2"

    def read_config(self) :
        """
            Description du fichier de données.
        """
        
        self.config = configparser.RawConfigParser()
        self.config.optionxform = str # pour conserver les majuscules sur les options
        self.config.add_section("structure")
        self.config.set("structure", "nb_lignes_entete", "7")
        self.config.set("structure", "numero_ligne_nom", "7")
        self.config.set("structure", "separateurs_colonnes", "TAB")
        self.config.set("structure", "temps", "col_Date,col_Time")
        self.config.set("structure", "format_temps", "%Y-%m-%d,%H:%M:%S:%f")
        self.config.set("structure", "nom_variable_temps", "rft_time_licor_as")
        
        
        # Vérification du fichier de config
        if self.check_config() :        
            return self.config
        else :
            raise ReaderError ("La syntaxe du fichier de config {} n'est pas valide".format(self.config_file))

    def help_config(self):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = "\n\nLe reader {} n'utilise pas de fichier de configuration\n".format(self.reader_type)
        
        return str_help

