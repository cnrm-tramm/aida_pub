#!/usr/bin/env python3

""" Génération d'un graphe de généalogie de vecteur en graphviz/dot.

    La génération du fichier final est assurée par la commande `dot`.
"""

__version__ = '2.0.0'

import sys
import os
import pwd
import argparse
import copy


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
from fct_messages import (info, warning, stop_error, result, wait_user)
import Units
from Fil_analyze import parse_instruction

from AIDAcalc.FVB2ADC   import fvb2adc
from AIDAcalc.OperTypes import OperTypes, get_OperType


# description des operateurs C
import oper_API_PY_desc
desc_opers_C = oper_API_PY_desc.oper_API_PY_desc
oper_C_names = desc_opers_C.keys()

def who_am_i():
    """ Essaie de savoir qui on est, dans tous les cas...
    """
    try:
        user = pwd.getpwuid(os.getuid())[0]
    except Exception:
        try:
            user = os.environ.get("USER")
        except Exception:
            user = os.getlogin()
    return user

# description des operateurs Python
def pydesc2cdesc(py_desc):
    """ Afin de simplifier les traitements ultérieurs,
        transforme les descritpeurs d'opérateurs python en descripteur C :
        - 'categorie': 'VECTOR_IN'   -> 'direction': DIR_IN , 'categorie': 'VECTOR'
        - 'categorie': 'VECTOR_OUT'  -> 'direction': DIR_OUT, 'categorie': 'VECTOR'
        - 'categorie': 'COEFFICIENT' -> 'direction': DIRIN  , 'categorie': 'COEFFICIENT'
        - 'unit'     : xxx           -> 'unite'    : xxx ('set by operator' si absente)

        :param dict() py_desc: dictionnaire de description des opérateurs python
    """
    c_desc = dict()
    for oper_name, oper_val in py_desc.items():
        c_desc[oper_name] = dict()
        args = oper_val['Args']
        c_desc[oper_name]['Arg_Cars'] = list()
        for arg in args:
            d = dict()
            if arg['categorie'] == 'VECTOR_IN':
                d['categorie'] = 'VECTOR'
                d['direction'] = 'DIR_IN'
                d['unite']     = arg.get('unit', None)
            elif arg['categorie'] == 'VECTOR_OUT':
                d['categorie'] = 'VECTOR'
                d['direction'] = 'DIR_OUT'
                d['unite']     = arg.get('unit', 'set by operator')
            elif arg['categorie'] == 'COEFFICIENT':
                d['categorie'] = 'COEFFICIENT'
                d['direction'] = 'DIR_IN'

            d['famille'] = 'set by operator'
            c_desc[oper_name]['Arg_Cars'].append(d)

    return c_desc


import oper
desc_opers_PY = pydesc2cdesc(oper.__desc_opers)
oper_PY_names = desc_opers_PY.keys()

# liste des outils de traitement du champ 'origine' qu'il faut traiter
# (il ne faut pas traiter : "origine = traitement profil_moy.py")
traiteurs = ['fvb', 'adc', 'AIDAcalc.py']

oper_inconnus = list()

def lit_fic_preference():
    """ Lecture du fichier de configuration, si il existe
        pour initialiser les variables
    """
    ### TODO :::: A REPRENDRE (générer le fichier s'il n'existe pas")
    AH = os.getenv('AIDA_HOME')
    global couleur_info_capteur
    global couleur_vecteur_init
    global couleur_vecteur_inter
    global couleur_vecteur_etudie
    global couleur_fonction_noeud
    global couleur_fonction_texte
    global repertoire_sav
    global nom_fic_out

    config_couleur = {}
    nom_fic_config = os.path.join(AH, 'config', 'gengraphvect.cfg')
    
    # initialisation par défaut
    couleur_info_capteur   = 'palegreen1'
    couleur_vecteur_init   = 'lightblue2'
    couleur_vecteur_inter  = 'white'
    couleur_vecteur_etudie = 'salmon1'
    couleur_fonction_noeud = 'yellow1'
    couleur_fonction_texte = 'brown'
    repertoire_sav         = '/tmp'

    try :
        fic_conf = open(nom_fic_config, 'r')
    except Exception as e:
        ### TODO ? info("Pas de fichier de configuration ; initialisation par défaut")
        pass
    else :
        for line_config in fic_conf:
            info_param = line_config.split("=")
            config_couleur[info_param[0]] = info_param[1]

        couleur_info_capteur   = config_couleur['couleur_info_capteur'][:-1]
        couleur_vecteur_init   = config_couleur['couleur_vecteur_init'][:-1]
        couleur_vecteur_inter  = config_couleur['couleur_vecteur_inter'][:-1]
        couleur_vecteur_etudie = config_couleur['couleur_vecteur_etudie'][:-1]
        couleur_fonction_noeud = config_couleur['couleur_fonction_noeud'][:-1]
        couleur_fonction_texte = config_couleur['couleur_fonction_texte'][:-1]

        try :
            repertoire_sav = config_couleur['rep_sav'][0:-1]
        except Exception as e:
            info(f"Répertoire de sauvegarder par défaut : {repertoire_sav}")

    return


