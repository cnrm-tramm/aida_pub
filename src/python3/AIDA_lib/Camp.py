#!/usr/bin/env python3

"""
Gestion des fichiers .camp.
"""

import os
import sys
import datetime
import configparser
import re
import subprocess

from string    import Template
from textwrap  import dedent

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
import AcqId

from fct_messages import (info, warning, stop_error, result, wait_user)


# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]

# valeurs par défaut de date
_DEF_dt_debut   = datetime.datetime.today()
_DEF_dt_fin     = datetime.datetime(1900,1,1,0,0,0,0)
_DEF_date_debut = _DEF_dt_debut.strftime("%d/%m/%Y")
_DEF_date_fin   = _DEF_dt_fin.strftime("%d/%m/%Y")


class Camp_comp:
    """ Classe statique de comparaison des valeurs de 2 campagnes.
    """

    @classmethod
    def get_str(cls, prev, new):
        """ Retourne la valeur la plus adaptée entre `prev` et `new` (:-D) :
            `new` est privilégiée à `prev`

            :param str prev: chaîne à tester.
            :param str new:  chaîne à tester.

            :return: la chaîne la plus adaptée.
            :rtype:  str
        """
        if new is None or len(new) == 0:
            return prev

        if prev == new:
            return new

        if prev != new:
            return new


    @classmethod
    def get_date_min(cls, prev, new):
        """ Retourne la date minimale entre `prev` et `new`.

            :param str prev: date à tester sous la forme 'jj/mm/aaaa'.
            :param str new:  date à tester sous la forme 'jj/mm/aaaa'.

            :return: la plus petite des dates fournies.
            :rtype:  str
        """
        dt_prev = datetime.datetime.strptime(prev, "%d/%m/%Y")
        dt_new  = datetime.datetime.strptime(new , "%d/%m/%Y")
        if dt_prev < dt_new:
            return prev
        else:
            return new


    @classmethod
    def get_date_max(cls, prev, new):
        """ Retourne la date maximale entre `prev` et `new`.

            :param str prev: date à tester sous la forme 'jj/mm/aaaa'.
            :param str new:  date à tester sous la forme 'jj/mm/aaaa'.

            :return: la plus grande des dates fournies.
            :rtype:  str
        """
        if new == 'running':
            return new

        dt_prev = datetime.datetime.strptime(prev, "%d/%m/%Y")
        dt_new  = datetime.datetime.strptime(new , "%d/%m/%Y")
        if dt_prev > dt_new:
            return prev
        else:
            return new


    @classmethod
    def get_region(cls, prev, new):
        """ TODO : ça se compare comment ?
            Retourne `new`.

            :param str prev: région à tester...
            :param str new:  région à tester...

            :return: la région `new`...
            :rtype:  str
        """
        return new


    @classmethod
    def get_un_m49_code(cls, prev, new):
        """ TODO : ça se compare comment ?
            Retourne `new`.

            :param str prev: code `un_m49` à tester.
            :param str new:  code `un_m49` à tester.

            :return: le code `un_m49` `new`...
            :rtype:  str
        """
        return new


    @classmethod
    def get_coord_min(cls, prev, new):
        """ Retourne la coordonnée minimale entre `prev` et `new`.

            :param float prev: coordonnée à tester.
            :param float new:  coordonnée à tester.

            :return: la plus petite des coordonnées fournies.
            :rtype:  float
        """
        s_prev = str(prev)
        s_new  = str(new )
        if s_prev is None or len(s_prev) == 0:
            return new

        if s_new is None or len(s_new) == 0:
            return prev

        if s_prev == s_new:
            return new

        f_prev = float(cls, prev)
        f_new  = float(new )
        if f_prev < f_new:
            return prev
        else:
            return new


    @classmethod
    def get_coord_max(cls, prev, new):
        """ Retourne la coordonnée maximale entre `prev` et `new`.

            :param float prev: coordonnée à tester.
            :param float new:  coordonnée à tester.

            :return: la plus grandes des coordonnées fournies.
            :rtype:  float
        """
        s_prev = str(prev)
        s_new  = str(new )
        if s_prev is None or len(s_prev) == 0:
            return new

        if s_new is None or len(s_new) == 0:
            return prev

        if s_prev == s_new:
            return new

        f_prev = float(prev)
        f_new  = float(new )
        if f_prev > f_new:
            return prev
        else:
            return new


    @classmethod
    def merge_liste_acqid(cls, prev, new):
        """ Retourne la liste de tous les acqids de `prev` et `new`.

            :param str prev: liste compacte d'acqid à fusionner.
            :param str new:  liste compacte d'acqid à fusionner.

            :return: la liste exhaustive résultat de la fusion des 2 listes
                     compactes fournies.
            :rtype:  list
        """
        e_prev  = expand_acqids_pltf(prev)
        e_new   = expand_acqids_pltf(new)
        return sorted(set(e_prev)|set(e_new))


