#!/usr/bin/env python3

"""
Remplacement simple de vivect.sh
    Dump en ASCII d'un vecteur.

    Sans option : le résultat du dump est enregistré dans le fichier 
    /tmp/$USER_<param>.asc puis ce fichier est visualisé sous `vi`.

    Avec l'option '-', le résultat du dump est listé à l'écran.

    NOTE : le script ancestral vivect.sh utilisait le programme vec2asc qui ne
           sait pas traiter les vecteurs de format string32.

  usage :
    {me} [-] <acqid> <paramtetre>

  avec :
    -s : le résultat du dump est listé à l'écran.

  exemple :
    {me}   P2240008 ctl_mode_cal_200
    {me} - P2240008 ctl_mode_cal_200
"""

import os
import sys

import argparse
import numpy     as np
import pandas    as pd

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
    #if len(sys.argv) != 3:
    #    usage()

    # parsing de la ligne de commande
    description = "Affichage d'un vecteur en ASCII."
    epilog      = "Remplace le script ancestral vivect.sh."

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('-','--',
                        dest='to_screen',
                        required=False,
                        action='store_true',
                        default=False,
                        help="le résultat du dump est listé à l'écran.")

    parser.add_argument('acqid',
                        help='acqid du paramètre')

    parser.add_argument('vecteur',
                        help='nom du vecteur (avec ou sans extension)')

    args = parser.parse_args()

    # récupération des arguments
    to_screen = args.to_screen
    acqid     = args.acqid
    vecteur   = args.vecteur
    # DBG info(f"acqid     = {acqid}")
    # DBG info(f"vecteur   = {vecteur}")
    # DBG info(f"to_screen = {to_screen}")

    # récupération du nom du paramètre
    param, _ = os.path.splitext(os.path.basename(vecteur))
    # DBG info(f"param   = {param}")

    # lecture du vecteur et de son temps assoicié
    try:
        data, times, header = AIDA.read_data(acqid, param, header_utf_8=True)
    except Exception as e:
        stop_error(f"problème de lecture du fichier '{param}' : {e}")

    if not header:
        stop_error(f"problème de lecture du fichier '{param}'")

    # calcul la longueur max de key du header
    lenght_max = max([len(k) for k in header.keys() ])


    # mise en fichier temporaire
    out_file = None
    if not to_screen:
        out_file = os.path.join(os.sep, 'tmp', f"{os.getenv('USER')}_{param}.asc")
        # DBG info(f"out_file = {out_file}")

        # 'reopen' de stdout sur out_file
        sys.stdout = open(out_file, 'w')


    # information sur le vecteur
    ###print(f"Nombre de valeurs : {len(data)}", file=sys.stderr)
    print(f"Nombre de valeurs : {len(data)} \n\n")

    # afficher proprement le header
    for k,v in header.items():
        print(f"{k:{lenght_max}s} : {v}")

    # afficher les data
    for t, d in zip(times, data):
        print(f"{t} : {d}")

    # fermeture de stdout
    sys.stdout.close()


    # ouvrir le fichier si l'option -f a été fournié
    if not to_screen:
        os.system(f"xterm -e vi {out_file}")


    # fin 'attention, stdout est fermé)
    if out_file:
        os.remove(out_file)
    ###print("...bye", file=sys.stderr)


    sys.exit(0)
