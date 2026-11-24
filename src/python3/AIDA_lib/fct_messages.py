#!/usr/bin/env python3

""" Fonctions d'écriture de message préfixés sur stderr.
"""


import os
import sys

__version__ = "1.0.0"

class bcolors:
    """ Pour écrire en couleur...
    """
    HEADER = '\033[35m'
    OKBLUE = '\033[34m'
    OKGREEN = '\033[32m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REVERSE = '\033[7m'
    WARNING = '\033[7m\033[33m'
    FAIL = '\033[1m\033[31m'


def warning(msg, prefixe='-+- ', bcolor=bcolors.BOLD):
    """ Ecrit un message sur stderr.
    """

    if sys.stderr.isatty():
        print( "%s%s%s%s" % (bcolor,
                            prefixe,
                            msg,
                            bcolors.ENDC), file=sys.stderr)
    else:
        print( "%s%s"    % (
                            prefixe,
                            msg), file=sys.stderr)


def stop_error(msg):
    """ Ecrit un message sur stderr et arrêt le programme.
    """
    warning(msg, prefixe='+++ ', bcolor=bcolors.FAIL)
    sys.exit(1)


def info(msg, bcolor=''):
    """ Ecrit un message sur stderr.
    """
    warning(msg, prefixe='--- ', bcolor=bcolor)


def result(msg, bcolor=bcolors.BOLD):
    """ Ecrit un message sur stderr.
    """
    warning(msg, prefixe='---> ', bcolor=bcolor)


def wait_user(msg='... taper la touche [ENTER] pour continuer'):
    """ Affiche un message à l'écran et attend une validation de l'utilisateur
    """
    input(msg)


#=========================================================================
def test():
    """ rassembler les tests ici."""


    print("%s.test : %s" % (os.path.split(sys.argv[0])[1], "warning"))
    warning("HEADER......", bcolor=bcolors.HEADER)
    warning("OKBLUE......", bcolor=bcolors.OKBLUE)
    warning("OKGREEN.....", bcolor=bcolors.OKGREEN)
    warning("BOLD........", bcolor=bcolors.BOLD)
    warning("UNDERLINE...", bcolor=bcolors.UNDERLINE)
    warning("REVERSE.....", bcolor=bcolors.REVERSE)
    warning("WARNING.....", bcolor=bcolors.WARNING)
    warning("FAIL........", bcolor=bcolors.FAIL)
    wait_user()

    info("ceci est un message d'info")
    warning("ceci est un message de warning")
    warning("ceci est un message de warning en OKBLUE", bcolor=bcolors.OKBLUE)
    result("résultat OK")
    stop_error('fin du test par stop_error() !')
    sys.exit(1)


#=========================================================================
if __name__ == '__main__':
    os.system('clear')
    test()


#=========================================================================
