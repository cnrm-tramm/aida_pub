#!/usr/bin/env python3

"""
AITO
    Point d'entrée de l'application.
"""
__version__ = '2.0.0'

import sys
import os
import logging
import datetime
import glob
import subprocess
from   enum import Enum


from PyQt5.QtWidgets import (QApplication, QMainWindow, QShortcut,
                             QWidget,
                             QMenu,
                             QTabWidget,
                             QLayout, QVBoxLayout, QHBoxLayout,
                             QPushButton,
                             QProgressBar,
                             QSizePolicy,
                             QMessageBox,
                            )
from PyQt5.QtGui     import (QKeySequence,
                            )
from PyQt5.QtCore    import (PYQT_VERSION_STR,
                             Qt, QSize, QPoint,
                             QCoreApplication, QSettings,
                             pyqtSlot, pyqtSignal,
                             QUrl,
                            )
from PyQt5.QtWebEngineWidgets import QWebEngineView

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
AIDA_LIB = os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y)
AITO_LIB = os.path.join(AIDA_LIB, 'aito')
AITO_DOC = os.path.join(AITO_LIB, 'documentations')
AITO_MAN = os.path.join(AITO_LIB, 'manual')

sys.path.append(AIDA_LIB)
sys.path.append(AITO_LIB)

import AIDA
import AIDA_logger
logger = AIDA_logger.configure_AIDA_logging('aito')

import AITO_icons
from   AITO_icons       import icons
from   Detail           import Detail
from   Importation      import Importation
from   Exportation      import Exportation
from   Gest_acqid       import Gest_acqid
from   Model_acqid      import Model_acqid
from   Model_by_date    import Model_by_date
from   Model_plateforme import Model_plateforme
from   Model_campagne   import Model_campagne


class ManuelWindow(QMainWindow):
    """ Gestion du manuel utilisateur.
    """
    def __init__(self):
        super().__init__()
        logger.log(logging.RUN, "ManuelWindow::__init")
        print("ManuelWindow::__init")

        self.setWindowTitle('Aide aito')

        self.setMinimumWidth (903)
        self.setMinimumHeight(607)
        self.move(200, 300)

        url = f'file://{AITO_MAN}/index.html'
        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)



