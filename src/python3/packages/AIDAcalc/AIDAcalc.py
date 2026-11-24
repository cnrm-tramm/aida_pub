#!/usr/bin/env -S python3 -u
# -u : Force  the stdout and stderr streams to be unbuffered.

"""
AIDAcalc (ou adc)
=================
    Filière de calcul sur les vecteurs de données AIDA.

  usage :
    {me} [option] <acqid> <fichier>

  sans option :
    les vecteurs résultants sont écrits sur le disque/base uniquement s'ils
    n'existent pas.

  options :
    *** Les options [-f, -F, -Ni] sont toutes exclusives SAUF "-F -Ni".
    *** L'option -Ni ne peut pas ête fournie s'il existe une base de
    *** données pour la plateforme de l'acqid.

    -h             : affiche cette aide et exit.
    -v             : affiche la version de ce programme et exit.
    -V             : mode Verbose.
    -n             : mode dry-run (non implémenté).
    -S             : mode stop on error : default = False
    -M <mail-list> : mode mail-to. Le fichier de configuration
                     $AIDA_HOME/profils/<PROFIL>/AIDA_mail.cfg doit exister.
                     Les adresses sont séparées par des ',' sans espaces.
                     A TRAMM, l'expédition de mail, via le VPN ne fonctionne pas.
    -f             : mode versionning.
    -F             : mode force.
    -Ni            : mode développement ('i' est un numéro de version).
                     (cette option ne peut pas être spécifiée s'il existe une
                     base de données pour la plateforme).
    -C             : invalide le contôle sur les familles.
                     Cette option pemet de retraiter les anciennes acquisitions
                     comme le faisait FVB (qui ne faisait pas ce contrôle)
    -T             : mode 'test et validation'
                     avant d'écrasser un vecteur généré par FVB, ADC le renomme
                     xxx.FVB.vbn. Ce vecteur pourra, par la suite, être utilisé
                     par l'outillage de validation du répertoire :
                     src/python3/packages/AIDAcalc/validation.

  arguments :
    <acqid>   : acqid des données
              : acqid peut être une liste de la forme : as200015-as200019
    <fichier> : fichier de commande de traitement (.fil)

Pour plus de documentation, consulter la documentation AIDA : user.pdf
"""

import sys
import os
import atexit
import getopt
import logging
import datetime
import re
import copy
import ctypes as ct


# cetains petits réglages seront fait selon que l'on lance :
# - '$AIDA_HOME/bin/adc' (prod) ou
# - './AIDAcalc' (dev)
who_am_i = os.path.basename(__file__)


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
AL            = os.path.join(os.getenv('AIDA_HOME'), 'lib')
path_lib_oper = os.path.join(AL, 'liboper.so')


# adapter sys.path selon que l'on lance 'bin/adc' (prod) ou './AIDAcalc' (dev)
if who_am_i == 'adc':
    sys.path.append(os.path.join(AL, PYTHON_X_Y))
    sys.path.append(os.path.join(AL, PYTHON_X_Y, 'AIDAcalc'))
else:
    here_dir = os.path.dirname(os.path.realpath(__file__))
    up_dir   = os.path.dirname(here_dir)
    sys.path.append(up_dir)
    sys.path.append(os.path.join(AL, PYTHON_X_Y))

# Création du logger au plus tôt pour qu'il puisse être utilisé par les modules
import AIDA_logger
logger = AIDA_logger.configure_AIDA_logging('adc')


import AIDA
from Fil_analyze import check_fil, parse_instruction

import args_opts
from OperTypes import OperTypes, get_OperType

import ADC_error

from fct_messages import wait_user
import AcqId
import DataBase
import AIDA_mail


# Rapport d'exécution
from ADC_rapport import ADC_Rapport as Rapport
Rapport.add('TODO', "Var_Ech.c et autre font des printf (voir stdout_redirect.py)", cat='dev')
Rapport.add('TODO', "FVB remplace $Chrono mais pas $Acq dans les fct_origine...", cat='dev')

