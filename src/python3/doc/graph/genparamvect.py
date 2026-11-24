#!/usr/bin/env python3

"""
Génère un graphe de généalogie de vecteur avec suivi d'un paramètre
===================================================================
(Ce programme est basé sur gengraphvect.py)

  usage :
    {me} -h
    {me} -a acqid [-p param] nom_vecteur

  options :
      -h         : affiche l'usage.
      -a acqid   : identifiant de l'acquisition.
      -p param   : paramètre du header des vecteurs à afficher
                   default : unit.
      -m numéro  : TODO : modèle 1, 2, 3 : nombre de ligne de description des
                   paramètres des opérateurs

  exemples :
    {me} -h
    {me} -a Tf210001            flx_cov_wconh2o_2D_Eti_%1800
    {me} -a Tf210001 -p famille flx_cov_wconh2o_2D_Eti_%1800

Certains noms de vecteur contiennent des '%' ou des  '.' qui pertube la
commande `dot` => il est préférable de noter les noms de vecteur entre "".
"""


import sys
import os
import getopt
import copy
import re
import ast
from enum import Enum
from string import Template


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

# Initialisation aux valeurs par defaut des couleurs
couleur_vecteur_init = "lightblue2"
couleur_vecteur_inter = "white"
couleur_vecteur_etudie = "salmon1"
couleur_fonction_noeud = "yellow1"

# templates opérateur -> .dot
tpl_title = """
// title
labelloc="t";
label="acqid : $acqid";
"""
tpl_in_1    = "    { <in$n> $param = $value } |\ "
tpl_in_2    = "    { <in$n> $arg_info | $param = $value } |\ "
tpl_in_3    = "    { <in$n> \$Arg$arg_nb | $arg_info | $param = $value } |\ "
tpl_in_4    = "    { <in$n> \$Arg$arg_nb | $arg_info } |\ "
tpl_out     = "    { <out$n> $param = $value } $end_arg"
# TODO : il faudrait faire partie de flèche de outX ou optX ou HDRX et passer
#        un paramètre `from`
#        tpl_out     = "    { <$from$n> $param = $value } $end_arg"
tpl_HDR     = "    { <HDR$n> $opt = $value } $end_arg"
tpl_opt     = "    { <opt$n> $opt = $value } $end_arg"


# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]

def usage():
    print(__doc__.format(me=me))
    sys.exit(1)


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


def get_param_value(acqid, nom_vect, param):
    """ retourne la valeur de 'param' lue dans le vecteur ou None
        si non-trouvé et l'objet vector
    """
    # DBG print(f">>> get_param_value : param = {param}, nom_vect = {nom_vect}")

    try:
        vecteur = AIDA.Vector(acqid, nom_vect, attributes_only=True)
        param_value = vecteur.attributes.get(param, 'not found')
        if param_value == 'not found':
            if param == 'unit' and nom_vect.startswith('rft'):
                param_value = f's'
    except AIDA.AidaError:
        print(f"Erreur de lecture du vecteur {acqid}::{nom_vect}",
              file=sys.stderr)
        return None, vecteur

    return param_value, vecteur


def genere_liste_vecteur(acqid, nom_vect, liste_nom_vect):
    """
     Génère la liste des vecteurs utilisés pour arriver au vecteur étudié.
    """
    #DBG print(f">>> genere_liste_vecteur : {nom_vect}, {liste_nom_vect}")

    liste_call        = list()
    liste_vecteur_new = list()
    try:
        vecteur = AIDA.Vector(acqid, nom_vect, attributes_only=True)
    except AIDA.AidaError:
        print("Erreur lecture vecteur {acqid} : {nom_vect}", file=sys.stderr)

    origine_parts = vecteur.attributes.get('origine', '').split(' ')
    if origine_parts[0] == 'traitement' and origine_parts[1] in traiteurs:
        if 'fct_origine' in vecteur.attributes.keys():
            v = vecteur.attributes["fct_origine"]
            if not v in liste_call:
                liste_call.append(vecteur.attributes["fct_origine"])
    else:
        return

    for i_op, call_line in enumerate(liste_call):
        try:
            oper_name, args_brut, args_opt, args_HDR = \
                    parse_instruction(call_line, mode="edifil")
            if not oper_name:
                stop_error(f"erreur de syntaxe : {operateur}")

            oper_type = get_OperType(oper_name, oper_C_names, oper_PY_names)
        except Exception as e:
            stop_error(f"erreur sur {call_line} : \n {e}")

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
                    f"  {call_line}")
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


