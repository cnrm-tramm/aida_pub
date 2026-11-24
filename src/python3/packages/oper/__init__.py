#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Importation des opérateurs python.

  Le dictionnaire '__desc_opers' contient la description de tous les
  opérateurs python. Il contient les informations de chaque 'desc_oper'
  (définit dans le module de l'opérateur) auxquelles sont ajoutées d'autres
  informations utiles à ADC, si besoin.

"""


import os
import sys
import logging
import importlib
from glob import glob
from keyword import iskeyword
import cfunits as cf

logger = logging.getLogger('adc')

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
import Units


# dictionnaire de description de tous les opérateurs python
__desc_opers = dict()

# liste des noms de tous les opérateurs python pour permettre l'exclusion
# des opérateurs C ré-écrits en python (le nom est mémorisé même si l'opérateur
# python est ignoré sinon adc pourrait finir par appeler l'ancien opérateur C)
__all_names = list()


# dictionnaires des familles et abreviation
abrev_to_families = { k: str(v)  for k, v in AIDA.get_all_abrev_to_family() }

cur_dir = os.path.dirname(__file__)

# valeurs acceptées
control_reftime_values = {'off': False, 'on': True}
categorie_values       = ['VECTOR_IN', 'COEFFICIENT', 'VECTOR_OUT']


# traitement
for file_name in glob( os.path.join(cur_dir, '*.py') ):
    short_module_name, _ = os.path.splitext( os.path.basename(file_name) )

    if short_module_name.startswith('_') or iskeyword(short_module_name):
        continue

    logger.debug(f"traitement de : {file_name}")
    module_name = __name__ + '.' + short_module_name

    try:
        # importer le module pour pouvoir étudier sa variable "desc_oper"
        imported_module = importlib.import_module(module_name)
    except Exception as e :
        logger.error(f"Exception à l'import de l'opérateur '{module_name}' : {e}" +
                     f"=> '{module_name}' n'est pas importé !")
        continue

    if not hasattr(imported_module, 'desc_oper'):
        logger.debug(f"{module_name} : pas de variable 'desc_oper' " +
                     f"=> ignoré")
        continue

    # vérification de la variable "desc_oper" du module
    for oper_name, oper_desc in imported_module.desc_oper.items():

        # doublon d'opérateur
        if oper_name in __all_names:
            raise Exception(f"il existe plusieurs opérateurs Python de nom : '{oper_name}'")
            sys.exit(1)


        __all_names.append(oper_name)

        # clés obligatoires
        err  = False
        desc_keys = list(oper_desc.keys())
        for key in ['Args']:
            if not key in desc_keys:
                logger.error(f"{module_name} : opérateur '{oper_name}' : " +
                             f"pas de clé '{key}' => ignoré")
                err = True
            else:
                desc_keys.remove(key)

        # s'il manque une clé obligatoire, on ne pourra pas faire grand-chose
        if err:
            continue

        # clés facultatives
        key = 'control_reftime'
        if key in desc_keys:
            desc_keys.remove(key)

            # vérifier la valeur fournie
            if not oper_desc[key] in control_reftime_values.keys():
                logger.error(f"{module_name} : opérateur '{oper_name}' : " +
                             f"{key} = '{oper_desc[key]}' : valeur inattendue " +
                             f"=> ignoré")
                err = True
                break
            else:
                oper_desc[key] = control_reftime_values[ oper_desc[key] ]
        else:
            oper_desc[key] = control_reftime_values['on']

        for key in ['repl_oper', 'repl_cause']:
            if key in desc_keys:
                desc_keys.remove(key)
            else:
                oper_desc[key] = None

        # il ne reste que des clés inconnues
        if desc_keys:
            logger.error(f"{module_name} : opérateur '{oper_name}' : " +
                         f"clé(s) inattendue(s) : '{','.join(desc_keys)}' => ignoré")


        # description des arguments
        for n, arg_desc in enumerate(oper_desc['Args'], start=1):
            arg_keys = list(arg_desc.keys())

            # clés obligatoires
            for key in ['Id', 'categorie']:
                if not key in arg_keys:
                    logger.error(f"{module_name} : opérateur '{oper_name}' : " +
                                 f"argument {n} : " +
                                 f"pas de clé '{key}' => ignoré")
                    err = True
                    break

                arg_keys.remove(key)

                # vérification des valeurs
                if key == 'categorie':
                    if not arg_desc[key] in categorie_values:
                        logger.error(f"{module_name} : opérateur '{oper_name}' : " +
                                     f"argument {n} : " +
                                     f"{key} = '{arg_desc[key]}' : valeur inattendue " +
                                     f"=> ignoré")
                        err = True
                        break

            # s'il manque une clé obligatoire, on ne pourra pas faire grand-chose
            if err:
                continue

            # clés facultatives
            for key in ['unit', 'famille']:
                if not key in arg_keys:
                    continue

                if key == 'unit':
                    # valider l'unité passée
                    try:
                        arg_desc[key] = Units.get_AIDA_unit(arg_desc[key])
                        arg_keys.remove(key)
                    except Exception as e:
                        logger.error(f"{module_name} : opérateur '{oper_name}' : " +
                                     f"argument {n} : " +
                                     f"{key} = '{arg_desc[key]}' : unité invalide " +
                                     f"=> ignoré")
                        arg_keys.remove(key)
                        err = True

                elif key == 'famille':
                    for value in arg_desc[key]:
                        if not value in abrev_to_families.values():
                            logger.error(f"{module_name} : opérateur '{oper_name}' : " +
                                         f"argument {n} : " +
                                         f"{key} = '{arg_desc[key]}' : " +
                                         f"{value} : famille invalide " +
                                         f"=> ignoré")

                            err = True
                            break
                    arg_keys.remove(key)


            # il ne reste que des clés inconnues
            if arg_keys:
                logger.error(f"{module_name} : opérateur '{oper_name}' : " +
                             f"argument {n} : " +
                             f"clé(s) inattendue(s) : '{','.join(arg_keys)}' => ignoré")


        # la description est correcte
        # => mémoriser tout ça dans le gros dictionaire de __init__.py
        if not err:
            # pointeur sur l'opérateur (pour faciliter l'appel)
            oper_desc['oper_ptr'] = eval(f"imported_module.{oper_name}")

            __desc_opers[oper_name] = oper_desc