class Pltf:
    """ Gestion des plateformes de la campagnes.
    """
    def __init__(self, **kwargs):
        """
            :param dict kwargs: dictionnanire d'attributs de la plateforme.

            kwargs contient un dictionnaire de tous les attributs possibles
            pour la plateforme.
            Il *doit* contenir une clé 'nom': <nom long de la plateforme>.
        """
        self.nom                    = kwargs.get('nom')
        self.date_debut             = kwargs.get('date_debut' , _DEF_date_debut)
        self.date_fin               = kwargs.get('date_fin'   , _DEF_date_fin)
        self.acqids                 = []
        l                           = kwargs.get('liste_acqid', None)
        self.principal_investigator = kwargs.get('principal_investigator', '')

        # vérification
        if self.nom is None:
            raise Exception ("Pltf::__init__ : pas de nom : {d}".
                    format(d=kwargs))

        if not self.nom in AIDA.plt_by_name:
            raise Exception ("Pltf::__init__ : '{n}' doit être un nom long".
                    format(n=self.nom))

        if l:
            self.acqids = expand_acqids_pltf(l)

        # handlers de comparaison des valeurs des options (pour la gestion des
        # mises à jour)
        self.handler_comp = {
                'nom'                    : Camp_comp.get_str          ,
                'date_debut'             : Camp_comp.get_date_min     ,
                'date_fin'               : Camp_comp.get_date_max     ,
                'liste_acqid'            : Camp_comp.merge_liste_acqid,
                'principal_investigator' : Camp_comp.get_str          ,
               }

        # gestion des dates pour la plateforme
        self._dt_debut = datetime.datetime.strptime(self.date_debut, "%d/%m/%Y")
        if self.date_fin != 'running':
            self._dt_fin = datetime.datetime.strptime(self.date_fin, "%d/%m/%Y")

        return


    def _to_dict(self):
        """ Retourne les attributs de la plateforme sous forme d'un
            dictionnaire.
            Les clés de ce dictionnaires sont les noms des options d'une
            section [_plateforme_] d'un fichier .camp.
        """
        return {'nom'                    : self.nom,
                'liste_acqid'            : compact_acqids_pltf(self.acqids),
                'date_debut'             : self.date_debut,
                'date_fin'               : self.date_fin,
                'principal_investigator' : self.principal_investigator,
               }


    def set_values(self, **kwargs):
        """ Initialise les attributs de la plateforme avec les valeurs du
            dictionnaire passé en argument.
            Les clés de ce dictionnaires sont les noms des options de la
            section [_plateforme_] d'un fichier .camp.
        """
        if kwargs.get('nom'):
            self.nom                    = kwargs.get('nom')

        if kwargs.get('date_debut'):
            self.date_debut             = kwargs.get('date_debut')

        if kwargs.get('date_fin'):
            self.date_fin               = kwargs.get('date_fin')

        if kwargs.get('liste_acqid'):
            self.acqids                 = kwargs.get('liste_acqid')

        if kwargs.get('principal_investigator'):
            self.principal_investigator = kwargs.get('principal_investigator')

        return


    def show_me(self):
        """ Debug...
        """
        print('    - plateforme :', self.nom)
        print('      - date_debut =', self.date_debut)
        print('      - date_fin   =', self.date_fin  )
        print('      - acqids     =', self.acqids    )


    def add_acqid(self, acqid, date):
        """ Ajoute un acqid à la liste des acqids.

            :param str acqid: valeur de l'acqid.
            :param str date: date sous la forme 'jj/mm/aaaa'.

            :return: datetime de la date fournie.
            :rtype: datetime
        """
        self.acqids.append(acqid)

        # mise à jour des champs 'date_debut' et 'date_fin'
        dt_date = datetime.datetime.strptime(date, "%d/%m/%Y")

        if dt_date < self._dt_debut:
            self._dt_debut  = dt_date
            self.date_debut = date
        if dt_date > self._dt_fin:
            self._dt_fin    = dt_date
            self.date_fin   = date

        return dt_date


    def update(self, other):
        """ Mise à jour de la plateforme avec les valeurs de 'other' si besoin.

            :param Pltf other: objet Pltf.
        """
        # récupérer les 2 plateformes sous forme de dictionnaire
        me_dict    = self._to_dict()
        other_dict = other._to_dict()

        # mettre à jour le dictionnaire de la plateforme
        for opt, val in me_dict.items():
            me_dict[opt] = self.handler_comp[opt](val, other_dict[opt])

        # mettre à jour les attributs de la plateforme
        self.set_values(**me_dict)

        return


