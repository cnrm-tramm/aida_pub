#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import json
from vista.modele import date as vd
from vista.modele.config import ConfigDocument, ConfigPage, ConfigGraphique, ConfigTrace
import numpy as np
import math
import datetime
from operator import or_
from scipy import stats
import AIDA  # @UnresolvedImport
import AcqId
import string
import copy
import glob
from matplotlib import dates as mpl_dates

"""
##################################### Document
"""
class Document :
    """
        Classe qui définit un document
    """
    nextId = 0 # id à affecter à la création d'un nouvel élément
    currentId = -1 # id de l'élément sélectionné
    couleurs =["#000000","#FF0000","#00FF00","#0000FF","#FF6B00"] # liste des couleurs par défaut utilisées dans le document.
    fichierDefaut = "/var/tmp/Sans nom"
    groupesLiaison = {} # contient les datas du documents quis ont liées par un groupe
    messageUpdate = ""
    pressePapier = None
    
    def getId(cls) :
        idElement = cls.nextId
        cls.nextId += 1
        return idElement
    getId = classmethod(getId)
    
    def __init__(self, srcType='DATA', src='{}', versionVista = '1.3.0') :
        self.compatible = 0
        self.message = ""
        self.id = -1
        self.type = "Document"
        if srcType == 'FICHIER' :
            self.fichier = src
        else :
            self.fichier = Document.fichierDefaut
        self.versionVista = versionVista
        self.typePeriode = 0 #0 = mois,  1=dates
        self.dateMois = vd.now()
        self.dateDebut, self.dateFin = vd.debutFinMois(self.dateMois)
        self.config = self.readConfig(srcType, src)
        self.parametres = ConfigDocument(self.config)
        ospath = os.path.dirname(sys.argv[0])
        if ospath == "" :
            ospath = "."
        self.logoPath = os.getenv('AIDA_HOME')+"/share/common/logos"
        self.logoList = [ f for f in glob.glob('*', root_dir=self.logoPath) ]
        self.batch = True
        self.nbDataALire = 0 # nombre de data à lire
        self.nbDataLu = 0 # nombre de data lues => permet de calculer la fraction de données lues
        self.constructor()
        self.checkCompatibiliteVersion()
        self.arretLecture = False
        
    def constructor(self):
        """
            Construit le document avec la config
        """
        if "pages" in list(self.config.keys()) :
            self.nbPages = len(self.config['pages'])
        else :
            self.nbPages = 0
        
        self.pages = []
        for i in range(0,self.nbPages) :
            self.pages.append(Page(self, self.config['pages'][i], self.parametres))
                          
    def getValue(self, param):
        if param in list(self.parametres.desc.keys()) :
            return self.parametres.desc[param]["value"]
        else :
            return None
        
    def setValue(self, param, value):
        if param in list(self.parametres.desc.keys()) :
            self.parametres.desc[param]["value"] = value
            
    def getDefault(self, param):
        return self.parametres.desc[param]["default"]             

    
    def saveConfig(self, dest) :
        """
            Sauvegarde de la config dans un fichier
            dest : nom du fichier à écrire
        """
        jsonDocument = {}
        self.toJson(jsonDocument)
        try:
            with open(dest, 'w+') as fp :
                try :
                    json.dump(jsonDocument, fp, indent=4)
                    fp.flush()
                except ValueError :
                    raise RuntimeError("Erreur saveConfig : la config n'est pas sérialisable en JSON.")     
        except IOError:
            raise RuntimeError("Erreur saveConfig : impossible d'ouvrir le fichier de config en écriture {}".format(dest))
        
    def toJson(self,jsonDocument):
        """
            Ecrit la config dans un dictionnaire
        """
        for key in sorted(self.parametres.desc) :
            if self.parametres.desc[key]["serialize"] :
                if self.getValue(key) != self.getDefault(key) :
                    jsonDocument[key] = self.getValue(key)
        jsonDocument["pages"] = []
        for page in self.pages :
            page.toJson(jsonDocument)
        
    def readConfig(self, srcType, src):
        """
            Lecture de la config depuis une chaîne de caractères ou un fichier
            srcType : DATA, FICHIER
            src : source de la donnée qui permet de construire le document
        """
        
        if ( srcType != "DATA" and srcType != "FICHIER") :
            raise RuntimeError ("Erreur readConfig : le type de source est inconnu.")
            
        if ( srcType == "DATA" ) :
            if not isinstance(src, str) :
                raise RuntimeError ("Erreur readConfig : src n'est pas une chaîne de caractères pour le type DATA.")
            
            try :
                data = json.loads(src)
            except ValueError :
                raise RuntimeError ("Erreur readConfig : src n'est pas une chaîne JSON valide.") 

        elif ( srcType == "FICHIER" ) :
            if not isinstance(src, str) :
                raise RuntimeError ("Erreur readConfig : src n'est pas une chaîne de caractères pour le type FICHIER")
            
            try:
                with open(src, 'r') as fp :
                    try :
                        data = json.load(fp)
                    except ValueError :
                        raise RuntimeError ("Erreur readConfig : le fichier {} n'est pas un fichier vista valide.".format(src))      
            except IOError:
                raise RuntimeError ("Erreur readConfig : Impossible d'ouvrir le fichier de config {}".format(src))
        
        return data


    def appendNew(self, typ):
        page = Page(self, {}, {})
        # la nouvelle page hérite de quelques attributs de la page précédente si elle existe
        if len(self.pages) != 0 :
            for attr in ["titre", "policeTitre", "orientation", "logo", "positionLogo"] :
                page.setValue(attr, self.pages[len(self.pages)-1].getValue(attr))
        else :
            # titre par défaut si première page
            titre = "du $DATEDEBUT1 au $DATEFIN1"
            page.setValue("titre", titre)
            
        self.pages.append(page)
        return page
    
    def removeElement(self, idElmt):
        """
            Suppression d'un élément du document
        """
        if idElmt == -1 :
            print ("Erreur : la suppression du document est interdite.")
            return False
        for p in range (0, len(self.pages)) :
            if self.pages[p].id == idElmt :
                self.pages.remove(self.pages[p])
                return True
            for g in range (0, len(self.pages[p].graphiques)) :
                if self.pages[p].graphiques[g].id == idElmt :
                    self.pages[p].graphiques.remove(self.pages[p].graphiques[g])
                    return True
                for t in range (0, len(self.pages[p].graphiques[g].traces)) :
                    if self.pages[p].graphiques[g].traces[t].id == idElmt :
                        self.pages[p].graphiques[g].traces.remove(self.pages[p].graphiques[g].traces[t])
                        return True
        raise RuntimeError("Erreur : aucun élément avec l'id {} n'a été trouvé dans le document.".format(idElmt))
    
    def getElementById(self, idElmt): 
        """
            Retourne l'élément du document correpondant à idElmt
        """
        if idElmt == -1 :
            return self
        for p in range (0, len(self.pages)) :
            if self.pages[p].id == idElmt :
                return self.pages[p]
            for g in range (0, len(self.pages[p].graphiques)) :
                if self.pages[p].graphiques[g].id == idElmt :
                    return self.pages[p].graphiques[g]
                for t in range (0, len(self.pages[p].graphiques[g].traces)) :
                    if self.pages[p].graphiques[g].traces[t].id == idElmt :
                        return self.pages[p].graphiques[g].traces[t]
        raise RuntimeError("Erreur getElementById : aucun élément avec l'id {} n'a été trouvé dans le document.".format(idElmt))
        
    def insertElement(self, idElmt, before, typ):
        """
            Insere un élément avant (before = True) ou après (before = False) idElmt
        """
        ind = 1
        if before :
            ind = 0
        if idElmt == -1 :
            return None
        for p in range (0, len(self.pages)) :
            if self.pages[p].id == idElmt :
                newElmt = self.fabrique('Page', self)
                # la nouvelle page hérite de quelques attributs de la page sélectionnée
                for attr in ["titre", "policeTitre", "orientation", "logo", "positionLogo"] :
                    newElmt.setValue(attr, self.pages[p].getValue(attr))
                self.pages.insert(p+ind, newElmt)                    
                return newElmt
            for g in range (0, len(self.pages[p].graphiques)) :
                if self.pages[p].graphiques[g].id == idElmt :
                    newElmt = self.fabrique('Graphique', self.pages[p], typ)
                    # le nouveau graphique hérite de quelques attributs du graphique sélectionné
                    for attr in ["titre", "policeTitre"] :
                        newElmt.setValue(attr, self.pages[p].graphiques[g].getValue(attr))
                    self.pages[p].graphiques.insert(g+ind, newElmt)
                    return newElmt
                for t in range (0, len(self.pages[p].graphiques[g].traces)) :
                    if self.pages[p].graphiques[g].traces[t].id == idElmt :
                        newElmt = self.fabrique('Tracé', self.pages[p].graphiques[g])
                        self.pages[p].graphiques[g].traces.insert(t+ind, newElmt)
                        # la couleur par défaut du nouveau tracé est celle correspondant à son numéro
                        if len(self.pages[p].graphiques[g].traces) <= len(Document.couleurs) :
                            newElmt.setValue("couleur", Document.couleurs[len(self.pages[p].graphiques[g].traces)-1])
                        return newElmt
        raise RuntimeError ("Erreur inserElement : aucun élément avec l'id {} n'a été trouvé dans le document pour insertion.".format(idElmt))
        return None
        
    def fabrique(self, typeElmt='Page', parent=None, typ=None):
        """
            fabrique d'objets à partir du type (Page, Graphique ou Tracé)
        """
        if typeElmt == 'Page' :
            return Page(parent, {}, {})
        if typeElmt == 'Graphique' :
            return Graphique(parent, {}, {}, typ)
        if typeElmt == 'Tracé' :
            return Trace(parent, {}, {}, parent.type)
        
        return None
    
    def getNumPage(self, idPage):
        """
            retourne le numéro de la page dans le document
        """
        for p in range (0, len(self.pages)) :
            if self.pages[p].id == idPage :
                return p
        
        raise RuntimeError("Erreur : la page {} n'a pas été trouvéé dans le document".format(idPage))
        #return -1
    
    def updateData(self, queue=None):
        """
            Met à jour les données
        """
        self.messsageUpdate = ""
        try :
            self.setNbDataALire()
            self.nbDataLu = 0
            self.setGroupesLiaison()
            for p in range(0, len(self.pages)) :
                self.pages[p].updateData(self.dateDebut, self.dateFin)
            self.updateDataGroupesLiaison()
            self.nbDataLu = -1

        except Exception :
            self.nbDataLu = -1
            if queue != None :
                queue.put(sys.exc_info())
    
    def setGroupesLiaison(self):
        """
            Parcours le document pour positionner les groupes de liaison et vérifier s'il y a eu des modifications.
            Si c'est le cas, toutes les datas concernées doivent être rechargées lors de l'update :
            pour cela on modifie juste le str_data du tracé.
        """
        groupesL = {}
        for p in self.pages :
            for g in p.graphiques :
                if g.getValue("groupe_liaison") != g.getDefault("groupe_liaison") :
                    for t in g.traces :
                        try :
                            groupesL[g.getValue("groupe_liaison")].append(t)
                        except :
                            groupesL[g.getValue("groupe_liaison")] = [t]
        # on compare les 2 groupesLiaison et on modifie le tracé si'il ya des différences
        for k in list(groupesL.keys()) :
            if k in list(self.groupesLiaison.keys()) :
                if set(groupesL[k]) != set(self.groupesLiaison[k]) :
                    for t in groupesL[k] :
                        t.strData = "to update"
                    for t in self.groupesLiaison[k] :
                        t.strData = "to update"
            else :
                for t in groupesL[k] :
                    t.strData = "to update"
                    
        for k in list(self.groupesLiaison.keys()) :
            if k not in list(groupesL.keys()) :
               for t in self.groupesLiaison[k] :
                    t.strData = "to update"
                    
        self.groupesLiaison = groupesL
    
    def updateDataGroupesLiaison(self):
        """
            Met à jour les données qui appartiennent à un même groupe de liaison : on ne conserve une donnée au temps t que
            si elle est présente dans l'ensemble des données au même temps t.
        """
        for k in list(self.groupesLiaison.keys()) :
            mask = np.array([False])
            for trace in self.groupesLiaison[k] :
                try :
                    if trace.data_x is not None :
                        mask = mask | trace.data_x.mask
                    mask = mask | trace.data_y.mask
                except Exception :
                    self.messageUpdate += "Impossible de créer le masque pour le groupe {} : toutes les données doivent avoir la même taille.\n".format(k)
                    mask = None
                    break
            if mask is not None :
                for trace in self.groupesLiaison[k] :
                    if trace.data_x is not None :
                        trace.data_x.mask = mask
                    trace.data_y.mask = mask
            
    def clearData(self):
        """
            Efface toutes les données : utile quand on interrompt le thread de lecture.
        """
        for p in range(0, len(self.pages)) :
            for g in range(0, len(self.pages[p].graphiques)) :
                for t in range(0, len(self.pages[p].graphiques[g].traces)) :
                    my_trace = self.pages[p].graphiques[g].traces[t]
                    my_trace.vecteur_y = None # vecteur en ordonnées
                    my_trace.vecteur_x = None # vecteur en abscisses
            
    def initLecture(self):
        """
            Initialise le nombre de data à lire/lu de façon que la fraction soit 0.
            A appeler avant tout updateData lancé dans un thread.
        """
        self.nbDataALire = 1
        self.nbDataLu = 0
        
    def getOutputFileName(self):
        """
            Retourne le nom du fichier output en substituant les macros si nécessaire
        """
        fichier = self.getValue("dest_fic")
        rac,_ = os.path.splitext(os.path.basename(self.fichier))
        fichier = fichier.replace("$CONFIG", rac)
        datedeb = self.dateDebut[0:8]
        fichier = fichier.replace("$DATEDEBUT", datedeb)
        datefin = self.dateFin[0:8]
        fichier = fichier.replace("$DATEFIN", datefin)
        
        rep = self.getValue("dest_dir")
        output = os.path.join(rep, fichier)
        
        return output
    
    def toTitle(self, titre):
        """
            Parse un titre et substitue les macros si nécessaire
        """
        # dates
        titre = titre.replace("$DATEDEBUT3", vd.toString(self.dateDebut, "JJ mm AAAA"))
        titre = titre.replace("$DATEDEBUT2", vd.toString(self.dateDebut, "jj mm AAAA"))
        titre = titre.replace("$DATEDEBUT1", vd.toString(self.dateDebut, "JJ/MM/AAAA"))
        titre = titre.replace("$DATEFIN3", vd.toString(self.dateFin, "JJ mm AAAA"))
        titre = titre.replace("$DATEFIN2", vd.toString(self.dateFin, "jj mm AAAA"))
        titre = titre.replace("$DATEFIN1", vd.toString(self.dateFin, "JJ/MM/AAAA"))
        titre = titre.replace("$MOIS1", vd.toString(self.dateFin, "mm AAAA"))
        titre = titre.replace("$MOIS2", vd.toString(self.dateFin, "mm"))
        
        # config
        rac,_ = os.path.splitext(os.path.basename(self.fichier))
        titre = titre.replace("$CONFIG", rac)
        
        return titre
        
    def getListeCouleurs(self):
        """
            Retourne la liste des couleurs utilisées dans le document.
        """
        couleurs = []
        for p in self.pages :
            for g in p.graphiques :
                for t in g.traces :
                    couleurs.append(t.getValue("couleur"))
                    for c in t.expressions_condition :
                        couleurs.append(c["couleur"])
        couls = list(set(couleurs))
        couls.sort()
        
        return couls
    
    def reloadDatas(self):
        """
            Force le chargement des données.
        """
        # on force le rechargement des données
        for p in self.pages :
            for g in p.graphiques :
                for t in g.traces :
                    t.strData = ""
                    t.strDataOperations = ""
        
                                
    def getPrettyAttrs(self):
        """
            Retourne une chaîne donnant la liste des attributs configurables avec leur valeur par défaut.
        """
        mystr =  "\n---------------------------------------"
        mystr += "\n- Liste des attributs configurables : -\n"
        mystr +=  "---------------------------------------\n"
        mystr += "\n\n-------- Attributs du document --------\n\n"
        for attr in list(self.parametres.desc.keys()) :
            if self.parametres.desc[attr]["desc"] != "" :
                mystr2 = "  "+attr+" :\t"+self.parametres.desc[attr]["desc"]
                mystr2 += "\n\t\t\tType : {}\n".format(self.parametres.desc[attr]["type"])
                if self.parametres.desc[attr]["authorized"] != None :
                    mystr2 += "\t\t\tValeurs possibles : {}\n".format(self.parametres.desc[attr]["authorized"])
                if self.parametres.desc[attr]["mixed"] != None :
                    mystr2 += "\t\t\tValeurs multiples possibles (sep = ,): {}\n".format(self.parametres.desc[attr]["mixed"])
                if self.parametres.desc[attr]["type"] == "str" :
                    mystr2 += "\t\t\tValeur par défaut : \"{}\"\n".format(self.getDefault(attr))
                else :
                    mystr2 += "\t\t\tValeur par défaut : {}\n".format(self.getDefault(attr))
                mystr += mystr2
        mystr += "\n\n-------- Attributs d'une page --------\n\n"
        page = self.fabrique('Page')
        for attr in list(page.parametres.desc.keys()) :
            if page.parametres.desc[attr]["desc"] != "" :
                mystr2 = "  "+attr+" :\t"+page.parametres.desc[attr]["desc"]
                mystr2 += "\n\t\t\tType : {}\n".format(page.parametres.desc[attr]["type"])
                if page.parametres.desc[attr]["authorized"] != None :
                    mystr2 += "\t\t\tValeurs possibles : {}\n".format(page.parametres.desc[attr]["authorized"])
                if page.parametres.desc[attr]["mixed"] != None :
                    mystr2 += "\t\t\tValeurs multiples possibles (sep = ,): {}\n".format(page.parametres.desc[attr]["mixed"])
                if page.parametres.desc[attr]["type"] == "str" :
                    mystr2 += "\t\t\tValeur par défaut : \"{}\"\n".format(page.getDefault(attr))
                else :
                    mystr2 += "\t\t\tValeur par défaut : {}\n".format(page.getDefault(attr))
                mystr += mystr2
        
        mystr += "\n\n-------- Attributs d'un graphique --------\n\n"
        graph = self.fabrique('Graphique')
        for attr in list(graph.parametres.desc.keys()) :
            if graph.parametres.desc[attr]["desc"] != "" :
                mystr2 = "  "+attr+" :\t"+graph.parametres.desc[attr]["desc"]
                mystr2 += "\n\t\t\tType : {}\n".format(graph.parametres.desc[attr]["type"])
                if graph.parametres.desc[attr]["authorized"] != None :
                    mystr2 += "\t\t\tValeurs possibles : {}\n".format(graph.parametres.desc[attr]["authorized"])
                if graph.parametres.desc[attr]["mixed"] != None :
                    mystr2 += "\t\t\tValeurs multiples possibles (sep = ,): {}\n".format(graph.parametres.desc[attr]["mixed"])
                if graph.parametres.desc[attr]["type"] == "str" :
                    mystr2 += "\t\t\tValeur par défaut : \"{}\"\n".format(graph.getDefault(attr))
                else :
                    mystr2 += "\t\t\tValeur par défaut : {}\n".format(graph.getDefault(attr))
                mystr += mystr2
                
        mystr += "\n\n-------- Attributs d'un tracé --------\n\n"
        trace = self.fabrique('Tracé', parent=graph)
        for attr in list(trace.parametres.desc.keys()) :
            if trace.parametres.desc[attr]["desc"] != "" :
                mystr2 = "  "+attr+" :\t"+trace.parametres.desc[attr]["desc"]
                mystr2 += "\n\t\t\tType : {}\n".format(trace.parametres.desc[attr]["type"])
                if trace.parametres.desc[attr]["authorized"] != None :
                    mystr2 += "\t\t\tValeurs possibles : {}\n".format(trace.parametres.desc[attr]["authorized"])
                if trace.parametres.desc[attr]["mixed"] != None :
                    mystr2 += "\t\t\tValeurs multiples possibles (sep = ,): {}\n".format(trace.parametres.desc[attr]["mixed"])
                if trace.parametres.desc[attr]["type"] == "str" :
                    mystr2 += "\t\t\tValeur par défaut : \"{}\"\n".format(trace.getDefault(attr))
                else :
                    mystr2 += "\t\t\tValeur par défaut : {}\n".format(trace.getDefault(attr))
                mystr += mystr2
        return (mystr)
    
    def getFractionDataLues(self):
        """
            Retourne la fraction de datas lues.
        """
        if self.nbDataALire == 0 :
            return -1.0
        fraction = self.nbDataLu / (self.nbDataALire*1.0)
        return fraction
    
    def setNbDataALire(self):
        """
            Calcule et positionne le nombre de datas à lire
        """
        nb_data = 0
        for p in range (0, len(self.pages)) :
            for g in range (0, len(self.pages[p].graphiques)) :
                for t in range (0, len(self.pages[p].graphiques[g].traces)) :
                    nb_data += 1
                    if self.pages[p].graphiques[g].traces[t].type == "PlotXY" or self.pages[p].graphiques[g].traces[t].type == "RDV":
                        nb_data += 1
                    nb_data += len(self.pages[p].graphiques[g].traces[t].datas_operation_definition_x)
                    nb_data += len(self.pages[p].graphiques[g].traces[t].datas_operation_definition_y)
                    nb_data += len(self.pages[p].graphiques[g].traces[t].datas_condition_definition)

        nbJours = vd.duree(self.dateDebut, self.dateFin)
        self.nbDataALire = nb_data*nbJours
    
    def checkCompatibiliteVersion(self):
        """
            Vérifie la compatibilité de la version du document avec la version de vista :
            0 = compatible
            1 = non compatible mais lisible
            2 = non compatible
            Met à jour les attributs compatible et message du document
        """
        versionDocument = self.getValue("version_vista")
        
        # Mise en place de la mise en page des graphiques en version 1.3.0
        if self.compareVersion(versionDocument, '1.3.0') == -1 :
            self.message = "Le fichier a été créé avec une version ancienne de Vista ({}).\n La mise en page des graphiques peut être impactée.".format(versionDocument)
            self.compatible = 1
        
        #     
        if self.compareVersion(versionDocument, '4.2.0') == -1 :
            # recherche des graphiques hovmoller :
            # en 4.2.0 on a déplacé des attributs du graphique vers le tracé avec la possibilité de
            # superposer plusieurs graphiques hovmoller.
            params_a_basculer = ["typeHov", "couleurHov", "reversePaletteHov", "seuilMinHov", "seuilMaxHov", "horsGammeVisibleHov"]
            for p in self.pages :
                for g in p.graphiques :
                    if g.type == "Hov" :
                        t = g.traces[0]
                        for param in params_a_basculer :
                            try :
                                value = g.getValue(param)
                                t.setValue(param, value)
                                g.setValue(param, g.getDefault(param))
                            except Exception as e:
                                print(e)
                            
        
    def compareVersion(self, version1, version2):
        """
            Compare 2 versions de vista et retourne :
            0 = versions identiques
            1 = version1 supérieure à version2
            -1 = version1 antérieure à version2
        """
        tversion1 = version1.split('.')
        tversion2 = version2.split('.')
        if tversion1[0] == tversion2[0] :
            if tversion1[1] == tversion2[1] :
                if tversion1[2] == tversion2[2] :
                    comp = 0
                else :
                    comp = (int(tversion1[2]) - int(tversion2[2])) / abs(int(tversion1[2]) - int(tversion2[2]))
            else :
                comp = (int(tversion1[1]) - int(tversion2[1])) / abs(int(tversion1[1]) - int(tversion2[1]))
        else :
            comp = (int(tversion1[0]) - int(tversion2[0])) / abs(int(tversion1[0]) - int(tversion2[0]))
        return comp
                    
    def paste(self, obj_to_paste) :
        """
            Colle un objet dans le document : on fait une hard copie de cet objet. 
            Certains attributs doivent être recopiés par deepcopy pour être distincts de l'objet d'origine.
            Retourne la liste de tous les objets collés récursivement (ici un seul objet)
        """
        obj_list = []
        if not isinstance(obj_to_paste, Page) :
            print("Warning Vista : pas possible de coller {} dans Document !".format(type(obj_to_paste)))
            return(obj_list)
        obj = copy.copy(obj_to_paste)
        obj.id = Document.getId()
        obj.parent = self
        obj.parametres = copy.deepcopy(obj.parametres)
        obj_list.append(obj)
        graphiques = copy.copy(obj.graphiques)
        obj.graphiques = []
        for g in graphiques :
            obj_g = obj.paste(g)
            obj_list.extend(obj_g)
        self.pages.append(obj)
        
        return(obj_list)            
        
