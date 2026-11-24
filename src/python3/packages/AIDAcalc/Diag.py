#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Gestion des diagnostiques de retour des opérateurs Python pour ADC.
"""

import sys
import os
import logging


logger = logging.getLogger('adc')


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

import ADC_error

# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


class Diag:
    """ Gestion des diagnostiques de retour des opérateurs Python.
    """
    def __init__(self, **kwargs):
        """
            :param dict kwargs: dictionnaire de sortie des fonctins de calcul.

            kwargs *doit* contenir :
                - une clé 'CodeRet'
                - une clé 'DiagExec'
            Raise une exception, si le diagnostique contient des clés
            non traitées.
        """
        if not 'CodeRet' in kwargs:
            raise Exception ("diagnostique sans clé 'CodeRet'")

        if not 'DiagExec' in kwargs:
            raise Exception ("diagnostique sans clé 'DiagExec'")

        self.CodeRet  = kwargs.get('CodeRet')
        self.DiagExec = kwargs.get('DiagExec')

        del kwargs['CodeRet']
        del kwargs['DiagExec']

        if kwargs:
            ADC_error.critical( "DEV : Diag::__init__ : le diagnostique de " +\
                                "retour contient des clés non-traitées : " +\
                               f"{kwargs}", stop=True)


    def show_me(self):
        """ Debug...
        """
        max_len = max( (len(key) for key in self.__dict__.keys()) )

        for key, value in self.__dict__.items():
            print(f'    - {key:{max_len}s}   = {value}')


if __name__ == '__main__':

    from fct_messages import wait_user


    os.system('clear')

    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')

    msg    = "test_Diag : ceci est le message de diagnostiue"
    P_header = {}
    P_header['unit']     = 'mhg'
    P_header['ref_time'] = 'ref_time_1'

    diag_out = {'CodeRet' : 0,
                'DiagExec': f"{msg}",
                'Headers' : P_header, # dict
    }

    print(f"\n\n==== TEST N° 1 : diag_out = {diag_out}")
    try:
        diag = Diag(**diag_out)
        diag.show_me()
    except Exception as e:
        logger.critical(e)
    wait_user()



    diag_out = {'CodeRet' : 0,
                'DiagExec': f"{msg}",
                'Headers' : [P_header], # list
    }

    print(f"\n\n==== TEST N° 2 : diag_out = {diag_out}")
    try:
        diag = Diag(**diag_out)
        diag.show_me()
    except Exception as e:
        logger.critical(e)
    wait_user()


    P2_header = {}
    P2_header['unit'] = 'Km/h'
    diag_out = {'CodeRet' : 0,
                'DiagExec': f"{msg}",
                'Headers' : [P_header, P2_header],
    }

    print(f"\n\n==== TEST N° 3 : diag_out = {diag_out}")
    try:
        diag = Diag(**diag_out)
        diag.show_me()
    except Exception as e:
        logger.critical(e)
    wait_user()


    diag_out = {
                'DiagExec': f"{msg}",
    }

    print(f"\n\n==== TEST N° 4 : diag_out = {diag_out}")
    try:
        diag = Diag(**diag_out)
        diag.show_me()
    except Exception as e:
        logger.critical(e)
    wait_user()


    diag_out = {'CodeRet' : 0,
    }

    print(f"\n\n==== TEST N° 5 : diag_out = {diag_out}")
    try:
        diag = Diag(**diag_out)
        diag.show_me()
    except Exception as e:
        logger.critical(e)
    wait_user()


    diag_out = {'CodeRet' : 0,
                'DiagExec': f"{msg}",
    }

    print(f"\n\n==== TEST N° 6 : diag_out = {diag_out}")
    try:
        diag = Diag(**diag_out)
        diag.show_me()
    except Exception as e:
        logger.critical(e)
    wait_user()
