#!/usr/bin/env python3

"""
AITO
    Déclaration des opérateurs accessibles dans l'onglet "Traitements"
"""

import sys
import os
import glob


AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

from   Misval import AIDA_type_misval as AIDA_type_misval


# fonctions de récupération des informations pour l'initialisation des widgets :
# ----------------------------------------------------------------------------
# Elles doivent avoir la signature obligatoire suivante :
#    (header, data, acqid_dir, new_time_header=None)
#   avec :
#   - header          : header du vecteur sélectionné par l'utilisateur
#   - data            : data   du vecteur sélectionné par l'utilisateur
#   - acqid_dir       : directory de l'acquisition du vecteur sélectionné par
#                       l'utilisateur.
#   - new_time_header : header du nouveau vecteur temps sélectionné par
#                       l'utilisateur.
#                       Voir MoyEch_tps_impos.
#                       None pour les opérateurs qui n'attendent pas de nouveau
#                       vecteur temps.
def get_name(header, data, acqid_dir, new_time_header=None):
    return header['#hdr_name']


def get_freq_ech(header, data, acqid_dir, new_time_header=None):
    # certains vecteurs mal-formés n'ont pas de freq_ech ou sample
    # (ex : Tf210001::alt_hbn3_dso_cl31_%60_Mhbn_%1800.vbn)
    return header.get('freq_ech', 0)


def get_obs_min(header, data, acqid_dir, new_time_header=None):
    # DBG print(f"=== AITO_operators.py::get_obs_min : RETURN : {header['obs_min']}")
    return header['obs_min']


def get_obs_max(header, data, acqid_dir, new_time_header=None):
    # DBG print(f"=== AITO_operators.py::get_obs_max : RETURN : {header['obs_max']}")
    return header['obs_max']


def get_ref_time(header, data, acqid_dir, new_time_header=None):
    # DBG print(f"=== AITO_operators.py::get_ref_time : RETURN : {header['ref_time']}")
    return header['ref_time']


def get_extra_ref_time_NbVal(header, data, acqid_dir, new_time_header=None):
    val = ''
    if new_time_header:
        val = new_time_header['NbVal']

    # DBG print(f"=== AITO_operators.py::get_extra_ref_time_NbVal : RETURN : >{val}<")
    return val


def get_nb_vals(header, data, acqid_dir, new_time_header=None):
    # DBG print(f"=== AITO_operators.py::get_nb_vals : RETURN : {len(data)}")
    return len(data)


def get_nb_vals_2(header, data, acqid_dir, new_time_header=None):
    """ Retourne le nombre de données du vecteurs - 2
        => pour retourner une autre valeur (ex : nombre de données
           du vecteurs - 4), il faut écrire une autre fonction.
           (dans des version ultérieure, on pourra peut-être passer par
           quelque chose comme : functools.partial(get_max_invalid, apply=-2)
    """
    # DBG print(f"=== AITO_operators.py::get_nb_vals_2 : RETURN : {len(data) - 2}")
    return len(data) - 2


def get_misval(header, data, acqid_dir, new_time_header=None):
    """ Retourne le misval trouvé dans le header, sous forme de strt() ou
        celui du type des données.
    """
    misval = None
    if 'misval' in header.keys():
        misval = header['misval']

    if not misval or 'nan' in misval.lower():
        misval = AIDA_type_misval [ header['format'] ]

    # DBG print(f"=== AITO_operators.py::get_misval : RETURN : {misval}")
    return misval


###def get_recommended_nb_ech(header, data, acqid_dir, new_time_header=None):
###    print(f"=== AITO_operators.py::get_recommended_nb_ech : RETURN : 42... Méthode A ECRIRE...")
###    return 42


def get_all_ref_times(header, data, acqid_dir, new_time_header=None):
    l0 = [ 'sélectionner un vecteur...' ]
    l1 = [ os.path.splitext(f)[0] for f in glob.glob('rft*.vbn', root_dir=acqid_dir) ]
    l2 = [ os.path.splitext(f)[0] for f in glob.glob('time*.vbn', root_dir=acqid_dir) ]
    l3 = [ os.path.splitext(f)[0] for f in glob.glob('TIME*.vbn', root_dir=acqid_dir) ]

    # DBG print(f"=== AITO_operators.py::get_all_ref_times : RETURN : {l0 + l1[0:5]} etc")
    return l0 + sorted(l1) + sorted(l2) + sorted(l3)