class Campagne():
    """ Classe de gestion des meta-données de campagne.
    """
    # attibuts de classe
    # extension des fichiers .camp
    ext_camp = '.camp'
    # répertoire des fichiers .camp
    dir_camp = os.path.join(AIDA.AIDA_getenv('meta'), 'campagnes')

    # templates de construction d'un fichier .camp
    identification_tpl = """\
            [IDENTIFICATION]
            nom                    = $nom
            date_debut             = $date_debut
            date_fin               = $date_fin
            projet                 = $projet
            region_geographique    = $region_geographique
            un_m49_code            = $un_m49_code
            geospatial_lat_min     = $geospatial_lat_min
            geospatial_lat_max     = $geospatial_lat_max
            geospatial_lon_min     = $geospatial_lon_min
            geospatial_lon_max     = $geospatial_lon_max
            description            = $description
            principal_investigator = $principal_investigator
    """

    plateforme_tpl = """\
            [$nom]
            liste_acqid            = $liste_acqid
            date_debut             = $date_debut
            date_fin               = $date_fin
            principal_investigator = $principal_investigator
    """


    def __init__(self, **kwargs):
        """
            :param dict kwargs: dictionnanire d'attributs de la campagne.

            kwargs contient un dictionnaire de tous les attributs possibles
            pour la campagne.
            Il *doit* contenir une clé 'nom': <nom de la campagne>.
        """
        self.nom                    = kwargs.get('nom')
        self.date_debut             = kwargs.get('date_debut'            ,
                                                             _DEF_date_debut)
        self.date_fin               = kwargs.get('date_fin'              ,
                                                             _DEF_date_fin)
        self.projet                 = kwargs.get('projet'                , '')
        self.region_geographique    = kwargs.get('region_geographique'   , '')
        self.un_m49_code            = kwargs.get('un_m49_code'           , '')
        self.geospatial_lat_min     = kwargs.get('geospatial_lat_min'    , '')
        self.geospatial_lat_max     = kwargs.get('geospatial_lat_max'    , '')
        self.geospatial_lon_min     = kwargs.get('geospatial_lon_min'    , '')
        self.geospatial_lon_max     = kwargs.get('geospatial_lon_max'    , '')
        self.description            = kwargs.get('description'           , '')
        self.principal_investigator = kwargs.get('principal_investigator', '')

        # vérification
        if self.nom is None:
            raise Exception ("Campagne::__init__ : pas de nom : {d}".
                    format(d=kwargs))

        # gestion des plateformes
        self.pltfs = {}

        # gestion des dates
        self._dt_debut = datetime.datetime.strptime(self.date_debut, "%d/%m/%Y")
        if self.date_fin != 'running':
            self._dt_fin = datetime.datetime.strptime(self.date_fin, "%d/%m/%Y")

        # handlers de comparaison des valeurs des options (pour la gestion des
        # mises à jour)
        self.handler_comp = {
                'nom'                    : Camp_comp.get_str        ,
                'date_debut'             : Camp_comp.get_date_min   ,
                'date_fin'               : Camp_comp.get_date_max   ,
                'projet'                 : Camp_comp.get_str        ,
                'region_geographique'    : Camp_comp.get_region     ,
                'un_m49_code'            : Camp_comp.get_un_m49_code,
                'geospatial_lat_min'     : Camp_comp.get_coord_min  ,
                'geospatial_lat_max'     : Camp_comp.get_coord_max  ,
                'geospatial_lon_min'     : Camp_comp.get_coord_min  ,
                'geospatial_lon_max'     : Camp_comp.get_coord_max  ,
                'description'            : Camp_comp.get_str        ,
                'principal_investigator' : Camp_comp.get_str        ,
               }


    def _to_dict(self):
        """ Retourne les attributs de la campagne sous forme d'un
            dictionnaire.
            Les clés de ce dictionnaires sont les noms des options de la
            section [IDENTIFICATION] d'un fichier .camp.
        """
        return {'nom'                    : self.nom,
                'date_debut'             : self.date_debut,
                'date_fin'               : self.date_fin,
                'projet'                 : self.projet,
                'region_geographique'    : self.region_geographique,
                'un_m49_code'            : self.un_m49_code,
                'geospatial_lat_min'     : self.geospatial_lat_min,
                'geospatial_lat_max'     : self.geospatial_lat_max,
                'geospatial_lon_min'     : self.geospatial_lon_min,
                'geospatial_lon_max'     : self.geospatial_lon_max,
                'description'            : self.description,
                'principal_investigator' : self.principal_investigator,
               }


    def set_values(self, **kwargs):
        """ Initialise les attributs de la campagne avec les valeurs du
            dictionnaire passé en argument.
            Les clés de ce dictionnaires sont les noms des options de la
            section [IDENTIFICATION] d'un fichier .camp.
        """
        if kwargs.get('nom'):
            self.nom                    = kwargs.get('nom')

        if kwargs.get('date_debut'):
            self.date_debut             = kwargs.get('date_debut')

        if kwargs.get('date_fin'):
            self.date_fin               = kwargs.get('date_fin')

        if kwargs.get('projet'):
            self.projet                 = kwargs.get('projet')

        if kwargs.get('region_geographique'):
            self.region_geographique    = kwargs.get('region_geographique')

        if kwargs.get('un_m49_code'):
            self.un_m49_code            = kwargs.get('un_m49_code')

        if kwargs.get('geospatial_lat_min'):
            self.geospatial_lat_min     = kwargs.get('geospatial_lat_min')

        if kwargs.get('geospatial_lat_max'):
            self.geospatial_lat_max     = kwargs.get('geospatial_lat_max')

        if kwargs.get('geospatial_lon_min'):
            self.geospatial_lon_min     = kwargs.get('geospatial_lon_min')

        if kwargs.get('geospatial_lon_max'):
            self.geospatial_lon_max     = kwargs.get('geospatial_lon_max')

        if kwargs.get('description'):
            self.description            = kwargs.get('description')

        if kwargs.get('principal_investigator'):
            self.principal_investigator = kwargs.get('principal_investigator')

        return


    def show_me(self):
        """ Debug...
        """
        print('  - campagne :', self.nom)
        print('    - date_debut =', self.date_debut)
        print('    - date_fin   =', self.date_fin  )
        print('    - projet     =', self.projet    )
        for pltf in self.pltfs.values():
            pltf.show_me()


    def add_plateforme(self, **kwargs):
        """ Ajoute une plateforme à la campagne.

            kwargs contient un dictionnaire de tous les attributs possibles
            pour la plateforme.
            Il *doit* contenir une clé 'nom': <nom long de la plateforme>.
        """
        nom = kwargs.get('nom')
        self.pltfs[nom] = Pltf(**kwargs)


    def get_plateformes_by_obj(self):
        """
            Generator des plateformes de la campagne.

            :yield: Pltf()
        """
        for pltf in self.pltfs.values():
            yield pltf


    def get_plateformes_by_name(self):
        """ Retourne la liste des noms des plateformes existantes pour cette
            campagne.

            :return: list(nom)
        """
        return [ p for p in self.pltfs.keys() if not p == 'IDENTIFICATION' ]


    def add_plateforme_acqid(self, nom, acqid, date):
        """ Ajoute un acqid à la platefome 'nom'.

            :param str nom: nom de la plateforme.
            :param str acqid: valeur de l'acqid.
            :param str date: date sous la forme 'jj/mm/aaaa'.
        """
        dt_date = self.pltfs[nom].add_acqid(acqid, date)

        # mise à jour des champs 'date_debut' et 'date_fin' pour la *campagne*
        if dt_date < self._dt_debut:
            self._dt_debut  = dt_date
            self.date_debut = date
        if self.date_fin != 'running' and dt_date > self._dt_fin:
            self._dt_fin    = dt_date
            self.date_fin   = date


    @staticmethod
    def load_from_file(name, path=dir_camp):
        """ Charge le contenu du fichier 'name' dans une Campagne().

            :param str name: basename *sans* extension du fichier.
            :param str path: chemin du fichier à charger.
                             Ne devrait être utiliser qu'à des fins de tests
                             pour ne pas polluer le répertoire des campagnes).

            :return: la campagne ou None si le fichier de campagne n'existe pas.
            :rtype: Campagne
        """
        fullname = os.path.join(path, name + Campagne.ext_camp)
        if not os.path.isfile(fullname):
            return None

        parser = configparser.ConfigParser()
        parser.read(fullname)

        if not 'IDENTIFICATION' in parser.sections():
            raise Exception ("Pas de section 'IDENTIFICATION' dans '{p}'".
                    format(p=fullname))

        camp = Campagne(**dict(parser.items('IDENTIFICATION')))

        others_sections = [ s for s in parser.sections()
                              if  s != 'IDENTIFICATION' ]
        for section in others_sections:
            camp.add_plateforme(nom=section, **dict(parser.items(section)))

        return camp


    @staticmethod
    def info_from_file(name, path=dir_camp):
        """ Retourne les informations contenues dans le fichier 'name'.
            (contrairement à load_from_file() ne crée pas une Campagne
            => temps d'accès beaucoup plus rapide !)

            :param str name: basename *sans* extension du fichier.
            :param str path: chemin du fichier à charger.
                             Ne devrait être utiliser qu'à des fins de tests
                             pour ne pas polluer le répertoire des campagnes).

            :return: les infos de la campagne.
            :rtype: dict()

            Le dictionnaire de retour est de la forme :

            >>>
                dict('header': { key: val}         : header de la campagne
                     'pltfs' : { pltf: {key, val}} : infos de chaque plateforme
                                                     (pltf = nom long)
                    )
            >>>
        """
        fullname = os.path.join(path, name + Campagne.ext_camp)
        if not os.path.isfile(fullname):
            return None

        parser = configparser.ConfigParser()
        parser.read(fullname)

        if not 'IDENTIFICATION' in parser.sections():
            raise Exception ("Pas de section 'IDENTIFICATION' dans '{p}'".
                    format(p=fullname))

        ret_dict = dict()
        ret_dict['header'] = dict(parser.items('IDENTIFICATION'))
        ret_dict['pltfs']  = {s: dict(parser.items(s)) for s in parser.sections()
                                 if  s != 'IDENTIFICATION' }

        return ret_dict


    @staticmethod
    def over_write_with_info(name, info, path=dir_camp):
        """ Écrase le contenu du fichier de campange 'name' avec le contenu
            du dictionnaire 'info'.

            Le dicionnaire 'info' doit contenir toutes les informations de la
            campagne et être de la même forme que celui retourné par la méthode
            'info_from_file()'.

            :param str    name: basename *sans* extension du fichier.
            :param ditc() info: dictionnaire de la campagne
                                (voir 'info_from_file()')
            :param str    path: chemin du fichier à écrire.
                                Ne devrait être utiliser qu'à des fins de tests
                                pour ne pas polluer le répertoire des campagnes).

            :return: True si l'écriture a été faite,False sinon.
            :rtype: bool
        """
        fullname = os.path.join(path, name + Campagne.ext_camp)
        if not os.path.isfile(fullname):
            warning(f"le fichier {fullname} n'existe pas et va être créé")

        identification = Template(dedent(Campagne.identification_tpl))
        plateforme     = Template(dedent(Campagne.plateforme_tpl))

        # création/écrassement du fichier
        try:
            with open(fullname, 'w') as handler:
                print(identification.substitute(info['header']), file=handler)

                for pltf, pltf_info in info['pltfs'].items():
                    pltf_info['nom'] = pltf
                    print(plateforme.substitute(pltf_info), file=handler)
        except:
            warning(f"erreur d'écriture sur le fichier '{fullname}'.")
            return False

        return True


    def update(self, other, force_name=False):
        """ Mise à jour de la campagne avec les valeurs de 'other' si besoin.
            N'écrit pas le ficher.

            :param Campagne other:  campagne mise à jour.
            :param bool force_name: si True, le nom de la campagne est remplacé
                               par le other.nom
                               si False, si le self.nom != other.nom, lève
                               une exception.

            La méthode dict.update() ne fait pas ce qu'il faut si, par exemple,
            'other' contient : projet = ''.
            Il faudra voir ce que fait la méthode de dictionnaire 'd | other'
            à partir de python-3.9
        """
        if not isinstance(other, Campagne):
            raise Exception ("Campagne::update : 'other' attendu : Campagne()" +
                             ", reçu : {o}".
                             format(o=type(other)))

        if self.nom != other.nom and force_name == False:
            raise Exception ("Campagne::update : noms différents : {s} != {o}".
                             format(s=self.nom, o=other.nom))

        # récupérer les 2 campagnes sous forme de dictionnaire
        me_dict    = self._to_dict()
        other_dict = other._to_dict()

        # mettre à jour le dictionnaire de la campagne
        for opt, val in me_dict.items():
            me_dict[opt] = self.handler_comp[opt](val, other_dict[opt])

        # mettre à jour les attributs de la campagne
        self.set_values(**me_dict)

        # pour les plateformes
        # récupérer tous les noms de plateformes pour les 2 campagnes
        me_pltfs    = self.get_plateformes_by_name()
        other_pltfs = other.get_plateformes_by_name()

        for pltf in other_pltfs:
            if not pltf in me_pltfs:
                # récupérer le dictionnaire de la plateforme de 'other'
                other_pltf_dict = other.pltfs[pltf]._to_dict()
                # et cette plateforme à 'self'
                self.add_plateforme(**other_pltf_dict)
            else:
                # mettre à jour la plateforme avec les valeurs de la plateforme
                # de 'other'
                self.pltfs[pltf].update(other.pltfs[pltf])

        return


    def write(self, path=dir_camp):
        """ Écriture du fichier de la campagne.

            :param str path: chemin du fichier à écrire.
                             Ne devrait être utiliser qu'à des fins de tests
                             pour ne pas polluer le répertoire des campagnes).

            On passe par des templates plutôt que par un configparser qui est
            moins souple...
        """
        fullname = os.path.join(path, self.nom + Campagne.ext_camp)

        identification = Template(dedent(Campagne.identification_tpl))
        plateforme     = Template(dedent(Campagne.plateforme_tpl))

        # création du fichier
        with open(fullname, 'w') as handler:
            print(identification.substitute(self._to_dict()), file=handler)

            for pltf in self.pltfs.values():
                print(plateforme.substitute(pltf._to_dict()), file=handler)


    def get_fullname(self, test_exists=False):
        """ Retourne le chemin complet du fichier de la campagne.

            :param bool test_exists: si True, vérifie l'existance du fichier.

            :return: chemin complet du fichier de la campagne.
                     Si test_exists=True et que le fichier n'existe pas,
                     retourne None
            :rtype:  str/None
        """
        fullpath = os.path.join(Campagne.dir_camp, self.nom + Campagne.ext_camp)
        if test_exists:
            if not os.path.isfile(fullpath):
                return None

        return fullpath


