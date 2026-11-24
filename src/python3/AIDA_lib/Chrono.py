#!/usr/bin/env python3

"""
Gestion des fichiers .chrono.
"""

import os
import sys
import re
import datetime


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from fct_messages import (info, warning, stop_error, result, wait_user)


# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


class Chrono():
    """ Classe de gestion des fichiers .chrono.
    """

    def __init__(self, acqid=None, plateforme=None):
        """
            :param str() acqid      : acqid de l'acquisition.
            :param str() plateforme : nom long de plateforme (ex : 'atr')

            Note : les paramètres 'acqid' et 'plateforme' sont exclusifs :
                   - paramètre 'acqid' :
                     - permet d'interroger le fichier .chrono sur la date de
                       l'acquisition.
                   - paramètre 'plateforme' :
                     - permet de tester la syntaxe du fichier .chrono
                     - ne permet pas d'interroger le fichier .chrono
        """
        if not acqid and not plateforme:
            raise Exception ("Chrono::__init__ : spécifier acqid ou plateforme")

        if acqid and plateforme:
            raise Exception ("Chrono::__init__ : spécifier acqid ou plateforme")

        self.date_acq = None

        # pour quelle plateforme
        self.plateforme = plateforme
        if acqid:
            # vérifier l'existence du .inf, sinon le message d'exception
            # remonté n'est pas très compréhensiblle...
            inf_file = AIDA.ID_to_inf_path(acqid)
            if not os.path.isfile(inf_file):
                raise Exception (f"Chrono::__init__ : acqid = '{acqid}' : " +
                                  "pas de fichier .inf")

            try:
                self.plateforme = AIDA.ID_to_full(acqid)[0]
                self.date_acq   = AIDA.Inf(acqid).get_acquisition_borne("debut_acquisition")
            except Exception as e:
                raise Exception (f"Chrono::__init__ : acqid = '{acqid}' : " +
                                  "erreur d'acqid")

        # parsing du fichier
        AH = os.getenv('AIDA_HOME')
        AP = os.getenv('AIDA_PROFIL')
        self.filename =  os.path.join (AH, 'profils', AP, 'chrono', self.plateforme + '.chrono')
        try:
            self.content  = self.load()
        except Exception as e:
            raise Exception (f"Chrono::__init__ : acqid = '{acqid}' : {e}")

        # vérification des plages fournies
        self.chek_plage()


    def show_me(self):
        """ Debug...
        """
        print("Chrono::show_me :")
        print("  - plateforme =", self.plateforme)
        print("  - filename   =", self.filename)
        print("  - date_acq   =", self.date_acq)
        print("  - content    :")
        for section in self.content.keys():
            print(f"    - {section}  :")
            for plage in self.content[section]:
                print(f"      - de {plage['beg']} à {plage['end']} : {plage['val']}")


    def load(self):
        """ Retourne le contenu du fichier .chrono de la plateforme sous forme
            de dictionnaire.
            Les clés de ce dictionnaire sont les noms de section du
            fichier .chrono.
        """
        with open(self.filename, 'r') as handler:
            lines = [ l.split('#')[0] for l in handler.readlines() ]

        content = None
        pattern = r'(?P<beg>[^\s]+)\s*(?P<end>[^\s]+)\s*(?P<val>[^\s]+)$'
        for i, line in enumerate(lines, start=1):
            # ligne vide
            if len(line) == 0:
                continue

            # ligne de section
            if line[0] == '[':
                if not ']' in line:
                    warning(f"fichier : {os.path.basename(self.filename)}, " +
                            f"ligne {i} = '{line[:-1]}' : " +
                            "erreur de syntaxe.")
                    continue

                section, _ = line[1:].split(']')

                if not content:
                    content = dict()

                content[section] = list()
                continue

            # ligne de datation : débute par le siècle => il est raisonnable
            # de tester que le 1ier caractère est '2'.
            if line[0] == '2':
                match = re.match(pattern, line.strip())
                if match:
                    s_beg = match.group('beg')
                    s_end = match.group('end')
                    s_val = match.group('val')
                else:
                    warning(f"fichier : {os.path.basename(self.filename)}, " +
                            f"ligne {i} = '{line}' : " +
                            "erreur de syntaxe.")
                    continue

                # transformer les dates au format str() au format datetime()
                plage = {'beg':s_beg, 'end':s_end}
                for key, s_date in plage.items():
                    try:
                        dt = datetime.datetime.strptime(s_date, "%Y-%m-%dT%H:%M:%SZ")
                    except Exception as e:
                        warning(f"fichier : {os.path.basename(self.filename)}, " +
                                f"ligne {i} : date {key} = '{s_date}' : " +
                                "erreur de syntaxe.")
                        continue
                    plage[key] = dt

                plage['val']     = s_val
                plage['line_nb'] = i

                # enregistrer tout ça
                content[section].append(plage)

        return content


    def chek_plage(self):
        """ Vérifie les plages fournies dans le .chrono...
        """
        for section in self.content.keys():
            prev_end = None
            for plage in self.content[section]:
                if plage['beg'] >= plage['end']:
                    warning(f"fichier : {os.path.basename(self.filename)}, " +
                            f"ligne {plage['line_nb']} : " +
                            f"date_de_début ({plage['beg']}) >= date_de_fin ({plage['end']})")
                    continue

                if prev_end:
                    if plage['beg'] != prev_end + datetime.timedelta(seconds=1):
                        warning(f"fichier : {os.path.basename(self.filename)}, " +
                                f"ligne {plage['line_nb']} : trou dans la datation : " +
                                f"date_de_début ({plage['beg']}) != date_de_fin_précédente + 1_seconde ({prev_end})")

                prev_end = plage['end']

        return


    def get_value(self, name, date_acq=None):
        """ Retourne la valeur de la variable 'name' pour la date de l'acqid
            ou spécifiée dans le paramètre 'date_acq'.

            :param str()      name    : nom de la variable à chercher
                                        (<=> nom de section dans le fichier
                                         .chrono.)
            :param datetime() date_acq: si spécifiée, cette date est utilisée
                                        à la place de la date de
                                        "debut_acquisition" de l'acqid.
                                        (a priori, utilise seulement lorsque
                                        l'instenciation a été faite sur une
                                        plateforme plutôt que sur un acqid).

            :return: value (= '' si non trouvée)
            :rtype: str()

            :raise: Exception : s'il n'y a pas de datation valide
                              : si name n'est pas trouvé
                              : s'il n'y a pas de valeur pour name à la date
                                spécifiée
        """
        if not date_acq:
            date_acq = self.date_acq

        if not date_acq:
            msg = f"Chrono::get_value({name}) : pas de datation valide"
            raise Exception (msg)

        if not name in self.content.keys():
            raise Exception (f"Chrono::get_value : " +\
                             f"la variable '{name}' n'existe pas")

        for plage in self.content[name]:
            if date_acq >= plage['beg'] and  date_acq <= plage['end']:
                return plage['val']

        raise Exception (f"Chrono::get_value : " +\
                         f"pas de valeur pour '{name}' à la date du {date_acq}")


