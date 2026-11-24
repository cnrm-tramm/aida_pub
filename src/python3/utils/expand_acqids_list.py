#!/usr/bin/env python3


"""
Affiche la liste exhaustive des acqids correspondants à la liste compacte
d'acqids passée en argument
(voir format fichier .camp)

  usage :
    {me} "<liste_compacte>"

    La liste doit être donnée entre "".

  exemple :
    {me} "Ho150281-Ho160305, Ho160308-Ho160327, Ho160329-Ho170115"
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
    if len(sys.argv) != 2:
        usage()

    string_1 = ''.join(sys.argv[1])
    for acqid in expand_acqids_pltf(string_1):
        print(acqid)