def get_parts_of_compact(compact_acqids, acqids_list=None):
    """ Retourne les différentes parties de la liste compacte d'acqids
        passée en argument.
        Aucun contrôle de validité des acqids n'est fait.

        :param str compact_acqids: chaîne compacted d'acqids.
                                   Ex : "as210001-as210004, as210003"
        :param list acqids_list:   si fournit, contient les acqids possibles,
                                   sinon AIDA.existing_inf_files() est utilisée.

        :return: les différentes partie de compact_acqids.
        :rtype:  list(dict())

            >>>
                dict('begin': premier_acqid_du_range
                     'end'  : dernier_acqid_du_range
                    )
                - pour les acqidis simples : 'begin' = 'end'.
                - la valeur '*' n'est pas remplacée.
            >>>
    """
    ret_list = list()

    # récupérer les champs
    # commencer par supprimer tous les espaces (' ',[TAB]...) inutiles
    pattern = re.compile(r'\s+')
    cleaned_compact_acqids = re.sub(pattern, '', compact_acqids)

    # recupérer les différentes parties utiles de compact_acqids
    fields = re.split(',', cleaned_compact_acqids)

    # boucle de traitement de chaque partie utile
    for field in fields:
        if '-' in field:
            # traiter les ranges d'acqids
            begin, end = field.split('-')
            ret_list.append ({'begin': begin, 'end': end})
        else:
            # traiter les acqids simples
            ret_list.append ({'begin': field, 'end': field})

    return ret_list



