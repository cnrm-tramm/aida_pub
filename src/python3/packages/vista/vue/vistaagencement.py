#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib as mpl
import os
if not os.environ.get('DISPLAY'):
    mpl.use('Agg')
else :
    from matplotlib import pyplot as plt
    from gi.repository import Gtk, Gdk

class ControlRectangles:
    """
        Classe controller des rectangles : gère les évènement sur la zone de tracé.
        Les rectangles sont tracés dans un canvas matplotlib, sur une grille carrée [0-100].
        L'origine du repère est en bas à gauche.
    """
    figure = None
    orientation = "portrait"
    rectangles = [] # liste des DraggableRectangle
    selection = [] # liste des DraggableRectangle sélectionnés
    poignee_selected = None # poignee sélectionnée
    rect_poignee_selected = None # rectangle auquel appartient la poignée sélectionnée
    pressed = None # le bouton gauche de la souris est enfoncé
    pressed_x = None # coordonnée x du clic
    pressed_y = None # coordonnée y du clic
    ctrl_is_held = False # booléen qui gère la touche ctrl
    labelTitre = None # widget label du titre du rectangle pointé par la souris
    
    @classmethod
    def clear(cls):
        cls.rectangles = [] # liste des DraggableRectangle
        cls.selection = [] # liste des DraggableRectangle sélectionnés
        cls.poignee_selected = None # poignee sélectionnée
        cls.rect_poignee_selected = None # rectangle auquel appartient la poignée sélectionnée
        cls.pressed = None # le bouton gauche de la souris est enfoncé
        cls.pressed_x = None # coordonnée x du clic
        cls.pressed_y = None # coordonnée y du clic
        cls.ctrl_is_held = False # booléen qui gère la touche ctrl
    
    @classmethod
    def showPoignees(cls):
        """
            Méthode de classe : affiche les poignées des rectangles sélectionnés.
        """
        for rectangle in cls.rectangles :
            if rectangle in cls.selection :
                rectangle.showPoignees(True)
            else :
                rectangle.showPoignees(False)
                
    @classmethod
    def reorder(cls, upper_rect):
        """
            Méthode de classe : passe le rectangle au premier plan..
        """
        for drect in cls.rectangles :
            if drect.nom == upper_rect.nom :
                drect.rect.zorder = 100
                drect.text.zorder = 100
            else :
                drect.rect.zorder = 1
                drect.text.zorder = 1
    
    @classmethod
    def inPoignee(cls, event):
        """
            Méthode de classe : renvoie la poignée et le rectangle associés à l'événement.
        """
        if len(cls.rectangles) == 0 :
            return None, None
        for drect in cls.rectangles :
            contains, _attrd = drect.poigneeBG.contains(event)
            if contains :
                return drect, "BG"
            contains, _attrd = drect.poigneeBD.contains(event)
            if contains :
                return drect, "BD"
            contains, _attrd = drect.poigneeHG.contains(event)
            if contains :
                return drect, "HG"
            contains, _attrd = drect.poigneeHD.contains(event)
            if contains :
                return drect, "HD"
        return None, None
                    
    @classmethod
    def inRectangle(cls, event):
        """
            Méthode de classe : retourne le rectangle sur lequel porte l'événement.
        """
        rectangle_impacte = None
        if len(cls.rectangles) == 0 :
            return None
        if event.inaxes != cls.rectangles[0].rect.axes: 
            return None
        rectangles_impactes = []
        for drect in cls.rectangles :
            contains, _attrd = drect.rect.contains(event)
            if contains :
                rectangles_impactes.append(drect)
        if len(rectangles_impactes) != 0 :
            #on cherche le rectangle dont le zorder est le plus élévé
            zorder = -1
            for r in rectangles_impactes :
                if r.rect.zorder >= zorder :
                    zorder = r.rect.zorder
        
                    rectangle_impacte = r

        return rectangle_impacte    
    
    @classmethod
    def ctrlValidite(cls):
        """
            Méthode de classe : vérifie la validités des positions des rectangles (pas d'intersection).
            On cherche les intersections entre les rectangles.
            On utilise mpl.transforms.BboxBase.intersection(bb1,bb2).
            On traite les 4 cas particuliers ou les rectangles sont collés bord à bord et pour lesquels
            le graphique est valide.
            
        """
        inter_rects = []        
        for f in cls.rectangles:
            for s in cls.rectangles:
                
                intersection = False
                bb1 = f.rect.get_bbox()
                bb2 = s.rect.get_bbox()
                # cas général : tous les cas d'intersections
                intersection = mpl.transforms.BboxBase.intersection(bb1,bb2)
                # cas particuliers
                if intersection and bb2.ymax == bb1.ymin :
                    intersection = False
                if intersection and bb2.ymin == bb1.ymax :
                    intersection = False
                if intersection and bb2.xmax == bb1.xmin :
                    intersection = False
                if intersection and bb2.xmin == bb1.xmax :
                    intersection = False    
                if intersection and f!=s :
                    inter_rects.append(f)
                    inter_rects.append(s)
        cls.updateColor(inter_rects)
        cls.figure.canvas.draw()   
                    
    @classmethod
    def getPosition(cls, idg):
        """
            Retourne la position du rectangle correspondant à l'id du graphique.
        """
        rect = [r for r in cls.rectangles if r.id == idg]
        if rect == [] :
            return None, None, None, None
        else :
            x,y = rect[0].rect.xy
            w = rect[0].rect.get_width()
            h = rect[0].rect.get_height()
            return int(x), int(y), int(w), int(h)
        
    @classmethod
    def updateColor(cls, intersection):
        """
            Méthode de classe : affiche en rouge les rectangles qui se chevauchent.
        """
        for rectangle in cls.rectangles :
            if rectangle in intersection :
                rectangle.setColor("#ff0000")
            else :
                rectangle.setColor("#aaaaaa")
            
                        
    def __init__(self, figure):
        self.figure = figure
        ControlRectangles.figure = figure
                           
    def connect(self):
        """
            Positionne les callbacks du canvas.
        """
        self.cidpress = self.figure.canvas.mpl_connect(
            'button_press_event', self.onPress)
        self.cidrelease = self.figure.canvas.mpl_connect(
            'button_release_event', self.onRelease)
        self.cidmotion = self.figure.canvas.mpl_connect(
            'motion_notify_event', self.onMotion)        
        self.cidkeypress = self.figure.canvas.mpl_connect(
            'key_press_event', self.onKeyPress2)
        self.cidkeyrelease = self.figure.canvas.mpl_connect(
            'key_release_event', self.onKeyRelease2)

    def onKeyRelease2(self, event):
        """
            Callback sur touche de clavier relaché.
        """
        key = event.key
        if key == 'ctrl+control' :
            ControlRectangles.ctrl_is_held = False
        ControlRectangles.ctrlValidite()

    def onKeyPress2(self, event):
        """
            Callback sur touche de clavier pressé.
        """
        key = event.key
        if key.lower() == 'control' :
            ControlRectangles.ctrl_is_held = True
            return
        
        if key.lower() == 'ctrl+a' :
            ControlRectangles.selection = ControlRectangles.rectangles[:]
            ControlRectangles.showPoignees()
            self.figure.canvas.draw()
            return
        
        # on travaille en coordonées mpl (0-100)
        # on vérifie qu'on reste dans la zone de tracé
        outs = []
        for r in ControlRectangles.selection :
            x,y = r.rect.xy
            h = r.rect.get_height()
            w = r.rect.get_width()
            # on agrandit le rectangle d'une unité dans tous les sens
            x = x - 1
            y = y - 1
            w = w + 2
            h = h + 2
            lims = r.movableMpl(x, y, w, h)
            outs = list(set(outs + lims))
             
        if key.lower() == "down" :
            for r in ControlRectangles.selection :
                x,y = r.rect.xy
                if "b" not in outs :
                    y -= 1
                    r.rect.xy = (x,y)
                    r.setCoordPoignees()
                    r.setCoordText()
        if key.lower() == "up":
            for r in ControlRectangles.selection :    
                x,y = r.rect.xy
                h = r.rect.get_height()
                if "h" not in outs :
                    y += 1
                    r.rect.xy = (x,y)
                    r.setCoordPoignees()
                    r.setCoordText()
        if key.lower() == "left":
            for r in ControlRectangles.selection :    
                x,y = r.rect.xy
                if "g" not in outs :
                    x -= 1
                    r.rect.xy = (x,y)
                    r.setCoordPoignees()
                    r.setCoordText()
        if key.lower() == "right":
            for r in ControlRectangles.selection :    
                x,y = r.rect.xy
                w = r.rect.get_width()
                if "d" not in outs :
                    x += 1    
                    r.rect.xy = (x,y)
                    r.setCoordPoignees()
                    r.setCoordText()
        self.figure.canvas.draw()
    

    def onKeyPress(self, w, event):
        """
            Callback sur touche de clavier pressé. Event est un événement GTK.
            Inutile depuis matplotlib-2.2.2 : on la conserve pour assure la compatibilité avec 
            la version 1.5.1
        """
        key = Gdk.keyval_name(event.keyval)

        if key == 'Control_L' or key == 'Control_R':
            ControlRectangles.ctrl_is_held = True
            return
        
        if key == 'a' and ControlRectangles.ctrl_is_held  :
            ControlRectangles.selection = ControlRectangles.rectangles[:]
            ControlRectangles.showPoignees()
            self.figure.canvas.draw()
            return
        
        # on travaille en coordonées mpl (0-100)
        # on vérifie qu'on reste dans la zone de tracé
        outs = []
        for r in ControlRectangles.selection :
            x,y = r.rect.xy
            h = r.rect.get_height()
            w = r.rect.get_width()
            # on agrandit le rectangle d'une unité dans tous les sens
            x = x - 1
            y = y - 1
            w = w + 2
            h = h + 2
            lims = r.movableMpl(x, y, w, h)
            outs = list(set(outs + lims))
             
        if key == "Down" :
            for r in ControlRectangles.selection :
                x,y = r.rect.xy
                if "b" not in outs :
                    y -= 1
                    r.rect.xy = (x,y)
                    r.setCoordPoignees()
                    r.setCoordText()
        if key == "Up":
            for r in ControlRectangles.selection :    
                x,y = r.rect.xy
                h = r.rect.get_height()
                if "h" not in outs :
                    y += 1
                    r.rect.xy = (x,y)
                    r.setCoordPoignees()
                    r.setCoordText()
        if key == "Left":
            for r in ControlRectangles.selection :    
                x,y = r.rect.xy
                if "g" not in outs :
                    x -= 1
                    r.rect.xy = (x,y)
                    r.setCoordPoignees()
                    r.setCoordText()
        if key == "Right":
            for r in ControlRectangles.selection :    
                x,y = r.rect.xy
                w = r.rect.get_width()
                if "d" not in outs :
                    x += 1    
                    r.rect.xy = (x,y)
                    r.setCoordPoignees()
                    r.setCoordText()
        self.figure.canvas.draw()
    

 
    def onKeyRelease(self, w, event):
        """
            Callback sur touche de clavier relaché. Event est un événement GTK.
            Inutile depuis matplotlib-2.2.2 : on la conserve pour assure la compatibilité avec 
            la version 1.5.1
        """
        key  = Gdk.keyval_name(event.keyval)
        if key == 'Control_L' or key == 'Control_R': #compatibilité gtk
            ControlRectangles.ctrl_is_held = False
        ControlRectangles.ctrlValidite()
                   
    def onPress(self, event):
        """
            Callback sur boutton de souris pressé.
        """
        if event.button != 1:
            return
        rectangle, poignee = self.inPoignee(event)
        if poignee is None :
            #pas de poignée sélectionnée, on vérifie si on a pas sélectionné un rectangle        
            rectangle = self.inRectangle(event)
            if rectangle is None :
                if ControlRectangles.ctrl_is_held == False :
                    ControlRectangles.selection = []
                    ControlRectangles.poignee_selected = None
                    ControlRectangles.showPoignees()
                    ControlRectangles.pressed = None               
                return
            if ControlRectangles.ctrl_is_held == False :
                if not rectangle in ControlRectangles.selection :
                    ControlRectangles.selection = []
                    ControlRectangles.selection.append(rectangle)
                    self.updateCursor("RECT")
                for r in ControlRectangles.selection :                    
                    r.pressed_x0, r.pressed_y0 = r.rect.xy
            else :
                if rectangle in ControlRectangles.selection :
                    ControlRectangles.selection.remove(rectangle)
                    self.updateCursor(None)
                else :
                    ControlRectangles.selection.append(rectangle)
                    self.updateCursor("RECT")
            ControlRectangles.pressed = True    
            ControlRectangles.pressed_x = event.xdata
            ControlRectangles.pressed_y = event.ydata
            ControlRectangles.reorder(rectangle)
            ControlRectangles.showPoignees()
        else :
            #une poignée est sélectionnée
            if rectangle not in ControlRectangles.selection :
                return
            for r in ControlRectangles.selection :                    
                    r.pressed_x0, r.pressed_y0 = r.rect.xy
            ControlRectangles.pressed = True
            ControlRectangles.pressed_x = event.xdata
            ControlRectangles.pressed_y = event.ydata
            ControlRectangles.showPoignees()
            if not rectangle in ControlRectangles.selection :
                    ControlRectangles.selection.append(rectangle)
            ControlRectangles.poignee_selected = poignee
            ControlRectangles.rect_poignee_selected = rectangle
            
        self.figure.canvas.draw()
    
    def onRelease(self, event):
        """
            Callback sur boutton de souris relaché.
        """
        ControlRectangles.poignee_selected = None 
        ControlRectangles.pressed_x = None
        ControlRectangles.pressed_y= None
        ControlRectangles.pressed = None
        ControlRectangles.ctrlValidite()
    
    def onMotion(self, event):
        """
            Callback sur souris déplacée.
        """
        if "grab_focus" in dir(self.figure.canvas) :
            self.figure.canvas.grab_focus()
        # si on est sur un rectangle, on met à jour le titre
        rectangle = self.inRectangle(event)
        if rectangle != None :
            ControlRectangles.labelTitre.set_text("{} : {}...".format(rectangle.type, rectangle.titre[0:30]))
        else :
            ControlRectangles.labelTitre.set_text("")
        if ControlRectangles.ctrl_is_held :
            return
        
        #
        # Si le bouton de la souris n'est pas enfoncé, on ne fait que changer le curseur.
        #
        # poignee ? 
        if not ControlRectangles.pressed :   
            rectangle, poignee = self.inPoignee(event)
            if poignee != None and rectangle in ControlRectangles.selection :
                self.updateCursor(poignee)
            else :
                #pas de poignée sélectionnée, on vérifie si on a pas sélectionné un rectangle        
                rectangle = self.inRectangle(event)
                if rectangle != None and rectangle in ControlRectangles.selection :
                    self.updateCursor("RECT")
                else :
                    self.updateCursor()
            return
        
        if ControlRectangles.poignee_selected != None :
            # on retaille que si tous les rectangles de la sélection sont retaillables
            dx, dy, dw, dh = ControlRectangles.rect_poignee_selected.resize(event, test=True)
            if dx != None :
                resize = True
                for r in ControlRectangles.selection :
                    x,y = r.rect.xy
                    w = r.rect.get_width()
                    h = r.rect.get_height()
                    if r.movableMpl(x+dx, y+dy, w+dw, h+dh) != [] :
                        resize = False
                if resize :
                    dx, dy, dw, dh = ControlRectangles.rect_poignee_selected.resize(event)
                    for r in ControlRectangles.selection :
                        if r != ControlRectangles.rect_poignee_selected :
                            r.resize(event, dx, dy, dw, dh)
        else :
            if event.xdata != None and event.ydata != None :
                dx = event.xdata - ControlRectangles.pressed_x
                dy = event.ydata - ControlRectangles.pressed_y
                movable = True
                if len(ControlRectangles.selection)>1 :
                    for r in ControlRectangles.selection :
                        x0 = r.pressed_x0
                        y0 = r.pressed_y0
                        if r.movable(x0+dx, y0+dy) == False :
                            movable = False
                if movable :    
                    for r in ControlRectangles.selection :    
                        x0 = r.pressed_x0
                        y0 = r.pressed_y0
                        if event.xdata != None and event.ydata != None :
                            r.move(x0+dx, y0+dy)

        self.figure.canvas.draw()
    
    def alignGrille(self, w, e, tree):
        dialog = tree.get_object("dialogAgencement2")
        spinLignes = tree.get_object("spinbuttonGrilleLignes")
        spinColonnes = tree.get_object("spinbuttonGrilleColonnes")
        spinLignes.set_value(1)
        spinColonnes.set_value(1)
        marge = 5
        hspace = 6
        vspace = 6
        response = dialog.run()
        if response == 1: # valider
            nbLignes = int(spinLignes.get_value())
            nbColonnes = int(spinColonnes.get_value())
            num=0
            for l in range(nbLignes) :
                for c in range(nbColonnes) :
                    width = int( (100 - (2*marge) - hspace*(nbColonnes-1)) / nbColonnes )
                    x = marge + c*(width + hspace)
                    height = int( (100 - (2*marge) - vspace*(nbLignes-1)) / nbLignes )
                    y = 100 - (2*marge) - (l+1)*height - (vspace*l) + marge
                    if num < len(ControlRectangles.rectangles) :
                        r = ControlRectangles.rectangles[num]
                        if r.type == "RDV" :
                            val = min(width, height)
                            width = val
                            if ControlRectangles.orientation == "portrait" :                        
                                height = int(round(val*(21/29.7)))
                            else :
                                height = int(round(val*(29.7/21)))
                        r.rect.set_x(x)
                        r.rect.set_y(y)
                        r.rect.set_width(width)
                        r.rect.set_height(height)
                        r.setCoordPoignees()
                        r.setCoordText()                  
                    num += 1
            self.figure.canvas.draw()
            ControlRectangles.ctrlValidite()  
        else :
            pass
        dialog.hide()
        
    def alignLeft(self, w, e):
        if len(ControlRectangles.selection) == 0 :
            return
        xleft = min([r.rect.xy[0] for r in ControlRectangles.selection])
        for r in ControlRectangles.selection :
            r.rect.set_x(xleft)
            r.setCoordPoignees()
            r.setCoordText()
        self.figure.canvas.draw()
        
    def alignRight(self, w, e):
        if len(ControlRectangles.selection) == 0 :
            return
        xright = max([r.rect.xy[0]+r.rect.get_width() for r in ControlRectangles.selection])
        for r in ControlRectangles.selection :
            x,y=r.rect.xy
            width = r.rect.get_width()
            if x + width != xright :
                r.rect.set_x(xright-width)
                r.setCoordPoignees()
                r.setCoordText()
        self.figure.canvas.draw()
        
    def alignBottom(self, w, e):
        if len(ControlRectangles.selection) == 0 :
            return
        ybottom = min([r.rect.xy[1] for r in ControlRectangles.selection])
        for r in ControlRectangles.selection :
            r.rect.set_y(ybottom)
            r.setCoordPoignees()
            r.setCoordText()
        self.figure.canvas.draw()
        
    def alignTop(self, w, e):
        ytop = max([r.rect.xy[1]+r.rect.get_height() for r in ControlRectangles.selection])
        for r in ControlRectangles.selection :
            x,y=r.rect.xy
            height = r.rect.get_height()
            if y + height != ytop :
                r.rect.set_y(ytop-height)
                r.setCoordPoignees()
                r.setCoordText()
        self.figure.canvas.draw()
    
    def sameWidth(self, w, e):
        wmin = min([r.rect.get_width() for r in ControlRectangles.selection])
        for r in ControlRectangles.selection :
            r.rect.set_width(wmin)
            r.setCoordPoignees()
            r.setCoordText()
        self.figure.canvas.draw()
    
    def sameHeight(self, w, e):
        hmin = min([r.rect.get_height() for r in ControlRectangles.selection])
        for r in ControlRectangles.selection :
            r.rect.set_height(hmin)
            r.setCoordPoignees()
            r.setCoordText()
        self.figure.canvas.draw()
                
    def disconnect(self):
        """
            Déconnection des callbacks.
        """
        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)
        self.figure.canvas.mpl_disconnect(self.cidkeypress)
        self.figure.canvas.mpl_disconnect(self.cidkeyrelease)
        
 
    def updateCursor(self, elmt=None):
        """
            Met à jour le curseur de la souris en fonction de l'élément sur lequel survient l'événement.
        """
        win = self.figure.canvas.get_window()
        if elmt is None :
            win.set_cursor(None)
            return
        if elmt == 'HD' :
            curs = Gdk.CursorType.TOP_RIGHT_CORNER # @UndefinedVariable
        elif elmt == 'HG' :
            curs = Gdk.CursorType.TOP_LEFT_CORNER # @UndefinedVariable
        elif elmt == 'BG' :
            curs = Gdk.CursorType.BOTTOM_LEFT_CORNER # @UndefinedVariable
        elif elmt == 'BD' :
            curs = Gdk.CursorType.BOTTOM_RIGHT_CORNER # @UndefinedVariable
        elif elmt == 'RECT' :
            curs = Gdk.CursorType.HAND1 # @UndefinedVariable
        try :        
            cursor = Gdk.Cursor(curs)  # @UndefinedVariable
            win.set_cursor(cursor)
        except Exception :
            win.set_cursor(None)
                
