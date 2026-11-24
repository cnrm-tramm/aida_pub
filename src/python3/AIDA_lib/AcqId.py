#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import datetime

import numpy as np

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA


class AcqIdVol(object):
    """
    Classe d'objet pour les acqid où le numero d'acquisition correspond au
    numero du vol dans l'année.
    On peut initialiser soit :
    - avec une chaine AcqId,
    - avec l'abréviation de la plateforme et la date (sous forme d'un datetime).

    Ce type d'acqid correspond aux plateformes où nom_serie_mesure=Vol
    """

    @staticmethod
    def date_to_acqid(abrev_pltf, dt_date, all=False):
        """ Transformation de plateforme + date(de type datetime) en acqid.

            Recherche des acquisitions correspondantes aux critères passés en
            argument.

            :param abrev_pltf: abréviation de la plateforme.
            :type  abrev_pltf: char*2

            :param dt_date:    limite la recherche à 'date'.
            :type  dt_date:    datetime

            :param all:        False : seulement la 1ière acquisition trouvée.
                               True  : toutes les acquisitions trouvées.
            :type  all:        bool

            :return: if all=False, nom d'acqid.
                     if all=True , liste de noms d'acqid.
            :rtype: str ou list

            :raise: pas d'acqid pour cette date
            :raise: 'dt_date' n'est pas un datetime
        """

        if not isinstance(dt_date, datetime.datetime):
            raise Exception("L'argument dt_date n'est pas de type datetime")

        # lecture du fichier plate-forme
        if (AIDA.plt_by_abrev == {}):
            AIDA.ini_plt_indexes()

        # il faut chercher dans les fichiers .inf
        # => methode sauvage, on lit tous les fichiers .inf.
        # TODO : à optimiser
        liste_inf = list(AIDA.existing_inf_files(
                            [AIDA.AIDA_abrev_to_plt(abrev_pltf)],
                            liste_annees=[dt_date.year]))

        tab_date = np.array([ Inf.get_date_acq() for Inf in liste_inf ])
        idx_date = np.where(tab_date == dt_date.date())[0]

        if len(idx_date) == 0:
            raise Exception("Pas d'acqid correspondant a cette date")

        if len(idx_date) == 1:
            if all:
                return [ liste_inf[idx_date[0]].acqid ]
            else:
                return liste_inf[idx_date[0]].acqid
        else:
            # cas de plusieurs vols par jour on renvoie l'acqid du vol
            # dont l'heure de debut d'acquisition est la plus proche de
            # date
            if all:
                liste_all = [ inf.acqid for inf in np.array(liste_inf)[idx_date] ]
                liste_all.sort(key=str.swapcase)
                return liste_all
            else:
                tab_date = np.array([ liste_inf[i].get_acquisition_borne("debut_acquisition") for i in idx_date ])
                imin = np.argmin(np.abs(tab_date - dt_date))
                return liste_inf[idx_date[imin]].acqid


    def __init__(self, acqid="", plateforme="", date=None, read_inf=True):
        """
            :param acqid:      nom d'acqid.
            :type  acqid:      str
            :param plateforme: abréviation de la plateforme.
            :type  plateforme: str
            :param date:       date de l'acquisition.
            :type  date:       datetime
        """
        if plateforme and date:
            self._valeur = self.date_to_acqid(plateforme, date)
        elif acqid:
            self._valeur = acqid
        else:
            self._valeur = None

        if read_inf:
            Inf = AIDA.Inf(self._valeur)
            try:
                self._date = Inf.get_acquisition_borne("debut_acquisition")
            except Exception as e:
                # pour les .inf mal formés (ex : me0208.inf, wk9513.inf...)
                # essayer de récupérer la date de [IDENTIFICATION]...
                try:
                    self._date = Inf.get_date_acq()
                except Exception as e:
                    self._date = None


    def existing_acqids(self):
        """ Generator qui yield tous les noms d'acqids de la plateforme de
            l'objet.
        """
        for acqid in existing_acqids_per_abrev(self._valeur[0:2]):
            yield acqid


    def __str__(self):
        return (self._valeur)

    def __add__(self, other):
        # récupération de tous les noms d'acqids de la plateforme
        acqids = [ a for a in self.existing_acqids() ]

        idx = acqids.index(self._valeur)

        if idx + other <= len(acqids) - 1:
            acqid = self.__class__(acqids[idx + other])
            return acqid
        else:
            return None

    def __sub__(self, other):
        # récupération de tous les noms d'acqids de la plateforme
        acqids = [ a for a in self.existing_acqids() ]

        idx = acqids.index(self._valeur)

        if idx - other >= 0:
            acqid = self.__class__(acqids[idx - other])
            return acqid
        else:
            return None

    def __lt__(self, other):
        if (self is None or other is None):
            return False

        num1 = int(self._valeur[2:8])
        num2 = int(other._valeur[2:8])
        if num1 < num2:
            return True
        else:
            return False

    def __gt__(self, other):
        if (self is None or other is None):
            return False

        num1 = int(self._valeur[2:8])
        num2 = int(other._valeur[2:8])
        if num1 > num2:
            return True
        else:
            return False

    def __le__(self, other):
        if (self is None or other is None):
            return False

        num1 = int(self._valeur[2:8])
        num2 = int(other._valeur[2:8])
        if num1 <= num2:
            return True
        else:
            return False

    def __ge__(self, other):
        if (self is None or other is None):
            return False

        num1 = int(self._valeur[2:8])
        num2 = int(other._valeur[2:8])
        if num1 >= num2:
            return True
        else:
            return False

    def __eq__(self, other):
        if (self is None or other is None):
            return False

        num1 = int(self._valeur[2:8])
        num2 = int(other._valeur[2:8])
        if num1 <= num2:
            return True
        else:
            return False

    def __ne__(self, other):
        if (self is None or other is None):
            return False

        num1 = int(self._valeur[2:8])
        num2 = int(other._valeur[2:8])
        if num1 != num2:
            return True
        else:
            return False

    def acqid_to_date(self):
        """ Transformation d'un AcqId en date de type datetime """

        return self._date


