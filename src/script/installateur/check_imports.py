#!/usr/bin/env python3

"""
Admin AIDA
==========
    A partir d'un fichier d'extraction des 'import' fait dans AIDA
    génère un fichier des modules manquants et un fichier _propre_ de toutes
    les dépendances externes de AIDA.

    S'appuie sur :
    - pkgutil.iter_modules :
        permet de connaitre les modules accessibles par sys.path
    - sys.builtin_module_names :
        permet de connaitre les modules compilés dans l'interpréteur python

    usage :
        {me} <fichier de tous les imports> <fichier des modules manquants> <fichier des module requis>

"""

import sys
import os
import pkgutil


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
AL = os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y)
sys.path.append(os.path.join(AL))

AIDA_HOME = os.getenv('AIDA_HOME')

# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


def usage():
    """ Affiche l'usage.
    """
    print(__doc__.format(me=me))
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        usage()

    all_imports_file  = sys.argv[1]
    missings_file = sys.argv[2]
    requis_file = sys.argv[3]
    #print(f"\n\n{me}")
    #print(f"- all_imports_file  = {all_imports_file}")
    #print(f"- missings_file     = {missings_file}")
    #print(f"- requis_file       = {requis_file}")

    # lecture du fichier d'entrée
    try:
        with open(all_imports_file, 'r') as handler:
            lines = handler.readlines()
    except Exception as e:
        print(f"problème de lecture du fichier {all_imports_file}", e)
        sys.exit(1)

    # ajout à sys.path ce qui vient de AIDA
    # => pkgutil va trouver les modules de AIDA importés directement
    #    (ex : AIDAcalc fait 'import Oper_PY')
    # note : lors du lancement par l'installateur, l'arborescence AIDA
    #        n'existe pas encore
    if os.path.isdir(AL):
        for name in  os.scandir(AL):
            if name.is_dir() and not '__pycache__' in name.path:
                sys.path.append(name.path)

    # construction de 2 listes :
    # - la liste des modules python connus
    # - la liste des modules appartenant à AIDA
    python_modules = list()
    AIDA_modules  = list()
    for where, module, _ in pkgutil.iter_modules():

        if AIDA_HOME in  str(where):
            AIDA_modules.append(module)
        else:
            python_modules.append(module)

    # ajouter à la liste des modules python ce qui est connu de sys.builtin_module_names
    # (ce n'est peut-être pas bien utile sauf peut-être si un jour un truc
    # compilé avec l'inerpréteur python été sorti...)
    for module in sys.builtin_module_names:
        python_modules.append(module)


    # Analyse du fichier d'entrée
    # ---------------------------
    # les lignes du fichier d'entrée sont de la forme :
    # - import MODULE
    # - from   MODULE ...
    # - from   MODULE.xxx.yyy ...

    # compter le nombre de MODULE inconnus, inscrire les MODULE non trouvés
    # dans le fichier des manquants
    aida_dependences = set()
    nb_not_found = 0
    with open(missings_file, 'w') as handler:
        for line in lines:
            # récupérer le 2ième mot (le nom du MODULE)
            need_module = line.split()[1].split('.')[0]

            # mémoriser tous les MODULE sauf ceux qui appartiennent à AIDA
            if not need_module in AIDA_modules:
                aida_dependences.add(need_module)

                # compter les MODULE NON connus qui n'appartiennent pas à AIDA
                if not need_module in python_modules:
                    #print(f"- module '{need_module}' NOT found")
                    print(f"- Module absent : {need_module}")
                    print(f"{need_module}", file=handler)
                    nb_not_found = nb_not_found + 1

    # créer le fichier _propre_ de sortie
    with open(requis_file, 'w') as handler:
        for module in reversed(sorted(aida_dependences, key=str.casefold)):
            print(f"import {module}", file=handler)

    # fin
    if nb_not_found > 0:
        print(f"--> Nombre de module(s) absent(s) : {nb_not_found}.\n")
    #print(f"--> fichier généré : {requis_file} \n")

    sys.exit(nb_not_found)