class DraggableRectangle:
    """
        Rectangle déplaçable et retaillable à l'aide de poignées.
    """
    def __init__(self, ax, fig, x, y, w, h, index, titre, idg, typeg):
        self.w_poignee = 0.7
        self.ax = ax
        self.nom = "rect{}".format(index)
        self.titre = titre
        self.id = idg
        self.type = typeg
        self.press = None #contient x0,y0,eventx et eventy
        self.poignee_press = None #idem
        self.rect = mpl.patches.Rectangle((x,y), w, h, facecolor='#aaaaaa', edgecolor='#000000', alpha=0.5)
        self.poigneeBG = mpl.patches.Rectangle((x-self.w_poignee,y-self.w_poignee), self.w_poignee*2, self.w_poignee*2, facecolor='#000000', edgecolor='#000000')
        self.poigneeBD = mpl.patches.Rectangle((x+w-self.w_poignee,y-self.w_poignee), self.w_poignee*2, self.w_poignee*2, facecolor='#000000', edgecolor='#000000')
        self.poigneeHG = mpl.patches.Rectangle((x-self.w_poignee,y+h-self.w_poignee), self.w_poignee*2, self.w_poignee*2, facecolor='#000000', edgecolor='#000000')
        self.poigneeHD = mpl.patches.Rectangle((x+w-self.w_poignee,y+h-self.w_poignee), self.w_poignee*2, self.w_poignee*2, facecolor='#000000', edgecolor='#000000')
        ax.add_patch(self.rect)
        ax.add_patch(self.poigneeBG)
        ax.add_patch(self.poigneeHG)
        ax.add_patch(self.poigneeBD)
        ax.add_patch(self.poigneeHD)
        self.figure = fig
        self.text = plt.text(x+(w/2),y+(h/2),"G{}".format(index))
        self.rect.zorder = index
        self.poigneeBG.zindex = 110
        self.poigneeBD.zindex = 110
        self.poigneeHG.zindex = 110
        self.poigneeHD.zindex = 110
        self.text.zorder = self.rect.zorder
        self.pressed_x0 = x
        self.pressed_y0 = y
        
        self.showPoignees(False)
        
    def setCoordText(self):
        x,y = self.rect.xy
        w = self.rect.get_width()
        h = self.rect.get_height()
        self.text.set_x(x+(w/2))
        self.text.set_y(y+(h/2))
        
    def setCoordPoignees(self):
        """
            Positionne les coordonnées des poignees
        """
        x,y = self.rect.xy
        w = self.rect.get_width()
        h = self.rect.get_height()
        self.poigneeBG.set_x(x - self.w_poignee)
        self.poigneeBG.set_y(y - self.w_poignee)
        self.poigneeBD.set_x(x + w - self.w_poignee)
        self.poigneeBD.set_y(y - self.w_poignee)
        self.poigneeHG.set_x(x - self.w_poignee)
        self.poigneeHG.set_y(y + h - self.w_poignee)
        self.poigneeHD.set_x(x + w - self.w_poignee)
        self.poigneeHD.set_y(y + h - self.w_poignee)
            
    def showPoignees(self, boole):
        """
            Affichage des poignees du rectangle.
        """
        self.poigneeBG.set_visible(boole)
        self.poigneeHG.set_visible(boole)
        self.poigneeBD.set_visible(boole)
        self.poigneeHD.set_visible(boole)
        
    def movable(self, rx, ry):
        """
            Détermine si le rectangle ne sort pas des limites.
        """
        x = int(rx)
        y = int(ry)
        w = self.rect.get_width()
        h = self.rect.get_height()
        cx, cy = self.rect.xy
        ret =True
        if x <= 0 and cx == 0  :
            ret = False
        if x + w > 100 :
            ret = False
        if y <= 0 and cy == 0 :
            ret= False
        if y + h > 100 :
            ret = False
        
        return ret
    
    def movableMpl(self, x, y, w, h):
        """
            Détermine si le rectangle n'est pas en dehors des limites dans le système de coordonnées mpl (0-100).
            Retourne la liste des limites dépassées : ["b", "h","g","d"] = toutes limites dépassées.
        """
        lims = []
        if x < 0 :
            lims.append('g')
        if x + w > 100 :
            lims.append('d')
        if y < 0 :
            lims.append('b')
        if y + h > 100 :
            lims.append('h')
        return lims
        
    def move(self, rx, ry):
        """
            Déplace le rectangle.
        """
        x = int(rx)
        y = int(ry)
        w = self.rect.get_width()
        h = self.rect.get_height()
        
        if x < 0  :
            x = 0
        if x + w > 100 :
            x = 100 - w
        if y < 0 :
            y = 0
        if y + h > 100 :
            y = 100 - h
        
        self.rect.set_x(x)
        self.rect.set_y(y)
        self.setCoordText()
        self.text.zorder = self.rect.zorder
        self.setCoordPoignees()
            
    def resize(self, event, dx=None, dy=None, dw=None, dh=None, test=False):
        """
            Modifie la taille du rectangle si test=False
            Retourne le tuplde dx, dy, dw, dh
        """
        if event.xdata is None or event.ydata is None :
            return (None, None, None, None)
        poignee = ControlRectangles.poignee_selected
        
        
        
        # coordonnées de la  poignée
        #xp = int(event.xdata) - self.w_poignee
        #yp = int(event.ydata) - self.w_poignee
        # coordonnées du rectangle
        x,y = self.rect.xy
        w = self.rect.get_width()
        h = self.rect.get_height()
        
        if dx != None : # la poignee n'appartient pas à ce rectangle, on applique les deltas.
            new_x = x + dx
            new_y = y + dy
            new_w = w + dw
            new_h = h + dh         
        else :  # c'est le rectangle auquel appartien la poignée, on utilise les coordonnées de la souris.      
            if poignee == "BG" :
                new_x = int(event.xdata)
                new_y = int(event.ydata)
                new_w = x + w - new_x
                new_h = y + h - new_y
            if poignee == "BD" :
                new_x = x
                new_y = int(event.ydata)
                new_w = int(event.xdata) - new_x
                new_h = h + y - int(event.ydata)
            if poignee == "HG" :
                new_x = int(event.xdata)
                new_y = y
                new_w = x + w - new_x
                new_h = int(event.ydata) - y
            if poignee == "HD" :
                new_x = x
                new_y = y
                new_w = int(event.xdata) - new_x
                new_h = int(event.ydata) - y
        
        if new_w < 0 :
            new_x = new_x + new_w
            new_w = new_w * -1
            if test == True :
                return (new_x-x, new_y-y, new_w-w, new_h-h)
            if poignee == "BG" :
                ControlRectangles.poignee_selected = "BD"
            if poignee == "BD" :
                ControlRectangles.poignee_selected = "BG"
            if poignee == "HG" :
                ControlRectangles.poignee_selected = "HD"
            if poignee == "HD" :
                ControlRectangles.poignee_selected = "HG"
            
        if new_h < 0 :
            new_y = new_y + new_h
            new_h = new_h * -1
            if test == True :
                return (new_x-x, new_y-y, new_w-w, new_h-h)
            if poignee == "BG" :
                ControlRectangles.poignee_selected = "HG"
            if poignee == "HG" :
                ControlRectangles.poignee_selected = "BG"
            if poignee == "BD" :
                ControlRectangles.poignee_selected = "HD"
            if poignee == "HD" :
                ControlRectangles.poignee_selected = "BD"
        if test == True :
                return (new_x-x, new_y-y, new_w-w, new_h-h)
        
        if self.type == "RDV" : # carré
            if ControlRectangles.orientation == "portrait" :
                new_h = int(round(new_w*(21.0/29.7)))
            else :
                new_h = int(round(new_w*(29.7/21.0)))
                
        self.rect.set_bounds(new_x, new_y, new_w, new_h)
        self.setCoordText()
        self.setCoordPoignees()
        
        return (new_x-x, new_y-y, new_w-w, new_h-h)
                    
    def setColor(self, couleur):
        """
            Positionne la couleur du rectangle.
        """
        self.rect.set_facecolor(couleur)



        
if __name__ == "__main__":
    mpl.rcParams['toolbar'] = 'None'        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    controller = ControlRectangles(fig)
    
    dr = DraggableRectangle(ax, fig, 10, 65, 65, 20, 1)
    ControlRectangles.rectangles.append(dr)
    
    dr = DraggableRectangle(ax, fig, 10, 45, 65, 20, 2)
    ControlRectangles.rectangles.append(dr)
    
    #dr = DraggableRectangle(ax, fig, 60, 50, 25, 45, 3)
    #ControlRectangles.rectangles.append(dr)
    
    controller.connect()
    for tl in ax.get_xticklabels() + ax.get_yticklabels():
        tl.set_visible(False)
    ax.xaxis.grid(True, zorder=100)
    ax.yaxis.grid(True, zorder=100)
    plt.xticks(list(range(0,100,5)))
    plt.yticks(list(range(0,100,5)))
    plt.xlim([0, 100])
    plt.ylim([0, 100])
    plt.show()