class Acquisition(AcqIdVol):
    """
    Cette classe N'EST PAS ENCORE BIEN DÉFINIE mais il semble quelle soit
    identique à la classe AcqIdVol...
    """
    def __init__(self, acqid="", plateforme="", date=None, read_inf=True):
        super().__init__(acqid, plateforme, date, read_inf)


class Lacher(AcqIdVol):
    """
    Cette classe n'est pas DU TOUT définie...
    Faisons comme si elle était identique à la classe AcqIdVol...
    """
    def __init__(self, acqid="", plateforme="", date=None, read_inf=True):
        super().__init__(acqid, plateforme, date, read_inf)



class AcqIdLeV(AcqIdVol):
    """
    Classe d'objet pour les acqid où le numero d'acquisition correspond au
    numero du vol dans l'année sur 3 digits suivi du numéro du lâcher sur un
    caractère [0-9 a-z A-Z] soit 62 numéros possibles.
    Ce type d'acqid correspond aux plateformes où nom_serie_mesure=Lacher_en_vol
    AcqIdLev hérite de AcqIdVol

    Utilisation :
        AcqIdLeV (acqid=<chaine acqid>, plateforme=<chaine abréviation plateforme>, date=<datetime>)
    """



    def existing_acqids(self):
        """ Generator qui yield tous les noms d'acqids de la plateforme de
            l'objet.
        """
        for acqid in existing_acqids_per_abrev(self._valeur[0:2]):
            yield acqid


    def __lt__(self, other):
        if (self is None or other is None):
            return False

        num1 = self._valeur[2:8]
        num2 = other._valeur[2:8]
        to_compare = [num1, num2]
        to_compare.sort(key=str.swapcase)
        if to_compare[0] == num1 and num1 != num2:
            return True
        else:
            return False

    def __gt__(self, other):
        if (self is None or other is None):
            return False

        num1 = self._valeur[2:8]
        num2 = other._valeur[2:8]

        to_compare = [num1, num2]
        to_compare.sort(key=str.swapcase)
        if to_compare[1] == num1 and num1 != num2:
            return True
        else:
            return False

    def __le__(self, other):
        if (self is None or other is None):
            return False

        num1 = self._valeur[2:8]
        num2 = other._valeur[2:8]
        to_compare = [num1, num2]
        to_compare.sort(key=str.swapcase)
        if to_compare[0] == num1 or num1 == num2:
            return True
        else:
            return False

    def __ge__(self, other):
        if (self is None or other is None):
            return False

        num1 = self._valeur[2:8]
        num2 = other._valeur[2:8]
        to_compare = [num1, num2]
        to_compare.sort(key=str.swapcase)
        if to_compare[1] == num1 or num1 == num2:
            return True
        else:
            return False

    def __eq__(self, other):
        if (self is None or other is None):
            return False

        num1 = self._valeur[2:8]
        num2 = other._valeur[2:8]
        if num1 == num2:
            return True
        else:
            return False

    def __ne__(self, other):
        if (self is None or other is None):
            return False

        num1 = self._valeur[2:8]
        num2 = other._valeur[2:8]
        if num1 != num2:
            return True
        else:
            return False