def genere_graph_geneal_vect(acqid, liste_nom_vect, file_name, param='unit',
                             tpl=tpl_in_4):
    """ Génère le fichier .dot de l'arbre généalogique du vecteur étudié.
    """
    # DBG print(f">>> genere_graph_geneal_vect :")

    flg = 0
    dot_file = open(file_name, "w")

    print("digraph G {", file=dot_file)
    title = Template(tpl_title)
    print(title.safe_substitute(acqid=acqid), file=dot_file)

    # les vecteurs
    # ------------
    liste_call = []
    for nom_vect in liste_nom_vect:
        nom_vect_dot = f'"{nom_vect}"'

        param_value, vecteur = get_param_value(acqid, nom_vect, param)
        if param_value is None:
            continue

        origine_parts = vecteur.attributes.get('origine', '').split(' ')
        if origine_parts[0] == 'traitement' and origine_parts[1] in traiteurs:
            if 'fct_origine' in vecteur.attributes.keys():
                v = vecteur.attributes["fct_origine"]
                if not v in liste_call:
                    liste_call.append(vecteur.attributes["fct_origine"])

                if nom_vect == liste_nom_vect[0] :
                    # vecteur cible
                    print(f' {nom_vect_dot} [shape=ellipse, ' +\
                          f'fillcolor={couleur_vecteur_etudie}, ' +\
                          f'style=filled, ' +\
                          f'label="{nom_vect}\\n{param} = {param_value}"]',
                          file=dot_file)
                else :
                    # vecteur ancêtre
                    print(f' {nom_vect_dot} [shape=ellipse, ' +\
                          f'fillcolor={couleur_vecteur_inter}, ' +\
                          f'style=filled, ' +\
                          f'label="{nom_vect}\\n{param} = {param_value}"]',
                          file=dot_file)
        else :
            # vecteur initial

            # ajouter l'origine
            fct_origine = vecteur.attributes.get('fct_origine', '')
            if fct_origine:
                fct_origine = fct_origine.replace('programme ', '')
                from_orig   = os.path.splitext(os.path.basename(fct_origine.split()[0]))[0]
                if from_orig:
                    param_value = f"{param_value}\\n({from_orig})"

            print(f' {nom_vect_dot} [shape=ellipse, ' +\
                  f'fillcolor={couleur_vecteur_init}, ' +\
                  f'style=filled, ' +\
                  f'label="{nom_vect}\\n{param} = {param_value}"]',
                  file=dot_file)

    # les opérateurs
    # --------------
    for i_op, call_line in enumerate(liste_call):
        try:
            oper_name, args_brut, args_opt, args_HDR = \
                    parse_instruction(call_line, mode="edifil")
            if not oper_name:
                stop_error(f"erreur de syntaxe : {operateur}")

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


        # open node
        node_code = f"OP_{i_op:03d}"
        print(f'\n{node_code}[label="{oper_name} |\ ', file=dot_file)

        # les paramètres de l'appel de l'opérateur
        dir_in      = dict()
        out_vectors = list()
        for i_arg, arg in enumerate(oper_args):
            if param == 'unit':
                # normaliser l'unité, si possible
                param_value = arg.get('unite', '')
                if param_value != 'set by operator':
                    try:
                        param_value = Units.get_AIDA_unit(param_value)
                    except Exception as e:
                        pass
            else:
                param_value = arg.get(param, 'not found').replace('"', '')

            if arg['direction'] == 'DIR_IN':
                if arg['categorie'] == 'VECTOR':
                    dir_in[ args_brut[i_arg] ] = i_arg
            else:
                out_vectors.append(args_brut[i_arg].replace('$', '\\$'))

            if arg['categorie'] == 'VECTOR':
                info = arg['categorie']
                if arg['unite']:
                    info = f"{info} (unit = {arg['unite']})"
            else: # arg['categorie'] == 'COEFFICIENT':
                if isinstance(args_brut[i_arg], str):
                    info = args_brut[i_arg].replace('$', '\\$')
                else:
                    info = args_brut[i_arg]
            info = info.replace('"', '')


            ###end_arg = '|\\' if i_arg < len(oper_args)-1 else '"'
            end_arg = '|\\'
            if i_arg == len(oper_args)-1 and (not args_opt) and (not args_HDR):
                # dernier argument
                end_arg = '"'

            if arg['direction'] == 'DIR_IN':
                arg = Template(tpl)
                print(arg.safe_substitute(n=i_arg,
                                          arg_nb=i_arg+1,
                                          arg_info=info,
                                          param=param, value=param_value),
                      file=dot_file)
                i_arg_out = 0
            else: # DIR_OUT
                arg = Template(tpl_out)
                print(arg.safe_substitute(n=i_arg_out,
                                      param=param, value=param_value,
                                      end_arg=end_arg),
                      file=dot_file)
                i_arg_out = i_arg_out + 1

        # les paramètres optionnels de l'appel de l'opérateur
        if args_opt:
            end_arg = '|\\'
            for i_arg, (key, val) in enumerate(args_opt.items()):
                arg = Template(tpl_opt)

                if i_arg == len(args_opt)-1 and (not args_HDR):
                    # dernier argument
                    end_arg = '"'

                print(arg.safe_substitute(n=i_arg,
                                          opt=key,
                                          value=val,
                                          end_arg=end_arg),
                      file=dot_file)

        # les paramètres optionnels de ADC de l'appel de l'opérateur
        if args_HDR:
            end_arg = '|\\'
            for i_arg, (key, val) in enumerate(args_HDR.items()):
                arg = Template(tpl_HDR)

                if i_arg == len(args_HDR)-1:
                    # dernier argument
                    end_arg = '"'

                print(arg.safe_substitute(n=i_arg,
                                          opt=key,
                                          value=val,
                                          end_arg=end_arg),
                      file=dot_file)

        #### cloture des arguments de l'opérateur
        ###print("    \"", file=dot_file)

        # close node
        print("    , fillcolor=yellow1, style=filled, shape=Mrecord];",
              file=dot_file)

        # liens sur le node
        # - entrée
        for key, value in dir_in.items():
            nom_vect_dot = key.replace("'", '"')
            print(f'    "{nom_vect_dot}" -> {node_code}:in{value};', file=dot_file)

        # - sortie
        for i, vector in enumerate(out_vectors):
            nom_vect_dot = vector.replace("'", '"')
            print(f'    {node_code}:out{i} -> "{nom_vect_dot}";', file=dot_file)

        for i, vector in enumerate(out_vectors):
            if not vector in liste_nom_vect:
                param_value, _ = get_param_value(acqid, vector, param)
                if param_value is None:
                    continue

                print(f' "{vector}" [shape=ellipse, ' +\
                      f'fillcolor={couleur_vecteur_inter}, ' +\
                      f'style=filled, ' +\
                      f'label="{vector}\\n{param} = {param_value}"]',
                      file=dot_file)


    # close dot
    print(("}"), file=dot_file)
    dot_file.close()