"""
##################################### Page
"""               
class Page :
    """
        Classe qui définit une page.
    """    
    def __init__(self, parent, config, parametres) :
        self.id = Document.getId()
        self.type = "Page"
        self.parent = parent
        self.parametres = ConfigPage(config)
        self.graphiques = []
        if "graphiques" in list(config.keys()) :
            for i in range(0, len(config['graphiques'])) :
                self.graphiques.append(Graphique(self, config['graphiques'][i], parametres)) 
            
    def getValue(self, param):
        if param in list(self.parametres.desc.keys()) :
            return self.parametres.desc[param]["value"]
        else :
            return None
        
    def setValue(self, param, value):
        if param in list(self.parametres.desc.keys()) :
            self.parametres.desc[param]["value"] = value
            
    def getDefault(self, param):
        return self.parametres.desc[param]["default"]
      
    def toJson(self,jsonDocument):
        """
            Ecrit la config dans un dictionnaire
        """
        jsonPage = {}
        for key in sorted(self.parametres.desc) :
            if self.parametres.desc[key]["serialize"] :
                if self.getValue(key) != self.getDefault(key) :
                    jsonPage[key] = self.getValue(key)
        jsonPage["graphiques"] = []
        for graphique in self.graphiques :
            graphique.toJson(jsonPage)
        
        jsonDocument["pages"].append(jsonPage)            
           

    def appendNew(self, typ):
        """
            Ajout d'un nouveau graphique
        """
        graph = Graphique(self, {}, {}, typ)
        # le nouveau graphique hérite de quelques attributs du graphique précédent s' il existe
        if len(self.graphiques) != 0 :
            for attr in ["titre", "policeTitre"] :
                graph.setValue(attr, self.graphiques[len(self.graphiques)-1].getValue(attr))
        self.graphiques.append(graph)
        return graph
    
    
    def updateData(self, debut, fin):
        """
            Met à jour les données
        """
        for g in range(0, len(self.graphiques)) :
            self.graphiques[g].updateData(debut, fin)
            
            
    def toTitle(self, titre):
        """
           Parse un titre et substitue les macros si nécessaire 
        """
        doc = self.parent
        return doc.toTitle(titre)

    def paste(self, obj_to_paste) :
        """
            Colle un objet dans la page : on fait une hard copie de cet objet. 
            Certains attributs doivent être recopiés par deepcopy pour être distincts de l'objet d'origine.
            Retourne la liste de tous les objets collés récursivement (ici un seul objet)
        """
        obj_list = []
        if not isinstance(obj_to_paste, Graphique) :
            print("Warning Vista : pas possible de coller {} dans Page !".format(type(obj_to_paste)))
            return(obj_list)
        obj = copy.copy(obj_to_paste)
        obj.id = Document.getId()
        obj.parent = self
        obj.parametres = copy.deepcopy(obj.parametres)
        obj_list.append(obj)
        traces = copy.copy(obj.traces)
        obj.traces = []
        for t in traces :
            obj_t = obj.paste(t)
            obj_list.extend(obj_t)
        self.graphiques.append(obj)
        
        return(obj_list)    
