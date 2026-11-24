#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import matplotlib
if not os.environ.get('DISPLAY'):
    matplotlib.use('Agg')
else :
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # @UnresolvedImport @UnusedImport
from matplotlib import lines
from matplotlib import dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import transforms
from matplotlib.ticker import FormatStrFormatter, FuncFormatter
from matplotlib.colors import ColorConverter, ListedColormap, BoundaryNorm, Normalize 
from matplotlib import dates as mpl_dates
from matplotlib.lines import Line2D

import AIDA
from vista.modele import date as vd
import datetime
#try:
#    from PIL import Image
#except ImportError:    
#    import Image
from PIL import Image
import numpy as np
from operator import or_
import gi
gi.require_version('Pango', '1.0')
from gi.repository import Pango as pg
from .vistarose import WindroseAxes
import matplotlib.cm as cm
from matplotlib.collections import LineCollection
from math import sqrt, floor, ceil, log10
import collections

# ATTENTION : la locale LC_NUMERIC=fr_FR pose quelque pb a cfunits :
# -erreur à l'import du module
# -erreurs sur certaines unités du type : 0.0001 volt
# On passe LC_NUMERIC à C
import locale
locale.setlocale(locale.LC_NUMERIC,'C')
try :
    import cfunits
    udunits = True
except :
    udunits = False


"""
    Ce module définit les classes graphiques de vista.
    Ces classes permettent le tracé des différents éléments du document.
    La bibliothèque utilisée est matplotlib.
    Les backends supportés sont : pdf, ps, png, gtk.
    
    -La méthode draw est chargée de construire les éléments graphiques matplotlib correspondant à chaque
    partie du document :
    
    page      <===> figure
    graphique <===> subplot
    tracé     <===> plot
    
    -Mise à jour des graphiques :
    La méthode redraw du document permet de tout retracer. Cette méthode est appelée à chaque modification
    du document (ajout, suppression, insertion d'éléments).
    
"""

"""
##################################### Document
"""
class Gdocument :
    """
        Classe qui définit un graphique 'document'
    """
    
    def __init__(self, document):
        self.id = document.id
        self.zoom = 1 # niveau de zoom (1, 1.1, ..., 1.5)
        self.document = document
        self.gpages = []
        for i in range(0,len(self.document.pages)) :
            self.gpages.append(Gpage(self.document.pages[i], self))
        
        
    def draw(self):
        """
            Crée l'arborescence matplot
        """
        message=""
        for p in range (0, len(self.gpages)) :
            mess = self.gpages[p].draw()
            if mess != "" :
                message += mess+"\n"
        return message
            
        
    def getElementById(self, idElmt): 
        """
            Retourne l'élément du gdocument correpondant à idElmt
        """
        if idElmt == -1 :
            return self
        for p in range (0, len(self.gpages)) :
            if self.gpages[p].id == idElmt :
                return self.gpages[p]
            for g in range (0, len(self.gpages[p].ggraphiques)) :
                if self.gpages[p].ggraphiques[g].id == idElmt :
                    return self.gpages[p].ggraphiques[g]
                for t in range (0, len(self.gpages[p].ggraphiques[g].gtraces)) :
                    if self.gpages[p].ggraphiques[g].gtraces[t].id == idElmt :
                        return self.gpages[p].ggraphiques[g].gtraces[t]
        print(("Erreur : aucun élément avec l'id {} n'a été trouvé dans le document.".format(idElmt)))
        exit(1)

        
    def removeElement(self, idElmt):
        """
            Suppression d'un élément du document
        """
        if idElmt == -1 :
            print("Erreur : la suppression du document est interdite.")
            return False
        for p in range (0, len(self.gpages)) :
            if self.gpages[p].id == idElmt :
                self.gpages.remove(self.gpages[p])
                return True
            for g in range (0, len(self.gpages[p].ggraphiques)) :
                if self.gpages[p].ggraphiques[g].id == idElmt :
                    self.gpages[p].ggraphiques.remove(self.gpages[p].ggraphiques[g])               
                    return True
                for t in range (0, len(self.gpages[p].ggraphiques[g].gtraces)) :
                    if self.gpages[p].ggraphiques[g].gtraces[t].id == idElmt :
                        self.gpages[p].ggraphiques[g].gtraces.remove(self.gpages[p].ggraphiques[g].gtraces[t])
                        return True
        return False
        print(("Erreur : aucun élément graphique avec l'id {} n'a été trouvé dans le document.".format(idElmt)))

    
    def appendNew(self, page):
        """
            Ajoute une nouvelle page au document
        """
        gdocument = self
        gpage = gdocument.fabrique('Page', self, page)
        self.gpages.append(gpage)
        return gpage
    
    def paste(self, obj):
        """
            Colle une page dans le document
        """
        _ = self.appendNew(obj)
        
        
    def redraw(self):
        """
            Recrée l'arborescence matplot après l'avoir nettoyée
        """
        self.clear() 
        message = self.draw()
        return message    

    def clear(self):
        """
            Nettoie l'arborescence matplot
        """
        plt.rcParams['ps.papersize']='A4'
        for p in range (0, len(self.gpages)) :
            if ( self.gpages[p].figure !=  None ) :
                self.gpages[p].figure.clf()
                self.gpages[p].figure = None
                
    def getNumPage(self, idElmt):
        """
            Retourne la page dans laquelle se trouve l'élément
        """
        if idElmt == -1 :
            return 0
        for p in range (0, len(self.gpages)) :
            if self.gpages[p].id == idElmt :
                return p
            for g in range (0, len(self.gpages[p].ggraphiques)) :
                if self.gpages[p].ggraphiques[g].id == idElmt :
                    return p
                for t in range (0, len(self.gpages[p].ggraphiques[g].gtraces)) :
                    if self.gpages[p].ggraphiques[g].gtraces[t].id == idElmt :
                        return p
        raise RuntimeError("Erreur getNumpage : aucun élément avec l'id {} n'a été trouvé dans le document.".format(idElmt))


    def getParent(self, idElmt):
        """
            Retourne l'objet graphique parent de idElement
        """
        if idElmt == -1 :
            return None
        for p in range (0, len(self.gpages)) :
            if self.gpages[p].id == idElmt :
                return self
            for g in range (0, len(self.gpages[p].ggraphiques)) :
                if self.gpages[p].ggraphiques[g].id == idElmt :
                    return self.gpages[p]
                for t in range (0, len(self.gpages[p].ggraphiques[g].gtraces)) :
                    if self.gpages[p].ggraphiques[g].gtraces[t].id == idElmt :
                        return self.gpages[p].ggraphiques[g]
        print(("Erreur : aucun élément graphique avec l'id {} n'a été trouvé dans le document.".format(idElmt)))
        

    def insertElement(self, idElmt, newElmt, before):
        """
            Insere un élément graphique avant (before = True) ou après (before = False) idElmt
        """
        ind = 1
        if before :
            ind = 0
        if idElmt == -1 :
            return None
        parent = self.getParent(idElmt)
        for p in range (0, len(self.gpages)) :
            if self.gpages[p].id == idElmt :
                newGElmt = self.fabrique('Page', parent, newElmt)
                self.gpages.insert(p+ind, newGElmt)                    
                return newGElmt
            for g in range (0, len(self.gpages[p].ggraphiques)) :
                if self.gpages[p].ggraphiques[g].id == idElmt :
                    newGElmt = self.fabrique('Graphique', parent, newElmt)
                    self.gpages[p].ggraphiques.insert(g+ind, newGElmt)
                    # recalcul des positions des graphiques dans la page
                    if self.gpages[p].page.getValue("autoAgencement") == "oui" :
                        self.gpages[p].calculePositionsAuto()
                    else :
                        self.gpages[p].calculePositionManuel(newGElmt)
                        self.gpages[p].agencementValide = False
                    return newGElmt
                for t in range (0, len(self.gpages[p].ggraphiques[g].gtraces)) :
                    if self.gpages[p].ggraphiques[g].gtraces[t].id == idElmt :
                        newGElmt = self.fabrique('Tracé', parent, newElmt)
                        self.gpages[p].ggraphiques[g].gtraces.insert(t+ind, newGElmt)
                        return newGElmt
        print(("Erreur : aucun élément graphique avec l'id {} n'a été trouvé dans le document pour insertion.".format(idElmt)))
        return None
    
        
    def fabrique(self, typeElmt, parent, newElmt):
        """
            fabrique d'objets à partir du type (Page, Graphique ou Tracé)
        """
        if typeElmt == 'Page' :
            return Gpage(newElmt, self)
        if typeElmt == 'Graphique' :
            exec("ggraphique = Ggraphique{}(newElmt, parent)".format(newElmt.type), globals(), locals())
            return locals()["ggraphique"]
        if typeElmt == 'Tracé' :
            exec("gtrace = Gtrace{}(newElmt, parent)".format(newElmt.type), globals(), locals())
            return locals()["gtrace"]
            #return Gtrace(newElmt, self.getParent(idElmtBrother))
        
        return None
    
    
    def exportPdf(self, fichier = None):
        """
            Exporte le document dans un seul pdf
        """
        message = ""
        if fichier is None :
            fic = self.document.getOutputFileName()
        else :
            fic,_ = os.path.splitext(fichier)
            
        ficPdf = "{}.pdf".format(fic)
        try :
            f = open(ficPdf,'w')
            f.close()
        except Exception :
            message = "Impossible d'ouvrir le fichier {} en écriture".format(ficPdf)
            return message
        
        pp = PdfPages("{}.pdf".format(fic))
        self.clear()
        for p in range(0,len(self.gpages)) :
            mess = self.gpages[p].draw(fmt="pdf")
            if mess != "" :
                message += mess+"\n"
            # sauvegarde dans le fichier pdf
            pp.savefig(self.gpages[p].figure, dpi=300, papertype='a4')
        pp.close()
        
        return message
        
        
    def exportPng(self, fichier = None):
        """
            Exporte le document en png : 1 fichier png par page
        """
        message = ""
        self.clear()
        if fichier is None :
            fic = self.document.getOutputFileName()
        else :
            fic,_ = os.path.splitext(fichier)
        
        for p in range(0,len(self.gpages)) :
            mess = self.gpages[p].draw(fmt="png")
            if mess != "" :
                message += mess+"\n"
            if len(self.gpages) == 1 :
                try :
                    f = open("{}.png".format(fic),'w')
                    f.close()
                except Exception :
                    message += "Impossible d'ouvrir le fichier {} en écriture".format("{}.png".format(fic))
                    return message
                plt.savefig("{}.png".format(fic))
            else :
                try :
                    f = open("{}.{}.png".format(fic, p+1),'w')
                    f.close()
                except Exception :
                    message += "Impossible d'ouvrir le fichier {} en écriture".format("{}.{}.png".format(fic, p+1))
                    return message
                plt.savefig("{}.{}.png".format(fic, p+1))
            plt.clf()
        
        return message
            
    
    def exportPs(self, fichier = None):
        """
            Exporte le document en postscript par conversion d'un pdf
        """
        if fichier is None :
            fic = self.document.getOutputFileName()
        else :
            fic,_ = os.path.splitext(fichier)
        # création du pdf
        message = self.exportPdf(fichier)
        if message != "" :
            return message
        ficPdf = "{}.pdf".format(fic)
        try :
            f = open("{}.ps".format(fic),'w')
            f.close()
        except Exception :
            message = "Impossible d'ouvrir le fichier {}.ps en écriture".format(fic)
            return message
        cmd = os.popen("pdftops \"{}\" \"{}.ps\"; rm -f \"{}\"".format(ficPdf, fic, ficPdf))
        cmd.read()
        
        return message
    
    def checkAgencement(self):
        """
            Vérifie que la mise en page de toutes les pages a bien été validée.
            Retourne la liste des pages non validées
        """
        pagesNonValidees = []
        for p in range(0,len(self.gpages)) :
            if not self.gpages[p].agencementValide :
                pagesNonValidees.append(p+1)
        return  pagesNonValidees
                       
