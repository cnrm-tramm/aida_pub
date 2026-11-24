#!/usr/bin/env python3

"""
Production de fichier NetCDF à partir de fichiers-vecteurs
==========================================================

  Gestion du fichier de selection de vecteur en fonction d'acqids.

  Format du fichier :
    [choix_XXX]
    default                        = valeur par défaut                # obligatoire
    default_cmt                    = commentaire du choix par défaut  # obligatoire

    <acqid>                        = valeur pour cet acqid
    <acqid>_cmt                    = commentaire pour cet <acqid>

    <acqid_first>-<acqid_last>     = valeur      pour tous les acqids appartenant à [acqid_first, acqid_last]
    <acqid_first>-<acqid_last>_cmt = commentaire pour tous les acqids appartenant à [acqid_first, acqid_last]

    <acqid_first>-*                = valeur      pour tous les acqids à partir de acqid_first
    <acqid_first>-*_cmt            = commentaire pour tous les acqids à partir de acqid_first

"""

import sys
import os
import logging
import re
import configparser

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AcqId

logger = logging.getLogger('prod_CDF')


class Selector:
    """ Gestion du fichier de selection de vecteur en fonction d'acqids.
    """

    def __init__(self, file):
        """
        :param str()  file : path du fichier de selection.
        """
        logger.log(logging.RUN, f"Selector::__init__: file = {file}")

        self.file    = file
        self.content = self.init_from_file()


    def show_me(self):
        """ Debug
        """
        print( "Selector :")
        for choix, options in self.content.items():
            print(f"{choix} :")
            for option, value in options.items():
                print(f"  - {option:25s} = {value}")

        return


    def init_from_file(self):
        """ A partir du contenu du fichier de selection, crée un dictionnaire
            de dicitionnaire des choix. La forme de ce dictionnaire est :
              {
               'choix_X' = {
                  'option_1': {
                    'first'  : l'objet AcqId() du premier acqid de la liste
                    'last'   : l'objet AcqId() du dernier acqid de la liste
                               (la valeur de 'last' = la valeur de 'first' pour
                                les acqids unique)
                    'value  ': valeur pour cette liste
                    'comment': commentaire pour cette liste
                  }
               }
               'choix_X' = {
               ...
               }
              }
            NOTE : on passe par la class AcqId() pour pouvoir faire des
                   comparaison entre l'acqid à chercher et les listes d'acqids.
        """
        # test de l'existance du fichier
        if not os.path.isfile(self.file):
            raise Exception(f"le fichier de sélection pour les paramètres " +\
                            f"'{self.file}' n'existe pas")

        # lecture du fichier dans un dictionnaire
        # (optionxform : obliger configparser à ne pas modifier la case des options)
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        parser.read(self.file)
        d_in = { section:dict(parser.items(section))
                    for section in parser.sections() }

        # construction du dictionnaire de sortie
        d_out = dict()

        # étude de d_in pour génération du d_out
        for section in d_in.keys():

            # vérifier que les options obligatoires sont présentes
            for opt in [ 'default', 'default_cmt' ]:
                if not opt in d_in[section].keys():
                    raise Exception(f"absence de l'option '{opt}' " +\
                                    f"pour la section '{section}' " +\
                                    f"dans le fichier '{self.file}'")

            # création de la section dans le dictionnaire de sortie
            d_out[section] = dict()

            # analyser les options
            for option, value in d_in[section].items():
                # le commentaire sera traité au moment de l'option elle-même
                if option.endswith('_cmt'):
                    continue

                # récupérer le commentaire
                comment = None
                option_cmt = f"{option}_cmt"
                if option_cmt in d_in[section].keys():
                    comment = d_in[section][option_cmt]
                else:
                    logger.warning(f"absence de l'option '{option_cmt}' " +\
                                   f"pour la section '{section}' " +\
                                   f"dans le fichier '{self.file}'")

                # analyse de l'option de la forme "liste d'acqid" ou
                # "acqid simple" pour trouver first et last
                if '-' in option:
                    first, last = option.split('-')
                else:
                    first = last = option


                # si first et last sont des acqid, passer par la class AcqId
                # sinon garder leur valeur
                if first.startswith('default'):
                    acqid_first = first
                else:
                    acqid_first = AcqId.AcqId(first)

                if last == '*' or last.startswith('default'):
                    acqid_last = last
                else:
                    acqid_last = AcqId.AcqId(last)

                d_out[section][option] = {'first'  : acqid_first,
                                          'last'   : acqid_last,
                                          'value'  : value,
                                          'comment': comment}

        return d_out


    def get_value(self, choix, acqid):
        """ Retourne la valeur de la section 'choix' pour l'acqid 'acqid'.
        """
        logger.log(logging.RUN, f"Selector::get_value({choix}, {acqid})")

        if not choix:
            return choix

        if not '$' in str(choix):
            return choix

        val = choix

        # choix est un mot qui contient des ${section}
        pattern   = r'(?P<section>\${.*?})'
        ret_value = choix

        # liste des ${xxx} trouvées dans 'choix'
        sections = re.findall(pattern, choix)

        for section in set(sections):
            # la section sans ${}
            section_name = section[2:-1]

            # si la section contient '_cmt', on retournera la clé 'comment',
            # sinon la clé 'value' mais la section est le nom sans '_cmt'
            wanted_key = 'value'
            if section_name.endswith('_cmt'):
                wanted_key = 'comment'
                section_name = section_name.replace('_cmt', '')

            # récupérer le self.content de la section
            if section_name in self.content.keys():
                d_section = self.content[section_name]
            else:
                raise Exception(f"la section '[{section_name}]' " +\
                                f"pour le choix '{choix}' " +\
                                f"n'existe pas dans le fichier '{self.file}'")

            # chercher l'acqid dans les clés de la section
            if acqid in d_section.keys():
                # acqid est une clé de la section : <acqid> = value
                val = val.replace(section, f'{d_section[acqid][wanted_key]}')
            else:
                # chercher acqid dans les clés qui sont des listes
                found = False
                for liste in [ k for k in d_section.keys() if '-' in k ]:
                    # pour faire la comparaison, il faut passer par la class AcqId
                    obj_AcqId = AcqId.AcqId(acqid)
                    if obj_AcqId >= d_section[liste]['first']:
                        if isinstance(d_section[liste]['last'], str): # vaut '*'
                            val = val.replace(section, f"{d_section[liste][wanted_key]}")
                            found = True
                        elif obj_AcqId <= d_section[liste]['last']:
                            val = val.replace(section, f"{d_section[liste][wanted_key]}")
                            found = True
                    if found:
                        break


                if not found:
                    # acqid n'apas été trouvé => on prend la valeur par défaut
                    val = val.replace(section, f"{d_section['default'][wanted_key]}")

        return val