if __name__ == "__main__":

    # paramètres par défaut
    param = 'unit'

    # options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'ha:p:')
    except getopt.GetoptError as msg:
        stop_error(msg)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()

        elif opt in ('-a'):
            acqid = arg

        elif opt in ('-p'):
            param = arg

        else:
            stop_error(f"option '{opt}' inconnue")

    # arguments
    wanted_args = ["in_vector"]
    if len(args) != len(wanted_args):
        warning( "nombre de paramètre invalide : " +\
                f"{len(wanted_args)} attendus ({wanted_args})")
        usage()

    # ATTENTION : il faut finir le tuple par ", )"
    (in_vector, ) = tuple(args)
    in_vector = os.path.basename(in_vector)
    in_vector = in_vector.replace('.vbn', '')

    # concernant les sorties
    dir_out  = os.path.join(os.sep, 'tmp')
    dot_file = os.path.join(dir_out, in_vector + '.' + os.getenv('USER') + '.dot')
    png_file = os.path.join(dir_out, in_vector + '.' + os.getenv('USER') + '.png')


    # information pour l'utilisateur
    print(f"{me} :")
    print(f" - acqid     = {acqid}")
    print(f" - param     = {param}")
    print(f" - in_vector = {in_vector}")
    print(f" - dot_file  = {dot_file}")
    print(f" - png_file  = {png_file}")
    print()


    # traitement
    if AIDA.vector_exists(acqid, in_vector):
        # générer la liste des vecteurs en amont du vecteur étudié
        liste_vecteur = list()
        liste_vecteur.append(in_vector)
        genere_liste_vecteur(acqid, in_vector, liste_vecteur)

        # generer le graphe
        genere_graph_geneal_vect (acqid, liste_vecteur, dot_file, param=param)

        command = f'dot -Tpng {dot_file} > {png_file}'
        # DBG input(f":::: command = {command}")
        os.system(command)

        # visualisation du png
        command = f'xdg-open {png_file}'
        # DBG input(f":::: command = {command}")
        os.system(command)
    else:
        stop_error(f"{acqid}::{in_vector} n'est pas un vecteur.")
        sys.exit(1)

    # bye
    print(f"\n--> fichiers générés :")
    print(f" - {dot_file}")
    print(f" - {png_file}")
    sys.exit(0)
