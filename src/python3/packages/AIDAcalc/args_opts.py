#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Parsing de la ligne de commande.
"""

import sys
import os
import logging
import getopt


logger = logging.getLogger('adc')


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
import AcqId
import DataBase
import AIDA_mail
import Camp ### TODO la fonction 'expand_acqids_pltf' aurait dû être dans AcqId...


def args_opts(argv, fct_usage, version):
    """ Récupération des options et arguments de la ligne de commande.

        Retourne :
        - acqid   list() : liste des acqids passés en arguments
        - in_file str()  : nom du fichier .fil ou '-' pour stdin
        - opts    dict() : dictionnaire des opptions passées en argument
    """

    # en ce début de programme, on ne passera pas par la fonction 'goodbye',
    # le Rapport et tout le tralala :
    # => ne pas utiliser ADC_error.critical
    # => on fait des logger.critical + sys.exit()

    acqid           = None
    in_file         = None
    backup          = False
    force           = False
    dev_nb          = None
    control_famille = True
    stop_on_error   = False
    AIDAcalc_mail   = None
    test_and_valid  = False

    try:
        opts, args = getopt.getopt(argv[1:],
                                   'hvVnSM:fFN:CT')
    except getopt.error as msg:
        logger.critical(f"option inconnue : '{msg.opt}'")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h'):
            fct_usage()
            sys.exit(1)

        elif opt in ('-v'):
            logger.info(f"{os.path.split(sys.argv[0])[1]} version : {version}")
            sys.exit(1)

        elif opt in ('-V'):
            logger.stream_handler.setLevel(logging.DEBUG)

        elif opt in ('-n'):
            logger.warning("mode dry_run non implémenté")

        elif opt in ('-S'):
            stop_on_error = True

        elif opt in ('-M'):
            # création de l'objet AIDA_mail
            try:
                AIDAcalc_mail = AIDA_mail.AIDA_mail('AIDAcalc', to_addrs=arg)
            except Exception as e:
                logger.critical(f"{e}")
                sys.exit(1)

        elif opt in ('-f'):
            if force or dev_nb:
                logger.critical(f"options incompatibles : -f et : -F ou -Ni")
                sys.exit(1)
            backup = True

        elif opt in ('-F'):
            if backup:
                logger.critical(f"options incompatibles : -f et -F")
                sys.exit(1)
            force = True

        elif opt in ('-N'):
            if backup:
                logger.critical(f"options incompatibles : -f et -Ni")
                sys.exit(1)

            try:
                dev_nb = int(arg)
            except ValueError as e:
                logger.critical(f"option -Ni : i doit être un entier positif")
                sys.exit(1)
            if dev_nb < 0:
                logger.critical(f"option -Ni : i doit être un entier positif")
                sys.exit(1)

        elif opt in ('-C'):
            control_famille = False

        elif opt in ('-T'):
            test_and_valid = True

        else:
            logger.critical(f"option inconnue : '{opt}'")
            sys.exit(1)

    # arguments
    if len(args) == 2:
        (acqid, in_file, ) = tuple(args)
    elif len(args) == 1:
        (acqid, )   = tuple(args)
        in_file = '-'
    else:
        fct_usage()
        logger.critical("1 ou 2 paramètres attendus : 'acqid' ou " +\
                        "'acqid et fichier'")
        sys.exit(1)


    # vérification des arguments
    # si besoin, récupérer la liste d'acqids
    try:
        acqids = Camp.expand_acqids_pltf(acqid)
    except Exception as e:
        logger.critical(f"erreur d'acqid : {acqid} : {e}")
        sys.exit(1)

    if len(acqids) == 0:
        logger.critical(f"erreur d'acqid : {acqid}")
        sys.exit(1)


    # existance du fichier de commande .fil
    if in_file != '-':
        if not os.path.isfile(in_file):
            logger.critical(f"le fichier '{in_file}' n'existe pas.")
            sys.exit(1)

        if not os.access(in_file, os.R_OK):
            logger.critical(f"le fichier '{in_file}' n'est pas lisible.")
            sys.exit(1)

    opts = dict()
    opts['backup']          = backup
    opts['force']           = force
    opts['dev_nb']          = dev_nb
    opts['control_famille'] = control_famille
    opts['stop_on_error']   = stop_on_error
    opts['mails']           = AIDAcalc_mail
    opts['test_and_valid']  = test_and_valid
    test_and_valid  = False

    return acqids, in_file, opts


if __name__ == '__main__':


    def dummy_usage():
        print("dummy usage")
        sys.exit(1)

    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)s : %(message)s')

    # parsing de la ligne de commande
    acqids, in_file, opts = args_opts(sys.argv, dummy_usage, '1.1.1')
    logger.info(f"acqids              = {acqids}")
    logger.info(f"in_file             = {in_file}")
    logger.info("opts :")
    for key, value in opts.items():
        logger.info(f"  - {key:15s} = {value}")
    input('...')


    # s'il existe une BdD pour la plateforme, l'optin -Ni est interdite
    if DataBase.ExistDataBase(acqids[0]):
        if opts['dev_nb']:
            logger.critical( "Il existe une BdD pour la plateforme " +\
                            f"'{acqids[0][0:2]}' => option -Ni interdite")
            sys.exit(1)
    logger.info(f"PAS de BdD pour la plateforme '{acqids[0][0:2]}'")
