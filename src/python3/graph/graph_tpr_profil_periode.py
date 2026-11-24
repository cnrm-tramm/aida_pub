#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# graph_tsol_an.py
# vim: set fileencoding=utf-8: #
#=====================================================
"""
usage :   python graph_tpr_profil.py $acqid 
                ou
          python graph_tpr_profil.py plateforme date_deb date_fin avec date au format YYYYMMDD 
                ou 
          python graph_tpr_profil.py -i fic_ini


exemple : graph_tpr_profil.py Tf120075

exemple : graph_tpr_profil.py Tf130365 => année 2013

exemple : graph_tpr_profil.py Tf 20131231 20141231

exemple : graph_tpr_profil.py -i INI/Y5_tpr_profil.ini Tf 20131231 20141231

exemple : graph_tpr_profil.py -i INI/Y5_tpr_profil.ini Tf130365

#plateformes acceptées    : Tf, Y5

"""
stations = {"Tf":"toulouse-flux", "Y5":"cerdanya-05", }

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import getopt
import time
import datetime as dt
import configparser
import argparse

AH = os.getenv('AIDA_HOME')
if not AH:
    print("FATAL : AIDA_HOME non defini")
    #print >> sys.stderr, "FATAL : AIDA_HOME non defini"
    sys.exit(1)