class Gpage :
    """
        Classe qui définit un graphique 'page'
    """
    def __init__(self, page, parent):
        self.id = page.id
        self.page = page
        self.parent = parent
        self.ggraphiques = []
        self.figure = None
        self.fmt = "gtk"
        self.agencementValide = True
        for i in range(0,len(self.page.graphiques)) :
            gdocument = self.parent
            ggraphique = gdocument.fabrique('Graphique', self, self.page.graphiques[i])
            self.ggraphiques.append(ggraphique)            
        
    def draw(self, fmt="gtk"):
        """
            Crée la figure matplot correspondant à une page
        """
        #self.figure = plt.figure(self.id,figsize=(8.27,11.69), dpi=100)
        self.fmt = fmt
        self.figure = plt.figure(self.id, dpi=100, linewidth=2, edgecolor='#dddddd')
        if os.environ.get('DISPLAY'):
            # on crée le canvas ici (sauf en mode batch) sinon on peu pas animer Axes3D avec la souris
            self.canvas = FigureCanvas(self.figure)
        
        # les valeurs de xmax et ymax sont fixées pour 100dpi et correpondent à la taille de la
        # fenêtre en pixel.
        if self.page.getValue("orientation") == "portrait" :
            self.figure.set_size_inches(8.27, 11.69)
            if fmt == "gtk" :
                xmax = int(round(481*self.getZoom()))
                ymax = int(round(685*self.getZoom()))
            elif fmt == "pdf" :
                xmax = 2462
                ymax = 3480
                coef_300dpi = 1
            elif fmt == "png" :
                xmax = 827
                ymax = 1169
            marge = 5*xmax/210

        else :
            self.figure.set_size_inches(11.69, 8.27)
            if fmt == "gtk" :
                xmax = int(round(786*self.getZoom()))
                ymax = int(round(552*self.getZoom()))
            elif fmt == "pdf" :
                xmax = 3480
                ymax = 2462
                coef_300dpi = 0.85 #facteur a appliquer en pdf landscape, pas d'explication
            elif fmt == "png" :
                xmax = 1169
                ymax = 827                
            marge = 5*xmax/297
            
        self.ratioPixel = 827*1.0/481 # ration à appliquer aux mesures en pixel pour respecter le wysiwyg (empirique ...)
        # on supprime les marges
        self.figure.subplots_adjust(left=0, bottom=0, right=1, top=1,wspace=0, hspace=0)
        # logo : les valeurs de xmax, ymax servent à positionner le logos. Elles représentent la bbox de la
        # figure et dépendent du format de sortie.
        # En pdf, un calcul empirique est fait pour bien positionner le logo en fonction de sa taille.
        # En gtk, on retaille le logo pour respecter le wysiwyg.
        if self.page.getValue("logo") != "" :
            logo = self.page.parent.logoPath+"/"+self.page.getValue("logo")
            im = Image.open(logo)
            newim = im.convert('RGBA')            
            im = newim
            if fmt == "gtk" :
                rsize = im.resize((int(im.size[0]*self.getZoom()/self.ratioPixel), int(im.size[1]*self.getZoom()/self.ratioPixel)))
                im = rsize
            if fmt == "pdf" :
                # par defaut dpi=100 et on veut 300 dpi pour que le raster soit propre donc on multiplie par 3             
                rsize = im.resize((int(im.size[0]*3*coef_300dpi), int(im.size[1]*3*coef_300dpi)))
                im = rsize
                
            width = im.size[0]
            height = im.size[1]
            
            im = np.array(im).astype(np.float) / 255
            
            #position du logo : on laisse une marge correspondant à 5mm tout autour
            position = self.page.getValue("positionLogo")
            if position == "hg" :
                x = marge
                if fmt == "pdf" :
                    y = ymax - marge - height
                else :
                    y = ymax - marge - height
            elif position == "bg" :
                x = marge
                if fmt == "pdf" :
                    y = marge                   
                else :
                    y = marge
            elif position == "hd" :
                x = xmax - width - marge
                y = ymax - height - marge
            elif position == "bd" :
                x = xmax - width - marge
                y = marge
            origin = 'upper'
            # Code à activer en matploltlib3    
            #origin = 'upper'
            #if fmt != "pdf" :
            #    origin = 'lower'
            self.figure.figimage(im, x, y , origin=origin, zorder=10)

        message =""    
        for g in range (0, len(self.ggraphiques)) :
            mess = self.ggraphiques[g].draw()
            if mess != "" :
                message += mess+"\n"
                 
        #date, numéro de page, fichier de conf
        numPage = self.parent.getNumPage(self.id)+1
        nbPages = len(self.parent.gpages)
        texte = "{}/{}".format(numPage, nbPages)
        size=8
        if fmt == "gtk" :
            size=size*self.getZoom()/self.ratioPixel
        if fmt == "pdf" :
            size = size * coef_300dpi
        self.figure.text(0.5,0.03,texte,size=size,ha='center')
        
        dte = vd.toString(vd.now(), "JJ-MM-AAAA HH:MI")
        texte = "{} {}".format(dte, self.parent.document.fichier)
        size=6
        if fmt == "gtk" :
            size=size*self.getZoom()/self.ratioPixel
        if fmt == "pdf" :
            size = size * coef_300dpi
        self.figure.text(0.5,0.015,texte,size=size,ha='center')
        
        # titre de la page
        if self.page.getValue("titre") != "" :
            (family, size, weight, style) = self.policeToValues(self.page.getValue("policeTitre"))
            if fmt == "gtk" :
                size = (size/self.ratioPixel)*self.getZoom()
            if fmt == "pdf" :
                size = size * coef_300dpi
            plt.suptitle(""+self.page.toTitle(self.page.getValue("titre")), family=family, weight=weight, size=size, style=style, rasterized=True)
            

        return message
     
    def getPosition(self, idGraphique):
        """
            retourne la position du graphique dans le layout
        """
        pos = -1
        for g in range (0, len(self.page.graphiques)) :
            if self.page.graphiques[g].id == idGraphique :
                pos = g
                break
            else :
                pos += 1 
        
        # graphique non trouvé
        if pos == -1 :
            print(("Erreur : le graphique {} n'a pas été trouvé dans la page".format(idGraphique)))
            return (None, None, None, None)
        x = self.page.graphiques[pos].getValue("x")
        if self.page.getValue("autoAgencement") == "oui" :
            # version ancienne, on calcule x,y,width et height
            # marges gauche/droite = 12
            # marges haut/bas = 10
            # espacement inter graphique = 6
            ng = len(self.ggraphiques)
            x = 12 
            width = 76
            height = (80 - ((ng-1)*6))/ng
            if self.page.graphiques[pos].type == "RDV" : # graphique RDV carré
                if self.page.getValue("orientation") == "landscape" :
                    width = int(round(height*(21/29.7)))
                else :
                    width = int(round(height*(29.7/21)))
                    if width > 65 :
                        width = 65
                        height = int(round(width*(21/29.7)))
                
            y = 10 + (pos * (height + 6))
        else :
            x = self.page.graphiques[pos].getValue("x")               
            y = self.page.graphiques[pos].getValue("y")
            width = self.page.graphiques[pos].getValue("width")
            height = self.page.graphiques[pos].getValue("height")
        return (int(x),int(y),int(width),int(height))
    
    def calculePositionsAuto(self):
        """
            Calcule la position de tous les graphiques en mode auto et met à jour le modèle
        """
        for g in self.ggraphiques :
            x,y,w,h = self.getPosition(g.id)
            g.graphique.setPosition(x,y,w,h)
            
    def calculePositionManuel(self, ggraphique):
        """
            Calcule la position d'un graphique en mode manuel et met à jour le modèle.
            Le calcul se fait en fonction de l'index du graphique dans la page.
            On positionne dans une pseudo-grille de 3 lignes * 4 colonnes des graphiques de 25x20
            avec une marge de 5.
        """
        width = 25
        height = 20
        marge = 5
        
        m = (self.ggraphiques.index(ggraphique)) % 3
        x = m*width + (m+1)*marge
        m = ((self.ggraphiques.index(ggraphique)%12)/3)+1
        y = 100 -m*(height+marge)
        ggraphique.graphique.setValue("x", x)
        ggraphique.graphique.setValue("y", y)
        ggraphique.graphique.setValue("width", width)
        ggraphique.graphique.setValue("height", height)
                    
    def getZoom(self):
        """
            Retourne le zoom
        """
        return self.parent.zoom
    
    
    def appendNew(self, graphique):
        """
            Ajoute un nouveau graphique dans la page
        """
        gdocument = self.parent
        ggraphique = gdocument.fabrique('Graphique', self, graphique)
        self.ggraphiques.append(ggraphique)
        # recalcul des positions des graphiques dans la page
        if self.page.getValue("autoAgencement") == "oui" :
            self.calculePositionsAuto()
        else :
            self.calculePositionManuel(ggraphique)
            self.agencementValide = False
            
        return ggraphique
    
    def paste(self, obj):
        """
            Colle un nouveau graphique dans la page
        """
        _ = self.appendNew(obj)
    
                    
    def mmToRatio(self, mm, orientation, sens):
        """
            Convertit des mm en "ration de figure", entre 0 et 1
        """       
        if sens == "h" : #horizontal
            if orientation == "landscape" :
                r =  mm/297.0
            else :
                r = mm/210.0
        else : # vertical
            if orientation == "landscape" :
                r =  mm/210.0
            else :
                r = mm/297.0
        return r
    
    def ratioToMm(self, ratio, orientation, sens):
        """
            Convertit un "ration de figure", entre 0 et 1, en mm
        """       
        if sens == "h" : #horizontal
            if orientation == "landscape" :
                mm =  ratio*297.0
            else :
                mm = ratio*210.0
        else : # vertical
            if orientation == "landscape" :
                mm =  ratio*210.0
            else :
                mm = ratio*297.0
        return mm
    
    def policeToValues(self, police) :
        """
            Décortique une police de caractères
        """
        police = pg.FontDescription(police)
        
        family = police.get_family()
                
        size = police.get_size()/1024
        
        if police.get_weight() == pg.Weight.BOLD :
            weight = "bold"
        elif police.get_weight() == pg.Weight.HEAVY :
            weight = "heavy"
        elif police.get_weight() == pg.Weight.LIGHT :
            weight = "light"
        elif police.get_weight() == pg.Weight.ULTRABOLD :
            weight = "ultrabold"
        elif police.get_weight() == pg.Weight.ULTRALIGHT :
            weight = "ultralight"
        else :
            weight = "normal"
        
        if police.get_style() == pg.Style.ITALIC :
            style = "italic"
        elif police.get_style() == pg.Style.OBLIQUE :
            style = "oblique"
        else :
            style = "normal"
        
        return (family, size, weight, style)
    
