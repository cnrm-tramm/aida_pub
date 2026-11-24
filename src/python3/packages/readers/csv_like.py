#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from readers import abstract_reader
import sys
import configparser
import csv
import re
import numpy as np
import os
import collections
import datetime
from operator import itemgetter
import gzip

class Reader(abstract_reader.Reader) :
    """
        Reader pour le type csv_like.
    """
    reader_type = "csv_like"
    
    def __init__(self, source, config_file=None, logger=None, start=None, end=None, keep_normal=False, no_checksum=False) :
        """
            Appelle le constructeur de la classe parente puis positionne ses attributs.
        """
        abstract_reader.Reader.__init__(self, source, config_file, logger, start, end, keep_normal, no_checksum)
        self.linesread = {} # stocke les lignes du fichier pour chaque msg_id
        self.last_line = {} # dernières lignes que l'on va conserver pour chacun des msg_id
        self.init_config()
    
    def init_config(self):
        """
            Initialise la config       
        """
        self.liste_sections = ["structure", "msg_", "instru_", "col_defaut",  "col_"]
        # description de la structure du fichier de config :
        # def_config est un dictionnaire qui contient un ordereddict de paramètres pour chaque section.
        # chaque attribut peut est décrit par le dictionnaire
        # {
        # "required" : True, (defaut = False)
        # "default" : valeur,(defaut = None)
        # "help" : texte d'aide
        # }
        structure = [
                ("separateurs_colonnes" ,{
                                       "required" : True,
                                       "help" : "Séparateurs des colonnes (syntaxe particulière pour ESPACE et TAB). "
                                       }),
                ("separateurs_multiples_ignores" ,{
                                       "help" : "Séparateurs des colonnes (syntaxe particulière pour ESPACE et TAB) que l'on considère comme un seul séparateur lorsque plusieurs sont consécutifs. "
                                       }),
                ("nb_lignes_entete" ,  {
                                       "default" : 0,
                                       "help" : "Nombre de lignes de l'en-tête." 
                                       }),
                ("nb_colonnes" ,       {
                                       "help" : "Nombre de colonnes (n'est pas utile si numero_ligne_nom est défini). "
                                       }),
                ("numero_ligne_nom" ,   {
                                       "default" : None, 
                                       "help" : "Numéro de la ligne qui donne le nom des colonnes. "
                                       }),
                ("numero_ligne_unit" ,  {
                                       "help" : "Numéro de la ligne qui donne les unités des colonnes. "
                                       }),
                ("numero_ligne_misval" ,{
                                       "help" : "Numéro de la ligne qui donne les valeurs des données manquantes des colonnes. "
                                       }),
                ("numero_ligne_borne_sup" ,{
                                       "help" : "Numéro de la ligne qui donne les valeurs supérieures de l'intervalle des bornes. "
                                       }),
                ("numero_ligne_borne_inf" ,{
                                       "help" : "Numéro de la ligne qui donne les valeurs inférieures de l'intervalle des bornes. "
                                       }),
                ("debut_ligne_a_ignorer" , {
                                       "help" : "Les lignes de data commencant par ce caractère seront ignorées. "
                                       }),
                ("colonne_msg_id" ,     {
                                       "default" : None, 
                                       "help" : "Colonne qui donne l'identifiant de message dans le cas de fichiers multi-messages (ex: col_3, col_IdMessage). "
                                       }),
                ("liste_msg_id" ,       {
                                       "help" : "Liste des id de messages. "
                                       }),
                ("temps" ,              {
                                       "help" : "Liste des colonnes qui donnent des informations sur le temps. syntaxe :<col_<A>|NOMFIC|NOMREP>[i1:i2], <col_<B>|NOMFIC|NOMREP>[j1:j2]  (ex:col_1, col_HH,  col_3[0:5] ). On peut également positionner une date en dur qui servira de base aux calculs (ex: 01011904, col_1)"
                                       }),
                ("format_temps" ,       {
                                       "help" : "Chaîne de caractère qui décrit le(s) format(s) de chaque colonne temps séparé(s) par une virgule (cf python strptime) ex : %Y-%m-%d,%H:%M:%S. Si plusieurs formats sont possibles on les sépare par '|' : %Y-%m-%d,%H:%M:%S|%H:%M"
                                       }),
                ("nom_variable_temps" ,         {
                                       "default" : "rft_time_<fic_config>[_msg_<ID>]",
                                       "help" : "Nom de la variable qui contient le temps. "
                                       }),
                ("UTC_offset" ,         {
                                       "default" : '+0000',
                                       "help" : "Chaîne de caractère qui décrit UTC Offset (option %z de strptime) . "
                                       }),
                ("separateur_decimal" , {
                                       "default" : '.',
                                       "help" : "Séparateur décimal. "
                                       }),
                ("colonne_checksum" ,   {
                                       "help" : "Colonne de checksum (ex: col_7, col_CHECK). "
                                       }),
                ("methode_checksum" ,   {
                                       "help" : "Fonction de checksum avec range pour argument. "
                                       }),
                ("ignore_doublons" ,    {
                                       "default" : None,
                                       "help" : "Liste des colonnes ignorées (séparateur = ',') par la recherche de doublons. "
                                       }),
                ("traite_doublons" ,    {
                                       "default" : "True",
                                       "help" : "Si False, on ne traite pas les doublons. "
                                       }),
                ("type_ech" ,           {
                                       "default" : "regulier",
                                       "help" : "Type d'échantillonnage attendu du message (regulier|irregulier). "
                                       }),
                ("freq_ech" ,          {
                                       "default" : None,
                                       "help" : "Fréquence du message en Hz. "
                                       }),
                ("time_bnds" ,         {
                                       "default" : None,
                                       "help" : "Description des bornes de temps : intervalle (-60,0) ou vecteur (vector:rft_bnds_%60) "
                                       })    
                ]
        
        
        
        msg_ =  [
                ("nb_colonnes" ,         {
                                        "inherited" : "structure:nb_colonnes"
                                        }),
                ("temps" ,               {
                                        "inherited" : "structure:temps"
                                        }),
                ("format_temps" ,        {
                                        "inherited" : "structure:format_temps"
                                        }),
                ("nom_variable_temps" ,  {
                                         "inherited" : "structure:nom_variable_temps"
                                        }),
                ("UTC_offset" ,          {
                                     "inherited" : "structure:UTC_offset"
                                        }),
                ("colonne_checksum" ,    {
                                         "inherited" : "structure:colonne_checksum"
                                        }),                         
                ("methode_checksum" ,    {
                                        "inherited" : "structure:methode_checksum"
                                        }),
                ("type_ech" ,            {
                                         "inherited" : "structure:type_ech"
                                        }),
                ("freq_ech" ,           {
                                         "inherited" : "structure:freq_ech"
                                        }),
                ("time_bnds" ,          {
                                        "inherited" : "structure:time_bnds"
                                        })                       
                ]
        
        
        col_defaut =    [            
                        ("unit" ,      {
                                      "default" : "unknown",
                                      "help" : "Unité. "
                                      }),
                        ("misval_in" , {
                                      "default" : "NULL",
                                      "help" : "Valeur manquante dans les données d'entrée. Si présent et non NULL la présence d'un champ vide génère un signalement. "
                                      }),
                        ("misval_out" ,{
                                      "default" : "NaN",
                                      "help" : "Valeur manquante dans les données de sortie. "
                                      }),
                        ("invval_in" , {
                                      "default" : "NULL",
                                      "help" : "Valeur invalide dans les données d'entrée. Si présent et non NULL la présence d'un champ vide génère un signalement. "
                                      }),
                        ("invval_out" ,{
                                      "default" : "NaN",
                                      "help" : "Valeur invalide dans les données de sortie. "
                                      }),
                        ("format" ,    {
                                      "default" : "Ieeefloat_32",
                                      "help" : "Format de sortie selon syntaxe AIDA (Ieeefloat_64, Ieeefloat_32, Int_16, Int_32, Int_64, ...). "
                                      }),
                        ("normal_min" ,{
                                         "help" : "Borne min de l'intervalle de validité de la variable. "
                                      }),
                        ("normal_max" ,{
                                       "help" : "Borne max de l'intervalle de validité de la variable. "
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
        
        col_ =  [                        
                ("ignore" ,      {
                                "default" : "False",
                                "help" : "Pas d'écriture si True. "
                                }),
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
                                "inherited" : "col_defaut:unit",
                                }),
                ("format" ,      {
                                "inherited" : "col_defaut:format", 
                                }),
                ("law" ,         {
                                "help" : "Loi à appliquer selon norme AIDA. (cf doc package readers, module abstract_reader, rechercher 'law') "
                                }),
                ("normal_min" ,  {
                                "inherited" : "col_defaut:normal_min",
                                }),
                ("normal_max" ,  {
                                "inherited" : "col_defaut:normal_max",
                                }),
                ("misval_in" ,   {
                                "inherited" : "col_defaut:misval_in" 
                                }),
                ("misval_out" ,  {
                                "inherited" : "col_defaut:misval_out" 
                                }),
                ("invval_in" ,   {
                                "inherited" : "col_defaut:invval_in" 
                                }),
                ("invval_out" ,  {
                                "inherited" : "col_defaut:invval_out" 
                                }),
                ("instru" ,      {
                                "help" : "Instrument de référence : instru_<N>. "
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
                ("controle" ,    {
                                "help" : "Controle sur la colonne : <fonction:valeur>. "
                                }),                        
                ("orientation" , {
                                "help" : "Description de l'orientation pour les grandeurs physiques orientées. " 
                                }),
                ("bornes" ,      {
                                "help" : "Bornes de chacun des éléments d'un tableau de dimension n>1. bornes = (x1,y1);...;(xn,yn) " 
                                }),
                ("unit_bornes" , {
                                "help" : "Indique l'unité de l'attribut bornes. " 
                                }),
                ("information" , {
                                "help" : "Commentaire libre. "
                                })
                ]

        
        self.def_config = {
                      "structure" : collections.OrderedDict(structure),
                      "msg_" : collections.OrderedDict(msg_),
                      "col_defaut" : collections.OrderedDict(col_defaut),
                      "instru_" : collections.OrderedDict(instru_),
                      "col_" : collections.OrderedDict(col_)
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
        self.config = configparser.RawConfigParser()
        self.config.optionxform = str # pour conserver les majuscules sur les options
        
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
        self.datas = {}
        self.time_list = collections.defaultdict(dict)
        abstract_reader.Reader.read_data(self)
        
        # on ajoute la dernière ligne retenue pour chaque msg_id (si date != datetime.max)
        for m in list(self.linesread.keys()) :
            try :
                if self.last_line[m][0] != datetime.datetime.max :
                    self.linesread[m].append(self.last_line[m])
                    self.logger.debug("{} : dernière date conservée = {}".format(m, self.last_line[m][0]))
            except :
                pass 
        
        for msg_id, lines in list(self.linesread.items()) :
            columnsread = np.transpose(lines)
            lines_to_delete = np.array([], dtype=np.int)
            # on parcours les colonnes
            if self.columns_list != None :
                columns_list = [ s for s in self.config.sections() if s[0:4] == "col_" and s != "col_defaut"]
                if len(columns_list) == 0:
                    columns_list = self.columns_list
            else :
                columns_list = [ s for s in self.config.sections() if s[0:4] == "col_" and s != "col_defaut"]
                if msg_id != "structure" :
                    columns_list = [ s for s in self.config.sections() if s.endswith("@{}".format(msg_id))]
                    
            for c in columns_list :
                column_num, col_2, step = self.columns_cache[c]
                # traitement dim_array > 1
                if col_2 != None :
                    # petit hack pour gérer le dernier élément du range
                    if (col_2-column_num)%step == 0 :
                        column = np.dstack(list((columnsread[c] for c in range(column_num, col_2+1, step))))[0]
                    else :
                        column = np.dstack(list((columnsread[c] for c in range(column_num, col_2, step))))[0]
                else :
                    column = columnsread[column_num]
                if not self.config.has_section(c) : # on en crée une avec juste le nom_variable=nom_colonne (quand la liste des colonnes est dans le fichier de données)
                    self.cfg[c] = {}
                    self.cfg[c]["nom_variable"] = c[4:]
                    try :
                        self.cfg[c]["misval_out"] = self.cfg["structure"]["misval_out"]
                    except :
                        self.cfg[c]["misval_out"] = self.def_config["col_defaut"]["misval_out"]["default"]
                    try :
                        self.cfg[c]["misval_in"] = self.cfg["structure"]["misval_in"]
                    except :
                        self.cfg[c]["misval_in"] = self.def_config["col_defaut"]["misval_in"]["default"]
                    try :
                        self.cfg[c]["invval_out"] = self.cfg["structure"]["invval_out"]
                    except :
                        self.cfg[c]["invval_out"] = self.def_config["col_defaut"]["invval_out"]["default"]
                    try :
                        self.cfg[c]["invval_in"] = self.cfg["structure"]["invval_in"]
                    except :
                        self.cfg[c]["invval_in"] = self.def_config["col_defaut"]["invval_in"]["default"]
                    try :
                        float(column[0])
                        self.cfg[c]["format"] = "Ieeefloat_32"
                        self.cfg[c]["ignore"] = "False"
                    except :
                        self.logger.warning("la colonne {} ne peut pas être convertie en float, on laisse un string".format(c))                        
                        self.cfg[c]["format"] = "string"
                        self.cfg[c]["ignore"] = "True"
                    

                nom_variable = self.cfg[c]["nom_variable"]
                
                #
                # data
                #
                format_out = self.cfg[c]["format"]
                # separateur decimal
                if self.np_string(format_out) != "string" :
                    if self.cfg["structure"]["separateur_decimal"] != self.def_config["structure"]["separateur_decimal"]["default"] :
                        column = np.asarray([x.replace(self.cfg["structure"]["separateur_decimal"],'.') for x in column])
                    
                # valeurs manquantes
                misval_out = eval("np.{}('{}')".format(self.np_string(format_out),self.cfg[c]["misval_out"]))
                misval_in = self.cfg[c]["misval_in"]
                if misval_in != self.def_config["col_defaut"]["misval_in"]["default"] :
                    if '' in column :
                        self.logger.critical("la colonne {} contient des champs vides alors que misval_in ne vaut pas {}".format(c, self.def_config["col_defaut"]["misval_in"]["default"] ))
                        raise abstract_reader.ReaderError ("Erreur à la lecture des donnees")
                    else :
                        column[column==misval_in] = misval_out
                else :
                    column[column==''] = misval_out
                    
                # valeurs invalides
                invval_out = eval("np.{}('{}')".format(self.np_string(format_out),self.cfg[c]["invval_out"]))
                invval_in = self.cfg[c]["invval_in"]
                if invval_in != self.def_config["col_defaut"]["invval_in"]["default"] :
                    column[column==invval_in] = invval_out
                
                # format de sortie : 
                #  on essaye un cast sur la colonne (plus rapide). Si ca échoue, on caste une à une les valeurs
                #  et si échec on remplace par invval_out et on stocke l'indice de la valeur à supprimer plus tard.
                try :
                    column = column.astype(self.np_string(format_out))
                except Exception as e :
                    iv = 0
                    ind_to_delete = []
                    for v in column :
                        try :
                            column[iv] = np.asarray([v], dtype=self.np_string(format_out))[0]
                        except :
                            column[iv] = invval_out
                            ind_to_delete.append(iv)
                        iv += 1
                    column = column.astype(self.np_string(format_out))
                    lines_to_delete = np.union1d(lines_to_delete, np.asarray(ind_to_delete))
                    dates_to_delete = [datetime.datetime.strftime(columnsread[0][ind], "%Y-%m-%dT%H:%M:%S.%f") for ind in ind_to_delete]
                    self.logger.warning("la colonne {} ne peut pas être convertie entièrement dans le type {} : mtv supprime {} valeurs.".format(c, format_out, len(dates_to_delete)))                  
                    if len(dates_to_delete) < 20 : # pour limiter la taille des logs                 
                        self.logger.warning("   liste des dates supprimées : {}".format(dates_to_delete))
                    else :
                        self.logger.warning("   liste des dates supprimées : {}...".format(dates_to_delete[:20]))
                    
                # law
                modified = False
                if self.config.has_option(c, "law") :
                    law = self.cfg[c]["law"]
                    search_result = re.search(r'<(.*)>:(.*)', law)
                    if search_result.group(2).strip() == '' : # la fonction n'a pas de paramètres
                        str_call = "self.{}(column)".format(search_result.group(1))
                    else : # la fonction a des paramètres
                        str_call = "self.{}(column,{})".format(search_result.group(1), search_result.group(2))
                    try :
                        calibrated_col, modified = eval(str_call)
                        if modified : # on stocke la data brute en ajoutant _cal à la clé
                            nom_variable_raw = nom_variable+"_raw"
                            self.datas[nom_variable_raw] = {"data" : column}
                            
                        column = calibrated_col
                    except Exception as e :
                        self.logger.error("la fonction {} a échoué sur la colonne {}".format(law, c))
                        self.logger.error(e)                        

                # normal_min, normal_max
                if not self.keep_normal :
                    if self.config.has_option(c, "normal_min") :
                        if np.isnan(misval_out) :
                            nb_misval_out_before = np.count_nonzero(np.isnan(column))
                        else :
                            nb_misval_out_before = len(np.where(column==misval_out)[0])
                        column_before = column.copy()
                        normal_min = eval("np.{}('{}')".format(self.np_string(format_out),self.cfg[c]["normal_min"]))
                        column[column<normal_min] = misval_out
                        if np.isnan(misval_out) :
                            nb_misval_out_after = np.count_nonzero(np.isnan(column))
                        else :
                            nb_misval_out_after = len(np.where(column==misval_out)[0])
                        if nb_misval_out_after -  nb_misval_out_before != 0 :
                            if np.isnan(misval_out) :
                                liste_index_out_min = np.where(np.isnan(column) != np.isnan(column_before))
                            else :
                                liste_index_out_min = np.where(column != column_before)
                            self.logger.warning("le controle sur normal_min a supprimé {} valeurs dans la colonne {}.".format(nb_misval_out_after-nb_misval_out_before, c))
                            dates_to_delete = [datetime.datetime.strftime(columnsread[0][ind], "%Y-%m-%dT%H:%M:%S.%f") for ind in liste_index_out_min[0]]                    
                            if len(dates_to_delete) < 20 : # pour limiter la taille des logs                 
                                self.logger.warning("   liste des dates supprimées : {}".format(dates_to_delete))
                            else :
                                self.logger.warning("   liste des dates supprimées : {}...".format(dates_to_delete[:20]))
                    if self.config.has_option(c, "normal_max") :
                        if np.isnan(misval_out) :
                            nb_misval_out_before = np.count_nonzero(np.isnan(column))
                        else :
                            nb_misval_out_before = len(np.where(column==misval_out)[0])
                        column_before = column.copy()
                        normal_max = eval("np.{}('{}')".format(self.np_string(format_out),self.cfg[c]["normal_max"]))
                        column[column>normal_max] = misval_out
                        if np.isnan(misval_out) :
                            nb_misval_out_after = np.count_nonzero(np.isnan(column))
                        else :
                            nb_misval_out_after = len(np.where(column==misval_out)[0])
                        if nb_misval_out_after -  nb_misval_out_before != 0 :
                            if np.isnan(misval_out) :
                                liste_index_out_max = np.where(np.isnan(column) != np.isnan(column_before))
                            else :
                                liste_index_out_max = np.where(column != column_before)
                            self.logger.warning("le controle sur normal_max a supprimé {} valeurs dans la colonne {}.".format(nb_misval_out_after-nb_misval_out_before, c))
                            dates_to_delete = [datetime.datetime.strftime(columnsread[0][ind], "%Y-%m-%dT%H:%M:%S.%f") for ind in liste_index_out_max[0]]                    
                            if len(dates_to_delete) < 20 : # pour limiter la taille des logs                 
                                self.logger.warning("   liste des dates supprimées : {}".format(dates_to_delete))
                            else :
                                self.logger.warning("   liste des dates supprimées : {}...".format(dates_to_delete[:20]))
                    
                self.datas[nom_variable] = {"data" : column}
                
                # bornes auto
                try :
                    if "bornes" in self.cfg[c] :
                        if self.cfg[c]["bornes"] == "auto" :                        
                            if self.borne_sup_list and self.borne_sup_list :
                                num_cols = self.col2num_col(c)
                                intervalle = slice(num_cols[0]-1, num_cols[1], 1)
                                bornes = ";".join([f"({inf},{sup})" for inf,sup in 
                                            zip(self.borne_sup_list[intervalle], self.borne_sup_list[intervalle])])
                                self.cfg[c]["bornes"] = bornes
                except Exception as e:
                    self.logger.info(e)
                    self.logger.info("""Problème pour décoder les bornes en mode auto 
                    de la colonne {}. Vérifier les attributs numero_ligne_borne_sup et 
                    numero_ligne_borne_inf de la section structure dans le fichier de 
                    configuration.""".format(c))
                    self.cfg[c]["bornes"] ="coucou"
                #
                # controle sur la colonne
                #
                if self.config.has_option(c, "controle") :
                    controle = self.cfg[c]["controle"]
                    search_result = re.search(r'<(.*)>:(.*)', controle)
                    if search_result.group(2).strip() == '' :
                        str_call = "self.{}(column)".format(search_result.group(1))
                    else :
                        str_call = "self.{}(column,{})".format(search_result.group(1), search_result.group(2))
                    try :
                        to_delete = eval(str_call)
                        if len(to_delete) != 0 :
                            self.logger.warning("le controle {} sur la colonne {} supprime les lignes aux indices suivants {}".format(search_result.group(1), c, to_delete))
                        lines_to_delete = np.union1d(lines_to_delete, to_delete)
                    except Exception as e :
                        self.logger.error("la fonction {} a échoué sur la colonne {}".format(controle, c))
                        self.logger.error(e)
                #
                # infos
                #
                infos = {}
                for o in self.cfg[c] :
                    infos[o] = self.cfg[c][o]
                # valeur par défaut de name
                if not "name" in self.cfg[c] :
                    if not "numero_ligne_nom" in self.cfg["structure"] :
                        infos["name"] = "{} du fichier {}".format(c, self.current_source)
                    else :
                        infos["name"] = "{} du fichier {}".format(c[4:], self.source)
                # valeur par défaut de english_name
                if not "english_name" in self.cfg[c] :
                    if not "numero_ligne_nom" in self.cfg["structure"] :
                        infos["english_name"] = "{} from file {}".format(c, self.current_source)
                    else :
                        infos["english_name"] = "{} from file {}".format(c[4:], self.current_source)
                
                infos["misval"] = misval_out
                infos["invval"] = invval_out        
                infos["temps"] = self.cfg[msg_id]["nom_variable_temps"]
                infos["type_ech"] = self.cfg[msg_id]["type_ech"]
                self.datas[nom_variable]["infos"] = infos
                if self.units_list != None :
                    try :
                        infos["unit"] = self.units_list[column_num-1]
                    except :
                        infos["unit"] = self.def_config["col_defaut"]["unit"]["default"]
                    
                if modified : # une law été appliquée
                    if "unit" not in infos :
                        infos["unit"] = self.def_config["col_defaut"]["unit"]["default"]
                    self.datas[nom_variable_raw]["infos"] = infos.copy()
                    infos["origine"] = "calibration {} {}".format(nom_variable_raw, law)
                                                   
            #
            # temps
            #
            nom_variable_temps = self.cfg[msg_id]["nom_variable_temps"]
            self.datas[nom_variable_temps] = {"data" : columnsread[0]}
            infos = {}
            infos["name"] = nom_variable_temps
            infos["temps"] = nom_variable_temps            
            if self.cfg[msg_id]["freq_ech"] != None :
                infos["freq_ech"] = float(self.cfg[msg_id]["freq_ech"])
            else :
                infos["freq_ech"], diag = self.get_frequency(columnsread[0], nom_variable_temps)
                infos["information"] = diag
            infos["UTC_offset"] = self.cfg[msg_id]["UTC_offset"]
            infos["ignore"] = "False"
            infos["type_ech"] = self.cfg[msg_id]["type_ech"]
            if self.cfg[msg_id]["time_bnds"] != self.def_config["structure"]["time_bnds"]["default"] :
                infos["time_bnds"] = self.cfg[msg_id]["time_bnds"]
            self.datas[nom_variable_temps]["infos"] = infos
            #
            # suppression des valeurs qui n'ont pas passé les controles
            #
            if len(lines_to_delete) != 0 :
                for param, value in list(self.datas.items()) :
                    self.datas[param]["data"] = np.delete(self.datas[param]["data"], lines_to_delete)    
              
    def read_file(self, the_file, encoding='utf-8'):
        """
            Lecture d'un fichier de données.
            
            Pour chaque ligne on calcule le temps (un datetime) avec les infos de la config.
            
            :param the_file: le fichier de données
            :type the_file: str
        """
        self.logger.info("Lecture du fichier {}".format(the_file))
        self.current_file = the_file
        nb_lignes_entete =  int(self.cfg["structure"]["nb_lignes_entete"])
        self.columns_list = None
        self.units_list = None
        self.borne_sup_list = None
        self.borne_inf_list = None
        
        
        if the_file.endswith(".gz") :
            f = gzip.open(the_file, 'rb', encoding=encoding, errors='replace')
        else :
            f = open(the_file, 'r', encoding=encoding, errors='replace')
        all_lines = f.readlines()
        f.close()
        header_lines = all_lines[:nb_lignes_entete]
        data_lines = all_lines[nb_lignes_entete:]

        # si numero_ligne_unit est défini dans [structure], on stocke les unités dans l'attribut units_list
        try :
            numero_ligne_unit = int(self.cfg["structure"]["numero_ligne_unit"])
            # on crée la liste des unités
            line = header_lines[numero_ligne_unit-1].strip("\r\n")
            # si les séparateurs ne sont pas significatifs, on remplace plusieurs séparateurs par un seul et on enlève ceux du début et de fin
            if self.config.has_option("structure", "separateurs_multiples_ignores") :
                for s in self.cfg["structure"]["separateurs_multiples_ignores"] :
                    line = re.sub(r'{}+'.format(s),'{}'.format(s),line).strip(s)
            lineread = [line]
            for delim in self.cfg["structure"]["separateurs_colonnes"] :
                linetmp = []
                for subline in csv.reader(lineread, delimiter=delim) :
                    if not subline : # subline est vide
                        linetmp.append('')
                    else :
                        linetmp.extend(subline)
                lineread = linetmp 
            self.units_list = [ self.parse_unit(unit) for unit in lineread ]
            self.logger.debug(self.units_list)                       
        except :
            pass
            
        # si numero_ligne_borne_sup est défini dans [structure], on stocke les bornes sup dans l'attribut borne_sup_list
        try :
            numero_ligne_borne_sup = int(self.cfg["structure"]["numero_ligne_borne_sup"])
            # on crée la liste des bornes sup
            line = header_lines[numero_ligne_borne_sup-1].strip("\r\n")
            # si les séparateurs ne sont pas significatifs, on remplace plusieurs séparateurs par un seul et on enlève ceux du début et de fin
            if self.config.has_option("structure", "separateurs_multiples_ignores") :
                for s in self.cfg["structure"]["separateurs_multiples_ignores"] :
                    line = re.sub(r'{}+'.format(s),'{}'.format(s),line).strip(s)
            lineread = [line]
            for delim in self.cfg["structure"]["separateurs_colonnes"] :
                linetmp = []
                for subline in csv.reader(lineread, delimiter=delim) :
                    if not subline : # subline est vide
                        linetmp.append('')
                    else :
                        linetmp.extend(subline)
                lineread = linetmp 
            self.borne_sup_list = lineread
            self.logger.debug(self.borne_sup_list)                       
        except :
            pass
            
        # si numero_ligne_borne_inf est défini dans [structure], on stocke les bornes inf dans l'attribut borne_inf_list
        try :
            numero_ligne_borne_inf = int(self.cfg["structure"]["numero_ligne_borne_inf"])
            # on crée la liste des bornes inf
            line = header_lines[numero_ligne_borne_inf-1].strip("\r\n")
            # si les séparateurs ne sont pas significatifs, on remplace plusieurs séparateurs par un seul et on enlève ceux du début et de fin
            if self.config.has_option("structure", "separateurs_multiples_ignores") :
                for s in self.cfg["structure"]["separateurs_multiples_ignores"] :
                    line = re.sub(r'{}+'.format(s),'{}'.format(s),line).strip(s)
            lineread = [line]
            for delim in self.cfg["structure"]["separateurs_colonnes"] :
                linetmp = []
                for subline in csv.reader(lineread, delimiter=delim) :
                    if not subline : # subline est vide
                        linetmp.append('')
                    else :
                        linetmp.extend(subline)
                lineread = linetmp 
            self.borne_inf_list = lineread
            self.logger.debug(self.borne_inf_list)                       
        except :
            pass     
        
        # si numero_ligne_nom est défini dans [structure], on stocke le nom des colonnes dans l'attribut columns_list
        try :
            numero_ligne_nom = int(self.cfg["structure"]["numero_ligne_nom"])
            # on crée la liste des colonnes
            line = header_lines[numero_ligne_nom-1].strip("\r\n")
            # si les séparateurs ne sont pas significatifs, on remplace plusieurs séparateurs par un seul et on enlève ceux du début et de fin
            if self.config.has_option("structure", "separateurs_multiples_ignores") :
                for s in self.cfg["structure"]["separateurs_multiples_ignores"] :
                    line = re.sub(r'{}+'.format(s),'{}'.format(s),line).strip(s)
            lineread = [line]
            for delim in self.cfg["structure"]["separateurs_colonnes"] :
                linetmp = []
                for subline in csv.reader(lineread, delimiter=delim) :
                    if not subline : # subline est vide
                        linetmp.append('')
                    else :
                        linetmp.extend(subline)
                lineread = linetmp
            self.columns_list = [ "col_{}".format(self.parse_nom(c)) for c in lineread ]
            self.logger.debug(self.columns_list)                       
        except :
            pass
        finally : # on met en cache les colonnes et leur(s) num_col (gain de performance par rapport à plein d'appels à col2num_col)
            sections_col_id = [ s for s in self.config.sections() if s[0:4] == "col_" and s != "col_defaut"]
            for s in sections_col_id :
                self.columns_cache[s] = self.col2num_col(s)
            if self.columns_list != None :
                for c in self.columns_list :
                    self.columns_cache[c] = self.col2num_col(c)
            else :
                try :
                    max_nb_colonnes = max([ self.config.getint(s,"nb_colonnes") for s in self.config.sections() if self.config.has_option(s,"nb_colonnes") ])
                    for n in range(1,max_nb_colonnes+1) :
                        c = "col_{}".format(n)
                        self.columns_cache[c] = self.col2num_col(c)
                except :
                    pass
        
        # on construit la liste des col_id ignores par la recherche de doublons
        skip_doublons_index = {}
        ignore_doublons = self.cfg["structure"]["ignore_doublons"]
        if ignore_doublons != None :
            skip_doublons_col_ids = ignore_doublons.split(',')
            for sdci in  skip_doublons_col_ids : 
                col_msg_id, col_2, step = self.columns_cache[sdci]
                msg_id = self.col2msg_id(sdci)
                try :
                    skip_doublons_index[msg_id].append(col_msg_id-1)
                except :
                    skip_doublons_index[msg_id] = []
                    skip_doublons_index[msg_id].append(col_msg_id-1)
        
        # lecture des datas
        line_num = nb_lignes_entete
        for line in data_lines :
            line = line.strip("\r\n")
            line_num += 1
            # si les séparateurs ne sont pas significatifs, on remplace plusieurs séparateurs par un seul et on enlève ceux du début et de fin
            if self.config.has_option("structure", "separateurs_multiples_ignores") :
                for s in self.cfg["structure"]["separateurs_multiples_ignores"] :
                    line = re.sub(r'{}+'.format(s),'{}'.format(s),line).strip(s)
            lineread=[line]
            debut_ligne_a_ignorer = None
            if self.config.has_option("structure", "debut_ligne_a_ignorer") :
                debut_ligne_a_ignorer =  self.cfg["structure"]["debut_ligne_a_ignorer"] 
            if len(lineread[0]) != 0 and lineread[0][0] != debut_ligne_a_ignorer :
                # on éclate la ligne suivant les séparateurs
                try :
                    for delim in self.cfg["structure"]["separateurs_colonnes"] :
                        linetmp = []
                        for subline in csv.reader(lineread, delimiter=delim) :
                            if not subline : # subline est vide
                                linetmp.append('')
                            else :
                                linetmp.extend(subline)
                        lineread = linetmp
                except :
                    self.logger.error("ligne {} : la ligne est illisible, on l'ignore.".format(line_num))
                    continue
                
                # on controle que le nombre d'éléments correspond au nombre de colonnes défini dans la config
                if self.columns_list != None :
                    nb_colonnes = len(self.columns_list)
                    msg_id = "structure"
                else :
                    if self.cfg["structure"]["liste_msg_id"][0] == "no_msg_id" :
                        msg_id = "structure"
                        nb_colonnes = int(self.cfg["structure"]["nb_colonnes"])
                    else :
                        col_msg_id, col_2, step = self.columns_cache[self.cfg["structure"]["colonne_msg_id"]]
                        try :
                            msg_id = "msg_{}".format(lineread[col_msg_id - 1])
                        except :
                            self.logger.warning("ligne {} : impossible de trouver le msg_id pour col_msg_id = {}. La ligne est ignorée.".format(line_num, col_msg_id))
                            continue
                        if not msg_id in self.cfg["structure"]["liste_msg_id"] :
                            self.logger.warning("ligne {} : msg_ID = {} n'est pas défini dans la config (ni une section, ni dans [structure]->liste_msg_id. La ligne est ignorée.".format(line_num, msg_id))
                            continue
                        try :
                            nb_colonnes = int(self.cfg[msg_id]["nb_colonnes"])
                        except :
                            self.logger.error("ligne {} : le nombre de colonnes de msg_ID = {} est inconnu. La ligne est ignorée".format(line_num, msg_id))
                            nb_colonnes = "<undefined>"
                if len(lineread) != nb_colonnes :
                    self.logger.error("ligne {} : {} colonnes attendues, {} trouvées. La ligne est ignorée.".format(line_num, nb_colonnes, len(lineread)))        
                else :
                    # on vérifie le checksum
                    if self.config.has_option(msg_id, "colonne_checksum") and self.no_checksum == False :
                        col, _slice = self.split_slice(self.cfg[msg_id]["colonne_checksum"])
                        col_checksum, col_2, step = self.columns_cache[col]
                        if _slice != None :
                            checksum = eval("lineread[col_checksum-1]{}".format(_slice))
                        else : 
                            checksum = lineread[col_checksum-1]
                        search_result = re.search(r'<(.*)>:(.*)', self.cfg[msg_id]["methode_checksum"])
                        if search_result.group(2).strip() == '' : # la fonction n'a pas de paramètres
                            str_call = "self.{}(line,checksum)".format(search_result.group(1))
                        else : # la fonction a des paramètres
                            str_call = "self.{}(line, checksum,{})".format(search_result.group(1), search_result.group(2))
                        
                        if not eval(str_call) :
                            self.logger.error("ligne {} : erreur de checksum. La ligne est ignorée.".format(line_num))
                            continue
                        
                    # on calcule le temps que l'on insère en début de lineread
                    time = self.get_time(lineread)
                    if isinstance(time, str) :
                        self.logger.error("ligne {} : impossible de décoder le temps. La ligne est ignorée.".format(line_num))
                        self.logger.error(time)
                    else :
                        # on teste les bornes temporelles : on conserver la date la plus proche de end
                        if msg_id not in list(self.last_line.keys()) :
                            self.last_line[msg_id] = [datetime.datetime.max]
                        if self.start != None :
                            if time < self.start :
                                continue
                        if self.end != None :
                            if time > self.end :
                                if time < self.last_line[msg_id][0] :
                                    lineread.insert(0, time)
                                    self.last_line[msg_id] = lineread
                                continue
                        # traitement des doublons
                        if self.cfg["structure"]["traite_doublons"].lower() == "true" :
                            try :                            
                                doublons = False
                                f = None
                                for i in self.time_list[msg_id][time] :
                                    if f is None :
                                        doublon_indexes = list(range(nb_colonnes))
                                        if msg_id in list(skip_doublons_index.keys()) :
                                            for j in skip_doublons_index[msg_id] :
                                                doublon_indexes.remove(j)
                                        f = itemgetter(*doublon_indexes)
                                    if f(self.linesread[msg_id][i][1:]) == f(lineread) :
                                        self.logger.warning("doublon détecté : {}".format(time))
                                        doublons = True
                                    else :
                                        self.logger.warning("faux doublon détecté : {}".format(time))
                                if doublons :
                                    continue
                            except :
                                self.time_list[msg_id][time] = []
                        lineread.insert(0, time)
                        try :
                            self.linesread[msg_id].append(lineread)
                        except :
                            self.linesread[msg_id] = []
                            self.linesread[msg_id].append(lineread)
                        if self.cfg["structure"]["traite_doublons"].lower() == "true" :
                            self.time_list[msg_id][time].append(len(self.linesread[msg_id])-1)   
        
    def read_url(self):
        """
            Lecture d'une URL.
        """
        self.logger.info("Lecture de l'URL {}".format(self.source))
        
    def help_config(self, required=True):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = "\n\nDescription du fichier de configuration du type {} :\n".format(self.reader_type)
        str_help += "-"*(len(str_help)-3)
        str_help += "\n\nLe fichier de configuration est de type .ini : il est composé de sections entre crochets à l'intérieur \ndesquelles sont définis des attributs sous la forme \n  attribut = valeur.\n"
        str_help += "Les attributs peuvent être requis et avoir une valeur par défaut.\n"
        str_help += "L'ordre des sections ainsi que l'ordre des attributs à l'intérieur des sections n'a pas d'importance.\n"
        str_help += "Le section [structure] est obligatoire.\n"
        str_help += "Les colonnes sont identifiées soit par leur numéro (col_1,..,col_N) soit par leur nom (col_humidite, col_tempe, ...)\n"
        str_help += "\n\nFormat attendu (* = paramètre hérité) :\n" 
        for section in self.liste_sections :
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
        if required :
            str_help += "\nATTENTION : le fichier de configuration est OBLIGATOIRE pour \
le reader {}\n".format(self.reader_type)
        else :
            str_help += "\nATTENTION : le fichier de configuration n'est PAS OBLIGATOIRE pour \
le reader {}\n".format(self.reader_type)    
        return str_help
            
    def check_config(self):
        """
            Vérifie la cohérence du fichier de config et positionne les valeurs par défaut.
            
            :return:True ou False
            :rtype: Boolean
        """
        sections_msg_id = [ s for s in self.config.sections() if s[0:4] == "msg_"]
        sections_col_id = [ s for s in self.config.sections() if s[0:4] == "col_" and s != "col_defaut"]
        
        #
        # Controle des sections
        #
        for section in self.config.sections() :
            if len ([s for s in self.liste_sections if section[0:len(s)] == s]) == 0 :
                self.logger.critical("Erreur dans le fichier de configuration : la section [{}] n'est pas exploitable par ce reader.".format(section))
                return False 
        
        #
        # Elements obligatoires
        #
        
        # [structure] est obligatoire
        if self.config.has_section("structure") == False :
            self.logger.critical("Erreur dans le fichier de configuration : la section [structure] est obligatoire.")
            return False
        # separateurs_colonnes est obligatoire dans [structure]
        if not self.config.has_option("structure", "separateurs_colonnes") :
            self.logger.critical("Erreur dans le fichier de configuration : separateurs_colonnes est obligatoire dans [structure].")
            return False
        # temps est obligatoire dans [structure] ou dans tous les [msg_<ID>]
        if not self.config.has_option("structure", "temps") :
            if len(sections_msg_id) == 0 :
                self.logger.critical("Erreur dans le fichier de configuration : temps est obligatoire dans [structure] ou dans tous les [msg_<ID>].")
                return False
            for section in sections_msg_id :
                if not self.config.has_option(section, "temps") :
                    self.logger.critical("Erreur dans le fichier de configuration : temps est obligatoire dans [structure] ou dans tous les [msg_<ID>].")
                    return False
        # format_temps est obligatoire dans [structure] ou dans tous les [msg_<ID>]
        if not self.config.has_option("structure", "format_temps") :
            if len(sections_msg_id) == 0 :
                self.logger.critical("Erreur dans le fichier de configuration : format_temps est obligatoire dans [structure] ou dans tous les [msg_<ID>].")
                return False
            for section in sections_msg_id :
                if not self.config.has_option(section, "format_temps") :
                    self.logger.critical("Erreur dans le fichier de configuration : format_temps est obligatoire dans [structure] ou dans tous les [msg_<ID>].")
                    return False            
        # Si numero_ligne_nom n'est pas défini, nb_colonnes est obligatoire soit dans [structure] soit dans tous les [msg_<ID>]
        if not self.config.has_option("structure", "numero_ligne_nom") :
            if not self.config.has_option("structure", "nb_colonnes") :                
                if len(sections_msg_id) == 0 :
                    self.logger.critical("Erreur dans le fichier de configuration : nb_colonnes est obligatoire dans [structure] ou dans tous les [msg_<ID>] si numero_ligne_nom n'est pas défini.")
                    return False
                for section in sections_msg_id :
                    if not self.config.has_option(section, "nb_colonnes") :
                        self.logger.critical("Erreur dans le fichier de configuration : nb_colonnes est obligatoire dans [structure] ou dans tous les [msg_<ID>] si numero_ligne_nom n'est pas défini.")
                        return False
            
        #
        # Elements liés (obligatoirement présents ensemble)
        #
                    
        # colonne_checksum et methode_checksum sont liés
        if len(sections_msg_id) != 0 :
            for s in sections_msg_id :
                if self.config.has_option(s, "methode_checksum") and not self.config.has_option(s, "colonne_checksum") :
                    self.logger.critical("Erreur dans le fichier de configuration section [{}] : methode_checksum est défini mais pas colonne_checksum.".format(s))
                    return False
                if self.config.has_option(s, "colonne_checksum") and not self.config.has_option(s, "methode_checksum") :
                    self.logger.critical("Erreur dans le fichier de configuration section [{}] : colonne_checksum est défini mais pas methode_checksum.".format(s))
                    return False
                                                                                                         
        # si colonne_msg_id est défini dans [structure], il faut au moins un [msg_<ID>]
        if self.config.has_option("structure", "colonne_msg_id") :
            if len(sections_msg_id) == 0 :
                self.logger.critical("Erreur dans le fichier de configuration : colonne_msg défini dans [structure] mais il n'existe aucun [msg_<ID>].")
                return False
        
        # existence des sections [instru_N]
        for s in sections_col_id :
            if self.config.has_option(s, "instru") :
                instru = self.config.get(s, "instru")
                if not self.config.has_section(instru) :
                    self.logger.critical("Erreur dans le fichier de configuration :  la section [{}] fait référence à {} qui n'est pas défini".format(s, instru))
                    return False
                
        #
        # Héritage [structure] -> [msg_<ID>]
        #
        for section in sections_msg_id :
            if not self.config.has_option(section, "nb_colonnes") :
                self.config.set(section, "nb_colonnes", self.config.get("structure", "nb_colonnes"))
            if not self.config.has_option(section, "temps") :
                self.config.set(section, "temps", self.config.get("structure", "temps"))
            if not self.config.has_option(section, "format_temps") :               
                self.config.set(section, "format_temps", self.config.get("structure", "format_temps"))
            if not self.config.has_option(section, "UTC_offset") :
                if self.config.has_option("structure", "UTC_offset") :               
                    self.config.set(section, "UTC_offset", self.config.get("structure", "UTC_offset"))
            if not self.config.has_option(section, "nom_variable_temps") :
                if self.config.has_option("structure", "nom_variable_temps") :               
                    self.config.set(section, "nom_variable_temps", self.config.get("structure", "nom_variable_temps"))
            if not self.config.has_option(section, "colonne_checksum") :
                if self.config.has_option("structure", "colonne_checksum") :               
                    self.config.set(section, "colonne_checksum", self.config.get("structure", "colonne_checksum"))
            if not self.config.has_option(section, "methode_checksum") :
                if self.config.has_option("structure", "methode_checksum") :               
                    self.config.set(section, "methode_checksum", self.config.get("structure", "methode_checksum"))
            if not self.config.has_option(section, "type_ech") :
                if self.config.has_option("structure", "type_ech") :               
                    self.config.set(section, "type_ech", self.config.get("structure", "type_ech"))
            if not self.config.has_option(section, "freq_ech") :
                if self.config.has_option("structure", "freq_ech") :               
                    self.config.set(section, "freq_ech", self.config.get("structure", "freq_ech"))
            if not self.config.has_option(section, "time_bnds") :
                if self.config.has_option("structure", "time_bnds") :               
                    self.config.set(section, "time_bnds", self.config.get("structure", "time_bnds"))
                    
        #
        # Héritage [col_defaut] -> [col_<ID>]
        #
        if not self.config.has_section("col_defaut") :
            self.config.add_section("col_defaut")
        for section in sections_col_id :
            if not self.config.has_option(section, "misval_in") :
                if self.config.has_option("col_defaut", "misval_in") :               
                    self.config.set(section, "misval_in", self.config.get("col_defaut", "misval_in"))
            if not self.config.has_option(section, "misval_out") :
                if self.config.has_option("col_defaut", "misval_out") :               
                    self.config.set(section, "misval_out", self.config.get("col_defaut", "misval_out"))                   
            if not self.config.has_option(section, "invval_in") :
                if self.config.has_option("col_defaut", "invval_in") :               
                    self.config.set(section, "invval_in", self.config.get("col_defaut", "invval_in"))
            if not self.config.has_option(section, "invval_out") :
                if self.config.has_option("col_defaut", "invval_out") :               
                    self.config.set(section, "invval_out", self.config.get("col_defaut", "invval_out"))                    
            if not self.config.has_option(section, "format") :
                if self.config.has_option("col_defaut", "format") :               
                    self.config.set(section, "format", self.config.get("col_defaut", "format"))
            if not self.config.has_option(section, "normal_min") :
                if self.config.has_option("col_defaut", "normal_min") :               
                    self.config.set(section, "normal_min", self.config.get("col_defaut", "normal_min"))
            if not self.config.has_option(section, "normal_max") :
                if self.config.has_option("col_defaut", "normal_max") :               
                    self.config.set(section, "normal_max", self.config.get("col_defaut", "normal_max"))
            if not self.config.has_option(section, "unit") :
                if self.config.has_option("col_defaut", "unit") :               
                    self.config.set(section, "unit", self.config.get("col_defaut", "unit"))
        
        #
        # Héritage [instru_N] -> [col_<ID>]
        #
        for section in sections_col_id :
            if self.config.has_option(section, "instru") :
                instru = self.config.get(section, "instru")
                if not self.config.has_option(section, "position") :
                    if self.config.has_option(instru, "position") :               
                        self.config.set(section, "position", self.config.get(instru, "position"))
                if not self.config.has_option(section, "chaine_acquisition") :
                    if self.config.has_option(instru, "chaine_acquisition") :               
                        self.config.set(section, "chaine_acquisition", self.config.get(instru, "chaine_acquisition"))
                # on traite également chaine_mesure pour compatibilité avec les anciens vecteurs
                if not self.config.has_option(section, "chaine_mesure") :
                    if self.config.has_option(instru, "chaine_mesure") :               
                        self.config.set(section, "chaine_mesure", self.config.get(instru, "chaine_mesure"))
                modules_id = [ m for m in self.config.options(instru) if m[0:7] == "module_"]
                for m in modules_id :
                    if not self.config.has_option(section, m) :
                        self.config.set(section, m, self.config.get(instru,m))
        #
        # Valeurs par défaut
        #
        
        # nb_lignes_entete        
        if not self.config.has_option("structure", "nb_lignes_entete") :
            self.config.set("structure", "nb_lignes_entete", self.def_config["structure"]["nb_lignes_entete"]["default"])
        # separateur_decimal
        if not self.config.has_option("structure", "separateur_decimal") :
            self.config.set("structure", "separateur_decimal", self.def_config["structure"]["separateur_decimal"]["default"])
        # UTC_offset
        if not self.config.has_option("structure", "UTC_offset") :
            self.config.set("structure", "UTC_offset", self.def_config["structure"]["UTC_offset"]["default"])
        for s in sections_msg_id :
            if not self.config.has_option(s, "UTC_offset") :
                self.config.set(s, "UTC_offset", self.def_config["structure"]["UTC_offset"]["default"])
        # type_ech
        if not self.config.has_option("structure", "type_ech") :
            self.config.set("structure", "type_ech", self.def_config["structure"]["type_ech"]["default"])
        for s in sections_msg_id :
            if not self.config.has_option(s, "type_ech") :
                self.config.set(s, "type_ech", self.def_config["structure"]["type_ech"]["default"])
        # nom_variable_temps
        try :        
            if not self.config.has_option("structure", "nom_variable_temps") :
                self.config.set("structure", "nom_variable_temps", "rft_time_{}".format(os.path.basename(self.config_file)))
            for s in sections_msg_id :
                if not self.config.has_option(s, "nom_variable_temps") :
                    self.config.set(s, "nom_variable_temps", "rft_time_{}_{}".format(os.path.basename(self.config_file), s[4:]))
        except :
            self.logger.critical("Erreur dans la configuration : impossible de définir nom_variable_temps (pas de fichier de config pour contruire une valeur par défaut)")
            return False
        # colonne_msg_id
        if not self.config.has_option("structure", "colonne_msg_id") :
            self.config.set("structure", "colonne_msg_id",self.def_config["structure"]["colonne_msg_id"]["default"])
        # traite_doublons
        if not self.config.has_option("structure", "traite_doublons") :
            self.config.set("structure", "traite_doublons",self.def_config["structure"]["traite_doublons"]["default"])
        # ignore_doublons
        if not self.config.has_option("structure", "ignore_doublons") :
            self.config.set("structure", "ignore_doublons",self.def_config["structure"]["ignore_doublons"]["default"])
        # liste_msg_id si colonne_msg_id est défini
        if self.config.get("structure", "colonne_msg_id") is None  :
            self.config.set("structure", "liste_msg_id", ["no_msg_id"])
        elif not self.config.has_option("structure", "liste_msg_id"):
            self.config.set("structure", "liste_msg_id", sections_msg_id)
        else :
            liste_msg_id = [ x.strip() for x in self.config.get("structure", "liste_msg_id").split(',')]
            self.config.set("structure", "liste_msg_id",liste_msg_id)
        # freq_ech
        if not self.config.has_option("structure", "freq_ech") :
            self.config.set("structure", "freq_ech",self.def_config["structure"]["freq_ech"]["default"])
        for s in sections_msg_id :
                if not self.config.has_option(s, "freq_ech") :
                    self.config.set(s, "freq_ech", self.def_config["structure"]["freq_ech"]["default"])
        # time_bnds
        if not self.config.has_option("structure", "time_bnds") :
            self.config.set("structure", "time_bnds",self.def_config["structure"]["time_bnds"]["default"])
        for s in sections_msg_id :
                if not self.config.has_option(s, "time_bnds") :
                    self.config.set(s, "time_bnds", self.def_config["structure"]["time_bnds"]["default"])
        # misval_in
        if not self.config.has_option("col_defaut", "misval_in") :
            self.config.set("col_defaut", "misval_in", self.def_config["col_defaut"]["misval_in"]["default"])
        for s in sections_col_id :
            if not self.config.has_option(s, "misval_in") :
                self.config.set(s, "misval_in", self.def_config["col_defaut"]["misval_in"]["default"])
        # misval_out
        if not self.config.has_option("col_defaut", "misval_out") :
            self.config.set("col_defaut", "misval_out", self.def_config["col_defaut"]["misval_out"]["default"])
        for s in sections_col_id :
            if not self.config.has_option(s, "misval_out") :
                self.config.set(s, "misval_out", self.def_config["col_defaut"]["misval_out"]["default"])
        # invval_in
        if not self.config.has_option("col_defaut", "invval_in") :
            self.config.set("col_defaut", "invval_in", self.def_config["col_defaut"]["invval_in"]["default"])
        for s in sections_col_id :
            if not self.config.has_option(s, "invval_in") :
                self.config.set(s, "invval_in", self.def_config["col_defaut"]["invval_in"]["default"])
        # invval_out (= misval_out par defaut)
        if not self.config.has_option("col_defaut", "invval_out") :
            self.config.set("col_defaut", "invval_out", self.config.get("col_defaut", "misval_out"))
        for s in sections_col_id :
            if not self.config.has_option(s, "invval_out") :
                self.config.set(s, "invval_out",  self.config.get(s, "misval_out"))        
        # format
        if not self.config.has_option("col_defaut", "format") :
            self.config.set("col_defaut", "format", self.def_config["col_defaut"]["format"]["default"])
        for s in sections_col_id :
            if not self.config.has_option(s, "format") :
                self.config.set(s, "format", self.def_config["col_defaut"]["format"]["default"])
        # ignore
        for s in sections_col_id :
            if not self.config.has_option(s, "ignore") :
                self.config.set(s, "ignore", self.def_config["col_"]["ignore"]["default"])                
        # nom_variable
        for s in sections_col_id :
            if not self.config.has_option(s, "nom_variable") :
                if not self.config.has_option("structure", "numero_ligne_nom") :
                    default = s
                else :
                    default = s[4:]
                self.config.set(s, "nom_variable", default)
        # unit
        if not self.config.has_option("structure", "numero_ligne_unit") :
            if not self.config.has_option("col_defaut", "unit") :
                self.config.set("col_defaut", "unit", self.def_config["col_defaut"]["unit"]["default"])
            for s in sections_col_id :
                if not self.config.has_option(s, "unit") :
                    self.config.set(s, "unit", self.def_config["col_defaut"]["unit"]["default"])      
        
        #
        # Controles divers
        #
        
        # traitement des mots clés des separateurs_colonnes
        separateurs_colonnes = self.config.get("structure", "separateurs_colonnes").replace(" ",'').replace('\t','').replace("ESPACE", " ").replace("TAB",'\t')
        self.config.set("structure", "separateurs_colonnes", separateurs_colonnes)
        if self.config.has_option("structure", "separateurs_multiples_ignores") :
            separateurs_multiples_ignores = self.config.get("structure", "separateurs_multiples_ignores").replace(" ",'').replace('\t','').replace("ESPACE", " ").replace("TAB",'\t')
            self.config.set("structure", "separateurs_multiples_ignores", separateurs_multiples_ignores)
        
        # les elements de separateurs_multiples_ignores doivent être dans separateurs_colonnes
        if self.config.has_option("structure", "separateurs_multiples_ignores") :
            separateurs_multiples_ignores = self.config.get("structure", "separateurs_multiples_ignores")
            separateurs_colonnes = self.config.get("structure", "separateurs_colonnes")
            for s in separateurs_multiples_ignores :
                if s not in separateurs_colonnes :
                    self.logger.critical("Erreur dans le fichier de configuration section [structure] : le separateur \"{}\" présent dans separateurs_multiples_ignores n'est pas dans separateurs_colonnes".format(s))
                    return False
        
        # méthode_checksum : on vérifie la syntaxe et que la fonction existe
        if self.config.has_option("structure", "methode_checksum") :
            methode_checksum = self.config.get("structure", "methode_checksum")
            if not self.check_function("structure", "methode_checksum", methode_checksum) :
                return False
        for s in sections_msg_id :
            if self.config.has_option(s, "methode_checksum") :
                methode_checksum = self.config.get(s, "methode_checksum")
                if not self.check_function(s, "methode_checksum", methode_checksum) :
                    return False

        for s in sections_col_id :
            if self.config.has_option(s, "law") :
                law = self.config.get(s, "law")
                if not self.check_function(s, "law", law) :
                    return False
                
        # loi de calibration (law) : on vérifie la syntaxe et que la fonction existe
        for s in sections_col_id :
            if self.config.has_option(s, "law") :
                law = self.config.get(s, "law")
                if not self.check_function(s, "law", law) :
                    return False
                                
        # controle : on vérifie la syntaxe et que la fonction existe
        for s in sections_col_id :
            if self.config.has_option(s, "controle") :
                controle = self.config.get(s, "controle")
                if not self.check_function(s, "controle", controle) :
                    return False
                
        # format reconnu
        for s in sections_col_id :
            fmt = self.config.get(s, "format")
            if self.np_string(fmt) is None :
                self.logger.critical("Erreur : le format {} défini dans [{}] n'est pas connu par le reader.".format(fmt,s))
                return False
            
        # misval_out doit être convertible dans le format                                                             
        for s in sections_col_id :
            misval_out = self.config.get(s, "misval_out")
            fmt = self.config.get(s, "format")
            try :
                eval("np.{}('{}')".format(self.np_string(fmt),misval_out))
            except :
                self.logger.critical("Erreur : misval_out ({}) défini dans [{}] n'est pas convertible dans le format {}.".format(misval_out, s, fmt))
                return False
            
        # invval_out doit être convertible dans le format                                                             
        for s in sections_col_id :
            invval_out = self.config.get(s, "invval_out")
            fmt = self.config.get(s, "format")
            try :
                eval("np.{}('{}')".format(self.np_string(fmt),invval_out))
            except :
                self.logger.critical("Erreur : invval_out ({}) défini dans [{}] n'est pas convertible dans le format {}.".format(invval_out, s, fmt))
                return False
            
        # tous les modules de chaine_acquisition doivent être définis.
        # on traite l'attribut chaine_mesure pour compatibilité avec les vieux vecteurs.
        for s in sections_col_id :
            chaine_acquisition = None
            if self.config.has_option(s, "chaine_acquisition") :
                chaine_acquisition = self.config.get(s, "chaine_acquisition").split(' ')
            if self.config.has_option(s, "chaine_mesure") :
                chaine_acquisition = self.config.get(s, "chaine_mesure").split(' ')
            if chaine_acquisition :    
                for c in chaine_acquisition :
                    if not self.config.has_option(s, c) :
                        self.logger.critical("Erreur : le module {} n'est pas défini dans {}.".format(c, s))
                        return False
    
        # type_ech doit valoir regulier ou irregulier et doit valoir irregulier si freq=0
        type_ech = self.config.get("structure", "type_ech")
        if type_ech != "regulier" and type_ech != "irregulier" :
            self.logger.critical("Erreur : type_ech = {} n'est pas connu (valeurs admises = regulier|irregulier) dans [structure].".format(type_ech))
            return False
        try :
            if float(self.config.get("structure", "freq_ech")) == 0  :
                self.config.set("structure", "type_ech", "irregulier")
        except :
            pass
        for s in sections_msg_id :
            type_ech = self.config.get(s, "type_ech")
            if type_ech != "regulier" and type_ech != "irregulier" :
                self.logger.critical("Erreur : type_ech = {} n'est pas connu (valeurs admises = regulier|irregulier) dans [{}].".format(type_ech, s))
                return False
            try :
                if float(self.config.get(s, "freq_ech")) == 0  :
                    self.config.set(s, "type_ech", "irregulier")
            except :
                pass
            
        # time_bnds doit décrire un intervalle (float,float) ou vecteur (vector:nom_du_vecteur)
        time_bnds = self.config.get("structure", "time_bnds")
        print("TIME_BNDS",time_bnds)
        if time_bnds != self.def_config["structure"]["time_bnds"]["default"] :
            if not self.check_time_bnds(time_bnds) :
                self.logger.critical("Erreur : time_bnds = {} ne décrit ni un intervalle ni un vecteur.".format(time_bnds))
                return False
        for s in sections_msg_id :
            time_bnds = self.config.get(s, "time_bnds")
            if time_bnds != self.def_config["structure"]["time_bnds"]["default"] :
                if not self.check_time_bnds(time_bnds) :
                    self.logger.critical("Erreur : time_bnds = {} ne décrit ni un intervalle ni un vecteur dans [{}].".format(time_bnds, s))
                    return False
            
        # on cache la config dans self.cfg pour ne plus avoir à utiliser self.config.get peu performant
        for s in self.config.sections() :
            for o in self.config.options(s) :
                self.cfg[s][o] = self.config.get(s,o)
                
        return True
    
    
    def check_function(self, section, param, str_func):
        """
            Vérification de la syntaxe et de l'existence d'une fonction définie dans la config.
            
            Syntaxe = <fonction>: param1, param2, ...
        
            :param section: la section qui contient la fonction
            :type param: str
            :param param: le paramètre associé à la fonction
            :type param: str
            :param str_func: la fonction telle que définie dans la config
            :type param: str
            :return: résultat de la vérification
            :rtype: bool
        """
        search_result = re.search(r'<(.*)>:(.*)', str_func)
        if search_result != None :
            fn = search_result.group(1)
            try :
                is_function = eval("callable(self.{})".format(fn))
                if not is_function :
                    self.logger.critical("Erreur dans le fichier de configuration section [{}] : le champ {} ne définit pas une fonction appelable par le reader.".format(section, param))
                    return False
            except :
                self.logger.critical("Erreur dans le fichier de configuration section [{}] : le champ {} ne définit pas une fonction connue par le reader.".format(section, param))
                return False
        else :
            self.logger.critical("Erreur dans le fichier de configuration section [{}] : la syntaxe du champ {} est incorrecte ({}).".format(section, param, str_func))
            return False
        return True

    def check_time_bnds(self, time_bnds) :
        """
            Vérification de la syntaxe du champs time_bnds qui décrit soit un intervalle soit un vecteur.
            
            Syntaxe pour un intervale = float,float
            Syntaxe pour un vecteur = vector:nom_du_vecteur
            
            :param section: la section qui contient la fonction
            :type param: str
            :return: résultat de la vérification
            :rtype: bool
        """
        if not time_bnds.lower().startswith("vector:") :
            try :
                inter = time_bnds.split(',')
                if len(inter) != 2 :
                    return False
                float(inter[0])
                float(inter[1])
            except :
                return False
        return True
                
