#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Gestion des erreurs...
"""

import sys
import os
import logging

logger = logging.getLogger('adc')


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

from ADC_rapport import ADC_Rapport as Rapport


def critical(adc_msg, stop=True, aida_msg=None):
    """ Gestion d'une erreur critique.
    """
    logger.critical(adc_msg)

    if aida_msg:
        logger.log(logging.AIDA, aida_msg)

    Rapport.add('erreur(s) critique(s)', adc_msg)

    if stop:
        sys.exit(1)

