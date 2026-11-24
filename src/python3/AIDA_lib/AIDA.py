#!/usr/bin/env python3
# coding: utf-8

""" Ce module rassemble des outils (fonctions, classes) pour
    travailler dans un environnement AIDA.
"""



__version__ = "$Revision: 7421 $"

import os
import sys
import codecs
import errno
import stat
import warnings
import logging
import gzip
import re
import datetime as dt
import dateutil.parser
import numpy as np
import configparser
from subprocess import Popen, PIPE, STDOUT
from operator import itemgetter
from collections import OrderedDict

import VersionVect
import DataBase
import datetime
import AcqId
from fct_messages import (info, warning, stop_error, result, wait_user)

# Un logger général pour tout le package AIDA
logger = logging.getLogger('AIDA')

# Le dictionnaire suivant donne à chaque attribut
# des vecteurs d'AIDA un "poids" numérique, qui peut
# servir dans une fonction de tri.

# Les attributs sont répartis dans plusieurs gammes :
#    [-500, 0]    : attributs standards, décrits dans refman.pdf
#    [0   , 100]  : Plage réservée (pour attributs inconnus)
#    [100 , 1000] : attributs utilisés, mais non officiellement définis
#    [1000, 9000] : attributs hérités des systèmes d'acquisition,
#    [9000, 9999] : attributs présents pour des raisons purement techniques.
#    10000        : Valeur max réservée pour "date_creation"
ATTRIBUTS_POIDS = {
    # Les attributs généraux obligatoires et fréquents
    "name": -499,
    "english_name": -498,
    "information": -497,
    "vol": -496,
    "date_vol": -495,
    "format": -399,
    "dimension": -398,
    "dim_array": -397,
    "ref_time": -396,
    "misval": -395,
    "invval": -394,
    "type_acq": -299,
    "type_ech": -298,
    "freq_ech": -297,
    "unit": -296,
    "orientation": -295,
    "bornes": -294,
    "unit_bornes": -293,
    "famille": -292,
    "law": -99,
    "delay": -97,
    "origine": -95,
    "position": -93,
    "normal_min": -91,
    "normal_max": -89,
    "obs_min": -87,
    "obs_max": -85,
    "chaine_mesure": -83,
    "chaine_acquisition": -82,
    "module_1": -81,
    "module_2": -80,
    "module_3": -79,
    "module_4": -78,
    "module_5": -77,
    "module_6": -76,
    "module_7": -75,
    "module_8": -74,
    "module_9": -73,
    # Les champs utilises avant la normalisation de "chaine_acquisition"
    "sensor": -66,
    "transducer": -65,
    "calibration": -64,
    # "laws", juste avant la partie réservée aux attributs inconnus,
    # triés par ordre alphabetique (gamme [0,100])
    "laws": -1,
    # Je ne crois pas qu'ils aient été définis, mais ils existent parfois
    "nb_obs_inf_normal_min": 200,
    "nb_obs_inf_normal_max": 201,
    "origine-WARNING": 202,
    "fct_origine": 203,
    "fct_comment": 204,
    "debut": 203,
    "fin": 206,
    "heuredeb": 207,
    "heurefin": 208,
    "commentaire": 209,
    "sense": 210,
    # Les attributs spécifiques au système d'acquisition "CAM"
    "bloc": 1001,
    "dim_fifo": 1002,
    "coupleur": 1003,
    "channel": 1004,
    "sample": 1005,
    "index": 1006,
    "msgindex": 1007,
    "label": 1008,
    "reftime": 1009,
    "gain": 1010,
    "range": 1011,
    "cutoff_freq": 1012,
    "mode": 1013,
    "code": 1014,
    "codeRT": 1015,
    "codage": 1016,
    "resolution": 1017,
    "typeofdata": 1018,
    "signal": 1019,
    # Des attributs "techniques" induits par
    # certains éléments de la chaine.
    "cvs_revision": 9001,
    "version": 9202,
    "endianness": 9203,
    # Toujours à la fin : la date de creation
    "date_creation": 10000,
}


def attribut_poids_tri(attribut):
    """ Donne un "poids de tri" à un attribut.

        Si c'est un attribut connu, donne le poids défini par
        'ATTRIBUTS_POIDS'.
        Sinon, donne une valeur entre 0 et 97 correspondant à un tri
        alphabétique simple.
    """
    if attribut in ATTRIBUTS_POIDS:
        return ATTRIBUTS_POIDS[attribut]
    ponder = 0
    k = 1
    for char in attribut.upper():
        ponder += k * (ord(char) - 32)
        k /= (128.0 - 32)
    return ponder


class AidaError(Exception):
    """ Classe pour les erreurs dans le module AIDA."""
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg

# Ancien nom gardé pour compatibilité
AIDA_error = AidaError


def report_error(msg):
    """ Écrit un message sur stderr, en faisant à peu près la même
        conversion d'encodage de caractères que print, mais avec une
        option "replace", ce qui évite les erreurs bloquantes.
    """
    # Tentative de connaître le codage pratiqué par la sortie
    encoding = None
    if sys.stderr.isatty():
        encoding = sys.stderr.encoding
    if not encoding:
        encoding = sys.getdefaultencoding()
    if not encoding:
        encoding = 'ascii'

    # Tentative d'encoder le message, de façon résistante aux erreurs.
    #     - Les éventuelles "EncodeError" sont évitées par
    #           l'argument "replace"
    #     - Une erreur se produit si msg est de type bytes auquel cas on fait juste un decode dans le write.
    try:
         output_msg = msg.encode(encoding, 'replace')
    except :
         output_msg = msg
    # On re-decode dans le encoding de sortie (on doit passer une str en python3)
    sys.stderr.write (output_msg.decode(encoding) + '\n')



def AIDA_getenv(mot):
    """ Récupère la valeur d'une variable d'environnement
        de type AIDA_XXX, en fournissant la valeur
        par défaut ($AIDA_HOME/xxx) si la variable elle-même
        n'est pas définie.
    """
    val = os.getenv('AIDA_' + mot.upper())
    if val is None:
        val = os.path.join(os.getenv('AIDA_HOME', ''), mot.lower())
    return val


def diagno_temps(serie_time, toler_saut=5):
    """ Fait un certain nombre de tests sur une série de temps, détermine les
        fréquences d'échantillonnage moyennes et médianes, et donne les
        indices et valeurs des échantillons "positifs".

        toler_saut est la tolerance (en %).
        Si toler_saut<=0, pas de recherche des 'gros delta_t'.

        Cette fonction n'a pas grand-chose de spécifique à AIDA, mais c'est un
        besoin récurrent.
    """
    diag = {'f_moy': np.nan,
            'f_med': np.nan,
            'idx_retour': None,
            'idx_saut': None,
            'toler_saut': None,
           }
    if len(serie_time) < 2:
        return diag

    delta_t = np.diff(serie_time)

    diag['idx_retour'] = np.where(delta_t < 0)[0]
    diag['sec_retour'] = serie_time[diag['idx_retour']]
    diag['val_retour'] = delta_t[diag['idx_retour']]

    duree = serie_time[-1] - serie_time[0]
    diag['f_moy'] = float(len(serie_time)) / float(duree)
    period_med = np.median(delta_t)
    diag['f_med'] = 1.0 / period_med

    if toler_saut > 0:
        diag['toler_saut'] = toler_saut
        seuil_saut = period_med * (1. + toler_saut/100.0)
        diag['idx_saut'] = np.where(delta_t > seuil_saut)[0]
        diag['sec_saut'] = serie_time[diag['idx_saut']]
        diag['val_saut'] = delta_t[diag['idx_saut']]
    return diag


def diagno_vect_temps(acq_id, nom_vect, toler_saut=5):
    """ Lance diagno_temps() sur les données d'un vecteur.
    """
    vect = Vector(acq_id, nom_vect)
    return diagno_temps(vect.data, toler_saut)


def format_liste_idx_diag(txt_list, idx, sec, val, desc, max_show):
    """ Ajoute à txt_list une information sur les échantillons
        ayant été signalés par le diagnostique décrit dans "desc"
    """
    if idx is not None and len(idx) > 0:
        txt_list.append("Attention : %d %s" % (len(idx), desc))
        if len(idx) <= max_show:
            txt_list.append("num. échantillon(s) : " + ','.join([str(x) for x in idx]))
        else:
            txt_list.append(("%d premiers échantillon(s) : " % max_show) + ','.join([str(x) for x in idx[:max_show]]))
        if len(sec):
            txt_list.append("heure(s) : " + ','.join([sec_to_hhmmss(x) for x in sec[:max_show]]))
        if len(val):
            txt_list.append("ecart(s) : " + ','.join([str(x) for x in val[:max_show]]))


def redige_diagno_temps (diag, max_show=15, with_freq=False):
    """ Genere une version texte (chaîne unicode) du diagnostique
     produit par diagno_temps()
    """
    txt = []

    if diag['f_moy'] <= 0.0:
        txt.append("Attention : fin avant début ?")

    idx = diag['idx_retour']
    sec = diag['sec_retour']
    val = diag['val_retour']
    desc = "retour(s) dans le passé"
    format_liste_idx_diag(txt, idx, sec, val, desc, max_show)

    idx = diag['idx_saut']
    sec = diag['sec_saut']
    val = diag['val_saut']
    desc = "delta_t hors de [médiane +- %d%%]" % diag['toler_saut']
    format_liste_idx_diag(txt, idx, sec, val, desc, max_show)

    txt.append("Fréquence moyenne : %g Hz, médiane : %g Hz " % (diag['f_moy'], diag['f_med']))

    return '\n'.join(txt)


def ecrit_diagno_temps (serie_time, toler_saut=5, dest=sys.stdout,
                        with_freq=False, encoding=None):
    """ Écrit sur dest une version texte du diagnostique
     sur la série des temps passée en argument.
    """
    txt = redige_diagno_temps(diagno_temps(serie_time, toler_saut),
                              with_freq=with_freq)
    if len(txt) == 0:
        return
    if encoding:
        dest.write(txt.encode(encoding, 'replace') + '\n')
    else:
        dest.write(txt + '\n')


def compute_obs_min_max(hdr, data):
    """ Calcule, si possible, les valeurs 'obs_min' et 'obs_max'
        pour un vecteur avec les valeurs min/max réelles du vecteur
        hors nan, misval, invval...

        Dans la majorité des cas, data = vector.data.
        Cependant, il peut arriver que data ait été positionné par
        AIDA::Vector::_write à :
            data = data.astype(np_string(hdr['format']))
        C'est pour cela que le paramètre 'data' est attendu (voir méthode
        `_write`)

        Cette fonction doit pouvoir être appellée par prod_CDF sur des data
        cumulées de plusieurs vecteur (=> cette fonction ne peut pas être une
        méthode de AIDA::Vector.

        L'idée est de traiter les data reçues en float pour pouvoir
        invalider les données "de remplacement" puis de retourner les
        valeurs 'obs_min' et 'obs_max' en str() (mais en accord avec le
        format réel de data).
        Ne sont traitées que les data de type "numérique"...

        :return: str(obs_min), str(obs_max) ou None, None
                 Dans le cas de vecteur multi-dimmensionnel, les min de
                 chaque colonne sont séparés par "," (idem pour le max).
    """
    if len(data) == 0:
        # parfois les vecteurs (de SAFIRE ?) peuvent être mal formés...
        return None, None

    if not data.dtype.char in ['f', 'd', 'b', 'B', 'h', 'H', 'i', 'I', 'q', 'Q']:
        # on ne positionne les champs que pour des types "usuels"
        return None, None

    elif data.dtype.char in ['b', 'B', 'h', 'H', 'i', 'I', 'q', 'Q']:
        # type 'int' sous toutes les formes => passer en float pour
        # pourvoir remplacer les misval et autre par nan
        data_float = data.astype('float32')

    else:
        # type 'float' sous toutes les formes
        data_float = data

    conditions = list()
    choices    = list()

    # récupérer les valeurs de invval et misvals dans le header (au bon
    # format numérique)
    # et construire les conditions et choix pour np.select
    if 'invval' in hdr.keys():
        invval = np.array([ hdr['invval'] ], data_float.dtype)[0]
        conditions.append(data_float == invval)
        choices.append   (np.nan)

    if 'misval' in hdr.keys() :
        if  hdr['misval'] != '' :
            misval = np.array([ hdr['misval'] ], data_float.dtype)[0]
            conditions.append(data_float == misval)
            choices.append   (np.nan)

    # ajouter des conditions et choix pour np.inf et -np.inf (au cas où...)
    if len(conditions) > 0:
        conditions.append(data_float == np.inf)
        choices.append   (np.nan)

        conditions.append(data_float == -np.inf)
        choices.append   (np.nan)
    else:
        # cas assez défavorable : pas de misval ou invval exploitable
        # => on travaille sur 'data' sans tenir compte de 'nan'
        if data.ndim > 1:
            obs_min = ','.join([str(m) for m in np.min(data, 0).astype(data.dtype)])
            obs_max = ','.join([str(m) for m in np.max(data, 0).astype(data.dtype)])
        else :
            obs_min = str(np.min(data, 0).astype(data.dtype))
            obs_max = str(np.max(data, 0).astype(data.dtype))
        return obs_min, obs_max

    # remplacer tout ce qui n'est pas une valeur *vraie* par np.nan
    valid_data = np.select(conditions, choices, default=data_float)

    # trouver les obs_min/obs_max (et les traduire au format de `data`)
    if data.ndim > 1:
        obs_min = ','.join([str(m) for m in np.nanmin(valid_data, 0).astype(data.dtype)])
        obs_max = ','.join([str(m) for m in np.nanmax(valid_data, 0).astype(data.dtype)])
    else :
        obs_min = str(np.nanmin(valid_data, 0).astype(data.dtype))
        obs_max = str(np.nanmax(valid_data, 0).astype(data.dtype))

    return obs_min, obs_max


class OperApi(object):
    """ Cette classe définit des objets qui décrivent l'API d'un opérateur :
        - son nom
        - le nombre d'arguments
        - pour chaque argument, le sens (in/out), la catégorie (vect/const) et
        le type (au sens AIDA).
    """
    def __init__(self, nb_arg):
        if nb_arg < 0:
            return
        self.nb_arg = nb_arg
        self.arg_sens = [""]*nb_arg
        self.arg_cat = [""]*nb_arg
        self.arg_typ = [""]*nb_arg

    def from_text(self, lin):
        """ Decode un 'dump text' d'une API.
        """
        if lin.endswith(";"):
            lin = lin[:-1]
        champs = lin.split(";")
        if len(champs) < 2:
            self.nb_arg = -1
            raise AidaError ("API text too short")
        self.nb_arg = int(champs[1])
        if len(champs) != 2 + self.nb_arg:
            self.nb_arg = -1
            raise AidaError ("bad number of fields : expected %d, got %d"
                             % (self.nb_arg, len(champs)))
        self.__init__(self.nb_arg)
        for i in range(self.nb_arg):
            arg_actuel = champs[i+2]
            self.arg_sens[i] = arg_actuel[0]
            self.arg_cat[i] = arg_actuel[1]
            self.arg_typ[i] = arg_actuel[2:]
        return champs[0]


def get_oper_APIs():
    """ Retourne un dictionnaire qui associe à un nom d'opérateur
        son API (Objet de la classe OperApi)
    """
    oper_APIs = {}
    aida_lib_path = AIDA_getenv("lib")
    fic_api = open(os.path.join(aida_lib_path, "oper_API_desc.txt"),
                   "rU")
    n_lin = 0
    for lin in fic_api:
        n_lin += 1
        lin = lin.strip()
        if lin.startswith("#"):
            continue
        API_oper_actuel = OperApi(0)
        try:
            nom_oper = API_oper_actuel.from_text(lin)
        except AidaError as msg:
            print("line %d of %s : %s" % (n_lin, "oper_API_desc", msg))
        oper_APIs[nom_oper] = API_oper_actuel
    return oper_APIs


