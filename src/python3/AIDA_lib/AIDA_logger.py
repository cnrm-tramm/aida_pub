#!/usr/bin/env python3

"""
Définition d'un logger spécifique à AIDA.
  Crée 2 logs :
  - affichage en console   : niveau INFO
  - inscription en fichier : niveau DEBUG (sous /tmp/$USERNAME.<name>.log)

  Le logger doit être défini au plus tôt pour qu'il puisse être utilisé par
  les sous-modules.

  Logger les messages retourner par AIDA.py
  -----------------------------------------
  AIDA.py retourne des messages préfixés par '---' (par exemple).
  Pour pouvoir logger ces messages, un nouveau niveau de message est
  créé : AIDA

  NOTE :
  la création de nouveau niveau de message est déconseillée. Voir :
    https://stackoverflow.com/questions/47888855/python3-add-logging-level

  ATTENTION :
  pour le niveau de log 'AIDA', l'espace qui sépare le levelname
  du message est inclu dans le préfixe (sinon les messages AIDA
  sont décalés d'un espace).


  Traces d'exécution
  ------------------
  Pour permettre de suivre plus facilement le déroulement des codes,  un
  nouveau niveau de message est créé : RUN
  (cf. Note au paragraphe précedent)
  Ces messages sont préfixés par "===".
  Ils ont été pensé pour être utilisés à l'entrée d'une fonction/méthode :
    logger.log(logging.RUN, f"ma_methode : in_arg = '{in_arg}'")
  A la lecture du fichier de log, les lignes préfixées par "===" permettent de
  suivre les appels de fonction/méthode.

  Utilisation
  -----------
  import AIDA_logger
  logger = AIDA_logger.configure_AIDA_logging('toto')
"""

import sys
import os
import logging
import getpass
from   logging.handlers import RotatingFileHandler


class AIDA_Formatter(logging.Formatter):
    """ Formattage selon le niveau de logging (from Web)
    """
    def format(self, record):
        self._style._fmt = "%(levelname)s%(message)s"
        if record.levelno == logging.DEBUG:
            self._style._fmt = "%(levelname)s%(message)s " +\
                               "(from : %(filename)s:%(funcName)s)"
        return super().format(record)

def configure_AIDA_logging(name):
    """
    """
    # création des niveaux de log 'AIDA', 'RUN'...
    logging.RUN  = 15   # DEBUG = 10
    logging.AIDA = 25   # INFO  = 20

    # attention : ajouter un ' ' à la fin du levelname
    logging.addLevelName(logging.DEBUG   , '>>> ')
    logging.addLevelName(logging.RUN     , '=== ')
    logging.addLevelName(logging.INFO    , '--- ')
    logging.addLevelName(logging.WARNING , '-+- ')
    logging.addLevelName(logging.ERROR   , '+++ ')
    # logging.addLevelName(logging.CRITICAL, '!!! ')
    logging.addLevelName(logging.CRITICAL, '+++ ')
    logging.addLevelName(logging.AIDA    , '')

    # création du logger et du formatter
    logger    = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = AIDA_Formatter()

    # création d'un premier handler de type console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    # la ligne de commande est analysée plus tard => pour que les traces 'debug'
    # des sous-modules soient affichées, il faut activer dès maintenant le mode
    # DEBUG.
    if '-V' in sys.argv:
        stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    # créaton d'un second handler de type fichier avec rotation :
    # - sur taille (100Mo),
    # - de profondeur de 10 fichiers,
    # - sous /tmp/$USERNAME.<name>.log
    username     = getpass.getuser()
    log_file     = os.path.join(os.sep, 'tmp', f'{username}.{name}.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=100000000, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.stream_handler = logger.handlers[0]

    return logger


if __name__ == '__main__':
    logger = configure_AIDA_logging('toto')

    logger.debug   ("in MAIN : is DEBUG   ")
    logger.info    ("in MAIN : is INFO    ")
    logger.warning ("in MAIN : is WARNING ")
    logger.error   ("in MAIN : is ERROR   ")
    logger.critical("in MAIN : is CRITICAL")

    logger.log(logging.AIDA, "in MAIN : is AIDA")
    logger.log(logging.RUN , "in MAIN : is RUN")

    print(f"\n--> Le fichier de log est :{logger.handlers[1].baseFilename}")
