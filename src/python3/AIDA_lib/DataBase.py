#!/usr/bin/env python3
# coding: utf-8

""" Ce module rassemble des outils (fonctions, classes) pour
    gérer les bases de données associées aux vecteurs AIDA.
"""

import os
import sys
import sqlite3
import datetime

aida_home = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(aida_home, 'lib', PYTHON_X_Y))
import AIDA

def GetDataBaseFile (acqid) :
    """Détermine le fichier de base de données à partir de l'acqid.
    
    :param acqid: acqid
    :type acqid: str
    :return: le chemin absolu du fichier de base de donnée.
    :rtype: str
    """
    
    plt, annee, num = AIDA.ID_to_full(acqid)
    basename = os.path.join(AIDA.AIDA_getenv ('data'), plt, plt+".db")
    
    return basename

def ExistDataBase(acqid) :
    """Détermine l'existence de la base de données associée à l'acqid.
    
    :param acqid: acqid
    :type acqid: str
    :return: True si la base de donnée existe, False sinon.
    :rtype: booleen
    """
    
    basename = GetDataBaseFile (acqid)
    
    return os.path.isfile(basename)

def VecteurLocked(acqid, parametre):
    """Détermine si un vecteur est locked par un tag en base de données.
    
    :param acqid: acqid
    :type acqid: str
    :param parametre: le paramètre associé au vecteur
    :type acqid: str
    :return: 0=non locked, 1=locked, -1=erreur.
    :rtype: int
    """
    
    if not ExistDataBase(acqid) :
        return -1
    # connexion à la base
    basename = GetDataBaseFile (acqid)
    try :
        conn = sqlite3.connect(basename)
        cursor = conn.cursor()
    except :
        return -1
    
    # lecture des données
    locked = 0
    try :
        sql = "SELECT tag FROM vecteurs WHERE acqid='{}' AND parametre='{}' AND version=0".format(acqid, parametre)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if len(rows) != 0 :
            tag = rows[0][0]
            if tag.strip() != '' :
                locked = 1
        
    except Exception as e :
        print("+++ Erreur de lecture dans la base {}".format(basename))
        print("    Requete = {}".format(sql))
        print(e)
        locked = -1
    conn.close()
    
    return locked

def GetMaxVersionDataBase(acqid, parametre):
    """Retourne la version le numéro de version le plus élevé d'un vecteur.
    
    :param acqid: acqid
    :type acqid: str
    :param parametre: le paramètre associé au vecteur
    :type acqid: str
    :return: numéro de version max ou -1 en cas d'erreur.
    :rtype: int
    """      

    if not ExistDataBase(acqid) :
        return -1
    # connexion à la base
    basename = GetDataBaseFile (acqid)
    try :
        conn = sqlite3.connect(basename)
        cursor = conn.cursor()
    except :
        return -1
    
    # lecture des données
    try :
        sql = "SELECT MAX(version) FROM vecteurs WHERE acqid='{}' AND parametre='{}'".format(acqid, parametre)
        cursor.execute(sql)
        rows = cursor.fetchall()
        version = rows[0][0]
        if version is None :
            version = -1
    except Exception as e :
        print("+++ Erreur de lecture dans la base {}".format(basename))
        print("    Requete = {}".format(sql))
        print(e)
        version = -1
    conn.close()
    
    return version

def UpdateDataBase(acqid, parametre):
    """Met à jour la base de données de gestion des vecteurs :
        -si le paramètre n'existe pas : création de la version 0.
        -si le paramètre existe : création de la version n+1 et mise à jour de la date de la version 0.
    
    :param acqid: acqid
    :type acqid: str
    :param parametre: le paramètre associé au vecteur
    :type acqid: str
    :return: numéro de version créée ou -1 en cas d'erreur.
    :rtype: int
    """    
    
    if not ExistDataBase(acqid) :
        return -1
    # connexion à la base
    basename = GetDataBaseFile (acqid)
    try :
        conn = sqlite3.connect(basename)
        cursor = conn.cursor()
    except :
        return -1
    
    # date et heure courante au format YYYY-MM-DD HH:MI:SS
    str_date = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S")
    
    version_max = GetMaxVersionDataBase(acqid, parametre)
    if version_max != -1 : 
        # La version 0 devient la version n+1
        try :
            sql = "UPDATE vecteurs SET version={} WHERE acqid='{}' AND parametre='{}' AND version=0".format(version_max+1, acqid, parametre)
            cursor.execute(sql)
            conn.commit()
        except Exception as e :
            print("+++ Erreur d'update de la base {}".format(basename))
            print("    Requete = {}".format(sql))
            print(e)
            conn.close()
            return -1
        
    # On recrée une version 0 dans tous les cas
    try :
        sql = "INSERT INTO vecteurs VALUES('{}', '{}', 0, '{}', '')".format(acqid, parametre, str_date)
        cursor.execute(sql)
        conn.commit()
    except Exception as e :
        print("+++ Erreur d'écriture dans la base {}".format(basename))
        print("    Requete = {}".format(sql))
        print(e)
        conn.close()
        return -1
    
    conn.close()
    return version_max+1

