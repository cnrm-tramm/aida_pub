#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Module de gestion du temps en lien notamment avec les acqid de AIDA.
"""
import os
import sys
import datetime as dt
from dateutil.relativedelta import relativedelta # @UnresolvedImport
AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
import AIDA  # @UnresolvedImport
import AcqIdDoY as ACQ # @UnresolvedImport

def str2datetime(str_time):
    """
        Convertit une chaine de caractère AAAAMMJJHHMMSS.sss en datetime.
        
        :param str_time: la chaîne à convertir
        :type str_time: str
        :return : un datetime ou None si la chaîne n'a pas pu être convertie
        :rtype : datetime
    """
    
    try :
        n = len(str_time)
        if n > 14 :
            time = dt.datetime.strptime(str_time,"%Y%m%d%H%M%S.%f")
        elif n == 14 :
            time = dt.datetime.strptime(str_time,"%Y%m%d%H%M%S")
        elif n == 12 :
            time = dt.datetime.strptime(str_time,"%Y%m%d%H%M")
        elif n == 10 :
            time = dt.datetime.strptime(str_time,"%Y%m%d%H")
        elif n == 8 :
            time = dt.datetime.strptime(str_time,"%Y%m%d")
        elif n == 6 :
            time = dt.datetime.strptime(str_time,"%Y%m")
        elif n == 4 :
            time = dt.datetime.strptime(str_time,"%Y")    
    except :
        time = None
    return time

def acqid2periode(acqid, frequence = 0, time_bnds = None):
    """
        Retourne la période couverte par l'acqid.
        Pour définir le premier et le dernier temps de la période on utilise time_bnds.
        Le principe est de retenir pour premier temps celui qui couvre [0,periode[.
        Pour dernier temps on retient celui qui couvre [24-periode, 0[.
        Si duree_vecteur = acquisition, retourne None,None.
        Le comportement par défaut pour les autres duree_vecteur est 0+p/2, 24+p/2, ce qui
        correspond à une datation de type fin de période.
        
        :param acqid: l'acqid
        :type acqid: str
        :param frequence: la fréquence en Hz
        :type frequence: float
        :return: date de début, date de fin
        :rtype: tuple de datetime
    """
    plateforme, _annee, _num = AIDA.ID_to_full(acqid)
    abrev = AIDA.liste_plt_to_abrev([plateforme])[0]
    if frequence != 0 :
        periode = 1./frequence
        if time_bnds == None or time_bnds.lower().startswith("vector") :
            # comportement par défaut
            decalage = periode/2.
            date_deb = ACQ.AcqIdDoY(acqid).acqid_to_date() + dt.timedelta(seconds = decalage)
            #print("Comportement par défaut : freq={} decalage={} date_deb={}".format(frequence, decalage, date_deb))
        else :
            # on calcule en fonction de time_bnds et de periode
            ratio = float(time_bnds.split(',')[0])/periode
            if ratio < -0.5 :
                decalage = periode/2
            else:
                decalage = -periode/2
            date_deb = ACQ.AcqIdDoY(acqid).acqid_to_date() + dt.timedelta(seconds = decalage)
            #print("Comportement avec time_bnds : time_bnds={} ratio={} freq={} periode={} decalage={} date_deb={}".format(time_bnds, ratio, frequence, periode, decalage, date_deb))

    else :
        date_deb = ACQ.AcqIdDoY(acqid).acqid_to_date()
    AIDA.ini_plt_indexes()
    duree = AIDA.plt_by_abrev[abrev].duree_vecteur
    if duree.lower() == "journee" :
        date_fin = date_deb + relativedelta(days = 1)
    elif duree.lower() == "mois" :
        date_fin = date_deb + relativedelta(months = 1)
    elif duree.lower() == "annee" :
        date_fin = date_deb + relativedelta(years = 1)
    else :
        return None,None
    
    return date_deb, date_fin
    
def periode2acqid(debut, fin, plateforme, fin_incluse=False):
    """
        Retourne la liste des acqid compris dans la période.
        Si duree_vecteur = acquisition, retourne None
        
        :param debut: la date de debut de période
        :type debut: datetime
        :param fin: la date de fin de période
        :type fin: datetime
        :param plateforme: nom (long) de la plateforme
        :type plateforme: str
        :param fin_incluse: True (defaut=False) si la date de fin est prise en compte
        :type fin_incluse: bool
        :return : liste des acqid
        :rtype : list
    """

    abrev = AIDA.liste_plt_to_abrev([plateforme])[0]
    AIDA.ini_plt_indexes()
    duree = duree_vecteur_from_plateforme(plateforme)
    if duree == "journee" :
        delta = relativedelta(days = 1)
        str_deb =dt.datetime.strftime(debut, "%Y%m%d")
        date_deb = dt.datetime.strptime(str_deb,"%Y%m%d")
        str_fin =dt.datetime.strftime(fin, "%Y%m%d")
        date_fin = dt.datetime.strptime(str_fin,"%Y%m%d")
        if not fin_incluse and date_deb != date_fin : # le test date_deb != date_fin permet de faire une selection de periode sur 1 acqid
            date_fin = date_fin + relativedelta(days = -1)
    elif duree.lower == "mois" :
        delta = relativedelta(months = 1)
        str_deb =dt.datetime.strftime(debut, "%Y%m")
        date_deb = dt.datetime.strptime(str_deb,"%Y%m")
        str_fin =dt.datetime.strftime(fin, "%Y%m")
        date_fin = dt.datetime.strptime(str_fin,"%Y%m")
        if not fin_incluse and date_deb != date_fin :
            date_fin = date_fin + relativedelta(months = -1)
    elif duree.lower == "annee" :
        delta = relativedelta(years = 1)
        str_deb =dt.datetime.strftime(debut, "%Y")
        date_deb = dt.datetime.strptime(str_deb,"%Y")
        str_fin =dt.datetime.strftime(fin, "%Y")
        date_fin = dt.datetime.strptime(str_fin,"%Y")
        if not fin_incluse and date_deb != date_fin :
            date_fin = date_fin + relativedelta(years = -1)
    else :
        return None
    
    acqids=[]   
    d = date_deb
    while d<= date_fin :
        acq = ACQ.AcqIdDoY(plateforme=abrev, date=d)
        acqids.append(acq._valeur)
        d = d + delta
    return acqids    

def duree_vecteur_from_plateforme(plateforme):
    """
        Retourne le champ duree_vecteur défini dans le fichier plate-formes correspondant à la plateforme
        
        :param plateforme: nom (long) de la plateforme
        :type plateforme: str
        :return : la valeur de duree_vecteur
        :rtype : str
    """    
    abrev = AIDA.liste_plt_to_abrev([plateforme])[0]
    AIDA.ini_plt_indexes()
    try :
        duree = AIDA.plt_by_abrev[abrev].duree_vecteur.lower()
    except :
        duree = "acquisition"
    
    return duree

def duree_vecteur_from_acqid(acqid):
    """
        Retourne le champ duree_vecteur défini dans le fichier plate-formes correspondant à la plateforme
        donnée par acqid.
        
        :param acqid: l'acqid
        :type acqid: str
        :return : la valeur de duree_vecteur
        :rtype : str
    """
    plateforme, _annee, _num = AIDA.ID_to_full(acqid)
    
    return duree_vecteur_from_plateforme(plateforme)

def timedata2timeaida(data_time, date0):
    """
       A partir d'un tableau de datetime, retourne un tableau de différences en secondes par rapport à date0 00H00M00S 
    """ 
    time_init = dt.datetime(date0.year, date0.month, date0.day)
    stim = [(x - time_init).total_seconds() for x in data_time]
    
    return stim    

def get_datation_convention(frequence, time_bnds) :
    """
        Retourne datation_convention entre 0(début) et 1(fin) d'un vecteur temps à partir
        de la fréquence et du time_bnds
    """
    if time_bnds == None or time_bnds.lower().startswith("vector") :
        return None
    if frequence == 0 :
        return None
    periode = 1./frequence
    ratio = float(time_bnds.split(',')[0])/periode
    return abs(ratio)
    