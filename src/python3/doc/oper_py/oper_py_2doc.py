#!/usr/bin/env python3

"""
Construction du squelette de la documentation de tous opérateurs python.

  usage :
    {me} [options]

  options :
    -h / --help    : affiche cette aide et sort.
    -v / --version : affiche la version de ce code et sort.
    -n / --dry-run : affiche ce qu'il y aurait à faire
"""

import os
import sys
import getopt
import re
from string import Template

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
from fct_messages import (info, warning, stop_error, result, wait_user)
import oper

# descriptions des opérateurs Python
desc_opers_PY = oper.__desc_opers


# répertoire de la doc
main_path = os.path.join(os.getenv('AIDA_HOME'), 'src', 'doc', 'oper')

# sous-répertoires de description des arguments (.args.tex)
args_path = os.path.join(main_path, 'arguments')

# sous-répertoires de description des formules (.frm.tex)
frm_path = os.path.join(main_path, 'formules')

# templates
main_tpl = """%%%%%
%
%% Dans ce fichier, les éventuels accents sont codés
%% en ISO-8859-15 (aka latin9)
%% La ligne suivante donne trois exemples 
%% e accent aigu : é, e accent grave : è, e-dans-l'o : ½
\section{INCONNU}

\itemstyle{Op\\'erateur~:} \operfmt{$protected_oper_name}
\index{$protected_oper_name}

%%%%%OBJET%%%%
\itemstyle{Objet~:}
INCONNU

%%%%%ARGUMENTS%%%%
\\bigskip
\input{arguments/$oper_name.args.tex}

%%%%%FORMULE%%%%
\itemstyle{Formule}

\input{formules/$oper_name.frm.tex}

%%%%%AUTEUR%%%%
\itemstyle{Auteur~:}
CNRM/GMEI/TRAMM

%%%%%REFERENCE%%%%
\itemstyle{R\\'ef\\'erences~:}
INCONNU"""

# l'Id sous la forme $Id$ ne peut pas appartenir au template...
single_arg_tpl = " & $cat & blabla (unité : $unit, famille : $fam)\\\\"

args_begin = """%% Dans ce fichier, les éventuels accents sont codés
%% en ISO-8859-15 (aka latin9)
%% La ligne suivante donne trois exemples 
%% e accent aigu : é, e accent grave : è, e-dans-l'o : ½
%%%%%ENTREES%%%%
\\begin{tabarg}
\multicolumn{3}{l}{\\titretab {Entr\\'ees}}\\\\
\\hline"""

args_middle = """\end{tabarg}

\medskip
%%%%%SORTIES%%%%
\\begin{tabarg}
\multicolumn{3}{l}{\\titretab {Sorties}}\\\\
\hline"""

args_end = "\end{tabarg}"

frm_tpl = """%% Formule de l'operateur : $oper_name
%% Dans ce fichier, les éventuels accents sont codés
%% en ISO-8859-15 (aka latin9)
%% La ligne suivante donne trois exemples 
%% e accent aigu : é, e accent grave : è, e-dans-l'o : ½
\[
Resultat = X + Y
\]
"""


# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


def usage():
    """ Affiche l'usage.
    """
    print(__doc__.format(me=me))


def generate_main(oper_name, protected_oper_name, dry_run=False):
    """ Génère le fichier principal de la documentation de l'opérateur
        'oper_name'.

        :param str() oper_name           : nom de l'opérateur.
        :param str() protected_oper_name : nom de l'opérateur avec les '_'
                                           protégés.
        :param boolean() dry_run         : mode dry_run

        :return: nombre de fichier générer (à générer en mode dry_run)
                 (=> 0 ou 1)
        :rtype : int()
    """
    oper_path = os.path.join(main_path, oper_name + '.tex')
    if os.path.isfile(oper_path):
        return 0
    elif dry_run:
        print(f"- documentation à générer/écrire : {oper_name}")
        return 1


    main  = Template(main_tpl)

    with open(oper_path, 'w', encoding='iso-8859-1') as handler:
        print(main.substitute(oper_name=oper_name,
                              protected_oper_name=protected_oper_name),
              file=handler)

    print(f"- fichier généré : {oper_path}")

    return 1


def arg2tex(desc):
    """ Génère la ligne au format LaTeX de l'argument 'name'  avec le contenu
        de la description 'desc'.

        :param dict() decr : dictionnaire de description de l'argument
                              { 'Id'  : 'arg1',
                                'cat' : 'Vecteur' ou 'Coefficient',
                                'fmt' : <type python> (float, int...)
                                'unit': unité
                              }

        :return: "\$Arg1 & Vecteur, \texttt{float} & blabla (degree)\\"
        :rtype : str()

    """
    # traitement des '_' dans le nom du paramètre
    name = desc['Id']
    pattern = r"_([a-zA-Z0-9]+)"
    #$time_{dest}$ & Vecteur, & blabla (unité : s, famille : [temps])\\
    Id = re.sub(pattern, r"_{\1}", name)

    cat  = desc['cat']
    unit = desc['unit']
    fam  = str(desc['famille']).replace("'", "")

    single_arg = Template(single_arg_tpl)

    # l'Id sous la forme $Id$ ne peut pas appartenir au template...
    return "$" + Id + "$" + single_arg.substitute(Id=Id, cat=cat, unit=unit, fam=fam)