class MainWindow(QMainWindow):

    # page <-> index du QTabWidget
    class page_index (Enum):
        DETAIL       = 0
        IMPORTATION  = 1
        EXPORTATION  = 2


    # signal de mise à jour de l'indicateur de progression
    in_progress_signal = pyqtSignal(int)

    # NOTE : home_signal est un signal émit par le bouton 'home' de Nav_tools
    #        il permet la réouverture de la page initiale.


    def __init__(self, app):
        super().__init__()
        logger.log(logging.RUN, "MainWindow::__init")

        self.app = app

        # préférences utilisateur
        QCoreApplication.setOrganizationName('aito')
        QCoreApplication.setApplicationName('aito')
        self.settings = QSettings()

        self.setWindowTitle(f'AITO-V{__version__}')
        self.setWindowIcon(icons['aito'])
        # ajustement de la fenêtre : user préférences ou par default
        self.resize( self.settings.value('MainWindow/size', QSize (1200, 900)) )
        self.move  ( self.settings.value('MainWindow/pos' , QPoint(   0,   0)) )
        point_size = self.settings.value('MainWindow/font_size', 10)
        if isinstance(point_size, str):
            point_size = int(point_size)
        self.font().setPointSize(point_size)

        # gestion des acqids
        self.gest_acqid = Gest_acqid()

        # définition des models
        self.models = dict()
        self.models['plateforme'] = Model_plateforme(parent     = self,
                                                     name       = 'plateforme',
                                                     gest_acqid = self.gest_acqid)

        self.models['campagne'  ] = Model_campagne  (parent     = self,
                                                     name       = 'campagne',
                                                     gest_acqid = self.gest_acqid)

        self.models['acqid'     ] = Model_acqid     (parent     = self,
                                                     name       = 'acqid',
                                                     gest_acqid = self.gest_acqid)

        self.models['by_date'   ] = Model_by_date   (parent     = self,
                                                     name       = 'by_date',
                                                     gest_acqid = self.gest_acqid)

        # mise en place de l'IHM
        self.setup_ihm()

        # les shortcuts classiques
        self.shortcut_zoom_in = QShortcut(QKeySequence.ZoomIn, self)
        self.shortcut_zoom_in.activated.connect(self.zoom_in)

        self.shortcut_zoom_out = QShortcut(QKeySequence.ZoomOut, self)
        self.shortcut_zoom_out.activated.connect(self.zoom_out)


        # reprise du contexte
        self.restore_context()

        self.manuel = None

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "MainWindow::setup_ihm")

        # les widgets graphiques
        # - le bouton menu et les boutons d'accès aux applications AIDA
        button_menu    = QPushButton(icons['menu'   ], None)
        button_vista   = QPushButton(icons['vista'  ], 'Vista')
        button_adp     = QPushButton(icons['adp'    ], 'ADP')
        button_edifil  = QPushButton(icons['edifil' ], 'Edifil')
        button_monitor = QPushButton(icons['monitor'], 'Monitor')
        button_manuel  = QPushButton(icons['help'   ], 'Manuel')

        # - l'indicatuer de progression
        self.progress_indicator = QProgressBar()

        # menu du bouton menu
        menu = QMenu()

        menu.addAction('Raccourcis clavier', self.menu_short_cuts)

        menu.addAction('Configurer la console (XTerm)', self.menu_xterm)

        menu.addAction('Quitter', self.menu_quit)

        button_menu.setMenu(menu)

        # indicateur de progression
        self.progress_indicator.setMaximumSize(37, 16)
        self.progress_indicator.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                          QSizePolicy.Fixed))
        self.progress_indicator.setToolTip('indicateur de progression')
        self.progress_indicator.setStyleSheet("QProgressBar"
                                "{background-color: red;}"
                                "QProgressBar::chunk{background-color: lime;}")
        self.progress_indicator.setTextVisible(False)
        self.progress_indicator.setValue(0)

        # - les objets du tabwidget
        # TODO : dans l'absolu, seul l'onglet visualisé doit appeler
        #        setup_ihm... mais il faudra alors gérer dans la méthode
        #        main_tab_changed s'il faut où non mettre en place l'ihm...

        # models :
        # NOTE : seul main détient les models. Les widget qui en ont besoin
        #        les récupère *directement* par parent.models
        tab_detail = Detail     (parent=self, app=app)
        tab_import = Importation(parent=self)
        tab_export = Exportation(parent=self)

        # listes des QThread
        self.threads = [tab_import.worker_thread, tab_export.worker_thread ]

        # - le tabwidget général
        self.main_tabs = QTabWidget()
        self.main_tabs.addTab(tab_detail, 'Detail')
        self.main_tabs.addTab(tab_import, 'Importation')
        self.main_tabs.addTab(tab_export, 'Exportation')

        # page courante : user préférences ou par default
        page = self.settings.value('MainWindow/page', self.page_index.DETAIL.name)
        self.main_tabs.setCurrentIndex(self.page_index[page].value)

        # rangements
        # - du menu et des boutons d'accès aux applications AIDA dans leur
        #   layout (en les tassant)
        layout_menu = QHBoxLayout()
        layout_menu.addWidget(button_menu    )
        layout_menu.addWidget(button_vista   )
        layout_menu.addWidget(button_adp     )
        layout_menu.addWidget(button_edifil  )
        layout_menu.addWidget(button_monitor )
        layout_menu.addWidget(button_manuel  )
        layout_menu.addStretch()
        layout_menu.addWidget(self.progress_indicator)
        layout_menu.setSizeConstraint(QLayout.SetMinimumSize)

        # - de tout ça dans le layout général
        layout = QVBoxLayout()
        layout.addLayout(layout_menu)
        layout.addWidget(self.main_tabs)

        # terminer la MainWindow
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # une fenêtre pour afficher des messages
        self.message = QMessageBox(self)
        self.message.setModal(False)

        # connexions
        button_vista  .clicked.connect(self.run_tool)
        button_adp    .clicked.connect(self.run_tool)
        button_edifil .clicked.connect(self.run_tool)
        button_monitor.clicked.connect(self.run_tool)
        button_manuel .clicked.connect(self.show_manuel)

        self.main_tabs.currentChanged.connect(self.main_tab_changed)


        # les signaux pour l'indicateur de progression
        self.in_progress_signal.connect(self.set_in_progress_value)
        # - pour les models
        for model in self.models.values():
            model.in_progress_signal.connect(self.set_in_progress_value)

        # - pour les tabs de la page Detail (TODO : c'est pas très propre...)
        n = tab_detail.detail_tabs.count()
        for i in range(tab_detail.detail_tabs.count()):
            w = tab_detail.detail_tabs.widget(i)
            w.in_progress_signal.connect(self.set_in_progress_value)

        # TODO :  peut-on retrouver TOUS les objets Nav_tools pour les
        #         connecter à redo_restore_context ?
        # les signaux pour le réaffichage de la page initiale
        tab_detail.selection.nav_tools.home_signal.connect(self.redo_restore_context)
        tab_export.selection.nav_tools.home_signal.connect(self.redo_restore_context)

        # fin
        self.progress_indicator.setValue(100)

        return


    def menu_short_cuts(self):
        """ Affichage de documentation
        """
        logger.log(logging.RUN, "MainWindow::menu_short_cuts")

        file = os.path.join(AITO_DOC, 'Short_cuts.html')
        with open(file, 'r') as handler:
            text = handler.read().replace('AIDA_ICON', AITO_icons.aida_dir_icons)

        self.message.setText(text)
        self.message.show()

        return


    def menu_xterm(self):
        """ Affichage de documentation
        """
        logger.log(logging.RUN, "MainWindow::menu_xterm")

        file = os.path.join(AITO_DOC, 'Console_XTerm.html')
        with open(file, 'r') as handler:
            text = handler.read()

        self.message.setText(text)
        self.message.show()

        return




    def menu_quit(self):
        """ L'utilisateur à demandé, par le menu, à quitter l'application.
        """
        logger.log(logging.RUN, "MainWindow::menu_quit")

        self.close()

        return


    def run_tool(self):
        """ Lance l'application AIDA reçue.
        """
        logger.log(logging.RUN, "MainWindow::run_tool")

        sender = self.sender().text().lower()
        subprocess.Popen( [ sender ] )

        return


    def show_manuel(self):
        """ Affiche le manuel d'utilisation
        """
        logger.log(logging.RUN, "MainWindow::mauel")

        # si besoin, créer le manuel
        if not self.manuel:
            self.manuel = ManuelWindow()

        # si la fenêtre est iconifiée, la désiconifier
        self.manuel.setWindowState(Qt.WindowNoState)

        self.manuel.show()

        return


    def zoom_in(self):
        """ Augmenter la taille de la font de 1.
        """
        logger.log(logging.RUN, "MainWindow::zoom_in")

        # récupérer la font actuelle
        font = self.font()
        size = font.pointSize()

        # augmenter la fonte
        font.setPointSize(size + 1)
        self.setFont(font)

        return


    def zoom_out(self):
        """ Diminuer la taille de la font de 1.
        """
        logger.log(logging.RUN, "MainWindow::zoom_out")

        # récupérer la font actuelle
        font = self.font()
        size = font.pointSize()

        # diminuer la fonte
        font.setPointSize(size - 1)
        self.setFont(font)

        return

    def main_tab_changed(self, index):
        """ L'onglet de numéro 'index' a été sélectioné.
            => positionner l'objets Selection affiché au même endroit.
        """
        logger.log(logging.RUN, "MainWindow::main_tab_changed")
        logger.debug(f"index = {index} : rien à faire ? (suppression de l'historique)")

        return


    def write_settings(self):
        """ Enregistrement des préférences utilisateur.
        """
        logger.log(logging.RUN, "MainWindow::write_settings")

        current_index = self.main_tabs.currentIndex()
        page          = list(self.page_index)[current_index].name

        self.settings.beginGroup('MainWindow')
        self.settings.setValue('size'     , self.size())
        self.settings.setValue('pos'      , self.pos())
        self.settings.setValue('font_size', self.font().pointSize())
        self.settings.setValue('page'     , page)

        self.settings.endGroup();

        return


    @pyqtSlot(int)
    def set_in_progress_value(self, value):
        """ Mise à jour de l'indicateur de progression (value : [0, 100])
            Emission du signal :
            1) l'émetteur doit être connecté dans la partie 'les signaux pour
               l'indicateur de progression' de la méthode MainWindow::setup_ihm
            2) dans l'émetteur :
                in_progress_signal = pyqtSignal(int)
                self.in_progress_signal.emit(12)
        """
        # DBG logger.log(logging.RUN, "MainWindow::set_in_progress_value")

        if value <= 0:
            value = 0
        elif value >= 100:
            value = 100

        self.progress_indicator.setValue(value)

        return


    def restore_context(self):
        """ Restauration du contexte de la dernière session de l'utilisateur.
        """
        logger.log(logging.RUN, "MainWindow::restore_context")

        self.main_tabs.currentWidget().restore_context()

        return


    def redo_restore_context(self):
        """ Refait la restauration du contexte de la dernière session d
            l'utilisateur.

            Cette méthode est connectée au signal home_signal émit par le
            bouton 'home' de Nav_tools
        """
        logger.log(logging.RUN, "MainWindow::redo_restore_context")

        # positionner la page courante : user préférences ou par default
        page = self.settings.value('MainWindow/page', self.page_index.DETAIL.name)
        self.main_tabs.setCurrentIndex(self.page_index[page].value)

        # faire la restautation du contexte.
        self.main_tabs.currentWidget().restore_context()

        return


    def closeEvent(self, event):
        """ Gestion de l'arret de l'applicaion
            Enregistrement des préférences utilisateur
        """
        logger.log(logging.RUN, "MainWindow::closeEvent")

        self.message.setModal(True)
        reply = self.message.question(self,
                                      '',
                                      'Êtes-vous sûr de vouloir quitter Aito ?',
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.Yes
                                     )

        if reply == QMessageBox.Yes:
            # terminer les QThread
            for thread in self.threads:
                thread.quit()

            # enregistrer les préférences utilisateur
            # - les généralités de la page principale
            self.write_settings()

            # - de la page (onglet) affichée
            self.main_tabs.currentWidget().write_settings()

            # terminer
            QApplication.closeAllWindows()
            event.accept()

        else:
            self.message.setModal(False)
            event.ignore()

        return


