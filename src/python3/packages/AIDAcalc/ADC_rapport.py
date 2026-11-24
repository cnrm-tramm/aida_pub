#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Gestion d'un rapport d'éxécution pour ADC.
"""

import sys
import os
import logging
from enum import Enum


logger = logging.getLogger('adc')


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


class ADC_Rapport:
    """ Gestion d'un rapport d'éxécution pour ADC.
    """

    # niveau de détail du rapport renvoyé par 'show'
    class Verbosity(Enum):
        ultra_light = 0
        light       = 1
        detailed    = 2

    # le rapport est un simple dictionnaire
    _usr = dict()

    # il peut être intéressant de mémoiriser des info pendant le dev
    _dev = dict()


    @classmethod
    def add(cls, key, value, cat='usr'):
        """ Ajout/mise à jour de la catégorie 'key' avec la valeur 'value'.

            :param str()  key  : nom de la catégorie.
            :param dict() value: valeur de la catégorie.
            :param str()  cat  : 'usr' => on adresse le dictionnaire '_usr'
                                 autre => on adresse le dictionnaire '_dev'
        """
        what = cls._usr
        if not cat == 'usr':
            what = cls._dev

        if not key in what.keys():
            what[key] = [ value ]
        else:
            what[key].append(value)


    @classmethod
    def show_one(cls, key, verbosity=Verbosity.ultra_light, cat='usr'):
        """ Retourne la catégorie 'key' du rapport en accord avec la verbosité
            'verbosity'.

            :param str()       key      : nom de la catégorie.
            :param Verbosity() verbosity: vebosité appartient à :
                                           [ Verbosity.ultra_light,
                                             Verbosity.light
                                             Verbosity.detailed
                                           ]
            :param str()  cat  : 'usr' => on adresse le dictionnaire '_usr'
                                 autre => on adresse le dictionnaire '_dev'

            :return: le contenu de la catégorie 'key' au format str().
        """
        what = cls._usr
        if not cat == 'usr':
            what = cls._dev

        if not key in what.keys():
            return ''

        head = f"  * {key} : {len(what[key])}"
        body = ''

        if verbosity == cls.Verbosity.light:
            body = f"\n    * {what[key]}"
        if verbosity == cls.Verbosity.detailed:
            body = ''.join([ f"\n      {v}" for v in what[key] ])
        return head + body


    @classmethod
    def show(cls, verbosity=Verbosity.ultra_light, cat='usr'):
        """ Retourne tout le contenu du rapport en accord avec la verbosité
            'verbosity'.

            :param Verbosity() verbosity: vebosité appartient à :
                                           [ Verbosity.ultra_light,
                                             Verbosity.light
                                             Verbosity.detailed
                                           ]
            :param str()  cat  : 'usr' => on adresse le dictionnaire '_usr'
                                 autre => on adresse le dictionnaire '_dev'

            :return: le contenu du rapport au format str().
        """
        what = cls._usr
        if not cat == 'usr':
            what = cls._dev

        return '\n'.join([cls.show_one(k, verbosity, cat) for k in what.keys()])


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s - %(message)s')

    print("ici debug au print")
    truc1 = 'param1 correct'
    logging.debug(f"init truc1 ok : truc1 = {truc1}")
    print(f"--- truc1 = {truc1}")
    ADC_Rapport.add('ok', truc1)

    truc2 = "il faut peut-être vérifier ce truc"
    logging.debug(f"truc2 = {truc2}")
    print(f"--- truc2 = {truc2}")
    ADC_Rapport.add('à traiter', truc2)

    truc3 = "param3 tout pourri"
    logging.debug(f"truc3 = {truc3}")
    print(f"--- truc3 = {truc3}")
    ADC_Rapport.add('NOK', truc3)

    print("!!! ici voir avec mon Chef-préféré !!!")
    ADC_Rapport.add('space', "!!! ici voir avec mon Chef-préféré !!!")

    truc4 = 'param4 correct'
    ADC_Rapport.add('ok', truc4)

    truc5 = "param5 tout pourri"
    ADC_Rapport.add('NOK', truc5)

    # impression en fin d'exécution
    verbosity = ADC_Rapport.Verbosity.detailed
    print('\n ========= RAPPORT : %-20.20s =========' % verbosity)
    print(ADC_Rapport.show(verbosity))

    verbosity = ADC_Rapport.Verbosity.light
    print('\n ========= RAPPORT : %-20.20s =========' % verbosity)
    print(ADC_Rapport.show(verbosity))

    verbosity = ADC_Rapport.Verbosity.ultra_light
    print('\n ========= RAPPORT : %-20.20s =========' % verbosity)
    print(ADC_Rapport.show())

    verbosity = ADC_Rapport.Verbosity.detailed
    print("\n ========= RAPPORT clé 'NOK' : %-20.20s =========" % verbosity)
    print(ADC_Rapport.show_one('NOK', verbosity))

    # avec un dictionnaire de dev
    verbosity = ADC_Rapport.Verbosity.detailed
    ADC_Rapport.add('ok', truc1, cat='dev')
    ADC_Rapport.add('critic', 'truc CRITIQUE !', cat='dev')
    ADC_Rapport.add('NOK', truc1 + " C'EST FAUX", cat='dev')
    print("\n ========= RAPPORT : USR : %-20.20s =========" % verbosity)
    print(ADC_Rapport.show(verbosity))
    print("\n ========= RAPPORT : DEV : %-20.20s =========" % verbosity)
    print(ADC_Rapport.show(verbosity, cat='dev'))



    print("\n=== python%d.%d ===\n" %
          (sys.version_info[0], sys.version_info[1]))


    sys.exit(0)