def expand_acqids_pltf(compact_acqids, acqids_list=None):
    """ Retourne la liste exhaustive des acqids répondant à la forme compacte
        passée en argument.

        :param str compact_acqids: chaîne compacted d'acqids.
                                   Ex : "as210001-as210004, as210003"
        :param list acqids_list:   si fournit, contient les acqids possibles,
                                   sinon AIDA.existing_inf_files() est utilisée.

        :return: la liste exhaustives des acqids.
                 Ex : [as210001, as210002, as210003, as210004]
        :rtype:  list

        Les doublons sont éliminés.

        La lib AIDA accepte les acqid de longeur 7. Dans l'usage, ils sont de
        longueur 6 *ou* 8. Il est impossible de savoir à quoi correspond le
        range : as190001-*as19004* (n° 0004 ou 004x ?) ou de savoir si as19004
        appartient au range as190001-as190015.
        De ce fait, *les acqid qui n'ont pas de .inf sont éliminés*.

        La forme compacte peut être de la forme xxaannnn-* :
            le joker est remplacé par le 'dernier acqid' pour la plateforme xx
            (le dernier acqid pour la plateforme est donc 'dynamique').
    """
    set_of_acqids = set()

    if len(compact_acqids) == 0:
        return set_of_acqids

    # récupérer les champs
    parts = get_parts_of_compact(compact_acqids)

    # boucle de traitement de chaque partie utile
    for part in parts:
        begin, end = part.values()

        if begin != end:
            if end == '*':
                # vérifier que begin est un acqid valide
                AIDA.check_acq_id(begin)
                # récupérer le dernier acqid de la plateforme de 'begin'
                end = AcqId.get_last_acqid(begin[0:2], acqids_list)

            # valider les 2 acqids
            for item in [begin, end]:
                inf_path = AIDA.ID_to_inf_path(item)
                if not os.path.isfile(inf_path):
                    warning("expand_acqids_pltf : pas de .inf pour " + item +
                            " => " + str(part) + " ignoré")
                    break
            else:   # du for !
                # récupérer la liste des acqids entre begin et end
                new_set = { a for a in AcqId.get_acqids_between(begin,
                                                                end,
                                                                acqids_list) }
                #if not new_set:
                #    print(f'DBG expand_acqids_pltf  : new_set = {new_set}')
                #    input('... continue')

                # et l'ajouter au set en cours
                set_of_acqids = set_of_acqids | new_set
        else:
            # traiter les acqids simples
            # valider l'acqid
            inf_path = AIDA.ID_to_inf_path(begin)
            if not os.path.isfile(inf_path):
                warning("expand_acqids_pltf : pas de .inf pour " + begin +
                        " => acqid ignoré")
                continue

            if acqids_list and not begin in acqids_list:
                warning("expand_acqids_pltf : pas dans la liste " + begin +
                        " => acqid ignoré")
                continue

            # ajouter l'acqid au set de traitement
            set_of_acqids.add(begin)

    return sorted(set_of_acqids)