class AcqIdDoY(object):
    """
    Classe d'objet pour les acqid où le numero d'acquisition correspond au
    numero du jour dans l'année.
    On peut initialiser soit avec une chaine AcqId, soit avec
    l'abréviation de la plateforme et la date sous forme d'un datetime.
    Ce type d'acqid correspond aux plateformes où nom_serie_mesure=Journee

    Utilisation :
        AcqIDoY (acqid=<chaine acqid>, plateforme=<chaine abréviation plateforme>, date=<datetime>)
    """

    @staticmethod
    def date_to_acqid(plateforme, date, all=False):
        """ Transformation de plateforme + date(de type datetime) en acqid """
        if isinstance(date, datetime.datetime):
            acqid = plateforme[0:2] + date.strftime("%y") + '{:04d}'.format(int(date.strftime("%j")))
            if all:
                return acqid.split()
            else:
                return acqid
        else:
            raise Exception("L'argument date n'est pas de type datetime")

    def __init__(self, acqid="", plateforme="", date=None):
        if plateforme and date:
            self._valeur = self.date_to_acqid(plateforme, date)
        elif acqid:
            self._valeur = acqid
        else:
            self._valeur = None
        self._date = datetime.datetime.strptime(self._valeur[2:8], "%y0%j")


    def existing_acqids(self):
        """ Generator qui yield tous les noms d'acqids de la plateforme de
            l'objet.
        """
        for acqid in existing_acqids_per_abrev(self._valeur[0:2]):
            yield acqid



    def __str__(self):
        return (self._valeur)

    def __add__(self, other):
        date = self.acqid_to_date()
        date_new = date + datetime.timedelta(days=other)
        acqid = self.__class__(plateforme=self._valeur[0:2], date=date_new)
        return acqid

    def __sub__(self, other):
        date = self.acqid_to_date()
        date_new = date - datetime.timedelta(days=other)
        acqid = self.__class__(plateforme=self._valeur[0:2], date=date_new)
        return acqid

    def __lt__(self, other):
        date1 = self.acqid_to_date()
        date2 = other.acqid_to_date()
        if date1 < date2:
            return True
        else:
            return False

    def __gt__(self, other):
        date1 = self.acqid_to_date()
        date2 = other.acqid_to_date()
        if date1 > date2:
            return True
        else:
            return False

    def __le__(self, other):
        date1 = self.acqid_to_date()
        date2 = other.acqid_to_date()
        if date1 <= date2:
            return True
        else:
            return False

    def __ge__(self, other):
        date1 = self.acqid_to_date()
        date2 = other.acqid_to_date()
        if date1 >= date2:
            return True
        else:
            return False

    def __eq__(self, other):
        date1 = self.acqid_to_date()
        date2 = other.acqid_to_date()
        if date1 == date2:
            return True
        else:
            return False

    def __ne__(self, other):
        date1 = self.acqid_to_date()
        date2 = other.acqid_to_date()
        if date1 != date2:
            return True
        else:
            return False

    def acqid_to_date(self):
        """ Transformation d'un AcqId en date de type datetime """
        return self._date


