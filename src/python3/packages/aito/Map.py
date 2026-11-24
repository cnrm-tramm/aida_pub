#!/usr/bin/env python3

"""
AITO
    Gestion des cartes.
"""

import sys
import os
import logging
import io

try:
    import folium
    from   folium.plugins import MarkerCluster
    from   PyQt5.QtWebEngineWidgets import QWebEngineView
    import_ok = True
except:
    import_ok = False
    print("Attention : Map non fonctionnelle." +\
          "QtWebEngineWidgets et folium doivent être installés")


logger = logging.getLogger('aito')


class Map():
    """ Gestion des cartes.
    """

    def __init__(self, desc_fixe_balises=None):
        logger.log(logging.RUN, "Map::__init__")

        self.import_ok = import_ok

        if not import_ok:
            self.webView = None
            self.data    = None
            self.fmap    = None
            return
        else:
            self.webView = QWebEngineView()


        # initialisation de la carte par défaut
        self.default_coordinate = (43.575524, 1.374452)

        # ajouter les plateformes fixes
        self.default_balises = dict()
        if desc_fixe_balises:
            self.default_balises = desc_fixe_balises
            self.set_default_map(balise_infos=desc_fixe_balises)


    def get_widget(self):
        """ Retourne le webView contenant la map
        """
        logger.log(logging.RUN, "Map::get_widget")
        return self.webView


    def set_campagne(self, campagne_infos, pltf_infos,
                     color="#ff7800", fill_color='#ffff00'):
        """ Supprime les balises et campagnes déjà présentes et les remplaces
            par celles de campagne_infos et pltf_infos.

            Param :
                campagne_infos : dictionnaire de la forme :
                    { 'nom campagne' : [description,
                                        [[coordonnée Xmax,coordonnée Ymax],
                                         [coordonnée Xmin,coordonnée Ymin]]]}

                pltf_infos : dictionnaire de la forme :
                    { 'nom balise'   : [description,
                                        [coordonnée,coordonnée]]}
        """
        logger.log(logging.RUN, "Map::set_campagne")

        if not import_ok:
            return

        # nouvelle map
        coordinate = self.fmap.location
        self.fmap  = folium.Map(tiles      = 'OpenStreetMap',
                                zoom_start = 11,
                                location   = coordinate)

        marker_cluster = MarkerCluster().add_to(self.fmap)

        # ajout des rectangles
        for camp_name, camp_vals in campagne_infos.items():
            desc   = camp_vals[0]
            bounds = camp_vals[1]

            if not bounds:
                continue

            iframe = folium.IFrame(desc, width=500, height=200)
            popup  = folium.Popup(iframe, max_width=500)
            marker = folium.Rectangle(bounds       = bounds,
                                      color        = color,
                                      tooltip      = camp_name,
                                      popup        = popup,
                                      fill         = True,
                                      fill_color   = fill_color,
                                      fill_opacity = 0.3)
            marker_cluster.add_child(marker)

        # plateformes de la campagne
        # - maker de la plateforme + infobulle au survol + popup sur click
        # - vals = [ string, [pos, pos] ]
        if pltf_infos:
            for key, vals in pltf_infos.items():
                desc   = vals[0].replace(' ', '&nbsp;')
                bounds = vals[1]

                if not bounds:
                    continue

                marker = folium.Marker(bounds,
                                       popup   = desc,
                                       tooltip = key)
                marker_cluster.add_child(marker)

        marker_cluster.add_to(self.fmap)
        self.fmap.fit_bounds(marker_cluster.get_bounds(), padding=[60,75])

        # save map data to data object
        self.data = io.BytesIO()
        self.fmap.save(self.data, close_file=False)

        self.webView = QWebEngineView()

        # création de l'html et on vire les attribution (en les cassant)
        s = self.data.getvalue().decode().replace('attribution','attributazf')
        self.webView.setHtml(s)

        return


    def set_default_map(self, balise_infos=None, position=None):
        """ Crée la carte par défaut avec les balises fournies.
            Si la position de la balise est connue, son marker est ajouté.

            Param :
                balise_infos : dictionnaire de la forme :
                    {"nom balise":[description, [coordonnée,coordonnée]]}
        """
        logger.log(logging.RUN, "Map::set_default_map")

        if not import_ok:
            return

        # nouvelle map
        if not balise_infos:
            balise_infos = self.default_balises

        if not position:
            coordinate = self.default_coordinate
        else :
            coordinate = position

        self.fmap = folium.Map(tiles      = 'OpenStreetMap',
                               zoom_start = 11,
                               location   = coordinate)

        # positionner toutes les balises (qui ont une postion défiénie)
        # - vals = [ string, [pos, pos] ]
        marker_cluster = MarkerCluster().add_to(self.fmap)

        for key, vals in balise_infos.items():
            desc   = vals[0].replace(' ', '&nbsp;')
            bounds = vals[1]

            if not isinstance(bounds, list):
                continue

            marker = folium.Marker(bounds,
                                   popup   = desc,
                                   tooltip = key)
            marker_cluster.add_child(marker)

        # save map data to data object
        self.data = io.BytesIO()
        self.fmap.save(self.data, close_file=False)

        self.webView = QWebEngineView()

        # création de l'html et on vire les attribution (en les cassant)
        s = self.data.getvalue().decode().replace('attribution','attributazf')
        self.webView.setHtml(s)

        return


    def zoom_on_plateforme_at(self, position):
        """ Positionne la map par défaut sur la position fournie (qui est celle
            d'une plateforme)
        """
        logger.log(logging.RUN, "Map::zoom_on_plateforme_at")
        self.set_default_map(balise_infos=None, position=position)

        return

