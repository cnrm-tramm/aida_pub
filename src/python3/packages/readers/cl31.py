#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from readers import csv_like
import configparser
import sys
import re
import numpy as np
from readers.abstract_reader import ReaderError
from readers import abstract_reader
import numpy as np
import datetime as dt
import sys
import math
import re
import logging
import tarfile
import pandas as pd
import argparse


class Reader(abstract_reader.Reader) :

    reader_type = "cl31"
    ERR_HEX_MSG = [
    {'hex': 0x000000000001, 'level': 'STATUS', 'msg': 'undefined'},
    {'hex': 0x000000000002, 'level': 'STATUS', 'msg': 'undefined'},
    {'hex': 0x000000000004, 'level': 'STATUS', 'msg': 'undefined'},
    {'hex': 0x000000000008, 'level': 'STATUS', 'msg': 'undefined'},
    {'hex': 0x000000000010, 'level': 'STATUS', 'msg': 'undefined'},
    {'hex': 0x000000000020, 'level': 'STATUS', 'msg': 'Polling mode is on'},
    {'hex': 0x000000000040, 'level': 'STATUS', 'msg': 'Manual blower control'},
    {'hex': 0x000000000080, 'level': 'STATUS', 'msg': 'Units are meters if on, else feet'},
    {'hex': 0x000000000100, 'level': 'STATUS', 'msg': 'undefined'},
    {'hex': 0x000000000200, 'level': 'STATUS', 'msg': 'Manual data acquisition settings are effective'},
    {'hex': 0x000000000400, 'level': 'STATUS', 'msg': 'Self test in progress'},
    {'hex': 0x000000000800, 'level': 'STATUS', 'msg': 'Standby mode is on'},
    {'hex': 0x000000001000, 'level': 'STATUS', 'msg': 'Working from battery'},
    {'hex': 0x000000002000, 'level': 'STATUS', 'msg': 'Internal heater is on'},
    {'hex': 0x000000004000, 'level': 'STATUS', 'msg': 'Blower heater is on'},
    {'hex': 0x000000008000, 'level': 'STATUS', 'msg': 'Blower is on'},
    {'hex': 0x000000010000, 'level': 'WARNING', 'msg': 'undefined'},
    {'hex': 0x000000020000, 'level': 'WARNING', 'msg': 'Tilt angle > 45 degrees warning'},
    {'hex': 0x000000040000, 'level': 'WARNING', 'msg': 'Receiver warning'},
    {'hex': 0x000000080000, 'level': 'WARNING', 'msg': 'Laser monitor failure'},
    {'hex': 0x000000100000, 'level': 'WARNING', 'msg': 'Battery failure'},
    {'hex': 0x000000200000, 'level': 'WARNING', 'msg': 'Ceilometer engine board failure'},
    {'hex': 0x000000400000, 'level': 'WARNING', 'msg': 'High background radiance'},
    {'hex': 0x000000800000, 'level': 'WARNING', 'msg': 'Heater fault'},
    {'hex': 0x000001000000, 'level': 'WARNING', 'msg': 'Humidity sensor failure'},
    {'hex': 0x000002000000, 'level': 'WARNING', 'msg': 'undefined'},
    {'hex': 0x000004000000, 'level': 'WARNING', 'msg': 'Blower failure'},
    {'hex': 0x000008000000, 'level': 'WARNING', 'msg': 'undefined'},
    {'hex': 0x000010000000, 'level': 'WARNING', 'msg': 'High humidity'},
    {'hex': 0x000020000000, 'level': 'WARNING', 'msg': 'Transmitter expires'},
    {'hex': 0x000040000000, 'level': 'WARNING', 'msg': 'Battery voltage low'},
    {'hex': 0x000080000000, 'level': 'WARNING', 'msg': 'Window contamination'},
    {'hex': 0x000100000000, 'level': 'ALARM', 'msg': 'Ceilometer engine board failure'},
    {'hex': 0x000200000000, 'level': 'ALARM', 'msg': 'Coaxial cable failure'},
    {'hex': 0x000400000000, 'level': 'ALARM', 'msg': 'undefined'},
    {'hex': 0x000800000000, 'level': 'ALARM', 'msg': 'undefined'},
    {'hex': 0x001000000000, 'level': 'ALARM', 'msg': 'undefined'},
    {'hex': 0x002000000000, 'level': 'ALARM', 'msg': 'undefined'},
    {'hex': 0x004000000000, 'level': 'ALARM', 'msg': 'undefined'},
    {'hex': 0x008000000000, 'level': 'ALARM', 'msg': 'undefined'},
    {'hex': 0x010000000000, 'level': 'ALARM', 'msg': 'Receiver saturation'},
    {'hex': 0x020000000000, 'level': 'ALARM', 'msg': 'Light path obstruction'},
    {'hex': 0x040000000000, 'level': 'ALARM', 'msg': 'Memory error'},
    {'hex': 0x080000000000, 'level': 'ALARM', 'msg': 'undefined'},
    {'hex': 0x100000000000, 'level': 'ALARM', 'msg': 'Voltage failure'},
    {'hex': 0x200000000000, 'level': 'ALARM', 'msg': 'Receiver failure'},
    {'hex': 0x400000000000, 'level': 'ALARM', 'msg': 'Transmitter failure'},
    {'hex': 0x800000000000, 'level': 'ALARM', 'msg': 'Transmitter shut-off'}]
    RCS_BYTES_SIZE = 5
    RCS_FACTOR = 1e-8
    DEG_TO_K = 273.15
    FEET_TO_METERS = 0.3048
    CLH_ALT_METERS_FACTOR = 10.
    CLH_ALT_FEET_FACTOR = 100.
    SUM_BCKSCATTER_FACTOR = 1.E-4
    OK_SCALE_VALUE = 100.
    FMT_DATE = "-%Y-%m-%d %H:%M:%S"
    FILE_HEADER = ["-Ceilometer Logfile", "-File created:"]
    STAT_MSG_LINE = { 1: 3, 2: 4 }
    RCS_MSG_LINE = { 1: 4, 2: 5 }
    CONF_MSG_REGEX = r'CL.\d{5}'
    MSG_NB_LINES =  {1: 6, 2: 7}
    RANGE_RESOL = { 1: 10, 2: 20, 3: 5, 4: 5, 5: -9, 6: 10, 8: -9 }
    RANGE_GATES = { 1: 770, 2: 385, 3: 1500, 4: 770, 5: -9, 6: 1540, 8: -9 }
    CBH_DIM = 3
    CLH_DIM = 5


    def __init__(self, source, config_file=None, logger=None, start=None, end=None, keep_normal=False, no_checksum=False) :
        """
            Appelle le constructeur de la classe parente puis positionne ses attributs.
        """
        abstract_reader.Reader.__init__(self, source, config_file, logger, start, end, keep_normal, no_checksum)
        self.file = source # stocke les fichiers
        self.data = {}
        self.data_dim = {}
        self.list_errors = {}
        self.conf = {
            'check_scale' : 'False',
            'time_resolution' : np.array(30),
            'missing_int' : np.nan,
            'missing_float' : np.nan}
        self.cfg_name = {}
        self.cfg_english_name = {}
        self.cfg_units = {}
        self.cfg_ignore = {}
        self.var_name = {}


    def read_config(self) :
        """
            Lecture du fichier de configuration.
            
            La structure du fichier de configuration est définie dans le dictionnaire def_config.
            Le résultat de la lecture est une structure de type ConfigParser stockée dans self.config
            
            :return: retourne une structure contenant la config.
            :rtype: ConfigParser
        
        """
        # Lecture du fichier de config
        config_data = np.loadtxt(self.config_file,delimiter = ",", skiprows = 1,dtype = str)
        for i in range(config_data.shape[0]) :
            self.var_name[config_data[i][0]] = config_data[i][1]
            self.cfg_name[config_data[i][0]] = config_data[i][2]
            self.cfg_english_name[config_data[i][0]] = config_data[i][3]
            self.cfg_units[config_data[i][0]] = config_data[i][4]
            self.cfg_ignore[config_data[i][0]] = config_data[i][5]

    def get_error_index(self,err_msg):
        """
        based on error error message read in file. return all indexes of related msg and level
        """

        err_ind = []
        err_int = int(err_msg, 16)
        for i, d in enumerate(self.ERR_HEX_MSG):
            if bool(err_int & d['hex']):
                err_ind.append(i)

        return err_ind


    def store_error(self, err_msg):
        """store errors msg and their count by type"""

        err_ind = Reader.get_error_index(self,err_msg)

        for i in err_ind:

            if self.ERR_HEX_MSG[i]['msg'] in self.list_errors:
                self.list_errors[self.ERR_HEX_MSG[i]['msg']]['count'] += 1
            else:
                self.list_errors[self.ERR_HEX_MSG[i]['msg']] = {}
                self.list_errors[self.ERR_HEX_MSG[i]['msg']]['count'] = 1
                self.list_errors[self.ERR_HEX_MSG[i]['msg']]['level'] = self.ERR_HEX_MSG[i]['level']

        return self.data


    def log_error_msg(self):

        msg_format = '{} : {:d} message(s)'

        # if len(self.list_errors) > 0:
        #     self.logger.info('summary of instruments messages')

        # for msg in self.list_errors:

        #     if self.list_errors[msg]['level'] == 'STATUS':
        #         self.logger.info(msg_format.format(msg, self.list_errors[msg]['count']))
        #     elif self.list_errors[msg]['level'] == 'WARNING':
        #         self.logger.warning(msg_format.format(msg, self.list_errors[msg]['count']))
        #     elif self.list_errors[msg]['level'] == 'ALARM':
        #         self.logger.error(msg_format.format(msg, self.list_errors[msg]['count']))


    def are_units_meters(self,err_msg):
        """
        based on status message, determine what are the units of CLH and CBH
        """

        err_ind = Reader.get_error_index(self,err_msg)

        for i in err_ind:
            if self.ERR_HEX_MSG[i]['msg'] == 'Units are meters if on, else feet':
                self.logger.debug("units are in meters")
                return True

        self.logger.debug("units are in feet")

        return False


    def get_conversion_coeff(self, are_units_meters):
        """
        based on the status message return the coefficient to convert feet to meters
        """
        

        coeff = 1.
        if not are_units_meters:
            coeff = self.FEET_TO_METERS

        return coeff


    def check_scale_value(self, the_file, ind):
        """
        check scale value. If value is not 100%, message is voided.
        """

        msg = "101 Instrument Calibration Issues in '{}'. "
        msg += "Values for {:%Y-%m-%d %H:%M:%S} will be replaced by missing value"

        if self.data['scale'][ind] != self.OK_SCALE_VALUE:
            self.logger.warning(msg.format(the_file, self.data['rft_time_cl31'][ind]))

            if self.conf['check_scale']:
                self.data['rcs_0'][ind, :] = self.conf['missing_float']
                self.data['pr2'][ind, :] = self.conf['missing_float']


    def get_file_lines(self,the_file):
        """
        read all lines of a given file and remove carriage return from
        all lines
        """
        lignes = []
        try:
            with open(the_file, 'rb') as f_id:
                self.logger.debug("reading " + the_file)
                lines = f_id.readlines()
                for l in lines :
                    lignes.append(l.rstrip().decode('utf-8'))
        except:
            self.logger.error("109 Impossible to open file " + the_file)
            return None

        return lignes


    def count_msg_to_read(self,the_file):
        """
        to a first reading of the CL31 file to determine the number
        of data messages which need to be read
        """

        n_data_msg = 0

        # read to count the number of messages
        # data message start with a date using the format "-%Y-%m-%d %H:%M:%S"
        lines = Reader.get_file_lines(self,the_file)

        for line in lines :
            try:
                dt.datetime.strptime(line, self.FMT_DATE)
                n_data_msg += 1
            except :
                continue
        # self.logger.info("%d data messages to read" % n_data_msg)

        return n_data_msg


    def get_conf_msg(self,line):
        """
        Extract conf message
        """

        conf_str = re.search(self.CONF_MSG_REGEX, line)
        if conf_str is not None:
            conf_msg = conf_str.group()
            self.logger.debug("conf message %s" % conf_msg)
        else:
            conf_msg = None

        return conf_msg


    def get_range_resol(self,conf_msg):
        """
        Extract vertical range resolution from configuration message line
        """
        try:
            int_coding = int(conf_msg[7:8])
            range_resol = self.RANGE_RESOL[int_coding]
            self.logger.debug("range resolution: %d m" % range_resol)
        except Exception as err:
            self.logger.warning("105 Problem reading range resolution: " + repr(err))
            return None

        return np.array(range_resol)


    def get_range_ngates(self,conf_msg):
        """
        Extract the number of gates from configuration message line
        """

        try:
            int_coding = int(conf_msg[7:8])
            range_ngates = self.RANGE_GATES[int_coding]
            # self.logger.debug("number of vertical gates: %d" % range_ngates)
        except Exception as err:
            # self.logger.warning("105 Problem reading number of vertical gates " +
                        # repr(err))
            return None

        return range_ngates


    def get_msg_type(self,conf_msg):
        """
        Extract from acquisition configuration line if the file contains
        message of type 1 or 2 (without or with sky state)
        """

        msg_type = int(conf_msg[6:7])

        if msg_type == 1:
            # self.logger.info("file contains messages of type 1 (without sky state)")
            msg_type = int(conf_msg[6:7])
        elif msg_type == 2:
            # self.logger.info("file contains messages of type 2 (with sky state)")
            msg_type = int(conf_msg[6:7])
        else:
            self.logger.error("106 problem determining type of message '{}'")
            msg_type = np.nan

        return np.array(msg_type)


    def get_msg_nb_lines(self,msg_number):
        """
        based ont the configuration read return the number of lines of a data
        message
        """

        return self.MSG_NB_LINES[int(msg_number)]


    def calc_range(resol, n_gates):
        """
        calculate range variable based on resolution and number of gates
        """

        range_vect = np.array(list(range(1, n_gates + 1)), dtype=np.float)

        return range_vect * np.float(resol)


    def check_range(self,the_file):
        """
        check we determining range was a success
        """

        # Test if the msg contains retrodiffusion profiles
        if self.data_dim['range'] == -9 or self.data['range_resol'] == -9:
            self.logger.error("101 according to the configuration read " +
                        "the file {} doesn't contains retrodiffusion ".format(the_file) +
                        "profiles. Trying next message")
            range_ok = False
            # Test if we manage to read resol anf number of gates
        elif self.data_dim['range'] is None or self.data['range_resol'] is None:
            self.logger.error("101 problem encountered reading range configuration." +
                        " from {} Trying next message".format(the_file))
            range_ok = False
        else:
            range_ok = True

        return range_ok


    def check_msg_type(self):
        """
        check if determining message type was a success
        """

        # test if message type could be determine
        if np.isnan(self.data['msg_type']) :
            msg_ok = False
            self.logger.error("Could not determine type of message in file")
        else:
            msg_ok = True

        return msg_ok, self.data


    def get_acq_conf(self, the_file):
        """
        extract acquisition configuration from a data message
        (range resolution and number of vertical gates)
        """

        lines = Reader.get_file_lines(self,the_file)
        n_lines = len(lines)
        i_line = 0
        range_ok = False
        msg_ok = False

        self.logger.debug(n_lines)

        conf_msg = None
        while i_line <= n_lines:
            try:
                dt.datetime.strptime(lines[i_line], self.FMT_DATE)
            except:

                conf_msg = None
                i_line += 1
                continue

            conf_msg = Reader.get_conf_msg(self,lines[i_line + 1])
            if conf_msg is None:
                continue

            self.data_dim['range'] = Reader.get_range_ngates(self,conf_msg)
            self.data['range_resol'] = Reader.get_range_resol(self,conf_msg)

            # check if reading of range was a success
            
            range_ok = Reader.check_range(self,the_file)
            if range_ok:
                self.data['range'] = Reader.calc_range(self.data['range_resol'], self.data_dim['range'])

            # Check if reading of message type is a success
            self.data['msg_type'] = Reader.get_msg_type(self, conf_msg)
            msg_ok, self.data = Reader.check_msg_type(self)
   

            if range_ok and msg_ok:
                break

        # if we are not able to read range in the file
        if not range_ok:
            self.logger.critical("107 Impossible to read range configuration in '" +
                            the_file + "'. Stopping Raw2L1")
        if not msg_ok:
            self.logger.critical("106 impossible to determine type of message in '" +
                            the_file + "'. Stopping Raw2L1")

        if not range_ok or not msg_ok:
            sys.exit(1)

        # Read instrument/sofware id
        self.data['instrument_id'] = np.array(conf_msg[0:3])
        self.data['software_id'] = np.array(conf_msg[3:6])

        return self.data, self.data_dim


    def init_data(self):
        """
        declare size of the numpy arraies and initialiase it
        """

        # get missing values
        missing_int = self.conf['missing_int']
        missing_float = self.conf['missing_float']

        # Dimension variables
        # -------------------------------------------------------------------------
        self.data['rft_time_cl31'] = np.ones((self.data_dim['rft_time_cl31'],),
                            dtype=np.dtype(dt.datetime)) * np.nan
        self.data['cbh_layer'] = np.array([x + 1 for x in range(self.CBH_DIM)])
        self.data['clh_layer'] = np.array([x + 1 for x in range(self.CLH_DIM)])

        # Time dependant variables
        # -------------------------------------------------------------------------
        self.data['scale'] = np.ones((self.data_dim['rft_time_cl31'],),
                                dtype=np.float32) * missing_float
        self.data['laser_temp'] = np.ones((self.data_dim['rft_time_cl31'],),
                                    dtype=np.float32) * missing_float
        self.data['laser_energy'] = np.ones((self.data_dim['rft_time_cl31'],),
                                    dtype=np.float32) * missing_float
        self.data['bckgrd_rcs_0'] = np.ones((self.data_dim['rft_time_cl31'],),
                                    dtype=np.float32) * missing_float
        self.data['window_transmission'] = np.ones((self.data_dim['rft_time_cl31'],),
                                            dtype=np.float32) * missing_float
        self.data['tilt_angle'] = np.ones((self.data_dim['rft_time_cl31'],),
                                    dtype=np.float32) * missing_float
        self.data['integrated_rcs_0'] = np.ones((self.data_dim['rft_time_cl31'],),
                                        dtype=np.float32) * missing_float
        self.data['vertical_visibility'] = np.ones((self.data_dim['rft_time_cl31'],),
                                            dtype=np.int32) * missing_int
        self.data['alarm'] = np.ndarray((self.data_dim['rft_time_cl31'],), dtype='S1')
        self.data['info_flags'] = np.ndarray((self.data_dim['rft_time_cl31'],), dtype='S12')

        # Time, layer dependant variables
        # -------------------------------------------------------------------------
        self.data['cbh'] = np.ones((self.data_dim['rft_time_cl31'], self.CBH_DIM),
                            dtype=np.int32) * missing_int
        self.data['clh'] = np.ones((self.data_dim['rft_time_cl31'], self.CLH_DIM),
                            dtype=np.int32) * missing_int
        self.data['cloud_amount'] = np.ones((self.data_dim['rft_time_cl31'], self.CLH_DIM),
                                    dtype=np.int16) * missing_int

        # Time, range dependent variables
        # -------------------------------------------------------------------------
        self.data['rcs_0'] = np.ones((self.data_dim['rft_time_cl31'], self.data_dim['range']),
                                dtype=np.float32) * missing_float
        self.data['pr2'] = np.ones((self.data_dim['rft_time_cl31'], self.data_dim['range']),
                            dtype=np.float32) * missing_float

        # Special variable to store for each message the unit of CBH and CLH
        # -------------------------------------------------------------------------
        self.data['are_unit_meter'] = np.ones((self.data_dim['rft_time_cl31'],),
                                        dtype=bool)

        return self.data


    def get_state_line_nb_in_msg(self,msg_type):
        """
        based on the configuration of the message type return the
        line number in data message containing ceilometer state
        """

        return self.STAT_MSG_LINE[int(msg_type)]


    def get_rcs_line_nb_in_msg(self,msg_type):
        """
        based on the configuration of the message type return the
        line number in data message containing ceilometer state
        """

        return self.RCS_MSG_LINE[int(msg_type)]

    def format_bornes(list_bornes) :
        """
        arrange the format of bounds for vectorisation
        list_bornes : list of bounds
        """
        bounds = "("
        for i in list_bornes :
            bounds = bounds + str(int(i)) + "," + str(int(i)) + ");("

        return bounds[:-2]


    def read_scalar_vars(self,msg):
        """
        extract scalar variables from data message
        """

        line_to_read = Reader.get_state_line_nb_in_msg(self,self.data['msg_type'])
        line = msg[line_to_read]

        return np.float(line.split()[6])


    def read_time_dep_vars(self,ind, msg):
        """
        read time only dependent variables
        ex: 00100 10 0770 098 +34 099 12 621 L0112HN15 139↵
        """

        line_to_read = Reader.get_state_line_nb_in_msg(self,self.data['msg_type'])
        params = msg[line_to_read].split()

        self.data['scale'][ind] = np.float(params[0])
        self.data['laser_energy'][ind] = np.float(params[3])
        self.data['laser_temp'][ind] = np.float(params[4]) + self.DEG_TO_K
        self.data['window_transmission'][ind] = np.float(params[5])
        self.data['tilt_angle'][ind] = np.float(params[6])
        self.data['bckgrd_rcs_0'][ind] = np.float(params[7])
        self.data['integrated_rcs_0'][ind] = np.float(params[9]) * self.SUM_BCKSCATTER_FACTOR

        return self.data


    def read_cbh_msg(self, ind, msg):
        """
        extract CBH
        ex: 30 01230 12340 23450 FEDCBA987654↵
        """

        elts = msg[2].split()

        # get the number of cloud layer
        if elts[0][0] == '/':
            self.logger.warning("105 cloud data missing for message %d" % ind)
            return self.data
        else:
            nlayers = int(elts[0][0])

        self.data['alarm'][ind] = elts[0][1]

        # flags
        self.data['info_flags'][ind] = elts[4]
        # get unit of CBH
        self.data['are_unit_meter'][ind] = Reader.are_units_meters(self,elts[4])

        coeff = Reader.get_conversion_coeff(self,self.data['are_unit_meter'][ind])

        self.data = Reader.store_error(self,elts[4])

        # number of CBH depends on nlayers value
        if 1 <= nlayers < 4:
            self.data['cbh'][ind, 0] = np.float(elts[1]) * coeff
        if 2 <= nlayers < 4:
            self.data['cbh'][ind, 1] = np.float(elts[2]) * coeff
        if 3 <= nlayers < 4:
            self.data['cbh'][ind, 2] = np.float(elts[3]) * coeff

        return self.data


    def read_clh_msg(self, ind, msg):
        """
        extract CLH, cloud amount and visibility
        """

        # split lines to get each elements
        # even elements are cloud amount
        # odd elements are CLH
        line = msg[3]
        elts = line.strip().split()
        octas = [int(octa) for octa in elts[0::2]]
        clh_str = elts[1::2]

        # depending on configuration a different factor need to be applied
        # if value are in meters or feets
        coeff = Reader.get_conversion_coeff(self,self.data['are_unit_meter'][ind])
        if self.data['are_unit_meter'][ind]:
            coeff = coeff * self.CLH_ALT_METERS_FACTOR
        else:
            coeff = coeff * self.CLH_ALT_FEET_FACTOR

        # get cloud amount
        for level, octa in enumerate(octas):
            if 1 <= octa <= 8:
                self.data['cloud_amount'][ind, level] = np.int(octa)
                self.data['clh'][ind, level] = float(clh_str[level]) * coeff
            elif octa == 0:
                self.data['cloud_amount'][ind, level] = np.int(octa)
            elif octa == 9:
                self.data['vertical_visibility'][ind] = float(clh_str[level])

        return self.data


    def read_cbh_vars(self, ind, msg):
        """
        Read the altitude of the 3 cloud layer in a data message
        """

        # reading of CBH depends on the kind of data message type
        self.data = Reader.read_cbh_msg(self, ind, msg)
        if self.data['msg_type'] == np.array(2):
            self.data = Reader.read_clh_msg(self, ind, msg)

        return self.data


    def read_rcs_var(self, ind, msg):
        """
        read the rcs value in a data msg
        """

        # get line a of the message containing RCS based on CL31 conf
        line_to_read = Reader.get_rcs_line_nb_in_msg(self,self.data['msg_type'])
        # size of the profile to read
        rcs_size = self.data['range'].size
        # extract line containing rcs
        rcs_line = msg[line_to_read]

        try:
            tmp = np.array([int(rcs_line[s * self.RCS_BYTES_SIZE:s * self.RCS_BYTES_SIZE +
                        self.RCS_BYTES_SIZE], 16) for s in range(rcs_size)])
            
            # Each sample is coded with a 20-bit HEX ASCII character set
            # msb nibble and bit first, 2's complement
            corr_2s_needed = (tmp > 2**19)
            if any(corr_2s_needed):
                tmp[corr_2s_needed] = - (2**20 - tmp[corr_2s_needed])

        except ValueError:
            print("Ligne indéchiffrable")
            tmp = np.zeros(rcs_size)*np.nan

        self.data['rcs_0'][ind][:] = np.array(tmp, dtype=np.float32)

        return self.data

    def remove_nan(self) :

        # tmp = np.array(self.data['rft_time_cl31'], dtype = float)
        index_nan = np.where(pd.isnull(self.data['rft_time_cl31']) == True)[0]
        
        for key in list(self.data.keys()):

            if (self.data_dim['rft_time_cl31'] in self.data[key].shape and key != 'rft_time_cl31'):
                self.data[key] = np.delete(self.data[key], index_nan)
            if key in list(self.data_dim.keys()):
                self.data_dim[key] = len(self.data[key])

        self.data['rft_time_cl31'] = np.delete(self.data['rft_time_cl31'], index_nan)

    def read_vars(self,lines, the_file, time_ind):
        """
        read all available variables in one file
        """

        n_lines = len(lines)
        i_line = 0
        msg_n_lines = Reader.get_msg_nb_lines(self,self.data['msg_type'])

        # loop over the lines
        while i_line < n_lines:

            # reject header lines
            if lines[i_line] in self.FILE_HEADER:
                i_line += 1
                continue

            # Try finding line with time stamp
            try:

                self.data['rft_time_cl31'][time_ind] = dt.datetime.strptime(lines[i_line],
                                                            self.FMT_DATE)
            except:
                i_line += 1
                continue

            self.logger.debug('timestamp: {:%Y%m%d %H:%M:%S}'.format(self.data['rft_time_cl31'][time_ind]))


            msg = lines[i_line:i_line + msg_n_lines]
            self.logger.debug("processing data message %d" % (time_ind + 1))

            # check if there is no change in message number
            cur_msg_type = Reader.get_msg_type(self,Reader.get_conf_msg(self,msg[1]))

            if cur_msg_type != self.data['msg_type']:
                i_line += 1
                time_ind += 1
                self.logger.error("100 Incorrect Header Information in '{}'. Message type change in file")
                continue

            # read rcs
            self.logger.debug("reading rcs")
            self.data = Reader.read_rcs_var(self, time_ind, msg)
            # print(self.data['rft_time_cl31'].shape, self.data['rcs_0'].shape)

            # read time only dependent variables
            self.logger.debug("reading time only dependent variables")
            self.data = Reader.read_time_dep_vars(self, time_ind, msg)

            # read CBH
            self.logger.debug("reading cbh/clh")
            self.data = Reader.read_cbh_vars(self, time_ind, msg)

            # check scale value if needed
            Reader.check_scale_value(self, the_file, time_ind)

            # Add number of line of a message to lines counter
            i_line += msg_n_lines
            time_ind += 1
        
        return time_ind, self.data


    def read_file(self, the_file):
        """
        Raw2L1 plugin to read data of the vaisala CL31
        """
       
        # analyse file to read to determine the size of the time variable
        # -------------------------------------------------------------------------

        # self.logger.info("analysing input files to get the configuration")
        self.data_dim['rft_time_cl31'] = Reader.count_msg_to_read(self,the_file)

        # checking conf parameters
        # -------------------------------------------------------------------------
        #try:
        #    conf['check_scale'] = conf['check_scale'].lower()=='true'
        #except (ValueError, KeyError):
        #    conf['check_scale'] = False
        try :
            self.conf['check_scale'] == True
        except :
            self.conf['check_scale'] == False
        try:
            self.conf['time_resol'] = self.conf['time_resolution']
        except KeyError:
            self.logger.error("the time_resolution option in reader_conf is required")
            sys.exit(1)

        # Get range and vertical resolution from first file
        # self.logger.info("analyzing first file to determine acquisition configuration")
        self.data, self.data_dim = Reader.get_acq_conf(self,the_file)

        # self.logger.info("initialising data arrays")
        self.data = Reader.init_data(self)

        # Get names and units from config file
        Reader.read_config(self)
        
        # Reading all the data
        # -------------------------------------------------------------------------
        # self.logger.info("reading files")
        time_ind = 0

        # try reading the file
        lines = Reader.get_file_lines(self,the_file)

        # reading data in the file
        time_ind, self.data = Reader.read_vars(self,lines, the_file, time_ind)

        # add start_time and time resolution variable
        # ------------------------------------------------------------------------
        self.data['time_resolution'] = self.conf['time_resol']

        # Final calculation on whole profiles
        # -------------------------------------------------------------------------
        self.data['pr2'] = self.data['rcs_0'] * self.RCS_FACTOR * self.data['range'] ** 2

        # Summary of instrument message
        # ------------------------------------------------------------------------
        Reader.log_error_msg(self)

        # # If line non readable --> np.nan is set
        # we remove this/these profiles
        if any(math.isnan(x) for x in list(self.data['rft_time_cl31']) if type(x) == float):
            Reader.remove_nan(self)

        # # Write correct data dict
        if self.datas is None :
            self.datas = {}

        try :
            for key in list(self.data.keys()):

                if key == "range" :
                    self.data[key] = np.tile(self.data[key],(self.data["pr2"].shape[0],1))
                # si la variable n'a pas 'time' dans ses dimensions, on ne la traite pas
                if self.data_dim['rft_time_cl31'] not in self.data[key].shape:

                    # self.logger.info(f"La variable {key} ne dépend pas pas du temps, on l'ignore.")
                    continue
                # # si la variable est start_time, ce n'est pas nécessaire de la vectoriser
                # if key == "start_time" :
                #     self.logger.info(f"La variable {key} n'a pas besoin d'être vectorisée")
                #     continue
                
                # lecture des datas et des infos de chaque variable
                infos = {}
                infos["freq_ech"]         = 1/int(self.data["time_resolution"])
                infos["misval"]           = np.nan
                infos["name"]             = self.cfg_name[key]
                infos["english_name"]     = self.cfg_english_name[key]
                infos["unit"]             = self.cfg_units[key]
                infos["bornes"]           = Reader.format_bornes(list(self.data["range"][0]))
                infos["unit_bornes"]      = "m"
                infos["range resolution"] = int(self.data["range_resol"])
                infos["instrument id"]    = str(self.data["instrument_id"])
                infos["software id"]      = str(self.data["software_id"])
                infos["temps"]            = "rft_time_cl31"
                infos["ignore"]           = self.cfg_ignore[key]

                # Special information regarding cbh and clh layers
                if key == 'cbh' :
                    infos["bornes"]       = Reader.format_bornes(list(self.data["cbh_layer"]))
                    infos["unit_bornes"]  = "nb"
                elif key == 'clh' :
                    infos["bornes"]      = Reader.format_bornes(list(self.data["clh_layer"]))
                    infos["unit_bornes"] = "nb"

                
                try :
                    tmp = np.append(self.datas[self.var_name[key]]['data'],self.data[key],axis = 0)
                except :
                    tmp = self.data[key]

                self.datas[self.var_name[key]] = {"data" : tmp, "infos" : infos}
        
        except Exception as e :
            self.logger.critical("Impossible de lire le fichier {}".format(the_file))
            self.logger.critical(e)
            raise(e)