class AcqId(object):
    """
    Classe d'objet pour les acqid
    On peut initialiser soit avec une chaine AcqId, soit avec
    l'abréviation de la plateforme et la date sous forme d'un datetime :

    Renvoie en fonction de la plateforme une classe AcqIdVol ou AcqIdDoY

    Utilisation :
        AcqId (acqid=<chaine acqid>, plateforme=<chaine abréviation plateforme>, date=<datetime>)
    """

    def __new__(cls, acqid="", plateforme="", date=None, read_inf=True):

        if not acqid and not (date and plateforme):
            raise Exception("Erreur : il faut acqid ou plateforme et date")
        
        if (AIDA.plt_by_abrev == {}):
            AIDA.ini_plt_indexes()

        if acqid:
            plateforme = acqid[0:2]

        nom_serie_mesure = AIDA.plt_by_abrev[plateforme].nom_serie_mesure

        if nom_serie_mesure == 'Journee':
            if acqid[4:] > "0366":
                print(f"-+- nom_serie_mesure '{nom_serie_mesure}' et acqid '{acqid}' incompatibles : > 0366")
                raise Exception("Erreur : type mesure = 'Journee' et numéro > 366")

            classe_acqid = object.__new__(AcqIdDoY, acqid=acqid, plateforme=plateforme, date=date)
            classe_acqid.__init__(acqid=acqid, plateforme=plateforme, date=date)

        elif nom_serie_mesure == 'Lacher_en_vol':
            classe_acqid = object.__new__(AcqIdLeV, acqid=acqid, plateforme=plateforme, date=date)
            classe_acqid.__init__(acqid=acqid, plateforme=plateforme, date=date)

        elif nom_serie_mesure == 'Acquisition':
            classe_acqid = object.__new__(Acquisition, acqid=acqid, plateforme=plateforme, date=date, read_inf=read_inf)
            classe_acqid.__init__(acqid=acqid, plateforme=plateforme, date=date, read_inf=read_inf)

        elif nom_serie_mesure == 'Lacher':
            classe_acqid = object.__new__(Lacher, acqid=acqid, plateforme=plateforme, date=date, read_inf=read_inf)
            classe_acqid.__init__(acqid=acqid, plateforme=plateforme, date=date, read_inf=read_inf)

        elif nom_serie_mesure == 'Vol':
            classe_acqid = object.__new__(AcqIdVol, acqid=acqid, plateforme=plateforme, date=date, read_inf=read_inf)
            classe_acqid.__init__(acqid=acqid, plateforme=plateforme, date=date, read_inf=read_inf)

        elif nom_serie_mesure == 'Drone':
            classe_acqid = object.__new__(AcqIdVol, acqid=acqid, plateforme=plateforme, date=date, read_inf=read_inf)
            classe_acqid.__init__(acqid=acqid, plateforme=plateforme, date=date, read_inf=read_inf)

        else:
            print("AcqId::__new__ : ne sait pas traiter le nom_serie_mesure = " + nom_serie_mesure)
            raise("AcqId::__new__ : ne sait pas traiter le nom_serie_mesure = " + nom_serie_mesure)

        return classe_acqid


def get_list_acqids(abrev_pltf, dt_date):
    """
    Retourne la liste d'objets acqid associés à une plateforme et à une date :
    il peut exister plusieurs acqids pour les acqids de type vol (plusieurs
    vols le même jour).

    :abrev_pltf: str():      abréviation de la plateforme
    :dt_date:    datetime(): date au format datetime

    :return: list(): liste d'objets AcqId()
    """
    try:
        acqId = AcqId(plateforme=abrev_pltf, date=dt_date)
    except:
        return []

    try:
        liste_acq = acqId.date_to_acqid(abrev_pltf, dt_date, all=True)
        return [ AcqId(acqid=acq) for acq in liste_acq ]
    except:
        return []