def BrnRange_to_array(strvct, nbval):
    lst_param = {'<debut>': np.nan,
                 '<fin>': np.nan,
                 '<nclasses>': np.nan,
                 '<pas>': np.nan,
                 '<largeur>': -1,
                }

    champs_bornes = strvct.split(',')
    for strb in champs_bornes :
        for cle in lst_param.keys() :
            if strb.find(cle) >= 0:
                try :
                    lst_param[cle] = int(strb[len(cle):])
                except ValueError:
                    try :
                        lst_param[cle] = float(strb[len(cle):])
                    except :
                        pass

    bpas = lst_param["<pas>"]
    if bpas is np.nan :
        raise ValueError ("ATTENTION décodage bornes : Le <pas> est obligatoire!")

    largeur = lst_param["<largeur>"]
    if largeur == -1 :
        largeur = bpas

    bmin = lst_param["<debut>"]
    bmax = lst_param["<fin>"]
    nb_bornes = lst_param["<nclasses>"]

    if np.isnan(lst_param["<debut>"]) :
        if ( bmax!=np.nan and nb_bornes != np.nan ) :
            bmin = bmax - largeur - (nb_bornes - 1) * bpas
        else :
            raise ValueError ("ATTENTION décodage bornes : pas assez de paramètres!")

    if np.isnan(lst_param["<fin>"]) :
        if ( bmin!=np.nan and nb_bornes != np.nan ) :
            bmax = bmin + largeur + (nb_bornes - 1) * bpas
        else :
            raise ValueError ("ATTENTION décodage bornes :pas assez de paramètres!")

    if np.isnan(nb_bornes) :
        nb_bornes = (( bmax - bmin - largeur ) / bpas) + 1

    if (( (nb_bornes - 1) * bpas ) + largeur != (bmax - bmin)) :
        raise ValueError ("ATTENTION décodage bornes : Nb_borne * bpas != bmax - bmin !")

    lst_bornes = np.arange(int(bmin), int(bmax)+1, int(bpas))
    bornes_ech = [[y,y+largeur] for y in lst_bornes]

    bornes = [bornes_ech for i in range(nbval)]
    return(bornes)


def BrnStandard_to_array(strstd, nbval):

    try :
        borne_str = [ (x.split(',')) for x in strstd.split(';') ]
    except :
        return None

    try :
        bornes_ech = [[int(y) for y in x] for x in borne_str]
    except ValueError:
        try :
            bornes_ech = [[float(y) for y in x] for x in borne_str]
        except :
            pass

    bornes = [bornes_ech for i in range(nbval)]

    return(bornes)


def strBornes_to_array(str_in, acqid=None, NbVal=1):
    """
        Retourne un tableau 2 colonnes (int ou float) de dimension (nb_bornes,2) à
        partir de la string bornes d'un vecteur.
    """

    lst_type_bornes=["<range>", "<vector_regulier>", "<vector_irregulier>"]
    bornes = None

    if "|" in str_in :
        str_in_list = str_in.split("|")
    else :
        str_in_list = [str_in]

    for element in range(len(str_in_list)) : 

        strb = str_in_list[element].replace(" ","").replace("(","").replace(")","")
        decoupe_str_bornes = strb.split(':')
        if len(decoupe_str_bornes) > 1 :
            type_bornes = decoupe_str_bornes[0]
            if type_bornes not in lst_type_bornes :
                print("Type de bornes inconnu!!")
                return None
            str_bornes = decoupe_str_bornes[1]
        else:
            type_bornes = "Standard"
            str_bornes = strb

        if type_bornes == "Standard" :
            temp = BrnStandard_to_array(str_bornes, NbVal)
        elif type_bornes == "<range>" :
            temp = BrnRange_to_array(str_bornes, NbVal)

        elif type_bornes == "<vector_regulier>" :
            largeur = 15
            alti=Vector (acqid, str_bornes, attributes_only = False)
            temp = [[[float(y),float(y+largeur)] for y in x] for x in alti.data]

        if element == 0 :
            bornes = np.array(temp)
        else :
            bornes = np.concatenate((bornes,np.array(temp)), axis = 1)

    return bornes


def get_dim_array(str_dim_array) :
    """
    Retourne le dim_array sous forme de tuple
    str_dim_array : le dim_array sous forme str
    """
    try :

        if "|" in str_dim_array :
            list_dim_array = [int(x) for x in str_dim_array.split("|")]
            tuple_dim_array = tuple(list_dim_array)
        else :
            list_dim_array = [int(str_dim_array)]
            tuple_dim_array = tuple(list_dim_array)

        return tuple_dim_array

    except :
        raise ValueError ("dim_array n'est pas reconnu")


def get_unit_bornes(str_unit_bornes):
    """
    Retourne le unit_bornes sous forme de tuple
    str_unit_bornes : le unit_bornes sous forme str
    """
    try :

        if "|" in str_unit_bornes :
            list_unit_bornes = [ x for x in str_unit_bornes.split("|") ]
        else :
            list_unit_bornes = [ str_unit_bornes ]
        tuple_unit_bornes = tuple(list_unit_bornes)

        return tuple_unit_bornes

    except :
        raise ValueError ("unit_bornes n'est pas reconnu")


def year_in_aida_range(year):
    """ Vérifie q'une année est dans la gamme traitable par AIDA.
        Ne renvoie rien si OK, ou un message d'erreur.
        Attention : Le message d'erreur est une chaine unicode.
    """
    if int(year) < 1970:
        return 'Annee antérieure à 1970'
    elif int(year) >= 2070:
        return 'Annee postérieure à 2070'
    else:
        return None


def Y2_to_Y4(aa):
    """ Convertit une année sur 2 chiffres en année sur 4 chiffres, selon les
        règles d'AIDA (année-pivot = 1970).

        Toutes les variables sont des chaines de caractères.
    """
    if int(aa) < 70:
        return "20" + aa
    else:
        return "19" + aa


def annee_2_car(nimporte):
    """ Renvoie, si possible, une annee sur deux caractères
     selon les règles AIDA (gamme [1970-2069]), à partir d'un
     entier ou d'une chaine.
    """
    int_nimporte = int(nimporte)
    if int_nimporte < 0 or int_nimporte > 2069:
        return None
    if int_nimporte > 99 and int_nimporte < 1970:
        return None
    str_nimporte = str(nimporte)
    if len(str_nimporte) == 2:
        return str_nimporte
    if len(str_nimporte) == 4:
        return str_nimporte[2:4]
    return None


def sec_to_hhmmss(seconds, separ=None):
    """ Convertit un nombre de secondes en chaine HHMMSS
         L'argument optionnel permet d'insérer "separ" entre
         les valeurs numeriques. Exemple "00:00:00"
    """
    hour, reste_sec = divmod(seconds, 3600)
    minu, sec = divmod(reste_sec, 60)
    if separ:
        fmt = "%02d" + separ + "%02d" + separ + "%02d"
    else:
        fmt = "%02d%02d%02d"
    return fmt % (hour, minu, sec)


def hhmmss_to_sec(heure_str, separ=None):
    """ Convertit une chaine HH[separ]MM[separ]SS[.mmm] en un nombre de
        secondes.

        L'argument optionnel permet l'existence de "separ" entre les valeurs
        numeriques. Exemple : '01:00:00'.

        Tolère HH >= 24, mais pas MM hors de [0, 60], ni SS hors de [0, 61]
        (61 pour les secondes intercalaires de l'UTC).
        Ces tolérances (HH>=24, sec == 60) font qu'il est impossible de stocker
        cette info dans un objet time de datetime (qui oblige hour in 0..23,
        second in 0..59). On utilise donc un nombre de secondes.
        Ce nombre de secondes est facilement comvertible en objet timedelta
        par datetime.timedelta(seconds=hhmmss_to_sec(chaine)).
    """
    if len(heure_str) < 5:
        raise ValueError ('La chaîne de caractères "%s" est trop courte pour etre une heure HHMMSS' % heure_str)
    if separ:
        X = heure_str.split(separ)
        if len(X) != 3:
            raise ValueError ("La chaîne de caractères \"%s\" n'est pas en trois parties" % heure_str)
        hour = int(X[0])
        minu = int(X[1])
        sec = float(X[2])
    else:
        hour = int(heure_str[0:2])
        minu = int(heure_str[2:4])
        sec = float(heure_str[4:])
    if minu > 60:
        raise ValueError ('minutes (%d) > 60' % minu)
    if minu < 0:
        raise ValueError ('minutes (%d) < 0' % minu)
    if sec > 61:
        raise ValueError ('secondes (%d) > 61' % sec)
    if sec < 0:
        raise ValueError ('secondes (%d) < 0' % sec)
    return sec + 60 * (minu + 60. * hour)


def freq_fmt(freq):
    """ Formate une fréquence selon les règles AIDA pour les cas où une forme
        compacte est nécessaire (en fin de nom, par exemple).
        (réunion AIDA du 12 novembre 2013 : précisions entre 0.5 et 2 Hz).
    """
    if freq < 0:
        raise ValueError ("fréquence négative (%g)" % freq)

    # Au-dessus du typique sys.float_info.epsilon (2.220446e-16)
    # mais physiquement assimilable à zéro.
    if freq < 1.0e-12:
        return "0"

    if freq > 2:
        return "%g" % round(freq)
    elif freq >= 1.0:
        return "%1.3g" % freq
    elif freq >= .5:
        return "%1.2g" % freq
    elif freq > 1.0e-9:
        return "%%%g" % round((1.0/freq))
    else:
        #  Moins d'un échantillon par 30 ans ??
        #  John Cage, on t'a reconnu !
        return "ASLSP"

# Ancien nom, pour compatibilité.
AIDA_freq_fmt = freq_fmt


def AIDA_abrev_to_family(acronyme):
    """ Renvoie le nom de la famille en se basant
     sur le fichier familles.
    """
    path = os.path.join (AIDA_getenv ('config'), 'familles')
    cfg = configparser.ConfigParser(delimiters=('='))
    cfg.read(path)
    if len(cfg.sections()) == 0:
        return "Undéterminé (AIDA probablement mal configuré)"
    for section in cfg.sections():
        if cfg.get(section, 'acronyme') == acronyme:
            family = section
            break
    # Syntaxe Python bien pratique : la clause else du for s'execute s'il
    # n'y a eu aucun break dans la boucle.
    else:
        family = "%s : famille inconnue." % acronyme

    return family


def get_all_abrev_to_family():
    """ Yield abrev,family pour tout le fichier familles.
    """
    path = os.path.join (AIDA_getenv ('config'), 'familles')
    cfg = configparser.ConfigParser(delimiters='=')
    cfg.read(path)
    for section in cfg.sections():
        yield cfg.get(section, 'acronyme'), section


class Plt(object):
    """  Une classe permettant de décrire chaque plate-forme
     connue d'AIDA (telles que) décrites dans le fichier "profils/$AIDA-PROFIL/plate-formes")
    """
    def __init__(self, nom, abrev, attributs=None):
        """
           Deux attributs sont obligatoires : le nom, l'abréviation.
           Tous les autres sont construits dynamiquement à partir d'une
        liste de couple (clef, valeurs). Dans la plupart des cas, cette liste
        aura été lue dans le fichier "plate-formes".
        """
        self.abrev = abrev
        self.nom = nom
        for key, value in attributs:
            if key == "abrev":
                continue
            self.__dict__[key] = value

    def __str__(self):
        result = []
        for key, value in list(self.__dict__.items()):
            result.append(str(key) + " = " + str (value))
        return '\n'.join(result)

#     On définit ici des dictionnaires, en tant que variables globales du
#  package, qui seront des index sur les plate-formes et permettront aux
#  utilisateurs d'accéder à  :
#    airport_by_name[name]
#    airport_by_icao_id[icao_id]

airport_by_name = {}
airport_by_icao_id = {}


def ini_airports_indexes():
    """ Lit le fichier de configuration d'AIDA qui indique les
    aeroports connus ("$AIDA_HOME/profils/$AIDA_PROFIL/airports.fdd"), et remplit
    les index par nom et par code OACI.
    """
    PROFIL=os.getenv('AIDA_PROFIL', '')
    path = os.path.join (AIDA_getenv ('profils'), PROFIL, 'airports.fdd')
    cfg = configparser.RawConfigParser()
    try:
        cfg.read(path, encoding='ISO8859-15')
    except UnicodeDecodeError:
        cfg.read(path)

    for dico in (airport_by_name, airport_by_icao_id):
        if dico:
            dico.clear()
    for nom_aeroport in cfg.sections():
        if nom_aeroport == 'FORMAT':
            continue
        if nom_aeroport in airport_by_name:
            warnings.warn("double definition de %s dans %s" % (nom_aeroport, path))
            continue
        try:
            icao_id = cfg.get(nom_aeroport, 'ICAO_ID')
        except configparser.NoOptionError:
            icao_id = None
        try:
            z_0 = cfg.get(nom_aeroport, 'Z0')
        except configparser.NoOptionError:
            z_0 = None
        airport_by_name[nom_aeroport] = (icao_id, z_0)
        if icao_id:
            airport_by_icao_id[icao_id] = (nom_aeroport, z_0)


#     On définit ici des dictionnaires, en tant que variables globales du
#  package, qui seront des index sur les plate-formes et permettront aux
#  utilisateurs d'accéder à  :
#    AIDA.plt_by_abrev[abrev].nom
#    AIDA.plt_by_name[nom].abrev
#    AIDA.plt_by_mf_id[mf_id].nom_long
#    AIDA.plt_by_wmo_id['07510'].tri
#    if hasattr (AIDA.plt_by_wmo_id['07510'], "responsable"):
#       resp = getattr (AIDA.plt_by_wmo_id['07510'], "responsable")
#   etc...

plt_by_abrev = {}
plt_by_name = {}
plt_by_mf_id = {}
plt_by_wmo_id = {}


def _add_obj_to_index(plt, nom_clef, index):
    """ Ajoute l'objet "plt" dans l'index "index" (qui est,
     techniquement, un dictionnaire) avec, comme clef,
     la valeur du chame "nom_clef".
    """
    if hasattr(plt, nom_clef):
        valeur_clef = getattr(plt, nom_clef)
        if not valeur_clef:
            return
        if valeur_clef in index:
            warnings.warn("doublon de %s : %s" % (nom_clef, valeur_clef))
            return
        index[valeur_clef] = plt