def DeleteVecteur(acqid, parametre, version):
    """Supprime une entrée de la table vecteurs
    
    :param acqid: acqid
    :type acqid: str
    :param parametre: le paramètre associé au vecteur
    :type acqid: str
    :param version: numéro de version.
    :type version: int
    :return: nombre de ligne supprimée (0 ou 1) si ok ou -1 en cas d'erreur.
    :rtype: int
    """
        
    if not ExistDataBase(acqid) :
        return -1
    # connexion à la base
    basename = GetDataBaseFile (acqid)
    try :
        conn = sqlite3.connect(basename)
        cursor = conn.cursor()
    except :
        return -1
    
    try :
        sql = "DELETE FROM vecteurs WHERE acqid='{}' AND parametre='{}' AND version={}".format(acqid, parametre, version)
        cursor.execute(sql)
        conn.commit()
    except Exception as e :
        print("+++ Erreur de delete dans la base {}".format(basename))
        print("    Requete = {}".format(sql))
        print(e)
        conn.close()
        return -1
    
    conn.close()
    return cursor.rowcount

def AddVecteur(acqid, parametre, version, date):
    """Ajoute une entrée de la table vecteurs
    
    :param acqid: acqid
    :type acqid: str
    :param parametre: le paramètre associé au vecteur
    :type acqid: str
    :param version: numéro de version.
    :type version: int
    :param date: %Y-%m-%d %H:%M:%S
    :type date: str
    :return: nombre de ligne insérée (en principe 1), -1 en cas d'erreur.
    :rtype: int
    """
        
    if not ExistDataBase(acqid) :
        return -1
    # connexion à la base
    basename = GetDataBaseFile (acqid)
    try :
        conn = sqlite3.connect(basename)
        cursor = conn.cursor()
    except :
        return -1
    
    try :
        sql = "INSERT INTO vecteurs VALUES ('{}', '{}', {}, '{}', '')".format(acqid, parametre, version, date)
        cursor.execute(sql)
        conn.commit()
    except Exception as e :
        print("+++ Erreur d'insertion dans la base {}".format(basename))
        print("    Requete = {}".format(sql))
        print(e)
        conn.close()
        return -1
    
    conn.close()
    return cursor.rowcount

def GetVersionAtFromDataBase(acqid, parametre, date) :
    """ Retourne la version d'un vecteur à la date passée en argument.
        -1 en cas d'erreur
        
    :param acqid: l'identifiant d'acquisition
    :type acqid: str
    :param parametre: le nom du paramètre
    :type parametre: str
    :param date: la date pour laquelle on recherche la version du vecteur
    :type date: datetime
    :return: le numéro de version
    :rtype: int
    """

    if not ExistDataBase(acqid) :
        return -1
    
    # connexion à la base
    basename = GetDataBaseFile (acqid)
    try :
        conn = sqlite3.connect(basename)
        cursor = conn.cursor()
    except :
        return -1
    
    # lecture des données
    version = -1
    date_version = None
    try :
        sql = "SELECT version, date_creation FROM vecteurs WHERE acqid='{}' AND parametre='{}'".format(acqid, parametre)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for r in rows :
            version_en_cours = r[0]
            date_creation = datetime.datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
            if date_creation <= date :
                if date_version is None :
                    date_version = date_creation
                    version =  version_en_cours
                elif date_creation > date_version :
                    version =  version_en_cours
                    date_version = date_creation
        
    except Exception as e :
        print("+++ Erreur de lecture dans la base {}".format(basename))
        print("    Requete = {}".format(sql))
        print(e)
        version = -1
    conn.close()
    
    return version