def recupere_attribut(vect, attribut):
    """ retourne la valeur de l'attribut passé en argument"""
    try :
        valeur = vect.attributes[attribut]
        return(valeur)
    except KeyError :
        return("NULL")
    except :
        return("NULL")


def conforme_adc(oper_name, oper_type, oper_args, args_brut):
    """ Pour les opérateurs portés en Python :
          supprime de la liste des arguments de l'appel, les arguments qui ont
          disparus.
        Pour les autres opérateurs :
          vérifie le nombre d'arguments reçus.

        :return: True si tout va bien, False sinon
    """
    # DBG print(f">>> conforme_adc : oper_name = {oper_name}, oper_type = {oper_type}")

    if len(args_brut) != len(oper_args):
        if oper_type == OperTypes.PY:
            if len(args_brut) == (len(oper_args) + len(fvb2adc[oper_name])):
                # appel par ancienne forme => supprimer les args_brut
                # surnuméraires
                for arg_nb in reversed(fvb2adc[oper_name]):
                    del args_brut[arg_nb]
                return True
            else:
                return False

        else:
            return False

    return True


def genere_dict_ascendance (acqid) :
    """ Génère un dictionnaire qui pour chaque vecteur d'un acqid donne le nom
        des vecteurs utilisés pour le fabriquer (ou null si sa fct_origine
        n'est pas un `traiteurs`)
    """
    # DBG print(f">>> genere_dict_ascendance")
    ascendant_vecteur={}

    oper_apis = AIDA.get_oper_APIs()
    data_path=AIDA.ID_to_datapath(acqid)
    liste_data = os.listdir(data_path)
    liste_data.sort()

    for vect in liste_data :
        if vect[0] != "." and vect[-4:] == ".vbn" :
            nom_vect = vect[:-4]
            if nom_vect not in ascendant_vecteur.keys() :
                ascendant_vecteur[nom_vect]=[]

            try:
                vecteur = AIDA.Vector(acqid, nom_vect, attributes_only=True)
            except Exception as e:
                print(f"Erreur lecture vecteur {acqid}::{nom_vect} : {e}", file=sys.stderr)
                sys.exit(10)

            origine_parts = recupere_attribut(vecteur,"origine").split(' ')
            if origine_parts[0] == 'traitement' and origine_parts[1] in traiteurs:
                operateur = recupere_attribut(vecteur,"fct_origine")
                try:
                    oper_name, args_brut, args_opt, args_HDR = \
                            parse_instruction(operateur, mode="edifil")
                    if not oper_name:
                        stop_error(f"erreur de syntaxe : {operateur}")

                    oper_type = get_OperType(oper_name, oper_C_names, oper_PY_names)
                except Exception as e:
                    stop_error(f"erreur sur {operateur} : \n {e}")


                try:
                    if oper_type == OperTypes.PY:
                        oper_args = copy.deepcopy(desc_opers_PY[oper_name]['Arg_Cars'])
                    else:
                        oper_args = desc_opers_C[oper_name]['Arg_Cars']
                except Exception as e:
                    warning(f"genere_dict_ascendance : opérateur '{oper_name}' inconnu")
                    continue

                # opérateur python porté ayant perdu des arguments
                if oper_type == OperTypes.PY:
                    if len(args_brut) != len(oper_args):
                        if len(args_brut) == (len(oper_args) + len(fvb2adc[oper_name])):
                            # appel de l'ancien appel C => supprimer les args_brut
                            # surnuméraires.
                            for arg_nb in reversed(fvb2adc[oper_name]):
                                del args_brut[arg_nb]
                        else:
                            print(f"Nombre d'argument dans l'appel inattendu : {operateur}")
                            continue

                for i, arg_name in enumerate(args_brut):
                    if oper_args[i]['direction'] == 'DIR_IN':
                        if oper_args[i]['categorie'] == 'VECTOR':
                            if arg_name in ascendant_vecteur.keys() :
                                lst_parent = ascendant_vecteur[arg_name]
                                if nom_vect not in lst_parent :
                                    lst_parent.append(nom_vect)
                                    ascendant_vecteur[arg_name] = lst_parent
                            else :
                                ascendant_vecteur[arg_name] = [nom_vect]

    return(ascendant_vecteur)