PYTHON_X_Y = "python{}.{}".format(sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
import AIDA
from AcqIdDoY import *


__version__ = "$Revision: 1.1 $"


#-------------------------------------------------------------
# fonctions
#-------------------------------------------------------------
def usage ():
    """Ecrit l'usage et sort
    """
    print( __doc__)
    sys.exit(0)

def stop_error(msg):
    """Ecrit l'erreur et sort
    """
    print(msg)
    sys.exit(1)

def decode_acqid(acqid):
    """vérifie la  validité de l'acqid,
    détermine abreviation, an, jour à partir de l'acqid
    vérifie validité des path
    """
    try :
        AIDA.check_acq_id(acqid)
    except  Exception as e:
        print( "Attention : acqid incorrect: {}".format(e))
        stop_error(usage())

    if len(acqid) == 7:
        print("Erreur de saisie dans l'acqid.")
        stop_error(usage())
    abrev = acqid[0:2]
    Y2 = acqid[2:4]
    Y4 = AIDA.Y2_to_Y4(Y2)
    jour = acqid[4:8]
    if abrev in stations:
        #vérifie que "an" est un répertoire
        path = os.path.join(AIDA.AIDA_getenv('data'), stations[abrev],
                            Y4, jour)
        if os.path.isdir(path):
            pass
        else :
            # on continue le calcul pour les autres vecteurs
            #stop_error("Path : %s non reconnu." % path)
            print("Path : {} inexistant .".format(path))
    else:
        print("Plateforme {} non valide.".format(abrev))
        usage()
    return 0

def normalise(unit):
    """ 
    normalisation des unités conforme a netcdf
    transformation de 0.001 meter en millimeter (udunits <= 2.7)
    correction de bug dans l'ecriture des unités ou traduction en anglais
    """
    if unit.lower()=="celcius":
        print("WARN : normalisation de {} en celsius".format(unit))
        unit="celsius"
    if unit.lower()=="pourcent":
        print("WARN : normalisation de {} en percent".format(unit))
        unit="percent"
    if unit.lower()=="0.001 meter":
        print("WARN : normalisation de {} en millimeter".format(unit))
        unit="millimeter"
    if unit.lower()=="degre":
        print("WARN : normalisation de {} en degree".format(unit))
        unit="degree"
    return(unit)



def moyenne(npliste):
    """calcule la moyenne des éléments d'un numpyarray contenant des NaN
    """

    moy=np.nanmean(npliste)
    return moy


def periode(acqidinf,acqidsup):
    """définit la période d'affichage pour l'affichage du graphe
    """
    Y2inf = acqidinf[2:4]
    Y2sup = acqidsup[2:4]
    jourinf = acqidinf[4:8]
    joursup = acqidsup[4:8]

    borne_sup = str(Y2sup)+" "+str(joursup[1:])
    t_sup = time.strptime(borne_sup, "%y %j")
    borne_inf = str(Y2inf)+" "+str(jourinf[1:])
    t_inf = time.strptime(borne_inf, "%y %j")
    bs = str(t_sup.tm_mday)+"/"+str(t_sup.tm_mon)+"/"+str(t_sup.tm_year)
    bi = str(t_inf.tm_mday)+"/"+str(t_inf.tm_mon)+"/"+str(t_inf.tm_year)
    return bi, bs

def graph(fig, ax,xmin, xmax, l_moy,l_moy_totale,l_manq,l_prof,l_rang,l_nom, unite,nom_graph, legend, xlabel=None,ylabel=None,tittle=None, color=1):
    """Affiche graphiquement profils de température sur une période  """

    global moy_base, nom_base
    fig.subplots_adjust(bottom = 0.15)
    coul_point=['red','blue','green', 'orange']
    if color == 1 :
        moy_base =  l_moy_totale
        nom_base = legend
        ecart_moy = 0
        ecart_nom = ""
    else :
        ecart_moy = moy_base - l_moy_totale
        ecart_nom = nom_base + " - "+ legend

    #configuration du graphe
    ax.grid(True)
    # on redimensionne les tableaux pour supprimer les moyennes égales à Nan
    select=np.isnan(l_moy) # moyennes non nulles
#    print("DEBUG: select={}".format(select));
#    print("DEBUG: ~select={}".format(~select));
    l_moy=np.array(l_moy)
    l_manq=np.array(l_manq)
    l_moy=l_moy[~select] # commande magique en python2 parce que le passage en UTF-8 le rend caduc
    l_manq=l_manq[~select]

    l_nom=np.array(l_nom)
    l_nom=l_nom[~select]
    l_rang=np.array(l_rang)
    l_rang=l_rang[~select]
    l_prof=(np.array(l_prof))
    l_prof=l_prof[~select]
    #unite=unicode(unite,'utf-8')

#    print("DEBUG graph: lmoy={}".format(l_moy))
#    print("DEBUG graph: lmoy_totale={}".format(l_moy_totale))
#    print("DEBUG graph: l_manq={}".format(l_manq))
#    print("DEBUG graph: l_prof={}".format(l_prof))
#    print("DEBUG graph: " + str(color))
#    print("DEBUG graph: l_rang={}".format(l_rang))
#    print("DEBUG graph: l_nom={}".format(l_nom))
#    print("DEBUG graph: unite={}".format(unite))
#    print("DEBUG graph: nom_graph={}".format(nom_graph))
#    print("DEBUG graph: xlabel={}".format(xlabel))
#    print("DEBUG graph: ylabel={}".format(ylabel))
#    print("DEBUG graph: tittle={}".format(tittle))

    ax.plot(l_moy,l_prof,'o', color=coul_point[color-1], label=legend)
    #pour determiner une couleur de texte différente pour chaque points a une même profondeur
    #(les points eux sont toujours de la même couleur: une seule courbe)
    tab_coul=['black','red','blue','green']

    xmin = min(min(l_moy), xmin) 
    xmax = max(max(l_moy), xmax)
    ymin = l_prof[len(l_prof)-1]
    ymax = l_prof[0]
    dx = (xmax - xmin) * 0.1
    dy = (ymax - ymin) * 0.1
    xmin = xmin  -dx
    xmax = xmax +dx
    ymin = ymin -dy
    ymax = ymax +dy
    #Modification des graduations
    #plt.yticks([-220,0,+10])

    ax.axis([xmin,xmax,ymin,ymax])
    if xlabel != None:
        #uxlabel=str(xlabel,"utf-8")
        #plt.xlabel(uxlabel)
        ax.set_xlabel(xlabel)
    if ylabel != None:
        #uylabel=str(ylabel,"utf-8")
        #plt.ylabel(uylabel)
        ax.set_ylabel(ylabel)
    if tittle != None:
        #utittle=str(tittle,"utf-8")
        #plt.title(str(utittle))
        ax.set_title(str(tittle))
    ax.axvline(x=l_moy_totale,color=coul_point[color-1],linestyle='--')
    if color > 1 :
        fig.text(0.1, 0.03*color, ecart_nom + "=" + str(ecart_moy))

    for i in range(len(l_moy)):
#        text='{}: {:.2f} {} ({:.2f}%)'.format(l_nom[i],l_moy[i],unite,l_manq[i])
        text='{:.2f} ({:.2f}%)'.format(l_moy[i],l_manq[i])
        ax.annotate(text, xy=(l_moy[i],l_prof[i]+0.1*dy*l_rang[i]),xycoords='data',xytext=(-40,5),
                        textcoords='offset points',size='x-small',color=tab_coul[l_rang[i]])
 
    ax.legend()
    return xmin, xmax

def moyenne_vecteur_tpr_hh(nom_vecteur,Acqid_inf,Acqid_sup,nb_val_jr,hh_deb=None,hh_fin=None):
    """" calcule moyenne, pourcentage de valeurs manquantes, unité de chaque vecteur de la liste
    entre acqidinf et acqidsup
    retourne le resultat sous forme de dictionaire vecteur
    {'nom_vecteur'=..., 'moyenne'=...,  'pourcent_val_manq'=... (,'prof'=...)} 
    """
    dict_moy_vecteur={}
    dict_moy_vecteur["nom_vecteur"]=nom_vecteur
    # on cree un tableau de listes de données a retourner
    data_infetsup = np.array([]) # cumul des vecteurs existant entre acqid_inf et acqid_sup

    k_infetsup = 0 # nb de jours manquants
    #nb_nan_infetsup est le nombre de données manquantes de l'année en cours ; nan = not a number
    nb_jour=0 # nb de jours entre acqid_inf et acqid_sup pour le commentaire
    unite_infetsup = []
    vectvide=np.full(nb_val_jr,np.NaN) # journée vide
    
    #récupération de la liste acqid heure a traiter
    if hh_deb != None:
        print (hh_deb[0:2], hh_deb[3:4])
        nbhh_deb=int(hh_deb[0:2])
        nbmn_deb=int(hh_deb[3:4])
    else:
        nbhh_deb=0
        nb_mndeb=0
    print ("nb_hh_deb={}".format(nbhh_deb))
    print ("nb_mn_deb={}".format(nbmn_deb))
    if  hh_fin != None:
        print (hh_fin[0:2], hh_fin[3:4])
        nbhh_fin=int(hh_fin[0:2])
        nbmn_fin=int(hh_fin[3:4])
    else:
        nbhh_fin=24
        nbmn_fin=0
    print ("nb_hh={}".format(nbhh_fin))
    print ("nb_mn={}".format(nbmn_fin))

    liste_acqid=[]
    Acqid=Acqid_inf
    if Acqid_inf==Acqid_sup:
        liste_acqid.append([Acqid_inf,nbhh_deb,nbhh_fin,nbmn_deb,nbmn_fin])
        nb_jour=nb_jour+1
    else:
        liste_acqid.append([Acqid_inf,nbhh_deb,24,nbmn_deb,0])
        while Acqid < Acqid_sup:
            liste_acqid.append([Acqid,0,24,0,0])
            Acqid=Acqid+1
            nb_jour=nb_jour+1
        liste_acqid.append([Acqid_sup,0,nbhh_fin,0,nbmn_fin])

#    print ("DEBUG: liste_acqid={}".format(liste_acqid))
    i=0
    while Acqid_sup>=Acqid:
        try:
            Acqid=liste_acqid[i][0]
            hh_deb=liste_acqid[i][1]
            hh_fin=liste_acqid[i][2]
            mn_deb=liste_acqid[i][3]
            mn_fin=liste_acqid[i][4]
            print ( hh_deb,mn_deb,hh_fin,mn_fin)
            print(  (hh_deb*60+mn_deb)*60 , (hh_fin*60+mn_fin)*60 ) 

            if AIDA.vector_exists(str(Acqid), nom_vecteur):
                vect = AIDA.Vector(str(Acqid), nom_vecteur)
#                print( "DEBUG: debut traitement vecteur {} {} heure debut {}:{} heure fin {}:{}".format(nom_vecteur,str(Acqid),hh_deb, mn_deb,hh_fin,mn_fin))
                if 'ref_time' not in vect.attributes:
                    print("ref_time manquant dans %s de %s" % (nom, str(Acqid)))
                ref_time = vect.attributes['ref_time']
                time = AIDA.Vector(str(Acqid), ref_time)
                nb_data=0
                for nbsec in range(len(time.data)):
                    if time.data[nbsec] > (hh_deb*60+mn_deb)*60 and time.data[nbsec] <= (hh_fin*60+nbmn_fin)*60 :
                        data_infetsup=np.append(data_infetsup,vect.data[nbsec])
                        nb_data=nb_data+1
                print ("nbsec={} nb_data={} data_infetsup={}".format(nbsec+1,nb_data,data_infetsup))
                unite = normalise(vect.attributes['unit'])
                unite_infetsup.append(unite)
            else:
                print( "WARN: Vecteur {}  {} inexistant ".format(nom_vecteur,str(Acqid)))
                k_infetsup = k_infetsup + 1
                data_infetsup=np.append(data_infetsup,vectvide)
                unite_infetsup.append('')
        except  Exception as e:
            print( "ERR: donnees_inf_et_sup vecteur {} {}: {}.  On continue.".format(nom_vecteur,str(Acqid_inf),e))
            data_infetsup=np.append(data_infetsup,vectvide)
            unite_infetsup.append('')
            k_infetsup = k_infetsup + 1
        i=i+1
        Acqid=Acqid+1

    # nb de valeurs manquantes dans le vecteur final
    nb_nan_infetsup=np.sum( np.isnan(data_infetsup))

    #pourcentage de valeur manquantes
    pourcent = (nb_nan_infetsup*100.)/ (len(data_infetsup))

#    print( "DEBUG: valeurs manquantes sur  {} jours, {} données utilisées pour le calcul : {} donnees manquantes dont {} jours manquants ({}% de valeur manquantes))".format(nb_jour,len(data_infetsup), nb_nan_infetsup,  k_infetsup,pourcent))

    #Mise a jour du dictionnaire 
    dict_moy_vecteur["pourcent"]= pourcent

    dict_moy_vecteur["moyenne"]= moyenne(data_infetsup)
    if dict_moy_vecteur["moyenne"] is np.NaN:
        print( "WARN: pas de données Tsol sur l'année choisie")
        dict_moy_vecteur["pourcent"]= '100'
        dict_moy_vecteur["unite"]=''
    elif  len(unite_infetsup) < 1:
        print( "ERR: Pas d'unité trouvée. On invalide la moyenne")
        #print( "WARN: Pas d'unité trouvée. ")
        dict_moy_vecteur["pourcent"]= '100'
        dict_moy_vecteur["unite"]=''
        dict_moy_vecteur["moyenne"]= np.NaN
    else:
        # on vérifie les unités
        # la ligne ci-dessous sert à supprimer tous les doublons de la liste ;
        # il ne devrait rester après cette opération, qu'un seul élément
        unite_infetsup = list(set(unite_infetsup))
        #print("DEBUG: Liste des unites trouvées apres set:{} ".format( unite_infetsup))
        if (len(unite_infetsup) == 1) :
            if (len(unite_infetsup) == 1) and   ((unite_infetsup[0] == 'Celsius' or unite_infetsup[0] == 'celsius')):
                unite_infetsup[0] = '°C'
            dict_moy_vecteur["unite"]=unite_infetsup[0].encode('utf-8')
        else:
#            print("WARN: Plusieurs unités détectées sur un an pour {} : {}.".format(nom_vecteur,unite_infetsup))
            dict_moy_vecteur["unite"]=''
     
#    print( "DEBUG: Moyenne: {:.2f} unite:{}".format(dict_moy_vecteur["moyenne"],dict_moy_vecteur["unite"]) )

    return dict_moy_vecteur

def moyenne_vecteur_tpr(nom_vecteur,Acqid_inf,Acqid_sup,nb_val_jr):
    """" calcule moyenne, pourcentage de valeurs manquantes, unité de chaque vecteur de la liste
    entre acqidinf et acqidsup
    retourne le resultat sous forme de dictionaire vecteur
    {'nom_vecteur'=..., 'moyenne'=...,  'pourcent_val_manq'=... (,'prof'=...)} 
    """
    dict_moy_vecteur={}
    dict_moy_vecteur["nom_vecteur"]=nom_vecteur
    # on cree un tableau de listes de données a retourner
    data_infetsup = np.array([]) # cumul des vecteurs existant entre acqid_inf et acqid_sup

    k_infetsup = 0 # nb de jours manquants
    #nb_nan_infetsup est le nombre de données manquantes de l'année en cours ; nan = not a number
    nb_jour=0 # nb de jours entre acqid_inf et acqid_sup pour le commentaire
    unite_infetsup = []
    vectvide=np.full(nb_val_jr,np.NaN) # journée vide

    # comparaison et addition sur les objets 
    while Acqid_sup>=Acqid_inf:
        try:
            if AIDA.vector_exists(str(Acqid_inf), nom_vecteur):
                vect = AIDA.Vector(str(Acqid_inf), nom_vecteur)
#                print(( "DEBUG: traitement vecteur {} {} ".format(nom_vecteur,Acqid_inf)))
                data_infetsup=np.append(data_infetsup,vect.data)
                unite = normalise(vect.attributes['unit'])
                unite_infetsup.append(unite)
            else:
                print( "WARN: Vecteur {}  {} inexistant ".format(nom_vecteur,Acqid_inf))
                k_infetsup = k_infetsup + 1
                data_infetsup=np.append(data_infetsup,vectvide)
        except  Exception as e:
            print( "ERR: donnees_inf_et_sup vecteur {} {}: {}.  On continue.".format(nom_vecteur,Acqid_inf,e))
            data_infetsup=np.append(data_infetsup,vectvide)
            k_infetsup = k_infetsup + 1
        Acqid_inf=Acqid_inf+1
        nb_jour=nb_jour+1
    
    # nb de valeurs manquantes dans le vecteur final
    nb_nan_infetsup=np.sum( np.isnan(data_infetsup))

    #pourcentage de valeur manquantes
    pourcent = (nb_nan_infetsup*100.)/ (len(data_infetsup))

#    print( "valeurs manquantes sur  {} jours, {} données utilisées pour le calcul : {} donnees manquantes dont {} jours manquants ({}% de valeur manquantes))".format(nb_jour,len(data_infetsup), nb_nan_infetsup,  k_infetsup,pourcent))

    #Mise a jour du dictionnaire 
    dict_moy_vecteur["pourcent"]= pourcent

    dict_moy_vecteur["moyenne"]= moyenne(data_infetsup)
    if dict_moy_vecteur["moyenne"] is np.NaN:
        print( "WARN: pas de données Tsol sur l'année choisie")
        dict_moy_vecteur["pourcent"]= 100.
        dict_moy_vecteur["unite"]=''
    elif  len(unite_infetsup) < 1:
        print( "ERR: Pas d'unité trouvée. On invalide la moyenne")
        #print( "WARN: Pas d'unité trouvée. ")
        dict_moy_vecteur["pourcent"]= 100.
        dict_moy_vecteur["unite"]=''
        dict_moy_vecteur["moyenne"]= np.NaN
    else:
        # on vérifie les unités
        # la ligne ci-dessous sert à supprimer tous les doublons de la liste ;
        # il ne devrait rester après cette opération, qu'un seul élément
        unite_infetsup = list(set(unite_infetsup))
#        print("DEBUG: Liste des unites trouvées apres set:{} ".format( unite_infetsup))
        if (len(unite_infetsup) == 1) :
            if (len(unite_infetsup) == 1) and   (unite_infetsup[0] == 'Celsius' or unite_infetsup[0] == 'celsius' or unite_infetsup[0] == '°C'):
                unite_infetsup[0] = '°C'
                unite_infetsup[0] = 'celsius'
                dict_moy_vecteur["unite"]=unite_infetsup[0]
            else:
                dict_moy_vecteur["unite"]=unite_infetsup[0]
        else:
            print("WARN: Plusieurs unités détectées sur un an pour {} : {}.".format(nom_vecteur,unite_infetsup))
            dict_moy_vecteur["unite"]=''
     
#    print( "DEBUG: Moyenne: {:.2f}".format(dict_moy_vecteur["moyenne"]) )

    return dict_moy_vecteur

def calcule_moyenne_profil(vecteur_liste,tsol,Acqid_inf,Acqid_sup,nb_val_jr,hh_deb,hh_fin):
    """ Fonction générale de calcul des moyennes des profils de température entre acqid_inf et acqid_sup"""

    l_moy_tsol = []
    l_donnees_manquantes = []
    l_prof = []
    for nom_vecteur in vecteur_liste:
        index_vect=vecteur_liste.index(nom_vecteur)
        if hh_deb is None or hh_fin is None:
            dict_moy_tsol=  moyenne_vecteur_tpr(nom_vecteur,Acqid_inf,Acqid_sup,nb_val_jr)
        else:
            dict_moy_tsol=  moyenne_vecteur_tpr_hh(nom_vecteur,Acqid_inf,Acqid_sup,nb_val_jr,hh_deb,hh_fin)
        print(dict_moy_tsol)
        dict_moy_tsol["prof"]=tsol[index_vect]
        if dict_moy_tsol["moyenne"] is np.NaN:
                print("calcule de la moyenne de {} impossible!".format(nom_vecteur))
        #on recupére la profondeur correspondant au vecteur lu
        l_prof.append(dict_moy_tsol["prof"])
        l_moy_tsol.append(dict_moy_tsol["moyenne"])
        l_donnees_manquantes.append(dict_moy_tsol["pourcent"])
        unite=dict_moy_tsol["unite"]

    print("liste des moyennes par hauteur:{}".format(l_moy_tsol))
    print("liste des profondeurs:{} ".format(l_prof))
    print("liste des pourcentages manquants:{}".format(l_donnees_manquantes))
    # encodage spécifié pour unité = °C sinon le programme plante au cron (la sortie stdout s'attend à un string ascii)
    #print("unite:",unite.encode('utf-8'))
    print("unite:{} ".format(unite))
    #print("DEBUG:unite:{} ".format(unite.encode('utf-8')))

    moy_tsol_glob = moyenne(l_moy_tsol)
    print("moyenne sur le profil = {}".format( moy_tsol_glob))

    return l_moy_tsol,l_prof,l_donnees_manquantes,moy_tsol_glob,unite


def main (argv=None):

    if argv is None :
        argv = sys.argv[1:]
    acqid_sup = ""
    acqid_inf = ""

    # liste des arguments

    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--datedeb", required=True,help="date de début sous forme AAAAMMJJ") 
    parser.add_argument("-f","--datefin", required=True,help="date de fin sous forme AAAAMMJJ") 
    parser.add_argument('-i','--config', required = True, help='chemin complet du fichier de config')
    parser.add_argument("-m","--hhdeb", help="heure de début sous forme AAAAMMJJ") 
    parser.add_argument("-n","--hhfin", help="heure de fin sous forme AAAAMMJJ") 
    args=parser.parse_args()

    #Lecture et décodage des arguments 

    arg_config = args.config
    date_deb = args.datedeb
    date_fin = args.datefin
    try:
        hh_deb = args.hhdeb
        hh_fin = args.hhfin
    except  ValueError :
        hh_deb=None
        hh_fin=None
    except Exception as e:
        print("Erreur lecture arguments:{}".format(e))
        sys.exit()
        
    # Cas ou plusieurs fichiers de config.
    lst_config=arg_config.split(',')

    # Création de la figure
    fig = plt.figure(figsize=(8,10), dpi=100)
    axg = fig.add_subplot(111)
    print(fig)
    print(axg)
    i=0
    xmin=50
    xmax=-50
    moy_base=-99
    nom_base=""

    for fic_config in lst_config :

        #Lecture du fichier de config 
        # on desactive le module interpolation qui assimile "% (" a "$(")
        print("INFO : traitement du fichier de config : " + fic_config)
        config = configparser.ConfigParser(interpolation=None)
        try:
            config.read(fic_config)
            abrev= config.get('cumul', 'abrev')
            lvect= config.get('cumul', 'vecteur_liste')
            vecteur_liste1=[]
            for vec in lvect.split(';'):
                vecteur_liste1.append(vec.strip())
            #print(vecteur_liste1)
            tsollu_haut= config.get('cumul', 'tsol')
            #print(tsollu)
            tsol_haut=[]
            for t in tsollu_haut.split(';'):
                tsol_haut.append(float(t.strip()))
            #print(tsol)
            tsol_ranglu= config.get('cumul', 'tsol_rang')
            tsol_rang=[]
            for trang in tsol_ranglu.split(';'):
                tsol_rang.append(int(trang.strip()))
            tsol_nomlu= config.get('cumul', 'tsol_nom')
            tsol_nom=[]
            for tnom in tsol_nomlu.split(';'):
                tnom=tnom.strip()
                tnom=tnom.strip('\'')
                tsol_nom.append(tnom)
                #print("tnom {}: tsol_nom:{}".format(tnom,tsol_nom))
            nb_val_jr= int(config.get('cumul', 'nb_val_jr'))

            #print("DEBUG:read_config:liste vecteurs:{} taille:{}".format(vecteur_liste1,len(vecteur_liste1)))
            #print("DEBUG:read_config:tsol_haut:{} taille:{}".format(tsol_haut,len(tsol_haut)))
            #print("DEBUG:read_config:tsol_rang:{} taille:{}".format(tsol_rang,len(tsol_rang)))
            #print("DEBUG:read_config:tsol_nom:{} taille:{}".format(tsol_nom,len(tsol_nom)))
            #print("DEBUG:read_config:abrev={} nb_val_jr:{}".format(abrev,nb_val_jr))

            # il faut enlever les doubles string sinon on ne peut concatener???
            nom_graph= config.get('graph', 'nom_graph')
            nom= config.get('graph', 'nom')
            legende= config.get('graph', 'legende')
            ylabel= config.get('graph', 'ylabel')
            ptittle= config.get('graph', 'ptittle')
            tittle=''
            # traitement des retours à la ligne
            for t in ptittle.split('\\n'):
                tittle=tittle+t+'\n'
            ptittle=tittle
        except Exception as e:
            print ("Erreur lecture {}: {}".format(fic_config,e))
            sys.exit()

        #Récupération de acqid_deb et fin en fonction de date de début et de fin
        dt_deb = dt.datetime.strptime(date_deb,"%Y%m%d")
        Acqid_inf = AcqIdDoY (plateforme = abrev, date = dt_deb)
        acqid_inf=str(Acqid_inf)
        dt_fin = dt.datetime.strptime(date_fin,"%Y%m%d")
        Acqid_sup = AcqIdDoY (plateforme = abrev, date = dt_fin)
        acqid_sup=str(Acqid_sup) 
        Y2 = acqid_sup[2:4]
        Y4 = AIDA.Y2_to_Y4(Y2)

        print ("DEBUG:Fin lecture arguments: {} {} {}".format(abrev, acqid_inf,acqid_sup))

        # validité de l'acqid
        decode_acqid(acqid_sup)
        decode_acqid(acqid_inf)


        if i > 0 :
            nom_graph=nom_graph+"{}_{}_compare.png".format(acqid_inf,acqid_sup)
        else :
            nom_graph=nom_graph+"{}_{}{}.png".format(acqid_inf,acqid_sup,nom)
        print("DEBUG: nom_graph={}".format( nom_graph))

        bornes = periode(acqid_inf,acqid_sup)
        if hh_deb == None or hh_fin == None:
            ptittle=ptittle[:]+' Période du {} au {}'.format(bornes[0],bornes[1])
        else:
            ptittle=ptittle[:]+' Période du {} {}:{} au {} {}:{}'.format(bornes[0],hh_deb[0:2].zfill(2)
                    ,hh_deb[3:4].zfill(2),bornes[1],hh_fin[0:2].zfill(2),hh_fin[3:4].zfill(2))
        #print ("DEBUG: ptittle={}".format(ptittle))



        #calcul des moyennes ur le période sélectionnée
        l_moy_tsol_haut,l_prof,l_donnees_manquantes,moy_tsol_glob,unite=calcule_moyenne_profil(vecteur_liste1,tsol_haut,Acqid_inf,Acqid_sup,nb_val_jr,hh_deb,hh_fin)
        #print (l_moy_tsol,type(l_moy_tsol))

        # Création du graphique de profil moyen
        xlabel='T {}'.format(unite)
        xmin, xmax = graph(fig,axg, xmin, xmax, l_moy_tsol_haut,moy_tsol_glob,l_donnees_manquantes,l_prof,tsol_rang,tsol_nom,unite,nom_graph,legende, xlabel,ylabel,ptittle, i+1)
        i = i + 1

    fig.savefig(nom_graph)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
