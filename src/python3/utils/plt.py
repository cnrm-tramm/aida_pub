#!/usr/bin/env python3


"""
Utilitaire autour des noms et abreviations de platefomres 

  usage :
    {me} <chaine>

    <chaine> peut-être :
    - une abreviation existante (2 caractères)
    - tout ou partie (3 caracères minimum) d'une nom de plateforme.

  exemple :
    {me} charbonniere : retourne : charbonniere                ch
    {me} cha          : retourne : charbonniere                ch
    {me} ch           : retourne : charbonniere
"""

import os
import sys

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
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

    what = sys.argv[1]

    AIDA.ini_plt_indexes()
    if len(AIDA.plt_by_name) == 0:
        print(f"Le fichier de définition des plate-formes est vide.")
        sys.exit(1)

    lon_max = max( [ len(name) for name in AIDA.plt_by_name ] )

    if len(what) == 2:
        if what in AIDA.plt_by_abrev:
            print(f"{AIDA.plt_by_abrev[what].nom:{lon_max}s} {AIDA.plt_by_abrev[what].abrev}")
    else:
        for pltf in AIDA.plt_by_abrev.values():
            if what in pltf.nom:
                print(f"{pltf.nom:{lon_max}s} {pltf.abrev}")

    #print(f"AIDA.plt_by_abrev : {AIDA.plt_by_abrev.keys()}")