# description des opérateurs et de leurs arguments pour l'IHM
# -----------------------------------------------------------
# Chaque opérateur traité par AITO est décrit dans un dictionnaire du
# dictionnaire 'operators' :
#   operators = { 'nom_d_operateur': { description de l'opérateur}
#
# La description de l'opérateur est un dictionnaire qui *doit* contenir une
# clé 'args' qui est une liste décrivant chaque argument de l'opérateur :
#   'args': [ { description d'un paramètre de l'opérateur } ]
#
# La description d'un paramètre  de l'opérateur est un dictionnaire qui *doit*
# contenir au minimum les clés 'name' et 'widget' :
# - 'name'   : nom affiché dans l'IHM.
#
# - 'widget' : ['lineedit', 'combo']
#              Type de widget (voir Operator.py).
#
# Les clés suivantes dépendent de la valeur de 'widget' :
# - pour les 'lineedit' :
#   - 'type'      : [int, float, str].
#                   Type des valeurs que l'utilisateur doit saisir.
#                   Pour les numériques, le QLineEdit sera muni d'un QValidator
#
#   - 'values'    : une liste [min, max] ou le nom d'une fonction décrite
#                   ci-dessus ou un float ou un int ou une string.
#                   Dans le cas [min, max] : min et max peuvent être des
#                   valeurs ou le nom d'une fonction décrite ci-dessus.
#
#   - 'editable'  : [False, True].
#                   Défaut : True.
#                   Si False, l'utilisateur ne pourra pas saisir une autre
#                   valeur dans le champ (le champ est présenté par cohérence
#                   avec la documentation)
#
#   - 'default'   : valeur par défaut.
#                   Défaut : la valeur minimum de 'values'
#                   Cette valeur peut être une valeur ou le nom d'une fonction
#                   décrite ci-dessus.
#
#   - 'show_range': [False, True]
#                   Défaut : True
#                   Affichage ou non du QLabel de range de saisie.
#
#   - 'call_type' : [int, float, str, 'vector_name'].
#                   Type de la valeur pour l'appel de l'opérateur
#                   Dans le cas str           : l'argument est enclos
#                                               dans des "'".
#                   Dans le cas 'vector_name' : l'argument N'est PAS enclos
#                                               dans des "'".
#                   mais le code de gestion est écrit...
#
# - pour les 'combo' :
#   - 'editable'  : [False, True].
#                   Défaut : True.
#                   Si False, l'utilisateur ne pourra pas saisir une autre
#                   valeur dans le champ (le champ est présenté par cohérence
#                   avec la documentation)
#
#   - 'type'      : NON IMPLÉMENTÉ (il faudrait le faire si on voulait
#                   présenter une liste de fréquence comme le faisait
#                   AITO-V1 pour Filtre_moy()
#
#   - 'values'    : liste des valeurs ou le nom d'une fonction décrite
#                   ci-dessus (qui doit retourner une liste de string).
#                   La liste des valeurs ne peut pas contenir de nom de
#                   fonction.
#                   Si 'call_type' est 'int' (voir ci-dessous), la valeur pour
#                   l'appel de l'opérateur est le numéro d'ordre du choix fait
#                   par l'utilisateur (en commençant à 0).
#                   Ex : pour Filtre_RC_sdph :
#                          - 'passe-bas'  aura la valeur 0 lors de l'appel et
#                          - 'passe-haut' aura la valeur 1.
#
#   - 'call_type' : [int, float, str, 'vector_name'].
#                   Type de la valeur pour l'appel de l'opérateur.
#                   Dans le cas str           : l'argument est enclos
#                                               dans des "'".
#                   Dans le cas 'vector_name' : l'argument N'est PAS enclos
#                                               dans des "'".
#
#   - 'changed'   : décrit sous la forme d'un dictionnaire ce qu'il faut faire
#                   lorsque la valeur du combo est changée.
#                   - la clé du dictionnaire est une action. Cette action est
#                     codée dans : IHMClasses/Operator.py::combo_changed().
#                   - la valeur du dictionnaire est une liste de widget.name
#                     qu'il faut mettre à jour suite au changement de la valeur
#                     du combo.
#                   Ex : pour MoyEch_tps_impos :
#                        'changed': {'read_vect': ['size out']},
#                       Lorsqu'un nouveau vecteur temps est sélectionné, lire
#                       le vecteur sélectionné et mettre à jour le widget dont
#                       champ name est 'size out'.
#
#
# *Pour les opérateurs qui retournent plusieurs jeux de données* (ex : data et
# control), il faut ajouter à la description de l'opérateur une clé 'outs'.
#   'outs': [ 'mot', 'mot' ]
#
# La clé 'out' est une liste de mots dont l'un est 'data'. Ces mots seront
# utilisé pour :
# 1) contruire les noms de sortie lors de l'appel de l'opérateur
# 2) les donnée de retour de 'data' seront tracées par AITO au retour de
#    l'opérator
# (voir Comble_spline)
# Par défaut, iAITO ajout à chaque description d'opérateur : ['data']
# (voir IHMClasses/Operator.py)
#
#
# *Certains opérateurs* ne peuvent être utilisés que sous certaines conditions
# ex : Correc_hors_stat ne fonctionnent pas si :
#      - fenêtre est hors de [50, 10000]
#      - fenêtre > nombre de valeurs du vecteur
# L'opérateur peut être invalidé par la clé : 'condition'.
# POUR LE MOMENT, la valeur de la condition doit être une chaine de caractères
# que Traitements.py::update_exec_button peut évaluer...
# Voir la description de Correc_hors_stat