if __name__ == '__main__':

    import AIDA_logger
    logger = AIDA_logger.configure_AIDA_logging('prod_CDF')

    # création d'un fichier de selection pour tests
    file = '/tmp/test_selector'
    config = configparser.ConfigParser(interpolation=None)
    # obliger configparser à ne pas modifier la case des options
    config.optionxform = str
    config['instru'] = {
                'default'               : 'instru_default'                         ,
                'default_cmt'           : 'commentaire de instru_default'          ,

                'Tf230002'              : 'instru_tf230002'                        ,
                'Tf230002_cmt'          : 'commentaire de instru_tf230002'         ,

                'Tf230003-Tf230004'     : 'instru_tf230003-tf230004'               ,
                'Tf230003-Tf230004_cmt' : 'commentaire de instru_tf230003-tf230004',

                'Tf230012-*'            : 'instru_tf230012-*'                      ,
                'Tf230012-*_cmt'        : 'commentaire de instru_ff230012-*'       ,
    }
    config['freq'] = {
                'default'               : 'freq_default'                            ,
                'default_cmt'           : 'commentaire de freq_default'             ,

                'Tf210001'              : 'FREQ_TF210001'                           ,
                #'Tf210001_cmt'          : 'COMMENTAIRE DE FREQ_TF210001'         ,

                'Tf230011'              : 'FREQ_TF230011'                           ,
                'Tf230011_cmt'          : 'COMMENTAIRE DE FREQ_TF230011'         ,
    }

    with open(file, 'w') as handler:
        config.write(handler)


    # tests
    try:
        selector = Selector(file)
    except Exception as e:
        print(f"ERREUR : {e}")
        sys.exit(1)

    print('\n')
    selector.show_me()
    print('\n')

    ccdf_file = {'long_name': 'lat ${instru}',
                 'origin'   : 'pos_lat_${instru}_${freq}',
                 'comment'  : '${instru_cmt} ET ${freq_cmt}',
                 'autre'    : '${erreur} ET ${freq_cmt}',
                }

    for acqid in [            'Tf230001', 'Tf230002', 'Tf230003', 'Tf230004',
                  'Tf230010', 'Tf230011', 'Tf230012', 'Tf230013', 'Tf230014'] :
        print(f"=== acqid = {acqid}")

        for k, v in ccdf_file.items():
            try:
                val = selector.get_value(v, acqid)
                print(f"      {k:10s} = {v:40s} -> {val}")
            except Exception as e:
                print(f"ERREUR : {e}")
        input('...')