def ini_plt_indexes():
    """ Lit le fichier de configuration d'AIDA qui indique les
    plate-formes de mesures connues ("$AIDA_HOME/profils/$AIDA_PROFIL/plate-formes"),
    crée un objet Plt pour chaque paragraphe correct, remplit
    les index par nom, par abreviation et, si ces attributs sont
    définis, les index par "mf_indicator" et "wmo_id".
    """

    PROFIL=os.getenv('AIDA_PROFIL', '')
    path = os.path.join (AIDA_getenv ('profils'), PROFIL, 'plate-formes')
    cfg = configparser.RawConfigParser()
    try:
        cfg.read(path, encoding='ISO8859-15')
    # Petite astuce : UnicodeDecodeError ne peut être levé que par Python3...
    # auquel cas on re-essaye avec les arguments Python3. Simple, non ?
    except UnicodeDecodeError:
        cfg.read(path)

    # Vu qu'on lit toujours le fichier "$AIDA_HOME/profils/$AIDA_PROFIL/plate-forme",
    # ça n'a pas beaucoup de sens de concatener la lecture actuelle
    # a un contenu qui aurait été lu précédemment.
    # Donc on commence par effacer
    for dico in (plt_by_abrev, plt_by_name, plt_by_mf_id, plt_by_wmo_id):
        if dico:
            dico.clear()
    for nom_plt in cfg.sections():
        if nom_plt == 'FORMAT':
            continue
        if nom_plt in plt_by_name:
            warnings.warn("double definition de %s dans %s" % (nom_plt, path))
            continue
        try:
            abrev = cfg.get(nom_plt, 'abrev')
        except configparser.NoOptionError:
            warnings.warn("dans %s, %s n'a pas d'abrev" % (path, nom_plt))
            continue
        if len(abrev) != 2:
            warnings.warn("l'abrev de %s ne fait pas 2 car : %s" % (nom_plt, abrev))
            continue
        new_plt = Plt(nom_plt, abrev, cfg.items(nom_plt))
        plt_by_abrev[abrev] = new_plt
        plt_by_name[nom_plt] = new_plt
        if hasattr(new_plt, 'aliases'):
            for alias in new_plt.aliases.split(','):
                alias = alias.strip()
                if alias in plt_by_name:
                    warnings.warn("l'alias %s de %s est un nom existant" % (alias, nom_plt))
                plt_by_name[alias] = new_plt

        _add_obj_to_index(new_plt, 'mf_indicator', plt_by_mf_id)
        _add_obj_to_index(new_plt, 'WMO_station_index_number', plt_by_wmo_id)


def AIDA_mf_indicator_to_abrev(mf_indicator):
    """ Renvoie l'abréviation pour les plate-formes qui sont des stations
        Meteo-France en se basant sur le fichier plate-formes.

        Lève une exception KeyError si l'indicatif n'est pas connu.
    """
    if not plt_by_mf_id:
        ini_plt_indexes()
    try:
        abrev = plt_by_mf_id[mf_indicator].abrev
    except KeyError:
        raise KeyError("Indicatif %s inconnu." % mf_indicator)
    return abrev


def AIDA_abrev_to_plt(abrev):
    """ Renvoie le nom de la plateforme en se basant sur le fichier
        plate-formes.

        Lève une exception KeyError si l'abréviation n'est pas connue.
    """
    if not plt_by_abrev:
        ini_plt_indexes()
    try:
        name = plt_by_abrev[abrev].nom
    except KeyError:
        raise KeyError("Abreviation %s inconnue" % abrev)
    return name


def AIDA_nom_long_to_abrev(name):
    """ Renvoie l'abreviation en se basant sur le fichier plate-formes.

        Lève une exception KeyError si le nom n'est pas connu.
    """
    if not plt_by_name:
        ini_plt_indexes()
    try:
        abrev = plt_by_name[name].abrev
    except KeyError:
        raise KeyError("Nom %s inconnu." % name)
    return abrev


def liste_plt_to_abrev(liste_nom_plt):
    """ Renvoie une liste des abreviations de noms de plate-forme correspondant
        à la liste des noms passés en arguments.

        La liste des abreviations a toujours le même nombre d'éléments que la
        liste des noms de plate-forme : si une plate-forme n'existe pas ou n'a
        pas d'abréviation, l'élément correspondant de la liste résultat est
        None.
    """
    if not plt_by_name:
        ini_plt_indexes()
    liste_abrev = []
    for nom_plt in liste_nom_plt:
        if nom_plt in plt_by_name:
            abrev = plt_by_name[nom_plt].abrev
        else:
            abrev = None
        liste_abrev.append(abrev)
    return liste_abrev


def AIDA_abrev_to_mf_indic(abrev):
    """ Renvoie l'indicatif Meteo-France, le nom_long, l'abreviation en
        se basant sur le fichier plate-formes.

        Lève une exception KeyError si l'abréviation n'est pas connue.
     """

    if not plt_by_abrev:
        ini_plt_indexes()
    try:
        nom_station = plt_by_abrev[abrev].nom
    except AttributeError:
        raise KeyError("La plate-forme dont l'abreviation est %s n'a pas d'attribut \"nom\"." % abrev)
    try:
        mf_indic = plt_by_abrev[abrev].mf_indicator
    except KeyError:
        raise KeyError("Abreviation %s inconnue." % abrev)
    except AttributeError:
        raise KeyError("La plate-forme dont l'abreviation est %s n'a pas d'attribut \"mf_indicator\"." % abrev)

    return mf_indic, nom_station, abrev

def conversion_latlon_en_float(slatlon):
    """ convertit n'importe que string xx°yy'ss'' ou xx,yyy° ... en float degre millieme """
    latlon=np.NaN
    udeg=""
    umin=""
    usec=""
    try:
        latlon=float(slatlon)
        return latlon
    except ValueError as e:
        #récupération des degres
        upos=slatlon.split('°')
        udeg=upos[0]
        #print(upos,udeg)
    except Exception as e:
        print("ERR calcul lat:{} : {} ".format(uslat,e))
        return latlon
    try:
        # recupération des minutes
        if (len(upos)>1) and (upos[1]!=''):
            ureste=upos[1].split('\'')
            umin=ureste[0]
            #recherche des secondes
            if (len(ureste)>1) and (ureste[1]!=''):
                ureste1=ureste[1].split('\"')
                usec=ureste1[0]
                latlon = abs(float(udeg)) + (float(umin)*60+float(usec))/3600
            else:
                latlon = abs(float(udeg)) + (float(umin))/60
        else:
            latlon = abs(float(udeg))
    except Exception as e:
        #print("ERR calcul :{} : {} ".format(upos,e))
        raise ValueError ("ERR calcul :{} : {} ".format(upos,e))
        return np.NaN

    return latlon if float(udeg) > 0 else latlon*-1

def  decode_latlon_plf(uslat,uslon):
        """ decodage des lat et longitudes du fichier plateforme ecrites sous n'importe que format et recodage en float degre milliemes
        formats possible: degre.millieme, degre °min'seconde", degre°minutes.millieme', "xxx"
        recodage direction: E/W pour les lat ou S/N pour les lon avec le signe -/rien
        on recode les lat,lon en float
        """

        #print(uslat,uslon)
        # On récupère la direction éventuellement si c'est un caractere à la fin du string
        slat1=uslat.split(' ',1)
        slat=slat1[0]
        if (len(slat1) >1) and (slat1!='') :
            if slat1[1]=='S':
                slat='-'+slat
        else:
            if slat1[0][-1:] =='S':
                slat='-'+slat[:-1]
            elif slat1[0][-1:] =='N':
                slat=slat[:-1]

        slon1=uslon.split(' ')
        slon=slon1[0]
        if len(slon1) >1:
            if slon1[1]=='W':
                slon='-'+slon
        else:
            if slon1[0][-1:] =='W':
                slon='-'+slon[:-1]
            elif slon1[0][-1:] =='E':
                slon=slon[:-1]

        #Conversion lat, lon en float
        lat=conversion_latlon_en_float(slat)
        lon=conversion_latlon_en_float(slon)

        return lat,lon

def decode_position_plf(abrevplf):
    """ recuperation des lat,lon event alti du champ position du fichier plate-formes
    les données sont lues en string de format variable et renvoyees en float degre.millieme pour les lat / lon et int pour les alti Nan pour les valeurs manquantes ou lat,lon "mobiles"""

    lat=lon=alti=np.NaN

    if not plt_by_abrev:
        ini_plt_indexes()
    try:
        upos=plt_by_abrev[abrevplf].position
    except KeyError as e:
        print(f"KeyError: Plateforme inconnue : '{abrevplf}'")
        return lat,lon,alti

    #recupération des champs position: lat, lon, alti
    if upos != "mobile":
        # on enleve les espaces inutils
        upos=''.join(upos.split(' '))
        tpos=upos.split('/')
        if (len(tpos)>1) and (tpos[1]!=''):
            lat,lon=decode_latlon_plf(tpos[0],tpos[1])
            #comment="Lecture position dans plateforme={} lat={} lon={}".format(abrevplf,lat,lon)
            if (len(tpos)>2) and (tpos[2]!=''):
                try:
                    alti=tpos[2]
                    if alti[len(alti)-1]=='m':
                        alti=float(alti[0:len(alti)-1])
                    else:
                        alti=float(alti)
                    #comment=comment+" alti={}".format(alti)
                except Exception as e:
                    alti=np.NaN
                    print("WARN: alti mise a Nan: {}".format(e))
        #print(comment)
    return lat,lon,alti


def check_acq_id(acq_id):
    """ Lève une exception AidaError si la chaine passée en argument
        ne peut pas être un identificateur d'acquisition.

        @return rien
    """
    if not isinstance(acq_id, str):
        raise TypeError ("acq_id devrait être une chaîne (%s)" % str(acq_id))
    if len(acq_id) < 6 or len(acq_id) > 8:
        raise AidaError (
            "Mauvaise longueur d'Acq_ID (%d: %s)" % (len(acq_id), acq_id))
    if acq_id.find(" ") != -1:
        raise AidaError (
            "Espace interdite dans Acq_ID (%s)" % acq_id)
    if not acq_id[2:4].isdigit():
        raise AidaError (
            "Caractères 3-4 autres que chiffres dans Acq_ID (%s)" % acq_id)


def ID_to_full(acq_id):
    """ Donne le nom de plate-forme, l'année, et le numéro d'acquisition
    correspondant à un acq_id.

    @param acq_id ID of acquisition
    @return triplet platform_name, year, acq_num : chaînes de caractère

    Peut générer une exception (AidaError ou KeyError) si l'acq_id
    est invalide ou ne correspond pas à une plate-forme connue.
    """
    check_acq_id(acq_id)

    abrev = acq_id[0:2]
    AA = acq_id[2:4]
    annee = Y2_to_Y4 (AA)
    num = acq_id[4:]
    nom_plateforme = AIDA_abrev_to_plt(abrev)

    return nom_plateforme, annee, num


def ID_to_relpath(acq_id):
    """ Construit un chemin relatif correspondant à un acq_ID.
    """
    nom, an, num = ID_to_full(acq_id)
    return os.path.join (nom, an, num)


def ID_to_datapath(acq_id):
    """ Construit le chemin des données correspondant à un Acq_ID.
    """
    return os.path.join (AIDA_getenv ('data'), ID_to_relpath(acq_id))

def ID_to_database(acq_id):
    """ Construit le chemin de la base de donnée associée à un Acq_ID.
    """
    plateforme, annee, num = ID_to_full(acq_id)
    return os.path.join (AIDA_getenv ('data'), plateforme, plateforme+".db")

def ID_to_inf_path(acq_id):
    """ Construit le chemin du fichier de meta-données (.inf)
        correspondant à une acquisition.
    """
    check_acq_id(acq_id)
    return os.path.join (AIDA_getenv('meta'), 'INF', acq_id + '.inf')

def datapath_to_ID(datapath) :
    """ Retourne l'acqid à partir du datapath
    """
    items = datapath.split('/')
    num = items[-1]
    annee = items[-2]
    plateforme = items[-3]
    ptf = AIDA_nom_long_to_abrev(plateforme)
    acqid = ptf+annee[2:]+num
    return acqid

def ecrit_inf (acq_id, acq_meta, force=False):
    """ Écrit sous la forme d'un fichier .inf les meta-données d'acquisition
        contenues dans acq_meta.

        acq_meta doit être un dictionnaire :
        - les clefs sont les noms de section (chaine)
        - les valeurs sont les contenus de chaque section : un dictionnaire
        {attribut:valeur}.

        Cette fonction n'écrasera un fichier existant que si force=True (même
        si tout le monde a tous les droits sur le fichier).
    """
    inf_fic_path = ID_to_inf_path(acq_id)
    if force:
        inf_fic = open(inf_fic_path, "w")
    else:
        # Ouverture explicite en mode "write", mais sans
        # écrasement possible :
        try:
            fd = os.open(inf_fic_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                         0o664)
        except OSError:
            return
        inf_fic = os.fdopen(fd, "w")

    try:
        for nom_rub, rub in list(acq_meta.items()):
            if not isinstance(nom_rub, str):
                inf_fic.write ('\n#Ignored [%s]\n' % str(nom_rub))
                continue
            inf_fic.write ('\n[%s]\n' % nom_rub)
            field_len = max([len(x) for x in list(rub.keys()) if isinstance(x, str)])
            fmt_ligne = '%%-%ds = %%s;\n' % field_len
            l_rub = list(rub.items())
            l_rub.sort(key=itemgetter(0), reverse=False)
            # for attribut, valeur in rub.items():
            for attribut, valeur in l_rub:
                if not isinstance(attribut, str):
                    inf_fic.write ('#Ignored %s = %s\n' % (str(attribut), str(valeur)))
                    continue
                if valeur is None:
                    inf_fic.write (fmt_ligne % (attribut, ''))
                elif isinstance(valeur, list):
                    for elt in valeur:
                        inf_fic.write (fmt_ligne % (attribut, elt))
                else:
                    inf_fic.write (fmt_ligne % (attribut, valeur))
    finally:
        inf_fic.close()


def date_acq(acq_id):
    """ Donne la date du démarrage d'une d'acquisition (lue dans
    le fichier <acq_id>.inf).

    @param acq_id ID of acquisition
    @return triplet annee, mois, jour
    """
    aida_bin_path = AIDA_getenv('bin')
    inffiltre_exe = os.path.join (aida_bin_path, 'INFfiltre')
    inf_fic_path = ID_to_inf_path(acq_id)

    cmd = [inffiltre_exe, '-i', inf_fic_path, '-l', '-f', '3',
           '-r0', 'IDENTIFICATION', '-c0', 'date']
    try:
        child = Popen (cmd, stdout=PIPE, stderr=STDOUT)
    except OSError:
        return (-1, -1, -1)
    res = child.stdout.read()
    exec_code = child.wait ()
    child.stdout.close()
    if exec_code == 255:
        raise AidaError (
            "fichier %s absent ou illisible" % inf_fic_path)
    elif exec_code != 0:
        raise AidaError (
            "Erreur %d lors lecture date dans [IDENTIFICATION] de %s)" % (exec_code, inf_fic_path))
    res = res.strip().decode('utf-8')
    if res == "":
        raise AidaError (
            "Attribut date manquant ou vide dans [IDENTIFICATION] de %s)" % inf_fic_path)
    try:
        date_object = dt.datetime.strptime(res, "%d/%m/%Y")
    except ValueError:
        try:
            date_object = dt.datetime.strptime(res, "%d/%m/%y")
        except ValueError:
            raise AidaError ("date indecodable dans %s : %s" % (inf_fic_path,
                             res))

    return (date_object.year, date_object.month, date_object.day)


def ressemble_vect(file_path):
    """ Retourne vrai si le fichier désigné par filepath existe et est
        probablement un vecteur :
        - extension .vbn ou .vbn.gz
        - taille > 512
        - Nom qui ne commence pas par '.' (fichiers 'cachés').
    """
    if file_path.startswith('.'):
        return False
    if not (file_path.endswith(".vbn") or file_path.endswith(".vbn.gz")):
        return False
    try:
        stat_info = os.stat(file_path)
    except OSError:
        return False
    if not stat.S_ISREG(stat_info[stat.ST_MODE]):
        return False
    if not stat_info.st_size > 512:
        return False
    return True


