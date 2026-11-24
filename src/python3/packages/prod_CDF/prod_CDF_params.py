#!/usr/bin/env python3

"""
Production de fichier NetCDF à partir de fichiers-vecteurs
==========================================================

  Gestion des paramètres à inscrire dans le fichier NetCDF.
"""

import sys
import os
import logging
import re
import numpy as np

logger = logging.getLogger('prod_CDF')

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
from AIDA_name_to_CF_name import AIDA_name_to_CF_name


class Param:
    """ Gestion des paramètres à inscrire dans le fichier NetCDF.
    """

    # options obligatoires
    _mandatory_options = ['long_name', 'origin']


    def __init__(self, name, selector, **kwargs):
        """
            :param Selector() selector  : objet Seliector contenant le
                                          dictionnaire de sélection de vecteurs.
            :param dict()     kwargs    : dictionnaire d'attributs du
                                          paramètre.

            kwargs est un dictionnaire qui contient les options lues dans le
            fichier de configuration.
        """
        logger.log(logging.RUN, f"Param::__init__ : {name}")

        self.name     = self.CF_compliency(name)
        self.selector = selector

        self.config = dict() # infos issues du fichier de configuration
        self.attrs  = dict() # infos issues des headers des vecteurs du paramètre
        self.source = None   # infos issues des headers des ancêtres du paramètre
        self.data   = None   # data  issues des vecteurs du paramètres

        self.config['long_name']     = kwargs.get('long_name'    , None)
        self.config['origin']        = kwargs.get('origin'       , None)
        self.config['standard_name'] = kwargs.get('standard_name', None)

        # vérification de la présence des options obligatoires
        for option in Param._mandatory_options:
            if self.config[option] == None:
                raise Exception (f"section {name:15s} : pas d'option " +\
                                 f"'{option}' fournie")

        # ajout des options libres
        for key, val in kwargs.items():
            if not key in Param._mandatory_options:
                self.config[key] = val
                # ATTENTION : la clé 'flag_values' peut se terminier par ':<fmt>'.
                if key.startswith('flag_values'):
                    if '"' in val:
                        logger.error(f"section {name:15s} : caractères " +\
                                     f"inattendus (\") dans : " +\
                                     f"{key} = {val}")
                        val = re.sub('"', '', val)

                    self.config[key] = np.array(re.split(r'[,\s\t]+', val))
                    for item in self.config[key]:
                        if len(item) == 0:
                            logger.error(f"section {name:15s} : la valeur " +\
                                         f"pour {key} est sans doute " +\
                                         f"mal-formée ({self.config[key]})")
                            break

        # si le vecteur n'est pas a chercher dans le fichier de selection (il
        # ne contient pas ${xxxx}), tentative de récupération du standard_name
        if not '${' in self.config['origin']:
            if self.config['standard_name'] is None:
                self.config['standard_name'] = AIDA_name_to_CF_name(self.config['origin'])

            if self.config['standard_name'] is None:
                logger.warning(f"section {name:15s} : pas de 'standard_name' ({self.config['origin']})")

        # check de cohérence pour les flag_values / flag_meanings (le
        # standard name peut ne pas avoir été postionné à 'status_flag')
        # ATTENTION : la clé 'flag_values' peut se terminier par ':<fmt>'.
        #             => trouver la liste des clés dont le nom commence pa
        #                'flag_values'
        flag_values_key = [ k for k in self.config.keys() if k.startswith('flag_values') ]
        if len(flag_values_key) > 1:
            raise Exception(f"section {name:15s} : plusieurs options dont " +\
                            f"le nom commence par 'flag_values' : " +\
                            f"{flag_values_key})")

        given_flag_values   =  len(flag_values_key) == 1
        given_flag_meanings = 'flag_meanings' in self.config.keys()

        # les options 'flag_values' et 'flag_meanings' :
        # - doivent être données toutes les 2 ou
        # - ne doivent pas être données ni l'une, ni l'autre
        if given_flag_values != given_flag_meanings:
            raise Exception(f"section {name:15s} : il manque 'flag_values' " +\
                            f"ou 'flag_meanings'")

        # si les 2 options sont données :
        if given_flag_values and given_flag_meanings:

            # les options 'flag_values' et 'flag_meanings' doivent contenir
            # le même nombre de valeur
            nb_flag_values   = len(self.config[flag_values_key[0]])
            nb_flag_meanings = len(re.split(r'[ \t]+', self.config['flag_meanings']))
            if nb_flag_values != nb_flag_meanings:
                raise Exception(f"section {name:15s} : 'flag_values' et " +\
                                f"'flag_meanings' n'ont pas le même nombre " +\
                                f"de valeurs ({nb_flag_values} et " +\
                                f"{nb_flag_meanings})")

            ### TODO : je n'ai pas compris dans https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#flag-variable-flag-values-ex
            ### ce que voulait dire :
            ###    The use of this modifier is deprecated and the
            ###    standard_name status_flag is preferred to describe
            ###    this type of metadata variable.
            ### => peut-être qu'il ne faut pas faire ce test...
            # le 'standard_name' devrait être 'status_flag'
            if self.config['standard_name']:
                if not 'status_flag' in self.config['standard_name']:
                    print(f":::: FAUT-IL FAIRE CE TEST ?")
                    logger.warning(f"section {name:15s} : 'standard_name' " +\
                                   f"ne contient pas 'status_flag'")

        return


    def show_me(self):
        """ Debug
        """
        print(f"--- {self.name}")

        print("  - config")
        for key, val in self.config.items():
            print(f"    - {key} = {val}")

        print("  - attrs")
        for key, val in self.attrs.items():
            print(f"    - {key} = {val}")

        print("  - data")
        if not self.data is None:
            print(f"    - [0:5] = {self.data[0:5]} ..")
            print(f"    - [-5:] = {self.data[-5:]}")

        print(f"  - source        = {self.source}")


    def CF_compliency(self, name):
        """ log un warning si le nom de la variable 'name' n'est pas conforme
            à la norme CF (qui accepte les lettres, nombres, et underscore...)

            :param str() name: nom du paramètre NetCDF.

            :return: le nom reçu en argument.
            :rtype : str()
        """
        logger.log(logging.RUN, f"Param::CF_compliency({name})")

        def not_CF_complient(name):
            logger.warning(f"'{name}' : n'est pas un nom de variable conforme CF")
            logger.warning("(voir #2.3 sur https://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html")

        err     = 0
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        name_u  = name.upper()

        if name_u[0] not in letters:
            not_CF_complient(name)
            return name

        for c in name_u[1:]:
            if not ( (c.isdigit() or (c in letters) or c == '_') ):
                not_CF_complient(name)
                return name

        return name


    def get_ancillary(self):
        """ Retourne le contenu de l'option 'ancillary_variables' si elle est
            positionnée pour le paramètre, sinon None

            :return: le contenu de l'option 'ancillary_variables' ou None
            :rtype : str() ou None
        """
        logger.log(logging.RUN, "Param::get_ancillary")

        if 'ancillary_variables' in self.config.keys():
            return self.config['ancillary_variables']
        else:
            return None


    def get_from_selector(self, choix, option, update_infos=False):
        """ Retourne la valeur pour 'choix' trouvée dans le fichier de
            selection pour l'acqid fourni.

            Si update_infos = True, initialise le standard_name (normalement,
            update_infos est postionné à True seulement si 'choix' est une
            recherche de nom de vecteur).

            :param str() choix  : chaîne contenant des champ ${section}
            :param str() option : option de la section
                                  ([section] option = value).
        """
        logger.log(logging.RUN, f"Param::get_from_selector(self, {choix}, {option})")

        ret_value = choix
        if self.selector:
            try:
                ret_value = self.selector.get_value(choix, option)
            except Exception as e:
                raise Exception (e)


        # mise à jour d'infos
        if update_infos:
            # recherche du standard_name
            if self.config['standard_name'] is None:
                self.config['standard_name'] = AIDA_name_to_CF_name(ret_value)

            if self.config['standard_name'] is None:
                logger.warning(f"section {self.name} : pas de " +\
                               f"'standard_name' pour " +\
                               f"({self.config['origin']})")
            # reset de la source (qui sera cherchée à chaque acqid
            # => on pourrait faire mieux...)
            self.source = None

        logger.debug(f"get_from_selector : return {ret_value}")

        return ret_value


    def set_attrs_from_header(self, hdr):
        """ Mémorise les attributs du header qui impactent le fichier NetCDF.

            :param dict() hdr: contenu du header du vecteur
        """
        logger.log(logging.RUN, "Param::set_attrs_from_header")

        attrs = [ 'dim_array'   ,
                  'format'      ,
                  'freq_ech'    ,
                  'misval'      ,
                  'unit'        ,
                  'bornes'      ,
                  'unit_bornes' ,
                  'valid_min'   ,
                  'valid_max'   ,
                  'valid_range' ,
                  'comment'     ,
                  'obs_min'     ,
                  'obs_max'     ,
                ]

        for attr in attrs:
            if attr in hdr.keys():
                self.attrs[attr] = hdr[attr]

                # si besoin, forcer degree_north / degree_east
                if attr == 'unit':
                    if self.config['standard_name'] == 'latitude':
                        self.attrs[attr] = 'degree_north'
                    elif self.config['standard_name'] == 'longitude':
                        self.attrs[attr] = 'degree_east'

        return


    def append_data(self, data):
        """ Ajoute les données du vecteur au data déjà mémorisées.

            :param np.array() data: data du vecteur
        """
        logger.log(logging.RUN, "Param::append_data")

        if self.data is None:
            self.data = data
        else:
            self.data = np.append(self.data, data, axis=0)


    def get_min_max(self):
        """ Renvoit les valeurs min et max des data.

            TODO
        """
        logger.log(logging.RUN, "Param::get_min_max")

        obs_min, obs_max = AIDA.compute_obs_min_max(self.attrs, self.data)

        # la verson historique traitait en float64...
        return np.float64(obs_min), np.float64(obs_max)


def get_params_from_config(config_parser, selector):
    """ Retourne un dictionnaire des tous les paramètres décrits dans le
        fichier de configuration.

        :params configparser() config_parser: contenu du fichier de confiration.
        :params configparser() selector     : contenu du fichier de sélection
                                              de vecteurs.

        :return: le dictionnaire des tous les paramètres décrits dans le
                 fichier de configuration :
                 - clé    = nom du paramètre
                 - valeur = objet Param

        :retype: dict()
    """
    logger.log(logging.RUN, "get_params_from_config")

    # la liste des paramètres décrits est la liste des section sans les
    # sections qui ne d"écrivent pas des paramètres (yeah !)
    param_names = config_parser.sections()
    param_names.remove('DIRECTIVES')
    param_names.remove('GENERAL')
    if 'METADATA_AERIS' in param_names:
        param_names.remove('METADATA_AERIS')

    # enregistrement des objets paramètres et leur configuration dans
    # params.
    params = dict()
    for param in param_names :
        try:
            params[param] = Param(param,
                                  selector,
                                  **dict(config_parser.items(param)))
        except Exception as e:
            logger.error(f"problème de configuration :\n --> {e}")

    return params

