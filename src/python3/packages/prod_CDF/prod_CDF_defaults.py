#!/usr/bin/env python3

"""
Production de fichier NetCDF à partir de fichiers-vecteurs
==========================================================

  Gestion du fichier de configuration par défaut.
"""

import sys
import os
import logging
import configparser

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

logger = logging.getLogger('prod_CDF')


class Defaults:
    """ Gestion du fichier de configuration par défaut.
    """

    def __init__(self):
        """
        """
        logger.log(logging.RUN, "Defaults::__init__")

        self.general = dict()

        AH = os.getenv('AIDA_HOME')
        AP = os.getenv('AIDA_PROFIL')
        self.filename = os.path.join (AH, 'profils', AP, 'CDF.defaults')

        if not os.path.isfile(self.filename):
            logger.warning(f"le fichier '{self.filename}' n'existe pas")
            return

        # récupérer les info de la section '[GENERAL]'
        parser = configparser.ConfigParser(interpolation=None)
        # obliger configparser a ne pas modifier la case des options
        parser.optionxform = str

        parser.read(self.filename)

        section = 'GENERAL'
        if not section in parser.sections():
            raise Exception (f"Defaults::__init__ : '{self.filename}' : " +\
                             f"pas de section '{section}'")

        self.general = dict(parser.items(section))


    def show_me(self):
        """ Debug
        """
        print( "Defaults.default :")
        for key, value in self.general.items():
            print(f"- {key} = {value}")

        return