def get_acqids_between(first_acqid, last_acqid, acqids=None):
    """ Retourne la liste de tous les noms d'acqids entre :
            [first_acqid, last_acqid].

        :param first_acqid:  nom du premier acqid.
        :typr  first_acqid:  str
        :param last_acqid:   nom du premier acqid.
        :typr  last_acqid:   str
        :param acqids:       si fournit, recherhe dans cette liste,
                             sinon cherche dans acqid.existing_acqids()
        :typr  acqids:       list

        :return: liste de noms d'acqid,
                 ou une liste vide si l'un ou l'autre des acqids n'est pas
                 trouvé.
        :rtype: list

        :raise: plateformes différentes
    """
    if first_acqid[0:2] != last_acqid[0:2]:
        raise Exception("get_acqids_between : plateformes différentes !")

    if not acqids:
        ## créer un objet de type AcqId pour accéder aux méthodes de la classe...
        #try :
        #    acqid = AcqId(first_acqid, read_inf=False)
        #except Exception:
        #    print(f'DBG get_acqids_between : PB DE CREATION AcqId pour {first_acqid}')
        #    input('...continue')
        #    return []

        ## récupération de tous les noms d'acqids de la plateforme
        #acqids = [ a for a in acqid.existing_acqids() ]

        acqids = [ a for a in existing_acqids_per_abrev(first_acqid[0:2]) ]
        if not acqids:
            return []

    acqids.sort()
    try:
        idx_begin = acqids.index(first_acqid)
        idx_end   = acqids.index(last_acqid) + 1
    except ValueError as e:
        return []

    return acqids[idx_begin:idx_end]


def existing_acqids_per_abrev(abrev_pltf):
    """ Generator qui yield tous les noms d'acqids de la plateforme.

        :param abrev_pltf: abréviation de la plateforme.
        :type  abrev_pltf: char*2
    """
    AIDA_META = AIDA.AIDA_getenv('meta')
    AIDA_INF = os.path.join(AIDA_META, "INF")
    
    # masque pour la plateforme avant l'an 2000
    path_inf_avant = '{}/{}[7-9]*.inf'.format(AIDA_INF, abrev_pltf)

    # récupèration des basenames sans l'extension
    acqids_avant = [ os.path.splitext(os.path.basename(f))[0] \
                   for f in glob.glob(path_inf_avant) ]

    # tri selon l'ordre chiffre, minuscule, majuscule (pour les AcqIdLeV)
    acqids_avant.sort(key=str.swapcase)

    # masque pour la plateforme apres l'an 2000
    path_inf_apres = '{}/{}[0-6]*.inf'.format(AIDA_INF, abrev_pltf)

    # récupèration des basenames sans l'extension
    acqids_apres = [ os.path.splitext(os.path.basename(f))[0] \
                   for f in glob.glob(path_inf_apres) ]

    # tri selon l'ordre chiffre, minuscule, majuscule (pour les AcqIdLeV)
    acqids_apres.sort(key=str.swapcase)


    for acqid in acqids_avant + acqids_apres:
        yield acqid


def get_last_acqid(abrev_pltf, acqids=None):
    """ Retourne le nom du dernier acqid pour la plateforme passée en argument.

        :param abrev_pltf:  abréviation de la plateforme.
        :type  abrev_pltf:  char*2
        :param acqids:      si fournit, recherhe dans cette liste,
                            sinon cherche dans existing_acqids_per_abrev().
        :type  acqids:      list

        :return: si trouvé, nom du dernier acqid.
                 sinon une chaine vide;
        :rtype:  str
    """
    if not acqids:
        # récupération de tous les noms d'acqids de la plateforme
        acqids = [ a for a in existing_acqids_per_abrev(abrev_pltf) ]

        if not acqids:
            return ''

    acqids.sort()
    return acqids[-1]