"""
##################################### Graphique
"""          
class Graphique :
    """
        Classe qui définit un graphique du document
    """
    def __init__(self, parent, config, parametres,typ=None) :
        self.id = Document.getId()
        self.parent = parent
        self.parametres = ConfigGraphique(config)
        if typ is None : # le type a été lu dans le fichier de config
            self.type = self.getValue("type")
        else : # création d'un nouvel objet avec le type passé en argument
            self.type = typ
            self.setValue("type", self.type)
            
        self.traces = []
        if "traces" in list(config.keys()) :
            for i in range(0, len(config['traces'])) :
                self.traces.append(Trace(self, config['traces'][i], parametres))
        self.bins = [] # bins pour les Histo3D
        self.info_rdv = None # données associées à la rose des vents (voir vistarose _info)
        self.labels_gauche_hov = ["100%","75%","50%","25%","10%","Auto","Aucun"]            
                
    def getValue(self, param):
        if param in list(self.parametres.desc.keys()) :
            return self.parametres.desc[param]["value"]
        else :
            return None
        
    def setValue(self, param, value):
        if param in list(self.parametres.desc.keys()) :
            self.parametres.desc[param]["value"] = value
            
    def getDefault(self, param):
        return self.parametres.desc[param]["default"]           
    
    def toJson(self,jsonPage):
        """
            Ecrit la config dans un dictionnaire
        """
        jsonGraphique = {}
        for key in sorted(self.parametres.desc) :
            if self.parametres.desc[key]["serialize"] :
                if self.getValue(key) != self.getDefault(key) :
                    jsonGraphique[key] = self.getValue(key)
        jsonGraphique["traces"] = []
        for trace in self.traces :
            trace.toJson(jsonGraphique)
        
        jsonPage["graphiques"].append(jsonGraphique)
        
    def appendNew(self, typ):
        """
            Ajout d'un nouveau trace
        """
        if not typ :
            typ = self.type
        trace = Trace(self, {}, {}, typ)
        self.traces.append(trace)        
        # la couleur par défaut du nouveau tracé est celle correspondant à son numéro
        if len(self.traces) <= len(Document.couleurs) :
            trace.setValue("couleur", Document.couleurs[len(self.traces)-1])
        return trace
    
    def updateData(self, debut, fin):
        """
            Met à jour les données
        """
        for t in range(0, len(self.traces)) :
            self.traces[t].updateData(debut, fin)
            
    def toTitle(self, titre):
        """
            Parse un titre et substitue les macros si nécessaire 
        """
        doc = self.parent.parent
        return doc.toTitle(titre)
    
    def setPosition(self, x, y, w, h):
        """
            Positionne les attributs x, y, width, height
        """
        self.setValue("x", int(x))
        self.setValue("y", int(y))
        self.setValue("width", int(w))
        self.setValue("height", int(h))
        
    def paste(self, obj_to_paste) :
        """
            Colle un objet dans le graphique : on fait une hard copie de cet objet. 
            Certains attributs doivent être recopiés par deepcopy pour être distincts de l'objet d'origine.
            Retourne la liste de tous les objets collés récursivement (ici un seul objet)
        """
        if not isinstance(obj_to_paste, Trace) :
            print("Warning Vista : pas possible de coller {} dans Graphique !".format(type(obj_to_paste)))
            return([])
        obj = copy.copy(obj_to_paste)
        obj.id = Document.getId()
        obj.parent = self
        # le type de l'objet est le même que son parent sauf pour Hov
        # qui admet des tracés Hov ou ST
        if self.type == "Hov" :
            if obj.type != "Hov" and obj.type != "ST" :
                obj.type = self.type
        else :
            obj.type = self.type
        obj.setValue('type', self.type)
        do_not_copy_list = ["id", "parent", "type"]
        for attr in obj.__dict__.keys() :
            if attr not in do_not_copy_list :
                cmd_copy = "obj.{}=copy.deepcopy(obj.{})".format(attr, attr)
                exec(cmd_copy)
        self.traces.append(obj)
        
        return [obj]
            