Rapport.add("à vérifier avec l'équipe",
            "Oper::normalize_famille: exit sur : acronyme ne correspond à " +\
            "aucune famille ?", cat='dev')
Rapport.add("à vérifier avec l'équipe",
            "Oper::normalize_famille: exit sur : famille inexistante ?", cat='dev')


# OPERATEURS
# ----------
# Il faut traiter en premier les opérateurs Python pour pouvoir ensuite
# exclure, des opérateurs C, ceux qui ont été ré-écrits en Python


# gestion des opérateurs Python
# -----------------------------
logger.debug("chargement des opérateurs Python")
try:
    import oper
except Exception as e:
    logger.critical(e)
    sys.exit(1)


import Oper_PY

# descriptions des opérateurs Python
desc_opers_PY = oper.__desc_opers

# dictionnaire des operateurs Python
opers_PY = { oper.Nom: oper for oper in Oper_PY.init_opers_PY(desc_opers_PY) }

# noms des opérateurs Python
opers_PY_names = desc_opers_PY.keys()
if logger.stream_handler.level == logging.DEBUG:
    logger.debug("opers_PY_names :")
    for i, oper_name in enumerate(opers_PY_names, start=1):
        logger.debug(f"  {i:03d} : {oper_name}")
    wait_user()
else:
    logger.debug(f"{len(opers_PY_names)} opérateurs PY chargés")


# gestion des opérateurs C
# ------------------------
import oper_API_PY_desc
import Oper_C

# description des opérateurs C
desc_opers_C = oper_API_PY_desc.oper_API_PY_desc

# liboper (utile pour récupérer les pointeurs sur fonctions)
lib_oper = ct.CDLL(path_lib_oper)


# dictionnaire des operateurs C
logger.debug("chargement des opérateurs C")
opers_C = { oper.Nom: oper
              for oper in Oper_C.init_opers_C(desc_opers_C,
                                              exclude=oper.__all_names)
          }

Rapport.add('TODO', "récupération des pointeurs sur OP_XXX dans Oper_C.py", cat='dev')
# opérateur C : récupération des pointeurs sur fonction OP_
logger.debug("Récupération des pointeurs sur fonction 'OP_'")
for oper_name, oper in opers_C.items():
    OP_name = f'lib_oper.{oper.OP_fct_name}'
    try:
        instruction = compile(f'OP_xxx = {OP_name}', '<string>', 'exec')
        env_fvb = {}
        eval(instruction, globals(), env_fvb)
    except AttributeError as e:
        logger.warning(f"la fonction {OP_name} n'existe pas")
        logger.warning(f"{e}")
        logger.warning("voir avec William le problème de Correl.c -> OP_correl")
        wait_user()
        continue
    oper.OP_fct = env_fvb['OP_xxx']

# noms des opérateurs C
opers_C_names = list(opers_C)
if logger.stream_handler.level == logging.DEBUG:
    logger.debug("opers_C_names :")
    for i, oper_name in enumerate(opers_C_names, start=1):
        logger.debug(f"  {i:03d} : {oper_name}")
    wait_user()
else:
    logger.debug(f"{len(opers_C_names)} opérateurs C-pur chargés / " +\
                 f"{len(desc_opers_C)} opérateurs C")


# concernant ce programme
__version__ = "2.0.0"
me = os.path.split(sys.argv[0])[1]


def usage():
    """ Affiche l'usage.
    """
    print(__doc__.format(me=me))


