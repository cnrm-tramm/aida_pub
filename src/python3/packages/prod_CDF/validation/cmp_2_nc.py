#!/usr/bin/env python3

"""
Comparaison de 2 fichiers NetCDF (.nc)
======================================

  usage :
    {me} [-h] file1 file2

  avec :
    [-h]   : affichage de l'aide.

    file1  : premier fichier NetCDF
    file2  : second  fichier NetCDF
"""

import sys
import os
import argparse
import re
import netCDF4 as nc

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

from fct_messages import (info, warning, stop_error, result, wait_user)


__version__ = '1.0.0'


missing = '(absent)'

def show_infos(desc, f1, f2):
    """ affiche les informations de démarrage
    """
    for h in [handler1, handler2]:
        if not h:
            continue
        print(desc, file=h)
        print(f"  - file1 : {f1}", file=h)
        print(f"  - file2 : {f2}", file=h)

    return


def show_line(key, v1, v2):
    """ affiche une ligne formatée : "    key | v1 | v2 | "
        ou "    key | v1 | v2 | (type1 | type2)" si les types sont différents
    """
    if v1 == v2:
        return

    # remplacer les \n par des espaces
    if isinstance(v1, str):
        v1 = re.sub('\n', ' ', v1)
    if isinstance(v2, str):
        v2 = re.sub('\n', ' ', v2)
    if v1 == v2:
        # les chaines peuvent être égales après le remplacement
        return

    # si les valeurs sont des longues chaines, présenter 3 caractères avant
    # la première différences
    if isinstance(v1, str) and isinstance(v2, str):
        i = 0
        if min(len(v1), len(v2)) > 35:
            for i in range(0, min(len(v1), len(v2))):
                if v1[i] != v2[i]:
                    if i > 3:
                        i = i-3
                    break
            v1 = '[ ]' + v1[i:]
            v2 = '[ ]' + v2[i:]

    if len(str(v1)) == 0:
        v1 = '(vide)'
    if len(str(v2)) == 0:
        v2 = '(vide)'

    # mémoriser les types (sous une forme courte)
    type1 = str(type(v1)).split("'")[1]
    type2 = str(type(v2)).split("'")[1]

    if type1 != type2:
        if not handler2:
            print(f"    {key:15.15} | " +\
                  f"{str(v1):40.40} | {str(v2):40.40} | " +\
                  f"({type1:15.15} / {type2:15.15})", file=handler1)
        else:
            print(f"    {key:15.15} | {str(v1)} ({type1})", file=handler1)
            print(f"    {key:15.15} | {str(v2)} ({type2})", file=handler2)
    else:
        if not handler2:
            print(f"    {key:15.15} | {str(v1):40.40} | {str(v2):40.40} | ", file=handler1)
        else:
            print(f"    {key:15.15} | {str(v1)}", file=handler1)
            print(f"    {key:15.15} | {str(v2)}", file=handler2)

    return


def show_variable_def(v1, v2):
    """ affiche la définiotn de la variable pour chacun des fichier.
    """
    # '|S1' n'est pas "humainement lisible => remplacer par "char"
    v1 = re.sub('\|S1', 'char', v1)
    v2 = re.sub('\|S1', 'char', v2)

    if v1 == v2:
        if not handler2:
            print(f"\n{v1}", file=handler1)
        else:
            print(f"\n{v1}", file=handler1)
            print(f"\n{v1}", file=handler2)
    else:
        if not handler2:
            print(f"\n{v1:62.62} | {v2}")
        else:
            print(f"\n{v1:62.62}", file=handler1)
            print(f"\n{v2:62.62}", file=handler2)

    return