def compact_acqids_pltf(exhaustive_acqids, running=False, acqids_list=None):
    """ Retourne une chaine représentant la forme compacte de la liste
        exhaustive d'acqids passée en argument.

        La liste exhaustive n'a pas besoin d'être triée.
        Elle peut contenir des acqids de plusieurs plateformes.

        :param list exhaustive_acqids: liste d'acqids. Ex :
                                       [as210001, as210002, as210003, as210007]
        :param bool running:           si True, si la forme compacte se termine
                                       par un range, le dernier acqid est
                                       remplacé par une '*'.
        :param lis acqids_list:        si fournit, contient les acqids
                                       possibles,
                                       sinon AIDA.existing_inf_files() est
                                       utilisé.

        :return: la liste compacte d'acqids.
                 Ex : "as210001-as210003, as210007"
        :rtype:  str

        La lib AIDA accepte les acqid de longeur 7. Dans l'usage, ils sont de
        longueur 6 *ou* 8. Il est impossible de savoir à quoi correspond le
        range : as190001-*as19004* (n° 0004 ou 004x ?) ou de savoir si as19004
        appartient au range as190001-as190015.
        De ce fait, *les acqid qui n'ont pas de .inf sont éliminés*.
    """

    def _builder(range_begin, range_end, acqids):
        """ Retourne une string contenant l'acqid unique ou la forme compacte
            des acqids représentatifs des arguments passés

            :param int range_begin: indice du premier acqid dans la liste
                                    'acqids`.
            :param int range_end:   indice du dernier acqid dans la liste
                                    'acqids`.
            :param list acqids:     liste des noms d'acqids.
                                    (généralement tous les nom d'acqids de la
                                    plateforme).

            :return: forme compact d'acqids.
            :rtype:  str
        """
        if range_begin == range_end:
            return acqids[range_begin]
        else:
            return f'{acqids[range_begin]}-{acqids[range_end]}'


    part_str = []
    pattern = r'(?P<plt>[a-zA-Z0-9]{2})(?P<year>\d{2})(?P<number>\d{2,4})'

    # récupérer dans `exhaustive_acqids` toutes les abréviations des
    # plateformes concernées
    try:
        abrevs = set( acqid[0:2] for acqid in sorted(exhaustive_acqids) )
    except TypeError as e:
        warning(f"compact_acqids_pltf : sorted retourne TypeError sur : '{exhaustive_acqids}'")
        return ''

    # récupérer tous les acqids des plateformes concernées
    all_acqids  = {}
    for abrev in abrevs:
        all_acqids[abrev] = [ a for a
                                    in AcqId.existing_acqids_per_abrev(abrev) ]

    idx_begin = None
    idx_end   = None
    for acqid in sorted(exhaustive_acqids):
        pltf = acqid[0:2]

        # vérifier que l'acqid existe (<=> il a un .inf)
        try:
            idx_current = all_acqids[pltf].index(acqid)
        except ValueError as e:
            warning("compact_acqids_pltf : pas de .inf pour " + acqid +
                    " => acqid ignoré")

            # si besoin, générer ce qui était n cours de traitement
            if idx_begin:
                part_str.append(_builder(idx_begin, idx_end, all_acqids[pltf]))
                idx_begin = None

            continue


        # ici on n'a que des acqids valides
        if idx_begin == None:
            idx_begin = idx_current
            idx_end   = idx_current
            continue

        if idx_current == idx_end + 1:
            # on est dans un range
            idx_end = idx_current
        else:
            # on n'est pas/plus dans un range
            part_str.append(_builder(idx_begin, idx_end, all_acqids[pltf]))
            idx_begin = idx_current
            idx_end   = idx_current

    # génération du dernier traitement
    part_str.append(_builder(idx_begin, idx_end, all_acqids[pltf]))

    # traitement de 'running'
    if running:
        field = part_str[-1]
        if '-' in field:
            begin, end = field.split('-')
            end = '*'
            part_str[-1] = f'{begin}-{end}'
        else:
            warning("compact_acqids_pltf : 'running' hors range : " + field +
                    " => non remplacé")

    return ', '.join(part_str)


def existing_camp_files(name_only=False):
    """
        Generator de chargement des fichiers .camp existants.

        :param bool name_only: si False, charge les fichiers campagne
                               si True , ne charge par les fichiers campagne

        :yield: tuple(): Si name_only=True (nom_campagne)
        :yield: tuple(): Si name_only=False (nom_campagne, Campagne())
    """
    list_camp_files = [ n for n in os.listdir(Campagne.dir_camp) \
                           if n.endswith(Campagne.ext_camp) ]
    for camp_file in list_camp_files:
        short_name = os.path.splitext(camp_file)[0]
        if name_only:
            yield (short_name)
        else:
            camp = Campagne.load_from_file(short_name)
            yield (camp.nom, camp)


def get_campagnes_for_pltf(pltf_name):
    """
        Renvoie la liste des campagnes dans lesquelles la plateforme a été
        engagée.

        :param str pltf_name: nom long de la plateforme.

        :return: liste des campagnes dans lesquelles la plateforme a été
                 engagée.
        :rtype: list()
    """
    try:
        cmd = [f'cd {Campagne.dir_camp} ; grep -l "^\[{pltf_name}\]" *{Campagne.ext_camp}']
        ret = subprocess.check_output(cmd, shell=True)
        names = ret.decode().split('\n')[:-1]

        return [ os.path.splitext(name)[0] for name in names ]
    except subprocess.CalledProcessError:
        return []


def get_campagnes_for_acqid(acqid):
    """
        Renvoie la liste des campagnes de l'acqid.

        Pour le moment, un acqid ne fait partie que d'une campagne mais cela
        pourrait changer ultérieurement.

        :param str acqid: valeur de l'acqid.

        :return: liste des campagnes de l'acqid.
        :rty
        pe: list()
    """
    # vérifier la validité de l'acqid
    try:
        AIDA.check_acq_id(acqid)
    except:
        return []

    # récupérer le nom de la plateforme de l'acqid
    try:
        pltf_name = AIDA.plt_by_abrev[acqid[0:2]].nom
    except:
        return []

    # créer un AcqId avec la chaine pasée en argument
    acqid_in = AcqId.AcqId(acqid, read_inf=False)

    # récupérer la liste des campagne dans laquelle la plateforme a été engagée.
    ret_campagnes = []
    campagnes = get_campagnes_for_pltf(pltf_name)
    for campagne in campagnes:
        camp_info = Campagne.info_from_file(campagne)
        
        # récupérer la liste des acqid pour la plateforme de cette campagne
        compact_acqids = camp_info['pltfs'][pltf_name]['liste_acqid']
        ##### TODO : beaucoup trop long !!!!
        ##### acqids = expand_acqids_pltf(compact_acqids)
        #####if acqid in acqids:
        #####    ret_campagnes.append(campagne)
        parts = get_parts_of_compact(compact_acqids)
        for part in parts:
            begin, end = part.values()

            if end == '*':
                end = AcqId.get_last_acqid(begin[0:2])

            # créer 2 acqid avec begin et end pour pouvoir faire des comparaisons...
            acqid_begin = AcqId.AcqId(begin, read_inf=False)
            acqid_end   = AcqId.AcqId(end  , read_inf=False)

            # si l'acqid donné est compris entre begin et and, alors il fait
            # partie de cette campagne
            if acqid_in >= acqid_begin and acqid_in <= acqid_end:
                ret_campagnes.append(campagne)


    return ret_campagnes