def generate_arg(oper_name, oper_args):
    """ Génère le fichier argument de la documentation de l'opérateur
        'oper_name'.

        :param str()  oper_name : nom de l'opérateur.
        :param dict() oper_args : description des arguments in/out l'opérateur.
         { 'in' : [ { 'Id': 'Arg1', 'cat': 'Vecteur'    , 'fmt': 'float', 'unit':'degree'},
                    { 'Id': 'Arg2', 'cat': 'Coefficient', 'fmt': 'int'  , 'unit':'m'},
                  ],
           'out': [ { 'Id': 'Arg3', 'cat': 'Vecteur'    , 'fmt': 'float', 'unit':'m/degree'},
                  ],
         }
    """
    oper_path = os.path.join(args_path, oper_name + '.args.tex')
    if os.path.isfile(oper_path):
        return

    with open(oper_path, 'w', encoding='iso-8859-1') as handler:
        print(args_begin, file=handler)

        for arg_desc in oper_args['in']:
            #print(f"- generate_arg : {arg_desc}")
            print(arg2tex(arg_desc), file=handler)

        print(args_middle, file=handler)

        for arg_desc in oper_args['out']:
            #print(f"- generate_arg : {arg_desc}")
            print(arg2tex(arg_desc), file=handler)

        print(args_end, file=handler)

    print(f"- fichier généré : {oper_path}")

    return


def generate_frm(oper_name):
    """ Génère le fichier formule de la documentation de l'opérateur
        'oper_name'.

        :param str() oper_name           : nom de l'opérateur.
    """
    oper_path = os.path.join(frm_path, oper_name + '.frm.tex')
    if os.path.isfile(oper_path):
        return

    frm  = Template(frm_tpl)

    with open(oper_path, 'w', encoding='iso-8859-1') as handler:
        print(frm.substitute(oper_name=oper_name),
              file=handler)

    print(f"- fichier généré : {oper_path}")

    return


if __name__ == '__main__':

    # parsing de la ligne de commande
    # -------------------------------
    argv = sys.argv

    # options
    dry_run = False
    nb_todo = 0
    todo_label = "créé(s)"
    try:
        opts, args = getopt.getopt(argv[1:],
                                   'hvn',
                                   ['help', 'version', 'dry-run'])
    except getopt.error as msg:
        usage()
        stop_error("option inconnue : '%s'" % (msg.opt))

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(1)
        elif opt in ('-v', '--version'):
            warning(f"{me} version : {__version__}")
            sys.exit(0)
        elif opt in ('-n', '--dry-run'):
            dry_run = True
            todo_label = "a créer"
            warning(f"{me} : mode dry-run") 
        else:
            warning("option '%s' inconnue" % (opt))
            usage()

    # aucun argument attendu
    if len(args) != 0:
        usage()

    # traitement
    for oper_name, oper_desc in desc_opers_PY.items():
        # 1) organiser les infos de la description de l'opérateur pour créer le
        #    dictionnaire d'entrée pour 'generate_arg'
        doc_args = dict()
        doc_args['in']  = list()
        doc_args['out'] = list()

        for dict_arg in oper_desc['Args']:

            doc_dict = {'Id': dict_arg['Id']}

            if dict_arg['categorie'] == 'VECTOR_IN':
                doc_dict['cat'] = 'Vecteur'
            else:
                doc_dict['cat'] = 'Coefficient'
                
            doc_dict['unit']    = dict_arg.get('unit', '')
            doc_dict['famille'] = dict_arg.get('famille', '')

            if dict_arg['categorie'] in ['VECTOR_IN', 'COEFFICIENT']:
                doc_args['in'].append(doc_dict)
            else: # VECTOR_OUT
                doc_args['out'].append(doc_dict)


        # 2) génération
        if not dry_run:
            print(f"\nopérateur : {oper_name}")

        protected_oper_name = oper_name.replace('_', '\_')

        ret = generate_main(oper_name, protected_oper_name, dry_run=dry_run)
        nb_todo = nb_todo + ret
        if not dry_run:
            generate_arg(oper_name, doc_args)
            generate_frm(oper_name)


    # fin
    print(f"\n--> {me} : nombre de documentation {todo_label} : {nb_todo}\n")
    sys.exit(0)