class Ggraphique() :
    """
        Classe qui définit un graphique 'graphique'
    """
    def __init__(self, graphique, parent):
        self.id = graphique.id
        self.graphique = graphique
        self.parent = parent
        self.gtraces = []
        self.subplot = None
        self.axes_gauche = []
        self.axes_droit = []
        self.unites = [] #unites abscisses gauche et droite
        for i in range(0,len(self.graphique.traces)) :
            exec("gtrace = Gtrace{}(self.graphique.traces[i], self)".format(self.graphique.traces[i].type), globals(), locals())
            self.gtraces.append(locals()["gtrace"])
        self.button_down = False #bouton de la souris enfoncé sur le graphique
        self.x_click = 0 #abscisse du clic
        self.y_click = 0 #ordonnée du clic
        # colormap RDV : correspondance avec le tableau couleursRDV de vista.py
        self.couleursRDV = [cm.afmhot, cm.autumn, cm.bone, cm.cool, cm.copper, cm.gist_heat, cm.gray, cm.hot, cm.pink, cm.spring, cm.summer, cm.winter, cm.rainbow]#@UndefinedVariable
        self.couleursRDVReverse = [cm.afmhot_r, cm.autumn_r, cm.bone_r, cm.cool_r, cm.copper_r, cm.gist_heat_r, cm.gray_r, cm.hot_r, cm.pink_r, cm.spring_r, cm.summer_r, cm.winter_r, cm.rainbow_r]#@UndefinedVariable
        self.couleursHov = [cm.rainbow,cm.afmhot, cm.autumn, cm.bone, cm.cool, cm.copper, cm.gist_heat, cm.gray, cm.hot, cm.pink, cm.spring, cm.summer, cm.winter]#@UndefinedVariable
        self.couleursHovReverse = [cm.rainbow_r,cm.afmhot_r, cm.autumn_r, cm.bone_r, cm.cool_r, cm.copper_r, cm.gist_heat_r, cm.gray_r, cm.hot_r, cm.pink_r, cm.spring_r, cm.summer_r, cm.winter_r]#@UndefinedVariable
        self.couleursDecoupage = [cm.rainbow,cm.afmhot, cm.autumn, cm.bone, cm.cool, cm.copper, cm.gist_heat, cm.gray, cm.hot, cm.pink, cm.spring, cm.summer, cm.winter]#@UndefinedVariable
        self.couleursDecoupageReverse = [cm.rainbow_r,cm.afmhot_r, cm.autumn_r, cm.bone_r, cm.cool_r, cm.copper_r, cm.gist_heat_r, cm.gray_r, cm.hot_r, cm.pink_r, cm.spring_r, cm.summer_r, cm.winter_r]#@UndefinedVariable

    def appendNew(self, trace):
        """
            Ajoute un nouveau tracé dans le graphique
        """
        gdocument = self.parent.parent
        gtrace = gdocument.fabrique('Tracé', self, trace)
        self.gtraces.append(gtrace)
        

        return gtrace
    
    def paste(self, obj):
        """
            Colle un nouveau tracé dans le graphique
        """
        _ = self.appendNew(obj)
            
    def draw(self):
        """
            Crée le subplot matplot correspondant à un graphique
        """
        raise NotImplementedError("Vous devez implémenter la méthode draw de la classe Ggraphique.")
        
    def draw_titre(self) :
        """
            Trace le titre du graphique
        """
        if self.graphique.getValue("titre") != "" :
            (family, size, weight, style) = self.parent.policeToValues(self.graphique.getValue("policeTitre"))
            if self.parent.fmt == "gtk" :
                size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
            
            plt.title(""+self.graphique.toTitle(self.graphique.getValue("titre")), family=family, weight=weight, size=size, style=style, rasterized=True)

    def draw_ticks_labels_units_grid(self) :
        """
            Affichage des labels, des ticks, de la grille et des unités
        """
        ax = self.subplot
        if self.graphique.getValue("grille") == "oui" :
            onTraceGrille = True
        else :
            onTraceGrille = False
        try :
            ax.ticklabel_format(axis='y', useOffset=False) # interdit les notation du type +1.011e3
            ax.ticklabel_format(axis='x', useOffset=False) 
        except :
            pass # compatible uniquement avec ScalarFormatter       
        size=2
        labelsize=8
        pad=2
        #to_percent = lambda y, pos: str(100 * y)
        to_percent = lambda y, pos: "{:0.1f}".format(100 * y)
        if self.parent.fmt == "gtk" :
            labelsize = np.round(labelsize*self.parent.getZoom()/self.parent.ratioPixel,5)
            pad = np.round(pad*self.parent.getZoom()/self.parent.ratioPixel,5)
            size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
        if self.graphique.type == "Histo3D" :
            unit = "nombre"
            if self.graphique.getValue("norme") == "oui" :
                unit = "pourcents"
                formatter = FuncFormatter(to_percent)
                ax.zaxis.set_major_formatter(formatter)
            ax.set_zlabel(unit, size=labelsize)
        else :
            self.subplot.xaxis.set_tick_params(size=size, which='both', direction='out', labelsize=labelsize, pad=pad)
            for axe_info in self.axes_gauche :
                unit = axe_info[1]
                try :
                    axe_info[0].ticklabel_format(axis='y', useOffset=False)
                    axe_info[0].ticklabel_format(axis='x', useOffset=False)
                except :
                    pass # compatible uniquement avec ScalarFormatter
                axe_info[0].yaxis.set_visible(True)
                axe_info[0].yaxis.set_tick_params(size=size, which='both', direction='out', labelsize=labelsize, pad=pad)
                if self.graphique.type == "Histo" :
                    axe_info[0].xaxis.set_visible(True)
                    axe_info[0].xaxis.set_tick_params(size=size, which='both', direction='out', labelsize=labelsize, pad=pad)
                if self.graphique.getValue("uniteGauche") == "oui" :
                    onTraceUnite = True
                else :
                    onTraceUnite = False
                if self.graphique.getValue("labelsGauche") == "oui" :
                    onTraceLabels = True
                else :
                    onTraceLabels = False
                if self.graphique.type == "Histo" :
                    unit = "nombre"
                    if self.graphique.getValue("norme") == "oui" :
                        unit = "pourcents"
                        formatter = FuncFormatter(to_percent)
                        axe_info[0].yaxis.set_major_formatter(formatter)
                if onTraceUnite :
                    axe_info[0].set_ylabel(unit, size=labelsize)
                if not onTraceLabels :
                    axe_info[0].set_yticklabels([])
                if onTraceGrille :
                    axe_info[0].grid(onTraceGrille, linestyle=(0,(1,3)))
                else :
                    axe_info[0].grid(onTraceGrille)
            for axe_info in self.axes_droit :
                unit = axe_info[1]
                try :
                    axe_info[0].ticklabel_format(axis='y', useOffset=False)
                    axe_info[0].ticklabel_format(axis='x', useOffset=False)
                except :
                    pass # compatible uniquement avec ScalarFormatter
                axe_info[0].yaxis.set_visible(True)
                axe_info[0].yaxis.set_tick_params(size=size, which='both', direction='out', labelsize=labelsize, pad=pad)
                if self.graphique.type == "Histo" :
                    axe_info[0].xaxis.set_visible(True)
                    axe_info[0].xaxis.set_tick_params(size=size, which='both', direction='out', labelsize=labelsize, pad=pad)
                if self.graphique.getValue("uniteDroite") == "oui" :
                    onTraceUnite = True
                else :
                    onTraceUnite = False
                if self.graphique.getValue("labelsDroite") == "oui" :
                    onTraceLabels = True
                else :
                    onTraceLabels = False
                if self.graphique.type == "Histo" :
                    unit = "nombre"
                    if self.graphique.getValue("norme") == "oui" :
                        unit = "pourcents"
                        formatter = FuncFormatter(to_percent)
                        axe_info[0].yaxis.set_major_formatter(formatter)
                if onTraceUnite :
                    axe_info[0].set_ylabel(unit, size=labelsize)
                if not onTraceLabels :
                    axe_info[0].set_yticklabels([])
                if onTraceGrille :
                    axe_info[0].grid(onTraceGrille, linestyle=(0,(1,3)))
                else :
                    axe_info[0].grid(onTraceGrille) 

        # labels, ticks, unites axe du bas pour PlotXY
        if  self.graphique.type == "PlotXY":
            if self.graphique.getValue("uniteBas") == "oui" :
                try :
                    unit = self.gtraces[0].trace.vecteur_x.attributes['unit']
                except :
                    unit = "unknow"
                ax.set_xlabel(unit, size=labelsize)
            if self.graphique.getValue("labelsBas") == "non" :
                ax.set_xticklabels([])
        
        # graphiques sans tracés        
        if len(self.axes_gauche) == 0 and len(self.axes_droit) == 0 :    
            plt.gca().xaxis.set_tick_params(size=size, which='both', direction='out', labelsize=labelsize, pad=pad)
       
        # unités et grille pour hovmoller
        """
        if self.graphique.type == "Hov" :
            if onTraceGrille :
                plt.gca().grid(onTraceGrille, linestyle=(0,(1,3)))
            else :
                plt.gca().grid(onTraceGrille)
        """
    
        # formatter des ticks label
        if self.graphique.type == "ST" or self.graphique.type == "Hov" :
            if self.graphique.getValue("decoupageActiver") == "oui" :                      
                if self.graphique.getValue("decoupagePeriode") == "j" :
                    nbj = self.graphique.getValue("nombreJoursDecoupage")
                    if nbj == 1 :
                        plt.gca().set_xticks( list(range(0,86400,2*3600)) )
                        plt.gca().set_xticklabels( [ "{:02d}h".format(x) for x in range(0,24,2)] )
                    else :
                        plt.gca().set_xticks( list(range(0,86400*nbj,24*3600)) )
                        plt.gca().set_xticklabels( [ "J{}".format(x) for x in range(1,nbj+1)] )
                elif self.graphique.getValue("decoupagePeriode") == "m" :
                    plt.gca().set_xticks( list(range(0,31*86400,86400*2)) )
                    plt.gca().set_xticklabels( [ "{:02d}".format(x) for x in range(1,32,2)] )
                else :
                    plt.gca().set_xticks(np.cumsum(np.array([0,29,31,30,31,30,31,31,30,31,30,31])*86400))
                    plt.gca().set_xticklabels( ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jui', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec'] )
            else :
                locator = mdates.AutoDateLocator()
                formatter = mdates.ConciseDateFormatter(locator, show_offset=False)
                plt.gca().xaxis.set_major_locator(locator)
                plt.gca().xaxis.set_major_formatter(formatter)
                plt.gca().set_xlabel("Time", size=labelsize)

        elif self.graphique.type == "Histo" :
            try :
                bins, fmt = self.getBins()
                ax.set_xticks(bins)
                ax.xaxis.set_major_formatter(FormatStrFormatter(fmt))
                # Tracé des labels de pourcentage sous les bins : on est obligé de boucler sut les tracés
                for t in self.gtraces :
                    bin_centers = 0.5 * np.diff(t.trace.bins) + t.trace.bins[:-1]
                    counts = t.trace.counts
                    if isinstance(counts, list) : # découpage en périodes, le dernier élément contient le total de chaque période
                        counts = t.trace.counts[-1]
                    for count, x in zip(counts, bin_centers):
                        if t.trace.getValue("labelNombreHisto") == "oui" :
                            # Label du nombre d'éléments dans la classe
                            y = np.round(-28*self.parent.getZoom()/self.parent.ratioPixel,5)
                            # Si le graphique est normé il faut recalculer le nombre d'éléments par classe
                            if self.graphique.getValue("norme") == "oui" :
                                ax.annotate(str(int(round(count*len(t.trace.data_y)))), xy=(x, 0), xycoords=('data', 'axes fraction'),
                                            xytext=(0, y), textcoords='offset points', va='top', ha='center', size=labelsize)
                            else :
                                ax.annotate(str(int(count)), xy=(x, 0), xycoords=('data', 'axes fraction'),
                                            xytext=(0, y), textcoords='offset points', va='top', ha='center', size=labelsize)
                        if t.trace.getValue("labelPourcentHisto") == "oui" :
                            # Label du pourcentage d'éléments dans la classe
                            y = np.round(-38*self.parent.getZoom()/self.parent.ratioPixel,5)
                            if self.graphique.getValue("norme") == "oui" :
                                percent = '%0.0f%%' % (100 * float(count))
                            else :
                                percent = '%0.0f%%' % (100 * float(count) / counts.sum())
                            ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
                                xytext=(0, y), textcoords='offset points', va='top', ha='center', size=labelsize)
                # affichage ticks et unité
                if self.graphique.getValue("uniteBas") == "oui" :
                    try :
                        unit = self.gtraces[0].trace.vecteur_y.attributes['unit']
                    except :
                        unit = "unknow"
                    ax.set_xlabel(unit, size=labelsize)
                if self.graphique.getValue("labelsBas") == "non" :
                    ax.set_xticks([])
            except :
                pass
        #rotation des labels : plt.xticks(rotation='vertical') ne marche pas quand on a plusieurs axes.
        plt.setp( ax.xaxis.get_majorticklabels(), rotation=90 )
            
    def draw_legende(self) :
        """
            Affiche la légende
        """
        if self.graphique.getValue("legendeVisible") == "oui" :
            ax = self.subplot
            handls = []
            lbls = []
            # on récupère la légende des tracés dans tous les cas : avec conditions la légende est positionnée à '' et donc pas tracée.            
            if self.graphique.getValue("decoupageActiver") == "oui" :
                for gt in self.gtraces :
                    for label, couleur in self.get_couleurs_decoupage().items() :
                        leg = Line2D([], [], color=couleur, linestyle=gt.trace.getValue("typeLigne"), linewidth=gt.trace.getValue("epaisseur"), marker=gt.trace.getValue("marqueur"), markersize=sqrt(gt.trace.getValue("epaisseur")),markeredgewidth=0 )
                        handls.append(leg)
                        if self.graphique.getValue("nombreJoursDecoupage") == 1 :
                            lbls.append(""+ label.split(':')[0])
                        else :
                            lbls.append(""+ label)
            else :
                for axe_info in self.axes_gauche :
                    axe = axe_info[0]
                    handles, labels = axe.get_legend_handles_labels()
                    handls.extend(handles)
                    lbls.extend(labels)
                    break # un seul axe à gauche, le subplot                   
                for axe_info in self.axes_droit :
                    axe = axe_info[0]
                    handles, labels = axe.get_legend_handles_labels()
                    handls.extend(handles)
                    lbls.extend(labels)
                
            # on ajoute celles des tracés conditionnels sauf pour Histo
            if self.graphique.type != "Histo" :
                for gt in self.gtraces :
                    if len(gt.trace.expressions_condition) > 1 : # tracé conditionnel
                        if gt.trace.getValue("legendeVisible") == "oui" : # légende du tracé                   
                            leg = Line2D([], [], color=gt.trace.getValue("couleur"), linestyle=gt.trace.getValue("typeLigne"), linewidth=gt.trace.getValue("epaisseur"), marker=gt.trace.getValue("marqueur"), markersize=sqrt(gt.trace.getValue("epaisseur")),markeredgewidth=0 )
                            handls.append(leg)
                            lbls.append(""+ gt.trace.getValue("legende"))
                        if gt.trace.type == "PlotXY" and gt.trace.getValue("filtrageConditionnel") == "oui" :
                            for c in gt.trace.expressions_condition[1:] : # légende des conditions sauf non résolue
                                if c["legendeVisible"] == "oui" :
                                    leg = Line2D([], [], color=c["couleur"], linestyle=gt.trace.getValue("typeLigne"), linewidth=c["epaisseur"], marker=gt.trace.getValue("marqueur"), markersize=sqrt(c["epaisseur"]), markeredgewidth=0)
                                    handls.append(leg)
                                    lbls.append(""+c["legende"])
                        else :
                            for c in gt.trace.expressions_condition : # légende des conditions
                                if c["legendeVisible"] == "oui" :
                                    leg = Line2D([], [], color=c["couleur"], linestyle=gt.trace.getValue("typeLigne"), linewidth=c["epaisseur"], marker=gt.trace.getValue("marqueur"), markersize=sqrt(c["epaisseur"]), markeredgewidth=0)
                                    handls.append(leg)
                                    lbls.append(""+c["legende"])
            
            (family, fontsize, weight, style) = self.parent.policeToValues(self.graphique.getValue("policeLegende"))
            if self.parent.fmt == "gtk" :
                    fontsize = np.round(fontsize*self.parent.getZoom()/self.parent.ratioPixel,5)
            loc = self.graphique.getValue("positionLegende").split(',')
            if int(loc[0]) == 0 : # best
                bbox_to_anchor = None
            else :
                bbox_to_anchor=(float(loc[1])+float(loc[3]), float(loc[2])+float(loc[4]))
            
            # nombre de colonnes de la légende
            nbcol = self.graphique.getValue("ncolLegende")
            leg = ax.legend(handls, lbls, prop={'size':fontsize, 'family':family, 'weight':weight, 'style':style}, loc=int(loc[0]), bbox_to_anchor=bbox_to_anchor, ncol=nbcol)
                            
    def draw_courbes(self) :
        """
            Trace les courbes de chaque tracé du graphique
        """
        ax = self.subplot
        message = ""
        for t in range (0, len(self.gtraces)) :
            mess = self.gtraces[t].draw()
            if mess != "" :
                message += mess+"\n"
        if message != "" :
            size = 12
            horizontalalignment = 'center'
            if self.parent.fmt == "gtk" :
                size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
                horizontalalignment='center'
            x1 = (ax.bbox.xmax + ax.bbox.xmin)/self.parent.figure.bbox.xmax/2
            y1 = (ax.bbox.ymin + ax.bbox.ymax)/self.parent.figure.bbox.ymax/2        
            plt.figtext(x1,y1, message, transform=self.parent.figure.transFigure, figure=self.parent.figure, size=size, horizontalalignment=horizontalalignment, verticalalignment='bottom', rasterized=True)    
        return message

    def draw_legende_aida(self) :
        """
            Trace la légende aida (nom des vecteurs sur le côté en travers, ou en dessous pour PlotXY)
        """
        ax = self.subplot
        if self.graphique.getValue("legendeAida") == "oui" :
            n = 1
            for t in self.graphique.traces :
                texte = t.getLegendeAida()
                size = 6
                if self.parent.fmt == "gtk" :
                    size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
                couleur = t.getValue("couleur")
                if t.type == "PlotXY" :
                    txt = texte.split("##")
                    texte = "".join(txt[:-1])
                    x1 = ax.bbox.xmin/self.parent.figure.bbox.xmax + 0.02
                    y1 = ax.bbox.ymin/self.parent.figure.bbox.ymax - 0.01*n
                    horizontalalignment = 'left'
                    verticalalignment = 'center'
                    rotation = 0
                    delta_x = 0
                    delta_y = -0.03
                    l1 = lines.Line2D([x1 - 0.01, x1 - 0.002], [y1+delta_y , y1+delta_y],
                           transform=self.parent.figure.transFigure, 
                           figure=self.parent.figure, 
                           color=couleur, 
                           ls=t.getValue("typeLigne"),
                           ms = size/3,
                           marker = t.getValue("marqueur"),
                           mfc = t.getValue("couleur"),
                           mec = t.getValue("couleur"),
                           rasterized=True)
                else :
                    x1 = ax.bbox.xmax/self.parent.figure.bbox.xmax + 0.01*n
                    y1 = ax.bbox.ymin/self.parent.figure.bbox.ymax
                    horizontalalignment = 'center'
                    verticalalignment = 'bottom'
                    rotation = 90
                    delta_x = 0
                    delta_y = 0.015
                    l1 = lines.Line2D([x1, x1], [y1, y1+0.01],
                           transform=self.parent.figure.transFigure, 
                           figure=self.parent.figure, 
                           color=couleur, 
                           ls=t.getValue("typeLigne"),
                           ms = size/3,
                           marker = t.getValue("marqueur"),
                           mfc = t.getValue("couleur"),
                           mec = t.getValue("couleur"),
                           rasterized=True)
                
                self.parent.figure.lines.extend([l1])
                    
                plt.figtext(x1+delta_x, y1+delta_y,texte, size=size, horizontalalignment=horizontalalignment, verticalalignment=verticalalignment, rotation=rotation, color=couleur, rasterized=True)
                n = n+1
                
    def draw_jour_nuit(self) :
        """
            jour / nuit : on le trace systématiquement, visible ou non. Ca permet d'avoir toute la période
            sur l'axe des abscisses même si les données sont manquantes en début ou fin de période
        """
        ax = self.subplot
        debut = self.graphique.parent.parent.dateDebut
        fin = self.graphique.parent.parent.dateFin
        if self.graphique.getValue("decoupageActiver") ==  "oui" :
            if self.graphique.getValue("decoupagePeriode") == "j" :
                nbj = self.graphique.getValue("nombreJoursDecoupage")
                xmin,xmax = 0, 86400*nbj
                x = []
                y = []
                for i in range(nbj+1) :
                    x.append(24*3600*i)                  
                    y = [1]
                width = 43200
            elif self.graphique.getValue("decoupagePeriode") == "m" :
                xmin,xmax = 0, 86400*31
                x = [43200]
                y = [1]
                width = 43200
            else :
                xmin,xmax = 0, 86400*366
                x = [43200]
                y = [1]
                width = 43200
            # on affiche jour/nuit que si la période de découpage == jour
            if self.graphique.getValue("jourNuit") == "oui" and self.graphique.getValue("decoupagePeriode") == 'j' and not self.graphique.type == "Hov" :
                valpha = 0.2
            else :
                valpha = 0.0
        else :
            width = 0.5
            nbjours = vd.duree(debut, fin)
            if self.graphique.getValue("jourNuit") == "oui" and nbjours < 90 and not self.graphique.type == "Hov" :
                valpha = 0.2
            else :
                valpha = 0.0                  
            x = []
            y = []
            for i in range(nbjours+1) :
                d = vd.toDate(debut) + datetime.timedelta(days=1)*i
                x.append(d)
                y.append(1)
                
            if self.graphique.getValue("fitData") != self.graphique.getDefault("fitData") :
                xmin,xmax = self.getDateMinMax()
                if xmin is None or xmax is None :
                    xmin,xmax = x[0], x[len(x)-1]
            else :
                xmin,xmax = x[0], x[len(x)-1]
        
        ax.set_xlim(xmin, xmax) #on force xlim sinon ca plante en mpl1.3 ...

        trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
        ax.bar(x, y, width=width, align="center", transform=trans, alpha=valpha, color='grey', linewidth=0, rasterized=False)        
        
        if self.graphique.getValue("decoupageActiver") ==  "non" :
            # ombrage des années (au dela de 3 ans) et des mois (au dela de 3 mois)
            ombrage = True
            l2 = vd.getListeAns(debut, fin)
            if len(l2) < 3 :
                l2 = vd.getListeMois(debut, fin)
                if len(l2) < 3 :
                    ombrage = False
            if self.graphique.getValue("moisAnnees") != "oui" and not self.graphique.type == "Hov" :
                ombrage = False
            if ombrage :
                for i in range(len(l2)) :
                    x = l2[i:(i+1)]
                    y = [1]
                    if i == len(l2)-1 :
                        diff = vd.toDate(fin) - l2[i]
                        width = diff.days +1
                    else :
                        diff = l2[i+1] - l2[i]
                        width = diff.days
                    
                    if i%2 == 0 :
                        valpha = 0.2
                    else :
                        valpha = 0.0
                    ax.bar(x, y, width=width, align="edge", transform=trans, color='#c2aaee', alpha=valpha, linewidth=0, rasterized=False)

    def def_unit_axis(self) :
        """
            Définit les axes avec leurs unités en fonction des tracés que contient le graphique sauf pour Histo3D
        """             
        if  self.graphique.type != "Histo3D" :           
            self.axes_gauche = [] #liste contenant les axes à gauche
            self.axes_droit = [] #liste contenant les axes à droite
            # on positionne les axes des tracés non auto
            unites_a_gauche = []
            unites_a_droite = []
            for t in range (0, len(self.gtraces)) :
                if self.gtraces[t].trace.vecteur_y != None :
                    if self.gtraces[t].trace.type == "Hov" :
                        self.gtraces[t].trace.setValue("axe_y", 0)
                        try :
                            unite = self.gtraces[t].trace.vecteur_y.attributes["unit_bornes"]
                        except :
                            unite = "HH:MM"
                    else :
                        unite = self.gtraces[t].trace.vecteur_y.attributes['unit']
                    
                    if self.gtraces[t].trace.getValue("cumul") > 0:
                        unite += "*s"
                    #TODO : utiliser udunits
                    if unite.lower() == "degres" :
                        unite = "degree"
                    if unite.lower() == "celsius" :
                        unite = "celsius"
                    if unite.lower() == "pourcent" :
                        unite = "percent"
                    
                    axe_y = self.gtraces[t].trace.getValue("axe_y")
                    
                    if axe_y == 0 : # à gauche
                        found, unit = self.unit_exists(unite, unites_a_gauche)
                        if found :
                            self.gtraces[t].axe_y = [ axe[0] for axe in self.axes_gauche if axe[1]==unit ][0]
                        else :                          
                            self.gtraces[t].axe_y = self.subplot
                            unites_a_gauche.append(unit)
                            self.axes_gauche.append((self.gtraces[t].axe_y, unit))   
                    elif axe_y == 1 : # à droite
                        found, unit = self.unit_exists(unite, unites_a_droite)
                        if found :
                            self.gtraces[t].axe_y = [ axe[0] for axe in self.axes_droit if axe[1]==unit ][0]
                        else :
                            self.gtraces[t].axe_y = self.subplot.twinx()
                            unites_a_droite.append(unit)
                            self.axes_droit.append((self.gtraces[t].axe_y, unit))           
            # on positionne les axes des tracés auto
            for t in range (0, len(self.gtraces)) :
                if self.gtraces[t].trace.vecteur_y != None :
                    if self.gtraces[t].trace.type == "Hov" :
                        self.gtraces[t].trace.setValue("axe_y", 0)
                        try :
                            unite = self.gtraces[t].trace.vecteur_y.attributes["unit_bornes"]
                        except :
                            unite = "HH:MM"
                    else :
                        unite = self.gtraces[t].trace.vecteur_y.attributes['unit']
                    
                    if self.gtraces[t].trace.getValue("cumul") > 0:
                        unite += "*s"
                    #TODO : utiliser udunits
                    if unite.lower() == "degres" :
                        unite = "degree"
                    if unite.lower() == "celsius" :
                        unite = "celsius"
                    if unite.lower() == "pourcent" :
                        unite = "percent"
                    
                    axe_y = self.gtraces[t].trace.getValue("axe_y")
                    if axe_y == 2 :
                        found_left, unit_left = self.unit_exists(unite, unites_a_gauche)
                        found_right, unit_right = self.unit_exists(unite, unites_a_droite)
                        if found_left :
                            self.gtraces[t].axe_y = [ axe[0] for axe in self.axes_gauche if axe[1]==unit_left ][0]
                        elif found_right :
                            self.gtraces[t].axe_y = [ axe[0] for axe in self.axes_droit if axe[1]==unit_right ][0]
                        else : 
                            if len(unites_a_gauche) == 0 :                          
                                self.gtraces[t].axe_y = self.subplot
                                unites_a_gauche.append(unite)
                                self.axes_gauche.append((self.gtraces[t].axe_y, unite))
                            else:
                                self.gtraces[t].axe_y = self.subplot.twinx()
                                unites_a_droite.append(unite)
                                self.axes_droit.append((self.gtraces[t].axe_y, unite))
            if len(unites_a_gauche) == 0 :
                self.subplot.yaxis.set_visible(False)
                
    def unit_exists(self, unit, unit_list):
        """
            Recherche si une unité existe dans une liste :
            - si udunits, on recherche une unité égale
            - retourne un tuple (found(boolean), unit(str))
        """
        if udunits :
            found = False
            try :
                utmp = cfunits.Units(unit)
                for u in unit_list :
                    utmp2 = cfunits.Units(u)
                    if utmp.equals(utmp2) :
                        found = True
                        unit = u
                        break
                return (found, unit)
            except :
                if unit in unit_list :
                    return(True, unit)
                else :
                    return(False, unit)
        else :
            if unit in unit_list :
                return(True, unit)
            else :
                return(False, unit)
    
    def getMinMax(self):
        """
            Retourne les valeurs minimales des datas contenues dans le graphique.
        """
        mins = []
        maxs = []
        
        for t in self.gtraces :
            try :
                mins.append(np.ma.min(t.trace.data_y))
            except :
                pass
            try :
                maxs.append(np.ma.max(t.trace.data_y))
            except :
                pass
        try :
            mini = min(mins)
        except :
            mini = None
        try :
            maxi = max(maxs)
        except :
            maxi = None
        return mini, maxi

    def set_amplitude_axes(self) :
        """
           Positionne l'amplitude sur les axes droit et gauche
        """
        # amplitude sur l'axe des ordonnées de gauche
        ax = self.subplot
        if self.graphique.getValue("echelle") == "auto" :
            amplitude = self.graphique.getValue("echelleAmplitude")
            if amplitude != 0 :
                limites = ax.get_ylim()     
                ymin = (limites[0]+limites[1])/2. - (amplitude/2.)
                ymax = (limites[0]+limites[1])/2. + (amplitude/2.)
                ax.set_ylim([ymin, ymax])
        else :
            ymin = self.graphique.getValue("echelleMin")
            ymax = self.graphique.getValue("echelleMax")          
            ax.set_ylim([ymin, ymax])
            
        # amplitude sur l'axe des ordonnées de droite
        try :
            ax = self.axes_droit[0][0]
            if self.graphique.getValue("echelleDroite") == "auto" :
                    amplitude = self.graphique.getValue("echelleAmplitudeDroite")
                    if amplitude != 0 :
                        limites = ax.get_ylim()     
                        ymin = (limites[0]+limites[1])/2. - (amplitude/2.)
                        ymax = (limites[0]+limites[1])/2. + (amplitude/2.)
                        ax.set_ylim([ymin, ymax])
            else :
                ymin = self.graphique.getValue("echelleMinDroite")
                ymax = self.graphique.getValue("echelleMaxDroite")          
                ax.set_ylim([ymin, ymax])
        except :
            pass
        
    def set_echelle_log(self) :
        """        
            Positionne l'échelle logarithmique s'il y a lieu
        """
        ax = self.subplot
        if self.graphique.getValue("echelleLogBas") == "oui" :
            ax.semilogx()
        if self.graphique.getValue("echelleLogGauche") == "oui" :
            ax.semilogy()
        if self.graphique.getValue("echelleLogDroite") == "oui" :
            ax = self.axes_droit[0][0]
            ax.semilogy()

        
    def get_couleurs_decoupage(self) :
        """
            Retourne un dict qui associe chaque période de découpage et une couleur
        """
        odeb = int(mpl_dates.date2num(vd.toDate(self.graphique.parent.parent.dateDebut)))
        ofin = int(mpl_dates.date2num(vd.toDate(self.graphique.parent.parent.dateFin)))
        odate = odeb
        labels = []
        nj = 0
        while odate <= ofin :
            if self.graphique.getValue("decoupagePeriode") == "j" :
                nbj = self.graphique.getValue("nombreJoursDecoupage")
                if nj == 0 :
                    label = mpl_dates.num2date(odate).strftime("%Y-%m-%d")+":"+mpl_dates.num2date(odate+nbj-1).strftime("%Y-%m-%d")
                if nj == nbj-1 :
                    nj = 0
                else :
                    nj = nj+1
            elif self.graphique.getValue("decoupagePeriode") == "m" :
                label = mpl_dates.num2date(odate).strftime("%Y-%m")
            else:
                label = mpl_dates.num2date(odate).strftime("%Y")
            if not label in labels :
                labels.append(label)
            odate += 1
            
        if self.graphique.getValue("reversePaletteDecoupage") == "oui" :
            palette_couleur = self.couleursDecoupageReverse[self.graphique.getValue("couleurDecoupage")]
        else :
            palette_couleur = self.couleursDecoupage[self.graphique.getValue("couleurDecoupage")]
        cNorm  = Normalize(vmin=0, vmax=len(labels)-1)
        scalarMap = cm.ScalarMappable(norm=cNorm, cmap=palette_couleur)
        
        couleurs_decoupage = {}
        ic = 0
        for l in labels :
            couleurs_decoupage[l] = scalarMap.to_rgba(ic)
            ic += 1
            
        return couleurs_decoupage

    def getDateMinMax(self):
        """
            Retourne les dates min et max d'un graphique.
        """
        date_min = None
        date_max = None
        for t in self.gtraces :
            xmin, xmax = t.getXminXmax()
            if date_min is None :
                date_min = xmin
            elif xmin is not None:
                date_min = min(date_min, xmin)
            if date_max is None :
                date_max = xmax
            elif xmax is not None :
                date_max = max(date_max, xmax)
                
        return date_min,date_max
        
     
            