def vector_exists(acq_id, nom_vect):
    """ Retourne vrai s'il existe un vecteur de nom "nom_vect"
    dans l'acquisition "acq_id".
    """
    nomrep = ID_to_datapath(acq_id)
    if ressemble_vect(os.path.join(nomrep, nom_vect + ".vbn")):
        return True
    if ressemble_vect(os.path.join(nomrep, nom_vect + ".vbn.gz")):
        return True
    return False


def listvectacq(acq_id):
    """ Donne la liste des vecteurs d'une acquisition
        sous la forme de nom du paramètre, pas du nom
        du fichier (sans .vbn ou .vbn.gz)
    """
    nomrep = ID_to_datapath(acq_id)
    try:
        l = os.listdir(nomrep)
    except OSError as err:
        raise AidaError (("Erreur lors lecture répertoire acquisition %s %s : " % (acq_id, nomrep)) + repr(err))
    return [v[:v.rfind(".vbn")] for v in l if ressemble_vect(os.path.join(nomrep, v)) ]


def aida_format(np_format):
    """ Donne le nom d'un format AIDA
        correspondant à une chaîne de définition dtype/numpy
    """
    x = {"f": "Ieeefloat_32",
         "d": "Ieeefloat_64",
         "i": "int_32",
         "I": "u_int_32",
         "h": "int_16",
         "H": "u_int_16",
         "b": "int_8",
         "B": "u_int_8",
         "V": "Special"
         }
    try:
        return x[np_format]
    except KeyError:
        return None


def np_string(aida_format_str, dimension=0):
    """ Donne la chaîne de format dtype/numpy
        correspondant à un format AIDA.
    """
    np_string_dict = {
        "quanta_12_bits": "H",
        "quanta_14_bits": "H",
        "quanta_14_bits_signe": "h",
        "quanta_16_bits": "H",
        "quanta_32_bits": "I",
        "int_8": "b",
        "u_int_8": "B",
        "byte": "B",
        "int_16": "h",
        "u_int_16": "H",
        "int_32": "i",
        "u_int_32": "I",
        "int_64": "q",
        "u_int_64": "Q",
        "ieeefloat_32": "f",
        "ieeefloat32": "f",
        "ieeefloat_64": "d",
        "ieeefloat64": "d",
        "hpfloat_32": "I",
        "arinc_sy429" : "Q",  # two 32-bit unsigned integers
        "arinc_bcd_sy429" : "{}a".format(dimension),
        "bc635_time" : "10a",  # 10 octets
        "icvpms_time" : "u4",   # 32-bit unsigned integer ??
        "string": "S{}".format(dimension),
        "string32": "U{}".format(int(dimension/4)),
        "special" : "{}a".format(dimension),
        # A remplacer par la ligne suivante dès que python 2.6 est mort.
        # nb_sec = (dt_obj - dt_ref).total_seconds()
        # "special" : "V%d" % dimension,
        }
    try:
        return np_string_dict[aida_format_str.lower()]
    except KeyError:
        # Les formats inconnus sont traités comme "Special"
        return "{}a".format(dimension)


def ensure_iso_885915(uni_or_str):
    """ Encode une chaine unicode en string codée en ISO8859-15,
       et essaie d'y arriver dans tous les cas, même si l'argument
       n'est pas une chaine unicode.
    """
    try:
        str_iso = uni_or_str.encode("iso8859-15", errors='replace')
    except AttributeError:
        str_iso = repr(uni_or_str)
    except UnicodeEncodeError:
        str_iso = uni_or_str

    # SB
    # python2 : str_iso est une string
    # python3 : str_iso est un tableau de bytes
    if isinstance(str_iso, bytes):
        return str_iso.decode('iso8859-15')
    else:
        return str_iso


def clean_for_name(chaine):
    """ Retourne une copie de la chaine passée en argument dans laquelle
     les caractères interdits dans les noms de vecteurs ont été supprimés.
     cf. Document de référence/Volume 1 section 7 : Nommage
    """
    interdits = set('/\\"\'*?<>|$;&+-()[]= ')
    return ''.join([c for c in chaine if c not in interdits])


