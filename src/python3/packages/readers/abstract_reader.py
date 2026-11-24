#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import urllib.request, urllib.parse, urllib.error
from glob import glob
from readers import str2time
import re
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
import collections
import tempfile

class Reader() :
    """
        Classe abstraite qui définit un lecteur de données.
        La source des données est une liste contenant un ou plusieurs fichiers, répertoires ou URL.
        Les classes qui héritent doivent implémenter obligatoirement la méthode read_config
        ainsi que les méthodes read_file et read_url si besoin.
        Le résultat de la lecture doit se faire dans l'attribut datas.
    """
    reader_type = "abstract"
    
    def __init__(self, source, config_file=None, logger=None, start=None, end=None, keep_normal=False, no_checksum=False):
        """
            Initialisation du reader.
            
            :param source: la source à lire (fichier(s), répertoire(s), url(s)
            :type source: list
            :param config_file: fichier de configuration
            :type config_file: str
            :param logger: objet de gestion des log
            :type logger: logging.Logger
            :param start: date de début (première date retenue par la lecture)
            :type start: datetime
            :param end: date de fin (avant dernière date retenue par la lecture pour répondre à des problématiques du style "la dernière donnée de J est la première de J+1)
            :type end: datetime
            :param keep_normal: on conserver les valeurs hors normes (défaut = False)
            :type keep_normal: boolean
            :param no_checksum: pas de checksum même s'il est demandé dans la config (défaut = False)
            :type no_checksum: boolean
        """
        self.source = source
        self.config_file = config_file
        self.start = start
        self.end = end
        self.keep_normal = keep_normal
        self.no_checksum = no_checksum
        self.config = None # la config en mémoire
        self.datas = None # les données en mémoire
        self.columns_list = None # liste des colonnes si décrites dans l'en-tête du fichier de données.
        self.columns_cache = collections.defaultdict(dict) # contient les colonnes et leur(s) num_col (gain de performance par rapport à plein d'appels à col2num_col)
        self.cfg = collections.defaultdict(dict)
        
        # création d'un logger
        if logger is None :
            self.log_file = tempfile.gettempdir()+"/reader_{}.log".format(self.reader_type)
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s :: %(process)s :: %(levelname)s :: %(message)s')        
            # création d'un handler de type fichier
            file_handler = RotatingFileHandler(self.log_file, maxBytes=100000000, backupCount=10)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
                   
            # création d'un second handler de type console
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            self.logger.addHandler(stream_handler)
        else :
            self.logger = logger
        self.logger_func = [self.logger.debug, self.logger.info, self.logger.warning, self.logger.error, self.logger.critical]
        
        self.logger.debug("### Le programme {} crée un reader {}.".format(os.path.basename(sys.argv[0]), self.reader_type))
        
        
    def read(self):
        """
            Lecture d'une source décrite par une configuration.
        """
        self.read_config()
        self.read_data()
            
    def read_config(self) :
        """
            Lit la configuration des données.
            
            Méthode à implémenter obligatoirement.
        """
        raise NotImplementedError("Vous devez implémenter la méthode read_config de la classe Reader pour le type {}".format(self.reader_type))

    def read_data(self) :
        """
            Lit une source de données.
        """
        for s in self.source :
            self.current_source = s
            type_source = self.get_source_type(s)
            if type_source == "DIR" :
                self.read_dir()
            elif type_source == "URL" :
                self.read_url()
            else :
                self.read_file(s)
                
    def read_dir(self):
        """
            Lecture d'un répertoire.
        """
        self.logger.info("Lecture du répertoire {}".format(self.current_source))
        files = glob(self.current_source+"/*")
        files.sort()
        for f in files :
            self.read_file(f)
            
    def read_file(self, encoding='utf-8') :
        """
            Lit un fichier de données.
            
            Méthode à implémenter obligatoirement.
        """
        raise NotImplementedError("Vous devez implémenter la méthode read_file de la classe Reader pour le type {}".format(self.reader_type))

    def read_url(self) :
        """
            Lit une url.
            
            Méthode à implémenter obligatoirement.
        """
        raise NotImplementedError("Vous devez implémenter la méthode read_url de la classe Reader pour le type {}".format(self.reader_type))
 
            
    def help_config(self, required=True) :
        """
            Décrit le fichier de config.
            
            :return: le texte de description.
            :rtype: str
        """
        return "La configuration du type {} n'est pas documentée.".format(self.reader_type)

    
    def get_source_type(self, source) :
        """
            Retourne le type de la source à lire : fichier, répertoire ou URL
            
            :param source: la source à lire
            :type param: str
            :return: le type de la source("FILE", "REP","URL")
            :rtype: str
        """
        
        type_source = None
        if os.path.isdir(source) :
            type_source = "DIR"
        elif os.path.isfile(source) :
            type_source = "FILE"
        else :
            try :
                urllib.request.urlopen(source) 
                type_source = "URL"
            except :
                pass
        if type_source is None :
            message = "La source {} ne correspond à aucun type connu (répertoire, fichier ou URL valide)".format(source)
            self.logger.critical(message)
            raise ReaderError(message)    
        return type_source
    
    def get_all_formats_temps(self, format_temps):
        """
            Détermine les combinaisons possibles à partir des différents formats de temps.
            
            Exemple : format_temps = %Y%m%d,%H%M|%H%M%S|%H%M%S.%f
            
                       donne 3 combinaisons possibles :
                       
                       - %Y%m%d,%H%M
                       - %Y%m%d,%H%M%S
                       - %Y%m%d,%H%M%S.%f
            
            :param format_temps: le format tel que défini dans la config
            :type format_temps: str
            :return: liste des formats
            :rtype: list
        """
        fmts = format_temps.split(',')

        # calcul du nombre de combinaisons (produit du nombre de format de chaque expression)
        lengths = [len(fmts[i].split('|')) for i in range(len(fmts))]
        nc = 1
        for s in lengths :
            nc *= s
        # initialisation du résultat
        result = []
        for i in range(nc) :
            result.append([])
        
        # boucle sur les expressions
        i = 0
        while i < len(fmts) :
            # calcul du nombre de combinaisons à l'indice i
            lengths = [len(fmts[j].split('|')) for j in range(i,  len(fmts))]
            p = 1
            for s in lengths :
                p *= s   
            # nombre de format 
            n = len(fmts[i].split('|'))
            # taille des blocs à écrire pour chaque format (p/n)
            nb = p//n
            # écriture
            ind = 0
            while ind < nc :
                for f in fmts[i].split('|') :
                    for n in range(nb) :
                        result[ind].append(f)
                        ind = ind+1
            i = i+1
            
        return result
    
    def get_time(self, line):
        """
            Retourne un datetime en utilisant les éléments de la ligne décrits dans la config.
            
            :param line: la ligne de donnée en cours de traitement
            :type line: list
            :return: le temps calculé ou un message d'erreur
            :rtype: datetime ou str
        """
        colonne_msg_id = self.cfg["structure"]["colonne_msg_id"]
        if colonne_msg_id is None :
            temps = self.cfg["structure"]["temps"]
            format_temps = self.cfg["structure"]["format_temps"]
        else :
            col_1, _col_2, step = self.columns_cache[colonne_msg_id]           
            msg_id = line[col_1-1]
            temps = self.cfg["msg_{}".format(msg_id)]["temps"]
            format_temps = self.cfg["msg_{}".format(msg_id)]["format_temps"]
        
        all_formats_temps = self.get_all_formats_temps(format_temps)
        msg = ""
        for fmt in all_formats_temps :
            try :            
                time = str2time._strptime(self.eval_temps(temps, line), ",".join(fmt))
                return time
            except Exception as e :
                msg += str(e) + "\n"
                
        return msg
    
    def eval_temps(self, str_time, line):
        """
            Evalue la chaîne de caractère représentant le temps :
            
            - évalue les mots clés NOMFIC, NOMREP, col_<A>
            - traite les slices
            
            :param str_time: decription du temps comme dans la config
            :param line: ligne de donnée en cours de traitement
            :type str_time: str
            :type line: str
            :return: une chaîne décodée représentant l'élément de temps
            :treturn: str
        """
        tab_eval=[]
        for s in str_time.split(',') :
            s = s.strip()
            if "NOMFIC" in s :
                new_str_time = eval("\""+s.replace("NOMFIC", os.path.basename(self.current_file)+"\""))
            elif "NOMREP" in s :
                new_str_time = eval("\""+s.replace("NOMREP", os.path.dirname(self.current_file)+"\""))
            elif "col_" in s :
                col, _slice = self.split_slice(s)
                col_1, col_2, step = self.columns_cache[col]                
                if _slice != None :
                    value = eval("line[col_1-1]{}".format(_slice))
                else :
                    value = line[col_1-1]
                new_str_time = eval("\""+s.replace("{}".format(s), value+"\""))             
            else : # date en dur
                new_str_time = s
            tab_eval.append(new_str_time)
        return ','.join(tab_eval)
    
    def col2num_col(self, col_name):
        """
            Retourne le(s) numéro(s) de la colonne à partir de son nom
            
            :param col_name: nom de la colonne
            :type col_name: str
            :return: numéro(s) de la colonne
            :rtype: tuple d'int
        """
        cols = col_name.split('@')[0].split(':')
        try :
            step = int(cols[2])
            cols = cols[:-1]
        except :
            step = 1
        cols_id = [c.split("col_")[1] for c in cols]
        if self.columns_list != None :
            cols_num = [self.columns_list.index(c)+1 for c in cols]
        else :
            cols_num = [int(c) for c in cols_id]
        if len(cols_num) == 1 :
            cols_num.extend([None, None])
        else :
            cols_num.append(step)
        
        return tuple(cols_num)
    
    def col2msg_id(self, col_name):
        """
            Retourne le msg_id de la colonne à partir de son nom : si pas de msg_id retourne "structure"
            
            :param col_name: nom de la colonne
            :type col_name: str
            :return: msg_id associé à la colonne
            :rtype: str
        """
        cols = col_name.split('@')
        if len(cols) == 2 :
            return cols[1]
        else :
            return "structure"
        
    def split_slice(self, expression):
        """
            Sépare le slice d'une chaîne.
            
            :param expression: la chaine à traiter
            :type expression: str
            :return: la chaîne et son slice séparés
            :rtype: tuple de str        
        """
        s = re.search(r"(.*)(\[.*:.*\])", expression)
        if s != None :
            return (s.group(1), s.group(2))
        else :
            return (expression, None)
        
    def np_string(self, format_str, reverse=False):
        """ Donne la chaîne de format dtype/numpy correspondant à un format AIDA ou inversement si reverse=True
            
            :param str format_str: le format selon la norme aida ou dtype/numpy (dépend de reverse)
            :param bool reverse:   si True donne le format AIDA à partir d'un format dtype/numpy

            :return : format
            :rtype: str
        """
        # on traite ici les formats non dtype/numpy de base float et double
        if format_str == 'float' :
            format_str = 'float32'
        if format_str == 'double' :
            format_str = 'float64'
        np_string_dict = {
            "int_8": "int8",
            "u_int_8": "uint8",
            "byte": "int8",
            "int_16": "int16",
            "u_int_16": "uint16",
            "int_32": "int32",
            "u_int_32": "uint32",
            "int_64": "int64",
            "u_int_64": "uint64",
            "ieeefloat_32": "float32",
            "ieeefloat_64": "float64",
            "string": "str",
            "string32": "str"
            }
        if reverse :
                return next((aida_format for aida_format,format in list(np_string_dict.items()) if format == format_str), None)
        else :
            try:
                return np_string_dict[format_str.lower()]
            except KeyError :
                return None

    def string2flag(self, data, num_table) :
        table_flags = {}
        table_flags[0] = {
                            "|" : '0',
                            "X" : '1',
                            "m" : '2',
                            "?" : '3',
                            "c" : '4',
                            "D" : '5'
                          }
        if num_table not in table_flags.keys() :
            raise("Law string2flag : numéro de table de flags inconnu {}\n".format(num_table))
        return [ table_flags[num_table][s] for s in data ], True

        
    def Poly_1(self, data, b, a):
        """
            Fonction polynome de degré 1 : y = ax + b
            Peut être utilisée dans le champs 'law' du fichier de config sous la forme :

                law = <Poly_1>:b,a
            
            :param None  data: les données sur lesquelles on applique la fonction
            :param float b:    coefficient b
            :param float a:    coefficient a

            :return: les données et un booléen qui indique si les données ont été modifiées
            :rtype: tuple
        """
        if a==1 and b==0 :
            return (data, False)
        else :
            data2 = a*data + b        
        return (data2, True)
    
    def Poly_2(self, data, c, b, a):
        """
            Fonction polynome de degré 2 : y = ax^2 + bx +c
            Peut être utilisée dans le champs 'law' du fichier de config sous la forme :

                law = <Poly_2>:c,b,a

            :param None data: les données sur lesquelles on applique la fonction
            :param float c:   coefficient c
            :param float b:   coefficient b
            :param float a:   coefficient a

            :return: les données et un booléen qui indique si les données ont été modifiées
            :rtype: tuple
        """
        if a==0 and b==1 and c==0 :
            return (data, False)
        else :
            data2 = a*data*data + b*data +c        
        return (data2, True)

    def Rotation_deg(self, data, angle):
        """
            Applique une rotation de valeur "angle" modulo 360° dans le sens trigonométrique.
            Peut être utilisée dans le champs 'law' du fichier de config sous la forme :

                law = <Rotation_deg>:angle

            :param ndarray data:  les données sur lesquelles on applique la fonction
            :param float   angle: angle de la rotation en degrés

            :return: les données résultantes et un booléen qui indique si les données ont été modifiées
            :rtype: tuple
        """
        data2 = [ (x-angle)%360 for x in data ]
        return(np.array(data2), True)

    def clip(self, data, value):
        """
            Fonction qui clippe (ie. remplace toute valeur inférieure à value par value)
            Peut être utilisée dans le champs 'law' du fichier de config sous la forme :

                law = <clip>:value
            
            :param None data:   les données sur lesquelles on applique la fonction
            :param float value: valeur du clip

            :return: les données et un booléen qui indique si les données ont été modifiées
            :rtype: tuple
        """
        try :
            data2 = data.clip(value)
            ret = True
        except :
            data2 = None
            ret = None
        
        return (data2, ret)

    def clip_and_log(self, data, value):
        """
            Fonction qui clippe (ie. remplace toute valeur inférieure à value par value) puis prend le log népérien
            Peut être utilisée dans le champs 'law' du fichier de config sous la forme :

                law = <clip_and_log>:value
            
            :param None data:   les données sur lesquelles on applique la fonction
            :param float value: valeur du clip

            :return: les données et un booléen qui indique si les données ont été modifiées
            :rtype: tuple
        """
        try :
            data2 = np.log(data.clip(value))
            ret = True
        except :
            data2 = None
            ret = None
        
        return (data2, ret)
    
    def egal(self, data, value):
        """
            Teste si data = value
            Peut être utilisée dans le champs 'controle' du fichier de config sous la forme :

                controle = <egal>:value

            :param None data:   les données sur lesquelles on applique la fonction
            :param float value: valeur utilisée pour le test

            :return: la liste des indices ne vérifiant pas la condition
            :rtype: numpy ndarray
        """
        if isinstance(value, str) :
            match_indices = np.where(data==value)[0]
        else :
            match_indices = np.where(np.isclose(data,value))[0]
        to_delete = np.setxor1d(match_indices, list(range(len(data))))
        
        return to_delete
    
    def different(self, data, value):
        """
            Teste si data != value
            Peut être utilisée dans le champs 'controle' du fichier de config sous la forme :

                controle = <different>:value

            :param None data:   les données sur lesquelles on applique la fonction
            :param float value: valeur utilisée pour le test

            :return: la liste des indices ne vérifiant pas la condition
            :rtype: numpy ndarray
        """
        if isinstance(value, str) :
            match_indices = np.where(data!=value)[0]
        else :
            match_indices = np.where(np.invert(np.isclose(data,value)))[0]
        to_delete = np.setxor1d(match_indices, list(range(len(data))))
        
        return to_delete
    
    def get_frequency (self, times, name=""):
        """ 
            Détermine empiriquement la fréquence 
            d'échantillonnage correspondant à une série de temps.
            
            Très fortement inspiré de AIDA.diagno_temps
            
            :param times: les données de temps
            :type times: list[datetime.datetime]

            :return : valeur de la fréquence en Hz, diagnostic
            :rtype: tuple (float, str)
        """
        diag = "{} : ".format(name)
        if len(times) < 2:
            diag += "taille du vecteur < 2 : frequence non calculable."
            return 0, diag
        
        delta_t = np.diff(times)
        delta_t = np.array([ d.total_seconds() for d in delta_t ])
        where_delta_t_neg = np.where (delta_t < 0)
        nb_delta_t_neg = len(where_delta_t_neg[0])
        if nb_delta_t_neg > 0:
            diag += "{} retours dans le passé. ".format(nb_delta_t_neg)
            #self.logger.debug("ligne(s) : {}".format([x for x in where_delta_t_neg[0]]))
        
        duree = (times[-1]-times[0]).total_seconds()
        freq_moy = len(times) / duree
        period_med = np.median (delta_t)
        freq_med = 1.0 / period_med
        diag += "Duree : {} sec, frequence moyenne : {} Hz, mediane : {} Hz.  ".format(duree, freq_moy, freq_med)
        if freq_med > 0.7:
            freq = int(round(freq_med))
        else:
            freq = freq_med
        where_delta_t_gros = np.where (delta_t > period_med * 1.05)
        nb_delta_t_gros = len(where_delta_t_gros[0])
        if nb_delta_t_gros > 0:
            diag += "{} delta_t > mediane + 5%.".format(nb_delta_t_gros)
            #self.logger.debug("ligne(s) : {}".format([x for x in where_delta_t_gros[0]]))
        self.logger.warning(diag)
        return freq, diag
    
    def xor_checksum(self, str_data, str_csum, start, end):
        """
            Checksum qui utilise la méthode "ou exclusif".
            
            :param str_data: la chaîne de caractère à vérifier
            :type str_data: str
            :param start: caractère ou chaine de debut
            :type start: str
            :param end: caractère ou chaine de fin
            :type end: str
            :param str_csum: la valeur du checksum
            :type str_csum: str
            :return: résultat de la vérification
            :rtype: bool
        """
        csum = 0
        try :
            str_to_check = re.search(r'.*{}(.*){}.*'.format(start, end), str_data).groups(1)[0]
        except :
            self.logger.error("Les marqueurs de début ({}) et de fin ({}) de checksum n'ont pas été trouvés dans la ligne :{}".format(start, end, str_data))
            return False
        for c in bytes(str_to_check) :
            csum ^= ord(c)
        if (hex(csum) == hex(int(str_csum,16))) :
            return True
        else :
            return False
    
    def get_periode_datas(self, whole=True):
        """
            Retourne la première et la dernière date des datas.
            
            :param whole: si False, ignore les données pour lesquelles le champ "ignore" = True
            :type param: bool
            :return: debut, fin
            :rtype: tuplede datetime
        """
        liste_rft_time = []
        for param, value in list(self.datas.items()) :   
            try :
                if not whole :
                    if value["infos"]["ignore"] == "False" :
                        liste_rft_time.append(value["infos"]["temps"])
                else :
                    liste_rft_time.append(value["infos"]["temps"])
            except :
                pass
        liste_rft_time = list(set(liste_rft_time))
        mins_max = []
        for t in liste_rft_time :
            mins_max.append(min(self.datas[t]['data']))
            mins_max.append(max(self.datas[t]['data']))
            
        return min(mins_max), max(mins_max)
    
    def parse_unit(self, unit):
        """
            Permet de modifier l'unité
            
            :param unit: unité en entrée
            :type unit: str
            :return: unité modifiée
            :rtype: str
        """
        return unit
    
    def parse_nom(self, nom):
        """
            Permet de modifier le nom des colonnes
            
            :param nom: nom de la colonne en entrée
            :type nom: str
            :return: nom de la colonne modifiée
            :rtype: str
        """
        return nom
    
class ReaderError(Exception):
    """ Classe pour les erreurs dans les modules readers."""
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg
    