def SetTag(acqid, parametre, version, tag):
    """Pose un tag
    
    :param acqid: acqid
    :type acqid: str
    :param parametre: le paramètre associé au vecteur
    :type parametre: str
    :param version: version
    :type version: str
    :param tag: tag commencant par # mais n'en contenant pas : si le premier caractère n'est pas # on le rajoute, s'il contient des # on remplace par des _
    :type tag: str
    :return: 0 ou-1=erreur.
    :rtype: int
    """
    if not ExistDataBase(acqid) :
        return -1
    
    # on vérifie le tag
    if tag[0] != '#' :
        tag = '#'+tag
    tag = '#'+tag[1:].replace('#', '_')

    # connexion à la base
    basename = GetDataBaseFile (acqid)
    try :
        conn = sqlite3.connect(basename)
        cursor = conn.cursor()
    except :
        return -1
    
    # lecture / réécriture du tag
    try :
        sql = "SELECT tag FROM vecteurs WHERE acqid='{}' AND parametre='{}'".format(acqid, parametre)
        cursor.execute(sql)
        rows = cursor.fetchall()
        tag_courant = rows[0][0]
        tags = tag_courant.split('#')
        if tag[1:] not in tags :
            tag_courant += tag
            try :
                sql = "UPDATE vecteurs SET tag='{}' WHERE acqid='{}' AND parametre='{}' AND version={}".format(tag_courant, acqid, parametre, version)
                cursor.execute(sql)
                conn.commit()
            except Exception as e :
                print("+++ Erreur d'update de la base {}".format(basename))
                print("    Requete = {}".format(sql))
                print(e)
                conn.close()
                return -1
    except Exception as e :
        print("+++ Erreur de lecture dans la base {}".format(basename))
        print("    Requete = {}".format(sql))
        print(e)
        version = -1
    conn.close()

def DeleteTag(acqid, parametre, version, tag='all'):
    """Supprime un tag
    
    :param acqid: acqid
    :type acqid: str
    :param parametre: le paramètre associé au vecteur
    :type parametre: str
    :param version: version
    :type version: str
    :param tag: tag commencant par # mais n'en contenant pas : si le premier caractère n'est pas # on le rajoute, s'il contient des # on remplace par des _ . Si tag est omis on supprime tous les tags.
    :type tag: str
    :return: 0 ou-1=erreur.
    :rtype: int
    """
    if not ExistDataBase(acqid) :
        return -1
    
    # on vérifie le tag
    if tag[0] != '#' :
        tag = '#'+tag
    tag = '#'+tag[1:].replace('#', '_')

    # connexion à la base
    basename = GetDataBaseFile (acqid)
    try :
        conn = sqlite3.connect(basename)
        cursor = conn.cursor()
    except :
        return -1
    
    # lecture / réécriture du tag
    try :
        sql = "SELECT tag FROM vecteurs WHERE acqid='{}' AND parametre='{}'".format(acqid, parametre)
        cursor.execute(sql)
        rows = cursor.fetchall()
        tag_courant = rows[0][0]
        tags = tag_courant.split('#')
        new_tag = None
        if tag[1:].lower() == 'all' :
                new_tag = ''
        else :
            if tag[1:] in tags :
                tags.remove(tag[1:])
                new_tag = '#'.join(tags)
        if new_tag is not None :
            try :
                sql = "UPDATE vecteurs SET tag='{}' WHERE acqid='{}' AND parametre='{}' AND version={}".format(new_tag, acqid, parametre, version)
                cursor.execute(sql)
                conn.commit()
            except Exception as e :
                print("+++ Erreur d'update de la base {}".format(basename))
                print("    Requete = {}".format(sql))
                print(e)
                conn.close()
                return(-1)
    except Exception as e :
        print("+++ Erreur de lecture dans la base {}".format(basename))
        print("    Requete = {}".format(sql))
        print(e)
        conn.close()
        return(-1)

    conn.close()
    return(0)