operators = {
    'Filtre_RC_sdph':   # python
    {'args': [
        # QLineEdit $Arg1.#hdr_name
        {'name'      : 'X',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_name,
         'show_range': False,
         'call_type' : 'vector_name',
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'fréquence de coupure',
         'widget'    : 'lineedit',
         'type'      : float,
         'values'    : [0., get_freq_ech],
         'call_type' : float,
        },

        # QComboBox 'passe-bas' / 'passe-haut'
        {'name'      : 'Filtre',
         'widget'    : 'combo',
         'editable'  : False,
         'values'    : [ 'passe-bas' , 'passe-haut' ],
         'call_type' : int,
        },
     ],
    },

    'Correc_pics_mnq':      # C
    {'args': [
        # QLineEdit $Arg1.#hdr_name
        {'name'      : 'X',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_name,
         'show_range': False,
         'call_type' : 'vector_name',
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'seuil',
         'widget'    : 'lineedit',
         'type'      : float,
         ###'values'    : [get_obs_min, get_obs_max],
         'default'   : 0.,
         'show_range': False,
         'call_type' : float,
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'seuil manquant',
         'widget'    : 'lineedit',
         'type'      : float,
         ###'values'    : [get_obs_min, get_obs_max],
         'default'   : 0.,
         'show_range': False,
         'call_type' : float,
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'nombre de points invalides',
         'widget'    : 'lineedit',
         'type'      : float,
         '###values'    : [0, get_nb_vals],
         'values'    : [0, get_nb_vals_2],
         'call_type' : float,
        },
     ],
     'outs': ['flag', 'data'],
    },

    'Correc_hors_stat':     # C
    {'args': [
        # QLineEdit $Arg1.#hdr_name
        {'name'      : 'X',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_name,
         'show_range': False,
         'call_type' : 'vector_name',
        },

        # QLineEdit $Arg1.misval
        {'name'      : 'valeur manquante',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_misval,
         'show_range': False,
         'call_type' : float,
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'borne inférieure',
         'widget'    : 'lineedit',
         'type'      : float,
         ###'values'    : [get_obs_min, get_obs_max],
         ###'default'   : get_obs_min,
         'default'   : 0.,
         'show_range': False,
         'call_type' : float,
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'borne supérieure',
         'widget'    : 'lineedit',
         'type'      : float,
         ###'values'    : [get_obs_min, get_obs_max],
         ###'default'   : get_obs_max,
         'default'   : 0.,
         'show_range': False,
         'call_type' : float,
        },

        # QLineEdit [min, max] QIntValidator
        {'name'      : 'toler X',
         'widget'    : 'lineedit',
         ###'type'      : int,
         ###'values'    : [0, 15],
         ###'default'   : 7,
         'type'      : float,
         'values'    : [0.5, 15.],
         'default'   : 7.,
         'call_type' : float,
        },

        # QLineEdit [min, max] QIntValidator
        {'name'      : 'toler dX',
         'widget'    : 'lineedit',
         ###'type'      : int,
         ###'values'    : [0, 15],
         ###'default'   : 10,
         'type'      : float,
         'values'    : [0.5, 15.],
         'default'   : 10.,
         'call_type' : float,
        },

        # QLineEdit [min, max] QIntValidator
        {'name'      : 'fenêtre',
         'widget'    : 'lineedit',
         'type'      : int,
         'values'    : [50, 10000],
         'call_type' : int,
        },

        # QLineEdit [min, max] QIntValidator
        {'name'      : 'seuil durée',
         'widget'    : 'lineedit',
         'type'      : int,
         'values'    : [0, get_nb_vals_2],
         'call_type' : int,
        },
     ],
     # le code C dit : fenêtre doit appartenir à [50, 10000] et fenêtre > NbVals
     # => retourne une erreur pour les petits vecteurs de 48 valeurs
     'condition' : 'len(self.vector.data) > 50',
    },

    'Comble_spline':        # python
    {'args': [
        # QLineEdit $Arg1.#hdr_name
        {'name'      : 'X',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_name,
         'show_range': False,
         'call_type' : 'vector_name',
        },

        # QLineEdit [min, max] QIntValidator
        {'name'      : 'lissage',
         'widget'    : 'lineedit',
         'type'      : int,
         'default'   : 5,
         'show_range': False,
         'call_type' : int,
        },
     ],
     'outs': ['data', 'ctl'],
     # L'opérateur peut écrire sur stdout :
     # -+- Le vecteur ne contient pas de nans, pas d'interpolation
     ###'condition' : 'np.count_nonzero(np.isnan(self.vector.data)) > 0',
    },

    'MoyEch_tps_impos':     # C
    {'args': [
        # QLineEdit $Arg1.#hdr_name
        {'name'      : 'X in',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_name,
         'show_range': False,
         'call_type' : 'vector_name',
        },

        # QLineEdit $Arg1.ref_time
        {'name'      : 'time in',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_ref_time,
         'show_range': False,
         'call_type' : 'vector_name',
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'écart avant',
         'widget'    : 'lineedit',
         'type'      : float,
         ###'values'    : [0, get_freq_ech],
         'default'   : 0.,
         'show_range': False,
         'call_type' : float,
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'écart après',
         'widget'    : 'lineedit',
         'type'      : float,
         ###'values'    : [0, get_freq_ech],
         'default'   : 0.,
         'show_range': False,
         'call_type' : float,
        },

        # QLineEdit [min, max] QIntValidator
        {'name'      : 'toler mnq', # nb échantillons
         'widget'    : 'lineedit',
         'type'      : int,
         ###'values'    : [0, 1000],
         ###'default'   : get_recommended_nb_ech,
         'default'   : 0,
         'show_range': False,
         'call_type' : int,
        },

        # QComboBox get_all_ref_times
        {'name'      : 'time out',
         'widget'    : 'combo',
         'editable'  : False,
         'values'    : get_all_ref_times,
         'call_type' : 'vector_name',
         'changed'   : {'read_vect': ['size out']},
        },

        # QLineEdit len(time_out.data)
        {'name'      : 'size out',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_extra_ref_time_NbVal,
         'show_range': False,
         'call_type' : float,
        },
     ],
     'condition' : 'not self.extra_rft_time is None',
    },

    'Decale':               # C
    {'args': [
        # QLineEdit $Arg1.#hdr_name
        {'name'      : 'X',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_name,
         'show_range': False,
         'call_type' : 'vector_name',
        },

        # QLineEdit $Arg1.freq_ech
        {'name'      : 'fréquence',
         'widget'    : 'lineedit',
         'editable'  : False,
         'type'      : str,
         'values'    : get_freq_ech,
         'show_range': False,
         'call_type' : float,
        },

        # QLineEdit [min, max] QDoubleValidator
        {'name'      : 'décalage',
         'widget'    : 'lineedit',
         'type'      : float,
         ###'values'    : [0., 86400.],
         'values'    : [0., 10.],
         'call_type' : float,
        },
     ],
    },

    ###DEMO 'Log_flt':               # C
    ###DEMO {'args': [
    ###DEMO     # QLineEdit $Arg1.#hdr_name
    ###DEMO     {'name'      : 'X',
    ###DEMO      'widget'    : 'lineedit',
    ###DEMO      'editable'  : False,
    ###DEMO      'type'      : str,
    ###DEMO      'values'    : get_name,
    ###DEMO      'show_range': False,
    ###DEMO      'call_type' : 'vector_name',
    ###DEMO     },

    ###DEMO     # QLineEdit float QDoubleValidator
    ###DEMO     {'name'      : 'C0',
    ###DEMO      'widget'    : 'lineedit',
    ###DEMO      'type'      : float,
    ###DEMO      'values'    : 0.,
    ###DEMO      'call_type' : float,
    ###DEMO      'show_range': False,
    ###DEMO     },

    ###DEMO     # QLineEdit float QDoubleValidator
    ###DEMO     {'name'      : 'C1',
    ###DEMO      'widget'    : 'lineedit',
    ###DEMO      'type'      : float,
    ###DEMO      'values'    : 0.,
    ###DEMO      'call_type' : float,
    ###DEMO      'show_range': False,
    ###DEMO     },

    ###DEMO     # QLineEdit float QDoubleValidator
    ###DEMO     {'name'      : 'C2',
    ###DEMO      'widget'    : 'lineedit',
    ###DEMO      'type'      : float,
    ###DEMO      'values'    : 0.,
    ###DEMO      'call_type' : float,
    ###DEMO      'show_range': False,
    ###DEMO     },

    ###DEMO     # QLineEdit float QDoubleValidator
    ###DEMO     {'name'      : 'C3',
    ###DEMO      'widget'    : 'lineedit',
    ###DEMO      'type'      : float,
    ###DEMO      'values'    : 0.,
    ###DEMO      'call_type' : float,
    ###DEMO      'show_range': False,
    ###DEMO     },

    ###DEMO     # QLineEdit str
    ###DEMO     {'name'      : 'unit_res',
    ###DEMO      'widget'    : 'lineedit',
    ###DEMO      'editable'  : False,
    ###DEMO      'type'      : str,
    ###DEMO      'values'    : '',
    ###DEMO      'show_range': False,
    ###DEMO      'call_type' : str,
    ###DEMO      'show_range': False,
    ###DEMO     },

    ###DEMO     # QLineEdit str
    ###DEMO     {'name'      : 'description (fr)',
    ###DEMO      'widget'    : 'lineedit',
    ###DEMO      'editable'  : False,
    ###DEMO      'type'      : str,
    ###DEMO      'values'    : '',
    ###DEMO      'show_range': False,
    ###DEMO      'call_type' : str,
    ###DEMO      'show_range': False,
    ###DEMO     },

    ###DEMO     # QLineEdit str
    ###DEMO     {'name'      : 'description (en)',
    ###DEMO      'widget'    : 'lineedit',
    ###DEMO      'editable'  : False,
    ###DEMO      'type'      : str,
    ###DEMO      'values'    : '',
    ###DEMO      'show_range': False,
    ###DEMO      'call_type' : str,
    ###DEMO      'show_range': False,
    ###DEMO     },

    ###DEMO  ],
    ###DEMO },
}