if __name__ == '__main__':
    print(f"VERSIONS : ")
    print(f" - PyQt5     : {PYQT_VERSION_STR}")
    #print(f" - pyqtgraph : {pg.Qt.VERSION_INFO}")

    # ------ mode DEBUG : début ----------------------------------------
    if '-D' in sys.argv:
        import traceback
        import sys

        print(f"\n\n!!! Mode DEBUG activé (option -D) !!!\n\n")

        # sauvegarde du sys.excepthook normal
        sys._excepthook = sys.excepthook

        def exception_hook(exctype, value, traceback):
            """ Arrêt de l'application à la moindre exception.
            """
            print(f"\n\n!!! exception_hook() : " +\
                  f"\033[1m\033[31m{value}\033[0m", file=sys.stderr)

            # exécution du sys.excepthook normal
            sys._excepthook(exctype, value, traceback)

            sys.exit(1)

        # positionnement du sys.excepthook sur le local
        sys.excepthook = exception_hook
    else:
        logger.debug("!!! Mode DEBUG désactivé (pas d'option -D) !!!")
    # ------ mode DEBUG : fin ----------------------------------------



    dt_now = datetime.datetime.now()
    start_at = datetime.datetime.strftime(dt_now, '%d/%m/%Y %H:%M:%S')
    logger.info(f"Démarrage : {start_at}")

    app = QApplication(sys.argv)

    ## feuille de style
    #with open('styles.qss', 'r') as f:
    #    style = f.read()
    #app.setStyleSheet(style)

    # construire les QIcons à partir des icônes de AIDA
    AITO_icons.build_QIcons()

    window = MainWindow(app=app)
    window.show()
    sys.exit( app.exec() )
