#!/usr/bin/env python3

"""
Gestion des environnements de travail de AIDA.
"""

import os
import sys
import configparser

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from fct_messages import (info, warning, stop_error, result, wait_user)


# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


class AIDA_env():
    """ Classe de gestion des environnements de travail de AIDA.
    """
    # attibuts de classe
    # nom du fichier INI de configuration
    file_INI_name = 'AIDA_env.ini'

    # path du fichier INI de configuration
    home_dir = os.path.expanduser( '~' )
    file_INI_path = os.path.join(home_dir, '.config', 'AIDA_env')

    # fullpath du fichier INI de configuration
    file_INI = os.path.join(file_INI_path, file_INI_name)


    def __init__(self):
        """
        """
        self.filename = AIDA_env.file_INI
        self.load_file()


    def load_file(self):
        """ Lecture du fichier INI de configuration des environnements de
            travail de AIDA.

            Raise différentes exception en cas d'erreur.
        """
        # testerl'existance du fichier (configparser n'est pas très cool sur la
        # remontée d'erreur "FileNotFoundError")
        if not os.path.isfile(self.filename):
            raise Exception (f"{self.filename} : le fichier n'existe pas")

        if not os.access(self.filename, os.R_OK):
            raise Exception (f"{self.filename} : problème de droits de lecture")

        parser = configparser.ConfigParser()
        parser.read(self.filename)

        if not 'default' in parser.sections():
            raise Exception (f"{self.filename} : pas de section 'default'")

        if not parser.has_option('default', 'env_name'):
            raise Exception (f"{self.filename} : pas d'option 'env_name' dans la section 'default'")

        default_env_name = parser.get('default', 'env_name')
        if not default_env_name in parser.sections(): 
            raise Exception (f"{self.filename} : la section par défaut '{default_env_name}' n'existe pas")
        self.default_env_name = parser.get('default', 'env_name')

        for section in parser.sections():
            if section == 'default':
                continue
            for option in ['AIDA_META', 'AIDA_DATA']:
                if not parser.has_option(section, option):
                    raise Exception (f"{self.filename} : pas d'option '{option}' dans la section '{section}'")
        
        self.parser = parser 


    def show_me(self):
        """
        """
        for section in self.parser.sections():
            print(f"{section} :")
            for option in self.parser[section]:
                #print(f"  - {option} : {self.parser.get(section, option)}")
                x = self.parser.get(section, option)
                print(f"  - {option:15s} : {os.path.expandvars(os.path.expanduser(x))}")


    def set_env(self, name):
        """ Export dans l'environnement de session toutes les variables de
            l'environnement de travail 'name'.

            NOTE : les variables de type 'PS1' n'ont pas d'impact dans un
                   programme Python (qui n'ont pas le prompt interactif Shell)

            Raise différentes exception en cas d'erreur.
        """
        if not name in self.parser.sections():
            raise Exception (f"{self.filename} : pas de section '{name}'")

        for option in self.parser[name]:
            value = self.parser.get(name, option)
            os.environ[option.upper()] = os.path.expandvars(os.path.expanduser(value))


    def get_env_vars(self, name):
        """ Renvoie toutes les variables d'environnement de travail pour 'name'
            sous la forme d'une chaine de caractères de la forme :
                "'key_1=value_1','key_2=value_2'..."

            Renvoie une chaine vide en cas d'erreur.
        """
        if not name in self.parser.sections():
            return ''

        options = [ f'{option.upper()}={os.path.expandvars(os.path.expanduser(self.parser.get(name, option)))}'
                        for option in self.parser[name] ]

        return ','.join(options)


    def get_env_list(self):
        """ Renvoie une liste de tous les nom d'environnement de travail.

            Renvoie une chaine vide en cas d'erreur.
        """
        return [ section for section in self.parser.sections() if section != 'default' ]


if __name__ == '__main__':

    env = AIDA_env()

    print(f"\n* Show_me()")
    env.show_me()
    wait_user()

    print(f"\n* Liste des environnement")
    vars = env.get_env_list()
    print(f"  - vars = {vars}")
    wait_user()


    for mode in env.get_env_list():
        print(f"\n* Traitement pour : {mode}")
        print(f"** Récupération des variables pour : {mode}")
        vars = env.get_env_vars(mode)
        print(f"    - vars = {vars}")

        print(f"** Positionnement des variables")
        print(f"    - AVANT : AIDA_META = {os.getenv('AIDA_META')}")
        print(f"    - AVANT : AIDA_DATA = {os.getenv('AIDA_DATA')}")
        print(f"    - AVANT : PS1       = {os.getenv('PS1')}")
        env.set_env(mode)
        print(f"    - APRES : AIDA_META = {os.getenv('AIDA_META')}")
        print(f"    - APRES : AIDA_DATA = {os.getenv('AIDA_DATA')}")
        print(f"    - APRES : PS1       = {os.getenv('PS1')}")

        wait_user()


    print(f"\n* Environnement inexistant")
    env.set_env('TRUC')