if __name__ == '__main__':
    os.system('clear')

    pltf = 'atr'
    print("\n* Récupération du nom des campagnes pour la plateforme :", pltf)
    l = get_campagnes_for_pltf(pltf)
    print("  liste :", l)
    wait_user()

    acqid = 'as190010'
    print("\n* Récupération du nom des campagnes pour l'acqid :", acqid)
    l = get_campagnes_for_acqid(acqid)
    print("  liste :", l)
    wait_user()

    acqid = 'Gt200047'
    print("\n* Récupération du nom des campagnes pour l'acqid :", acqid)
    l = get_campagnes_for_acqid(acqid)
    print("  liste :", l)
    wait_user()

    acqid = 'Gt210350'
    print("\n* Récupération du nom des campagnes pour l'acqid :", acqid)
    l = get_campagnes_for_acqid(acqid)
    print("  liste :", l)
    wait_user()

    pltf = 'toto'
    print("\n* Récupération du nom des campagnes pour :", pltf)
    l = get_campagnes_for_pltf(pltf)
    print("  liste :", l)
    wait_user()


    # info_from_file <-> load_from_file
    nom_camp = 'SMOSMANIA'
    print("\n* Info de la campagne :", nom_camp)
    SMOSMANIA_info = Campagne.info_from_file(nom_camp)

    print(f'  - header de {nom_camp} :')
    for key, value in SMOSMANIA_info['header'].items():
        print(f'    - header[{key:25s}] = {value}')
    wait_user()

    print(f'  - liste des plateformes de {nom_camp} :')
    for key in SMOSMANIA_info['pltfs'].keys():
        print(f'    - pltf : {key}')
    wait_user()

    print(f'  - info sur les plateformes de {nom_camp} :')
    for pltf, infos in SMOSMANIA_info['pltfs'].items():
        print(f'    - {pltf} :')
        for key, value in infos.items():
            print(f'      - {key:25s} = {value}')
    wait_user()

    pltf_name = 'mazan-radome'
    print(f'  - liste des acqid de la plateforme {pltf_name} de {nom_camp} :')
    compact_acqids = SMOSMANIA_info['pltfs'][pltf_name]['liste_acqid']
    print(f'    - forme compact : {compact_acqids} :')
    acqids = expand_acqids_pltf(compact_acqids)
    print(f'    - forme expand  : {acqids} :')
    wait_user()

    print("\n* Chargement de la campagne", nom_camp)
    SMOSMANIA_camp = Campagne.load_from_file(nom_camp)
    print('  - SMOSMANIA_camp.nom =', SMOSMANIA_camp.nom)
    wait_user()

    print("\n* Récupération du nom seulement des campagnes existantes :")
    for camp_name in existing_camp_files(name_only=True):
        print("  - camp_name :", camp_name)
    wait_user()

    nom = 'bidon'
    p1  = 'atr'
    p2  = 'falcon'
    p1_acqids = {'as190001' : "01/01/2019", 'as190002' : "01/02/2019"}
    p2_acqids = {'fs200001' : "21/01/2020", 'fs200002' : "22/02/2020"}

    print("\n* création de la campagne :", nom)
    new_camp = Campagne(nom=nom, projet='test des classes')
    new_camp.show_me()
    #wait_user()



    print("\n* ajout de la plateforme :", p1)
    new_camp.add_plateforme(nom=p1)
    new_camp.show_me()
    #wait_user()

    print("\n* ajout des acqids :", list(p1_acqids.keys()))
    for acqid, date_acq in p1_acqids.items():
        print("  * acqid =", acqid, "date_acq =", date_acq)
        new_camp.add_plateforme_acqid(p1, acqid, date_acq)
        new_camp.pltfs[p1].show_me()
        #wait_user()
    print('\n\n')
    new_camp.show_me()
    #wait_user()
    print('\n\n')

    d = {'principal_investigator': "pi:pi:pi:pi"}
    print("\n* mise à jour  :", d)
    new_camp.pltfs[p1].set_values(**d)
    new_camp.pltfs[p1].show_me()
    #wait_user()
    print('\n\n')



    print("\n* ajout de la plateforme :", p2)
    new_camp.add_plateforme(nom=p2)
    new_camp.show_me()
    #wait_user()
    print("\n* ajout des acqids :", list(p2_acqids.keys()))
    for acqid, date_acq in p2_acqids.items():
        new_camp.add_plateforme_acqid(p2, acqid, date_acq)
        new_camp.pltfs[p2].show_me()
        #wait_user()
    print('\n\n')
    new_camp.show_me()
    #wait_user()


    path = '/tmp'
    fullname = os.path.join(path, nom + Campagne.ext_camp)
    print("\n* écriture du fichier :", fullname)
    new_camp.write(path=path)
    print("--> Modifier le fichier", fullname,
             " pour vérifier l'update faite ci-après")
    wait_user()


    print("\n* load du fichier :", fullname)
    other_camp = Campagne.load_from_file(nom, path=path)
    other_camp.show_me()


    print("\n* update new_camp with loaded file :", fullname)
    new_camp.update(other_camp, force_name=True)
    print("\n*   écriture du fichier updaté :", fullname)
    new_camp.write(path=path)
    new_camp.show_me()
    wait_user()


    print("\n* Récupération des campagnes existantes :")
    for camp_name, camp in existing_camp_files():
        print("  - campagne : {n:20s} début = {d}".
            format(n=camp_name, d=camp.date_debut))

        print("    ** Récupération des plateformes de la campagne par leur nom :")
        for pltf_name in camp.get_plateformes_by_name():
            print("    - plateforme : {n}".format(n=pltf_name))
            print("      - acqids = {a}".format(a=camp.pltfs[pltf_name].acqids))
            print("      - acqids = {c}".format(c=compact_acqids_pltf(camp.pltfs[pltf_name].acqids)))

        print("    ** Récupération des objets Pltf de la campagne :")
        for pltf in camp.get_plateformes_by_obj():
            print("    - plateforme : {n}".format(n=pltf.nom))
            print("      - acqids = {a}".format(a=pltf.acqids))
            print("      - acqids = {c}".format(c=compact_acqids_pltf(pltf.acqids)))
        print()
    wait_user()


    print("\n* création d'une campagne SANS nom :")
    try:
        new_camp = Campagne(projet='test des classes')
    except Exception as e:
        result("ERROR : msg = >" + str(e) + "<")
    wait_user()


    print("\n* création d'une platefome SANS nom:")
    try:
        new_pltf = Pltf()
    except Exception as e:
        result("ERROR : msg = >" + str(e) + "<")
    wait_user()


    print("\n* création d'une platefome avec *ABREV*:")
    try:
        new_pltf = Pltf(nom='as')
    except Exception as e:
        result("ERROR : msg = >" + str(e) + "<")

    truc_camp = """
[IDENTIFICATION]
nom                    = HISAIII
date_debut             = 01/07/2019
date_fin               = running
projet                 = HISA
region_geographique    = South of France
un_m49_code            = 250
geospatial_lat_min     = 43.2153454
geospatial_lat_max     = 45.5454545
geospatial_lon_min     = -1.56455121
geospatial_lon_max     = 1.154654552
description            = Test of DGA instrumentation on Falcon, ATR, and at
                         Pic du Midi.
principal_investigator = Xavier:Gauthier:DGA:xavier.gauthier@intradef.gouv.fr>


[atr]
liste_acqid            = as0897-as090003, as190007, as19016-as190019, as200021- as200025, as21007, as21001-as210003
date_debut             = 04/07/2019
date_fin               = 21/02/2021
principal_investigator = Xavier:Gauthier:DGA:xavier.gauthier@intradef.gouv.fr>

[falcon]
liste_acqid            = fs200013, fs200014
date_debut             = 28/10/2020
date_fin               = 28/12/2020
principal_investigator = Xavier:Gauthier:DGA:xavier.gauthier@intradef.gouv.fr>

[gillot-aeroport-mf]
liste_acqid            = gi180001-*
date_debut             = 31/12/2018
date_fin               = running
principal_investigator = Xavier:Gauthier:DGA:xavier.gauthier@intradef.gouv.fr>
"""

    # récupérer la liste exhaustive des acqids
    print("\n\n\n* expand_acqids_pltf et expand_acqids_pltf (truc.camp)")
    parser = configparser.ConfigParser()
    parser.read_string(truc_camp)

    for pltf in parser.sections()[1:]:
        print("* plateforme =", pltf)
        acqids = parser.get(pltf, 'liste_acqid')
        print("** liste_acqid lue        =", acqids)
        e_acqids = expand_acqids_pltf(acqids)
        print("   liste_acqid exhaustive =", e_acqids)
        print()

    wait_user()

    # construire une forme compacte d'acqids à partir d'une liste exhaustive
    print("\n* Construction d'une chaine compacte")

    new_list = [
            'as0602'  ,
            'fs190013',
            'as19003',
            'as190001',
            'fs190001',
            'fs190006',
            'fs190007',
            'fs190008',
            'as0601'  ,
            'fs190010',
            'fs190011',
            'ZZ190011',
            'fs190012',
            'fs190014',
            'fs190002',
            'as190003',
            'fs190009',
            'fs190003',
            'as0603'  ,
            'as190004',
            'fs190004',
            'as190005',
            'fs190005',
            'as190006',
            'as190007',
            'as190008',
            'as190009',
            'as190010',
            'as190021',
            'as190002',
        ]

    print("  liste à compacter :")
    print("      brute \t| triée")
    for acqid, sort_acqid in zip(new_list, sorted(new_list)):
        print("    -", acqid, "\t|", sort_acqid)
    print()
    wait_user()

    field_acqids = compact_acqids_pltf(new_list)

    #print("    résultat : chaine =", field_acqids)
    result("résultat : " + field_acqids)


    # construire une forme compacte d'acqids avec passage d'année et running
    print("\n* Construction d'une chaine compacte avec passage d'année " +
          "et running")
    new_list = [ 'as0897',
                 'as0898',
                 'as0899',
                 'as090001',
                 'as090002',
                 'as090003',
               ]


    print("  liste à compacter :")
    print("      brute \t| triée")
    for acqid, sort_acqid in zip(new_list, sorted(new_list)):
        print("    -", acqid, "\t|", sort_acqid)
    print()
    wait_user()

    field_acqids = compact_acqids_pltf(new_list, running=True)

    #print("    résultat : chaine =", field_acqids)
    result("résultat : " + field_acqids)


    # construire une forme compacte d'acqids avec running
    print("\n* Construction d'une chaine compacte avec running")
    new_list = [ 'as0897',
                 'as0898',
                 'as0899',
                 'as090001',
                 'as090002',
                 'as090003',
                 'as090009',
               ]

    print("  liste à compacter :")
    print("      brute \t| triée")
    for acqid, sort_acqid in zip(new_list, sorted(new_list)):
        print("    -", acqid, "\t|", sort_acqid)
    print()
    wait_user()

    field_acqids = compact_acqids_pltf(new_list, running=True)

    #print("    résultat : chaine =", field_acqids)
    result("résultat : " + field_acqids)


    sys.exit(0)

