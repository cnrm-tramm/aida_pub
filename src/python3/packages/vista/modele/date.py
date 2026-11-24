#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import locale

"""
    Module de gestion des dates
    vistadate est de forme AAAAMMJJHHMMSS
"""
mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

def now() :
    """
        Retourne la vistadate du jour
    """
    today = datetime.datetime.now()
    return toVistaDate(today)


def toVistaDate(date, hhmmss=True):
    """
        Retourne la vistadate correspondant à la date
    """
    if hhmmss :
        return "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(date.year, date.month, date.day, date.hour, date.minute, date.second)
    else :
        return "{:04d}{:02d}{:02d}000000".format(date.year, date.month, date.day)

def calendarToVistadate(caldate) :
    """
        Convertit une date au format calendar tuple (AAAA, MM-1, JJ) en vistadate
    """
    chn = "{:04d}{:02d}{:02d}000000".format(caldate[0], caldate[1]+1, caldate[2])
    return chn


def toString(vistadate, fmt):
    chn = vistadate
    fmts = {
            "JJ/MM/AAAA" : toFmt1,            
            "jj mm AAAA" : toFmt2,
            "JJ mm AAAA" : toFmt3,
            "AAAA" : toFmt4,
            "MM" : toFmt5,
            "JJ" : toFmt6,
            "JJ-MM-AAAA HH:MI" : toFmt7,
            "mm AAAA" : toFmt11,
            "mm" : toFmt12
            }
    if not fmt in list(fmts.keys()) :
        print(("Erreur : le format de date {} n'est pas géré par vista.".format(fmt)))
    else :
        chn = fmts[fmt](vistadate)
    return chn

    
def toFmt1(vistadate): # JJ/MM/AAAA
    dte = toDate(vistadate)
    return dte.strftime("%d/%m/%Y")


def toFmt2(vistadate): # jj mm AAAA (lundi, 03 février 2014)
    dte = toDate(vistadate)
    return dte.strftime("%A, %d %B %Y")

    
def toFmt3(vistadate): # JJ mm AAAA (03 février 2014)
    dte = toDate(vistadate)
    return dte.strftime("%d %B %Y")

def toFmt4(vistadate): # AAAA (2014)
    dte = toDate(vistadate)
    return dte.strftime("%Y")

def toFmt5(vistadate): # MM (02)
    dte = toDate(vistadate)
    return dte.strftime("%m")

def toFmt6(vistadate): # JJ (03)
    dte = toDate(vistadate)
    return dte.strftime("%d")

def toFmt7(vistadate): # JJ-MM-AAAA HH:MI (03-04-1968 10:30)
    dte = toDate(vistadate)
    return dte.strftime("%d-%m-%Y %H:%M")

def toFmt11(vistadate): # mm AAAA (février 2014)
    dte = toDate(vistadate)
    return dte.strftime("%B %Y")


def toFmt12(vistadate): # mm (février)
    dte = toDate(vistadate)
    return dte.strftime("%B")


def duree(date1, date2):
    """
        Nombre de jours entre 2 vistadates
    """
    AAAA = int(date1[0:4])
    MM = int(date1[4:6])
    JJ = int(date1[6:8])
    d1 = datetime.date(AAAA,MM,JJ)
    AAAA = int(date2[0:4])
    MM = int(date2[4:6])
    JJ = int(date2[6:8])
    d2 = datetime.date(AAAA,MM,JJ)
    
    diff = d2 - d1
    if diff.days >= 0 :
        return diff.days + 1
    else : 
        return diff.days - 1

def ecart(date1, date2):
    """
        Ecart de jours entre 2 vistadates
    """
    AAAA = int(date1[0:4])
    MM = int(date1[4:6])
    JJ = int(date1[6:8])
    d1 = datetime.date(AAAA,MM,JJ)
    AAAA = int(date2[0:4])
    MM = int(date2[4:6])
    JJ = int(date2[6:8])
    d2 = datetime.date(AAAA,MM,JJ)
    
    diff = d2 - d1
    
    return diff.days
    
