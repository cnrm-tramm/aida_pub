#!/usr/bin/env python3

"""
Created on 7 mai 2019

@author: CNRM/GMEI/TRAMM
"""

import os
import sys
import re
import logging 

from .Element import element
from .Operation import operation
from .Format_latex import format_latex

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))


class gestOper(element):
    """
    Gere les differentes operations disponibles
    """

    # Liste des opérations (Operation[])
    oper_list = list()

    # Liste des opérations (str Chapitre:Operation[])
    oper_list_par_chap = list()

    # Couleur représentant ce type d'element (String)
    couleur = ""

    # Nom definisant ce type d'element (String)
    nom = ""


    def __init__(self):
        """
        Constructor
        """
        self.load()


    def load(self):
        """
        Met en mémoire la liste des operations
        """
        self.oper_list = [ ]

        latex_formateur = format_latex()

        the_path = os.path.join(AH, 'src', 'doc', 'oper', 'CATALOG_OPER.tex')
        fichierTotal = open(the_path, encoding='ISO-8859-15')
        chapitre_list = fichierTotal.read().split("\chapter")[2:]

        # on prend chaques lignes du fichier
        guillemets = re.compile("(\{(.*?)\})")

        for chapitre in chapitre_list:
            # list des operateurs du chapitre
            chap_oper_list = []

            # Nom du chapitre
            nom_chapitre = chapitre.split("\chapter{")[0].split("}")[0].replace("{","")
            nom_chapitre = latex_formateur.suppr_carac_speciaux(nom_chapitre)

            chapitre= chapitre.split("\input")[1:]
            for nom_oper in chapitre:
                # liste des arguments ([nom arg, type arguments])
                arg_list = list()
                # On stop aux annexes
                if "ANNEXES" in nom_oper:
                    fichierTotal.close()
                    return True

                nom_oper = guillemets.findall(nom_oper)[0][1]

                # si il y a deja l'extention .tex
                if nom_oper[-4:] == ".tex":
                    nom_oper = nom_oper[:-4]

                file_name = nom_oper
                if file_name == 'RTTOV_ground':
                    continue
                # On recupere la description de l'objet
                objet = "\nObjet :\n"

                the_path = os.path.join(AH, 'src', 'doc', 'oper', file_name+'.tex')
                fichierData = open(the_path, encoding='ISO-8859-15')
                tab_ligne = fichierData.read().split("OBJET")[1].split("\\input")
                for line in tab_ligne[0].split("\n"):
                    if not "%%%" in line and not "itemstyle" in line and line != "" and not "bigskip" in line:
                        objet += line + '\n'

                arg_file = tab_ligne[1].split('\n')[0].replace('{', '').replace('}', '').replace(' ', '')

                fichierData.close()

                the_path = os.path.join(AH, 'src', 'doc', 'oper', arg_file)
                fichierData = open(the_path, encoding='ISO-8859-15')

                tab_ligne = fichierData.read()
                tab_ligne = tab_ligne.split("\hline")

                ## SB --- DEBUT
                trace_me = False
                ##if 'rayon_IR_auto_tempe' in nom_oper:
                ##    trace_me = True
                ## SB --- FIN

                # Récupération des ENTREES
                description = "Entrée :\n"
                part = tab_ligne[1].split("\end")[0]
                # supprimer de qui traine après les '\\' de fermeture de la
                # colone (ex : commentaire dans
                # rayon_IR_auto_tempe.args.tex, 1ier paramètre)
                part = re.sub(r'(\\\\).*\n', r'\1', part)
                input_lines = part.split('\\\\')
                
                # compter les arguments de type vecteur d'entrée, pour
                # proposer les n° pour les $Arg
                nb_vectors_in = 0
                for line in input_lines:
                    line = line.replace('\n', ' ')
                    ## SB --- DEBUT
                    ##if trace_me:
                    ##    logging.debug(f":::: {nom_oper} : line : {line}")
                    ## SB --- FIN

                    # ajout de l'argument
                    if "&" in line and not line.startswith("%"):

                        nom_arg, type_arg, desc_arg = line.split("&")

                        nom_arg  = latex_formateur.suppr_carac_speciaux(nom_arg , trace_me).replace('\n','').replace(' ','')
                        type_arg = latex_formateur.suppr_carac_speciaux(type_arg, trace_me).replace(' ','').replace(',',', ')
                        desc_arg = latex_formateur.suppr_carac_speciaux(desc_arg, trace_me).strip()
                        # supprimer les ' ' surnuméraires de desc_arg
                        while '  ' in desc_arg:
                            desc_arg = desc_arg.replace('  ', ' ')
                        if type_arg.startswith('Vecteur'):
                            nb_vectors_in = nb_vectors_in + 1

                        # ajout de l'argument de la forme ([nom arg, type arguments])
                        arg_list += [[nom_arg, type_arg.replace(".", "")]]

                        # ajout de la ligne dans la description
                        description += f"{nom_arg:10s} {type_arg:18s} {desc_arg}\n"

                # Si un argument est '⋮' on réalise une répétition des aguments
                # ex: x1,x2, ... , x12 => ... est remplacé par x3, x4, x5 ... jusqu'à x11
                for i in range(len(arg_list)):
                    if "⋮" in arg_list[i]:
                        deb = re.findall(r'\d+', arg_list[i-1][0])# Premier nombre (non inclus)
                        fin = re.findall(r'\d+', arg_list[i+1][0])# Dernier nombre (non inclus)

                        # Si on a bien récupéré un nombre de fin (il y a parfois un "n" en indice et non un nombre)
                        if fin != [] and deb != []:
                            deb = int(deb[0])
                            fin = int(fin[0])
                            # texte avant le nombre
                            texte = re.findall(r'\D+', arg_list[i-1][0])[0]
                            # texte après le nombre si il y en a un
                            try:
                                texte2 = re.findall(r'\D+', arg_list[i-1][0])[1]
                            except:
                                texte2 = ""

                            # on suprime les ...
                            del arg_list[i]
                            # Ajout des arguments représentés par les ...
                            for x in range(fin-deb-1):
                                nom_arg = texte+str(x+deb+1)+texte2
                                arg_list.insert(i+x,[nom_arg,arg_list[x-1][1]])
                            break


                # Récupération des SORTIES
                description += "\nSortie :\n"
                input_lines = tab_ligne[2].split("\end")[0]
                for line in input_lines.split("\\\\"):
                    # ajout de l'argument
                    if "&" in line and not line.startswith("%"):
                        nom_arg, type_arg, desc_arg = line.split("&")

                        nom_arg  = latex_formateur.suppr_carac_speciaux(nom_arg , trace_me).replace("\n","").replace(" ","")
                        type_arg = latex_formateur.suppr_carac_speciaux(type_arg, trace_me).replace(" ","").replace(",",", ")
                        desc_arg = latex_formateur.suppr_carac_speciaux(desc_arg, trace_me).strip()

                        # ajout de l'argument de la forme ([nom arg, type arguments])
                        arg_list += [[nom_arg, type_arg]]

                        # ajout de la ligne dans la description
                        description += f"{nom_arg:10s} {type_arg:18s} {desc_arg}\n"

                # Récupération des ENTREES OPTIONNELLES
                arg_opt_list = dict()
                if len(tab_ligne) > 3:
                    description += "\nEntrée optionnelle :\n"
                    input_lines = tab_ligne[3].split("\end")[0]
                    for line in input_lines.split("\\\\"):
                        # ajout de l'argument
                        if "&" in line and not line.startswith("%"):
                            nom_arg, type_arg, desc_arg = line.split("&")

                            nom_arg = latex_formateur.suppr_carac_speciaux(nom_arg  , trace_me).replace("\n","").replace(" ","")
                            type_arg = latex_formateur.suppr_carac_speciaux(type_arg, trace_me).replace(" ","").replace(",",", ")
                            desc_arg = latex_formateur.suppr_carac_speciaux(desc_arg, trace_me).strip()

                            # ajout de l'argument optionnel sous de la forme { nom arg: type_arguments }
                            arg_opt_list[nom_arg] = type_arg

                            # ajout de la ligne dans la description
                            description += f"{nom_arg:10s} {type_arg:18s} {desc_arg}\n"


                description += latex_formateur.suppr_carac_speciaux(objet)

                # ajout du nouvel opérateur
                chap_oper_list += [operation(nom_oper, arg_list, arg_opt_list, description, nb_vectors_in)]

            # ajout les nouvelles valeurs
            self.oper_list          += chap_oper_list
            self.oper_list_par_chap += [[nom_chapitre, chap_oper_list]]

        fichierTotal.close()


    def find(self, nom):
        """
        Recherche une liste d'operations dont le nom commence par la
        chaine entree en parametre
        param :
            nom : String recherché dans oper_list

        return :
            Liste des operations correspondante (Operations[])
        """
        result_list = []
        for operation in self.oper_list:
            if operation.nom.startswith(nom):
                result_list += [operation]

        return result_list


    def get(self, nom):
        """
        Recherche l'operations dont le nom est entree en parametre
        param :
            nom : String recherché dans oper_list

        return :
            Operations correspondante (Operations) ou None
        """
        for operation in self.oper_list:
            if operation.nom == nom:
                return operation

        return None


    def exist(self, nom):
        """
        Recherche un nom dans la liste et retourne True si
        il est present, False sinon
        """
        for operation in self.oper_list:
            if operation.nom == nom:
                return True

        return False

