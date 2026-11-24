#!/usr/bin/env python3

"""
Gestion des mails automatiques de AIDA.

    La configuration est lue, par défaut, dans le fichier
        $AIDA_HOME/profils/$AIDA_PROFIL/AIDA_mail.cfg.

    Ce fichier est au format INI.
    Ex :
        [AIDAcalc]
        smtp      = smtp.XXX
        from_addr = user@domain

    Les adresses des destinataires ne sont pas validées avant l'expédition du 
    mail.
"""


import os
import sys
import logging
import datetime as dt
import configparser
import re
import smtplib
from email.message import EmailMessage


logger = logging.getLogger()


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA


class AIDA_mail():
    """ Classe de gestion des mails de AIDA.
    """
    def __init__(self, section, filename=None, to_addrs=None):
        """ La configuration est lue, par défaut, dans le fichier
            $AIDA_HOME/profils/$AIDA_PROFIL/AIDA_mail.cfg.

            La section 'section' est utilisée pour initialiser le SMTP et
            l'adresse expéditeur.

            :param str() section  : section du fichier de configuration à
                                    utiliser.
            :param str() filename : path complet du fichier de configuration.
            :param str() to_addrs : liste des adresses des destinataires.
                                    overwrite la configuration lue dans le
                                    fichier (si présente)
        """
        self.filename = filename

        if not self.filename:
            AH = os.getenv('AIDA_HOME')
            AP = os.getenv('AIDA_PROFIL')
            self.filename = os.path.join (AH, 'profils', AP, 'AIDA_mail.cfg')

        if not os.path.isfile(self.filename):
            raise Exception (f"AIDA_mail::__init__ : " +\
                             f"le fichier '{self.filename}' n'existe pas")

        # récupérer les info de la section depuis le fichier de configuration
        parser = configparser.ConfigParser()
        parser.read(self.filename)

        if not section in parser.sections():
            raise Exception (f"AIDA_mail::__init__ : '{self.filename}' :" +\
                             f"pas de section '{section}'")


        self.cfg = dict(parser.items(section))
        self.cfg['to_addrs'] = to_addrs

        # vérifier que les options obligatoires sont présentes
        if not 'smtp' in self.cfg.keys():
            raise Exception (f"AIDA_mail::__init__ : '{self.filename}' : " +\
                             f"section '{section}' : pas d'option 'smtp'")

        if not 'from_addr' in self.cfg.keys():
            raise Exception (f"AIDA_mail::__init__ : '{self.filename}' : " +\
                             f"section '{section}' : pas d'option 'from_addr'")

        return


    def send_report(self, subject=None, body_txt=None,
                    from_addr=None, to_addrs=None, smtp=None):
        """ Expédie un mail TEXTE 'subject'/'body_txt' depuis l'adresse
            'from_addr' aux destinataires 'to_addrs' en utilisant le
            SMTP 'smtp'.

            NOTES :
            - pas de gestion de proxy.
            - les adresses des destinataires ne sont pas validées avant
              l'expédition du mail.

            :param str() subject  : sujet du mail.
            :param str() body_txt : corps du mail.
            :param str() from_addr: adresse de l'expéditeur
            :param str() to_addrs : liste des destinataires.
                                    FORMAT : suite d'adresses valides séparées
                                    par un caractère : ,; +|
                                    Ex : nom.prenom@a.fr+nom.prenom@b.fr
            :param str() smtp     : SMPT à utiliser.
                                    'localhost' ne fonctionnera que si un SMPT
                                    a été configuré sur la machine expéditrice.
        """
        # smtp
        if not smtp:
            smtp = self.cfg['smtp']
        logger.debug(f"AIDA_mail::send_report : use smtp : {smtp}")

        # from_addr
        if not from_addr:
            from_addr = self.cfg['from_addr']
        logger.debug(f"AIDA_mail::send_report : use from_addr : {from_addr}")

        # to_addrs
        if not to_addrs:
            to_addrs = self.cfg['to_addrs']
        logger.debug(f"AIDA_mail::send_report : use to_addrs : {to_addrs}")

        # création du message
        msg = EmailMessage()
        msg.set_content(body_txt)

        msg['Subject'] = subject
        msg['From']    = from_addr
        msg['To']      = re.sub('[; +|]', ',', to_addrs)

        # expédition du mail via SMTP
        try:
            srv = smtplib.SMTP(smtp)
            srv.send_message(msg)
            srv.quit()
        except Exception as e:
            raise Exception(f'erreur : {e}')

        return


if __name__ == '__main__':

    import getopt


    #print(__doc__.format(me=__file__))
    #print()

    # logger basic
    if len(logger.handlers) == 0:
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')


    to_dest = None

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'M:')
    except getopt.error as msg:
        logger.critical(f"option inconnue : '{msg.opt}'")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-M'):
            to_dest = arg
            logger.warning( "les adresses des destinataires ne sont pas " +\
                           f"vérifiées : {to_dest}")

        else:
            logger.critical(f"option inconnue : '{opt}'")
            sys.exit(1)

    if not to_dest:
        logger.critical("fournir l'option : -M adresses_destinataires") 
        sys.exit(1)

    # instanciation
    try:
        test_mail = AIDA_mail('AIDAcalc', to_addrs=to_dest)
    except Exception as e:
        logger.critical(f"{e}")
        sys.exit(1)

    # envoyer le mail
    today = dt.datetime.strftime(dt.datetime.now(), '%d/%m/%Y')
    subject = f"[AIDAcalc] : {today} compte-rendu d'exécution"
    body    = """Bonjour,

                Je suis désolée de vous faire parvenir ce mail de test.
                Merci cependant d'en accuser réception.

                AIDAcalc
              """

    try:
        #test_mail.send_report(subject=subject, body_txt=body, to_addrs=to_dest)
        test_mail.send_report(subject=subject, body_txt=body)
    except Exception as e:
        logger.critical(f"exception de 'test_mail.send_report' : {e}")
        sys.exit(1)

    logger.info("mail expédié")