def genere_liste_vecteur_inverse(acqid, nom_vect, liste_nom_vect):
    """ Génère la liste des vecteurs élaborés à partir du vecteur étudié.
    """
    # DBG print(f">>> genere_liste_vecteur_inverse")
    dict_vecteur = genere_dict_ascendance (acqid)

    liste_calc = []
    liste_vecteur_new = []
    
    for lst_vect in dict_vecteur[nom_vect] :
        if  lst_vect not in liste_nom_vect :
            liste_vecteur_new.append(lst_vect)
            liste_nom_vect.append(lst_vect)

    if len(liste_vecteur_new) > 0 :
        for vct in liste_vecteur_new :
            if AIDA.vector_exists(acqid, vct):
                genere_liste_vecteur_inverse(acqid, vct, liste_nom_vect)
            else:
                print("Argument %s ignoré : vecteur inconnu " \
                % vct, file=sys.stderr)

def genere_liste_vecteur(acqid, nom_vect, liste_nom_vect):
    """ Génère la liste des vecteurs utilisés pour arriver au vecteur étudié.
    """
    # DBG print(f">>> genere_liste_vecteur")

    oper_apis = AIDA.get_oper_APIs()
    liste_calc = []
    liste_vecteur_new = []
    try:
        vecteur = AIDA.Vector(acqid, nom_vect, attributes_only=True)
    except Exception as e:
        print(f"Erreur lecture vecteur {acqid}::{nom_vect} : {e}", file=sys.stderr)
        sys.exit(20)

    origine_parts = recupere_attribut(vecteur,"origine").split(' ')
    if origine_parts[0] == 'traitement' and origine_parts[1] in traiteurs:
        if 'fct_origine' in vecteur.attributes.keys():
            v = vecteur.attributes["fct_origine"]
            if not v in liste_calc:
                liste_calc.append(vecteur.attributes["fct_origine"])
    else:
        return

    for i_op, calcul in enumerate(liste_calc):
        try:
            oper_name, args_brut, args_opt, args_HDR = \
                    parse_instruction(calcul, mode="edifil")
            if not oper_name:
                stop_error(f"erreur de syntaxe : {calcul}")

            oper_type = get_OperType(oper_name, oper_C_names, oper_PY_names)
        except Exception as e:
            stop_error(f"erreur sur {calcul} : \n {e}")


        try:
            if oper_type == OperTypes.PY:
                oper_args = copy.deepcopy(desc_opers_PY[oper_name]['Arg_Cars'])
            else:
                oper_args = desc_opers_C[oper_name]['Arg_Cars']
        except Exception as e:
            warning(f"genere_liste_vecteur : opérateur '{oper_name}' inconnu")
            continue

        # opérateur python porté ayant perdu des arguments
        if not conforme_adc(oper_name, oper_type, oper_args, args_brut):
            warning(f"genere_liste_vecteur : nombre d'argument inattendu : " +\
                    f"  {calcul}")
            sys.exit(1)


        for i, oper_arg in enumerate(oper_args):
            if oper_arg['direction'] == 'DIR_IN':
                if oper_arg['categorie'] == 'VECTOR':
                    brut_arg = args_brut[i].strip("'")
                    if  args_brut[i]  not in liste_nom_vect:
                        liste_vecteur_new.append(brut_arg)
                        liste_nom_vect.append(brut_arg)

    for vct in liste_vecteur_new :
        if AIDA.vector_exists(acqid, vct):
            genere_liste_vecteur(acqid, vct, liste_nom_vect)
        else:
            warning(f"vecteur '{vct}' inexistant => ignoré")

    return