class GgraphiqueHisto(Ggraphique) :
    """
        Classe qui définit un graphique 'graphique'
    """
                    
    def draw(self):
        """
            Crée le subplot matplot correspondant à un graphique
        """
        x,y,width,height = self.parent.getPosition(self.id)
        self.subplot = plt.subplot2grid((100,100), (int(y), int(x)), colspan=int(width), rowspan=int(height))
        self.def_unit_axis()
        self.draw_legende_aida()
        message = self.draw_courbes()
        self.draw_legende()
        self.draw_percent_misval()
        self.draw_ticks_labels_units_grid()
        self.draw_titre()
        self.set_amplitude_axes()
        self.set_echelle_log()
        return message
        
    def draw_percent_misval(self) :
        """
            Affichage du nombre et pourcentage de données absentes pour Histo,  piloté par legendeAida
        """
        ax = self.subplot
        if self.graphique.getValue("legendeAida") == "oui" :
            x1 = ax.bbox.xmin/self.parent.figure.bbox.xmax
            y1 = ax.bbox.ymax/self.parent.figure.bbox.ymax
            delta_y = 0.01
            for nt in range(len(self.graphique.traces), 0, -1) :
                try :
                    nb_valeurs = len(self.graphique.traces[nt-1].vecteur_y.data) - self.graphique.traces[nt-1].nb_manquants
                    texte = "{} ({:0.2f}% manquant)".format(nb_valeurs, self.graphique.traces[nt-1].pourcent_manquants)
                    size = 6
                    if self.parent.fmt == "gtk" :
                        size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
                    couleur = self.graphique.traces[nt-1].getValue("couleur")
                    plt.figtext(x1, y1+(delta_y*(len(self.graphique.traces)-(nt-1))), texte, size=size, color=couleur, rasterized=True)
                except :
                    pass
                    
    def getBins(self):
        """
            Retourne la liste des bins pour les graphiques de type Histo.
            On récupère la liste des bins de chaque tracé.
        """
        if len(self.gtraces) == 0 :
            return np.array([])
        bins = None
        amplitude = 0
        odg = 0
        for t in range (0, len(self.gtraces)) :
            if bins is None :
                bins = self.gtraces[t].trace.bins
            else :
                bins = np.concatenate([bins, self.gtraces[t].trace.bins])
            if amplitude == 0 :
                amplitude = self.gtraces[t].amplitudeClasse 
            elif self.gtraces[t].amplitudeClasse < amplitude :
                amplitude = self.gtraces[t].amplitudeClasse
            if self.gtraces[t].odg > odg :
                odg = self.gtraces[t].odg
        
        fmt = "%0.{}f".format(odg)
        return list(set(bins)), fmt
    
class GgraphiqueHisto3D(Ggraphique) :
    """
        Classe qui définit un graphique 'graphique'
    """

    def draw(self):
        """
            Crée le subplot matplot correspondant à un graphique
        """
        x,y,width,height = self.parent.getPosition(self.id)
        self.subplot = plt.subplot2grid((100,100), (int(y), int(x)), colspan=int(width), rowspan=int(height), projection='3d')
        ax = self.subplot 
        self.def_unit_axis()
        self.draw_legende_aida()
        message = self.draw_courbes()
        self.draw_legende()
        self.draw_percent_misval()
        self.draw_ticks_labels_units_grid()
        self.draw_titre()
        self.set_amplitude_axes()
        self.set_echelle_log()
        
        #azimut / elevation
        ax.azim = self.graphique.getValue("azimut")
        ax.elev = self.graphique.getValue("elevation")
        # ticks et labels
        size=2
        labelsize=8
        pad=2
        labelsize = np.round(labelsize*self.parent.getZoom()/self.parent.ratioPixel,5)
        pad = np.round(pad*self.parent.getZoom()/self.parent.ratioPixel,5)
        size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
        ax.tick_params(axis='both',which='minor',size=size,direction='out', labelsize=labelsize, pad=pad)
        ax.tick_params(axis='both',which='major',size=size,direction='out', labelsize=labelsize, pad=pad)
        try :
            bins, fmt = self.getBinsGraphique()
            ax.set_xticks(bins)
            ax.xaxis.set_major_formatter(FormatStrFormatter(fmt))
        except :
            pass
        ax.set_ylim(0,self.getYmax())
        #on enlève les ticks sur yaxis
        ax.yaxis.set_major_locator(plt.NullLocator())
        return message

    def draw_percent_misval(self) :
        """
            Affichage du nombre et pourcentage de données absentes pour Histo et Histo3D piloté par legendeAida
        """
        ax = self.subplot
        if self.graphique.getValue("legendeAida") == "oui" :
            x1 = ax.bbox.xmin/self.parent.figure.bbox.xmax
            y1 = ax.bbox.ymax/self.parent.figure.bbox.ymax
            delta_y = 0.01
            for nt in range(len(self.graphique.traces), 0, -1) :
                try :
                    nb_valeurs = len(self.graphique.traces[nt-1].vecteur_y.data) - self.graphique.traces[nt-1].nb_manquants
                    texte = "{} ({:0.2f}% manquant)".format(nb_valeurs, self.graphique.traces[nt-1].pourcent_manquants)
                    size = 6
                    if self.parent.fmt == "gtk" :
                        size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
                    couleur = self.graphique.traces[nt-1].getValue("couleur")
                    plt.figtext(x1, y1+(delta_y*(len(self.graphique.traces)-(nt-1))), texte, size=size, color=couleur, rasterized=True)
                except :
                    pass
                    
    def draw_legende(self) :
        """
            Affiche la légende pour les graphiques Histo_3D : traitement particulier pour Histo3D car bar3D n'a pas d'argument label
        """
        if self.graphique.getValue("legendeVisible") == "oui" :
            ax = self.subplot
            handls = []
            lbls = []
            for gt in self.gtraces :
                if gt.trace.getValue("legendeVisible") == "oui" : # légende du tracé                   
                    leg = Line2D([], [], color=gt.trace.getValue("couleur"), linestyle=gt.trace.getValue("typeLigne"), linewidth=gt.trace.getValue("epaisseur"))
                    handls.append(leg)
                    lbls.append(""+ gt.trace.getLegende()) 
            (family, fontsize, weight, style) = self.parent.policeToValues(self.graphique.getValue("policeLegende"))
            if self.parent.fmt == "gtk" :
                    fontsize = np.round(fontsize*self.parent.getZoom()/self.parent.ratioPixel,5)
            loc = self.graphique.getValue("positionLegende").split(',')
            if int(loc[0]) == 0 : # best
                bbox_to_anchor = None
            else :
                bbox_to_anchor=(float(loc[1])+float(loc[3]), float(loc[2])+float(loc[4]))
            
            # nombre de colonnes de la légende
            nbcol = self.graphique.getValue("ncolLegende")
            leg = ax.legend(handls, lbls, prop={'size':fontsize, 'family':family, 'weight':weight, 'style':style}, loc=int(loc[0]), bbox_to_anchor=bbox_to_anchor, ncol=nbcol)

        
    def getBinsGraphique(self):
        """
            Retourne la liste des bins pour les graphiques de type Histo3D et RDV : 
            la liste des bins est définie au niveau du graphique et non de chaque tracé contrairement à getBins()
        """
        if len(self.gtraces) == 0 :
            return tuple()
        bins = []
        minData, maxData = self.getMinMax()
        
        if self.graphique.getValue("minHisto") != self.graphique.getDefault("minHisto") :
            minHisto = float(self.graphique.getValue("minHisto"))
        else :
            minHisto = minData            
        if self.graphique.getValue("maxHisto") != self.graphique.getDefault("maxHisto") :
            maxHisto = float(self.graphique.getValue("maxHisto"))
        else :
            maxHisto = maxData
        if self.graphique.getValue("infHisto") == "oui" and minHisto > minData :
            bins.append(minData)    
        bins.append(minHisto)
            
        if self.graphique.getValue("amplitudeClassesHisto") != self.graphique.getDefault("amplitudeClassesHisto") :
            # on a choisi une amplitude
            amplitude = float(self.graphique.getValue("amplitudeClassesHisto"))
            nbClasses = round((maxHisto - minHisto) / amplitude)
        else :
            # on calcule l'amplitude avec le nombre d'intervalles
            nbClasses = float(self.graphique.getValue("nombreClassesHisto"))
            amplitude = (maxHisto - minHisto) / nbClasses
        val = minHisto
        nbc = 0
        while nbc < nbClasses :
            val += amplitude
            bins.append(val)
            nbc += 1
            
        if self.graphique.getValue("supHisto") == "oui"  and maxHisto < maxData :
            bins.append(maxData)
        
        binsSet = set(bins)
        bins = list(binsSet)
        bins.sort()       
                
        # calcul de la précision des ticks : on cherche l'ordre de grandeur de l'amplitude min des classes :
        # si c'est un entier on prend l'ordre de grandeur du premier bins
        amplitude = amplitude - int(amplitude)
        if amplitude != 0 :
            odg = abs(int(floor(log10(amplitude))))
        else :
            try :
                odg = abs(int(floor(log10(abs(bins[0]-int(bins[0]))))))
            except : # les bins sont des entiers => odg=0
                odg = 0
        fmt = "%0.{}f".format(odg+1)
        return bins, fmt

    def getPositionTrace(self, gtrace):
        """
            Retourne la position du vecteur sur l'axe des ordonnées dans un graphique Histo3D.
        """
        num_trace = self.gtraces.index(gtrace)
        return 2*num_trace +1
    
    def getYmax(self):
        """
            Retourne la valeur max de l'axe des ordonnées dans un graphique Histo3D.
        """
        marges = 1+1
        n = len(self.gtraces)
        maxy = n + n-1 + marges
        return maxy
        
    