"""
##################################### Tracé
"""        
class Trace :
    """
        Classe qui définit un tracé d'un graphique
    """
    def __init__(self, parent, config, parametres, typ=None) :
        self.id = Document.getId()
        self.parent = parent
        self.parametres = ConfigTrace(config)
        if typ is None : # le type a été lu dans le fichier de config
            self.type = self.getValue("type")
        else : # création d'un nouvel objet avec le type passé en argument
            self.type = typ
            self.setValue("type", self.type)
        self.vecteur_y = None # vecteur en ordonnées
        self.vecteur_x = None # vecteur en abscisses
        self.data_y = None # data en ordonnées après calculs (y compris cumul et conditions)
        self.data_x = None # data en abscisses après calculs (y compris cumul et conditions)
        self.data_quiver = (None, None, None, None) # data pour le quiver des graphiques hovmoller (tuple u,v,time,bornes)
        self.debut = ""
        self.fin = ""
        self.nb_manquants = 0 # nombre de valeurs manquantes ou de valeurs pour lesquelles on n'a pas pu évaluer la condition (Histo)
        self.pourcent_manquants=0. # pourcentage correspondant à nb_manquants
        self.coeff_a = None
        self.coeff_b = None
        self.coeff_r = None
        self.data_regression = None # data de la regression linéaire pour PlotXY
        self.bins = [] # bins pour les Histo (utile pour les ticks)
        self.counts = [] # counts pour les Histo (utile pour les ticks)
        self.datas_condition_definition = [] # definitions des datas pour l'affichage conditionnel
        self.expressions_condition = [] # expressions des conditions pour l'afffichage conditionnel
        self.backup_condition = [] # stocke les datas et les conditions
        self.backup_legende = [] # stocke l'état de la legende ([visibilité, texte])
        self.strData = self.dataToString()
        self.strDataOperations = ""
        self.conditions = np.empty(0) # résultat de l'application des conditions (-1=y absent, 0=non évaluable, 1=pas de condition, 2=condition 1, 3=condition 2,...)
        self.datas_operation_definition_x = [] # definitions des datas pour l'opération
        self.expression_operation_x = "" # expression de l'opération (chaine de caractères)
        self.backup_operation_x = [] # stocke les datas et l'opération
        self.datas_operation_definition_y = [] # definitions des datas pour l'opération
        self.expression_operation_y = "" # expression de l'opération (chaine de caractères)
        self.backup_operation_y = [] # stocke les datas et l'opération
        try :
            self.configToConditions()
        except Exception :
            raise RuntimeError("Erreur ConfigTrace : la config des conditions n'est pas correcte")
            
        try :
            self.configToOperation()
        except Exception :
            raise RuntimeError("Erreur ConfigTrace : la config de l'opération n'est pas correcte")
        self.check()

        if self.getValue("legende") == "" :
            if self.getValue("plateforme") != "" and self.getValue("parametre") != "" :
                self.setLegende()
    
    def check(self):
        """
            Vérifications sur le tracé : existence des plates-formes
        """
        plateformes=[]
        if self.getValue('plateforme') != '' :
            plateformes.append(self.getValue('plateforme'))
        if self.getValue('plateforme_x') != '' :
            plateformes.append(self.getValue('plateforme_x'))
        for d in self.datas_condition_definition :
            plateformes.append(d['plateforme'])
        for d in self.datas_operation_definition_x :
            plateformes.append(d['plateforme'])
        for d in self.datas_operation_definition_y :
            plateformes.append(d['plateforme'])

        for p in plateformes :
            try :
                name = AIDA.AIDA_abrev_to_plt(p)
            except Exception as e:
                raise RuntimeError("Erreur : la plateforme {} est inconnue.\nVérifier le fichier plate-formes".format(p))
                
    def getValue(self, param):
        """
            Retourne la valeur de la config
        """
        if param in list(self.parametres.desc.keys()) :
            return self.parametres.desc[param]["value"]
        else :
            return None
        
    def setValue(self, param, value):
        """
            Positionne la valeur de la config
        """
        if param in list(self.parametres.desc.keys()) :
            self.parametres.desc[param]["value"] = value
            
    def getDefault(self, param):
        """
            Retourne la valeur par defaut de la config
        """
        return self.parametres.desc[param]["default"]             

    def getLegende(self):
        legende = self.getValue("legende")
        if legende == '' :
            self.setLegende()
        return legende
    
    def setLegende(self):
        """
            Positionne la légende avec plateforme:parametre
        """
        legende = self.getValue("plateforme")+":"+self.getValue("parametre")
        self.setValue("legende", legende)
        
    def operationToString(self, axe='y') :
        """
            Retourne une chaîne qui décrit l'opération (pour tooltip notamment)
        """
        str_operation = ""
        if axe == 'x' :
            if self.expression_operation_x != "" :
                str_operation += "y = "+self.expression_operation_x+'\n'
                for d in self.datas_operation_definition_x :
                    str_operation += "{}={}:{}".format(d["nom"], d["plateforme"], d["parametre"])
        else :
            if self.expression_operation_y != "" :
                str_operation += "y = "+self.expression_operation_y+'\n'
                for d in self.datas_operation_definition_y :
                    str_operation += "{}={}:{}\n".format(d["nom"], d["plateforme"], d["parametre"])
        return  str_operation
       
    def operationToConfig(self, axe='y'):
        """
            Ecrit la config de l'opération à partir de datas_operation_definition et expression_operation
        """
        if axe == 'x' :
            if len(self.expression_operation_x) == 0 and len(self.datas_operation_definition_x) == 0 :
                self.setValue("operation_x", self.getDefault("operation_x"))
            else :
                str_operation = ""
                # écriture des variables
                virgule=""
                for d in self.datas_operation_definition_x :
                    str_operation = "{}{}{}={}:{}".format(str_operation, virgule,d["nom"], d["plateforme"], d["parametre"])
                    virgule=","
                # écriture de l'opération
                str_operation = "{}##{}".format(str_operation, self.expression_operation_x)
                self.setValue("operation_x", str_operation)
        else :
            if len(self.expression_operation_y) == 0 and len(self.datas_operation_definition_y) == 0:
                self.setValue("operation_y", self.getDefault("operation_y"))
            else :
                str_operation = ""
                # écriture des variables
                virgule=""
                for d in self.datas_operation_definition_y :
                    str_operation = "{}{}{}={}:{}".format(str_operation, virgule,d["nom"], d["plateforme"], d["parametre"])
                    virgule=","
                # écriture de l'opération
                str_operation = "{}##{}".format(str_operation, self.expression_operation_y)
                self.setValue("operation_y", str_operation)
        
        
    def configToOperation(self):
        """
            Ecrit datas_operation_definition et expression_definition à partir de la config
        """
        # data en x (PlotST)
        self.datas_operation_definition_x = []
        self.expression_operation_x = ""
        str_operation = self.getValue("operation_x")
        if str_operation == self.getDefault("operation_x") :
            self.datas_operation_definition_x = []
            self.expression_operation_x = ""
        else :
            items = str_operation.split("##")
            # definition des variables contenues dans les conditions
            variables = items[0].split(",")
            if variables[0] != '' :
                for v in variables :
                    def_variable = v.split("=")
                    variable = {}
                    variable["nom"] = def_variable[0]
                    variable["plateforme"] = def_variable[1].split(":")[0]
                    variable["parametre"] = def_variable[1].split(":")[1]
                    variable["vecteur"] = None
                    self.datas_operation_definition_x.append(variable)
            # expressions de l'operation
            self.expression_operation_x = items[1]
        # data en y
        self.datas_operation_definition_y = []
        self.expression_operation_y = ""
        str_operation = self.getValue("operation_y")
        if str_operation == self.getDefault("operation_y") :
            self.datas_operation_definition_y = []
            self.expression_operation_y = ""
        else :
            items = str_operation.split("##")
            # definition des variables contenues dans les conditions
            variables = items[0].split(",")
            if variables[0] != '' :
                for v in variables :
                    def_variable = v.split("=")
                    variable = {}
                    variable["nom"] = def_variable[0]
                    variable["plateforme"] = def_variable[1].split(":")[0]
                    variable["parametre"] = def_variable[1].split(":")[1]
                    variable["vecteur"] = None
                    self.datas_operation_definition_y.append(variable)
            # expressions de l'operation
            self.expression_operation_y = items[1]
            
            
    def updateExpressionOperation(self, operation, axe='y') :
        """
            Met à jour l'expression de l'opération
        """
        if axe == 'x' :
            self.expression_operation_x = operation
        else :
            self.expression_operation_y = operation
        self.operationToConfig(axe)
        
    def addVariableOperation(self, nom_variable, plateforme, parametre, axe='y') :
        """
            Ajoute une variable de condition à la liste
        """
        variable = {}
        variable["nom"] = nom_variable
        variable["plateforme"] = plateforme
        variable["parametre"] = parametre
        variable["vecteur"] = None
        if axe == 'x' :
            self.datas_operation_definition_x.append(variable)
        else :
            self.datas_operation_definition_y.append(variable)
        self.operationToConfig(axe)
        
    def updateVariableOperation(self, nom_variable, plateforme, parametre, axe='y'):
        """
            Met à jour une variable d'opération
        """
        if axe == 'x' :
            for d in self.datas_operation_definition_x :
                if d["nom"] == nom_variable :
                    d["plateforme"] = plateforme
                    d["parametre"] = parametre
                    break
        else :
            for d in self.datas_operation_definition_y :
                if d["nom"] == nom_variable :
                    d["plateforme"] = plateforme
                    d["parametre"] = parametre
                    break
        self.operationToConfig(axe)
        
    def delVariableOperation(self, nom_variable, axe='y'):
        """
            Supprime une variable d'opération à la liste
        """
        if axe == 'x' :
            self.datas_operation_definition_x = [d for d in self.datas_operation_definition_x if d["nom"] != nom_variable]
        else :
            self.datas_operation_definition_y = [d for d in self.datas_operation_definition_y if d["nom"] != nom_variable] 
        self.operationToConfig(axe)
                
    def getNomVariableOperation(self, axe='y'):
        """
            Retourne la première lettre disponible pour le nom d'une variable (operation)
        """
        for v in list(string.ascii_lowercase) :
            if axe == 'x' :
                if len([ d for d in self.datas_operation_definition_x if d["nom"] == v ]) == 0 :
                    return v
            else :
                if len([ d for d in self.datas_operation_definition_y if d["nom"] == v ]) == 0 :
                    return v
        print ("Erreur : plus de nom de variable disponible ...")
        return None
    
    def setBackupOperation(self, axe):
        """
            Sauve l'opération dans le backup
        """
        if axe == 'x' :
            bak_datas_operation_definition_x = [d.copy() for d in self.datas_operation_definition_x]
            bak_expression_operation_x = self.expression_operation_x  
            self.backup_operation_x = [bak_datas_operation_definition_x, bak_expression_operation_x]
        else :
            bak_datas_operation_definition_y = [d.copy() for d in self.datas_operation_definition_y]
            bak_expression_operation_y = self.expression_operation_y  
            self.backup_operation_y = [bak_datas_operation_definition_y, bak_expression_operation_y]
                
    def restaureBackupOperation(self, axe):
        """
            Restaure le backup
        """
        if axe == 'x' :
            self.datas_operation_definition_x = self.backup_operation_x[0]
            self.expression_operation_x = self.backup_operation_x[1]
        else :
            self.datas_operation_definition_y = self.backup_operation_y[0]
            self.expression_operation_y = self.backup_operation_y[1]
        self.operationToConfig(axe)
    
    def conditionsToConfig(self):
        """
            Ecrit la config de l'affichage conditionnel à partir de datas_condition_definition et expressions_condition
        """
        if len(self.expressions_condition) == 0 :
            self.setValue("conditions", self.getDefault("conditions"))
            return
        str_conditions = ""
        # écriture des variables
        virgule=""
        for d in self.datas_condition_definition :
            str_conditions = "{}{}{}={}:{}".format(str_conditions, virgule,d["nom"], d["plateforme"], d["parametre"])
            virgule=","
        # écriture des conditions : par defaut la légende est visible et a pour label la condition
        for e in self.expressions_condition[1:] :
            str_conditions = "{}##{},{},{},{}".format(str_conditions, e["str"], e["couleur"], e["typeLigne"], e["epaisseur"])
            if e["legende"] != e["str"] or e["legendeVisible"] != self.getDefault("legendeVisible") :
                str_conditions += ","+e["legende"]+","+e["legendeVisible"]
        # écriture de la condition non évaluable
        e=self.expressions_condition[0]
        str_conditions = "{}##{},{},{},{}".format(str_conditions, e["str"], e["couleur"], e["typeLigne"], e["epaisseur"])
        if e["legende"] != e["str"] or e["legendeVisible"] != self.getDefault("legendeVisible") :
                str_conditions += ","+e["legende"]+","+e["legendeVisible"]
        self.setValue("conditions", str_conditions)    
        
    def configToConditions(self):
        """
            Ecrit datas_condition_definition et expressions_condition à partir de la config
        """
        self.datas_condition_definition=[]
        self.expressions_condition=[]
        conditions = self.getValue("conditions")
        # condition par defaut
        if conditions == self.getDefault("conditions") :
            self.datas_condition_definition = []
            condition = {}
            condition["id"] = self.getIdCondition()
            condition["str"] = "condition non évaluable"
            condition["couleur"] = "#000000"
            condition["typeLigne"] = '-'
            condition["epaisseur"] = 1
            condition["legende"] = condition["str"]
            condition["legendeVisible"] = "oui"
            self.expressions_condition.append(condition)
            return
        items = conditions.split("##")
        # definition des variables contenues dans les conditions
        variables = items[0].split(",")
        if variables[0] != '' :
            for v in variables :
                def_variable = v.split("=")
                variable = {}
                variable["nom"] = def_variable[0]
                variable["plateforme"] = def_variable[1].split(":")[0]
                variable["parametre"] = def_variable[1].split(":")[1]
                variable["vecteur"] = None
                self.datas_condition_definition.append(variable)
        # expressions des conditions
        # condition non évaluable (dernière condition de la string)
        condition = {}
        items2 = items[-1].split(",")
        condition["id"] = self.getIdCondition()
        condition["str"] = items2[0]
        condition["couleur"] = items2[1]
        condition["typeLigne"] = items2[2]
        condition["epaisseur"] = int(items2[3])
        try :
            condition["legende"] = items2[4]
            condition["legendeVisible"] = items2[5]
        except :
            condition["legende"] = condition["str"]
            condition["legendeVisible"] = "oui"
        self.expressions_condition.append(condition)
        # autres conditions
        for c in items[1:-1] :
            items2 = c.split(",")
            condition = {}
            condition["id"] = self.getIdCondition()
            condition["str"] = items2[0]
            condition["couleur"] = items2[1]
            condition["typeLigne"] = items2[2]
            condition["epaisseur"] = int(items2[3])
            try :
                condition["legende"] = items2[4]
                condition["legendeVisible"] = items2[5]
            except :
                condition["legende"] = condition["str"]
                condition["legendeVisible"] = "oui"
            self.expressions_condition.append(condition)
    
    def addVariableCondition(self, nom_variable, plateforme, parametre):
        """
            Ajoute une variable de condition à la liste
        """
        variable = {}
        variable["nom"] = nom_variable
        variable["plateforme"] = plateforme
        variable["parametre"] = parametre
        variable["vecteur"] = None
        self.datas_condition_definition.append(variable)
        self.conditionsToConfig()
        
    def updateVariableCondition(self, nom_variable, plateforme, parametre):
        """
            Met à jour une variable de condition
        """
        for d in self.datas_condition_definition :
            if d["nom"] == nom_variable :
                d["plateforme"] = plateforme
                d["parametre"] = parametre
                #d["vecteur"] = None
                break 
        self.conditionsToConfig()
        
    def delVariableCondition(self, nom_variable):
        """
            Supprime une variable ce condition à la liste
        """
        self.datas_condition_definition = [d for d in self.datas_condition_definition if d["nom"] != nom_variable]
        self.conditionsToConfig()
                
    def getNomVariableCondition(self):
        """
            Retourne la première lettre disponible pour le nom d'une variable (affichage conditionnel)
        """
        for v in list(string.ascii_lowercase) :
            if len([ d for d in self.datas_condition_definition if d["nom"] == v ]) == 0 :
                return v
        print ("Erreur : plus de nom de variable disponible ...")
        return None
    
    
    def getValueCondition(self, idc, valeur):
        """
            Retourne la valeur correspondante
        """
        for e in self.expressions_condition :
            if e["id"] == idc :
                return e[valeur]
            
    def getIdCondition(self):
        """
            Retourne un id disponible (max(Id) +1)
        """
        if len(self.expressions_condition) == 0 :
            return 0
        return max([e["id"] for e in self.expressions_condition])+1
    
    def addCondition(self, expression="", couleur="#000000", type_ligne=None, epaisseur=1):
        """
            Ajoute une condition à la liste
        """
        condition = {}
        condition["id"] = self.getIdCondition()
        condition["str"] = expression
        condition["couleur"] = couleur
        condition["typeLigne"] = type_ligne
        condition["epaisseur"] = epaisseur
        condition["legende"] = expression
        condition["legendeVisible"] = "oui"
        self.expressions_condition.append(condition)
        self.conditionsToConfig()
        return condition["id"]
    
    def delCondition(self, idc):
        """
            Supprime une condition de la liste
        """
        self.expressions_condition = [e for e in self.expressions_condition if e["id"] != idc]
        self.conditionsToConfig()
    
    def updateCondition(self, idc, expression=None, couleur=None, type_ligne=None, epaisseur=None, legende=None, legende_visible=None):
        """
            Met à jour une condition
        """
        for e in self.expressions_condition :
            if e["id"] == idc :
                if expression != None:
                    e["str"] = expression
                    e["legende"] = expression
                if couleur != None:
                    e["couleur"] = couleur
                if type_ligne != None:
                    e["typeLigne"] = type_ligne
                if epaisseur != None:
                    e["epaisseur"] = epaisseur
                if legende != None:
                    e["legende"] = legende
                if legende_visible != None:
                    e["legendeVisible"] = legende_visible
                break 
        self.conditionsToConfig()
        
    def setBackupCondition(self):
        """
            Sauve les conditions dans le backup
        """
        bak_datas_condition_definition = [d.copy() for d in self.datas_condition_definition]
        bak_datas_expressions_condition = [d.copy() for d in self.expressions_condition]   
        self.backup_condition = [bak_datas_condition_definition, bak_datas_expressions_condition]
        
        
    def restaureBackupCondition(self):
        """
            Restaure le backup
        """
        self.datas_condition_definition = self.backup_condition[0]
        self.expressions_condition = self.backup_condition[1]
        self.conditionsToConfig()
        
    def setBackupLegende(self):
        """
            Sauve la légende dans le backup
        """    
        self.backup_legende = [self.getValue("legendeVisible"), self.getValue("legende")]

        
    def restaureBackupLegende(self):
        """
            Restaure le backup de la légende
        """
        self.setValue("legendeVisible", self.backup_legende[0])
        self.setValue("legende", self.backup_legende[1])
        
        
    def toJson(self,jsonGraphique):
        """
            Ecrit la config dans un dictionnaire
        """
        jsonTrace = {}
        for key in sorted(self.parametres.desc) :
            if self.parametres.desc[key]["serialize"] :
                if self.getValue(key) != self.getDefault(key) :
                    jsonTrace[key] = self.getValue(key)
        
        jsonGraphique["traces"].append(jsonTrace)
        
    def appendNew(self, typ):
        """
            Ajout d'un nouveau tracé à la suite
        """
        
        return None
    
    
    def updateData(self, debut, fin):
        """
            Met à jour les données si besoin
        """
        self.debut = debut
        self.fin = fin
        # si les datas ont été modifiées on relit les données
        if self.strData != self.dataToString():
            self.readDatas(debut, fin)
            self.doDatasOperations()
        if self.strDataOperations != self.dataOperationsToString() :
            self.doDatasOperations()
        
    def doDatasOperations(self):
        """
            Applique les opérations sur les datas : opérations, conditions, cumul, regression
        """
        
        # opérations
        self.doOperations()

        # conditions
        self.doConditions()
            
        # calcul de la régression linéaire pour les plotsXY
        if self.type == "PlotXY" :
            self.calculRegression()
        
        # cumul
        self.doCumul()
        
        self.strDataOperations = self.dataOperationsToString()
        
    def doOperations(self):
        """
            Applique l'opération sur y et x (si PlotXY) 
        """
        Document.messageUpdate = ""
        numTrace = self.parent.traces.index(self)+1
        numGraphique = self.parent.parent.graphiques.index(self.parent)+1
        numPage = self.parent.parent.parent.pages.index(self.parent.parent)+1
        # sur y 
        if self.expression_operation_y != "" and self.vecteur_y != None and self.vecteur_y.isempty() == False :
            # évaluation des variables de condition
            # y est toujours défini (c'est la donnée du tracé)
            y = self.vecteur_y.data.copy()
            var_ok = True
            for var_operation in self.datas_operation_definition_y :
                try :                           
                    exec("{} = var_operation['vecteur'].data".format(var_operation['nom']))
                except :
                    Document.messageUpdate = "Erreur Vista tracé n°{}, graphique n°{} de la page {} : \n la variable d'opération {}={}:{} ne peut pas être évaluée (donnée absente ?)".format(numTrace, numGraphique, numPage, var_operation['nom'], var_operation["plateforme"], var_operation["parametre"])
                    var_ok = False
            # on vérifie que tous les vecteurs associés aux variables ont la même taille = taille de la data du tracé
            if var_ok :
                for var_operation in self.datas_operation_definition_y :
                    if len(var_operation["vecteur"].data) != len(y) :
                        Document.messageUpdate = "Erreur Vista tracé n°{}, graphique n°{} de la page {} : \nla variable d'opération {}={}:{} a une taille ({}) \ndifférente de la taille ({}) de la donnée visualisée {}:{}".format(numTrace, numGraphique, numPage, var_operation['nom'], var_operation["plateforme"], var_operation["parametre"],len(var_operation["vecteur"].data), len(y), self.getValue("plateforme"), self.getValue("parametre"))
                        var_ok = False
            # évaluation de l'opération
            if var_ok :
                str_oper = "from numpy import *\nself.data_y = {}".format(self.expression_operation_y)
                try :
                    exec(str_oper)
                except :
                    Document.messageUpdate = "Erreur Vista tracé n°{}, graphique n°{} de la page {} : \n l'opération \"y = {}\" n'a pas pu être effectuée.\n Vérifier la syntaxe et les variables utilisées.".format(numTrace, numGraphique, numPage, self.expression_operation_y)
        else :
            try :
                self.data_y = self.vecteur_y.data.copy()
            except :
                pass
            
        # sur x (PlotXY et RDV) 
        if self.expression_operation_x != "" and self.vecteur_x != None and self.vecteur_x.isempty() == False :
            # évaluation des variables de condition
            # y est toujours défini (c'est la donnée du tracé)
            y = self.vecteur_x.data.copy()
            var_ok = True
            for var_operation in self.datas_operation_definition_x :
                try :                           
                    exec("{} = var_operation['vecteur'].data".format(var_operation['nom']))
                except :
                    Document.messageUpdate = "Erreur Vista tracé n°{}, graphique n°{} de la page {} : \n la variable d'opération {}={}:{} ne peut pas être évaluée (donnée absente ?)".format(numTrace, numGraphique, numPage, var_operation['nom'], var_operation["plateforme"], var_operation["parametre"])
                    var_ok = False
            # on vérifie que tous les vecteurs associés aux variables ont la même taille = taille de la data du tracé
            if var_ok :
                for var_operation in self.datas_operation_definition_x :
                    if len(var_operation["vecteur"].data) != len(y) :
                        Document.messageUpdate = "Erreur Vista tracé n°{}, graphique n°{} de la page {} : \n la variable d'opération {}={}:{} a une taille ({}) \ndifférente de la taille ({}) de la donnée visualisée {}:{}".format(numTrace, numGraphique, numPage, var_operation['nom'], var_operation["plateforme"], var_operation["parametre"],len(var_operation["vecteur"].data), len(y), self.getValue("plateforme_x"), self.getValue("parametre_x"))                        
                        var_ok = False
            # évaluation de l'opération
            if var_ok :
                str_oper = "from numpy import *\nself.data_x = {}".format(self.expression_operation_x)
                try :
                    exec(str_oper)
                except :
                    Document.messageUpdate = "Erreur Vista tracé n°{}, graphique n°{} de la page {} : \n l'opération \"y = {}\" n'a pas pu être effectuée.\n Vérifier la syntaxe et les variables utilisées.".format(numTrace, numGraphique, numPage, self.expression_operation_x)
        else :
            try :
                self.data_x = self.vecteur_x.data.copy()
            except :
                pass
        
    def calculRegression(self,x=None,y=None):
        if x is None :
            try : 
                x = self.data_x
            except :
                x = None
        if y is None :
            try :
                y = self.data_y
            except :
                y = None
        # on controle que les vecteurs soient non nuls, non vides et de même taille
        #if x != None and len(np.ma.compressed(x)) != 0  and y != None and len(np.ma.compressed(y)) != 0  and len(x) == len(y):
        if x is not None and len(np.ma.compressed(x)) != 0  and y is not None and len(np.ma.compressed(y)) != 0  and len(x) == len(y):
            x2 = np.ma.compressed(np.ma.array(x.data,mask=list(map(or_,np.ma.getmaskarray(x),np.ma.getmaskarray(y)))))
            y2 = np.ma.compressed(np.ma.array(y.data,mask=list(map(or_,np.ma.getmaskarray(x),np.ma.getmaskarray(y)))))
            # avant le calcule de la regression, on transforme les data en float64 sinon on a des surprises avec les gros vecteurs
            self.coeff_a, self.coeff_b, self.coeff_r, _, _ = stats.linregress(x2.astype('float64'),y2.astype('float64')) # @UndefinedVariable
            self.data_regression = self.coeff_b + self.coeff_a * x
        else :
            self.coeff_a = None
            self.coeff_b = None
            self.coeff_r = None
            self.data_regression = None
        
    def readDatas(self, debut, fin):
        """ 
            Lit les données
        """
        # datas de base
        if self.type == "PlotXY":
            self.vecteur_x = self.readData(debut, fin, "plateforme_x", "parametre_x")
            self.vecteur_y = self.readData(debut, fin, "plateforme", "parametre")
        elif self.type == "RDV":
            self.vecteur_x = self.readData(debut, fin, "plateforme", "parametre_x")
            self.vecteur_y = self.readData(debut, fin, "plateforme", "parametre")            
        else :
            self.vecteur_y = self.readData(debut, fin, "plateforme", "parametre")
        # datas de l'opération
        for d in self.datas_operation_definition_x :
            d["vecteur"] = self.readDataAnnexe(debut, fin, d["plateforme"], d["parametre"])
        for d in self.datas_operation_definition_y :
            d["vecteur"] = self.readDataAnnexe(debut, fin, d["plateforme"], d["parametre"])
        # datas des conditions
        for d in self.datas_condition_definition :
            d["vecteur"] = self.readDataAnnexe(debut, fin, d["plateforme"], d["parametre"])
        # datas des quiver hovmoller    
        self.readDataQuiver(debut, fin)
        
        try :
            self.data_x = self.vecteur_x.data
        except :
            self.data_x = None
        try :
            self.data_y = self.vecteur_y.data
        except :
            self.data_y = None
        
        self.strData = self.dataToString() 
    
    def uniformData(self, liste_vect):
        """
        Avant de concaténer des vecteurs pour en faire un "big_vecteur" on redimensionne les vecteurs vides
        correspondants aux journées absentes (vecteurs de taille 2) :
            - On donne aux datas des vecteurs de NaN la shape du vecteur le plus grand
            - On adapte la taille du time des vecteurs NaN.
            - On donne arbitrairement aux bornes les bornes du vecteur le plus grand
        """
        if len(liste_vect) == 0 :
            return
        max_nb_vals = max([len(v.data) for v in liste_vect])
        for vref in liste_vect :
            if len(vref.data) == max_nb_vals :
                break
        date_ref = vref.time[0]
        for v in liste_vect :
            if v.isempty() and len(v.data) == 2 :
                date0 = v.time[0]
                ecart = (date0.date()-date_ref.date()).days
                data_tmp = np.empty(vref.data.shape)
                data_tmp[:] = np.nan
                time_tmp = [t + datetime.timedelta(days = ecart) for t in vref.time]
                v.data = np.ma.array(data_tmp,mask=np.isnan(data_tmp))
                v.time = time_tmp
                v.bornes = vref.bornes
                
    def vectFromDate(self, plateforme, parametre, date, fill=True) :
        """ 
            Retourne un vecteur correspondant à une date pour un paramètre donné.
            Prend en compte le fait que pour une date on peut avoir plusieurs acqids
            (pour les plateformes de type Vols, Lacher, Lacher_en_vol)
            En cas de données absentes, on retourne un vecteur vide si fill==True sinon None
        """
        liste_acq = AcqId.get_list_acqids(plateforme, date)
        vect_at_date = None
        data = None
        time = None
        bornes = None
        for acqId in liste_acq :
            vect = self.readVecteur(str(acqId), parametre)
            if vect :
                if vect_at_date is None :
                    vect_at_date = vect
                if data is not None :
                    data = np.ma.concatenate((data,vect.data))
                else :
                    data = vect.data
                if time is not None :
                    time = np.ma.concatenate((time,vect.time))                    
                else :
                    time = vect.time
                try :
                    bornes_vect = AIDA.strBornes_to_array(vect.attributes["bornes"], 
                                                     acqid=str(acqId), 
                                                     NbVal=len(vect.time))
                except :
                    bornes_vect = None
                if bornes is not None and bornes_vect is not None :
                    bornes = np.concatenate((bornes,bornes_vect))
                else :
                    bornes = bornes_vect
                
        if vect_at_date is None :
            if not fill :
                return None
            acqId = plateforme + vd.toAcqId(vd.toVistaDate(date))# on crée un acqid de type 'journee' par defaut
            pseudo_data = np.empty(2)
            pseudo_data[:] = np.nan
            vect_at_date = AIDA.VectorMask(acqId, parametre, attributes={"misval":np.nan}, data=pseudo_data, overwrite=True)
            vect_at_date.time = np.empty(2, dtype=datetime.datetime)
            vect_at_date.time[0] = date
            vect_at_date.time[1] = date + datetime.timedelta(seconds=86399)
            vect_at_date.bornes = None
        else :
            vect_at_date.data = data
            vect_at_date.time = time
            vect_at_date.bornes = bornes

        return vect_at_date
                       
    def readData(self, debut, fin,  attrplateforme, attrparametre) :
        """ 
            Lit une série de vecteurs et cree un pseudo-vecteur
            qui contient la série complète de données.
        """
        if self.getValue(attrparametre) == "" or self.getValue(attrplateforme) == "" :
            return
        liste_vect = []
        nbJours = vd.duree(debut, fin)
        for retard in range(nbJours):
            if self.parent.parent.parent.arretLecture :
                return None
            date = vd.add(fin, retard*-1)
            vect_at_date = self.vectFromDate(self.getValue(attrplateforme), self.getValue(attrparametre), vd.toDate(date))
            liste_vect.insert(0, vect_at_date)
            self.parent.parent.parent.nbDataLu += 1        
                    
        self.uniformData(liste_vect)
                
        big_data = np.ma.concatenate([vect.data for vect in liste_vect])
        big_time = np.ma.concatenate([vect.time for vect in liste_vect])
        
        try :
            big_bornes = np.concatenate([vect.bornes for vect in liste_vect if vect.bornes is not None])
        except :
            big_bornes = None
        # Et on attribue toutes les données au premier vecteur non-nul
        # de la liste (qui doit être le plus ancien)
        for vect in liste_vect:
            if not vect.isempty() and vect.attributes :
                if not 'unit' in list(vect.attributes.keys()) :
                    for vect2 in liste_vect:
                        if vect2.attributes and 'unit' in list(vect2.attributes.keys()) :
                            vect.attributes['unit'] = vect2.attributes['unit']
                if not 'unit' in list(vect.attributes.keys()) :
                    vect.attributes['unit'] = '???'
                break
        vect.data = big_data
        vect.time = big_time
        # on stocke les dates au format matplotlib pour le tracé (passage mpl3.5.1)
        # ça nous permet de pouvoir utiliser datetime ou format mpl selon les besoins.
        # il y a un coût de conversion (surtout pour les hautes fréquences) mais si on
        # ne fait pas la conversion, mpl s'en charge au moment du tracé avec le même coût.
        vect.time_mpl = mpl_dates.date2num(vect.time)
        vect.bornes = big_bornes
             
        if vect.isempty() :
            print(("Warning vista : donnée absente pour {}:{} du {} au {}".format(
                                self.getValue(attrplateforme),
                                self.getValue(attrparametre),
                                vd.toString(debut,"JJ/MM/AAAA"),
                                vd.toString(fin, "JJ/MM/AAAA"))))
            return None
        else :
            return vect
        
    def readDataQuiver(self, debut, fin) :
        """ 
            Lit les données U/V nécessaires au tracé des quiver (graphiques Hovmoller).
            La source des données est soit :
              -un vecteur U et un vecteur V -> il faut juste lire les données.
              -un vecteur DD et un vecteur FF -> il faut recalculer U et V. 
        """
        data_u = None
        data_v = None
        data_dd = None
        data_ff = None
        if self.getValue("quiverHov") == "non" :
            self.data_quiver = (None, None, None, None)
            return
        try :
            if self.getValue("quiverModeUVHov") == "oui" :
                vect_u = self.readDataAnnexe(debut, fin, self.getValue("plateformeQuiverHov"), self.getValue("parametre_u_hov"))
                vect_v = self.readDataAnnexe(debut, fin, self.getValue("plateformeQuiverHov"), self.getValue("parametre_v_hov")) 
                time = np.repeat(vect_u.time, repeats=vect_u.bornes.shape[1], axis=0).reshape(vect_u.data.shape)
                bornes = np.array([vect_u.bornes[:,:,0][0]], dtype = float)
                new_bornes = np.repeat(bornes, repeats=vect_u.data.shape[0], axis=0).reshape(vect_u.data.shape)                
                # Echantillonnage en X et Y
                step_x = int(100/float(self.getValue("echantillonHovQuiverX")))
                step_y = int(100/float(self.getValue("echantillonHovQuiverY")))
                self.data_quiver = (vect_u.data[::step_x,::step_y], 
                                    vect_v.data[::step_x,::step_y], 
                                    time[::step_x,::step_y], 
                                    new_bornes[::step_x,::step_y])
            else :
                vect_dd = self.readDataAnnexe(debut, fin, self.getValue("plateformeQuiverHov"), self.getValue("parametre_dd_hov"))
                vect_ff = self.readDataAnnexe(debut, fin, self.getValue("plateformeQuiverHov"), self.getValue("parametre_ff_hov"))
                data_u = vect_ff.data * np.sin((vect_dd.data - 180)*(np.pi/180))
                data_v = vect_ff.data * np.cos((vect_dd.data - 180)*(np.pi/180))
                time = np.repeat(vect_dd.time, repeats=vect_dd.bornes.shape[1], axis=0).reshape(vect_dd.data.shape)
                bornes = np.array([vect_dd.bornes[:,:,0][0]], dtype = float)
                new_bornes = np.repeat(bornes, repeats=vect_dd.data.shape[0], axis=0).reshape(vect_dd.data.shape)
                # Echantillonnage en X et Y
                step_x = int(100/float(self.getValue("echantillonHovQuiverX")))
                step_y = int(100/float(self.getValue("echantillonHovQuiverY")))
                self.data_quiver = (data_u[::step_x,::step_y], 
                                    data_v[::step_x,::step_y], 
                                    time[::step_x,::step_y], 
                                    new_bornes[::step_x,::step_y])
        except :
            self.data_quiver = (None, None, None, None)
            
    def readDataAnnexe(self, debut, fin, plateforme, parametre):
        """ 
            Lit une série de vecteurs et crée un pseudo-vecteur
            qui contient la série complète de données pour des variables de condition ou d'opération
        """
        if parametre == "" or plateforme == "" :
            return
        liste_vect = []
        nbJours = vd.duree(debut, fin)
        for retard in range(nbJours):
            if self.parent.parent.parent.arretLecture :
                return None
            date = vd.add(fin, retard*-1)
            vect_at_date = self.vectFromDate(plateforme, parametre, vd.toDate(date))
            liste_vect.insert(0, vect_at_date)
            self.parent.parent.parent.nbDataLu += 1

        self.uniformData(liste_vect)    
        big_data = np.ma.concatenate([vect.data for vect in liste_vect])
        big_time = np.ma.concatenate([vect.time for vect in liste_vect])
        # Et on attribue toutes les données au premier vecteur non-nul
        # de la liste (qui doit être le plus ancien)
        for vect in liste_vect:
            if not vect.isempty() and vect.attributes :
                if not 'unit' in list(vect.attributes.keys()) :
                    for vect2 in liste_vect:
                        if vect2.attributes and 'unit' in list(vect2.attributes.keys()) :
                            vect.attributes['unit'] = vect2.attributes['unit']
                if not 'unit' in list(vect.attributes.keys()) :
                    vect.attributes['unit'] = '???'
                break
        vect.data = big_data
        vect.time = big_time
        # on stocke les dates au format matplotlib pour le tracé (passage mpl3.5.1)
        data_time_mpl = []
        vect.time_mpl = mpl_dates.date2num(vect.time)        
        if vect.isempty() :
            print(("Warning vista : donnée absente pour {}:{} du {} au {}".format(
                                plateforme,
                                parametre,
                                vd.toString(debut,"JJ/MM/AAAA"),
                                vd.toString(fin, "JJ/MM/AAAA"))))
            try :
                vect.data = np.ma.masked_all(len(self.vecteur_y.data))
                vect.time = self.vecteur_y.time[:]
                vect.time_mpl = mpl_dates.date2num(vect.time) 
            except :
                pass            
        return vect
            
    def readVecteur(self, acqId, param, refTime=None):
        """
            Lit un vecteur et son ref_time.
            Le ref_time sera du type datetime de python.
            le ref_time est stocké dans l'attribut "time" du vecteur (vect.time)
            le nom du ref_time est stocké dans l'attribut "time_name" du vecteur
        """
        try:
            vect = AIDA.VectorMask(acqId, param, overwrite=True)
        except IOError as excpt:
            print(("Jour vide pour %s de %s: " % (param, acqId), str(excpt)))
            return None
    
        if 'ref_time' not in vect.attributes:
            print(("Pas de ref_time dans %s de %s" % (param, acqId)))
            return None
        if refTime is None:
            ref_time = vect.attributes['ref_time']
        time = AIDA.Vector(acqId, ref_time, overwrite=True)
        if len(time.data) != len(vect.data):
            print(("len(%s) = %d, ref_time = %s, len=%d" % (param, len(vect.data),
                                  ref_time, len(time.data))))
            return None
        #  Conversion du temps du vecteur (secondes depuis 0h00 le jour du
        # démarrage de l'acquisition) en temps UTC numérique tel que
        # représenté par le module "datetime" de python, matplotlib, etc...
        # nombre de jour depuis le 01/01/0000  en calendrier grégorien
        # proleptique)
        try :
            date_acq = AIDA.Inf(acqId).get_date_acq()
        except Exception :
            print(("Erreur de lecture du fichier INF pour {}.".format(acqId)))
            return None
        #vect.time = date_acq.toordinal() + time.data / 86400.0
        date_acq = datetime.datetime(date_acq.year, date_acq.month, date_acq.day)
        vect.time = [date_acq + datetime.timedelta(seconds=t) for t in time.data]
        vect.time_name = ref_time
        return vect
    
    def dataToString(self) :
        """
            Retourne les datas du tracé sous forme de chaine
        """
        strData_x = self.getValue("plateforme_x")+":"+self.debut+":"+self.fin+":"+self.getValue("parametre_x")
        strData = self.getValue("plateforme")+":"+self.debut+":"+self.fin+":"+self.getValue("parametre")
        strDataOperation = ""
        variablesOperation = self.getValue("operation_y").split("##")[0].split(",")
        for v in variablesOperation :
            try :
                plt_param = v.split("=")[1]
                strDataOperation += ':'+plt_param
            except :
                pass
        strDataOperation_x = ""
        variablesOperation = self.getValue("operation_x").split("##")[0].split(",")
        for v in variablesOperation :
            try :
                plt_param = v.split("=")[1]
                strDataOperation_x += ':'+plt_param
            except :
                pass
        strDataConditions = ""
        for d in self.datas_condition_definition :
            strDataConditions = "{}:{}:{}".format(strDataConditions, d["plateforme"], d["parametre"])
        strDataQuiver = ""
        if self.getValue("quiverHov") == "oui" :
            if self.getValue("quiverModeUVHov") == "oui" :
                strDataQuiver = self.getValue("plateformeQuiverHov")+":"+self.getValue("parametre_u_hov")+":"+self.getValue("parametre_v_hov")
            else :
                strDataQuiver = self.getValue("plateformeQuiverHov")+":"+self.getValue("parametre_dd_hov")+":"+self.getValue("parametre_ff_hov")
            strDataQuiver += "##"+str(self.getValue("echantillonHovQuiverX"))+":"+str(self.getValue("echantillonHovQuiverY"))
                
        return  strData_x+"##"+strData+"##"+strDataOperation_x+"##"+strDataOperation+"##"+strDataConditions+"##"+strDataQuiver

    def dataOperationsToString(self) :
        """
            Retourne les opérations (y compris condition et cumul) sur la data du tracé sous forme de chaine
        """
        strDataCumul = str(self.getValue("cumul"))
        strDataOperation = self.getValue("operation_y")
        strDataOperation_x = self.getValue("operation_x")       
        strExpressionsCondition = ""
        for e in self.expressions_condition :
            strExpressionsCondition = "{}:{}".format(strExpressionsCondition, e["str"])
        strDataRegression = str(self.getValue("regression"))
        strDataFiltrage = str(self.getValue("filtrageConditionnel"))
        return  strDataCumul+"##"+strDataOperation_x+"##"+strDataOperation+"##"+strExpressionsCondition+"##"+strDataRegression+"##"+strDataFiltrage
    
    def getLegendeAida(self):
        """
            Retourne la légende 'aida' correspondant au tracé (tracée en travers sur le côté)
        """
        #data
        strData = ""
        if self.getValue("plateforme") != self.getDefault("plateforme") :
            strData = self.getValue("plateforme")+":"+self.getValue("parametre")
            if self.getValue("operation_y") != self.getDefault("operation_y") :         
                strData += " ("+self.getValue("operation_y")+")"
                
        #data_x
        if self.type == "RDV" :
            plateforme_x = "plateforme"
        else :
            plateforme_x = "plateforme_x"
        strData_x = ""
        if self.getValue(plateforme_x) != self.getDefault(plateforme_x) :
            strData_x = self.getValue(plateforme_x)+":"+self.getValue("parametre_x")
            if self.getValue("operation_x") != self.getDefault("operation_x") :         
                strData_x += " ("+self.getValue("operation_x")+")"
        
        #data RDV : on concatène le paramètre dd et le paramètre ff
        if self.type == "RDV" :
            strLegende = strData_x+"#"+strData   
            
        elif self.type == "PlotXY" :
            strLegende = strData_x+" vs "+strData
            if self.coeff_a != None and self.coeff_b != None and self.coeff_r != None :
                # on concatene la légende de la droite de régression avec ## comme séparateur
                strLegende = strLegende + "##y={:3.4f}x {:+3.4f}  R={:3.2f}".format(self.coeff_a, self.coeff_b, self.coeff_r)
        else :
            strLegende = strData
            
        return strLegende
        
    def getData(self, valx, valy):
        """
        Retourne un tuple avec les valeurs sous la souris selon le type de Trace :
            -ST,PlotXY :  x,y correspondant à la valeur de valx la plus proche sauf en mode découpage.
            -Histo : classe+y correspondant à la valeur de valx la plus proche.
            -Histo3D : x,z correspondant à la valeur de valx la plus proche.
            -RDV : x=secteur de direction en ° correspondant à la valeur de valx, y=liste d'infos sur les classes de vent.
            -Hov : x,y ou y est un dictionnaire contenant la valeur du niveau le plus proche de valy
        """
        # idx est l'indice qui correspond à la valeur de x la plus proche
        x=None
        y=None
        if self.type == "ST" :
            if self.parent.getValue("decoupageActiver") == "oui" :
                if self.parent.getValue("decoupagePeriode") == "j" :
                    nbj = self.parent.getValue("nombreJoursDecoupage")
                    if nbj == 1 :
                        HH = int(valx/3600)
                        MM = int((valx % 3600)/60)
                        x = "{:02d}H{:02d}".format(HH, MM)
                    else :
                        q, r = divmod(valx, (24*3600))
                        q2, r2 = divmod(r, (3600))
                        x = "J{}-{:02d}H{:02d}".format(int(q+1),int(q2), int(r2/60))
                elif self.parent.getValue("decoupagePeriode") == "m" :
                    dd = int(valx/(24*3600)) + 1
                    x = dd
                else :
                    x = int(valx/(24*3600)) +1
                y = valy
            else :
                if self.vecteur_y != None :
                    idx = (np.abs(self.vecteur_y.time_mpl-float(valx))).argmin()
                    x = self.vecteur_y.time[idx]
                    y = self.data_y[idx]
                else :
                    y = "--" # représente une valeur masquée = donnée manquante
        elif self.type == "Histo" :
            xtmp = [ xt for xt in self.bins if xt <= float(valx) ]
            if xtmp != [] and float(valx)<= max(self.bins):
                x = max(xtmp)                
                idx = list(self.bins).index(x)
                try :
                    # on précise la classe à coté de la valeur.
                    right_bracket = '['
                    if idx+2 == len(list(self.bins)) :
                        right_bracket = ']' 
                    chn_x = "\"[{}-{}"+right_bracket+"\".format(list(self.bins)[idx], list(self.bins)[idx+1])"
                    x=""
                    # ordre de grandeur de y
                    counts = self.counts
                    if self.parent.getValue("decoupageActiver") == "oui" : 
                        # self.counts est une liste de array dont le dernier contient le total de chaque bin
                        counts = self.counts[-1]
                    try :
                        odg = abs(int(math.floor(math.log10(abs(counts[idx]-int(counts[idx]))))))+1
                    except : 
                        odg = 0 
                    fmt_y = "{{:0.{}f}}".format(odg)
                    chn_y = "\""+fmt_y+"\".format(counts[idx])"
                    y = eval(chn_x)+" : "+eval(chn_y)                  
                except :
                    y = None
        elif self.type == "Histo3D" :
            xtmp = [ xt for xt in self.parent.bins if xt <= float(valx) ]
            if xtmp != []  and float(valx) <= max(self.parent.bins) :
                x = max(xtmp)                
                idx = list(self.parent.bins).index(x)
                y = self.counts[idx]
        elif self.type == "PlotXY" : # on retourne les valeurs sous le curseur
            x = float(valx)
            y = float(valy)            
        elif self.type == "RDV" : # on retourne les valeurs sous le curseur
            x = int(round(450 - (float(valx)*180/np.pi)))
            if x > 360 :
                x -= 360              
            # on cherche l'indice de la direction dans le tableau des directions
            # on repositionne la 1ere valeur à la fin du tableau
            dir2=self.parent.info_rdv['dir'][1:]
            dir2.append(self.parent.info_rdv['dir'][0])
            trouve = False
            for d in dir2 :
                if d > x :
                    trouve = True
                    break            
            indice = dir2.index(d)
            if indice == len(dir2) - 1  and trouve == False :
                indice = 0
            
            # secteur :
            if indice == len(self.parent.info_rdv['dir'])-1 :
                secteur = (self.parent.info_rdv['dir'][indice], self.parent.info_rdv['dir'][0])
            else :
                secteur = (self.parent.info_rdv['dir'][indice], self.parent.info_rdv['dir'][indice+1])
            x = secteur
            
            y = []
            # nombre de vents pour ce secteur
            total = 0
            for i in self.parent.info_rdv['table'] :
                total += i[indice]
            y.append(total)    
            # classes des ff pour le secteur
            for i in range(len(self.parent.info_rdv['bins'])-2) :
                if total == 0 :
                    pct = 0
                else :
                    pct = self.parent.info_rdv['table'][i][indice]*100/total
                classe = '[{:.1f}-{:.1f}['.format(self.parent.info_rdv['bins'][i], self.parent.info_rdv['bins'][i+1])
                valeur = '{:.1f}%'.format(pct)
                y.append({classe : valeur})
        
        elif self.type == "Hov" :
            if self.vecteur_y != None :
                try :
                    dim_array = AIDA.get_dim_array(self.vecteur_y.attributes["dim_array"])[0]
                except :
                    dim_array = None
                
                if dim_array == 1 : 
                    # Rappel : y est l'heure et x le jour. 
                    # On reconstitue l'heure avec la partie entiere de x et la partie décimale de y.
                    X = int(valx) + valy - int(valy)
                    idx = (np.abs(self.vecteur_y.time_mpl-X)).argmin()
                    x = self.vecteur_y.time[idx]
                    y = self.data_y[idx]
                elif dim_array is None : # on sait pas faire
                    x = "??"
                    y = "??"
                else :
                    idx = (np.abs(self.vecteur_y.time_mpl-float(valx))).argmin()
                    x = self.vecteur_y.time[idx]
                    bornes = self.vecteur_y.bornes
                    idy = (np.abs(bornes[idx][:,0]-float(valy))).argmin()
                    y = {str(bornes[idx][idy]) : self.data_y[idx][idy]}                
            else :
                y = "--" # représente une valeur masquée = donnée manquante   
        else :
            pass
        return x,y    
    
    def doCumul(self):
        """
            Effecture un cumul sur data_y avec ou sans raz sur valeur manquante
        """
        if self.data_y is None :
            return
        cumul = self.getValue("cumul")
        if cumul != 0 :
            if self.data_y[0] is np.ma.masked :
                res_cumul = np.ma.array([np.ma.masked])
                sigma = 0        
            else :
                res_cumul = np.ma.array([self.data_y[0]])
                sigma = self.data_y[0]
            for y in self.data_y[1:] :
                if y is np.ma.masked :
                    if cumul == 2 :
                        sigma = 0
                    res_cumul = np.ma.append(res_cumul, np.ma.masked)
                else :
                    sigma = sigma + y
                    res_cumul = np.ma.append(res_cumul, sigma)
            self.data_y = res_cumul
    
    def doConditions(self):
        """
            Applique les conditions à data_y et remplit self.conditions :
            -1   => data_y ou data_x absent (variables y et x de la condition)
             0   => au moins une des variables de la condition (autre que y et x) est absente
             1   => aucune condition n'est vraie
             n>1 => numéro de la dernière condition qui retourne vrai
        """
        # pour ne pas afficher les warnings numpy quand on a des nans
        np.seterr(invalid='ignore')
        
        if len(self.expressions_condition) < 2 : # tracé non conditionnel
            return
        if self.data_y is None :
            return

        # les variables x et y sont toujours définies (ce sont les données du tracé)
        if self.type == "PlotXY" :
            x = self.data_x
        else :
            x = np.ma.zeros((len(self.data_y),), dtype=np.int)
        y = self.data_y
        
        # par défaut pas de condition => conditions = 1
        self.conditions = np.full(len(self.data_y), 1, dtype=np.int)

        # donnée de base absente => conditions = -1
        self.conditions[(y.mask|x.mask)] = -1
        
        ic = 1
        for cond in self.expressions_condition[1:] :
            # liste des variables de la condition
            str_vars = "x,y"            
            str_tmp = ""
            for car in cond["str"] :
                if car.isalpha() :
                    str_tmp += car
                else :
                    str_tmp += ' '
            liste_variables = [m for m in str_tmp.split(' ') if len(m)==1 and m!='x' and m!='y' ]
            for variable in liste_variables :
                str_vars += ",{}".format(variable)  
       
            var_ok = True
            for var_condition in self.datas_condition_definition :
                try :                           
                    exec("{} = var_condition['vecteur'].data".format(var_condition['nom']))
                except :
                    print(("Erreur Vista : la variable de condition {}={}:{} ne peut pas être évaluée (donnée absente ?)".format(var_condition['nom'], var_condition["plateforme"], var_condition["parametre"])))
                    var_ok = False
            # on vérifie que tous les vecteurs associés aux variables ont la même taille = taille de la data du tracé
            if var_ok :
                for var_condition in self.datas_condition_definition :
                    if var_condition["nom"] in liste_variables :
                        if len(var_condition["vecteur"].data) != len(self.data_y) :
                            print("Erreur Vista : la variable de condition {}={}:{} \
                                   a une taille ({}) différente de la taille ({}) \
                                   de la donnée visualisée {}:{}".format(var_condition['nom'],
                                                                         var_condition["plateforme"],
                                                                         var_condition["parametre"],
                                                                         len(var_condition["vecteur"].data),
                                                                         len(self.data_y),
                                                                         self.getValue("plateforme"),
                                                                         self.getValue("parametre")))
                            var_ok = False
            if not var_ok :
                self.conditions = np.full(len(self.data_y), 0, dtype=np.int)
                break
                
            # Evaluation de la condition
            #
            # donnée de condition absente => conditions = 0 (sauf si conditions = -1)
            filtre = ""
            is_filtre = False
            for variable in liste_variables :
                is_filtre = True
                filtre  = "{}{}.mask|".format(filtre, variable)
            filtre = "({}) & (self.conditions>0)".format(filtre[:-1])
            if is_filtre :
                str_cond = "self.conditions[{}] = 0".format(filtre)
                exec(str_cond)
            
            # mise en forme pour numpy.where
            str_cond_parsed = '('+cond["str"].replace('and', ')&(').replace('or', ')|(')+')'
            # condition remplie => conditions = numéro condition
            indexes = np.array([])
            str_cond = "indexes = np.where({} & (self.conditions>0))\nself.conditions[indexes] = {}".format(str_cond_parsed, ic+1)
            exec(str_cond)
            
            ic = ic+1
            
    def paste(self, obj) :
        """
            Colle un objet dans un Trace.
            L'opération n'est pas permise, retour d'un message d'erreur.
        """
        print("Tenative de coller dans un objet Trace normalement impossible ...")
        return []