def goodbye(start_at, cmd_line):
    """ Fonction lancée à l'arrêt de l'interpréteur (<=> atexit)
    """
    logger.log(logging.RUN, "goodbye")

    stop_at = datetime.datetime.strftime(dt_now, '%d/%m/%Y %H:%M:%S')

    # informations récapitulatives en fin d'excécution
    logger.log(logging.AIDA, "\nbye...")
    logger.info(f"fichier de log : {logger.handlers[1].baseFilename}")
    logger.info(f"commande       : {cmd_line}")
    logger.info(f"démarrage      : {start_at}")
    logger.info(f"arrêt          : {stop_at}")

    if len(Rapport._usr) > 0:
        logger.info(f"rapport d'exécution :")
        #print(Rapport.show(Rapport.Verbosity.ultra_light))
        #print(Rapport.show(Rapport.Verbosity.light))
        print(Rapport.show(Rapport.Verbosity.detailed))
    else:
        logger.info(f"rapport d'exécution : RAS :-)")


    if adc_opts['test_and_valid'] and len(Rapport._dev) > 0:
        print()
        logger.info(f"rapport de dev :")
        print(Rapport.show(Rapport.Verbosity.detailed, cat='dev'))


    # si besoin, envoi par mail des informations récapitulatives
    # il n'est pas simple de récupérer le code d'exit dans la fonction
    # enreistrée auprès de atexit
    # => le "si besoin" est déterminé par la taille du dictionnaire
    # du Rapport (oui, c'est moyen)
    if adc_opts['mails'] and len(Rapport._usr) > 0:
        AIDAcalc_mail = adc_opts['mails']

        logger.debug(f"AIDAcalc::goodbye: AIDAcalc_mail = {AIDAcalc_mail}")

        subject = f"[AIDAcalc] : {start_at} : compte-rendu d'exécution"
        rapport = Rapport.show(Rapport.Verbosity.detailed)
        body    = f"commande  : {cmd_line}\n" +\
                  f"démarrage : {start_at}\n" +\
                  f"arrêt     : {stop_at}\n" +\
                  f"rapport d'exécution : \n" +\
                  f"{rapport}\n"

        try:
            AIDAcalc_mail.send_report(subject=subject, body_txt=body)
        except Exception as e:
            # cette erreur ne doit pas être inscrite dans le Rapport
            # => ne pas utiliser ADC_error.critical
            logger.critical(f"erreur de 'AIDA_mail.send_report' : {e}")

        return


def check_args_HDR(oper):
    """ Vérifie la cohérence des args_HDR pour l'opérateur 'oper'.
    """
    logger.log(logging.RUN, "check_args_HDR")
    if not oper.args_HDR:
        return

    nb_VO = len(list(oper.get_VECTOR_DIR_OUT()))

    for key, val in oper.args_HDR.items():
        if not isinstance(val, list):
            ADC_error.critical(f"l'argument optionnel '{key}' doit être une liste (ligne {oper.line_nb})", stop=True)

        if len(val) != nb_VO:
            ADC_error.critical(f"l'argument optionnel '{key}' doit être une liste de {nb_VO} valeurs (ligne {oper.line_nb})", stop=True)


def get_console_cmd(opers_C_names, opers_PY_names):
    """ lit et vérifie une ligne de commande en mode 'console'
    """
    logger.log(logging.RUN, "get_console_cmd")

    ok = False
    while not ok:
        print("\nEntrez 1 commande ou [Entrée] pour terminer :")
        lines = [ input() ]

        try:
            check_fil(in_file, lines, opers_C_names, opers_PY_names, logger)
            ok = True
        except Exception as e:
            logger.critical(e)

    return lines