if __name__ == '__main__':
    from fct_messages import (info, warning, stop_error, result, wait_user)

    os.system('clear')

    ### TEST MODIF de AcqID::_new_
    print("\n* Test des modifications du 22 mars 2021 de AcqId")
    acqid_obj = AcqId(plateforme='as', date=datetime.datetime(2009, 5, 6))
    print("** quel est sa  valeur ?", acqid_obj._valeur)
    print("** quel est sa  date   ?", acqid_obj._date)
    wait_user()
    

    ### TEST PRELIMINAIRE
    acqid = 'as380012'
    print("\n* Test AcqId pour acqid inexistant :", acqid)
    acqid_obj = AcqId(acqid)
    print("** quel est sa  valeur ?", acqid_obj._valeur)
    print("** quel est sa  date   ?", acqid_obj._date)
    wait_user()

    acqid = 'as180012'
    print("\n* Test AcqId et passage d'année à partir de ", acqid)
    acqid_obj = AcqId(acqid)
    for i in range(1, 5):
        print("acqid_obj + ", i, " = ", acqid_obj + i,
            ", acqid_obj - ", i, " = ", acqid_obj - i)
    wait_user()


    print("* existing_acqids")
    print("** les acqids pour ", acqid)
    all_acqids_obj = [ a for a in acqid_obj.existing_acqids() ]

    print("** les acqids pour ", acqid[0:2])
    all_acqids     = [ a for a in existing_acqids_per_abrev(acqid[0:2]) ]

    if all_acqids_obj != all_acqids:
        print(" LES LISTES SONT DIFFERENTES !!!")
        sys.exit(1)
    else:
        print(" les listes sont égales")
    wait_user()

    print("** index de :", acqid, "=", all_acqids.index(acqid))
    try:
        print("** index de : as6801    =", all_acqids.index('as6801'))
    except ValueError as e:
        result("ERROR : msg = >" + str(e) + "<")
    try:
        print("** index de : as280001  =", all_acqids.index('as280001'))
    except ValueError as e:
        result("ERROR : msg = >" + str(e) + "<")
    wait_user()
    ### TEST PRELIMINAIRE


    abrev_pltf = 'as'

    dt_dates = [ datetime.datetime(2018, 11, 7),
                 datetime.datetime(2019, 1, 16),
               ]


    # AcqIdVol.date_to_acqid : OK
    # ----------------------
    for dt_date in dt_dates:
        print("* AcqIdVol.date_to_acqid({a}, {d}, all=False)".
              format(a=abrev_pltf, d=dt_date))
        single_acqid = AcqIdVol.date_to_acqid(abrev_pltf, dt_date, all=False)
        print("  -", single_acqid, " (single)")
        wait_user()

        print("* AcqIdVol.date_to_acqid({a}, {d}, all=True)".
              format(a=abrev_pltf, d=dt_date))
        liste_acq = AcqIdVol.date_to_acqid(abrev_pltf, dt_date, all=True)
        for acq in liste_acq:
            print("  -", acq, "(from list)")
        wait_user()

    # AcqIdVol.date_to_acqid : RAISE
    # ----------------------
    dt_date = "07/11/2018"
    print("* AcqIdVol.date_to_acqid({a}, {d}, all=True)".
              format(a=abrev_pltf, d=dt_date))
    try:
        liste_acq = AcqIdVol.date_to_acqid(abrev_pltf, dt_date, all=True)
    except Exception as e:
        result("ERROR : msg = >" + str(e) + "<")
    wait_user()

    dt_date = datetime.datetime(2029, 1, 16)
    print("* AcqIdVol.date_to_acqid({a}, {d}, all=True)".
              format(a=abrev_pltf, d=dt_date))
    try:
        liste_acq = AcqIdVol.date_to_acqid(abrev_pltf, dt_date, all=True)
    except Exception as e:
        result("ERROR : msg = >" + str(e) + "<")
    wait_user()


    # get_list_acqids : OK
    # ---------------
    for dt_date in dt_dates:
        print("* get_list_acqids({a}, {d})".
              format(a=abrev_pltf, d=dt_date))
        liste_acq = get_list_acqids(abrev_pltf, dt_date)
        for acq in liste_acq:
            print("  -", acq, "(from list)")
        wait_user()

    # get_list_acqids : no data or masked Exception
    # ---------------
    dt_date = "07/11/2018"
    print("* get_list_acqids({a}, {d})".
          format(a=abrev_pltf, d=dt_date))
    liste_acq = get_list_acqids(abrev_pltf, dt_date)
    if not liste_acq:
        print("  - NO DATA")
    else:
        for acq in liste_acq:
            print("  -", acq, "(from list)")
    wait_user()

    dt_date = datetime.datetime(2029, 1, 16)
    print("* get_list_acqids({a}, {d})".
              format(a=abrev_pltf, d=dt_date))
    liste_acq = get_list_acqids(abrev_pltf, dt_date)
    if not liste_acq:
        print("  - NO DATA")
    else:
        for acq in liste_acq:
            print("  -", acq, "(from list)")
    wait_user()


    # get_last_acqid
    # ---------------
    abrev_pltfs = [
            'as',
            'fs',
            'gi',
            ]
    all_acqids  = [
            [a for a in AIDA.existing_inf_files(['atr']               , names_only=True) ],
            [a for a in AIDA.existing_inf_files(['falcon']            , names_only=True) ],
            [a for a in AIDA.existing_inf_files(['gillot-aeroport-mf'], names_only=True) ],
            ]

    for abrev_pltf, list_acqids in zip(abrev_pltfs, all_acqids):
        print("* get_last_acdid({a})".
            format(a=abrev_pltf))
        print("  -", get_last_acqid(abrev_pltf))

        print("* get_last_acdid({a}, list)".
            format(a=abrev_pltf))
        print("  -", get_last_acqid(abrev_pltf, acqids=list_acqids))
        print()

        wait_user()


    # get_acqids_between : OK
    # ------------------
    begin = 'as0897'
    end   = 'as090003'
    print("* get_acqids_between({b}, {e})".
        format(b=begin, e=end))
    liste_acq = get_acqids_between(begin, end)
    for acq in liste_acq:
        print("  -", acq, "(from list)")

    print("* get_acqids_between({b}, {e}, liste)".
        format(b=begin, e=end))
    liste_acq = get_acqids_between(begin, end, acqids=all_acqids[0])
    for acq in liste_acq:
        print("  -", acq, "(from list)")
    wait_user()

    # get_acqids_between : ERROR
    # ------------------
    begin = 'as0897'
    end   = 'as490003'
    print("* get_acqids_between({b}, {e})".
        format(b=begin, e=end))
    liste_acq = get_acqids_between(begin, end)
    if not liste_acq:
        print("  - NO DATA")
    else:
        for acq in liste_acq:
            print("  -", acq, "(from list)")
    wait_user()

    # get_acqids_between : ERROR
    # ------------------
    begin = 'ZZ0897'
    end   = 'ZZ490003'
    print("* get_acqids_between({b}, {e})".
        format(b=begin, e=end))
    liste_acq = get_acqids_between(begin, end)
    if not liste_acq:
        print("  - NO DATA")
    else:
        for acq in liste_acq:
            print("  -", acq, "(from list)")
    wait_user()


    # classe Acquisition
    # ------------------
    print("\n* Test de la class Acquisition")
    acqid_acquisition = "Cl040134"
    acqid_obj = AcqId(acqid=acqid_acquisition)
    print("** quelle est sa  valeur   ?", acqid_obj._valeur)
    print("** quelle est sa  date     ?", acqid_obj._date)
    inf = AIDA.Inf(acqid_obj._valeur)
    print("** quelle est sa  campagne ?",
              inf.get_field_value('IDENTIFICATION', 'campagne'))

