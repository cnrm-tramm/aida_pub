#!/usr/bin/env python3


"""
Utilitaire de gestion des environnements de travail de AIDA.

  usage :
    {me} -l     : renvoie la liste des noms des environnements de travail
                  définis dans le fichier ~/.config/AIDA_env/AIDA_env.ini.
    {me} <nom>  : renvoie une chaine contenant toutes les variables définies
                  pour l'environnement de travail <nom>, séparées par des ','.

  exemple :
    {me} -l
    {me} OPERATIONNEL

Ce script a pour vocation d'être appelé par le script shell : 'aida_env.sh'.
"""

import os
import sys

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA_env
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

    # récupération de la liste des environnements
    if sys.argv[1] == '-l':
        try:
            env = AIDA_env.AIDA_env()
            print(' '.join(env.get_env_list()))
        except:
            sys.exit(1)
    # récupération des variables d'un environnement
    else:
        try:
            env = AIDA_env.AIDA_env()
            print(env.get_env_vars(sys.argv[1]))
        except:
            sys.exit(1)

    sys.exit(0)
