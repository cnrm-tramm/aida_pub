#!/usr/bin/env python3


"""
Utilitaire autour des datations de type DOY.

  usage :
    {me} <acqid>
       retourne la date correspondante à l'acqid.

    {me} <yy0xxx> avec yy=année et xxx=numéro du jour
       retourne la date correspondante à yy0xxx.

    {me} <yyyy-mm-dd>|<dd/mm/yyyy>
       retourne le DOY correspondant à la date fournie.

    {me} <yyyymmdd>
       retourne le DOY correspondant à la date fournie (préfixé d'un 0).
"""

import os
import sys
import locale
import datetime as dt


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

    in_str = sys.argv[1]

    if len(in_str) == 10:   # date
        if '/' in in_str:
            date = dt.datetime.strptime(in_str, "%d/%m/%Y")
        else:
            date = dt.datetime.strptime(in_str, "%Y-%m-%d")
        print(f"{in_str} --> {date.strftime('%j')} (numéro du jour)")

        sys.exit(1)

    elif len(in_str) == 8:  # acqid ou yyyymmdd
        if in_str[0] in ['1', '2']:
            date = dt.datetime.strptime(in_str, "%Y%m%d")
            print(f"{in_str} --> {date.strftime('0%j')} (numéro du jour)")

            sys.exit(1)
        else:
            date = dt.datetime.strptime(in_str[2:], "%y0%j")

    elif len(in_str) == 6:  # yy0xxx
        date = dt.datetime.strptime(in_str, "%y0%j")

    else:
        print(f"\n--> erreur : argument '{in_str}' : mauvais format")
        usage()

    # pour avoir les noms de mois en français
    locale.setlocale(locale.LC_TIME,'')

    # récupérer le datatime de l'acqid
    print(f"{in_str} --> {date.strftime('%d %B %y')}")