if __name__ == '__main__':

    print(f"\n{who_am_i} version {__version__} vous souhaite la bienvenue.\n")
    dt_now = datetime.datetime.now()
    start_at = datetime.datetime.strftime(dt_now, '%d/%m/%Y %H:%M:%S')
    logger.info(f"Démarrage : {start_at}")

    # parsing de la ligne de commande
    acqids, in_file, adc_opts = args_opts.args_opts(sys.argv, usage, __version__)

    # enregistrement de la fonction à exécuter au moment de l'arrêt de
    # l'interpréteur
    atexit.register(goodbye, start_at=start_at, cmd_line=' '.join(sys.argv))

    # logger les infos de la ligne de commande
    logger.info(f"acqids  : {acqids}")
    logger.info(f"in_file : {in_file}")
    logger.info( "options de lancement :")
    for key, value in adc_opts.items():
        logger.info(f"  - {key:15} : {value}")


    # vérifier qu'il existe des données pour les acqids
    nb_err = 0
    for acqid in acqids:
        acqid_datapath = AIDA.ID_to_datapath(acqid)
        if not os.path.isdir(acqid_datapath):
            logger.critical(f"{acqid} : pas de données...")
            nb_err = nb_err + 1
    if nb_err >0:
        ADC_error.critical(f"pas de données pour {nb_err} acqid(s)", stop=True)


    # lecture du .fil et vérification de la syntaxe globale 
    if not in_file == '-':
        # les .fil sont en utf-8 ou en lantin-1...
        try:
            with open(in_file, 'r') as handler:
                lines = handler.readlines()
        except UnicodeDecodeError:
            with open(in_file, 'r', encoding='iso-8859-1') as handler:
                lines = handler.readlines()

        # vérification de la syntaxe globale
        try:
            check_fil(in_file, lines, opers_C_names, opers_PY_names, logger)
        except Exception as e:
            ADC_error.critical(e, stop=True)
        else:
            logger.debug("main : check_fil pass...")


    # traitements
    # -----------
    while True:
        # en mode 'console', lire la commande à traiter depuis stdin
        if in_file == '-':
            lines = get_console_cmd(opers_C_names, opers_PY_names)
            if lines[0] == '':
                # fin des commandes
                break

        # en mode 'console', appliquer la ligne lue    sur chacun des acqid
        # en mode '.fil'   , appliquer tout le fichier sur chacun des acqid
        for acqid in acqids:

            logger.log(logging.AIDA, '')    # saut de ligne...
            logger.info(f"{acqid} ----------------")

            # traiter la ligne donnée par stdin ou les lignes du .fil
            for line_nb, line_cmd in enumerate(lines, start=1):
                line_cmd = line_cmd.replace ('\n', '')
                line     = line_cmd.strip()
                if line == '' or line[0] == '#':
                    continue

                logger.info(f"Traitement de : {line} (ligne : {line_nb})")
                try:
                    oper_name, args_brut, args_opt, args_HDR = parse_instruction(line)
                    oper_type = get_OperType(oper_name, opers_C_names, opers_PY_names)
                except Exception as e:
                    ADC_error.critical(e, stop=True)


                # initialisation de la variable 'oper' en fonction du type
                # d'opérateur
                if oper_type == OperTypes.C:
                    oper = opers_C[oper_name]
                    if args_opt:
                        logger.warning(f"l'opérateur '{oper_name}' ne prend " +\
                                       f"pas d'argument optionnel ('{args_opt}')")
                else:
                    # ATTENTION : faire une copie profonde pour pouvoir
                    # ajouter des atributs de l'instruction à la
                    # description de l'opérateur
                    oper = copy.deepcopy(opers_PY[oper_name])
                oper.line_nb  = line_nb
                oper.line_cmd = line_cmd
                oper.adc_opts = adc_opts
                oper.args_HDR = args_HDR

                # vérifier la cohérence des args_HDR
                check_args_HDR(oper)

                # afficher un message en cas d'obsolescence de l'opérateur
                oper.warn_if_obsolet()

                # exécution
                if oper_type == OperTypes.C:

                    try:
                        oper.exec_line(acqid, args_brut)
                    except Exception as e:
                        ADC_error.critical(f"{acqid} : erreur d'exécution "
                                           f"à la ligne {line_nb} : {e}",
                                           stop=adc_opts['stop_on_error'])
                else:
                    try:
                        oper.exec_line(acqid, args_brut, args_opt)
                    except Exception as e:
                        ADC_error.critical(f"{acqid} : erreur d'exécution "
                                           f"à la ligne {line_nb} : {e}",
                                           stop=adc_opts['stop_on_error'])

                logger.log(logging.AIDA,"")

        logger.debug(f"Fin des commandes sur acqid = {acqids}")

        # en mode '.fil', sortie de la boucle 'while True:'
        if not in_file == '-':
            break


    # fin (exécute goodbye())
    sys.exit(0)