def toDate(date1):
    """
        Retourne la date correspondant au vistadate
    """
    AAAA = int(date1[0:4])
    MM = int(date1[4:6])
    JJ = int(date1[6:8])
    HH = int(date1[8:10])
    MI = int(date1[10:12])
    SS = int(date1[12:14])
    
    return datetime.datetime(AAAA,MM,JJ,HH,MI,SS)

      
def add(date1, nbDays):
    """
        Ajoute un nombre de jour (qui peut être négatif) et retourne une vistadate
    """  
    date = toDate(date1) + datetime.timedelta(days=nbDays)
    return toVistaDate(date)

    
def toAcqId(date1):
    """
        Retourne la partie date de l'acqid
    """
    date = toDate(date1)
    return "{:02d}".format(date.year % 100) + '0' + date.strftime('%j')


def debutFinMois(dateMois):
    """ 
        Retourne les vistadates de debut et fin de mois
    """
    dateDebut = toDate(dateMois)
    newDateDebut = dateDebut.replace(day=1)
    debut = toVistaDate(newDateDebut, False)
    
    dateMoisSuivant = newDateDebut + datetime.timedelta(days=32)
    newDateMoisSuivant = dateMoisSuivant.replace(day=1)
    dateFin = newDateMoisSuivant - datetime.timedelta(days=1)
    fin = toVistaDate(dateFin, False)
    
    return (debut, fin)

 
def jourNuit(ordinal):
    """
        Retourne faux si la date (ordinal datetime) est en journée, vrai pour la nuit
    """
    nbsec =  (ordinal - int(ordinal))*86400
    nbsec6H = 6*3600
    nbsec18H = 18*3600
    if nbsec >= nbsec6H and nbsec <= nbsec18H :
        return False
    else :
        return True
    
def dateFromOrdinal(ordinal) :
    """
        Retourne une chaine pour la jauge à partie d'un ordinal vista
    """
    date = datetime.datetime.fromordinal(int(ordinal))
    nbsec = round((ordinal-int(ordinal)) * 86400, 3)
    date2 = date + datetime.timedelta(seconds=nbsec)
    return "{}.{:03d}".format(date2.strftime('%d-%m-%Y %H:%M:%S'), date2.microsecond//1000)

def datetimeFromOrdinal(ordinal) :
    """
        Retourne un datetime à partie d'un ordinal vista
    """
    date = datetime.datetime.fromordinal(int(ordinal))
    nbsec = round((ordinal-int(ordinal)) * 86400)+1
    date2 = date + datetime.timedelta(seconds=nbsec)
    return date2

def getListeAns(debut, fin):
    """
        Retourne la liste de dates des premiers janvier de chaque année de la période 
    """
    listeAns = []
    finDate = toDate(fin)
    currentDate = toDate(debut)
    while currentDate < finDate :
        if currentDate.month == 1 and currentDate.day == 1 :
            listeAns.append(currentDate)
        currentDate += datetime.timedelta(days=1)
    return listeAns
    
def getListeMois(debut, fin):
    """
        Retourne la liste de dates des premiers de chaque mois de la période 
    """
    listeMois = []
    finDate = toDate(fin)
    currentDate = toDate(debut)
    while currentDate < finDate :
        if currentDate.day == 1 :
            listeMois.append(currentDate)
        currentDate += datetime.timedelta(days=1)
    return listeMois

def getMois(num) :
    """
        Retourne le mois correspondant au numéro 
    """
    return mois[num-1]

if __name__ == "__main__":
    #print(toString('20140101120000', 'JJ/MM/AAAA'))
    #print(calendarToVistadate((2014, 7, 2)))
    #print(now())
    loc = locale.getlocale() 
    locale.setlocale(locale.LC_ALL, 'fr_FR')
    print(toFmt1("20140609000000"))