if __name__ == '__main__':
    os.system('clear')

    ### test sur lannemezan-mais.chrono qui contient une ligne de datation
    ### ce terminant par un commentaire
    # sur une plateforme
    plateforme = 'lannemezan-mais'
    print(f"\n* Chrono (plateforme={plateforme})")
    chrono = Chrono(plateforme=plateforme)
    chrono.show_me()
    wait_user()

    print("** récupération de valeur")
    variable = 'H_CANOPEE'
    ###try:
    ###    value = chrono.get_value(variable)
    ###    print(f"   - pour plateforme = {plateforme} : '{variable}' = >{value}<")
    ###except Exception as e:
    ###    print(f"ERREUR : Chrono(plateforme={plateforme}) :")
    ###    warning(f"{e}")
    ###wait_user()

    date_acq = AIDA.Inf('ls230290').get_acquisition_borne("debut_acquisition")
    try:
        value = chrono.get_value(variable, date_acq=date_acq)
        print(f"   - pour plateforme = {plateforme}, à la date du {date_acq} : '{variable}' = >{value}<")
    except Exception as e:
        print(f"ERREUR : Chrono(plateforme={plateforme}) :")
        warning(f"{e}")
    wait_user()

    date_acq = AIDA.Inf('ls230297').get_acquisition_borne("debut_acquisition")
    try:
        value = chrono.get_value(variable, date_acq=date_acq)
        print(f"   - pour plateforme = {plateforme}, à la date du {date_acq} : '{variable}' = >{value}<")
    except Exception as e:
        print(f"ERREUR : Chrono(plateforme={plateforme}) :")
        warning(f"{e}")
    wait_user()




    # sur une plateforme
    plateforme = 'atr'
    print(f"\n* Chrono (plateforme={plateforme})")
    chrono = Chrono(plateforme=plateforme)
    chrono.show_me()
    wait_user()

    print("** récupération de valeur")
    variable = 'DELAI_LICOR_RS'
    try:
        value = chrono.get_value(variable)
        print(f"   - pour plateforme = {plateforme} : '{variable}' = >{value}<")
    except Exception as e:
        print(f"ERREUR : Chrono(plateforme={plateforme}) :")
        warning(f"{e}")
    wait_user()

    date_acq = AIDA.Inf('as140007').get_acquisition_borne("debut_acquisition")
    try:
        value = chrono.get_value(variable, date_acq=date_acq)
        print(f"   - pour plateforme = {plateforme}, à la date du {date_acq} : '{variable}' = >{value}<")
    except Exception as e:
        print(f"ERREUR : Chrono(plateforme={plateforme}) :")
        warning(f"{e}")
    wait_user()

    date_acq = AIDA.Inf('as160007').get_acquisition_borne("debut_acquisition")
    try:
        value = chrono.get_value(variable, date_acq=date_acq)
        print(f"   - pour plateforme = {plateforme}, à la date du {date_acq} : '{variable}' = >{value}<")
    except Exception as e:
        print(f"ERREUR : Chrono(plateforme={plateforme}) :")
        warning(f"{e}")
    wait_user()



    # sur un acqid
    acqid = 'Tf210001'
    print(f"\n* Chrono (acqid={acqid})")
    chrono = Chrono(acqid=acqid)
    chrono.show_me()
    wait_user()

    # récupération de valeur
    print("** récupération de valeur")
    variable = 'CHOIX_RAYON_IRM'
    try:
        value = chrono.get_value(variable)
        print(f"   - pour acqid = {acqid} : '{variable}' = >{value}<")
    except Exception as e:
        print(f"ERREUR : Chrono(acqid={acqid}) :")
        warning(f"{e}")
    wait_user()



    # erreurs
    print(f"\n* Erreur Chrono :")
    try:
        chrono = Chrono('Tf21001')
    except Exception as e:
        print(f"ERREUR 1 : Chrono() :")
        warning(f"{e}")

    try:
        chrono = Chrono(acqid=acqid, plateforme=plateforme)
    except Exception as e:
        print(f"ERREUR 2 : Chrono(acqid={acqid}, plateforme={plateforme}) :")
        warning(f"{e}")

    try:
        chrono = Chrono()
    except Exception as e:
        print(f"ERREUR 3 : Chrono() :")
        warning(f"{e}")