def genere_info_capteurs_vect(acqid, liste_nom_vect, nom_fic_sav):
    """ Génère un fichier ascii donnant la liste des capteurs utilisés pour
        l'élaboration du vecteur étudié.
    """
    nom_fic_asc = nom_fic_sav+".asc"
    fic_asc = open(nom_fic_asc,"w")

    print("LISTE DES CAPTEURS UTILISES POUR L'ELABORATION DE %s" % (liste_nom_vect[0]), file=fic_asc)

    for nom_vect in liste_nom_vect:
        try:
            vecteur = AIDA.Vector(acqid, nom_vect, attributes_only=True)
        except Exception as e:
            print(f"Erreur lecture vecteur {acqid}::{nom_vect} : {e}", file=sys.stderr)
            sys.exit(30)

        Origine = recupere_attribut(vecteur,"origine")
        if Origine.find("traitement") < 0 :
            print("\n    Vecteur %s" % (nom_vect), file=fic_asc)
            print("\n    Vecteur %s" % (nom_vect))
            print("        Origine  = %s\n" % recupere_attribut(vecteur, "origine"), end=' ', file=fic_asc)
            print("        Origine  = %s\n" % recupere_attribut(vecteur, "origine"), end=' ')
            module = str(recupere_attribut(vecteur,"chaine_mesure")).split(" ")
            if module[0] == "NULL" :
                module = str(recupere_attribut(vecteur,"chaine_acquisition")).split(" ")

            if module[0] == "NULL" :
                module = ["sensor", "transducer", "calibration"]
                       
            no_info_mod = ""
            for mod in module :
                INFO = recupere_attribut(vecteur, mod)
                if INFO != "NULL" :
                    print("           %s\n" %  INFO, end=' ', file=fic_asc)
                    print("           %s\n" %  INFO, end=' ')
                else :
                    no_info_mod = no_info_mod + mod + ", "
            if len(no_info_mod) > 1 :
#                print(nom_vect + " : pas d'info sur " + no_info_mod, file=sys.stderr) 
                print("       Pas d'info sur %s. " % (no_info_mod))
                print("       Pas d'info sur %s. " % (no_info_mod), file=fic_asc)


