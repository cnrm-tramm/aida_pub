#!/usr/bin/env python3
# coding: utf-8

""" Ce module rassemble des outils (fonctions, classes) pour
    gérer les versions des vecteurs dans AIDA.
"""

import os
import sys
import datetime
aida_home = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(aida_home, 'lib', PYTHON_X_Y))
import AIDA
import DataBase


def VersionVect(file_path) :
    """ Retourne la version du vecteur passé en argument.
        file_path est supposé être un chemin de vecteur valide selon la norme AIDA.
        On isole la partie contenant frequence.version.vbn et on decode la version
        si elle est présente.
        
    :param file_path: le chemin du vecteur
    :type file_path: str
    :return: la version du vecteur
    :rtype: int
    """

    version = 0
    nom_vecteur = file_path.split('/')[-1]
    freq_version_vbn = nom_vecteur.split("_")[-1].split('.')
    if freq_version_vbn[-1] == "gz" :
        freq_version_vbn = freq_version_vbn[:-1]
    if len(freq_version_vbn) == 3 and freq_version_vbn[1].startswith('v') :
        version = int(freq_version_vbn[1][1:])

    return version

def VersionMaxVectFromFiles(file_path) :
    """ Retourne la version la plus élevée d'un vecteur (-1 si le vecteur n'existe pas)
        en parcourant l'arborescence.
        file_path est supposé être un chemin de vecteur valide (sans version) selon la norme AIDA.
    
    :param file_path: le chemin du vecteur
    :type file_path: str
    :return: la version max du vecteur
    :rtype: int
    """
    version = -1
    version_en_cours = 0
    

    # On liste les fichiers du répertoire (data_path) contenant le vecteur (file_path)
    nom_vecteur = file_path.split('/')[-1].split(".vbn")[0]
    data_path = file_path[0:file_path.rindex('/')]

    liste_fic = [ f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path,f)) and not f.startswith('.') and ( f.endswith(".vbn") or f.endswith(".vbn.gz"))]
    for f in liste_fic :
        # Si le fichier listé correspond au vecteur dont on cherche la version on détermine sa version
        if f.startswith(nom_vecteur) :
            version_en_cours = VersionVect(f)
            if version_en_cours > version :
                version = version_en_cours

    return version

def VersionMaxVectFromDataBase(acqid, parametre) :
    """ Retourne la version la plus élevée d'un vecteur (-1 si le vecteur n'existe pas)
        en lisant la base de données de gestion des vecteurs.
        
    :param acqid: l'identifiant d'acquisition
    :type acqid: str
    :param parametre: le nom du paramètre
    :type parametre: str
    :return: la version max du vecteur
    :rtype: int
    """
    
    version = DataBase.GetMaxVersionDataBase(acqid, parametre)
    
    return version

def VersionMaxVect(acqid, parametre) :
    """ Retourne la version la plus élevée d'un vecteur : 
        -1 si le vecteur n'existe pas
        -2 si incohérence entre le système de fichier et la base de données (ce qui ne devrait jamais se produire ...)
        
    :param acqid: l'identifiant d'acquisition
    :type acqid: str
    :param parametre: le nom du paramètre
    :type parametre: str
    :return: la version max du vecteur
    :rtype: int
    """

    file_path = AIDA.ID_to_datapath(acqid)+"/"+parametre+".vbn"
    version = VersionMaxVectFromFiles(file_path)
    if os.path.isfile(AIDA.ID_to_database(acqid)) :
        version_base = VersionMaxVectFromDataBase(acqid, parametre)
        if version != version_base :
            AIDA.report_error("+++ Versions incohérentes entre la base de données (v{}) et les fichiers (v{}) pour le vecteur {}".format(version_base, version, file_path))
            return -2

    return version

def VersionMaxPlus1(acqid, parametre) :
    """ Retourne le nom du vecteur (FilePath) à la version Max + 1, None si erreur.
        FilePath est supposé être un chemin de vecteur valide (sans version) selon la norme AIDA.
        
    :param acqid: l'identifiant d'acquisition
    :type acqid: str
    :param parametre: le nom du paramètre
    :type parametre: str
    :return: le nom du vecteur à la version max+1
    :rtype: str
    """
    
    version = VersionMaxVect(acqid, parametre)
    if version == -2 :
        return None
    file_path = AIDA.ID_to_datapath(acqid)+"/"+parametre+".vbn"
    base_file_path = file_path.split(".vbn")[0]

    if version == -1 :
        new_file_path = file_path
    else :
        new_file_path = base_file_path+".v{}".format(version+1)+".vbn"  

    return new_file_path

def GetVersionAt(acqid, parametre, date) :
    """ Retourne la version d'un vecteur à la date passée en argument.
        -1 si le vecteur n'existe pas
        
    :param acqid: l'identifiant d'acquisition
    :type acqid: str
    :param parametre: le nom du paramètre
    :type parametre: str
    :param date: la date pour laquelle on recherche la version du vecteur
    :type date: datetime
    :return: le numéro de version
    :rtype: int
    """

    if os.path.isfile(AIDA.ID_to_database(acqid)) :
        version = DataBase.GetVersionAtFromDataBase(acqid, parametre, date)
    else :
        file_path = AIDA.ID_to_datapath(acqid)+"/"+parametre+".vbn"
        version = GetVersionAtFromFiles(file_path, date)

    return version

def GetVersionAtFromFiles(file_path, date) :
    """ Retourne la version la version d'un vecteur à la date passée en argument
        en parcourant l'arborescence (-1 si le vecteur n'existe pas).
        file_path est supposé être un chemin de vecteur valide (sans version) selon la norme AIDA.
    
    :param file_path: le chemin du vecteur
    :type file_path: str
    :param date: la date pour laquelle on recherche la version du vecteur
    :type date: datetime
    :return: le numéro de version
    :rtype: int
    """
    version = -1
    date_version = None
    # On liste les fichiers du répertoire (data_path) contenant le vecteur (file_path)
    nom_vecteur = file_path.split('/')[-1].split(".vbn")[0]
    data_path = file_path[0:file_path.rindex('/')]
    acqid = AIDA.datapath_to_ID(data_path)

    liste_fic = [ f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path,f)) and not f.startswith('.') and ( f.endswith(".vbn") or f.endswith(".vbn.gz"))]
    for f in liste_fic :
        # Si le fichier listé correspond au vecteur dont on cherche la version on détermine sa version et sa date de création
        if f.startswith(nom_vecteur) :
            version_en_cours = VersionVect(f)
            vector = AIDA.Vector(acqid, nom_vecteur, attributes_only=True, version=version_en_cours)
            date_creation = vector.get_date_creation()
            if date_creation <= date :
                if date_version is None :
                    date_version = date_creation
                    version =  version_en_cours
                elif date_creation > date_version :
                    version =  version_en_cours
                    date_version = date_creation
            
    return version
