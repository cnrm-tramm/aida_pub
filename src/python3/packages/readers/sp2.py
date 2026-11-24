#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from readers import abstract_reader
import struct
import numpy as np
import datetime as dt
import collections



class Reader(abstract_reader.Reader) :
    """
        Reader pour le type sp2, board 6133
    """
    reader_type = "sp2"
    
    def __init__(self, source, config_file=None, logger=None, start=None, end=None, keep_normal=False, no_checksum=False) :
        """
            Appelle le constructeur de la classe parente puis positionne ses attributs.
        """
        abstract_reader.Reader.__init__(self, source, config_file, logger, start, end, keep_normal, no_checksum)
        self.liste_var = ["ray_scat_hg", "ray_inc_wb_hg", "ray_inc_nb_hg", "ray_split_hg", "ray_scat_lg", "ray_inc_wb_lg", "ray_inc_nb_lg", "ray_split_lg"] 
        self.freq = 2500000 #6133 board 
        self.periode = 1/self.freq
        
    def read_config(self) :
        """
            Pas de fichier de config, méthode muette.
        """
        return True 
    
    def read_file(self, the_file, encoding='utf-8'):
        """
            Lecture du fichier de données
         
            Pour lire le fichier on utilise le module struct (https://docs.python.org/3/library/struct.html)
            c'est du big endian : > dans le format
            On lit les données dans des list que l'on concatène ensuite dans la structure datas : c'est bien
            plus performant que de concaténer des np.array
            Pour le temps, on stocke des timestamps et on convertit an datetime le plus tard possible.
        """
        self.logger.info("Lecture du fichier {}".format(the_file))
        date_jour = dt.datetime.strptime(os.path.basename(the_file)[0:8], "%Y%m%d")
        ts_jour = date_jour.timestamp()
        date_01011904 = dt.datetime.strptime("1904-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        datas_final = [] # stockage des datas
        ts_final = [] # stockage des timestamp
        index_time_final = [] # stockage des index permettant de recalculer un temps (voir doc constructeur)
        count = 0
        with open (the_file, 'rb') as file :
            while True :
                try :
                    if self.datas is None :
                        # Initialisations en dur, pas de config
                        self.datas = collections.defaultdict(dict)
                        for v in self.liste_var :
                            self.datas[v]['data'] = np.array([])
                            self.datas[v]['infos'] = {}
                            self.datas[v]['infos']["temps"] = "rft_time_sp2"
                            self.datas[v]['infos']["freq_ech"] = self.freq
                            self.datas[v]['infos']["ignore"] = "False"
                        self.datas["rft_time_sp2"]['data'] = np.array([])
                        self.datas["rft_time_sp2"]['infos'] = {}
                        self.datas["rft_time_sp2"]['infos']["temps"] = "rft_time_sp2"
                        self.datas["rft_time_sp2"]['infos']["freq_ech"] = self.freq
                        self.datas["rft_time_sp2"]['infos']["ignore"] = "False"
                        self.datas["ctl_index_time_sp2"]['data'] = np.array([])
                        self.datas["ctl_index_time_sp2"]['infos'] = {}
                        self.datas["ctl_index_time_sp2"]['infos']["temps"] = "rft_time_sp2"
                        self.datas["ctl_index_time_sp2"]['infos']["freq_ech"] = self.freq
                        self.datas["ctl_index_time_sp2"]['infos']["ignore"] = "False"
                    
                    #
                    # Lecture du fichier de données
                    #
                    dims= struct.unpack('>ii', file.read(8))
                    size = dims[0]*dims[1]        
                    datas = list(struct.unpack('>{}h'.format(size), file.read(2*size)))
                    flag = struct.unpack('>H', file.read(2))
                    time_stamp_buffer = struct.unpack('>f', file.read(4))
                    buffer_index = int(time_stamp_buffer[0]/self.periode)
                    reserverd1 = struct.unpack('>f', file.read(4))
                    event_index = struct.unpack('>f', file.read(4))
                    time_10000 = struct.unpack('>f', file.read(4))
                    time_remainder = struct.unpack('>f', file.read(4))
                    #delta_sec = dt.timedelta(seconds=time_10000[0]*10000 + time_remainder[0])            
                    #date = date_01011904 + delta_sec         
                    reserverd5 = struct.unpack('>f', file.read(4))
                    reserverd6 = struct.unpack('>f', file.read(4))
                    reserverd7 = struct.unpack('>d', file.read(8))
                    reserverd8 = struct.unpack('>d', file.read(8))        
                    spare_no_elts_1 = struct.unpack('>i', file.read(4))
                    spare = struct.unpack('>{}f'.format(spare_no_elts_1[0]), file.read(4*spare_no_elts_1[0]))
                    
                    #
                    # Remplissage des listes finales :
                    #  datas_final = les datas
                    #  ts_final = les timestamp
                    #
                    # D'abord les datas
                    #
                    datas_final.append(datas)
                    #
                    # Puis le temps
                    #
                    delta_ts_event = event_index[0] * self.periode # correspond à ts_event -ts_buffer (voir doc intrument)
                    # on contruit un tableau de ts avec pour base ts_event
                    ts_datas = np.array([ts_jour+time_stamp_buffer[0]+delta_ts_event]*dims[0])
                    # on construit un tableau de delta ts à appliquer
                    deltas = np.arange(dims[0])*self.periode
                    # on applique le delta ts
                    ts_datas = ts_datas + deltas
                    # on ajoute au tableau final
                    ts_final.append(list(ts_datas))

                    #
                    # Et enfin les index des datas par rapport à J 00H (a utiliser à la place du temps pour pouvoir zoomer à fond)
                    #
                    index_time_datas = np.ones(dims[0])*buffer_index + np.arange(event_index[0], event_index[0]+dims[0])
                    index_time_final.append(list(index_time_datas))

                    count = count+1
                    #print(count)
                    #
                    #if count == 1 :
                    #    break
                    #
                except Exception as e:
                    self.logger.info("Fin de lecture du fichier {}".format(the_file))
                    break
        #
        # Remplissage de la structure datas
        #
        np_datas = np.reshape(datas_final, (count*dims[0], dims[1]))
        for i in range(len(self.liste_var)) :
            nom_variable = self.liste_var[i]
            self.datas[nom_variable]["data"] = np.append(self.datas[nom_variable]["data"], np_datas[:,i])
        dates_result = [ dt.datetime.fromtimestamp(t) for t in np.reshape(ts_final, count*dims[0]) ]
        self.datas["rft_time_sp2"]["data"] = np.append(self.datas["rft_time_sp2"]["data"], dates_result)
        self.datas["ctl_index_time_sp2"]["data"] = np.append(self.datas["ctl_index_time_sp2"]["data"], index_time_final)
        
    def read_data(self):
        abstract_reader.Reader.read_data(self) 
        return True

    def help_config(self):
        """
            Donne de l'aide sur la structure du fichier de config.
        """
        str_help = "\n\nLe reader {} n'utilise pas de fichier de configuration\n".format(self.reader_type)
        
        return str_help