class GgraphiqueRDV(Ggraphique) :
    """
        Classe qui définit un graphique 'graphique'
    """

    def draw(self):
        """
            Crée le subplot matplot correspondant à un graphique
        """
        x,y,width,height = self.parent.getPosition(self.id)
        rect = [0.1, 0.1, 0.8, 0.8]
        x,y,width,height = self.parent.getPosition(self.id)
        fontsize=10
        if self.parent.fmt == "gtk" :
                fontsize = np.round(fontsize*self.parent.getZoom()/self.parent.ratioPixel,5)
        ax = WindroseAxes(self.parent.figure, rect, fontsize=fontsize, rasterized=False)
        self.subplot = ax
        ax.set_position([x/100., (100-y-height)/100., width/100., height/100.])
        
        # on trace les courbes
        message = ""    
        for t in range (0, len(self.gtraces)) :
            mess = self.gtraces[t].draw()
            if mess != "" :
                message += mess+"\n"
        if message != "" :
            size = 12
            horizontalalignment = 'center'
            if self.parent.fmt == "gtk" :
                size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
                horizontalalignment='center'
            x1 = (ax.bbox.xmax + ax.bbox.xmin)/self.parent.figure.bbox.xmax/2
            y1 = (ax.bbox.ymin + ax.bbox.ymax)/self.parent.figure.bbox.ymax/2        
            plt.figtext(x1,y1, message, transform=self.parent.figure.transFigure, figure=self.parent.figure, size=size, horizontalalignment=horizontalalignment, verticalalignment='bottom', rasterized=True)    
            self.parent.figure.add_axes(ax)
        else :
            l = ax.legend(borderaxespad=-0.10, loc=(1,0), framealpha=0.5, prop={'size':fontsize})
            plt.setp(l.get_texts(), fontsize=fontsize)      
            self.parent.figure.add_axes(ax)
          
        # titre du graphique
        if self.graphique.getValue("titre") != "" :
            (family, size, weight, style) = self.parent.policeToValues(self.graphique.getValue("policeTitre"))
            if self.parent.fmt == "gtk" :
                size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
            
            plt.title(""+self.graphique.toTitle(self.graphique.getValue("titre")), family=family, weight=weight, size=size, style=style, rasterized=True)
        
        #légende aida (nom des 2 vecteurs dd et ff en dessous du graphique)
        if self.graphique.getValue("legendeAida") == "oui" :
            texte=""
            for t in self.graphique.traces :
                texte = t.getLegendeAida()
            if texte != "" :
                textes = texte.split("#")
                size = 6
                if self.parent.fmt == "gtk" :
                    size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)                    
                horizontalalignment = 'left'
                verticalalignment = 'center'
                rotation = 0
                x1 = ax.bbox.xmin/self.parent.figure.bbox.xmax + 0.02
                y1 = ax.bbox.ymin/self.parent.figure.bbox.ymax
                plt.figtext(x1, y1,textes[0], size=size, horizontalalignment=horizontalalignment, verticalalignment=verticalalignment, rotation=rotation)
                x1 = ax.bbox.xmin/self.parent.figure.bbox.xmax + 0.02
                y1 = ax.bbox.ymin/self.parent.figure.bbox.ymax - 0.01
                plt.figtext(x1, y1,textes[1], size=size, horizontalalignment=horizontalalignment, verticalalignment=verticalalignment, rotation=rotation, rasterized=True)
                
                # nombre de valeurs manquantes
                x1 = ax.bbox.xmin/self.parent.figure.bbox.xmax
                y1 = ax.bbox.ymax/self.parent.figure.bbox.ymax
                try :
                    nb_valeurs = len(self.graphique.traces[0].vecteur_y.data) - self.graphique.traces[0].nb_manquants
                    texte = "{} ({:0.2f}% manquant)".format(nb_valeurs, self.graphique.traces[0].pourcent_manquants)
                    size = 6
                    if self.parent.fmt == "gtk" :
                        size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
                    couleur = self.graphique.traces[0].getValue("couleur")
                    plt.figtext(x1, y1, texte, size=size, color=couleur, rasterized=True)
                except :
                    pass

        return (message)
    
    def getBinsGraphique(self):
        """
            Retourne la liste des bins pour les graphiques de type Histo3D et RDV : 
            la liste des bins est définie au niveau du graphique et non de chaque tracé contrairement à getBins()
        """
        if len(self.gtraces) == 0 :
            return tuple()
        bins = []
        minData, maxData = self.getMinMax()
        
        if self.graphique.getValue("minHisto") != self.graphique.getDefault("minHisto") :
            minHisto = float(self.graphique.getValue("minHisto"))
        else :
            minHisto = minData            
        if self.graphique.getValue("maxHisto") != self.graphique.getDefault("maxHisto") :
            maxHisto = float(self.graphique.getValue("maxHisto"))
        else :
            maxHisto = maxData
        if self.graphique.getValue("infHisto") == "oui" and minHisto > minData :
            bins.append(minData)    
        bins.append(minHisto)
            
        if self.graphique.getValue("amplitudeClassesHisto") != self.graphique.getDefault("amplitudeClassesHisto") :
            # on a choisi une amplitude
            amplitude = float(self.graphique.getValue("amplitudeClassesHisto"))
            nbClasses = round((maxHisto - minHisto) / amplitude)
        else :
            # on calcule l'amplitude avec le nombre d'intervalles
            nbClasses = float(self.graphique.getValue("nombreClassesHisto"))
            amplitude = (maxHisto - minHisto) / nbClasses
        val = minHisto
        nbc = 0
        while nbc < nbClasses :
            val += amplitude
            bins.append(val)
            nbc += 1
            
        if self.graphique.getValue("supHisto") == "oui"  and maxHisto < maxData :
            bins.append(maxData)
        
        binsSet = set(bins)
        bins = list(binsSet)
        bins.sort()       
                
        # calcul de la précision des ticks : on cherche l'ordre de grandeur de l'amplitude min des classes :
        # si c'est un entier on prend l'ordre de grandeur du premier bins
        amplitude = amplitude - int(amplitude)
        if amplitude != 0 :
            odg = abs(int(floor(log10(amplitude))))
        else :
            try :
                odg = abs(int(floor(log10(abs(bins[0]-int(bins[0]))))))
            except : # les bins sont des entiers => odg=0
                odg = 0
        fmt = "%0.{}f".format(odg+1)
        return bins, fmt
                
class GgraphiqueHov(Ggraphique) :
    """
        Classe qui définit un graphique 'graphique'
    """

    def draw(self):
        """
            Crée le subplot matplot correspondant à un graphique
        """
        message = self.ctrl()
        if message :
            return message
        x,y,width,height = self.parent.getPosition(self.id)
        self.subplot = plt.subplot2grid((100,100), (int(y), int(x)), colspan=int(width), rowspan=int(height))
        self.def_unit_axis()
        self.draw_jour_nuit()
        self.draw_legende_aida()
        message = self.draw_courbes()
        self.draw_legende()
        self.draw_ticks_labels_units_grid()
        self.set_echelle_log()
        self.set_labels_gauche()
        self.draw_titre()
        self.set_amplitude_axes()
        self.invertYAxis()

        return message
    
    def ctrl(self):
        """
            Effectue quelques controles
        """
        message = None
        # un tracé de type Hov de dim_array = 1 doit être seul
        found = False
        for t in self.gtraces :
            try :
                dim_array = int(AIDA.get_dim_array(t.trace.vecteur_y.attributes["dim_array"])[0])
                if t.trace.type == "Hov" and dim_array == 1 :
                    numTrace = self.gtraces.index(t)+1
                    numGraphique = self.parent.ggraphiques.index(self)+1
                    numPage = self.parent.parent.gpages.index(self.parent)+1
                    found = True
                    break
            except :
                pass
        if found and  len(self.gtraces) > 1 :
            message = "Le tracé n°{}, graphique n°{} de la page {} est de type Hov et de dimension 1. Aucune superposition autorisée".format(numTrace, numGraphique, numPage)

        return message
    
    def invertYAxis(self) :
        """
            Inverse l'axe des ordonnées de gauche
        """
        ax = self.subplot
        if self.graphique.getValue("inverseAxeYHov") == "oui" :
            ax.invert_yaxis()
        
    def set_labels_gauche(self) :
        """
            Trace le pourcentage de labels sélectionné.
        """
        ax = self.subplot
        try : # en cas de données absentes
            qtt_labels = self.graphique.getValue("labelsGaucheHov")
            if qtt_labels == "Auto" :
                return
            if qtt_labels == "Aucun" :
                ax.yticks([])
                return
            ticks_bornes = np.array([])
            try :
                dim_array = int(AIDA.get_dim_array(self.gtraces[0].trace.vecteur_y.attributes["dim_array"])[0])
            except :
                dim_array = 1
            if dim_array > 1 :
                for t in self.gtraces :
                    if t.trace.type == "Hov" :
                        bornes = np.array(t.trace.vecteur_y.bornes[:,:,0], dtype = float)
                        ticks_bornes = np.concatenate((ticks_bornes,bornes), axis = None)
                ticks_bornes=list(set(ticks_bornes))
                ticks_bornes.sort()
                step = int(100/int(qtt_labels[:-1]))
                ax.set_yticks(ticks_bornes[::step])
                ax.set_yticklabels(ticks_bornes[::step])
        except Exception as e:
            print(e)
            pass
    

        
class GgraphiquePlotXY(Ggraphique) :
    """
        Classe qui définit un graphique 'graphique'
    """

    def draw(self):
        """
            Crée le subplot matplot correspondant à un graphique
        """
        x,y,width,height = self.parent.getPosition(self.id)
        self.subplot = plt.subplot2grid((100,100), (int(y), int(x)), colspan=int(width), rowspan=int(height))
        ax = self.subplot
        self.def_unit_axis()
        self.draw_legende_aida()
        message = self.draw_courbes()
        self.draw_legende()
        self.draw_label_regression()
        self.draw_ticks_labels_units_grid()
        self.draw_titre()
        # autoscale pour les plotXY du a un bug matlplotlib sur les scatter plot (utilisés pour l'affichage conditionnel si PlotXY)
        ax.autoscale()
        self.set_amplitude_axes()
        self.set_amplitude_axe_bas()
        self.set_echelle_log()
        if self.graphique.getValue("x=y") == "oui" :              
            limites = ax.get_ylim()
            ax.plot([limites[0],limites[1]], [limites[0],limites[1]], color='black', rasterized=True)
        return message
    
    def set_amplitude_axe_bas(self) :
        """
            Positionne l'amplitude sur l'axe du bas
        """
        ax = self.subplot
        if self.graphique.getValue("echelleBas") == "auto" :
            amplitude = self.graphique.getValue("echelleAmplitudeBas")                
            if amplitude != 0 :
                limites = ax.get_xlim()     
                xmin = (limites[0]+limites[1])/2. - (amplitude/2.)
                xmax = (limites[0]+limites[1])/2. + (amplitude/2.)
                ax.set_xlim([xmin, xmax])
        else :
            xmin = self.graphique.getValue("echelleMinBas")
            xmax = self.graphique.getValue("echelleMaxBas")          
            ax.set_xlim([xmin, xmax])

    def draw_label_regression(self) :
        """
            Trace les labels de la droite de régression au-dessus du graphique PlotXY
        """
        ax = self.subplot
        x1 = ax.bbox.xmin/self.parent.figure.bbox.xmax
        y1 = ax.bbox.ymax/self.parent.figure.bbox.ymax
        delta_y = 0.01
        nt = len([t for t in self.graphique.traces if t.getValue("regression")=="oui"])
        for trace in self.graphique.traces :
            if trace.getValue("regression") == "oui" :
                try :
                    texte = trace.getLegendeAida().split("##")[-1]
                    x1 = ax.bbox.xmin/self.parent.figure.bbox.xmax
                    y1 = ax.bbox.ymax/self.parent.figure.bbox.ymax
                    delta_y = 0.01
                    size = 6
                    if self.parent.fmt == "gtk" :
                        size = np.round(size*self.parent.getZoom()/self.parent.ratioPixel,5)
                    couleur = trace.getValue("couleur")
                    plt.figtext(x1, y1+(delta_y*nt), texte, size=size, color=couleur, rasterized=True)
                    nt = nt-1
                except :
                    pass
                    
class GgraphiqueST(Ggraphique) :
    """
        Classe qui définit un graphique 'graphique'
    """
            
    def draw(self):
        """
            Crée le subplot matplot correspondant à un graphique
        """
        x,y,width,height = self.parent.getPosition(self.id)
        self.subplot = plt.subplot2grid((100,100), (int(y), int(x)), colspan=int(width), rowspan=int(height))
        self.def_unit_axis()
        self.draw_jour_nuit()
        self.draw_legende_aida()
        message = self.draw_courbes()
        self.draw_legende()
        self.draw_ticks_labels_units_grid()
        self.draw_titre()
        self.set_amplitude_axes()
        self.set_echelle_log()        

        ax = self.subplot              
        # droite y=n
        if self.graphique.getValue("y=n") == "oui" :              
            limites = ax.get_xlim()
            n = self.graphique.getValue("n")
            ax.plot([limites[0],limites[1]], [n,n], color='black', rasterized=True)
                
        return message
    
                   
class Gtrace :
    """
        Classe abstraite qui définit un graphique 'tracé'
    """
    def __init__(self, trace, parent):
        self.id = trace.id
        self.trace = trace
        self.parent =parent 
    
    def draw(self):
        """
            Ajoute un plot matplot dans le subplot graphique parent
        """
        raise NotImplementedError("Vous devez implémenter la méthode draw de la classe Gtrace.")
    
    def getBins(self, minHisto, maxHisto, minData, maxData):
        """
            Retourne un tuple contenant les bins d'un tracé de type histogramme
        """
        bins = []
        if self.trace.getValue("infHisto") == "oui" and minHisto > minData :
            bins.append(minData)    
        bins.append(minHisto)
            
        if self.trace.getValue("amplitudeClassesHisto") != self.trace.getDefault("amplitudeClassesHisto") :
            # on a choisi une amplitude
            amplitude = float(self.trace.getValue("amplitudeClassesHisto"))
            nbClasses = ceil((maxHisto - minHisto) / amplitude)
        else :
            # on calcule l'amplitude avec le nombre d'intervalles
            nbClasses = float(self.trace.getValue("nombreClassesHisto"))
            amplitude = (maxHisto - minHisto) / nbClasses
        val = minHisto
        nbc = 0
        while nbc < nbClasses :
            val += amplitude
            bins.append(val)
            nbc += 1
        if self.trace.getValue("supHisto") == "oui"  and maxHisto < maxData :
            bins.append(maxData)
        # ordre de grandeur à appliquer aux bins
        try :
            odg_amp = abs(int(floor(log10(abs(amplitude-int(amplitude))))))
        except :
            odg_amp = 0
        try :
            odg_min_val = abs(int(floor(log10(abs(minHisto-int(minHisto))))))
        except :
            odg_min_val = 0
        self.odg = max(odg_amp,odg_min_val)
        fmt_val = "{{:0.{}f}}".format(self.odg)
        bins = [ float(fmt_val.format(value)) for value in bins ]      
        binsSet = set(bins)
        bins = list(binsSet)
        bins.sort()       
        return tuple(bins)
    
    def getXminXmax(self):
        """
            Retourne les valeurs min et max en abscisse d'un tracé.
        """
        return None,None 
    
    def decoupe_periode(self, data_y, data_time) :
        """
            Découpe la série temporelle en périodes selon le choix utilisateur.
            Retourne 2 dict indexés par les périodes : 1 pour les datas et 1 pour le temps (secondes depuis le début de la période)
        """
        graphique = self.trace.parent
        seconds_by_periode = collections.defaultdict(list)
        datas_by_periode = collections.defaultdict(list)
        dtime = data_time.astype(int)
        odeb = int(mpl_dates.date2num(vd.toDate(self.trace.debut)))
        ofin = int(mpl_dates.date2num(vd.toDate(self.trace.fin)))
        odate = odeb
        if graphique.getValue("decoupagePeriode") == "j" :
            nbj = graphique.getValue("nombreJoursDecoupage")
            n = 0
            date_jour = collections.defaultdict(list)
            while odate <= ofin :
                if n == 0 :
                    j1 = mpl_dates.num2date(odate).strftime("%Y-%m-%d")
                    jn = mpl_dates.num2date(odate+nbj-1).strftime("%Y-%m-%d")
                    key = "{}:{}".format(j1,jn)
                if n == nbj-1 :                    
                    n = 0
                else :
                    n = n+1
                date_jour[key].append(odate) 
                odate += 1
            for j1jn, values in date_jour.items() :
                label = j1jn
                wdate = np.where((dtime>=values[0])&(dtime<=values[-1]))
                if len(wdate[0]) == 0 : # peut se produire pour les graphiques Histo filtrés
                    seconds_by_periode[label] = np.array([])
                    datas_by_periode[label] = np.array([])
                else :
                    imin = np.min(wdate)
                    imax = np.max(wdate)
                    j1 = j1jn.split(':')[0]
                    ojour1 = mpl_dates.date2num(datetime.datetime(int(j1.split('-')[0]), int(j1.split('-')[1]), int(j1.split('-')[2]), 0, 0, 0))
                    seconds_by_periode[label] = np.concatenate((seconds_by_periode[label], (data_time[imin:imax+1] - ojour1)*24*3600))
                    datas_by_periode[label] = np.concatenate((datas_by_periode[label], data_y[imin:imax+1]))
        elif graphique.getValue("decoupagePeriode") == "m" :
            date_mois = collections.defaultdict(list)
            while odate <= ofin :
                aaaamm = mpl_dates.num2date(odate).strftime('%Y-%m')
                date_mois[aaaamm].append(odate)
                odate += 1
            for aaaamm, values in date_mois.items() :
                wdate = np.where((dtime>=values[0])&(dtime<=values[-1]))
                imin = np.min(wdate)
                imax = np.max(wdate)
                label = aaaamm
                omois = mpl_dates.date2num(datetime.datetime(int(aaaamm.split('-')[0]), int(aaaamm.split('-')[1]), 1, 0, 0, 0))
                seconds_by_periode[label] = np.concatenate((seconds_by_periode[label], (data_time[imin:imax+1] - omois)*24*3600))
                datas_by_periode[label] = np.concatenate((datas_by_periode[label], data_y[imin:imax+1]))
        else :
            date_an = collections.defaultdict(list)
            while odate <= ofin :
                aaaa = mpl_dates.num2date(odate).strftime('%Y')
                date_an[aaaa].append(odate)
                odate += 1
            for aaaa, values in date_an.items() :
                wdate = np.where((dtime>=values[0])&(dtime<=values[-1]))
                imin = np.min(wdate)
                imax = np.max(wdate)
                label = aaaa
                oan = mpl_dates.date2num(datetime.datetime(int(aaaa), 1, 1, 0, 0, 0))
                seconds_by_periode[label] = np.concatenate((seconds_by_periode[label], (data_time[imin:imax+1] - oan)*24*3600))
                datas_by_periode[label] = np.concatenate((datas_by_periode[label], data_y[imin:imax+1]))
                
        return datas_by_periode, seconds_by_periode 

        
