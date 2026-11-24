#!/usr/bin/env python3


"""
Affiche la différence entre 2 listes compactes d'acqids passées en argument
(voir format fichier .camp)

  usage :
    {me} "liste_compacte_a" "liste_compacte_b"

    Chacune des 2 listes doit être donnée entre "".

  exemple :
    {me} "Ho150281-Ho170115" "Ho150281-Ho160305, Ho160308-Ho160327, Ho160329-Ho170115"
"""

import os
import sys
#import getopt
#import re
#import configparser
#from datetime import datetime

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

#import AIDA
from Camp import expand_acqids_pltf
from fct_messages import (info, warning, stop_error, result, wait_user)


# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


def usage():
    """ Affiche l'usage.
    """
    print(__doc__.format(me=me))
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()

    string_1 = ''.join(sys.argv[1])
    string_2 = ''.join(sys.argv[2])

    acqids_1 = expand_acqids_pltf(string_1)
    acqids_2 = expand_acqids_pltf(string_2)
    diffs    = list ( set(acqids_1) - set(acqids_2) )

    for acqid in diffs:
        print(acqid)
