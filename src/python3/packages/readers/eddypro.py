#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from readers import csv_like
import configparser
import sys
import re
from readers.abstract_reader import ReaderError

class Reader(csv_like.Reader) :
    """
        Reader pour le type eddypro.

    """
    reader_type = "eddypro"

    def get_eddypro_id (self) :
        nomfic = str(self.source)
        try : 
            eddypro_id = nomfic.split('eddypro_')[1].split('_full_output')[0]
        except :
            eddypro_id = 'X'
        return eddypro_id

    def set_nom_variable(self, nom):
        """
        ajout de la famille et d'un préfixe au nom des colonnes pour definir le nom des variables (-> vecteurs) 
        """

        # dictionnaire qui définit la famille AIDA en fonction du nom 
        # de la variable EddyPro
        famille = {
            "tpr" : ["sonic_temperature" , "air_temperature" ],
            "hum" : ["RH" , "Tdew", "e" , "h2o_mixing_ratio", "h2o_molar_density"   ],
            "ven" : ["w_unrot" , "wind_speed" , "wind_dir" , "max_wind_speed" ],
            "trb" : ["TKE", "L" , "(z-d)/L" , "u_var" , "v_var" , "w_var" , 
                        "ts_var", "u*", "h2o_var", "co2_var" ],
            "flx" : ["H", "LE", "co2_flux","h2o_flux", "Tau", "w/ts_cov" , 
                        "w/h2o_cov" , "w/co2_cov",  "bowen_ratio" ,  ],
            "tmd" : ["air_density" , "air_heat_capacity" ],
            "chm" : ["co2_mixing_ratio",  "co2_molar_density" ],
            "ctl" : ["qc_H",  "rand_err_H", "qc_LE",  "rand_err_LE", "qc_Tau",  "rand_err_Tau","qc_h2o_flux" , 
                "rand_err_h2o_flux", "qc_co2_flux" , "rand_err_co2_flux",
                "u_spikes" , "v_spikes" , "w_spikes" , "ts_spikes" , "h2o_spikes" , "co2_spikes",
                "used_records" , "h2o_time_lag" , "co2_time_lag", "model", "yaw", "pitch" ], 
            }
        fam = "xxx"
        for k,v in iter(famille.items()) :
            if nom in v :
                fam = k
                break

        if nom == "(z-d)/L" :
            nom="z_sur_L"

        if nom == "u*" :
            nom = "ustar"

        eddypro_id = self.get_eddypro_id() 
        new_nom = "{}_EP_{}_{}".format(fam, eddypro_id, nom)

        return new_nom


    def read_config(self) :
        """
            Description du fichier de données.
        """
 
        # tous ls parametres du fichier full ouput de Eddypro  ne sont
        # pas utiles. On fait une liste des paramètres a vectoriser
        liste_params = ["w_unrot" , "wind_speed" , "wind_dir" , "max_wind_speed" , "sonic_temperature" , "air_temperature" , "RH" , 
                        "Tdew" , "air_density" , "air_heat_capacity" , "e" , "h2o_mixing_ratio" , "co2_mixing_ratio" , "Tau" , 
                        "qc_Tau" , "rand_err_Tau" , "H" , "qc_H" , "rand_err_H" , "LE" , "qc_LE" , "rand_err_LE" , "bowen_ratio" , 
                        "h2o_flux" , "qc_h2o_flux" , "rand_err_h2o_flux" , "co2_flux" , "qc_co2_flux" , "rand_err_co2_flux" , 
                        "h2o_molar_density" , "co2_molar_density" , "u*" , "TKE" , "L" , "(z-d)/L" , "u_var" , "v_var" , "w_var" , 
                        "ts_var" , "u_spikes" , "v_spikes" , "w_spikes" , "ts_spikes" , "h2o_spikes" , "co2_spikes" , "w/ts_cov" , 
                        "w/h2o_cov" , "w/co2_cov" , "model" , "used_records" , "h2o_time_lag" , "co2_time_lag" ,"co2_var", "h2o_var", "yaw", "pitch" ] 


        self.config = configparser.RawConfigParser()
        self.config.optionxform = str # pour conserver les majuscules sur les options
        self.config.add_section("structure")
        self.config.set("structure", "nb_lignes_entete", "3")
        self.config.set("structure", "numero_ligne_nom", "2")
        self.config.set("structure", "numero_ligne_unit", "3")
        self.config.set("structure", "separateurs_colonnes", ",")
        self.config.set("structure", "temps", "col_date,col_time")
        self.config.set("structure", "format_temps", "%Y-%m-%d,%H:%M")
        self.config.set("structure", "misval_out", "-9999.0")
        eddypro_id = self.get_eddypro_id() 
        self.config.set("structure", "nom_variable_temps", "rft_time_EP_{}".format(eddypro_id))

        # le nom de la variable

        for p in liste_params :
            section = "col_{}".format(p)
            if not self.config.has_section(section) :
                self.config.add_section(section)

            param = self.set_nom_variable(p)
            self.config.set(section, "nom_variable", param)

        #self.set_config(section, "name", desc_param)
        #self.set_config(section, "unit", unit)

        # Vérification du fichier de config
        if self.check_config() :        
            return self.config
        else :
            raise ReaderError ("La syntaxe du fichier de config {} n'est pas valide".format(self.config_file))

    
    def parse_unit(self, unit):
        # récupère l'unité à l'intérieur des crochets
        unit1 = re.sub(r'^\[|\]$',"", unit)

        if unit1 == "#" :
            unit1 = "unitless"

        if unit1.find("deg") >= 0 :
            unit1 = unit1.replace("deg", "degrees" )

        # on enleve les +1 et les + et on met des . pour separer les
        # unites

        i=0
        iprec=0
        list_unit=[]

        while i < len(unit1) :
            if unit1[i].isdigit() :
                u = unit1[iprec:i+1]
                u = u.replace("+1", "")
                u = u.replace("+","")
                list_unit.append(u)
                iprec = i+1

            i = i+1

        if len(list_unit) == 0 :
            list_unit.append(unit1)

        return ".".join(list_unit)
    
    def help_config(self):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = "\n\nLe reader {} n'utilise pas de fichier de configuration\n".format(self.reader_type)
        
        return str_help

       
