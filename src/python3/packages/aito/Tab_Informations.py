#!/usr/bin/env python3

"""
AITO
    Gestion de page Informations.
"""

import sys
import os
import logging
from   enum import Enum

from PyQt5.QtWidgets import (QWidget,
                             QPushButton, QLabel, QStackedWidget,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QScrollArea,
                             QSizePolicy,
                            )
from PyQt5.QtGui     import (QFont,
                            )
from PyQt5.QtCore    import (Qt,
                             pyqtSignal,
                            )

PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from AITO_icons                    import icons
from Map                           import Map
from Stack_Informations_plateforme import Stack_Informations_plateforme
from Stack_Informations_campagne   import Stack_Informations_campagne

logger = logging.getLogger('aito')


class Tab_Informations(QWidget):
    """ Gestion de page Informations.
    """

    # signal de mise à jour de l'indicateur de progression
    in_progress_signal = pyqtSignal(int)


    # stack <-> index du QStackedWidget
    class stack_index (Enum):
        STACK_PLTF  = 0
        STACK_CAMP  = 1


    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Tab_Informations::__init__")

        self.parent    = kwargs.get('parent', None)

        # récupérer les objets de l'application (models, gest_XXX...)
        self.models    = self.parent.models
        self.gest_camp = self.models['campagne'].gest_camp
        self.gest_pltf = self.models['plateforme'].gest_pltf

        # récupérer les informations des plateformes fixes
        desc_pltfs = dict()
        for pltf in self.gest_pltf.get_names():
            desc = self.gest_pltf.get_description(pltf)
            if desc:
                desc_pltfs[pltf] = desc

        # gestion de la carte
        self.map = Map(desc_pltfs)

        # mise en place de l'IHM
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.

            NOTE : sur la même 'surface', affichage soit d'une carte, soit
                   d'un label "pas de localisation"
        """
        logger.log(logging.RUN, "Tab_Informations::setup_ihm")

        # les widgets graphiques
        # - map (soit le self.label_no_bounds, soit le self.widget_map)
        self.label_no_bounds       = QLabel("<b>Aucune donnée de localisation.</b>")
        self.widget_map            = self.map.get_widget()

        # - widget stackés des informations textuelles de plateforme et campagne
        self.stack                 = QStackedWidget (self)
        stack_plateforme           = Stack_Informations_plateforme(parent=self)
        stack_campagne             = Stack_Informations_campagne(parent=self)

        # - une scrollarea pour ranger tout çaA sauf la map
        scroll_area                = QScrollArea(self)
        scroll_area_content        = QWidget()
        layout_scroll_area_content = QVBoxLayout()

        # affinage
        width  = 639
        height = 479
        try:
            width  = self.widget_map.frameGeometry().width()
            height = self.widget_map.frameGeometry().height()
        except Exception as e:
            logger.debug(f"pas de map !")
        self.label_no_bounds.setMinimumSize(width, height)
        self.label_no_bounds.setAlignment(Qt.AlignCenter)
        scroll_area.setWidgetResizable(True)
        scroll_area_content.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                      QSizePolicy.Fixed))
        scroll_area_content.setLayout(layout_scroll_area_content)

        # rangement de la stack
        self.stack.addWidget(stack_plateforme)
        self.stack.addWidget(stack_campagne)

        # rangement du scroll_area
        # - stack
        layout_scroll_area_content.addWidget(self.stack)
        layout_scroll_area_content.addStretch()

        # ranger le scroll_area_content dans la scroll_area
        scroll_area.setWidget(scroll_area_content)

        # rangement de tout ça dans le layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.widget_map)
        layout.addWidget(scroll_area)

        # positionnement du layout
        self.setLayout(layout)

        # connexions

        return


    # Gestion des informations de CAMPAGNE
    def show_campagne_detail(self):
        """ Affiche les détails de la campagne
        """
        logger.log(logging.RUN, "Tab_Informations::show_campagne_detail")

        sender = self.sender()
        name   = sender.name

        # récupérer le header de la campagne
        infos = self.gest_camp.get_header_infos(name)

        if sender.opened:
            sender.opened = False
            sender.setIcon(icons['right_arrow'])
            sender.label_widget.setHidden(True)
        else:
            sender.opened = True
            sender.setIcon(icons['down_arrow'])
            if sender.label_widget.text() == '':
                content = '\n'.join( [ f"{k:22s} : {v}"
                                        for k, v in infos.items() ] )
                sender.label_widget.setText(content)
            sender.label_widget.setWordWrap(True)
            sender.label_widget.setHidden(False)

        return


    def update_page_campagne(self, camp_name=None):
        """ Mise à jour pour une campagne :
            - la carte de la campagne et de ses plateformes.
              (la carte existante est supprimée et la nouvelle est re-crée)
            - la partie textuelle
        """
        logger.log(logging.RUN, f"Tab_Informations::update_page_campagne" +\
                                f"camp_name = {camp_name}")

        # afficher la stack campagne
        self.stack.setCurrentIndex(self.stack_index.STACK_CAMP.value)
        self.stack.currentWidget().init_page(camp_name=camp_name)

        desc_camp  = None
        desc_pltfs = None

        if camp_name:
            # récupérer les informations de la campagne
            desc_camp = dict()
            desc_camp[camp_name] = self.gest_camp.get_description(camp_name)

            # récupérer les informations des plateformes de la campagne
            desc_pltfs = dict()
            for pltf in self.gest_camp.get_pltfs(camp_name):
                desc = self.gest_pltf.get_description(pltf)
                if desc:
                    desc_pltfs[pltf] = desc

        # la map
        self.update_map_campagne(camp_name, desc_camp, desc_pltfs)

        return


    def update_map_campagne(self, camp_name=None, desc_camp=None, desc_pltfs=None):
        """ Mise à jour de la carte de la campagne et de ses plateformes.
            (la carte existante est supprimée et la nouvelle est re-crée)
        """
        logger.log(logging.RUN, f"Tab_Informations::update_map_campagne" +\
                                f"camp_name = {camp_name}")

        if not self.map.import_ok:
            return

        # carte par défaut
        if camp_name == None:
            self.map.set_default_map()
        else:
            # carte sans bounding_box ni plateforme
            if desc_camp[camp_name][1] == None and desc_pltfs == {}:
                self.widget_map.hide()
                self.label_no_bounds.show()
                self.layout().takeAt(0)
                self.layout().insertWidget(0, self.label_no_bounds)

                return

            else:
                self.widget_map.show()
                self.label_no_bounds.hide()

            # créer la carte
            self.map.set_campagne(desc_camp, desc_pltfs)

        new_map = self.map.get_widget()

        # remplacement de la map si besoin
        if new_map != self.widget_map:
            # supprimer la map
            try:
                self.widget_map.deleteLater()
            except Exception as e:
                pass

            # mettre la nouvelle carte dans le layout
            self.widget_map = new_map
            self.layout().takeAt(0)
            self.layout().insertWidget(0, self.widget_map)

        return


    # Gestion des informations de PLATEFORME
    def show_plateforme_detail(self):
        """ Affiche les détails de la plateforme
        """
        logger.log(logging.RUN, f"Tab_Informations::show_plateforme_detail")

        sender = self.sender()
        name   = sender.name

        # récupérer le header de la plateforme
        infos = self.gest_pltf.get_header_infos(name)

        if sender.opened:
            sender.opened = False
            sender.setIcon(icons['right_arrow'])
            sender.label_widget.setHidden(True)
        else:
            sender.opened = True
            sender.setIcon(icons['down_arrow'])
            if sender.label_widget.text() == '':
                content = '\n'.join( [ f"{k:22s} : {v}"
                                        for k, v in infos.items() ] )
                sender.label_widget.setText(content)
            sender.label_widget.setWordWrap(True)
            sender.label_widget.setHidden(False)

        return


    def update_page_plateforme(self, pltf_name=None):
        """ Mise à jour pour une plateforme :
            - la carte de la plateforme
              (la carte existante est supprimée et la nouvelle est re-crée)
            - la partie textuelle
        """
        logger.log(logging.RUN, f"Tab_Informations::update_page_plateforme : " +\
                                f"pltf_name = {pltf_name}")

        # afficher la stack plateforme
        self.stack.setCurrentIndex(self.stack_index.STACK_PLTF.value)
        self.stack.currentWidget().init_page(pltf_name=pltf_name)

        desc_pltf = None
        position  = None

        if pltf_name:
            # récupérer la description  de la plateforme (même si sa position
            # est indéfinie
            desc_pltf = self.gest_pltf.get_description(pltf_name, force=True)
            # récupérer la position
            position = self.gest_pltf.get_position(pltf_name)


        # la map
        self.update_map_plateforme(desc_pltf, position)

        return


    def update_map_plateforme(self, desc_pltf=None, position=None):
        """ Mise à jour de la carte de la plateforme.
            (la carte existante est supprimée et la nouvelle est re-crée)
        """
        logger.log(logging.RUN, f"Tab_Informations::update_map_plateforme : " +\
                                f"desc_pltf = {desc_pltf}, position = {position}")

        if not self.map.import_ok:
            return

        # carte par défaut
        if desc_pltf == None:
            self.map.set_default_map()
        else:
            # position indéninie
            if not isinstance(position, list):
                self.widget_map.hide()
                self.label_no_bounds.show()
                self.layout().takeAt(0)
                self.layout().insertWidget(0, self.label_no_bounds)

                return

            else:
                self.widget_map.show()
                self.label_no_bounds.hide()

            # créer la carte
            self.map.zoom_on_plateforme_at(position)

        new_map = self.map.get_widget()

        # remplacement de la map si besoin
        if new_map != self.widget_map:
            # supprimer la map
            try:
                self.widget_map.deleteLater()
            except Exception as e:
                pass

            # mettre la nouvelle carte dans le layout
            self.widget_map = new_map
            self.layout().takeAt(0)
            self.layout().insertWidget(0, self.widget_map)

        return


    def update(self, **kwargs):
        """ Mise à jour de la page.

            Toute la page est toujours "reconstruite", sinon, on peut avoir
            des incohérences dans les affichages lorsqu'on descend au fond
            des hyerarchies...

            Vue 'campagne'  , filiation = 'campagne', 'plateforme', 'year', 'num'
            Vue 'plateforme', filiation = 'plateforme', 'year', 'num'
            Vue 'by_date'   , filiation = 'year', 'month', 'day', 'acqid'

            Cette méthode *doit* exister
        """
        logger.log(logging.RUN, f"Tab_Informations::update : " +\
                                f"kwargs.items = {kwargs.items()}")

        model     = kwargs.get('model'    , None)
        filiation = kwargs.get('filiation', None)
        acqid = None
        if filiation and 'num' in filiation.keys():
            pltf  = filiation['plateforme']
            year  = filiation['year']
            num   = filiation['num']
            acqid = AIDA.datapath_to_ID(os.path.join(pltf, year, num))
        elif filiation and 'acqid' in filiation.keys():
            acqid = filiation['acqid']

        # model='campagne'/'plateforme'/'by_date'
        # => si model = 'campagne'      , afficher la *stack campagne*
        #    pour tous les autres models, afficher la *stack plateforme*
        if model:
            if model == 'campagne':
                self.update_page_campagne(camp_name=None)

                camp_name = None
                if filiation and 'campagne' in filiation.keys():
                    camp_name = filiation['campagne']
                self.update_page_campagne(camp_name=camp_name)

            else:
                pltf_name=None
                if filiation and 'plateforme' in filiation.keys():
                    pltf_name = filiation['plateforme']
                elif filiation and 'acqid' in filiation.keys():
                    pltf_name, year, num = AIDA.ID_to_full(acqid)
                self.update_page_plateforme(pltf_name=pltf_name)

            if acqid:
                self.stack.currentWidget().init_acqid(acqid=acqid)

        return