class GtraceST(Gtrace):
    """
        Classe qui définit un graphique 'tracé de type ST'
    """
    def __init__(self, trace, parent):
        Gtrace.__init__(self, trace, parent)

    def draw(self):
        message = ""
        numTrace = self.parent.gtraces.index(self)+1
        numGraphique = self.parent.parent.ggraphiques.index(self.parent)+1
        numPage = self.parent.parent.parent.gpages.index(self.parent.parent)+1
        self.zorder = 2 + numGraphique*0.01

        if self.trace.vecteur_y != None :
            # Tracé conditionnel ou pas
            if len(self.trace.expressions_condition) < 2 : # tracé classique
                self.plot_date()
            else : # tracé conditionnel
                if self.trace.getValue("typeLigne") != "None" or  self.trace.getValue("marqueur") == "None" :
                    self.plot_conditionnel_lines()
                else :
                    self.plot_conditionnel_points()
        else :
            if self.trace.getValue("plateforme") == self.trace.getDefault("plateforme") :
                message = "Plateforme non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            elif self.trace.getValue("parametre") == self.trace.getDefault("parametre") :
                message = "Paramètre non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            else :
                message = "Pas de données sur la période pour {} {}.".format(self.trace.getValue("plateforme"), self.trace.getValue("parametre"))
        return message
                
    def plot_date(self) :
        """
            Trace un graphique ST classique, sans conditions
        """
        ax = self.axe_y
        data_y = self.trace.data_y.copy()
        data_time = self.trace.vecteur_y.time_mpl.copy()
        label_legende=''
        lineWidth = self.trace.getValue("epaisseur")
        markerSize = self.trace.getValue("epaisseur")
        if self.parent.parent.fmt == "gtk" :
            lineWidth = np.round(lineWidth*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
            markerSize = np.round(markerSize*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
        graphique = self.trace.parent
        if graphique.getValue("decoupageActiver") == "oui" :
            datas_by_periode, seconds_by_periode = self.decoupe_periode(data_y, data_time)
            couleurs_decoupage = self.parent.get_couleurs_decoupage()
            for periode in seconds_by_periode :
                if periode in couleurs_decoupage :
                    ax.plot(seconds_by_periode[periode], datas_by_periode[periode],
                              label=label_legende,
                              color=couleurs_decoupage[periode],
                              ls=self.trace.getValue("typeLigne"),
                              lw=lineWidth,
                              marker = self.trace.getValue("marqueur"),
                              ms=markerSize,
                              mfc = couleurs_decoupage[periode],
                              mec = couleurs_decoupage[periode],
                              rasterized = True,
                              zorder = self.zorder
                              )
                
        else :
            if self.trace.getValue("legendeVisible") == "oui" :
                label_legende = ""+self.trace.getLegende()
            ax.plot(self.trace.vecteur_y.time_mpl, data_y,
                          label=label_legende,
                          color=self.trace.getValue("couleur"),
                          ls=self.trace.getValue("typeLigne"),
                          lw=lineWidth,
                          marker = self.trace.getValue("marqueur"),
                          ms=markerSize,
                          mfc = self.trace.getValue("couleur"),
                          mec = self.trace.getValue("couleur"),
                          rasterized = True,
                          zorder = self.zorder)

    def plot_conditionnel_lines(self) :
        """
            Trace un graphique ST avec conditions
        """
        ax = self.axe_y
        data_y = self.trace.data_y.copy()
        data_time = self.trace.vecteur_y.time_mpl.copy()
        lineWidth = self.trace.getValue("epaisseur")
        markerSize = self.trace.getValue("epaisseur")
        if self.parent.parent.fmt == "gtk" :
            lineWidth = np.round(lineWidth*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
            markerSize = np.round(markerSize*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
        graphique = self.trace.parent
        
        # colormap : ["non évaluable", "tracé", "condition1", "condition2",...,"condition n"]
        cmap = [self.trace.expressions_condition[0]["couleur"]]
        cmap.append(self.trace.getValue("couleur"))
        # epaisseurs : ["non évaluable", "tracé", "condition1", "condition2",...,"condition n"]
        epaisseurs = [self.trace.expressions_condition[0]["epaisseur"]]
        epaisseurs.append(self.trace.getValue("epaisseur"))
        for cond in self.trace.expressions_condition[1:] :
            cmap.append(cond["couleur"])
            epaisseurs.append(cond["epaisseur"])

        # tableau des epaisseurs
        linewidths = []
        for r in self.trace.conditions[0:-1] :
            linewidths.append(epaisseurs[r])
            
        if graphique.getValue("decoupageActiver") == "oui" :
            datas_by_periode, seconds_by_periode = self.decoupe_periode(data_y, data_time)
            couleurs_decoupage = self.parent.get_couleurs_decoupage()
            periodes = list(seconds_by_periode.keys())
            periodes.sort()
            i_deb_periode = 0                    
            for periode in periodes :
                # on place la couleur du tracé en 2eme position (on converti avant de (r, g, b, a) en #rrggbbaa )
                couleur_trace = "#{:02x}{:02x}{:02x}".format(*tuple([int(val*255) for val in couleurs_decoupage[periode][0:3]]))
                cmap[1] = couleur_trace
                
                i_fin_periode = i_deb_periode + len(seconds_by_periode[periode])
                if periode in couleurs_decoupage :
                    result = set([ r for r in self.trace.conditions[i_deb_periode:i_fin_periode] if r != -1 ])
                    for r in result :
                        mask_cond = np.ma.getmaskarray(data_y[i_deb_periode:i_fin_periode]).copy()
                        mask_cond[np.where(self.trace.conditions[i_deb_periode:i_fin_periode] != r)] = True
                        # on raboute les segments : on passe à False les True précédés d'un False
                        a = np.where(mask_cond == False)[0]
                        b = np.where(mask_cond == True)[0]
                        a = a+1
                        mask_cond[np.intersect1d(a,b)] = False
                        
                        data = np.ma.array(datas_by_periode[periode].data,
                                                mask=mask_cond)                    
                        data_time = np.ma.array(seconds_by_periode[periode].data,
                                                     mask=mask_cond)                
                        ax.plot(data_time, data,
                                  color=cmap[r],
                                  ls=self.trace.getValue("typeLigne"),
                                  lw=epaisseurs[r],
                                  marker = self.trace.getValue("marqueur"),
                                  ms=markerSize,
                                  mfc = self.trace.getValue("couleur"),
                                  mec = self.trace.getValue("couleur"),
                                  rasterized = True,
                                  zorder = self.zorder)                                       
                i_deb_periode = i_fin_periode
        else :
            result = set([ r for r in self.trace.conditions if r != -1 ])
            for r in result :
                mask_cond = np.ma.getmaskarray(data_y).copy()
                mask_cond[np.where(self.trace.conditions != r)] = True                
                data = data_y.copy()
                data.mask = mask_cond
                # on raboute les segments : on passe à False les True précédés d'un False
                a = np.where(mask_cond == False)[0]
                b = np.where(mask_cond == True)[0]
                a = a+1
                data.mask[np.intersect1d(a,b)] = False
                ax.plot(data_time, data,
                          color=cmap[r],
                          ls=self.trace.getValue("typeLigne"),
                          lw=epaisseurs[r],
                          marker = self.trace.getValue("marqueur"),
                          ms=markerSize,
                          mfc = self.trace.getValue("couleur"),
                          mec = self.trace.getValue("couleur"),
                          rasterized = True,
                          zorder = self.zorder)
            
        # on trace un point x=debut y=moyenne d'epaisseur 0 (invisible) pour forcer l'échelle en mode auto
        moy = (np.ma.min(data_y)+np.ma.max(data_y))/2
        ax.plot([self.trace.vecteur_y.time_mpl[0]], [moy], color='black', linewidth=0, rasterized=False)
    
    def plot_conditionnel_points(self) :
        """
            Trace un graphique ST avec conditions
        """
        ax = self.axe_y
        data_y = self.trace.data_y.copy()
        data_time = self.trace.vecteur_y.time_mpl.copy()
        lineWidth = self.trace.getValue("epaisseur")
        markerSize = self.trace.getValue("epaisseur")
        if self.parent.parent.fmt == "gtk" :
            lineWidth = np.round(lineWidth*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
            markerSize = np.round(markerSize*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
        graphique = self.trace.parent
        
        # colormap : ["non évaluable", "tracé", "condition1", "condition2",...,"condition n"]
        cmap = [self.trace.expressions_condition[0]["couleur"]]
        cmap.append(self.trace.getValue("couleur"))
        # epaisseurs : ["non évaluable", "tracé", "condition1", "condition2",...,"condition n"]
        epaisseurs = [self.trace.expressions_condition[0]["epaisseur"]]
        epaisseurs.append(self.trace.getValue("epaisseur"))
        for cond in self.trace.expressions_condition[1:] :
            cmap.append(cond["couleur"])
            epaisseurs.append(cond["epaisseur"])
            
        if graphique.getValue("decoupageActiver") == "oui" :
            datas_by_periode, seconds_by_periode = self.decoupe_periode(data_y, data_time)
            couleurs_decoupage = self.parent.get_couleurs_decoupage()
            periodes = list(seconds_by_periode.keys())
            periodes.sort()
            i_deb_periode = 0
            for periode in periodes :               
                # on place la couleur du tracé en 2eme position (on converti avant de (r, g, b, a) en #rrggbbaa )
                couleur_trace = "#{:02x}{:02x}{:02x}".format(*tuple([int(val*255) for val in couleurs_decoupage[periode][0:3]]))
                cmap[1] = couleur_trace
                i_fin_periode = i_deb_periode + len(seconds_by_periode[periode])
                result = set([ r for r in self.trace.conditions[i_deb_periode:i_fin_periode] if r != -1 ])
                if periode in couleurs_decoupage :
                    for r in result :
                        mask_cond = np.ma.getmaskarray(data_y[i_deb_periode:i_fin_periode]).copy()
                        mask_cond[np.where(self.trace.conditions[i_deb_periode:i_fin_periode] != r)] = True
                        data = np.ma.compressed(np.ma.array(datas_by_periode[periode].data,
                                                mask=mask_cond))                    
                        data_time = np.ma.compressed(np.ma.array(seconds_by_periode[periode].data,
                                                     mask=mask_cond))
                        
                        ax.scatter(data_time, data, c=cmap[r], edgecolors='none', marker=self.trace.getValue("marqueur"), s=epaisseurs[r], zorder = self.zorder)
                    
                i_deb_periode = i_fin_periode
            ax.set_ylim([np.ma.min(data_y), np.ma.max(data_y)])
        else :
            result = set([ r for r in self.trace.conditions if r != -1 ])
            for r in result :
                mask_cond = np.ma.getmaskarray(data_y).copy()
                mask_cond[np.where(self.trace.conditions != r)] = True
                data = np.ma.compressed(np.ma.array(data_y,mask=mask_cond))
                time = np.ma.compressed(np.ma.array(data_time,mask=mask_cond))                        
                ax.scatter(time, data, c=cmap[r], edgecolors='none', marker=self.trace.getValue("marqueur"), s=epaisseurs[r], zorder = self.zorder)
        
    def getXminXmax(self):
        """
            Retourne les dates min et max d'un graphique ST :
            on retourne les dates de la 1ère et de la dernière data non masquées.
        """
        data_y = self.trace.data_y
        try :
            data_time = self.trace.vecteur_y.time
        except :
            return None, None
        if np.ma.count(data_y) != 0 :
            index_first_value = data_y.nonzero()[0][0]
            index_last_value = data_y.nonzero()[0][-1]
            #return vd.datetimeFromOrdinal(data_time[index_first_value]), vd.datetimeFromOrdinal(data_time[index_last_value ])
            return data_time[index_first_value], data_time[index_last_value ]
        else :
            return None, None


class GtracePlotXY(Gtrace):
    """
        Classe qui définit un graphique 'tracé de type PlotXY'
    """
    def __init__(self, trace, parent):
        Gtrace.__init__(self, trace, parent)

    def draw(self):
        message = ""
        numTrace = self.parent.gtraces.index(self)+1
        numGraphique = self.parent.parent.ggraphiques.index(self.parent)+1
        numPage = self.parent.parent.parent.gpages.index(self.parent.parent)+1
        lineWidth = self.trace.getValue("epaisseur")
        markerSize = self.trace.getValue("epaisseur")
        if self.parent.parent.fmt == "gtk" :
            lineWidth = np.round(lineWidth*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
            markerSize = np.round(markerSize*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
        if self.trace.vecteur_y != None :
            ax = self.axe_y
            #ax = self.parent.subplot
        if self.trace.vecteur_x != None and len(np.ma.compressed(self.trace.data_x))!=0  and self.trace.vecteur_y != None and len(np.ma.compressed(self.trace.data_y))!=0 :
            if len(self.trace.data_x) != len(self.trace.data_y) :
                    message = "Les vecteurs ne sont pas de taille identique pour le tracé PlotXY :\n"
                    message += "{} {} : {}\n".format(self.trace.getValue("plateforme_x"),self.trace.getValue("parametre_x"),len(self.trace.data_x))
                    message += "{} {} : {}".format(self.trace.getValue("plateforme"),self.trace.getValue("parametre"),len(self.trace.data_y))

            else :
                data_x_regression = self.trace.data_x
                data_x = self.trace.data_x.copy()
                data_time_x = self.trace.vecteur_x.time_mpl.copy()
                data_y = self.trace.data_y.copy()
                data_time_y = self.trace.vecteur_y.time_mpl.copy()
                
                # tracé conditionnel ou pas
                if len(self.trace.expressions_condition) < 2 : # tracé classique
                    if self.parent.graphique.getValue("decoupageActiver") == "oui" :
                        datas_by_periode_x, seconds_by_periode_x = self.decoupe_periode(data_x, data_time_x)
                        datas_by_periode_y, seconds_by_periode_y = self.decoupe_periode(data_y, data_time_y)
                        couleurs_decoupage = self.parent.get_couleurs_decoupage()
                        for periode in datas_by_periode_x :
                            if periode in couleurs_decoupage :
                                x2 = np.ma.compressed(np.ma.array(datas_by_periode_x[periode],mask=list(map(or_,np.ma.getmaskarray(datas_by_periode_x[periode]),np.ma.getmaskarray(datas_by_periode_y[periode])))))
                                y2 = np.ma.compressed(np.ma.array(datas_by_periode_y[periode],mask=list(map(or_,np.ma.getmaskarray(datas_by_periode_x[periode]),np.ma.getmaskarray(datas_by_periode_y[periode])))))                        
                                label_legende=''
                                ax.plot(x2, y2,
                                          label=label_legende,
                                          color=couleurs_decoupage[periode],
                                          ls=self.trace.getValue("typeLigne"),
                                          lw=lineWidth,
                                          marker = self.trace.getValue("marqueur"),
                                          ms=markerSize,
                                          mfc = couleurs_decoupage[periode],
                                          mec = couleurs_decoupage[periode],
                                          rasterized=True)
                    else :
                        x2 = np.ma.compressed(np.ma.array(self.trace.data_x,mask=list(map(or_,np.ma.getmaskarray(self.trace.data_x),np.ma.getmaskarray(self.trace.data_y)))))
                        y2 = np.ma.compressed(np.ma.array(self.trace.data_y,mask=list(map(or_,np.ma.getmaskarray(self.trace.data_x),np.ma.getmaskarray(self.trace.data_y)))))                        
                        label_legende=''
                        if self.trace.getValue("legendeVisible") == "oui" :
                            label_legende = ""+self.trace.getLegende()
                        ax.plot(x2, y2,
                                  label=label_legende,
                                  color=self.trace.getValue("couleur"),
                                  ls=self.trace.getValue("typeLigne"),
                                  lw=lineWidth,
                                  marker = self.trace.getValue("marqueur"),
                                  ms=markerSize,
                                  mfc = self.trace.getValue("couleur"),
                                  mec = self.trace.getValue("couleur"),
                                  rasterized=True)
                else : # tracé conditionnel
                    # colormap : ["non évaluable", "tracé", "condition1", "condition2",...,"condition n"]
                    cmap = [self.trace.expressions_condition[0]["couleur"]]
                    cmap.append(self.trace.getValue("couleur"))
                    # epaisseurs : ["non évaluable", "tracé", "condition1", "condition2",...,"condition n"]
                    epaisseurs = [self.trace.expressions_condition[0]["epaisseur"]]
                    epaisseurs.append(self.trace.getValue("epaisseur"))
                    for cond in self.trace.expressions_condition[1:] :
                        cmap.append(cond["couleur"])
                        epaisseurs.append(cond["epaisseur"])
                        
                    if self.parent.graphique.getValue("decoupageActiver") == "oui" :
                        datas_by_periode_x, seconds_by_periode_x = self.decoupe_periode(data_x, data_time_x)
                        datas_by_periode_y, seconds_by_periode_y = self.decoupe_periode(data_y, data_time_y)
                        couleurs_decoupage = self.parent.get_couleurs_decoupage()
                        periodes = list(datas_by_periode_x.keys())
                        periodes.sort()
                        i_deb_periode = 0
                        all_data_x = np.array([])
                        all_data_y = np.array([])
                        for periode in datas_by_periode_x :
                            if periode in couleurs_decoupage :
                                i_fin_periode = i_deb_periode + len(seconds_by_periode_x[periode])
                                # en mode affichage
                                if self.trace.getValue("filtrageConditionnel") == "non" :
                                    result = [ r for r in self.trace.conditions[i_deb_periode:i_fin_periode] if r != -1 ]
                                    x2 = np.ma.compressed(np.ma.array(datas_by_periode_x[periode],mask=list(map(or_,np.ma.getmaskarray(datas_by_periode_x[periode]),np.ma.getmaskarray(datas_by_periode_y[periode])))))
                                    y2 = np.ma.compressed(np.ma.array(datas_by_periode_y[periode],mask=list(map(or_,np.ma.getmaskarray(datas_by_periode_x[periode]),np.ma.getmaskarray(datas_by_periode_y[periode])))))                        
                                else :
                                # en mode filtrage
                                    x2_filtre = np.ma.array(datas_by_periode_x[periode],mask=[False if r>1 else True for r in self.trace.conditions[i_deb_periode:i_fin_periode]])
                                    x2 = np.ma.compressed(np.ma.array(x2_filtre,mask=list(map(or_,np.ma.getmaskarray(datas_by_periode_x[periode]),np.ma.getmaskarray(datas_by_periode_y[periode])))))
                                    y2_filtre = np.ma.array(datas_by_periode_y[periode],mask=[False if r>1 else True for r in self.trace.conditions[i_deb_periode:i_fin_periode]])
                                    y2 = np.ma.compressed(np.ma.array(y2_filtre,mask=list(map(or_,np.ma.getmaskarray(datas_by_periode_x[periode]),np.ma.getmaskarray(datas_by_periode_y[periode])))))
                                    result = [ r for r in self.trace.conditions[i_deb_periode:i_fin_periode] if r>1 ]
                                if len(x2) == 0  :
                                    i_deb_periode = i_fin_periode
                                    continue
                                # on place la couleur du tracé en 2eme position (on converti avant de (r, g, b, a) en #rrggbbaa )
                                couleur_trace = "#{:02x}{:02x}{:02x}".format(*tuple([int(val*255) for val in couleurs_decoupage[periode][0:3]]))
                                cmap[1] = couleur_trace
                                # tableau des couleurs
                                couleurs = []
                                for r in result :
                                    couleurs.append(cmap[r])
                                # tableau des epaisseurs
                                size = []
                                for r in result :
                                    size.append(epaisseurs[r])
                                if periode in couleurs_decoupage :                    
                                    ax.scatter(x2, y2, c=couleurs, edgecolors='none', marker=self.trace.getValue("marqueur"), s=size, zorder=2.5)
                                all_data_x = np.append(all_data_x, x2)
                                all_data_y = np.append(all_data_y, y2)
                            i_deb_periode = i_fin_periode
                        ax.set_xlim([np.min(all_data_x), np.max(all_data_x)])
                        ax.set_ylim([np.min(all_data_y), np.max(all_data_y)])
                        # en mode filtrage on recalcule la regression avec les données soumises aux conditions
                        if self.trace.getValue("filtrageConditionnel") == "oui" :
                            self.trace.calculRegression(all_data_x, all_data_y)
                            data_x_regression = np.ma.array(all_data_x)
                    else : 
                        # en mode affichage
                        if self.trace.getValue("filtrageConditionnel") == "non" :
                            result = [ r for r in self.trace.conditions if r != -1 ]
                            x2 = np.ma.compressed(np.ma.array(self.trace.data_x,mask=list(map(or_,np.ma.getmaskarray(self.trace.data_x),np.ma.getmaskarray(self.trace.data_y)))))
                            y2 = np.ma.compressed(np.ma.array(self.trace.data_y,mask=list(map(or_,np.ma.getmaskarray(self.trace.data_x),np.ma.getmaskarray(self.trace.data_y)))))                        
                        else :
                        # en mode filtrage
                            x2_filtre = np.ma.array(self.trace.data_x,mask=[False if r>1 else True for r in self.trace.conditions])
                            x2 = np.ma.compressed(np.ma.array(x2_filtre,mask=list(map(or_,np.ma.getmaskarray(self.trace.data_x),np.ma.getmaskarray(self.trace.data_y)))))
                            y2_filtre = np.ma.array(self.trace.data_y,mask=[False if r>1 else True for r in self.trace.conditions])
                            y2 = np.ma.compressed(np.ma.array(y2_filtre,mask=list(map(or_,np.ma.getmaskarray(self.trace.data_x),np.ma.getmaskarray(self.trace.data_y)))))
                            result = [r for r in self.trace.conditions if r>1]
    
                        if len(x2) == 0  :
                            message = "Condition non remplie pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
                            self.trace.coeff_a = None # suffit pour ne pas tracer la légende de regression
                            return message
                        label_legende=''
                        if self.trace.getValue("legendeVisible") == "oui" :
                            label_legende = ""+self.trace.getLegende()
                        # tableau des couleurs
                        couleurs = []
                        for r in result :
                            couleurs.append(cmap[r])
                        # tableau des epaisseurs
                        size = []
                        for r in result :
                            size.append(epaisseurs[r])
                        marqueur = self.trace.getValue("marqueur")
                        if marqueur == "None" :
                            marqueur = "."
                            
                        ax.scatter(x2, y2, c=couleurs, edgecolors='none', marker=marqueur, s=size, zorder=2.5)
                        ax.set_xlim([np.ma.min(x2), np.ma.max(x2)])
                        ax.set_ylim([np.ma.min(y2), np.ma.max(y2)])
                        # en mode filtrage on recalcule la regression avec les données soumises aux conditions
                        if self.trace.getValue("filtrageConditionnel") == "oui" :
                            self.trace.calculRegression(np.ma.array(x2), np.ma.array(y2))
                            data_x_regression = np.ma.array(x2)
                
                # regression ?
                if self.trace.getValue("regression") == "oui" :
                    # tracé de la droite
                    try :
                        ax.plot( data_x_regression , self.trace.data_regression , color = self.trace.getValue("couleur") , rasterized=True)
                    except :
                        pass
        else :
            if self.trace.vecteur_x is None or len(np.ma.compressed(self.trace.data_x)) == 0 :
                message = "Pas de données sur la période pour {} {}.".format(self.trace.getValue("plateforme_x"), self.trace.getValue("parametre_x"))
            else :
                message = "Pas de données sur la période pour {} {}.".format(self.trace.getValue("plateforme"), self.trace.getValue("parametre"))

        return message
    

    
class GtraceHisto(Gtrace):
    """
        Classe qui définit un graphique 'tracé de type Histo'
    """
    def __init__(self, trace, parent):
        Gtrace.__init__(self, trace, parent)
                
    def draw(self):
        message = ""
        numTrace = self.parent.gtraces.index(self)+1
        numGraphique = self.parent.parent.ggraphiques.index(self.parent)+1
        numPage = self.parent.parent.parent.gpages.index(self.parent.parent)+1
        if self.trace.vecteur_y != None :
            data_y = self.trace.data_y.copy()
            data_time = self.trace.vecteur_y.time.copy()
            ax = self.parent.subplot # un seul axe pour Histo : le subplot
            # Tracé conditionnel (sert de filtre pour les histo)
            if len(self.trace.expressions_condition) == 2 :
                self.trace.nb_manquants = 0
                self.trace.pourcent_manquants = 0.0
                if len(data_y) == 0 :
                    message = "Condition non remplie pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
                    return message
                # on filtre avec les conditions
                mask = [False if r>1 else True for r in self.trace.conditions]
                data_y = np.ma.compressed(np.ma.array(data_y,mask=mask))
                if len(data_y) == 0 :
                    message = "Condition non remplie pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
                    return message
                data_time = np.ma.compressed(np.ma.array(data_time,mask=mask))
            else : # tracé non conditionnel on compte les valeurs manquantes
                try :
                    self.trace.nb_manquants = np.ma.count_masked(data_y)
                    self.trace.pourcent_manquants = (float(self.trace.nb_manquants)/len(data_y))*100.
                except :
                    pass        
                
            
            if self.trace.parent.traces.index(self.trace) == 0 :
                alpha = 1.0
            else : 
                alpha = 0.5
            auto = True
            # on positionne le min et le max de l'échantillon
            if self.trace.getValue("minHisto") != self.trace.getDefault("minHisto") :
                auto = False
                minHisto = float(self.trace.getValue("minHisto"))
            else :
                minHisto = np.ma.min(data_y)
                
            if self.trace.getValue("maxHisto") != self.trace.getDefault("maxHisto") :
                auto = False
                maxHisto = float(self.trace.getValue("maxHisto"))
            else :
                maxHisto = np.ma.max(data_y)
            # si on a choisit une amplitude de classe on est plus en mode auto        
            if self.trace.getValue("amplitudeClassesHisto") != self.trace.getDefault("amplitudeClassesHisto") :
                auto = False
            
            label_legende=''
            if self.trace.getValue("legendeVisible") == "oui" :
                label_legende = ""+self.trace.getLegende()
                
            if self.parent.graphique.getValue("norme") == "oui" :
                normed = True
            else :
                normed = False    
            
            
            if self.parent.graphique.getValue("decoupageActiver") == "oui" :
                datas_by_periode, seconds_by_periode = self.decoupe_periode(data_y, data_time)
                couleurs_decoupage = self.parent.get_couleurs_decoupage()
                periodes = list(couleurs_decoupage.keys())
                periodes.sort()
                datas = [ datas_by_periode[p] for p in periodes]
                couleurs = [ couleurs_decoupage[p] for p in periodes]
                weights = [np.ones_like(datas_by_periode[p])/float(len(np.ma.compressed(data_y))) for p in periodes]
            else :
                datas = data_y
                        
            if auto == False :
                # calcul des bins
                if minHisto > maxHisto :
                    message = "Le max de l'histogramme est inférieur au min."
                else :
                    minData = np.ma.min(data_y)
                    maxData = np.ma.max(data_y)                         
                    bins = self.getBins(minHisto, maxHisto, minData, maxData)
                    # trace de l'histogramme
                    if self.parent.graphique.getValue("decoupageActiver") == "oui" :
                        if normed :
                            self.trace.counts, self.trace.bins, _  = ax.hist(datas,bins=bins,
                                        histtype='bar', stacked=True, fill=True,
                                        label=label_legende,
                                        color=couleurs,
                                        weights=weights,
                                        rasterized = False
                                        )
                        else :
                            self.trace.counts, self.trace.bins, _  = ax.hist(datas,bins=bins,
                                    histtype='bar', stacked=True, fill=True,                                         
                                    label=label_legende,
                                    color=couleurs,
                                    rasterized = False
                                    )
                    else :
                        if normed :
                            weights = np.ones_like(np.ma.compressed(datas))/float(len(np.ma.compressed(datas)))
                            self.trace.counts, self.trace.bins, _  = ax.hist(np.ma.compressed(datas),bins=bins,
                                    label=label_legende,
                                    color=self.trace.getValue("couleur"),
                                    alpha = alpha,
                                    weights=weights,
                                    rasterized = False
                                    )
                        else :
                            self.trace.counts, self.trace.bins, _  = ax.hist(np.ma.compressed(datas),bins=bins,
                                    label=label_legende,
                                    color=self.trace.getValue("couleur"),
                                    alpha = alpha,
                                    rasterized = False
                                    )
            else :
                if self.parent.graphique.getValue("decoupageActiver") == "oui" :
                    if normed :
                        self.trace.counts, self.trace.bins, _  = ax.hist(datas,self.trace.getValue("nombreClassesHisto"),
                                    histtype='bar', stacked=True, fill=True,
                                    label=label_legende,
                                    color=couleurs,
                                    weights=weights,
                                    rasterized = False
                                    )
                    else :
                        self.trace.counts, self.trace.bins, _  = ax.hist(datas,self.trace.getValue("nombreClassesHisto"),
                                histtype='bar', stacked=True, fill=True,                                         
                                label=label_legende,
                                color=couleurs,
                                rasterized = False
                                )
                else :
                    if normed :
                        weights = np.ones_like(np.ma.compressed(data_y))/float(len(np.ma.compressed(data_y)))
                        self.trace.counts, self.trace.bins, _  = ax.hist(np.ma.compressed(data_y),self.trace.getValue("nombreClassesHisto"),
                                label=label_legende,
                                color=self.trace.getValue("couleur"),
                                alpha = alpha,
                                weights=weights,
                                rasterized = False
                                )
                    else :
                        self.trace.counts, self.trace.bins, _  = ax.hist(np.ma.compressed(data_y),self.trace.getValue("nombreClassesHisto"),
                                label=label_legende,
                                color=self.trace.getValue("couleur"),
                                alpha = alpha,
                                rasterized = False
                                )
            if self.trace.getValue("amplitudeClassesHisto") == self.trace.getDefault("amplitudeClassesHisto") :
                self.amplitudeClasse = (np.ma.max(data_y) - np.ma.min(data_y))*1.0 / self.trace.getValue("nombreClassesHisto")
            else :
                self.amplitudeClasse = self.trace.getValue("amplitudeClassesHisto")
        else :
            if self.trace.getValue("plateforme") == self.trace.getDefault("plateforme") :
                message = "Plateforme non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            elif self.trace.getValue("parametre") == self.trace.getDefault("parametre") :
                message = "Paramètre non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            else :
                message = "Pas de données sur la période pour {} {}.".format(self.trace.getValue("plateforme"), self.trace.getValue("parametre"))
   
        return message

    
class GtraceHisto3D(Gtrace):
    """
        Classe qui définit un graphique 'tracé de type Histo3D'
    """
    def __init__(self, trace, parent):
        Gtrace.__init__(self, trace, parent)
        
    def draw(self):
        message = ""
        numTrace = self.parent.gtraces.index(self)+1
        numGraphique = self.parent.parent.ggraphiques.index(self.parent)+1
        numPage = self.parent.parent.parent.gpages.index(self.parent.parent)+1
        if self.trace.vecteur_y != None :
            data_y = self.trace.data_y.copy()
            ax = self.parent.subplot
            # Tracé conditionnel (sert de filtre pour les histo)
            if len(self.trace.expressions_condition) == 2 :
                self.trace.nb_manquants = 0
                self.trace.pourcent_manquants = 0.0
                if len(data_y) == 0 :
                    message = "Condition non remplie pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
                    return message
                # on filtre avec les conditions
                data_y = np.ma.compressed(np.ma.array(data_y,mask=[False if r>1 else True for r in self.trace.conditions]))
            else : # tracé non conditionnel on compte les valeurs manquantes
                try :
                    self.trace.nb_manquants = np.ma.count_masked(data_y)
                    self.trace.pourcent_manquants = (float(self.trace.nb_manquants)/len(data_y))*100.
                except :
                    pass
                
            if self.parent.graphique.getValue("norme") == "oui" :
                normed = True
            else :
                normed = False
            ax = self.parent.subplot
            auto = True
            # on positionne le min et le max de l'échantillon
            mini, maxi = self.parent.getMinMax()
            if self.parent.graphique.getValue("minHisto") != self.parent.graphique.getDefault("minHisto") :
                auto = False
                minHisto = float(self.parent.graphique.getValue("minHisto"))
            else :
                minHisto = mini
                
            if self.parent.graphique.getValue("maxHisto") != self.parent.graphique.getDefault("maxHisto") :
                auto = False
                maxHisto = float(self.parent.graphique.getValue("maxHisto"))
            else :
                maxHisto = maxi
            
            # si on a choisit une amplitude de classe on est plus en mode auto        
            if self.parent.graphique.getValue("amplitudeClassesHisto") != self.parent.graphique.getDefault("amplitudeClassesHisto") :
                auto = False
            
            if auto == False :
                if minHisto > maxHisto :
                    message = "Le max de l'histogramme est inférieur au min."
                else :
                    bins, _fmt = self.parent.getBinsGraphique()
                    if normed :
                        weights = np.ones_like(data_y)/float(len(data_y))
                        hist, bin_edges = np.histogram(data_y, bins, weights=weights, range=(min(bins),max(bins)))
                    else :
                        hist, bin_edges = np.histogram(data_y, bins, range=(min(bins),max(bins)))
                    self.trace.counts = hist
                    self.parent.graphique.bins = bins
                    amplitude = np.diff(bins)
                    position_trace = self.parent.getPositionTrace(self)
                    color = ColorConverter().to_rgba(self.trace.getValue("couleur"), 1)
                    color_transp = ColorConverter().to_rgba(self.trace.getValue("couleur"), 0)
                    colors = [color if x != 0 else color_transp for x in hist]
                    epaisseur = (2*self.parent.graphique.getValue("epaisseurBarre"))/100.
                    amplitude = (amplitude*self.parent.graphique.getValue("largeurBarre"))/100.
                    hist = [0.1 if x==0 else x for x in hist ] # ack : on remplace les 0 par 0.1 sinon le pdf plante
                    ax.bar3d(list(bins)[:-1],[position_trace]*len(hist),[0]*len(hist),amplitude,epaisseur,hist,color=colors, linewidth=0)
            else :
                if normed :                        
                    weights = np.ones_like(data_y)/float(len(data_y))
                    hist, bin_edges = np.histogram(data_y, self.parent.graphique.getValue("nombreClassesHisto"), range=(minHisto,maxHisto), weights=weights)
                else :
                    hist, bin_edges = np.histogram(data_y, self.parent.graphique.getValue("nombreClassesHisto"), range=(minHisto,maxHisto))
                self.trace.counts = hist
                self.parent.graphique.bins = bin_edges
                amplitude = np.diff(bin_edges)
                position_trace = self.parent.getPositionTrace(self)
                color = ColorConverter().to_rgba(self.trace.getValue("couleur"), 1)
                color_transp = ColorConverter().to_rgba(self.trace.getValue("couleur"), 0)
                colors = [color if x != 0 else color_transp for x in hist]
                hist = [0.1 if x==0 else x for x in hist ] # ack : on remplace les 0 par 0.1 sinon le pdf plante                 
                epaisseur = (2*self.parent.graphique.getValue("epaisseurBarre"))/100.
                amplitude = (amplitude*self.parent.graphique.getValue("largeurBarre"))/100.
                ax.bar3d(list(bin_edges)[:-1],[position_trace]*len(hist),[0]*len(hist),amplitude,epaisseur,hist,color=colors, linewidth=0)
        else :
            if self.trace.getValue("plateforme") == self.trace.getDefault("plateforme") :
                message = "Plateforme non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            elif self.trace.getValue("parametre") == self.trace.getDefault("parametre") :
                message = "Paramètre non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            else :
                message = "Pas de données sur la période pour {} {}.".format(self.trace.getValue("plateforme"), self.trace.getValue("parametre"))

        return message

    
class GtraceRDV(Gtrace):
    """
        Classe qui définit un graphique 'tracé de type RDV'
    """
    def __init__(self, trace, parent):
        Gtrace.__init__(self, trace, parent)

    def draw(self):
        message = ""
        numTrace = self.parent.gtraces.index(self)+1
        numGraphique = self.parent.parent.ggraphiques.index(self.parent)+1
        numPage = self.parent.parent.parent.gpages.index(self.parent.parent)+1
        
        if self.trace.vecteur_x != None  and len(np.ma.compressed(self.trace.data_x))!=0 and self.trace.vecteur_y != None and len(np.ma.compressed(self.trace.data_y))!=0:
            try :
                self.trace.nb_manquants = np.ma.count_masked(self.trace.data_y)
                self.trace.pourcent_manquants = (float(self.trace.nb_manquants)/len(self.trace.data_y))*100.
            except :
                pass
            
            bins, _ = self.parent.getBinsGraphique()
            ax = self.parent.subplot
            nsecteurs = self.parent.graphique.getValue("secteursRDV")
            type_rdv = self.parent.graphique.getValue("typeRDV")
            if self.parent.graphique.getValue("roseStandard") == "oui" :
                bins = [1.5, 3, 7, 12]
            self.parent.graphique.bins = bins
            if self.parent.graphique.getValue("reversePaletteRDV") == "oui" :
                palette_couleur = self.parent.couleursRDVReverse[self.parent.graphique.getValue("couleurRDV")]
            else :
                palette_couleur = self.parent.couleursRDV[self.parent.graphique.getValue("couleurRDV")]
            x2 = np.ma.compressed(np.ma.array(self.trace.data_x,mask=list(map(or_,np.ma.getmaskarray(self.trace.data_x),np.ma.getmaskarray(self.trace.data_y)))))
            y2 = np.ma.compressed(np.ma.array(self.trace.data_y,mask=list(map(or_,np.ma.getmaskarray(self.trace.data_x),np.ma.getmaskarray(self.trace.data_y)))))
            if type_rdv == 0 :
                ax.contourf(x2, y2, nsector=nsecteurs, bins=bins, cmap=palette_couleur, rasterized=False)#@UndefinedVariable
            elif type_rdv == 1 :
                ax.bar(x2, y2, nsector=nsecteurs, bins=bins, opening=0.8, edgecolor='white',cmap=palette_couleur, rasterized=False)#@UndefinedVariable
            elif type_rdv == 2 :
                ax.box(x2, y2, nsector=nsecteurs, bins=bins, cmap=palette_couleur, rasterized=False)#@UndefinedVariable
            self.parent.graphique.info_rdv = ax._info
        else :
            if self.trace.getValue("plateforme") == self.trace.getDefault("plateforme") :
                message = "Plateforme non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            elif self.trace.getValue("parametre_x") == self.trace.getDefault("parametre_x") :
                message = "Paramètre dd non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            elif self.trace.getValue("parametre") == self.trace.getDefault("parametre") :
                message = "Paramètre ff non valide pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
            else :
                message = "Pas de données de rose des vents sur la période pour {}.".format(self.trace.getValue("plateforme"))
        
        return (message)
 
        
class GtraceHov(Gtrace):
    """
        Classe qui définit un graphique 'tracé de type Hov'
    """
    def __init__(self, trace, parent):
        Gtrace.__init__(self, trace, parent)
    
    def draw(self):
        message = ""
        numTrace = self.parent.gtraces.index(self)+1
        numGraphique = self.parent.parent.ggraphiques.index(self.parent)+1
        numPage = self.parent.parent.parent.gpages.index(self.parent.parent)+1
        zorder = 1 # en dessous des tracés ST éventuellement superposés
        if self.trace.vecteur_y != None :
            #ax = self.parent.subplot
            ax = self.axe_y
            # On retravaille les données en fonction du type de hovmöller et de dim_array :
            # si dim_array == 1 et que l'on a un seul graphique, on trace les minutes en ordonnées 
            # et le temps en abscisses.
            typeHov = self.trace.getValue("typeHov")
            try :
                dim_array = int(AIDA.get_dim_array(self.trace.vecteur_y.attributes["dim_array"])[0])
            except :
                dim_array = 1
            if dim_array == 1 :
                duree = vd.duree(self.trace.debut, self.trace.fin)
                nb_time_jour = int(len(self.trace.vecteur_y.time)/duree)
                if duree == 1 :
                    # z.shape doit être au moins = (2,2) pour utiliser contourf, on force le mode auto
                    # pour utiliser pcolormesh
                    typeHov = "auto"
                if typeHov == "auto" or '%' in typeHov :
                    # on ajoute 1 a x et y pour visualiser les valeurs aux limites(cf. doc pcolor)                      
                    x = np.array([ vd.toDate(vd.add(self.trace.debut,j)) for j in range(duree+1)])
                    y = self.trace.vecteur_y.time[0:nb_time_jour]
                    y = np.append(y, y[-1])
                else :
                    x = np.array([ vd.toDate(vd.add(self.trace.debut,j)) for j in range(duree)])
                    y = self.trace.vecteur_y.time[0:nb_time_jour]
                try :
                    z = self.trace.data_y.reshape(duree, nb_time_jour).T
                except :
                    message_hov = "le graphique Hovmöller exige des données sur la même base de temps pour {} {}.".format(self.trace.getValue("plateforme"), self.trace.getValue("parametre"))
                    return message_hov
                xv = x
                yv = y
            else :
                bornes = self.trace.vecteur_y.bornes
                if bornes is None :
                    message_hov = "Bornes absentes ou illisibles dans les données pour {} {}.".format(self.trace.getValue("plateforme"), self.trace.getValue("parametre"))
                    return message_hov
                y = np.array(bornes[:,:,0], dtype = float)
                if typeHov == "auto" or '%' in typeHov :
                    x = np.array(self.trace.vecteur_y.time)
                    # on rajoute une valeur à x et y (cf. doc pcolor)
                    mini = x[-1]- x[-2]
                    x = np.append(x,x[-1]+mini)
                    # y est de dimension2, on duplique sur les 2 dimensions
                    y = np.insert(y, y.shape[1], y[0][-1], axis=1)
                    y = np.append(y,[y[-1]], axis=0)                        
                else :
                    x = np.array(self.trace.vecteur_y.time)
                # conversion en datetime sinon contourf ne sait pas convertir après meshgrid
                #x = np.array([vd.datetimeFromOrdinal(o) for o in x])
                # bornes : pour éviter tout cas particulier, on a forcé AIDA.strBornes_to_array 
                # à retourner un tableau 2D avec toutes les valeurs (en forcant NbVal dans vectFromDate).
                # On prépare les données pour le tracé (xv,yv) en simulant un meshgrid
                yv = y.T
                xv = np.full((len(yv),len(x)), x)    
                z = self.trace.data_y.T
                
            if self.trace.getValue("reversePaletteHov") == "oui" :
                palette_couleur = self.parent.couleursHovReverse[self.trace.getValue("couleurHov")]
            else :
                palette_couleur = self.parent.couleursHov[self.trace.getValue("couleurHov")]
           
            # Tracé du hovmöller en fonction du type
            if self.trace.getValue("seuilAutoHov") == "oui" :
                vmin = np.min(z)
                vmax = np.max(z)
                extend = "neither"
            else :
                vmin = self.trace.getValue("seuilMinHov")
                vmax = self.trace.getValue("seuilMaxHov")
                if self.trace.getValue("horsGammeVisibleHov") == "non" :
                    palette_couleur.set_under('1.0')
                    palette_couleur.set_over('1.0')
                else :
                    palette_couleur.set_under(palette_couleur(1))
                    palette_couleur.set_over(palette_couleur(palette_couleur.N-1))
                extend = "both"
            bounds=np.linspace(vmin,vmax,100)
            colorbar = False
            try :
                if "shading" in typeHov :
                    contour = ax.contourf(xv, yv, z, 100, cmap=palette_couleur, vmin=vmin, vmax=vmax, extend=extend, levels=bounds, zorder=zorder)
                    # hack : en pdf les lignes de contours sont visibles (bug). 
                    #        Pour corriger ça on fixe une épaisseur très fine
                    for c in contour.collections:
                        c.set_edgecolor("face")
                        c.set_linewidth(0.000000000001)
                        c.set_rasterized(True)

                    colorbar = True
                if "iso" in typeHov :
                    linewidth = round(1*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
                    contour = ax.contour(xv, yv, z, 10, colors=('black'), linewidths=linewidth, zorder=zorder)
                    for c in contour.collections:
                        c.set_rasterized(True)
                    fontsize = round(9*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
                    ax.clabel(contour, fontsize=fontsize, use_clabeltext=True)
                    
                if typeHov == "auto" or '%' in typeHov :
                    if '%' in typeHov :
                        if dim_array > 1:
                            # on calcule l'écart mini entre 2 niveaux en ne tenant pas compte de la
                            # dernière valeur, dupliquée plus haut.
                            mini = min(np.diff(y[0][:-1]))
                            largeur = int(typeHov.strip()[0:-1])
                            delta = mini*largeur/100.
                            # on insère des niveaux intermédiaires pour lesquels z vaut np.nan
                            z2 = np.ones(z.shape)*np.nan
                            z = np.hstack([z, z2]).reshape(z.shape[0]*2, z.shape[1])
                            xv = np.hstack([xv, xv]).reshape(xv.shape[0]*2, xv.shape[1])[:-1]
                            yv = np.hstack([yv, yv+delta]).reshape(yv.shape[0]*2, yv.shape[1])[:-1]
                        else :
                            message_hov = "On force Hovmöller en mode auto (dim_array = 1) pour le tracé n°{}, graphique n°{} de la page {}".format(numTrace, numGraphique, numPage)
                    contour = ax.pcolormesh(xv, yv, z, cmap=palette_couleur, vmin=vmin, vmax=vmax, rasterized=False, zorder=zorder)
                    colorbar = True
                    
            except Exception as e :
                print(e)
                return message_hov
                
            if colorbar :
                cbar = plt.colorbar(contour, extend=extend)
                size = round(8*self.parent.parent.getZoom()/self.parent.parent.ratioPixel,5)
                try :
                    unite = self.trace.vecteur_y.attributes['unit']
                except :
                    unite = "unknown"
                cbar.ax.set_ylabel(unite, size=size)
                cbar.ax.tick_params(labelsize=size)
            
            if dim_array == 1 :
                ax = plt.gca()
                ax.yaxis_date()
                ax.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.yaxis.set_major_locator(mdates.HourLocator())
        
            # Tracé du quiver
           
            if self.trace.getValue("quiverHov") == "oui" :
                try :
                    time = self.trace.data_quiver[2] 
                    bornes = self.trace.data_quiver[3]
                    u = self.trace.data_quiver[0]
                    v = self.trace.data_quiver[1]               
                    ax = plt.gca()
                    ax.quiver(time, bornes, u, v, units='xy')
                except :
                    message ="""                    Impossible d'afficher les quivers : vérifier que les données existent,
                    qu'elles sont bien de dimension 2 et qu'elles ont la même taille que
                    la donnée hovmöller."""                               
        else :
            message = "Pas de données sur la période pour {} {}".format(self.trace.getValue("plateforme"), self.trace.getValue("parametre"))         
        return message

                            
class Main :
    """
        La classe principale
    """
    pass
             
if __name__ == "__main__":
    Main()
