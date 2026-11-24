#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from readers import abstract_reader
import numpy as np
from netCDF4 import Dataset
from netCDF4 import num2date
import re
import collections
import configparser
import datetime
import os


class Reader(abstract_reader.Reader) :
    """
        Reader pour le type netcdf.
    """
    reader_type = "netcdf"
    
    def __init__(self, source, config_file=None, logger=None, start=None, end=None, keep_normal=False, no_checksum=False) :
        """
            Appelle le constructeur de la classe parente puis positionne ses attributs.
        """
        abstract_reader.Reader.__init__(self, source, config_file, logger, start, end, keep_normal, no_checksum)
        self.init_config()
        self.liste_var = []        
    
    def init_config(self):
        """
            Initialise la config       
        """
        self.liste_sections = ["structure", "instru_", "var_defaut", "var_", "dimensions"]
        # description de la structure du fichier de config :
        # def_config est un dictionnaire qui contient un ordereddict de paramètres pour chaque section.
        # chaque attribut peut est décrit par le dictionnaire
        # {
        # "required" : True, (defaut = False)
        # "default" : valeur,(defaut = None)
        # "help" : texte d'aide
        # }
        structure = [
                    ("format_temps" ,       {
                                           "help" : "Chaîne de caractère qui décrit la référence du temps (time:units) si celle contenue dans le fichier netcdf n'est pas conforme à la norme CF. Cette chaîne peut contenir des références à des global attributes (${nom_variable}) auxquels peuvent être associés des formats de date, exemple : format_temps = seconds since {${Day}:%Y%m%d} 00:00 UTC "
                                           }),
                    ("nom_variable_temps" ,         {
                                           "default" : "rft_time_<fic_config>[_msg_<ID>]",
                                           "help" : "Nom de la variable qui contient le temps. "
                                           }),
                    ("freq_ech" ,          {
                                           "help" : "Fréquence du message en Hz. "
                                           })
                    ]
        
        instru_ =   [
                    ("position" , {
                                 "help" : "Description de la position de la mesure (fortement recommandée !). "
                                 }),
                    ("chaine_acquisition" ,  {
                                 "help" : "Description de la chaine d'acquisition selon norme AIDA, liste des modules (fortement recommandé !) : module_1 module_2 ... "
                                 }),
                    ("module_" ,  {
                                 "dynamic" : "True",
                                 "help" : "Description d'un module d'aquisition selon norme AIDA (fortement recommandé !) : module_<N> "
                                 })
                    ]
        
        var_defaut =    [            
                        ("unit" ,      {
                                      "default" : "variable d'attribut units ou unknown",
                                      "help" : "Unité. "
                                      }),
                        ("misval_out" ,{
                                      "default" : "NaN",
                                      "help" : "Valeur manquante dans les données de sortie. "
                                      }),
                        ("normal_min" ,{
                                         "help" : "Borne min de l'intervalle de validité de la variable. "
                                      }),
                        ("normal_max" ,{
                                       "help" : "Borne max de l'intervalle de validité de la variable. "
                                      }),
                        ("instru" ,    {
                                        "help" : "Instrument de référence : instru_<N>. "
                                        }),
                        ("bornes" ,    {
                                        "help" : "Variables définissant les bornes pour les variables multi dimensionnelles : [var1,var2,...,varn]"
                                        }),
                        ("format" ,    {
                                      "default" : "Ieeefloat_32",
                                      "help" : "Format de sortie selon syntaxe AIDA (Ieeefloat_64, Ieeefloat_32, Int_16, Int_32, Int_64, ...). "
                                      })
                        ]        
        
        var_ =      [
                    ("nom_variable" ,{
                                    "help" : "Nom du fichier vecteur ou de la variable. "
                                    }),
                    ("name" ,        {
                                    "help" : "Nom long explicite de la variable. "
                                    }),
                    ("english_name" ,{
                                    "help" : "Nom long explicite en anglaisde la variable. "
                                    }),
                    ("unit" ,        {
                                    "inherited" : "var_defaut:unit",
                                    }),
                    ("format" ,      {
                                    "inherited" : "var_defaut:format", 
                                    }),
                    ("normal_min" ,  {
                                    "inherited" : "var_defaut:normal_min",
                                    }),
                    ("normal_max" ,  {
                                    "inherited" : "var_defaut:normal_max",
                                    }),
                    ("misval_out" ,  {
                                    "inherited" : "var_defaut:misval_out" 
                                    }),
                    ("instru" ,      {
                                    "inherited" : "var_defaut:instru"
                                    }),
                    ("bornes" ,      {
                                    "inherited" : "var_defaut:bornes"
                                    }),
                    ("position" ,    {
                                    "inherited" : "instru_:position" 
                                    }),
                    ("chaine_acquisition" ,  {
                                    "inherited" : "instru_:chaine_acquisition" 
                                    }),
                    ("module_" ,     {
                                    "inherited" : "instru_:module_" 
                                    }),
                    ("information" , {
                                    "help" : "Commentaire libre. "
                                    })
                    ]
        
        dimensions = [] # pas d'attributs prédéfinis pour les dimensions
                    
        self.def_config = {
                      "structure" : collections.OrderedDict(structure),
                      "instru_" : collections.OrderedDict(instru_),
                      "var_defaut" : collections.OrderedDict(var_defaut),
                      "var_" : collections.OrderedDict(var_)
                      }
        
    
    def read_config(self) :
        """
            Lecture du fichier de configuration.
            
            La structure du fichier de configuration est définie dans le dictionnaire def_config.
            Le résultat de la lecture est une structure de type ConfigParser stockée dans self.config
            
            :return: retourne une structure contenant la config.
            :rtype: ConfigParser
        
        """
        # Lecture du fichier de config
        if self.config_file is None :
            return
        
        self.config = configparser.RawConfigParser()
        self.config.optionxform = str # pour conserver les majuscules sur les options
        self.config.macros_parsed = False

        try :
            if len(self.config.read(self.config_file)) == 0 :
                message = "Le fichier de config {} n'existe pas...".format(self.config_file)
                self.logger.critical(message)
                raise abstract_reader.ReaderError (message)
        except Exception as e :
            message = "Erreur à la lecture du fichier {}".format(self.config_file)
            self.logger.critical(message)
            self.logger.critical(e)
            raise abstract_reader.ReaderError (message)
        
        # Vérification du fichier de config
        if self.check_config() :        
            return self.config
        else :
            raise abstract_reader.ReaderError ("La syntaxe du fichier de config {} n'est pas valide".format(self.config_file))

    
    def check_config(self):
        """
            Vérifie la cohérence du fichier de config et positionne les valeurs par défaut.
            
            :return:True ou False
            :rtype: Boolean
        """
        
        sections_var = [ s for s in self.config.sections() if s[0:4] == "var_" and s != "var_defaut"]

        #
        # Controle des sections
        #
        for section in self.config.sections() :
            if len ([s for s in self.liste_sections if section[0:len(s)] == s]) == 0 :
                self.logger.critical("Erreur dans le fichier de configuration : la section [{}] n'est pas exploitable par ce reader.".format(section))
                return False 
    
        #
        # Elements liés (obligatoirement présents ensemble)
        #
                    
        # existence des sections [instru_N]
        for s in sections_var :
            if self.config.has_option(s, "instru") :
                instru = self.config.get(s, "instru")
                if not self.config.has_section(instru) :
                    self.logger.critical("Erreur dans le fichier de configuration :  la section [{}] fait référence à {} qui n'est pas défini".format(s, instru))
                    return False
                
                #
        # Héritage [var_defaut] -> [var_<ID>]
        #
        if not self.config.has_section("var_defaut") :
            self.config.add_section("var_defaut")
        for section in sections_var :
            if not self.config.has_option(section, "misval_out") :
                if self.config.has_option("var_defaut", "misval_out") :               
                    self.config.set(section, "misval_out", self.config.get("var_defaut", "misval_out"))                                     
            if not self.config.has_option(section, "format") :
                if self.config.has_option("var_defaut", "format") :               
                    self.config.set(section, "format", self.config.get("var_defaut", "format"))
            if not self.config.has_option(section, "normal_min") :
                if self.config.has_option("var_defaut", "normal_min") :               
                    self.config.set(section, "normal_min", self.config.get("var_defaut", "normal_min"))
            if not self.config.has_option(section, "normal_max") :
                if self.config.has_option("var_defaut", "normal_max") :               
                    self.config.set(section, "normal_max", self.config.get("var_defaut", "normal_max"))
            if not self.config.has_option(section, "unit") :
                if self.config.has_option("var_defaut", "unit") :               
                    self.config.set(section, "unit", self.config.get("var_defaut", "unit"))
            if not self.config.has_option(section, "instru") :
                if self.config.has_option("var_defaut", "instru") :               
                    self.config.set(section, "instru", self.config.get("var_defaut", "instru"))
            if not self.config.has_option(section, "bornes") :
                if self.config.has_option("var_defaut", "bornes") :               
                    self.config.set(section, "bornes", self.config.get("var_defaut", "bornes"))
            if not self.config.has_option(section, "format") :
                if self.config.has_option("var_defaut", "format") :               
                    self.config.set(section, "format", self.config.get("var_defaut", "format"))
                    
        #
        # Héritage [instru_N] -> [var_<ID>]
        #
        for section in sections_var :
            if self.config.has_option(section, "instru") :
                instru = self.config.get(section, "instru")
                if not self.config.has_option(section, "position") :
                    if self.config.has_option(instru, "position") :               
                        self.config.set(section, "position", self.config.get(instru, "position"))
                if not self.config.has_option(section, "chaine_acquisition") :
                    if self.config.has_option(instru, "chaine_acquisition") :               
                        self.config.set(section, "chaine_acquisition", self.config.get(instru, "chaine_acquisition"))
                modules_id = [ m for m in self.config.options(instru) if m[0:7] == "module_"]
                for m in modules_id :
                    if not self.config.has_option(section, m) :
                        self.config.set(section, m, self.config.get(instru,m))
                
        #
        # Valeurs par défaut
        #
        
        # nom_variable_temps
        try :        
            if not self.config.has_option("structure", "nom_variable_temps") :
                self.config.set("structure", "nom_variable_temps", "rft_time_{}".format(os.path.basename(self.config_file)))
        except :
            self.config.set("structure", "nom_variable_temps", "rft_time")
        # misval_out
        if not self.config.has_option("var_defaut", "misval_out") :
            self.config.set("var_defaut", "misval_out", self.def_config["var_defaut"]["misval_out"]["default"])
        for s in sections_var :
            if not self.config.has_option(s, "misval_out") :
                self.config.set(s, "misval_out", self.def_config["var_defaut"]["misval_out"]["default"])                
        # nom_variable
        for s in sections_var :
            if not self.config.has_option(s, "nom_variable") :
                default = s[4:]
                self.config.set(s, "nom_variable", default)
        # unit
        if not self.config.has_option("var_defaut", "unit") :
            self.config.set("var_defaut", "unit", self.def_config["var_defaut"]["unit"]["default"])
        for s in sections_var :
            if not self.config.has_option(s, "unit") :
                self.config.set(s, "unit", self.def_config["var_defaut"]["unit"]["default"])

        # format
        if not self.config.has_option("var_defaut", "format") :
            self.config.set("var_defaut", "format", self.def_config["var_defaut"]["format"]["default"])
        for s in sections_var :
            if not self.config.has_option(s, "format") :
                self.config.set(s, "format", self.def_config["var_defaut"]["format"]["default"]) 
        
        # on cache la config dans self.cfg pour ne plus avoir à utiliser self.config.get peu performant
        for s in self.config.sections() :
            for o in self.config.options(s) :
                self.cfg[s][o] = self.config.get(s,o)
                
        return True              
    
    def read_data(self):
        """
            Lecture des données.
            
            Le résultat de la lecture est stocké dans le dictionnaire self.datas :
            
            datas = {
            
                    "<nom_variable1>" :    {
            
                                            "infos" :    {
            
                                                        "temps" : "<nom_variable_temps>
            
                                                         .
            
                                                         .
            
            
                                            },
            
                                            "data" : [...]
            
                    },
            
                    "<nom_variable2>" : ...
            
            
            }                            
        """
        self.time_list = collections.defaultdict(dict)
        abstract_reader.Reader.read_data(self)        

        for var,nom_variable in self.liste_var :
            data = self.datas[nom_variable]["data"]
            print("########## traitement de {}".format(nom_variable))
            # si la variable n'est pas en config on en crée une avec juste le nom_variable=variable.
            # c'est pour traiter le cas ou on n'a pas de fichier de config et on lit donc toutes les variables

            if len(self.cfg) == 0 or "var_"+var not in self.cfg : 
                self.cfg["var_"+var] = {}
                self.cfg["var_"+var]["nom_variable"] = var

                try :
                    self.cfg["var_"+var]["misval_out"] = self.cfg["structure"]["misval_out"]
                except :
                    self.cfg["var_"+var]["misval_out"] = self.def_config["var_defaut"]["misval_out"]["default"]
                self.cfg["var_"+var]["format"] = self.np_string(str(data.dtype), reverse=True)                         

            # valeurs manquantes : on remplace les _FillValue (si défini) par des misval_out

            try :
                misval_out = eval("np.{}('{}')".format(str(data.dtype),self.cfg["var_"+var]["misval_out"]))
            except :
                if "file_misval" in self.cfg["var_"+var] :
                    misval_out = self.cfg["var_"+var]["file_misval"]
                else :
                    misval_out = None    

            if "file_misval" in self.cfg["var_"+var] and misval_out != None :
                data[data==self.cfg["var_"+var]["file_misval"]] = misval_out

            if  misval_out != None : 
                self.datas[nom_variable]["infos"]["misval"] = str(misval_out)
            else :
                self.datas[nom_variable]["infos"]["misval"]=''

            # normal_min, normal_max
            if not self.keep_normal :
                if "normal_min" in self.cfg["var_"+var] and misval_out != None :
                    if np.isnan(misval_out) :
                        nb_misval_out_before = np.count_nonzero(np.isnan(data))
                    else :
                        nb_misval_out_before = len(np.where(data==misval_out)[0])

                    normal_min = eval("np.{}('{}')".format(str(data.dtype),self.cfg["var_"+var]["normal_min"]))
                    data[data<normal_min] = misval_out

                    if np.isnan(misval_out) :
                        nb_misval_out_after = np.count_nonzero(np.isnan(data))
                    else :
                        nb_misval_out_after = len(np.where(data==misval_out)[0])
                    if nb_misval_out_after -  nb_misval_out_before != 0 :
                        self.logger.warning("le controle sur normal_min a supprimé {} valeurs pour la variable {}.".format(nb_misval_out_after-nb_misval_out_before, var))

                if "normal_max" in self.cfg["var_"+var] and misval_out != None :
                    if np.isnan(misval_out) :
                        nb_misval_out_before = np.count_nonzero(np.isnan(data))
                    else :
                        nb_misval_out_before = len(np.where(data==misval_out)[0])
                    
                    normal_max = eval("np.{}('{}')".format(str(data.dtype),self.cfg["var_"+var]["normal_max"]))
                    data[data>normal_max] = misval_out

                    if np.isnan(misval_out) :
                        nb_misval_out_after = np.count_nonzero(np.isnan(data))
                    else :
                        nb_misval_out_after = len(np.where(data==misval_out)[0])
                    if nb_misval_out_after -  nb_misval_out_before != 0 :
                        self.logger.warning("le controle sur normal_max a supprimé {} valeurs pour la variable {}.".format(nb_misval_out_after-nb_misval_out_before, var))                       
        
    def read_file(self, the_file):

        """

            Lecture d'un fichier de données.

            

            :param the_file: le fichier de données

            :type the_file: str

        """

        self.logger.info("Lecture du fichier {}".format(the_file))
        self.current_file = the_file

        if self.datas is None :
            self.datas = {}

        try :
            dataset = Dataset(the_file)
            #
            # A la lecture du premier fichier on met à jour les macros de la config et
            # on récupère les attributs utiles (_FillValue, units, long_name)
            #

            if self.config != None and self.config.macros_parsed == False :
                self.parse_macros_config(dataset)
                self.config.macros_parsed = True
                self.get_attr_from_file(dataset)

            for var in list(dataset.variables.keys()) :
                # Si on a un fichier de config on ne traite que les variables définies dans celui-ci,
                # sinon on traite tout.
                # On traite systématiquement la variable time et la variable time_bnds
                if var == "time_bnds" : # on s'en occupe avec time
                    continue

                if self.config_file != None and not self.config.has_section("var_"+var) and var != 'time':
                    continue

                # si la variable n'a pas 'time' dans ses dimensions, on ne la traite pas
                dimensions_var = dataset.variables[var].dimensions
                dimension_var_time = dataset.variables['time'].dimensions

                if not any(elem in list(dimensions_var) for elem in list(dimension_var_time)) :
                    self.logger.info("La variable {} ne dépend pas pas du temps, on l'ignore.".format(var))
                    continue

                # lecture des datas et des infos de chaque variable
                infos = {}
                for o in self.cfg["var_"+var] :
                    infos[o] = self.cfg["var_"+var][o]

                data = dataset.variables[var][:]

                if var == "time" : # conversion en datetime                    
                    time = dataset.variables['time']

                    try :
                        if "time_bnds" in dataset.variables.keys() : # si un time_bnds est défini, on l'utilise en prenant la 2ème borne
                            time_bnds = dataset.variables['time_bnds']
                            data = num2date(time_bnds[:,1], units= self.parse_time_units(time.units), only_use_cftime_datetimes=False, only_use_python_datetimes=True)

                        else :
                            data = num2date(time[:], units= self.parse_time_units(time.units), only_use_cftime_datetimes=False, only_use_python_datetimes=True)

                    except Exception as e :
                        message = "Erreur dans le décodage de format_temps du fichier netcdf : {}".format(time.units)
                        self.logger.critical(message)
                        self.logger.critical(e)
                        raise abstract_reader.ReaderError (message)

                    try :
                        infos["freq_ech"] = float(self.cfg["structure"]["freq_ech"])
                    except :
                        infos["freq_ech"], diag = self.get_frequency(data, "rft_time")

                for attr in dataset.variables[var].ncattrs() :
                    if (self.parse_attr(attr) in self.cfg["var_"+var].keys() and 
                        self.cfg["var_"+var][self.parse_attr(attr)] != self.cfg["var_defaut"][self.parse_attr(attr)]):
                        # si l'attribut est en config, on l'utilise 
                        # print(var,self.parse_attr(attr),self.cfg["var_"+var][self.parse_attr(attr)])
                        infos[self.parse_attr(attr)] = self.cfg["var_"+var][self.parse_attr(attr)]

                    else : 
                        # sinon on utilise celui défini dans le fichier netcdf
                        infos[self.parse_attr(attr)] = getattr(dataset.variables[var], attr)

                try :
                    infos["temps"] = self.cfg['structure']['nom_variable_temps']
                except :
                    infos["temps"] = "rft_time"         

                infos["ignore"] = "False"
                infos["name"] = var

                try :
                    infos["name"] = self.cfg["var_"+var]["name"]
                except :
                    try :
                        infos["name"] = getattr(dataset.variables[var], "long_name")
                    except :
                        infos["name"] = var

                try :
                    infos["english_name"] = self.cfg["var_"+var]["english_name"]
                except :
                    pass

                # traitement des bornes des variables de type tableau
                if len(dimensions_var) > 1 :
                    str_bornes = ""
                    str_units_bornes = ""
                    nb_dim_not_time = 0

                    # on regarde si on a défini des bornes en config pour cette variable
                    try :
                        dimensions_var = self.cfg["var_"+var]["bornes"].strip()[1:-1].split(',')
                        dimensions_var = [ d.strip()[4:] for d in dimensions_var]
                        # on vérifie que les variables qui définissent les bornes existent
                        for d in dimensions_var :
                            if not d in list(dataset.variables.keys()) :
                                message = "Erreur dans le fichier de config {} dans l'attribut bornes de [var_{}] : \nla variable {} n'existe pas dans le fichier netcdf {}".format(self.config_file, var, d, the_file)
                                raise abstract_reader.ReaderError (message)

                        borne_type = "variable"
                    except Exception as e :
                        if isinstance(e, abstract_reader.ReaderError) :
                            raise e
                        else :
                            borne_type = "dimension"

                    for dim in dimensions_var :
                        if dim != "time" :
                            # unit_bornes
                            str_units_bornes = self.add_units_bornes(dataset, dim, str_units_bornes)                            
                            # bornes
                            str_bornes = self.add_bornes(dataset, dim, str_bornes, borne_type)
                            nb_dim_not_time += 1

                    if nb_dim_not_time > 1 :        
                        infos["bornes"] = str_bornes
                    else :
                        infos["bornes"] = str_bornes[1:-1] # 1 dimension : on enlève un niveau de parenthèse pour compatibilité
                    infos["unit_bornes"] = str_units_bornes

                # stockage dans la structure datas du reader                            
                if var == "time" :

                    try :
                        nom_variable = self.cfg['structure']['nom_variable_temps']
                    except :
                        nom_variable = "rft_time"

                    try :
                        data = np.append(self.datas[nom_variable]["data"], data)
                    except :
                        pass                
                    self.datas[nom_variable] = {"data" : data, "infos":infos}

                else :
                    try :
                        nom_variable = self.cfg['var_'+var]['nom_variable']
                    except :
                        nom_variable = var

                    try :
                        if len(data.shape) != 1 :
                            data = np.append(self.datas[nom_variable]["data"], data, axis=0)
                        else :
                            data = np.append(self.datas[nom_variable]["data"], data)
                    except :
                        pass
                    self.datas[nom_variable] = {"data" : data, "infos":infos}
                    # mise à jour de la liste des variables lues
                    if (var,nom_variable) not in self.liste_var :
                        if len(self.liste_var) == 0 :
                            self.liste_var = [(var,nom_variable)]
                        else :
                            self.liste_var.append((var,nom_variable))



        except Exception as e :
            self.logger.critical("Impossible de lire le fichier {}".format(the_file))
            self.logger.critical(e)
            raise(e)
 
    
    def parse_macros_config(self, dataset):
        """
            Recherche toutes les macros du fichier de config et les remplace
            par les valeurs correspondantes dans le fichier de données :
            $macro$ = global attributes
            @macro@ = attribut de variable
        """
        for s in self.cfg :
            for o in self.cfg[s] :
                # print("{}:{}".format(s,o))
                # remplacement des $macros$
                valeur = self.cfg[s][o]
                try :
                    m = re.findall("\${(.*?)}", valeur)
                    for val in m :
                        str_val = "value=dataset.{}".format(val)
                        exec(str_val, globals(), locals())
                        valeur = re.sub("\${{{}}}".format(val), locals()["value"], valeur)
                    # remplacement des @macros@
                    m = re.findall("@{(.*?)}", valeur)
                    for val in m :
                        str_val = "value=getattr(dataset.variables['{}'], '{}')".format(s[4:], val)
                        valeur = re.sub("@{{{}}}".format(val), locals()["value"], valeur)
                    # remplacement des &macros&
                    m = re.findall("&{(.*?)}", valeur)
                    for val in m :
                        value = str(dataset.variables[val][:])
                        valeur = re.sub("&{{{}}}".format(val), value, valeur)
                    # remplacement des ~macros~
                    m = re.findall("~{(.*?)}", valeur)
                    for val in m :
                        val_split = val.split(",")
                        value=getattr(dataset.variables[val_split[0]],val_split[1])
                        valeur = re.sub("~{{{}}}".format(val), value, valeur)
                except Exception : # valeur=None par exemple
                    pass
                self.cfg[s][o] = valeur
                   
        #for s in self.cfg :
        #    print("[{}]".format(s))
        #    for o in self.cfg[s] :
        #        print("{} = {}".format(o, self.cfg[s][o])) 
    
    def get_attr_from_file(self, dataset):
        """
            Recherche les attributs utiles à la config dans le fichier netcdf :
            _FillValue | missing_value, name, units
            et les stocke dans la config (file_misval, file_name, file_unit)
        """
        for var in list(dataset.variables.keys()) :
            try :
                file_misval = getattr(dataset.variables[var], "_FillValue")
                self.cfg["var_"+var]["file_misval"] = file_misval
                # print("file_misval de {} = {}".format(var, file_misval))
            except :
                try :
                    file_misval = getattr(dataset.variables[var], "missing_value")
                    self.cfg["var_"+var]["file_misval"] = file_misval
                    # print("file_misval de {} = {}".format(var, file_misval))
                except :
                    pass
            try :
                file_name = getattr(dataset.variables[var], "long_name")
                self.cfg["var_"+var]["file_name"] = file_name
                # print("long_name de {} = {}".format(var, file_name))
            except :
                pass
            try :
                file_unit = getattr(dataset.variables[var], "units")
                self.cfg["var_"+var]["file_unit"] = file_unit
                # print("file_unit de {} = {}".format(var, file_unit))
            except :
                pass
    
    def add_units_bornes(self, dataset, dim, str_units_bornes):
        """
            Construit la chaine de caractère de l'attribut 'unit_bornes' du header
        """
        if len(str_units_bornes) == 0 :
            try :
                str_units_bornes = getattr(dataset.variables[dim], "units")
            except :
                str_units_bornes = "number"
        else :
            try :
                str_units_bornes += "|"+getattr(dataset.variables[dim], "units")
            except :
                str_units_bornes += "|number"
        return  str_units_bornes   
    
    
    def add_bornes(self, dataset, dim, str_bornes, borne_type):
        """
            Construit la chaine de caractère de l'attribut 'bornes' du header
        """

        try :
            bounds = getattr(dataset.variables[dim], "bounds")
            data_bounds = dataset.variables[bounds][:]
            bornes = ""
            point_virgule = ""
            for bound in data_bounds :
                str_bound = "("
                virgule=""
                for b in bound :
                    str_bound += "{}{}".format(virgule,b)
                    virgule=","
                str_bound += ")"
                bornes = bornes +point_virgule+"{}".format(str_bound)
                point_virgule = ";"

        except :

            if borne_type == "dimension" :
                dim_size = dataset.dimensions[dim].size
                bornes = ""
                point_virgule = ""
                for i in range(dim_size) :
                    bornes += point_virgule+"({},{})".format(i+1,i+1)
                    point_virgule = ";"
            else :
                bornes = ""
                point_virgule = ""
                for i in dataset.variables[dim][:] :
                    bornes += point_virgule+"({},{})".format(i,i)
                    point_virgule = ";"
                
        if len(str_bornes) == 0 :
            str_bornes = "("+bornes+")"
        else :
            str_bornes += "|"+"("+bornes+")"
            
        return(str_bornes)
                            
    
    def parse_attr(self, attr) :
        """
            Traduit les attributs si besoin
        """
        attrs = {
                    "units" : "unit",
                    "_FillValue" : "misval_out"
                }
        try :
            return attrs[attr]
        except :
            return attr
        
    
    def parse_time_units(self, str_time_units):
        """
            Corrige le temps pour qu'il soit au standard CF (ce qui devrait être le cas dans un netcdf).
            Exemple de format attendu : seconds since 2020-02-23 00:00 UTC
        """
        if "format_temps" not in self.cfg["structure"] :
            return str_time_units
        else :
            try :
                format_temps = self.cfg["structure"]["format_temps"]
                # on applique le format à la date s'il y en a un
                m = re.findall("{(.*:.*)}", format_temps)

                if len(m) == 0 :
                    return format_temps
                for val in m :
                    str_temps = val.split(':')[0]

                    str_fmt_temps = val.split(':')[1]
                    temps =  datetime.datetime.strptime(str_temps, str_fmt_temps)
                    new_str_temps = datetime.datetime.strftime(temps, "%Y-%m-%d")
                    format_temps = re.sub("{{{}}}".format(val), new_str_temps , format_temps)
                    return format_temps

            except Exception as e :
                message = "Erreur dans le décodage de format_temps : \n attendu en config : {}\n trouvé dans le fichier netcdf : {}".format(format_temps, str_time_units)
                self.logger.critical(message)
                self.logger.critical(e)
                raise abstract_reader.ReaderError (message)
              
    def help_config(self):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = "\n\nDescription du fichier de configuration du type {} :\n".format(self.reader_type)
        str_help += "-"*(len(str_help)-3)
        str_help += "\n\nLe fichier de configuration est de type .ini : il est composé de sections entre crochets à l'intérieur \ndesquelles sont définis des attributs sous la forme \n  attribut = valeur.\n"
        str_help += "Les attributs peuvent être requis et avoir une valeur par défaut.\n"
        str_help += "L'ordre des sections ainsi que l'ordre des attributs à l'intérieur des sections n'a pas d'importance.\n"
        str_help += "Le section [structure] est obligatoire.\n"
        str_help += "Les variables sont identifiées par leur nom (var_humidite, var_tempe, ...)\n"
        str_help += "Il est possible de faire référence à des attributs de variables : @{nom_variable}\n"
        str_help += "Il est également possible de faire référence à des global attributes : ${nom_variable}"
        str_help += "\n\nFormat attendu (* = paramètre hérité) :\n" 
        for section in self.liste_sections :
            if section == "dimensions" :
                continue
            str_help +="\n[{}]\n".format(section)
            for param in sorted(self.def_config[section].keys()) :
                star = '' # on met une étoile si le paramètre est hérité.
                current_section = section
                try :
                    inherited = self.def_config[section][param]["inherited"].split(':')
                    current_section = inherited[0]
                    param = inherited[1]
                    star = '*'
                except :
                    pass    
                try :
                    str_help +="{:25} => {}\n".format(param+star, self.def_config[current_section][param]["help"])
                    try :
                        if self.def_config[current_section][param]["required"] == True :
                            str_help +="{:25}    requis = {}\n".format(" ", self.def_config[current_section][param]["required"])
                    except :
                        pass
                    try :
                        if self.def_config[current_section][param]["default"] != None :
                            str_help +="{:25}    defaut = {}\n".format(" ", self.def_config[current_section][param]["default"])
                    except :
                        pass
                except :
                    pass
        return str_help
    
        