if __name__ == '__main__':
    # pour rappel : les variables crées sous : "if __name__ == '__main__':"
    # sont globales

    # parsing de la ligne de commande
    description = 'Comparaison de 2 fichiers NetCDF (.nc)'
    epilog      = ''

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('file1',
                        help='chemin du premier fichier NetCDF.')
    parser.add_argument('file2',
                        help='chemin du second fichier NetCDF.')

    parser.add_argument('-m','--meld',  action='store_true',
                        help='visualisation graphique de la comparaison')

    args = parser.parse_args()

    # récupération des arguments
    file1 = args.file1
    file2 = args.file2
    meld  = args.meld


    for f in [file1, file2]:
        if not os.path.isfile(f):
            stop_error(f"le fichier '{f}' n'existe pas")

    if meld:
        handler1 = open('/tmp/cmp_2_nc.file1.txt', 'w')
        handler2 = open('/tmp/cmp_2_nc.file2.txt', 'w')
    else:
        handler1 = sys.stdout
        handler2 = None
    show_infos(description, file1, file2)

    # lecture des fichiers
    ds1 = nc.Dataset(file1)
    ds2 = nc.Dataset(file2)

    # dimensions
    # ----------
    # récupération des dimensions de chaque dataset
    dims1 = ds1.dimensions
    dims2 = ds2.dimensions

    print('\n// dimensions', file=handler1)
    if handler2:
        print('\n// dimensions', file=handler2)
    # dim1 et dim2 ne sont par ordonné de la même façon
    # => on ne peut pas utiliser "zip()
    for key, value1 in dims1.items():
        value2 = dims2.get(key)

        unlimited1 = ''
        unlimited2 = ''
        if key == 'time':
            if dims1[key].isunlimited():
                unlimited1 = '(UNLIMITED)'
            if dims2[key].isunlimited():
                unlimited2= '(UNLIMITED)'

        if not value2:
            show_line(key, f"{value1.size} {unlimited1}", missing)
        elif value1.size != value2.size or unlimited1 != unlimited2:
            show_line(key, f"{value1.size} {unlimited1}", f"{value2.size} {unlimited2}")

    # ce qui n'apparait que dans le second fichier
    missing_keys1 = dims2.keys() - dims1.keys()
    for key in missing_keys1:
        show_line(key, missing, f"{dims2[key].size}")


    # variables
    # ---------
    # récupération des variables de chaque dataset
    vars1 = ds1.variables
    vars2 = ds2.variables

    print('\n// variables', end='', file=handler1)
    if handler2:
        print('\n// variables', end='', file=handler2)
    for key, attrs1 in vars1.items():
        # la variable
        if not key in vars2.keys():
            show_variable_def(str(attrs1).split('\n')[1],
                              missing)
            continue

        attrs2 = vars2[key]
        if str(attrs1) != str(attrs2):
            show_variable_def(str(attrs1).split('\n')[1],
                              str(attrs2).split('\n')[1])

        # attributs de la variables
        attrs2 = vars(vars2[key])
        for k1, v1 in vars(attrs1).items():
            v2 = attrs2.get(k1, missing)
            if str(v1) != str(v2):
                show_line(k1, v1, v2)

        # et ceux qui n'apparaissent que dans le second fichier
        attrs2 = vars2[key]
        for k2, v2 in vars(attrs2).items():
            v1 = vars(vars1[key]).get(k2)

            if not v1:
                show_line(k2, missing, v2)

    # ce qui n'apparait que dans le second fichier
    missing_keys1 = vars2.keys() - vars1.keys()
    for key in missing_keys1:
        attrs2 = vars2[key]
        show_variable_def(missing,
                          str(attrs2).split('\n')[1])


    # globales
    # --------
    # récupération des globales de chaque dataset
    globs1 = vars(ds1)
    globs2 = vars(ds2)

    print('\n// globales', file=handler1)
    if handler2:
        print('\n// globales', file=handler2)
    for key, value1 in globs1.items():
        value2 = globs2.get(key, missing)

        show_line(key, value1, value2)

    # ce qui n'apparait que dans le second fichier
    missing_keys1 = globs2.keys() - globs1.keys()
    for key in missing_keys1:
        show_line(key, missing, globs2[key])

    sys.exit(0)

