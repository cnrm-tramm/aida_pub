#!/usr/bin/env python3

"""
Production de fichier NetCDF à partir de fichiers-vecteurs
==========================================================

  Gestion du fichier de configuration.
"""

import sys
import os
import logging
import re
import configparser

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

logger = logging.getLogger('prod_CDF')

geospatial_keys = [ 'geospatial_lat_min'          ,
                    'geospatial_lat_max'          ,
                    'geospatial_lat_units'        ,
                    'geospatial_lon_min'          ,
                    'geospatial_lon_max'          ,
                    'geospatial_lon_units'        ,
                    'geospatial_vertical_min'     ,
                    'geospatial_vertical_max'     ,
                    'geospatial_vertical_units'   ,
                    'geospatial_vertical_positive',
                  ]

class Config:
    """ Gestion du fichier de configuration.
    """

    def __init__(self, parser, defaults={}):
        """
        :param configparser()  parser   : contenu du fichier de
                                          configuration.
        :param dict()          defaults : dictionnaire des valeurs lues
                                          dans le fichier de configuration
                                          par défaut.
        """
        logger.log(logging.RUN, f"Config::__init__: defaults = {defaults}")

        self.directives = dict()
        self.general    = dict()

        # enregistrer les valeurs par défaut
        self.general.update(defaults)

        for section in ['DIRECTIVES', 'GENERAL']:
            if not section in parser.sections():
                raise Exception (f"Defaults::__init__ : '{parser.filename}' : " +\
                                 f"pas de section : '{section}'")

        self.directives = dict(parser.items('DIRECTIVES'))
        self.general.update(dict(parser.items('GENERAL')))

        # récupérer d'éventuelles clé geospatial_XXX (il eut été préférable
        # d'imposer une section scpéciale...)
        self.geos = dict()
        for key in geospatial_keys:
            if key in self.general.keys():
                if key.endswith('min') or key.endswith('max'):
                    self.geos[key] = float(self.general[key])
                else:
                    self.geos[key] = self.general[key]
                del self.general[key]

        self.parser = parser


    def show_me(self, part=None):
        """ Debug
        """
        def show_me_directives(self):
            print( "Config.directives :")
            for key, value in self.directives.items():
                print(f"- {key:25s} = {value}")


        def show_me_general(self):
            print( "Config.general :")
            for key, value in self.general.items():
                print(f"- {key:25s} = {value}")


        def show_me_geos(self):
            print( "Config.geos :")
            for key, value in self.geos.items():
                print(f"- {key:25s} = {value}")


        if part == 'directives':
            show_me_directives(self)
        elif part == 'general':
            show_me_general(self)
        elif part == 'geos':
            show_me_geos(self)
        else:
            show_me_directives(self)
            show_me_general(self)
            show_me_geos(self)

        return


    def check_directives(self):
        """ Vérification des options de la section DIRECTIVES.
        """
        logger.log(logging.RUN, "Config::check_directives")

        section   = 'DIRECTIVES'
        mandatory = [ 'prefix'    ,
                      'plateforme',
                      'reftime'   ,
                      'mode'      ,
                    ]
        optional  = { 'date_format'           : '%Y%m%d'    ,
                      'replace_missing_vector': 'False'     ,
                      'datation_convention'   : 'fin'       ,
                      'dimensions'            : 'Unlimited' ,
                    }

        for key in mandatory:
            if not key in self.directives.keys():
                raise Exception (f"section {section} : absence de l'option '{key}'")

        for key in optional.keys():
            if not key in self.directives.keys():
                self.directives[key] = optional[key]
                logger.info(f"section {section} : valeur par défaut : " +\
                            f"'{key} = {self.directives[key]}'")

        # vérifications
        # mode
        value     = self.directives['mode']
        available = ['jour', 'periode', 'mobile']
        if value not in available:
            raise Exception (f"section {section} : "+\
                             f"valeur incorrecte : 'mode = {value}' " +\
                             f"(valeur possible : {available})")

        # datation_convention
        value     = self.directives['datation_convention']
        available = ['debut', 'milieu', 'fin']
        if value not in available:
            raise Exception (f"section {section} : " +\
                             f"valeur incorrecte : 'datation_convention = {value}' " +\
                             f"(valeur possible : {available})")

        # dimensions
        value     = self.directives['dimensions']
        available = ['Limited', 'Unlimited']
        if value not in available:
            raise Exception (f"'{self.parser.filename}' : " +\
                             f"valeur incorrecte : 'dimensions = {value}' " +\
                             f"(valeur possible : {available})")

        self.mode = self.directives['mode']

        return


    def check_contributor_name(self):
        """ Vérification le formalisme de l'option 'contributor_name' de la
            section GENERAL.

            :return: le nombre de 'contributor_name'.
        """
        logger.log(logging.RUN, "Config::check_contributor_name")

        contributor_name = self.general['contributor_name']
        parts = re.split(r'[;\n]+', contributor_name)
        for part in parts:
            if not part:
                continue

            fields = re.split(r'[:]+', part)
            if len(fields) != 4:
                logger.warning(f"section GENERAL : option 'contributor_name' : " +\
                        f"'{part}' devrait contenir " +\
                         "'prenom:nom:email:institution'")

        return len(parts)


    def check_contributor_role(self):
        """ Vérification les rôles de l'option 'contributor_role' de la section
            GENERAL.

            :return: le nombre de 'contributor_role'.
        """
        logger.log(logging.RUN, "Config::check_contributor_role")

        roles = [ 'owner'                 ,
                  'funder'                ,
                  'sponsor'               ,
                  'editor'                ,
                  'coauthor'              ,
                  'custodian'             ,
                  'pointofcontact'        ,
                  'author'                ,
                  'principalinvestigator' ,
                  'originator'            ,
                  'distributor'           ,
                  'processor'             ,
                  'stakeholder'           ,
                  'collaborator'          ,
                  'contributor'           ,
                  'metadatapointofcontact',
                  'resourceprovider'      ,
                  'publisher'             ,
                  'mediator'              ,
                  'user'                  ,
                  'rightsholder'          ,
                  'metadatapointofcontact',
                ]

        contributor_role = self.general['contributor_role']
        parts = re.split(r'[;:\s\t]+', contributor_role)
        for part in parts:
            if part and not part in roles:
                logger.warning(f"section GENERAL : option 'contributor_role' : " +\
                               f"role invalide : '{part}'")
        return len(parts)


    def check_general(self):
        """ Vérification des options de la section GENERAL.
        """
        logger.log(logging.RUN, "Config::check_general")

        section      = 'GENERAL'

        defaults     = { 'Conventions'         : 'CF-1.8, ACDD-1.3'      ,
                         'keywords_vocabulary' : 'GCMD Science Keywords' ,
                         ### pas de data_policy par défaut !'data_policy'         : 'ACTRIS-FR data policy' ,
                         'data_policy'         : ''                      ,
                         'processing_level'    : 'L2'                    ,
                       }
        mandatory    = [ 'title'              ,
                         'summary'            ,
                         'keywords'           ,
                         'Conventions'        ,
                         'keywords_vocabulary',
                         'data_policy'        ,
                         'doi'                ,
                         'creator_name'       ,
                       ]
        ignored      = [ 'product_version'    ,
                       ]
        recommended  = [ 'creator_institution',
                         'creator_email'      ,
                         'institution'        ,
                         'project'            ,
                         'comment'            ,
                         'history'            ,
                       ]

        for key in defaults.keys():
            if not key in self.general.keys():
                self.general[key] = defaults[key]
                logger.info(f"section {section} : valeur par défaut : " +\
                            f"{key} = {self.general[key]}")

        for key in mandatory:
            if not key in self.general.keys():
                logger.error(f"section {section} : absence de l'option '{key}'")
                continue
            if len(self.general[key]) == 0:
                logger.warning(f"section {section} : pas de valeur pour " +\
                               f"l'option '{key}'")

        for key in ignored:
            if key in self.general.keys():
                logger.error(f"section {section} : option ignorée '{key}'")
                del self.general[key]

        for key in recommended:
            if not key in self.general.keys():
                logger.warning(f"section {section} : pas d'option '{key}'")
                continue
            if len(self.general[key]) == 0:
                logger.warning(f"section {section} : pas de valeur pour " +\
                               f"l'option '{key}'")

        nb_name = None
        if 'contributor_name' in self.general.keys():
            nb_name = self.check_contributor_name()

        nb_role = None
        if 'contributor_role' in self.general.keys():
            nb_role = self.check_contributor_role()

        if nb_name and nb_role and nb_name != nb_role:
            logger.warning(f"section {section} : incohérence entre " +\
                           f"nombre de 'contributor_name' ({nb_name}) et " +\
                           f"nombre de 'contributor_role' ({nb_role})")
            ...


        try:
            self.trajectory = self.general['coordinates']
        except Exception as e:
            self.trajectory = None

        if self.mode == 'mobile' and self.trajectory == None:
            logger.warning(f"section {section} : mode 'mobile' et " +\
                            "option 'coordinate' absente " +\
                            "=> pas d'informations automatiques pour 'geospatial_XXX'")

        return


    def check_project(self, acqid):
        """ Si l'option 'project' n'est pas fournie dans le fichier de
            configuration, tente de l'initialiser avec l'option 'campagne' du
            fichier .inf de l'acqid reçu.
        """
        logger.log(logging.RUN, f"Config::check_project({acqid})")

        project = self.general.get('project', None)
        if project:
            return

        logger.warning(f"l'option 'project' n'est pas positionnée")

        inf_acqid = AIDA.Inf(acqid)
        campagne = inf_acqid.get_field_value('IDENTIFICATION', 'campagne')

        if campagne:
            self.general['project'] = campagne
            logger.warning(f"l'option 'project' est forcée à : '{campagne}'")
        else:
            logger.error(f"l'option 'campagne' n'est pas trouvée dans {acqid}.inf")