def genere_graph_geneal_vect(acqid, liste_nom_vect, niveau):
    """ Genere le fichier .dot de l'arbre généalogique du vecteur étudié.
    """
    # DBG print(f">>> genere_graph_geneal_vect")

    global repertoire_sav
    user = who_am_i()

    flg = 0
    oper_apis = AIDA.get_oper_APIs()
    nom_fic_dot = repertoire_sav + "/" + liste_nom_vect[0] + "." + user + ".dot"
    fic_dot = open(nom_fic_dot,"w")
    print("digraph G {", file=fic_dot)

    # les vecteurs
    # ------------
    liste_call = []
    for nom_vect in liste_nom_vect:
        nom_vect_dot = f'"{nom_vect}"'

        try:
            vecteur = AIDA.Vector(acqid, nom_vect, attributes_only=True)
        except Exception as e:
            print(f"Erreur lecture vecteur {acqid}::{nom_vect} : {e}", file=sys.stderr)
            sys.exit(40)

        origine_parts = recupere_attribut(vecteur,"origine").split(' ')
        if origine_parts[0] == 'traitement' and origine_parts[1] in traiteurs:
            #if recupere_attribut(vecteur,"fct_origine") not in liste_call:
            #    liste_call.append(vecteur.attributes["fct_origine"])
            if 'fct_origine' in vecteur.attributes.keys():
                v = vecteur.attributes["fct_origine"]
                if not v in liste_call:
                    liste_call.append(vecteur.attributes["fct_origine"])

                if nom_vect == liste_nom_vect[0] :
                    print(" %s [shape=ellipse, fillcolor=%s, style=filled, label=\"%s\" ] " % \
                    (nom_vect_dot, couleur_vecteur_etudie, nom_vect), file=fic_dot)
                else :
                    print(" %s [shape=ellipse, label=\"%s\", fillcolor=%s, style=filled] " \
                                    % (nom_vect_dot, nom_vect, couleur_vecteur_inter), file=fic_dot)
        else :
            print(" %s [shape=ellipse, fillcolor=%s, style=filled, label=\"%s\" ] " %\
                            (nom_vect_dot, couleur_vecteur_init, nom_vect), file=fic_dot)
            if niveau == 0 or niveau == 3 :
                print(" \"ori_%s\" [shape=record, fillcolor=%s, style=filled, "% (nom_vect_dot.strip('"'),couleur_info_capteur), file=fic_dot)
                print(" label=\"{%s " % \
                                recupere_attribut(vecteur, "origine"), end=' ', file=fic_dot)
                module = str(recupere_attribut(vecteur,"chaine_mesure")).split(" ")
                if module[0] == "NULL" :
                    module = str(recupere_attribut(vecteur,"chaine_acquisition")).split(" ")

                if module[0] == "NULL" :
                    module = ["sensor", "transducer", "calibration"]
                       
                no_info_mod = ""
                for mod in module :
                    INFO = recupere_attribut(vecteur, mod)
                    if INFO != "NULL" :
                        print(" | %s " %  INFO, end=' ', file=fic_dot)
                    else :
                        no_info_mod = no_info_mod + mod + ", "
                if len(no_info_mod) > 1 :
                    print(nom_vect + " : pas d'info sur " + no_info_mod, file=sys.stderr) 

                print(" }\"];", file=fic_dot)
                print("  \"ori_%s\" -> %s [dir=none, color=%s,\
                                style=bold];" % (nom_vect_dot.strip('"'),\
                                nom_vect_dot, couleur_fonction_texte), file=fic_dot)

    # les opérateurs
    # --------------
    for i_op, call_line in enumerate(liste_call):
        try:
            oper_name, args_brut, args_opt, args_HDR = \
                    parse_instruction(call_line, mode="edifil")
            if not oper_name:
                stop_error(f"erreur de syntaxe : {call_line}")

            oper_type = get_OperType(oper_name, oper_C_names, oper_PY_names)
        except Exception as e:
            stop_error(f"erreur sur {call_line} : \n {e}")

        try:
            if oper_type == OperTypes.PY:
                oper_args = desc_opers_PY[oper_name]['Arg_Cars']
            else:
                oper_args = desc_opers_C[oper_name]['Arg_Cars']
        except Exception as e:
            warning(f"genere_graph_geneal_vect : opérateur '{oper_name}' inconnu")
            continue

        # opérateur python porté ayant perdu des arguments
        if not conforme_adc(oper_name, oper_type, oper_args, args_brut):
            warning(f"genere_graph_geneal_vect : nombre d'argument inattendu : " +\
                    f"  {call_line}")
            sys.exit(1)


        node_code = "OP%d" % i_op

        if niveau >= 2 :
            flg = 1
            print("  %s [shape=record, fillcolor=%s, style=filled, label=\"%s " % (node_code, couleur_fonction_noeud, oper_name), end=' ', file=fic_dot)
        elif niveau == 1 :
            print("  %s [shape=box, fillcolor=%s, style=filled, label=\"%s \"]" % (node_code, couleur_fonction_noeud, oper_name), end=' ', file=fic_dot)


        # a faire ?
        if len(args_brut) != len(oper_args):
            if niveau >= 2 and flg == 1 :
                ### TODO input(":::: fermer ?")
                print(" \"];", file=fic_dot)
                flg = 0
            continue


        vecteur_in = []
        vecteur_out  = []
        if niveau == 0 :
            for i, arg_name in enumerate(args_brut):
                if oper_args[i]['categorie'] == "VECTOR":
                    if oper_args[i]['direction'] == "DIR_IN":
                        if arg_name in liste_nom_vect :
                            vecteur_in.append(arg_name)
                    elif oper_args[i]['direction'] == "DIR_OUT":
                        if arg_name in liste_nom_vect :
                            vecteur_out.append(arg_name)

            for vecti in vecteur_in :
                for vecto in vecteur_out :
                    vi_dot = f'"{vecti}"'
                    vo_dot = f'"{vecto}"'
                    print("  %s -> %s [ label = \" %s\" \
                                ,fontcolor = %s];" % (vi_dot, vo_dot, oper_name,couleur_fonction_texte), file=fic_dot)

        if niveau >= 2 :
            for i, arg_name in enumerate(args_brut):
                if oper_args[i]['direction'] == "DIR_IN":
                    if oper_args[i]['categorie'] == "COEFFICIENT":
                        value = arg_name.replace('"', '')
                        print(f" | {value} ", end=' ', file=fic_dot)
            print(" \"];", file=fic_dot)
            flg = 0

        if niveau > 0 :
            for i, arg_name in enumerate(args_brut):
                if arg_name in liste_nom_vect :
                    arg_name_dot = f'"{arg_name}"'
                    if oper_args[i]['direction'] == "DIR_IN":
                        if oper_args[i]['categorie'] == "VECTOR":
                            print("  %s -> %s;" \
                                            % (arg_name_dot, node_code), file=fic_dot)
                    elif oper_args[i]['direction'] == "DIR_OUT":
                        if arg_name in liste_nom_vect :
                            print("  %s -> %s;" \
                                             % (node_code, arg_name_dot), file=fic_dot)

    print(("}"), file=fic_dot)
    fic_dot.close()

    return