class Vector(object):
    """ A class implementing AIDA's time series ("vector").

        acq_id is in Vector.acq_id (a string)
        name   is in Vector.name (a string)
        Data   is in Vector.data (a numpy array)
        Attributes are in Vector.attributes (a dict)

        There is a special key for ('#hdr_name') for the name found in the
        header, which can be different frome the file name.
    """

    __magic = b'VECT-DATA'
    __hdr_startmark = b'\x02'
    __hdr_endmark = b'\x0C\x03\x1A'
    __hdr_ASCIIend = b'FIN_HDR'
    hdr_name_key = '#hdr_name'
    _existings = {}

    def __init__ (self, acq_id, name, attributes=None, data=None,
                  attributes_only=False, overwrite=False, strict=True,
                  version=0, url=None, misval_auto=True):
        """ Creation of an AIDA Vector object corresponding to a
            name in a given acq_id.

             If "data" and "attributes" arguments are None,
               the data and the attributes of the vector are read on disk.
             Else
               the data and the attributes of the vector are taken from the "data" and "attributes" arguments

             Use Vector.write() to save it

              acq_id          : the identifier of the acquisition
              name            : the name on the vector
              attributes      : a dict containing the attributes of the vector,
                                using AIDA vocabulary ('format", etc...)
              data            : an np_array object
              attributes_only : read only attributes calling read method
              overwrite       : useless (for compatibility)
              strict          : raise an AidaError exception in
                                case of format error found while reading a
                                vector file, even if it could be ignored.
              version         : the version of the vector
              url             : force the absolute path of the vector to read
                                or write (test mode)
              misval_auto     : if True and self.attributes['misval'], misval
                                values are replaced by NaN by _read() method,
                                for float and double data.

            Possible Exceptions :
                AidaError, IOError
        """
        self.acq_id = acq_id
        self._ref_time = None
        self._overwrite = overwrite
        self.version = version
        self.misval_auto = misval_auto
        self.url = url
        if url :
            self.storage_path = url
        else :
            if version == 0 :
                self.storage_path = os.path.join (ID_to_datapath(acq_id), name+'.vbn')
            else :
                self.storage_path = os.path.join (ID_to_datapath(acq_id), name+'.v'+str(version)+'.vbn')

        if " " in name:
            report_error("Espace dans un nom de vecteur !")
            report_error("--> remplacé par '_' ")
            name = name.replace(" ", "_")
        self.name = name

        if data is None and attributes is None:
            # Lecture d'un vecteur existant
            self.read (attributes_only, strict=strict)
            return

        # Verifier qu'il n'existe pas déjà
        #if os.path.exists(storage_path) and not overwrite and not backup :
        #    raise AidaError (
        #        u"Re-création d'un vecteur existant %s:%s" % (acq_id, name))

        if isinstance(data, np.ndarray):
            self.data = data
        else:
            # tentative de conversion automatique vers le type le plus courant
            try:
                self.data = np.array(data, dtype=float)
            except TypeError as err:
                raise AidaError ("Echec conversion automatique data %s" % err)

        if attributes is None:
            if len(self.data) > 0:
                self.attributes = {
                    "format" : aida_format(self.data.dtype.char),
                    "vol" : acq_id}
        else:
            if isinstance (attributes, dict):
                self.attributes = attributes
            else:
                raise TypeError (
                   "Vecteur %s : les attributs doivent etre un dict s" % name)
        if not self.hdr_name_key in self.attributes :
            self.attributes[self.hdr_name_key] = name

    def _open_vec_file(self, force) :
        """ Fonction qui ouvre un fichier vecteur en mode écriture binaire ('wb')
        """
        filepath = self.storage_path
        try:
            vec_file = open (filepath, 'wb')
        except IOError as excpt:
            if excpt.errno == errno.ENOENT: # no such file
                dest_dir = os.path.dirname(filepath)
                os.makedirs (dest_dir)
                os.chmod (dest_dir, 0o777)
                vec_file = open (filepath, 'wb')
            elif excpt.errno == errno.EACCES and force: # permission denied
                os.remove (filepath)
                vec_file = open (filepath, 'wb')
            else:
                raise
        return vec_file

    def compare_vect_data(self, other=None):
        """ Comparaison des données d'un objet vecteur avec :
                si other=None   : les données de son fichier vecteur.
                si other=<name> : les données du fichier vecteur <name> de même
                                  acqid que self.
            :return: False/True, message explicatif (vide si le retour est True)
        """

        if not other:
            file_vector = Vector(self.acq_id, self.name)
        else:
            file_vector = Vector(self.acq_id, other)

        # TODO : il faudrait ne pas dupliquer le code de 'def _comparvect(...)'
        # data différentes ?
        if len(self.data) != len(file_vector.data):
            return False, 'longueurs des données différentes'
        if not np.all(np.isclose(self.data, file_vector.data, equal_nan=True)) :
            return False, 'données différentes'

        return True, ''


    def _comparvect(self):
        """ Fonction qui compare un objet vecteur (header + data) avec
            le contenu de son fichier vecteur.
        """

        file_vector = Vector(self.acq_id, self.name, misval_auto=False)

        # Headers différents ?
        for a in self.attributes :
            if a == "date_creation" or a == "fct_comment" or a == "endianness" :
                continue
            if a not in file_vector.attributes :
                print ("--- _comparvect : l'attribut {} n'est pas dans le header du fichier {}:{}".format(a, self.acq_id, self.name))
                return False
            elif ensure_iso_885915(self.attributes[a]).strip(' ') != ensure_iso_885915(file_vector.attributes[a]).strip(' ') :
                try : # on traite les attributs pour lesquels les strings représentent des floats (obs_min, obs_max) pour régler les problèmes de précision
                    v1 = np.array([float(self.attributes[a])])
                    v2 = np.array([float(file_vector.attributes[a])])
                    if not np.all(np.isclose(v1,v2)) :
                        print ("--- _comparvect : les headers sont différents {} = \"{}\" -> \"{}\" pour {}:{}".format(a, ensure_iso_885915(self.attributes[a]), ensure_iso_885915(file_vector.attributes[a]), self.acq_id, self.name))
                        return False
                except :
                    print ("--- _comparvect : les headers sont différents {} = \"{}\" -> \"{}\" pour {}:{}".format(a, ensure_iso_885915(self.attributes[a]), ensure_iso_885915(file_vector.attributes[a]), self.acq_id, self.name))
                    return False

        for a in file_vector.attributes :
            if a == "date_creation" or a == "##Tecnic-Hdr_len" or a == "fct_comment" or a == "endianness" :
                continue
            if a not in self.attributes :
                print ("--- _comparvect : l'attribut {} n'est pas dans le header du vecteur {}:{}".format(a, self.acq_id, self.name))
                return False
            elif ensure_iso_885915(self.attributes[a]).strip(' ') != ensure_iso_885915(file_vector.attributes[a]).strip(' ') :
                try : # on traite les attributs pour lesquels les strings représentent des floats (obs_min, obs_max) pour régler les problèmes de précision
                    v1 = np.array([float(self.attributes[a])])
                    v2 = np.array([float(file_vector.attributes[a])])
                    if not np.all(np.isclose(v1,v2)) :
                        print ("--- _comparvect : les headers sont différents {} = \"{}\" -> \"{}\" pour {}:{}".format(a, ensure_iso_885915(file_vector.attributes[a]), ensure_iso_885915(self.attributes[a]), self.acq_id, self.name))
                        return False
                except :
                    print ("--- _comparvect : Problème comparaison des headers {} = \"{}\" -> \"{}\" pour {}:{}".format(a, ensure_iso_885915(file_vector.attributes[a]), ensure_iso_885915(self.attributes[a]), self.acq_id, self.name))
                    return False

        # data différentes ?
        if len(self.data) != len(file_vector.data) :
            print ("--- _comparvect : les data ont des longueurs différentes pour {}:{}.".format(self.acq_id, self.name))
            return False

        # pour les données de type string, on ne peut pas utiliser np.isclose
        if not self.data.dtype.char in ['U', 'S']:
            if not np.all(np.isclose(self.data, file_vector.data, equal_nan=True)) :
                print ("--- _comparvect : les data sont différentes pour {}:{}.".format(self.acq_id, self.name))
                return False
        else:
            if not np.all(self.data == file_vector.data):
                print ("--- _comparvect : les data sont différentes pour {}:{}.".format(self.acq_id, self.name))
                return False

        return True

    def _new_version(self) :
        """ Fonction qui crée une nouvelle version d'un vecteur sur le file system.
        """
        new_file_path = VersionVect.VersionMaxPlus1(self.acq_id, self.name)
        if new_file_path == None :
            return -1
        if os.path.isfile(self.storage_path+".gz") :
            os.rename(self.storage_path+".gz", new_file_path+".gz")
        else :
            os.rename(self.storage_path, new_file_path)
        return VersionVect.VersionVect(new_file_path)

    def _write(self, force, backup):
        """ Fonction de bas niveau pour l'écriture de vecteur.
            On s'interdit d'écrire des vecteurs dont la version != 0 .
        """

        comment = ""
        hdr = self.attributes
        data = self.data
        path = self.storage_path
        pathgz = self.storage_path+".gz"
        if not os.path.isfile(path) and os.path.isfile(pathgz) :
            path = pathgz
        if self.version != 0 :
            raise AidaError("+++ Erreur d'écriture du vecteur {} : il est interdit d'écrire un vecteur dont la version est différente de 0.".format(path))

        # On écrit les vecteurs en little endian
        hdr['endianness'] = 'little'

        # Si le champ format est présent, et différent de "special",
        # on vérifie sa cohérence avec le type de "data". En cas de désaccord,
        # le champ "format" est prioritaire, et le tableau data est
        # converti vers le type décrit par "format"
        if 'format' in hdr:
            if hdr['format'].lower() == 'special':
                if 'dimension' not in hdr:
                    raise AidaError ("+++ Impossible écrire vecteur {} : format special sans dimension ".format(self.name))
            elif np_string(hdr['format'])[0] != data.dtype.char and np_string(hdr['format'])[0] != 'S':
                # print "converting internal ", data.dtype, " to vector ", hdr["format"]
                data = data.astype(np_string(hdr['format']))
        else:
            hdr['format'] = aida_format(self.data.dtype.char)
            hdr['dimension'] = data.dtype.itemsize

        # On force l'écriture des string en string32
        if hdr['format'] == "string" :
            hdr['format'] = "string32"

        # Si le champ dimension" est présent, on vérifie sa cohérence avec le
        # type de "data". En cas de désaccord, l'information déduite du
        # type de "data" est prioritaire.
        if 'dimension' in hdr :
            # vérifier que hdr["dimension"]==dimension(format)
            dimension = int(hdr["dimension"])
            if dimension != data.dtype.itemsize :
                hdr["dimension"] = str(data.dtype.itemsize)
        else:
            hdr["dimension"] = str(data.dtype.itemsize)

        # Si date_creation est déjà dans "hdr" on ne la modifie pas
        if 'date_creation' not in hdr:
            hdr['date_creation'] = dt.datetime.strftime(dt.datetime.utcnow(), '%d/%m/%Y %H:%M:%S')

        # obs_min et obs_max. Parfois on a :
        #   data = data.astype(np_string(hdr['format']))
        self.set_obs_min_max(data)

        # Si le tableau "data" a plus d'une dimension (le temps)
        # on renseigne dim_array
        if data.ndim > 1:
            hdr['dim_array'] = '|'.join([str(i) for i in data.shape[1:] ])

        # Création de l'en-tête, dans une chaîne (iso, pas unicode...)
        pad_10 = '#'*10
        ### parag_def = '[' + ensure_iso_885915(self.name) + ']'
        ### SB : self.name peut contenir ".nx."
        ###      => utiliser plutôt self.hdr_name_key
        parag_def = '[' + ensure_iso_885915(hdr[self.hdr_name_key]) + ']'

        # SB
        # python2 : mélange byte / str
        # python3 : expected str instance, bytes found
        try:
            hdr_str = "\012".join ((Vector.__magic,
                                    pad_10,
                                    Vector.__hdr_startmark,
                                    parag_def, ""))
        except TypeError:
            hdr_str = "\012".join ((Vector.__magic.decode('iso8859-15'),
                                    pad_10,
                                    Vector.__hdr_startmark.decode('iso8859-15'),
                                    parag_def, ""))


        for key in sorted(iter(hdr.keys()), key=attribut_poids_tri):
            if key == Vector.hdr_name_key:
                continue
            # Si les valeurs sont en unicode, on les
            # ecrit en ISO-8859-15 (norme des vecteurs)
            v_iso = ensure_iso_885915(hdr[key])
            k_iso = ensure_iso_885915(key)
            hdr_str = hdr_str + k_iso + " = " + v_iso + "\012"

        # La fin de l'en-tête

        # SB
        # python3 : TypeError: Can't convert 'bytes' object to str implicitly
        try:
            hdr_str = hdr_str + Vector.__hdr_ASCIIend + "\012"
            hdr_str = hdr_str + Vector.__hdr_endmark + "\012"
        except TypeError:
            hdr_str = hdr_str + Vector.__hdr_ASCIIend.decode('iso8859-15') + "\012"
            hdr_str = hdr_str + Vector.__hdr_endmark.decode('iso8859-15') + "\012"

        hdr_len = len(hdr_str)
        quotient, reste = divmod (hdr_len, 512)  # division entière !
        if reste != 0:
            hdr_len = 512 * (quotient + 1)
            pad_end = chr(0) * (512 - reste)
            hdr_str = hdr_str + pad_end

        hdr_str = hdr_str.replace(pad_10, ("%10d" % hdr_len)[-10:], 1)

        # Si l'array est "big-endian", il faut le swapper avant de l'écrire
        if data.dtype.str[0] == '>':
            # print ("write : swaping byte order")
            data = data.byteswap()

        # si url est défini, on fait l'écriture dans le fichier sans se poser de question,
        # c'est une verrue qui sert en mode test/debug.
        if self.url:
            vec_file = self._open_vec_file(force)
        else:
            update_database = 0

            # si force=False et backup=False
            #   si le fichier exite
            #      on sort
            #   sinon
            #      on écrit le fichier à la version 0
            #      on update la base
            if force == False and backup == False :
                if os.path.isfile(path) :
                    return f"-+- Le vecteur {path} existe, pas d'écriture (force=False et backup=False)"
                else:
                    vec_file = self._open_vec_file(force)
                    update_database = 1

            # si force=True
            #   si base de donnée
            #     si le vecteur est locked
            #       création d’un nouvelle version
            #       mise à jour de la base
            #     sinon
            #       on écrase le vecteur
            #       mise à jour de la base si nouveau vecteur
            #  sinon
            #    on écrase le vecteur

            elif force == True :
                if DataBase.ExistDataBase(self.acq_id) :
                    if DataBase.VecteurLocked(self.acq_id, self.name) :
                        # création nouvelle version
                        status = self._new_version()
                        if status < 0 :
                            raise AidaError("+++ Erreur à la création d'une nouvelle version du vecteur {}".format(path))
                        vec_file = self._open_vec_file(force)
                        update_database = 1
                    else :
                        if not os.path.isfile(path) :
                           update_database = 1
                        vec_file = self._open_vec_file(force)
                else :
                    vec_file = self._open_vec_file(force)

            # si backup=True
            #   si le fichier exite et est identique
            #     on sort
            #   sinon
            #     si le fichier n'existe pas
            #       on crée le fichier à la version 0
            #       on update la base
            #     sinon (nouveau vecteur différent sauf pour vecteur temps pour lesquel on interdit le versionning)
            #       création d’une nouvelle version de vecteur .vn.vbn
            #       on crée le fichier à la version 0
            #       on update la base
            elif backup == True :
                if os.path.isfile(path) and self._comparvect() :
                    return "--- le vecteur {} existe et est identique, pas d'écriture".format(path)
                else :
                    if not os.path.isfile(path) :
                        vec_file = self._open_vec_file(force)
                    else :
                        # création nouvelle version sauf pour vecteur temps car il est référencé dans l'en-tête des vecteurs
                        if hdr['famille'] == "temps" :
                            raise AidaError("+++ Erreur : la création d'une nouvelle version est interdite pour le vecteur temps {}. Utiliser l'option -F".format(path))
                        status = self._new_version()
                        if status < 0 :
                            raise AidaError("+++ Erreur à la création d'une nouvelle version du vecteur {}".format(path))
                        comment += "--- sauvegarde d'une nouvelle version v{} du vecteur {}".format(status, path)
                        vec_file = self._open_vec_file(force)
                        update_database = 1

        # Ecriture du header et des data
        # SB
        # python2 : write attend une string
        # python3 : write attend bytes-like object
        try:
            vec_file.write(hdr_str)
        except TypeError:
            vec_file.write(hdr_str.encode('iso8859-15'))
        data.tofile (vec_file)
        vec_file.close()
        try:
            os.chmod (self.storage_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        except OSError as excpt:
            status = -1
            comment += excpt.strerror

        # Mise à jour de la base de données
        if not self.url and update_database == 1 and DataBase.ExistDataBase(self.acq_id) :
            self._write_database()

        return comment

    def _write_database(self):
        """ "internal" method which writes vector informations in a database if exists.
        """
        DataBase.UpdateDataBase(self.acq_id, self.name)

    def _readhdr(self, url):
        """ "internal" method which reads the header vector
        @param url
        @return rien
        """
        pass

    def _readvect(self, url, attributes_only, strict):
        """ "internal" method which reads a vector
        @param url
        @return rien
        """
        try:
            vec_file = open (url, 'rb')
        except IOError:
            vec_file = gzip.open(url+'.gz', 'rb')

        lin_1 = vec_file.read (len(Vector.__magic))
        if lin_1 != Vector.__magic:
            vec_file.close()
            raise AidaError ("Mauvais format : début de %s" % url)
        lin_2 = vec_file.read (10 + 1)
        try:
            hdr_size = int(lin_2)
        except:
            vec_file.close()
            raise AidaError ("Mauvais format : taille en-tête de %s" % url)

        # Si on veut être pointilleux : vérifier hdr_size multiple de 512
        size_reste_hdr = hdr_size - len(Vector.__magic) - 11
        hdr = vec_file.read (size_reste_hdr)
        if len(hdr) != size_reste_hdr:
            vec_file.close()
            raise AidaError (
                "En-tête de %s tronquée ? Seulement %d/%s octets lus" % (url, len(hdr), size_reste_hdr))
        i_deb = hdr.find (Vector.__hdr_startmark)
        if i_deb == -1:
            vec_file.close()
            raise AidaError (
                "Mauvais format : absence du marqueur début en-tête dans %s" % url)

        i_fin = hdr.find (Vector.__hdr_endmark)
        if i_fin == -1:
            message = "Mauvais format : manque marqueur fin en-tête dans %s" % url
            if strict:
                vec_file.close()
                raise AidaError (message)
            else:
                logger.warning (message)

        if i_fin <= i_deb:
            vec_file.close()
            raise AidaError (
                "Erreur de format : marqueurs fin avant début %s" % url)
        hdr_tab = hdr[i_deb+1:i_fin].decode('iso8859_15').split("\n")
        if len(hdr_tab) <= 1:
            vec_file.close()
            raise AidaError (
                "Mauvais format : en-tête trop court, moins de 2 lignes %s" % url)

        self.attributes = {}
        for lin in hdr_tab:
            lin = lin.strip()
            if lin.startswith('[') and lin.endswith(']'):
                self.attributes[Vector.hdr_name_key] = lin[1:-1]
                if self.name != lin[1:-1]:
                    pass
                continue
            champs = lin.split("=", 1)
            if len(champs) > 1:
                self.attributes[champs[0].strip()] = champs[1].strip()

        if attributes_only:
            vec_file.close()
            return

        if "format" not in self.attributes:
            vec_file.close()
            raise AidaError (
                     "Mauvais en-tête : manque attribut \"format\" %s" % url)
        dimension = int(self.attributes.get("dimension", 0))
        dtype_str = np_string(self.attributes["format"], dimension)
        try:
            nptypedef = np.dtype(dtype_str)
        except TypeError as excpt:
            raise AidaError ("Erreur du dtype %s construit à partir de %s" % (dtype_str, self.attributes["format"]))

        try:
            self.data = np.fromstring (vec_file.read(), dtype=nptypedef,
                                       count=-1)
            # Et pourquoi pas :
            #  self.data = np.fromfile (vec_file, dtype=nptypedef, count=-1) ?
        except ValueError as excpt:
            raise AidaError (
                     "Problème lecture donnés %s (dtype=%s) : %s" % (url, nptypedef, str(excpt)))
        finally:
            vec_file.close()

        # Les vecteurs peuvent être "big-endian" (historique) ou "little-endian" (depuis 04/2021).
        # En fonction de l'endianness de la machine et du vecteur, il faut ou non swapper les bites.
        vect_endianness = 'big'
        if 'endianness' in self.attributes and self.attributes['endianness'] == 'little' :
            vect_endianness = 'little'
        current_endianness = 'big'
        if np.little_endian :
            current_endianness = 'little'
        if vect_endianness !=  current_endianness :
            self.data = self.data.byteswap()
        
        # on convertit les bytes en unicode si besoin (impératif de le faire après un byteswap éventuel)
        try :
            if nptypedef.char == 'S' :
                self.data = self.data.astype('U')
        except :
            pass

        # et la forme...
        if "dim_array" in self.attributes:
            dim_array = self.attributes['dim_array'].strip()
            # Tolerance d'un , final (mais pas de ,,)
            if dim_array[-1] == ',':
                dim_array = dim_array[:-1]
            if len (dim_array) == 0 or dim_array == "1":
                # dim_array absent ou ==1 équivalents : pas de reshape
                self.attributes['dim_array'] = '1'
            else:
                shape = (self.attributes["dim_array"]).split('|')
                # split() renvoie toujours une liste, même a un seul élément
                try:
                    shape = [int(d) for d in shape]
                except ValueError as excpt:
                    raise AidaError (
                        "%s Mauvais en-tête : erreur decodage attribut \"dim_array\" %s" % (url, str(excpt)))
                shape.insert(0, -1)
                self.data = self.data.reshape(shape)
        else:
            # Standard vecteur : dim_array pas obligatoire, son absence
            # équivaut à "dim_array=1". On génère cette valeur par défaut
            # pour faciliter la tâche aux programmes.
            self.attributes["dim_array"] = "1"
        # Pour les types float/double, remplacement des misval par des NaN
        if self.misval_auto and (nptypedef == 'f' or nptypedef == 'd'):
            if "misval" in self.attributes and self.attributes['misval']:
                misval = np.array(self.attributes['misval'], dtype=nptypedef)
                self.data = np.where(self.data == misval, np.nan, self.data)

    def read (self, attributes_only, strict=True):
        """ Reads a vector.

            if attributes_only==True, doesn't read the data.
            if strict==True, raises an AidaError exception if vector marks are
            not perfect.

            @return nothing, but self.attributes and possibly self.data are
            read from disk.
        """

        self._readvect(self.storage_path, attributes_only, strict)

    def write (self, force=False, backup=False):
        """ Writes a vector """
        if "vol" not in self.attributes:
            self.attributes["vol"] = self.acq_id

        return self._write (force, backup)

    def timedata (self):
        """ Returns the time array associated to a vector.

            May raise an exception if self._ref_time.data) != len(self.data)
        """
        if self._ref_time:
            return self._ref_time.data
        if 'ref_time' not in self.attributes:
            unit = self.attributes.get('unit', '')
            fmt = self.attributes.get('format', '')
            if unit == 'second' and fmt == 'ieeefloat64':
                return self.data
            return None

        self._ref_time = Vector(self.acq_id,
                                self.attributes['ref_time'])

        if len(self._ref_time.data) != len(self.data):
            raise AidaError("len(%s) = %d, ref_time = %s, len=%d" % (self.name,
                len(self.data), self.attributes['ref_time'],
                len(self._ref_time.data)))
        return self._ref_time.data

    def header_utf_8(self):
        """ Tente d'encoder les valeurs du header (self.attributes) en utf-8.
        """

        try:
            for key, val in self.attributes.items():
                self.attributes[key] = val.encode('ISO8859-15').decode('utf-8')
        except Exception as e:
            pass

        return

    def synthese_diff(self, other):
        """ Caractérisation de la différence avec les données d'un autre
            vecteur.

            @param other : (Vector) le vecteur avec lequel comparer celui-ci.

            @return : (différence min, différence max, nombre de différences).

            @raise : AidaError si les données sont de longueurs différentes.
        """
        if len(self.data) != len(other.data):
            raise AidaError("données de longueurs différentes {s} {o}"
                            .format(s=len(self.data), o=len(other.data)))

        diffs = self.data - other.data
        return (np.nanmin(diffs),
                np.nanmax(diffs),
                (diffs != 0.).sum())

    def get_names(self) :
        """ Retourne les valeurs des champs name/english_name du vecteur.
            (ces champs ne sont pas obligatoires).
            Si ces champs sont absents ou vide, retourne leurs valeurs par
            défaut.

            :return: str(), str() : valeurs des champ name et english_name.
        """
        def_value = self.attributes.get('#hdr_name')

        fr_name = self.attributes.get('name'        , f"la variable {def_value}")
        en_name = self.attributes.get('english_name', f"the variable named {def_value}")

        if len(fr_name) == 0:
            fr_name = f"la variable {def_value}"
        if len(en_name) == 0:
            en_name = f"the variable named {def_value}"

        return fr_name, en_name


    def get_date_creation(self) :
        """ Retourne la date de création du vecteur contenue dans le header ou
            bien celle du fichier.

            @return : datetime ou None.
        """
        try : # format norme AIDA
            date_creation = datetime.datetime.strptime(self.attributes["date_creation"][:19], "%d/%m/%Y %H:%M:%S")
        except :
            try : # format incorrect AIDA.py (jusqu'au 20/10/2018)
                date_creation = datetime.datetime.strptime(self.attributes["date_creation"][:19], "%Y-%m-%d %H:%M:%S")
            except Exception as e : # date du fichier
                try :
                    time_modification = os.path.getmtime(self.storage_path)
                    date_creation = datetime.datetime.fromtimestamp(time_modification)
                    UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
                    date_creation = date_creation + UTC_OFFSET_TIMEDELTA
                except :
                    date_creation = None

        return date_creation


    def set_obs_min_max(self, data):
        """ Positionne, si possible, les champs 'obs_min' et 'obs_max'
            du header du vecteur.
        """
        hdr = self.attributes
        obs_min, obs_max = compute_obs_min_max(hdr, data)
        if obs_min and obs_max:
            hdr['obs_min'] = obs_min
            hdr['obs_max'] = obs_max

        return


class VectorMask(Vector):
    """ Classe qui hérite de la classe Vector.
       Elle surcharge la méthode read de façon à masquer le tableau data
       avec les valeurs manquantes.
    """
    def __init__ (self, acq_id, name, attributes=None, data=None,
                  attributes_only=False, overwrite=False, backup=False):
        """ Appelle le constructeur de la classe Vector puis on masque les datas """
        Vector.__init__(self, acq_id, name, attributes, data, attributes_only, overwrite, backup)
        self.maskData()

    def maskData(self):
        """ Masque les datas du vecteur avec la valeur de l'attribut misval.
            Pour le type float/double, les datas manquantes sont des NaN (positionnées par la classe Vector).
            Pour les autres types, si le type de l'attribut misval ne correspond pas au type des données (erreur dans le fichier de config)
            on masque avec les valeurs manquantes classiques (32000, -32000, -9999)

        """
        attr_misval = ""
        if "misval" in list(self.attributes.keys()):
            attr_misval = self.attributes['misval']
        try :
            nptypedef = self.data.dtype
        except :
            nptypedef = np.dtype('f')
        # la classe Vector remplace les valeurs manquantes par des NaN pour les float/double
        if nptypedef == 'f' or nptypedef == 'd':
            self.data = np.ma.masked_invalid(self.data)
        else:
            try:
                misval = np.array(attr_misval, dtype=nptypedef)
                if nptypedef.char == 'U':
                    def f(x, misval):
                        return x == misval
                    vfunc = np.vectorize(f)
                    result = vfunc(self.data, misval)
                    self.data = np.ma.array(self.data)
                    self.data.mask=result
                else :
                    self.data = np.ma.masked_equal(self.data, misval)
            except ValueError:
                # misval n'est pas du type des datas (erreur dans le fichier de config)
                # on masque avec les valeurs manquantes classiques
                if nptypedef.char == 'U':
                    self.data = np.ma.masked_where([x=="-32000" or x=="32000" or x=="-9999" for x in self.data], self.data)
                else:
                    self.data = np.ma.masked_where([x==-32000 or x==32000 or x==-9999 for x in self.data], self.data)

    def isempty(self):
        """ Retourne True si le vecteur est vide ou totalement masqué """
        if len(np.ma.compressed(self.data)) == 0:
            return True
        else:
            return False

    def write(self, force=False, backup=False, filepath=None):
        """ L'écriture d'un VectorMask ne doit rien faire à cause des valeurs masquées. """
        raise AidaError("objet de type VectorMask : pas d'écriture")

class PointRep(object):
    """  Pour les points de repères tels que définis dans la
      section [POINTS_CARACTERISTIQUES] des fichiers .inf d'AIDA
    """
    official_types = ('wpt', 'radar', 'balise', 'bouee', 'station', 'ville')

    def __eq__(self, other):
        """ En créant cette méthode, on permet le code suivant :
           a = PointRep(some_list)
           b = PointRep(some_list)
           >>> a is b
           False
           >>> a == b
           True
        """
        return (isinstance(other, self.__class__) and
                self.__dict__ == other.__dict__)

    def __init__(self, typ=None, nom=None, lat=None, lon=None, alt=None, inf_item=None):
        """ Deux possibilités d'appel :
              Soit avec tous les arguments explicites :
                p = PointRep(typ='wpt', nom="S1", lat=45.0, lon=-12.23)
              Soit avec un élément d'un fichier Inf
                p = PointRep(inf_item=('wpt', 'A1/N45d00.0/W179d59.94'))
        """
        if inf_item is not None:
            if any ((typ, nom, lat, lon, alt)):
                raise ValueError (
                      'Argument inf_item incompatible avec typ, nom, lat, lon, alt')
            self.from_inf_item(inf_item)
        else:
            if lat and (lat < -90 or lat > 90):
                raise ValueError ("|lat| > 90")
            if lon and (lon < -180 or lon > 180):
                raise ValueError ("|lon| > 180")
            if typ and typ not in PointRep.official_types:
                warnings.warn("Le type (%s) ne fait pas partie de la liste officielle" % str(typ))
            self.typ = typ
            if nom is None:
                self.nom = nom
            else:
                self.nom = str(nom)
            self.lat = lat
            self.lon = lon
            self.alt = alt

    def from_inf_item(self, inf_item):
        """ Décode un item de fichier .inf (un couple de chaîne
          (type, valeur) définissant un point de repère)

          Remplit les attributs typ, nom, lat, lon
          Lève une exception ValueError en cas de pb de format.
        """
        if len(inf_item) != 2:
            raise ValueError ("Mauvais argument")
        self.typ = inf_item[0].strip()
        point_str = inf_item[1].strip()
        if len(point_str) == 0:
            self.__init__()
            return
        point_fields = point_str.split('/')
        if len(point_fields) < 3:
            raise ValueError ("Moins de trois champs dans : " + point_str)
        if len(point_fields) > 4:
            raise ValueError ("Plus de quatre champs dans : " + point_str)
        self.nom = point_fields[0]
        lat_str = point_fields[1].strip()
        if len (lat_str) != 0:
            latflag = lat_str[0]
            if latflag not in 'NS':
                raise ValueError ("latflag autre que N/S dans " + lat_str)
            degmin = lat_str[1:].split('d')
            if len (degmin) < 2:
                raise ValueError ("'d' absent de lat " + lat_str)
            if len (degmin) > 2:
                raise ValueError ("trop de 'd' dans lat " + lat_str)
            latdeg = int(degmin[0])
            if latdeg > 90.0:
                raise ValueError ("lat > 90.0 dans " + lat_str)
            latmin = float(degmin[1])
            if latmin >= 60.0:
                raise ValueError ("minutes_lat >= 60.0 dans " + lat_str)
            self.lat = latdeg + latmin / 60.0
            if latflag == 'S':
                self.lat *= -1
        lon_str = point_fields[2].strip()
        if len (lon_str) != 0:
            lonflag = lon_str[0]
            if lonflag not in 'EW':
                raise ValueError ("lonflag autre que E/W dans " + lon_str)
            degmin = lon_str[1:].split('d')
            if len (degmin) < 2:
                raise ValueError ("'d' absent de lon " + lon_str)
            if len (degmin) > 2:
                raise ValueError ("trop de 'd' dans lon " + lon_str)
            londeg = int(degmin[0])
            if londeg > 180.0:
                raise ValueError ("lon > 180.0 dans " + lon_str)
            lonmin = float(degmin[1])
            if lonmin >= 60.0:
                raise ValueError ("minutes lon >= 60.0 dans " + lon_str)
            self.lon = londeg + lonmin / 60.0
            if lonflag == 'W':
                self.lon *= -1
        if len(point_fields) == 4:
            self.alt = float(point_fields[3].strip())
        else:
            self.alt = None

    @staticmethod
    def _fmt_latlon(typ, val):
        """ Fonction générique de formattage d'une lat ou d'une lon
          dans un fichier .inf  : <prefix><dd>d<mm>.<m>
        """
        if typ == 'lat':
            prefix_pos = 'N'
            prefix_neg = 'S'
            fmt = '%s%02dd%02d%s'
        elif typ == 'lon':
            prefix_pos = 'E'
            prefix_neg = 'W'
            fmt = '%s%03dd%02d%s'
        else:
            raise ValueError("typ(%s) devrait etre 'lat' ou 'lon'" % typ)

        if val > 0:
            prefix = prefix_pos
            val_abs = val
        else:
            prefix = prefix_neg
            val_abs = -val
        (deg_int, deg_dec) = divmod(val_abs, 1)
        (minu_int, minu_dec) = divmod(deg_dec * 60.0, 1)
        minu_dec_str = ('%#3f' % minu_dec)[1:]
        return fmt % (prefix, deg_int, minu_int, minu_dec_str)

    def to_inf_item(self):
        """ Produit un couple (nom, valeur) pouvant être
          inséré dans un objet Inf.
        """
        lat_str = self._fmt_latlon('lat', self.lat)
        lon_str = self._fmt_latlon('lon', self.lon)
        if self.alt:
            liste_champs = (self.nom, lat_str, lon_str, str(self.alt))
        else:
            liste_champs = (self.nom, lat_str, lon_str)
        point_str = '/'.join (liste_champs)
        return (self.typ, point_str)


class ParsingError(AidaError):
    """Raised when a .inf file does not follow legal syntax."""

    def __init__(self, filename):
        AidaError.__init__(self, 'File contains parsing errors: %s' % filename)
        self.filename = filename
        self.errors = []
        self.message = ""

    def append(self, lineno, line):
        """ Etend le message actuel avec le numéro de ligne, et une copie de la ligne"""
        self.errors.append((lineno, line))
        self.message += '\n\t[line %2d]: %s' % (lineno, line)

    def __repr__(self):
        return self.message


class MissingSectionHeaderError(ParsingError):
    """Raised when a key-value pair is found before any section header."""

    def __init__(self, filename, lineno, line):
        ParsingError.__init__(
            self,
            'File contains no section headers.\nfile: %s, line: %d\n%r' %
            (filename, lineno, line))
        self.filename = filename
        self.lineno = lineno
        self.line = line


def dt_total_seconds(timedelta):
    """ fonction de substitution à la methode total_seconds()
        d'un objet timedelta de datetime, qui n'existe pas en 2.6
    """
    return (timedelta.microseconds * 10**-6 +
            timedelta.seconds + timedelta.days * 24 * 3600.0)


class Inf(object):
    """  A class implementing AIDA's acquisition meta-data (".inf" files)

       Terminologie :
             un fichier .inf est constitué de sections
             chaque section contient des options

        Un fichier .inf est codé en ISO-8859-15 ou pas...
    """

    # sections obligatoires (cf doc format .inf)
    _mandatory_sections = {'FORMAT'           : [],
                           'IDENTIFICATION'   : ['plate-forme',
                                                 'acq_id'     ,
                                                 'date'       ,
                                                 'campagne'   ,
                                                ],
                           'PARAMETRES_ACQUIS': [],
                           'ACQUISITION'      : ['systeme_acquisition',
                                                 'debut_acquisition'  ,
                                                 'fin_acquisition'    ,
                                                 'media'              ,
                                                ],
                          }

    # Le nombre de champs de chaque définition de séquence
    # est clairement défini et ne va pas changer : on
    # peut en faire une constante de classe
    nb_champs_seq = {
        'palier': 8,
        'sondage': 8,
        'cercle': 6,
        'zoom': 9,
        'virage': 8,
        'station': 7,
        'sequence': 4,
    }

    # Regular expressions for parsing section headers and options.
    SECTCRE = re.compile(
        r'\['                                 # [
        r'(?P<header>[^]]+)'                  # very permissive!
        r'\]'                                 # ]
        )
    OPTCRE = re.compile(
        r'(?P<option>[^:=\s][^:=]*)'          # very permissive!
        r'\s*(?P<vi>[:=])\s*'                 # any number of space/tab,
                                              # followed by separator
                                              # (either : or =), followed
                                              # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
        )

    ENDSECT = "FIN"

    strict_parsing = True


    def __init__(self, acq_id=None):
        """
        Plusieurs cas de création d'un objet "Inf" sont possibles :
           - sans argument acq_id : création d'un objet vide
           - avec argument acq_id :
                - Si le fichier correspondant existe et est lisible,
                   l'objet est créé avec le contenu du fichier.
                - Si le fichier correspondant n'existe pas (read échoue
                   en IOError et errno=2), création d'un objet quasi-vide
                   dont l'attribut [IDENTIFICATION]/acq_id est le seul rempli
        """
        self._filename = ''
        self._sections = OrderedDict()
        if not acq_id:
            return
        self.acqid = acq_id

        try:
            self.read(acq_id)
        except IOError as excpt:
            # Si l'erreur est autre que "existe pas"
            if excpt.errno != 2:
                raise
            try:
                check_acq_id(acq_id)
            except AidaError:
                pass
            else:
                self._sections['IDENTIFICATION'] = {'acq_id': acq_id}


    def check_field_exists(self, sect_name, field):
        """ Raises KeyError if field "field" of section "sect_name"
        cannot be found in current "Inf" object
        """
        if self._filename:
            deb_msg = self._filename + ' : '
        else:
            deb_msg = ''
        if sect_name not in self._sections:
            raise KeyError('%sMissing section : %s' % (deb_msg, sect_name))
        if field not in self._sections[sect_name]:
            raise KeyError("%sMissing field %s in [%s]" %
                           (deb_msg, field, sect_name))

    def get_field_value(self, sect_name, field):
        """ Return the value of the field "field" in section "sect_name".
           Raises KeyError if field "field" of section "sect_name"
        cannot be found in current "Inf" object
           If there are multiple instances of "field" in the section,
        they are concatenated using ';' as a separator.
           Tries to return an unicode object.
        """
        try:
            self.check_field_exists(sect_name, field)
        except KeyError:
            return None
        encoding = 'ISO-8859-15'        # par definition dans un .inf (ou pas)
        val = self._sections[sect_name][field]
        if isinstance(val, list):
            val = ';'.join(val)
        try:
            ustr = val
        except UnicodeDecodeError:
            ustr = val
        return ustr

    def iter_items_str(self, nom_sect='SEQUENCES', list_noms_sel=None):
        """ Une fonction-generator qui permet de parcourir l'ensemble
        des (noms, valeurs) définies dans une section d'un objet "Inf" (en
        considérant que chaque section est constituée d'une série
        de <nom>=<valeur>;)

        list_noms_sel : une liste (ou un n-uplet) de noms
          à sélectionner. Par exemple :
             - None si on souhaite toutes les valeurs
             - ('machin') si on ne souhaite que les attributs "machin=valeur;"

        """
        if not nom_sect.isupper():
            warnings.warn("Nom de section pas en majucule ? (%s)" % nom_sect)
        if nom_sect not in self._sections:
            return
        for att_name, att_val in self._sections[nom_sect].items():
            if att_name == '__name__':
                continue
            if list_noms_sel is not None:
                if att_name not in list_noms_sel:
                    continue
            if isinstance(att_val, str):
                yield ((att_name, att_val))
            else:
                for single_val in att_val:
                    yield ((att_name, single_val))

    def iter_items_list(self, nom_sect='SEQUENCES', list_noms_sel=None):
        """ Une fonction-generator qui permet de parcourir l'ensemble
        des listes de valeurs associées à des "noms" dans une
        section de fichier .inf
        """
        if not nom_sect.isupper():
            warnings.warn("Nom de section pas en majucule ? (%s)" % nom_sect)
        if nom_sect not in self._sections:
            return
        for att_name, att_val in self._sections[nom_sect].items():
            if att_name == '__name__':
                continue
            if list_noms_sel is not None:
                if att_name not in list_noms_sel:
                    continue
            if isinstance(att_val, list):
                yield ((att_name, att_val))
            else:
                yield ((att_name, [att_val]))

    def set_field_value(self, sect_name, field, value):
        """ Sets the value of the field "field" in section "sect_name".
            Value should be a string : unicode, or basic encoded in latin9
        """
        if not sect_name.isupper():
            warnings.warn("Nom de section pas en majucule ? (%s)" % sect_name)

        # Un fichier .inf est codé en ISO-8859-15 ou pas

        if sect_name not in self._sections:
            self._sections[sect_name] = {field: value}
        else:
            self._sections[sect_name][field] = value

    def add_field_value(self, sect_name, field, value):
        """ La même chose que `set_field_value` mais pour les options à valeur
            multiple comme POINTS_CARACTERISTIQUES::wpt ou PERSONNEL::operateur.
        """
        if not sect_name.isupper():
            warnings.warn("Nom de section pas en majucule ? (%s)" % sect_name)

        if sect_name not in self._sections:
            self._sections[sect_name] = {field: [value]}
        else:
            self._sections[sect_name][field].append(value)

    def read(self, acq_id):
        """ Reads the .inf file corresponding to a specific acquisition.

            May raise an IOError exception if it's impossible to open/read the
            file.

            Les fichiers .inf _devraient_ être en `iso-8859-1` mais certains
            sont en `utf-8`, `ASCII`... De plus ils contiennent parfois dus
            texte qui est mal encodé...
        """
        inf_file_path = ID_to_inf_path(acq_id)
        fp = codecs.open(inf_file_path, 'r', 'iso-8859-1')

        try:
            self._read(fp, acq_id + '.inf')
        except:
            print('ENCODAGE MAUVAIS')
            raise ValueError("ENCODAGE MAUVAIS")

        fp.close()
        self.check_field_exists('IDENTIFICATION', 'acq_id')
        if acq_id != self._sections['IDENTIFICATION']['acq_id']:
            raise ValueError("acq_id in IDENTIFICATION differs from name")

    def _read(self, fp, fpname):
        """Parse a ".inf" file.

        The sections in ".inf" file contains a title line at the top,
        indicated by a name in square brackets (`[]'), plus key/value
        options lines, indicated by `name = value' format lines.
        The value can run on multiple lines, and is ended by ';'
        Blank lines, and just about everything else are ignored.

        *Le configparser de python ne permet pas de gérer les options à valeurs
        multiples (comme wpt, operateur...)*
        => The code of this method is largely inspired from the _read method
        in the ConfigParser package of python 2.6.

        Gestion des commentaires :
        Si le fichier lu contient des lignes commençant par '#', elles sont
        enregistrées dans le dictionnaire `self.comments` :
        - dans la liste `__name__`, si le commentaire est juste en dessous de
          la ligne de déclaration d'une section
        - dans la liste <optname>, si le commentaire est juste en dessous d'une
          ligne de déclaration d'une d'option.
        Si la section ou l'option était supprimée du dictionnaire
        'self._sections' alors les commentaires qui sont attachés à la section
        ou à l'option ne seraient pas ré-écrit par _write().

        Les fichiers .inf _devraient_ être en `iso-8859-1` mais certains sont
        en `utf-8`, `ASCII`.. De plus ils contiennent parfois du texte qui
        est mal encodé...
        """
        self._filename = fpname
        self.acqid     = os.path.splitext(fpname)[0]
        self.comments  = dict()

        sectname     = None
        cursect      = None         # None, or a dictionary
        optname      = None
        lineno       = 0
        e            = None         # None, or an exception
        unended_line = False
        for line in fp:
            line = line.strip('\n')
            try:
                # gestion des _mixing encoding_
                line = line.encode('ISO-8859-1').decode('utf-8')
            except UnicodeDecodeError:
                pass

            # BOM ?
            if lineno == 0:
                if line.startswith('\xef\xbb\xbf'):
                    e = ParsingError(fpname)
                    e.append(lineno, "File starts with a utf-8 BOM")
                    if self.strict_parsing:
                        break
                    else:
                        line = line[3:]
                        continue
                if line.startswith('\xfe\xff') or line.startswith('\xff\xfe'):
                    e = ParsingError(fpname)
                    e.append(lineno, "File starts with a utf-16 BOM")
                    if self.strict_parsing:
                        break
                    else:
                        line = line[2:]
                        continue

            lineno = lineno + 1

            # continuation line ?
            if unended_line:
                value = line.strip()
                pos = value.find(';')
                if pos != -1:
                    value = value[:pos]
                    unended_line = False
                if isinstance(cursect[optname], list):
                    cursect[optname][-1] = "%s\n%s" % (cursect[optname][-1],
                                                       value)
                else:
                    cursect[optname] = "%s\n%s" % (cursect[optname], value)
                continue

            # blank line ?
            if line.strip() == '':
                continue

            # comment ?
            if line[0] in '#;':
                # mémoriser les commentaires pour pouvoir les réécrire dans
                # la méthode _write().
                if sectname:
                    if not sectname in self.comments:
                        self.comments[sectname] = dict()
                        self.comments[sectname]['__name__'] = list()

                    if not optname:
                        self.comments[sectname]['__name__'].append(line)
                    else:
                        if not optname in self.comments[sectname]:
                            self.comments[sectname][optname] = list()
                        self.comments[sectname][optname].append(line)
                continue

            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                # no leading whitespace
                continue
            else:
                # a section header or option header?

                # is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if sectname in self._sections:
                        cursect = self._sections[sectname]
                    elif sectname == self.ENDSECT:
                        break
                    else:
                        cursect = {}
                        cursect['__name__'] = sectname
                        self._sections[sectname] = cursect
                    # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        if vi in ('=', ':') and ';' in optval:
                            # ';' is a comment delimiter only if it follows
                            # a spacing character
                            pos = optval.find(';')
                            optval = optval[:pos]
                        else:
                            unended_line = True
                        optval = optval.strip()
                        # allow empty values
                        if optval == '""':
                            optval = ''
                        optname = optname.rstrip()
                        if optname in cursect:
                            if isinstance(cursect[optname], list):
                                cursect[optname].append(optval)
                            else:
                                cursect[optname] = [cursect[optname], optval]
                        else:
                            cursect[optname] = optval
                    else:
                        # a non-fatal parsing error occurred. Set up the
                        # exception but keep going. The exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, repr(line))
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

    def _write(self, fp):
        """ Écrit dans le flux "fp" les meta-données d'acquisition
         contenues dans l'objet "Inf" courant, en respectant le format
         des fichiers .inf
        """
        # le tout premier caractère du fichier n'a pas à être un '\n'...
        first_char = ''
        for nom_sect in self._sections.keys():
            if not isinstance(nom_sect, str):
                fp.write('\n#Ignored [%s]\n' % str(nom_sect))
                continue
            fp.write('%s[%s]\n' % (first_char, nom_sect))
            first_char = '\n'

            # ajouter les commentaires
            if nom_sect   in self.comments and \
               '__name__' in self.comments[nom_sect]:
                for c in self.comments[nom_sect]['__name__']:
                    fp.write('%s\n' % c)

            sect = self._sections[nom_sect]
            field_len = max([len(x) for x in list(sect.keys()) \
                                        if isinstance(x, str)])
            fmt_ligne = '%%-%ds = %%s;\n' % field_len
            for attribut in sect.keys():
                valeur = sect[attribut]
                if not isinstance(attribut, str):
                    fp.write('#Ignored %s = %s\n' % \
                             (str(attribut), str(valeur)))
                    continue
                if attribut == '__name__':
                    continue
                if valeur is None:
                    fp.write(fmt_ligne % (attribut, ''))
                elif isinstance(valeur, list):
                    for elt in valeur:
                        fp.write(fmt_ligne % (attribut, elt))
                else:
                    fp.write(fmt_ligne % (attribut, valeur))
                # ajouter les commentaires
                if nom_sect in self.comments and \
                   attribut in self.comments[nom_sect]:
                    for c in self.comments[nom_sect][attribut]:
                        fp.write('%s\n' % c)

        fp.write('\n[%s]\n' % self.ENDSECT)

    def write(self, force=False, strict_opt=True):
        """ Écrit sous la forme d'un fichier .inf avec le nom standard
         les meta-données d'acquisition contenues dans l'objet "Inf" courant

         :param bool strict_opt:

            Si True  : raise une exception si une options
                       obligatoires n'est pas présentes.
            Si False : affiche un warning  si une options
                       obligatoires n'est pas présentes.
        """
        self.check_field_exists('IDENTIFICATION', 'acq_id')
        acq_id = self._sections['IDENTIFICATION']['acq_id']
        inf_fic_path = ID_to_inf_path(acq_id)


        # vérification de la présence des sections obligatoires
        for sect_name, opt_list in self._mandatory_sections.items():
            if not sect_name in self._sections.keys():
                if strict_opt:
                    raise KeyError('%s : missing mandatory section : %s' %
                                    (inf_fic_path, sect_name))
                else:
                    warning('%s : missing mandatory section : %s' %
                                    (inf_fic_path, sect_name))
                    continue # ne pas passer dans le for qui suit !

            for opt in opt_list:
                if not opt in self._sections[sect_name].keys():
                    if strict_opt:
                        raise KeyError('%s : missing mandatory option : %s in %s'%
                                        (inf_fic_path, opt, sect_name))
                    else:
                        warning('%s : missing mandatory option : %s in %s'%
                                        (inf_fic_path, opt, sect_name))


        if force:
            inf_fic = open(inf_fic_path, "w")
        else:
            # Ouverture explicite en mode "write", mais sans
            # écrasement possible :
            try:
                fd = os.open(inf_fic_path,
                             os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                             0o664)
            except OSError:
                return
            inf_fic = os.fdopen(fd, "w")
        self._write(inf_fic)
        inf_fic.close()

    def set_date_acq(self, jour, mois, annee):
        """ Fixe la date du démarrage de l'acquisition décrite
        dans l'objet "Inf" actuel.
        """
        if isinstance(annee, int):
            cr = year_in_aida_range(annee)
            if cr:
                raise ValueError(cr.encode('ascii', 'ignore'))
            annee_str = '%4d' % annee
        else:
            annee_str = str(annee)
        # Vérifier correspondance annee<->acq_id
        try:
            self.check_field_exists('IDENTIFICATION', 'acq_id')
        except KeyError:
            pass
        else:
            acq_id = self._sections['IDENTIFICATION']['acq_id']
            if acq_id[2:4] != annee[2:4]:
                raise ValueError("année[2:4] != acq_id[0:2] : %s != %s " %
                                 (annee[2:4], acq_id[2:4]))

        if mois is None:
            mois_str = 'MM'
        else:
            if isinstance(mois, int):
                if mois < 1:
                    raise ValueError("Numéro de mois <= 0")
                if mois > 12:
                    raise ValueError("Numéro de mois > 12")
                mois_str = '%02d' % mois
            else:
                mois_str = str(mois)

        if jour is None:
            jour_str = 'JJ'
        else:
            if isinstance(jour, int):
                if jour < 1:
                    raise ValueError("Numéro de jour <= 0")
                if jour > 31:
                    raise ValueError("Numéro de mois > 31")
                jour_str = '%02d' % jour
            else:
                jour_str = str(jour)

        self.set_field_value('IDENTIFICATION', 'date',
                             "%s/%s/%s" % (jour_str, mois_str, annee_str))

    def get_date_acq(self):
        """ Donne la date du démarrage de l'acquisition décrite dans l'objet
            'Inf' actuel.

            Il s'agit du champ : [IDENTIFICATION]/date
            et non pas         : [ACQUISITION]/debut_acquisition

            On considere que la date d'une acquisition est une information
            importante, donc on leve une exception en cas d'absence ou de
            probleme de decodage.

            @return un objet date du package datetime
        """
        self.check_field_exists('IDENTIFICATION', 'date')
        value = self._sections['IDENTIFICATION']['date']
        if not value:
            raise ValueError("date vide")
        try:
            dt_object = dt.datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            try:
                dt_object = dt.datetime.strptime(value, "%d/%m/%y")
            except ValueError:
                raise ValueError("%s, date indecodable : %s" %
                                 (self._filename, value))
        return dt.datetime.date(dt_object)

    def get_acquisition_borne(self, name):
        """ Lit et décode un des champs horaires de la section [ACQUISITION].

            Typiquement, name est soit 'debut_acquisition', soit
            'fin_acquisition'.

            @return un objet datetime du package datetime, ou None en cas
            d'absence.

            Peut lever une exception ValueError si la date/l'heure est
            indecodable.
        """
        try:
            self.check_field_exists('ACQUISITION', name)
        except KeyError:
            return None
        value = self._sections['ACQUISITION'][name]
        if not isinstance(value, str):
            raise ValueError("field %s in [%s] ! " % (name, 'ACQUISITION'))
        value = value.strip()
        if not value:
            return None
        if len(value) == 6:
            try:
                dt_object = dt.datetime.strptime(value, '%H%M%S')
            except ValueError as excpt:
                raise ValueError(self._filename + " : " + str(excpt))
            time = dt.datetime.time(dt_object)
            try:
                date = self.get_date_acq()
            except KeyError:
                pass
            dt_object = dt.datetime.combine(date, time)
        elif len(value) < 17:
            raise ValueError("%s : champ %s trop court %s" %
                             (self._filename, name, value))
        elif len(value) == 17:
            # Format "traditionnel"
            try:
                dt_object = dt.datetime.strptime(value, '%d/%m/%Y/%H%M%S')
            except ValueError as excpt:
                # Tentative de récupération du cas : HH hors de [0:23)]
                try:
                    heure_i = int(value[11:13])
                except ValueError:
                    raise ValueError(self._filename +
                                     " : Bug HH " + str(excpt))
                if heure_i >= 0 and heure_i < 24:
                    # L'erreur ne vient pas de HH
                    raise ValueError(self._filename + " : " + str(excpt))
                jour_plus, heure_cor = divmod(heure_i, 24)
                cor = value[:11] + '%02d' % heure_cor + value[13:]
                try:
                    dt_object = dt.datetime.strptime(cor, '%d/%m/%Y/%H%M%S')
                except ValueError:
                    raise
                dt_object += dt.timedelta(days=jour_plus)
        elif len(value) <= 19:
            # Acceptation du format ISO8601, qui a un 'T' entre la date
            # et l'heure, et éventuellement un 'Z' à la fin pour dire 'UTC"
            try:
                dt_object = dateutil.parser.parse(value)
            except ValueError as excpt:
                raise ValueError(self._filename + " : " + str(excpt))
        else:
            raise ValueError(self._filename +
                             " : champ heure trop long " + value)
        cr = year_in_aida_range(dt_object.year)
        if cr:
            raise ValueError(self._filename +
                             ' : ' + cr.encode('ascii', 'ignore'))
        return dt_object

    def get_horaire(self, name):
        """ Lit et décode un des champs de la section [HORAIRES_UTC].

            @return un objet datetime du package datetime, ou None en cas
            d'absence.

            Peut lever une exception ValueError si la date/l'heure est
            indecodable.
        """
        try:
            self.check_field_exists('HORAIRES_UTC', name)
        except KeyError:
            return None
        value = self._sections['HORAIRES_UTC'][name]
        if not isinstance(value, str):
            raise ValueError("field %s in [%s] ! " % (name, 'HORAIRES_UTC'))
        value = value.strip()
        if not value:
            return None
        if len(value) <= 5:
            raise ValueError(self._filename +
                             " : champ heure trop court " + value)
        if len(value) == 6:
            decal_jour = 0
            try:
                dt_object = dt.datetime.strptime(value, '%H%M%S')
            except ValueError as excpt:
                # 2 cas : soit champs foireux, soit HH >= 24.
                # On essaye de récupérer le second cas.
                try:
                    heure = int(value[:2])
                except ValueError as excpt:
                    raise ValueError(self._filename + " : " + str(excpt))
                decal_jour, heure = divmod(heure, 24)
                try:
                    dt_object = dt.datetime.strptime(value[2:], '%M%S')
                except ValueError as excpt:
                    raise ValueError(self._filename + " : " + str(excpt))
                dt_object = dt_object.replace(hour=heure)
            time = dt.datetime.time(dt_object)

            try:
                date = self.get_date_acq()
            except KeyError:
                pass
            dt_object = dt.datetime.combine(date, time)
            if decal_jour:
                dt_object = dt_object + dt.timedelta(days=decal_jour)
            # N'oublions pas une petite particularité du format .inf :
            # Si le champ "atterrissage" ne contient que HHMMSS
            # et que, si on l'affecte au jour d'acquisition, il se
            # retrouve avant le décollage, on considère qu'il
            # a eu lien le lendemain.
            if name == 'atterrissage':
                heure_deb = None
                try:
                    heure_deb = self.get_horaire('decollage')
                except ValueError:
                    pass
                if heure_deb:
                    if heure_deb > dt_object:
                        dt_object += dt.timedelta(days=1)

        elif len(value) > 10:
            dt_object = dt.datetime.strptime(value, '%d/%m/%y %H%M%S')
        else:
            raise ValueError(self._filename +
                             ", champ heure trop long :" + value)
        return dt_object

    def get_sequence_times(self, name):
        """ Lit et décode les champs debut/fin d'une sequence
        de la section [SEQUENCES]

        @return une paire d'objets datetime du package datetime
        """
        for (_, seq_str) in self.iter_items_str('SEQUENCES'):
            champs = seq_str.split('/')
            if champs[0] != name:
                continue
            if len(champs) < 3:
                raise ValueError("Champs manquants dans sequence %s : %s" %
                                 (name, seq_str))
            time_deltas = [None, None]
            for idx in (1, 2):
                if len(champs[idx]) != 6:
                    raise ValueError("heure invalide : " + champs[idx])
                time_deltas[idx - 1] = dt.timedelta(seconds=hhmmss_to_sec(champs[idx]))
            dt_objects = [None, None]
            try:
                acq_date = dt.datetime.combine(self.get_date_acq(),
                                               dt.time(0))
                dt_objects[0] = acq_date + time_deltas[0]
                dt_objects[1] = acq_date + time_deltas[1]
            except KeyError:
                pass
            if dt_objects[0] > dt_objects[1]:
                dt_objects[1] = dt_objects[1] + dt.timedelta(days=1)
            return dt_objects
        raise KeyError('Sequence ' + name + ' not found')

    def datetime_to_sec(self, dt_obj):
        """ Transforme un objet datetime en temps AIDA de l'acquisition :
            le nombre de secondes depuis 0h00 le jour du démarrage.

            Utilisation typique :
            sec_dec = inf_obj.datetime_to_sec (inf_obj.get_horaire('decollage'))
        """
        dt_ref = dt.datetime.combine(self.get_date_acq(), dt.time(0))
        nb_sec = dt_total_seconds(dt_obj - dt_ref)
        # A remplacer par la ligne suivante dès que python 2.6 est mort.
        # nb_sec = (dt_obj - dt_ref).total_seconds()
        nb_sec = dt_total_seconds(dt_obj - dt_ref)
        return nb_sec


def existing_inf_files(liste_divers, liste_camp=(), liste_annees=(), names_only=False, very_verbose=True):
    """ Generator qui permet de parcourir la liste des fichiers .inf existants
        pour un ensemble d'acq_id ou de plate-formes.

        Paramètres obligatoire :

        - liste_divers = un ensemble d'acq_id ou de plate-formes.

        Paramètres optionnels :

        - liste_camp   = une liste des campagnes auxquelles on veut se limiter :
                         iterable de chaines de caractères (ne s'applique qu'à
                         la recherche par plate-forme).
        - liste_annes  = une liste des annees auxquelles la recherche sera
                         limitée :
                         liste ou n-nuplet d'entiers ou de chaines, sur deux ou
                         4 chiffres (ne s'applique qu'à la recherche par
                         plate-forme).
        - names_only   = Si False, les .inf sont lus
                         Si True , les .inf ne sont pas lus.
        - very_verbose = Si True, traces maximales  sur ParsingError
                         Si False, traces minimales sur ParsingError

        Usage typique :

        >>>
            liste_plt = ('merlin', 'arat')
            for inf_obj in AIDA.existing_inf_files(liste_plt):
                do_something(inf_obj)
        >>>
    """

    liste_abrev = liste_plt_to_abrev(liste_divers)
    liste_acq_id = []
    liste_non_rec = []
    for (abrev, nom) in zip(liste_abrev, liste_divers):
        if abrev is not None:
            continue
        try:
            plt, annee, num = ID_to_full(nom)
        except (KeyError, AidaError):
            liste_non_rec.append(nom)
        liste_acq_id.append(nom)
    if liste_non_rec:
        print("argument(s) ni acq_id, ni plate-forme :",
              ", ".join(liste_non_rec),
              file=sys.stderr)

    inf_file_dir = os.path.join(AIDA_getenv('meta'), 'INF')
    try:
        list_files_in_inf_dir = os.listdir(inf_file_dir)
    except OSError as excpt:
        print("Pas possible d'ouvrir %s : %s" %
              (inf_file_dir, excpt.strerror), file=sys.stderr)

    liste_aa = [annee_2_car(x) for x in liste_annees]

    for filename in list_files_in_inf_dir:
        if not filename.endswith('.inf'):
            continue
        if len(filename) < 9 or  len(filename) > 12:
            continue
        # si le filename correspond à un acq_id explicitement demandé, on peut
        # passer à la lecture.
        # Sinon, il faut tester si l'année et la plate-forme correspondent.
        if filename[:-4] not in liste_acq_id:
            if filename[0:2] not in liste_abrev:
                continue
            if liste_aa:
                if filename[2:4] not in liste_aa:
                    continue


        if names_only:
            yield os.path.splitext(filename)[0]
            continue


        try:
            stream = open(os.path.join(inf_file_dir, filename), 'r',
                          encoding='ISO-8859-1')
        except IOError as excpt:
            print("Pas possible d'ouvrir %s : %s" %
                  (filename, excpt.strerror), file=sys.stderr)
            continue
        inf_obj = Inf()
        try:
            inf_obj._read(stream, filename)
        except ParsingError as excpt:
            print("Erreur de décodage de %s : %s" %
                  (filename, str(excpt)), file=sys.stderr)
            if very_verbose:
                print(excpt.message, file=sys.stderr)
            stream.close()
            continue
        stream.close()

        campagne = inf_obj.get_field_value('IDENTIFICATION', 'campagne')
        if not campagne:
            continue
        if liste_camp and campagne not in liste_camp:
            #TODO? Faire aussi une comparaison case-insensitive ?
            continue

        yield inf_obj

def read_data(acqId, param, ordinal=False, header_utf_8=False):
    """ Lit un vecteur et son ref_time.
        Retourne le tuple (data, time, header)

        :acqId:        identifiant d'acquisition
        :param:        paramètre associé au vecteur
        :ordinal:      précise le format de temps retourné :
                         True=ordinal,
                         False=datetime(défaut)
        :header_utf_8: appelle Vector.:header_utf_8() pour tenter d'encoder 
                       le header en utf-8

        :return: data, time, header
        :rtype:  tuple(numpy.ma.core.MaskedArray,
                       numpy.ma.core.MaskedArray,
                       dict)
    """
    try:
        vect = VectorMask(acqId, param, overwrite=True)
    except IOError as excpt:
        print("-+- Jour vide pour %s de %s: " % (param, acqId), str(excpt))
        return (None, None, None)

    if 'ref_time' not in vect.attributes:
        # si c'est un vecteur temps les datas font aussi office de temps
        if vect.attributes['#hdr_name'].startswith("rft_time") :
            return (vect.data, vect.data, vect.attributes)
        else :
            return (vect.data, None, vect.attributes)
    ref_time = vect.attributes['ref_time']
    vect_time = VectorMask(acqId, ref_time, overwrite=True)
    if len(vect_time.data) != len(vect.data):
        print("--- len(%s) = %d, ref_time = %s, len=%d" %
              (param, len(vect.data), ref_time, len(vect_time.data)))
        return (None, None, None)

    try :
        date_acq = Inf(acqId).get_date_acq()
    except Exception :
        print("-+- Erreur de lecture du fichier INF pour {}.".format(acqId))
        return (None, None, None)
    data_time = []
    datetime_acq = datetime.datetime(date_acq.year,
                                     date_acq.month,
                                     date_acq.day)
    if ordinal : # on retourne un time format ordinal
        data_time = datetime_acq.toordinal() + vect_time.data / 86400.0
    else :# on retourne un time format datetime
        data_time_acq = np.full(len(vect_time.data),datetime_acq,
                                dtype="datetime64[us]")
        time_delta = (vect_time.data*1000000).astype("timedelta64[us]")
        data_time = (data_time_acq + time_delta).astype(datetime.datetime)

    if header_utf_8:
        vect.header_utf_8()

    return (vect.data, np.array(data_time), vect.attributes)

def read_datas(acqIdStart, param, acqIdEnd=None, ordinal=False, header_utf_8=False) :
    """
        Lit les vecteurs et les ref_time pour la période définie par
        acqIdStart et acqIdEnd.
        Retourne le tuple (data, time, header) :

        On boucle sur les acqid (read_data) et on construit par concaténation
        des MaskedArray big_data et big_time.
        Le header retourné est le header du premier vecteur lu.

        :acqIdStart:   identifiant d'acquisition de début
        :param:        paramètre associé aux vecteurs
        :acqIdEnd:     identifiant d'acquisition de fin
                       (si None, acqIdEnd=acqIdStart)
        :ordinal:      précise le format de temps retourné :
                         True=ordinal
                         False=datetime(défaut)
        :header_utf_8: appelle Vector.:header_utf_8() pour tenter d'encoder 
                       le header en utf-8

        :return: data, time, header
        :rtype:  tuple(numpy.ma.core.MaskedArray,
                       numpy.ma.core.MaskedArray,
                       dict)
    """
    if acqIdEnd is None :
        acqIdEnd = acqIdStart
    big_data = None
    big_time = None
    big_header = None

    acqid_debut = AcqId.AcqId(acqIdStart)
    acqid_fin = AcqId.AcqId(acqIdEnd)
    acqid = acqid_debut
    if acqid_debut > acqid_fin :
        print("Erreur : acqIdStart > acqid_fin")
        return (None, None, None)

    while acqid <= acqid_fin :
        data, time, header = read_data(str(acqid), param, ordinal, header_utf_8=header_utf_8)
        if data is None :
            acqid += 1
            continue
        if big_header is None :
            big_header = header
        if big_data is None :
            big_data = data
        else :
            big_data = np.ma.concatenate([big_data, data])
        if big_time is None :
            big_time = time
        else :
            big_time = np.ma.concatenate([big_time, time])
        acqid += 1

    return(big_data, big_time, big_header)

def time_to_data_bnds(acqid, rft_time, show_msg=True):
    """
        Lit rft_time, décode time_bnds (ou bornes_temps pour compatibilité) et retourne un tableau à 2
        dimensions contenant les 2 bornes à chaque pas de temps.

        :acqid: identifiant d'acquisition
        :rft_time: nom du vecteur temps
        :return: tableau de bornes
        :rtype: numpy array de dimension len(data_time),2

        ATTENTION : retourne un np.array OU un np.ma.array !!!
    """
    # Lecture du vecteur temps
    data_time, time, header = read_datas(acqid, rft_time)
    if data_time is None :
        return None
    try :
        time_bnds = header['time_bnds']
    except :
        try :
            # compatibilite avec ancienne syntaxe
            time_bnds = header['bornes_temps']
            time_bnds = "vector:"+time_bnds
        except :
            # pas de bornes de temps définies : on date en fin de période.
            if show_msg:
                print("--- Pas de time_bnds ou de bornes_temps dans le vecteur temps {}".format(rft_time))
                print("--- On date en fin de période par défaut.".format(rft_time))
            data_bnds = np.empty( (len(data_time), 2) )
            data_bnds [0, 0] = data_time[0] - (data_time[1] -data_time[0])
            data_bnds [1:, 0] = data_time[0:-1]
            data_bnds [:, 1] = data_time[:]
            return data_bnds
    if len(time_bnds.split(',')) == 2 :
        # construction des datas avec les bornes calculées
        start_bound = float(time_bnds.split(',')[0])
        end_bound = float(time_bnds.split(',')[1])
        data_bnds = [[t+start_bound, t+end_bound] for t in data_time]
        return np.array(data_bnds)
    elif len(time_bnds.split(':')) == 2 :
        # lecture du vecteur time_bnds
        try :
            vecteur_bnds = time_bnds.split(':')[1]
            data_bnds, time, header = read_datas(acqid, vecteur_bnds)
            if header['dim_array'] != '2' :
                if show_msg:
                    print("--- Erreur : le vecteur bnds {} n'est pas de dimension 2.".format(vecteur_bnds))
                return None
            return data_bnds
        except :
            if show_msg:
                print("--- Erreur : impossible de lire le vecteur bnds {}".format(vecteur_bnds))
            return None
    else :
        return None

SIMPLE_TEST = """[SIMPLE]
a=b;

# Commentaire
[DOUBLE]
x=t;
x=rr;

; Autre commentaire
[MULTI_LIGNES]
x=ff
gg;
"""

MINI_INF = """[IDENTIFICATION]
plate-forme = atr;
acq_id = as120042;
date = 02/10/2012;

[HORAIRES_UTC]
depart_parking = ;
decollage = 194315;
atterrissage = 220732;

[SEQUENCES]
#palier = name/hms_deb/hms_fin/wpt_deb/wpt_fin/cap/alt/comment;
palier = P1/200505/201005/A/B/270/350ft/palier bidon pour test;
[FIN]"""


def test():
    """ Rassembler les tests ici """
    import io

    flux = io.StringIO(SIMPLE_TEST)
    x = Inf()
    x._read(flux, "SIMPLE_TEST")
    print(x._write(sys.stdout))

    flux = io.StringIO(MINI_INF)
    x = Inf()
    x._read(flux, "MINI_INF")
    print(x.get_horaire('decollage'))
    print(x.get_horaire('atterrissage'))
    print(x.get_date_acq())

    s_time = x.get_sequence_times('P1')
    for idx in (0, 1):
        if not isinstance (s_time[idx], dt.datetime):
            print("type(", str(s_time[idx]), ") is not dt.datetime : ", type(s_time[idx]))
    # print x.get_sequence_times('P2')

    print(hhmmss_to_sec("120000") == 43200)
    print(hhmmss_to_sec("24:00:00.1", ":") == 86400.1)
    string_result = io.StringIO()
    x._write(string_result)
    # print string_result.getvalue()
    print(liste_plt_to_abrev(('arat', 'atalante', 'atr')))

#    print "Nb plate-formes connues ", len(plt_by_name)
#    print len(plt_by_name) >= len(plt_by_abrev )
#    print sorted(plt_by_name.keys())

    print(AIDA_abrev_to_plt("as"))
    print(AIDA_nom_long_to_abrev("atr"))

    start = 15500.0
    n = 100
    freq = 2.0
    temps = np.arange(start, start + n / freq, 1.0 / freq)

    ecrit_diagno_temps (temps)
    temps[n//2] = temps[n//2+1]
    print(diagno_temps (temps))
    ecrit_diagno_temps (temps)
    temps[n//2] = temps[n//2-2]
    print(diagno_temps (temps))
    ecrit_diagno_temps (temps)
    for lon in (-179.999, -0.0001, 0.0, 1.00, 22.222):
        point_obj = PointRep(typ='wpt', nom="A1", lat=45.0, lon=lon)
        paire = point_obj.to_inf_item()
        second_point_obj = PointRep(inf_item=paire)
        print (paire)
        if not second_point_obj == point_obj:
            print(point_obj.to_inf_item(), second_point_obj.to_inf_item())
            print(point_obj.__dict__, second_point_obj.__dict__)

    for nom_dangereux in ("", "a+B=X'", "a&b%10°"):
        print (nom_dangereux, clean_for_name(nom_dangereux))

# Lors du chargement du package, initialisation
# de la liste des plate-formes connues, et des index.
try:
    ini_plt_indexes()
except IOError as excpt:
    warnings.warn ("Erreur d'I/O lors lecture initiale fichier plate-formes({0}): {1}".format(excpt.errno, excpt.strerror))

if __name__ == '__main__':
    test()