def main(argv=None):
    # arguments
    ### TODO : comment avoir en même temps :
    ###         1) l'affichage des valeurs par défaut
    ###            -> formatter_class=argparse.ArgumentDefaultsHelpFormatter
    ###         2) une présentation multi-ligne des niveaux
    ###            -> formatter_class=argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(
                    epilog="NOTES : \n" + \
                           " - Fichier de configuration : $AIDA_HOME/config/gengraphvect.cfg \n" +\
                           " - En niveau=9 : seul le premier vecteur est traité \n" +\
                           " - Le mode 'visu' est inopérant pour les niveaux 4 et 9",
                    formatter_class=argparse.RawTextHelpFormatter)

    help_niveau = "0 : vecteurs + capteurs. \n" +\
                  "1 : opérateurs utilisés. \n" +\
                  "2 : niveau 1 + arguments des opérateurs. \n" +\
                  "3 : niveau 2 + capteurs. \n" +\
                  "4 : capteurs uniquement (ascii) \n" +\
                  "9 : liste des ascendants ou des descendants (ascii) \n" +\
                  "default : 0 \n"


    parser.add_argument("-a", "--acqid"      , help="identification de l'acquisition", required=True)
    parser.add_argument("-o", "--out"        , help="format de sortie \ndefault : png", choices=['ps', 'pdf', 'svg', 'png', 'gif', 'jpg', 'json'], default='png')
    parser.add_argument("-n", "--niveau"     , help=help_niveau, default=0, type=int)
    parser.add_argument("-f", "--nom_fic_out", help="nom du fichier de sortie \ndefault : voir fichier de configuration")
    parser.add_argument("-s", "--sens"       , help="sens de l'arbre : asc=ascendant, desc=descendant \ndefault : asc", default='asc')
    parser.add_argument("-v", "--visu"       , help="lance le visualisateur sur le fichier de sortie", action='store_true')
    parser.add_argument('in_vectors'         , help="paramètre de l'acquisition", metavar='VECTEUR', nargs='+')

    args = parser.parse_args()

    # Récuperation user pur nom de fichier
    user = who_am_i()

    # fichier de configuration
    lit_fic_preference()

    # traitement
    for in_vector in args.in_vectors:
        in_vector = in_vector.replace('.vbn', '')
        # DBG print(f"=== traitement de {in_vector}", file=sys.stderr)

        try:
            AIDA.vector_exists(args.acqid, in_vector)
        except Exception as e:
            stop_error(e)

        liste_vecteur = []
        liste_vecteur.append(in_vector)
        if args.sens == 'desc' :
            # génère la liste des vecteurs en aval du vecteur étudié
            genere_liste_vecteur_inverse(args.acqid, in_vector, liste_vecteur)
        else :
            # génère la liste des vecteurs en amont du vecteur étudié
            genere_liste_vecteur(args.acqid, in_vector, liste_vecteur)

        if not args.nom_fic_out:
            fic_out = os.path.join(repertoire_sav, f"{liste_vecteur[0]}_n{str(args.niveau)}.{user}")
        else :
            fic_out = os.path.join(repertoire_sav, f"{args.nom_fic_out}")


        if args.niveau == 9 :
            ### ATTENTION : seul le premier vecteur passé est traité
            nom_fic_asc = fic_out+".asc"
            fic_asc = open(nom_fic_asc,"w")
            for vect in liste_vecteur :
                print(vect, file=fic_asc)
                print(vect)
            fic_asc.close()
            return("")

        # génère l'arbre des vecteurs
        # ---------------------------
        if args.niveau == 4 :
            genere_info_capteurs_vect(args.acqid, liste_vecteur, fic_out)
        else :
            genere_graph_geneal_vect(args.acqid, liste_vecteur, args.niveau)
            dot_out = os.path.join(repertoire_sav, f"{liste_vecteur[0]}.{user}.dot")
            command = f"dot -T {args.out} {dot_out} > {fic_out}.{args.out}"
            # DBG input(f":::: command = {command}")
            os.system(command)

            if args.visu:
                os.system(f"xdg-open {fic_out}.{args.out} &")

    return("OK")

if __name__ == "__main__":
    sys.exit(main())

