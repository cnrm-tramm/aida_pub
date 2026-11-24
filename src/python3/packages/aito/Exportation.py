#!/usr/bin/env python3

"""
AITO
    Gestion de la page Exportation

    Exportation doit :
    1) lancer le producteur de fichier NetCDF
    2) afficher au fur et à mesure les lignes d'output du producteur dans
       un widget graphique.

    Pour ce faire, on pourrait être tenté de lancer le producteur par un
    `subprocess.Popen` (en faisant en sorte récupérer les lignes d'output au
    fur et à mesure) et d'ajouter chaque ligne d'output reçue dans le widget.
    CELA NE MARCHE PAS car pendant toute la durée du process géré par le
    `subprocess.Popen`, l'application graphique n'a plus la main => les lignes
    d'output sous bien ajoutées au widget graphique MAIS on ne les voient que
    lorsque le `subprocess.Popen` se termine.
    Il faut donc lancer le producteur dans un Thread (class Worker) et faire
    communiquer l'application graphique et le Thread par des signaux.
    (méthodologie pompée directement du Net)
"""

import sys
import os
import logging
import subprocess
import shlex
import glob
import configparser

from PyQt5.QtWidgets import (QWidget,
                             QPushButton, QRadioButton,
                             QLabel, QLineEdit, QListWidget, QStackedWidget,
                             QSpinBox, QComboBox, QDateEdit, QPlainTextEdit,
                             QHBoxLayout, QVBoxLayout,
                             QSplitter,
                             QGroupBox, QButtonGroup,
                             QFileDialog, QMessageBox,
                            )
from PyQt5.Qt        import (QAbstractItemView,
                            )
from PyQt5.QtGui     import (QFont,
                            )
from PyQt5.QtCore    import (Qt, QDate, QSize,
                             QSettings,
                             QThread, QObject,
                             pyqtSignal, pyqtSlot,
                            )


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from AITO_icons       import icons, get_default_size
from Selection        import Selection
from Vector           import Vector
###from Splitter_handler import Splitter_handler

tool_CDF = os.path.join(AIDA.AIDA_getenv('BIN'), 'prod_CDF.py')

logger = logging.getLogger('aito')


class Worker(QObject):
    # signaux de  communication avec le "propriétaire"
    info      = pyqtSignal(str)
    completed = pyqtSignal(int)

    @pyqtSlot(str)
    def do_work(self, runstring):
        # logger.log(logging.RUN, f"Exportation::Worker::do_work : " +\
        #                         f"runstring = {runstring}")

        # lancer de process
        process = subprocess.Popen(shlex.split(runstring),
                                   stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        # lire les output du process
        while process.poll() is None:
            line = process.stdout.readline().decode('utf-8').strip()
            if line:
                # renvoyer la ligne d'output au "propriétaire" du Worker
                self.info.emit(line)

        # renvoyer le code de sortie du process au "propriétaire" du Worker
        # TODO : en fait ça ne marche pas, je récupère toujours 0. Je pense
        #        que je récupère le code d'exit de python3 -u (qui lui ne
        #        semble pas lire le code d'exit de prod_CDF...)
        ###ret_code = process.poll()
        ret_code = process.returncode
        self.completed.emit(ret_code)

        return


class Exportation(QWidget):
    """ Gestion de la page Exportation
    """
    # signal de lancement d'un processus par la class Worker
    work_requested = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Exportation::__init__")

        self.parent  = kwargs.get('parent' , None)

        # récupérer les objets de l'application (models, gest_XXX...)
        self.models     = self.parent.models
        self.gest_acqid = self.parent.gest_acqid

        # self.acqid sera mis à jour par la méthode 'multi_vectors_selected' et
        # par la méthode 'acqid_changed' appelée par la Selection
        self.acqid = None

        # dictionnaire contenant les choix de l'utilisateur
        self.config = dict()
        # et les choix par défaut pour le mode 'configuration manuelle'
        self.config['config_mode']       = None # 'Par fichier' / 'Manuelle'
        self.config['config_file']       = None # path complet
        self.config['prod_mode']         = 'Un fichier pour la période'
        self.config['version']           = 1
        self.config['processing_level']  = 'L1'
        self.config['prefix']            = 'quick'
        self.config['dir_out']           = '/tmp'
        # autres clés qui seront enrgistrées :
        # - 'plage'           : 'by_date' / 'by_acqid'
        # - 'start' et 'stop' : acqids ou dates


        # Gestion d'un sous-process long dont il faut lire les lignes
        # d'output au fur et à mesure
        self.worker        = Worker()
        self.worker_thread = QThread(parent=self.parent)

        # - connexions
        self.worker.info.connect(self.worker_throws_info)
        self.worker.completed.connect(self.worker_completed)
        self.work_requested.connect(self.worker.do_work)

        # - move worker to the worker thread
        self.worker.moveToThread(self.worker_thread)

        # - start the thread
        self.worker_thread.start()

        # préférences utilisateur
        self.settings      = QSettings()
        self.settings.name = 'Exportation'

        # mise en place de l'IHM
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Exportation::setup_ihm")

        # les widgets graphiques
        # - la Selection
        self.selection = Selection(parent      = self,
                                   select_mode = 'extended')


        # type de fichier
        export_type = QLabel("<b>Exportation au format NetCDF</b>")

        # partie mode de configuration
        box_conf_mode = self.setup_conf_mode_ihm()

        # partie période
        box_period = self.setup_period_ihm()

        # partie destination
        box_destination = self.setup_destination_ihm()

        # bouton d'exécution
        button_exec = QPushButton(icons['run'], None)
        button_exec.setIconSize(get_default_size())
        button_exec.setToolTip('excétuter')

        # partie result
        box_result = self.setup_result_ihm()


        # on ne peut pas mettre de layout dans un splitter
        # => créer un pseudo-widget avc la partie 'configuration'
        pseudo_widget = QWidget()
        layout_speudo = QVBoxLayout()
        layout_speudo.addWidget(export_type    )
        layout_speudo.addWidget(box_conf_mode  )
        layout_speudo.addWidget(box_period     )
        layout_speudo.addWidget(box_destination)
        layout_speudo.addWidget(button_exec    )

        pseudo_widget.setLayout(layout_speudo)

        # un splitter pour ranger la partie pseudo_wiget et le résultat
        ###splitter_right = Splitter_handler(Qt.Vertical)
        splitter_right = QSplitter(Qt.Vertical)
        splitter_right.addWidget(pseudo_widget)
        splitter_right.addWidget(box_result   )

        # un splitter pour ranger la selection et la partie droite
        ###splitter = Splitter_handler(Qt.Horizontal)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.selection)
        splitter.addWidget(splitter_right)

        # rangement de tout ça dans le layout principal
        layout = QHBoxLayout()
        layout.addWidget(splitter)

        # positionnement du layout
        self.setLayout(layout)

        # connexions
        button_exec.clicked.connect(self.run_prod)

        # une fenêtre pour afficher des messages
        self.message = QMessageBox(self)

        return


    def setup_conf_mode_ihm(self):
        box_conf_mode = QGroupBox("Configuration")

        # la page 'par fichier'
        # ---------------------
        page_by_file       = QWidget()
        self.file_lineedit = QLineEdit()
        file_button_browse = QPushButton(icons['folder'], None)

        # son layout
        layout = QHBoxLayout()
        layout.addWidget(self.file_lineedit, alignment=Qt.AlignTop)
        layout.addWidget(file_button_browse, alignment=Qt.AlignTop)
        page_by_file.setLayout(layout)

        # son affinage
        self.file_lineedit.setPlaceholderText('sélectionner un fichier de configuration')

        ###file_button_browse.setIconSize(QSize(20, 20))
        file_button_browse.setIconSize(get_default_size())
        file_button_browse.setToolTip('sélectionner un fichier de configuration')


        # la page 'manuelle'
        # -----------------
        page_manual                  = QWidget()
        manual_label_vectors         = QLabel('vecteurs')
        self.manual_list_vectors     = QListWidget()
        manual_button_clear_list     = QPushButton(icons['clear'], None)
        manual_button_one_for_period = QRadioButton(self.config['prod_mode'])
        manual_button_one_by_day     = QRadioButton('Un fichier par jour')
        manual_label_version         = QLabel('version')
        manual_spinbox_version       = QSpinBox()
        manual_label_processing      = QLabel('processing level')
        manual_combo_processing      = QComboBox()

        # grouper les boutons
        self.button_period_group = QButtonGroup()
        self.button_period_group.addButton(manual_button_one_for_period)
        self.button_period_group.addButton(manual_button_one_by_day)

        # son affinage
        manual_button_clear_list.setIconSize(get_default_size())

        # layout des boutons
        layout_vectors = QHBoxLayout()
        layout_vectors.addWidget(manual_label_vectors)
        layout_vectors.addWidget(self.manual_list_vectors)
        layout_vectors.addWidget(manual_button_clear_list)

        # layout des boutons
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(manual_button_one_for_period)
        layout_buttons.addWidget(manual_button_one_by_day)

        # layout de version
        layout_version = QHBoxLayout()
        layout_version.addWidget(manual_label_version)
        layout_version.addWidget(manual_spinbox_version)

        # layout de processing
        layout_processing = QHBoxLayout()
        layout_processing.addWidget(manual_label_processing)
        layout_processing.addWidget(manual_combo_processing)


        # préfixe du fichier de sortie
        # ----------------------------
        manual_prefix_file_out      = QLabel('Préfixe du fichier de sortie')
        self.manual_prefix_lineedit = QLineEdit(self.config['prefix'])

        # son rangement
        layout_prefix = QHBoxLayout()
        layout_prefix.addWidget(manual_prefix_file_out)
        layout_prefix.addWidget(self.manual_prefix_lineedit)
        ###layout.addStretch()

        # son affinage
        ###self.manual_prefix_lineedit.setToolTip('...')

        # son layout
        layout = QVBoxLayout()
        layout.addLayout(layout_vectors)
        layout.addLayout(layout_buttons)
        layout.addLayout(layout_version)
        layout.addLayout(layout_processing)
        layout.addLayout(layout_prefix)
        page_manual.setLayout(layout)

        # son affinage
        self.manual_list_vectors.setToolTip("""
                <b>pour remplir cette liste :</b>
                <ol>
                  <li>sélectionner des vecteurs dans la liste à gauche</li>
                  <li>terminer en tapant la touche [ENTER]</li>
                </ol>
                <p>
                <b>pour supprimer des vecteurs de cette liste :</b>
                <ol>
                  <li>sélectionner ici les vecteurs à supprimer</li>
                  <li>clicker sur ile bouton <i>supprimer...</i>
                </ol>""")
        self.manual_list_vectors.setSelectionMode(QAbstractItemView.ExtendedSelection)
        manual_button_clear_list.setToolTip('supprimer les vecteurs sélectionnés')
        manual_button_one_for_period.setChecked(True)
        manual_spinbox_version.setRange(1, 99)
        manual_spinbox_version.setValue(self.config['version'])
        manual_combo_processing.addItem(self.config['processing_level'])
        manual_combo_processing.addItem('L2')
        manual_combo_processing.setCurrentIndex(0)


        # pages stackées : by_file / manual
        self.stack_conf_mode = QStackedWidget()
        self.stack_conf_mode.addWidget(page_by_file)
        self.stack_conf_mode.addWidget(page_manual)


        # des radio boutons pour sélectionner le mode de configuration
        # -----------------
        self.button_by_file = QRadioButton('Par fichier')
        self.button_manual  = QRadioButton('Manuelle')

        # son rangement
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_by_file)
        layout_buttons.addWidget(self.button_manual )

        # son affinage
        # - bouton par défaut
        self.button_by_file.setChecked(True)
        # - liaison button <-> page
        self.button_by_file.widget = page_by_file
        self.button_manual.widget  = page_manual

        # grouper les radio bouton
        # -------------------------
        self.button_mode_group = QButtonGroup()
        self.button_mode_group.addButton(self.button_by_file)
        self.button_mode_group.addButton(self.button_manual)

        # rangement de tout ça dans le layout de mode configuration
        layout = QVBoxLayout()
        layout.addLayout(layout_buttons)
        layout.addWidget(self.stack_conf_mode)
        box_conf_mode.setLayout(layout)

        # connexions
        self.button_mode_group.buttonClicked.connect(self.display_configuration_page)
        self.file_lineedit.textChanged.connect(self.configuration_file_changed)
        file_button_browse.clicked.connect(self.get_configuration_file)
        manual_button_clear_list.clicked.connect(self.clear_list)
        ###self.manual_list_vectors.itemClicked.connect(self.delete_name)
        self.button_period_group.buttonClicked.connect(self.period_selected)
        manual_spinbox_version.valueChanged.connect(self.version_changed)
        manual_combo_processing.currentTextChanged.connect(self.processing_level_changed)
        self.manual_prefix_lineedit.textChanged.connect(self.prefix_changed)


        return box_conf_mode


    def setup_period_ihm(self):
        box_period = QGroupBox("Période")

        # la page 'par acqid'
        # ------------------
        page_by_acqid                      = QWidget()
        page_label_from                    = QLabel('de :')
        self.page_by_acqid_lineedit_start  = QLineEdit()
        page_by_acqid_button_stop_to_start = QPushButton(icons['right_to_left'], None)
        page_by_acqid_button_start_to_stop = QPushButton(icons['left_to_right'], None)
        page_label_to                      = QLabel('à  :')
        self.page_by_acqid_lineedit_stop   = QLineEdit()

        # son layout
        layout = QHBoxLayout()
        layout.addWidget(page_label_from)
        layout.addWidget(self.page_by_acqid_lineedit_start)
        layout.addStretch()
        layout.addWidget(page_by_acqid_button_stop_to_start)
        layout.addWidget(page_by_acqid_button_start_to_stop)
        layout.addStretch()
        layout.addWidget(page_label_to)
        layout.addWidget(self.page_by_acqid_lineedit_stop)
        page_by_acqid.setLayout(layout)

        # son affinage
        self.page_by_acqid_lineedit_start.name = 'start'
        self.page_by_acqid_lineedit_start.setMaxLength(8)
        self.page_by_acqid_lineedit_start.setPlaceholderText('acqid')
        ###page_by_acqid_button_stop_to_start.setIconSize(QSize(20, 20))
        page_by_acqid_button_stop_to_start.setIconSize(get_default_size())

        self.page_by_acqid_lineedit_stop.name  = 'stop'
        self.page_by_acqid_lineedit_stop.setMaxLength(8)
        self.page_by_acqid_lineedit_stop.setPlaceholderText('acqid')
        ###page_by_acqid_button_start_to_stop.setIconSize(QSize(20, 20))
        page_by_acqid_button_start_to_stop.setIconSize(get_default_size())

        page_by_acqid_button_stop_to_start.widget_from = self.page_by_acqid_lineedit_stop
        page_by_acqid_button_stop_to_start.widget_to   = self.page_by_acqid_lineedit_start
        page_by_acqid_button_start_to_stop.widget_from = self.page_by_acqid_lineedit_start
        page_by_acqid_button_start_to_stop.widget_to   = self.page_by_acqid_lineedit_stop

        # la page 'par date'
        # ------------------
        page_by_date                      = QWidget()
        page_label_from                   = QLabel('du :')
        page_by_date_dateedit_start       = QDateEdit(calendarPopup=True)
        page_by_date_button_stop_to_start = QPushButton(icons['right_to_left'], None)
        page_by_date_button_start_to_stop = QPushButton(icons['left_to_right'], None)
        page_label_to                     = QLabel('au :')
        page_by_date_dateedit_stop        = QDateEdit(calendarPopup=True)

        # son layout
        layout = QHBoxLayout()
        layout.addWidget(page_label_from)
        layout.addWidget(page_by_date_dateedit_start)
        layout.addStretch()
        layout.addWidget(page_by_date_button_stop_to_start)
        layout.addWidget(page_by_date_button_start_to_stop)
        layout.addStretch()
        layout.addWidget(page_label_to)
        layout.addWidget(page_by_date_dateedit_stop)
        page_by_date.setLayout(layout)

        # son affinage
        page_by_date_dateedit_start.name = 'start'
        page_by_date_dateedit_stop.name  = 'stop'
        page_by_date_dateedit_start.setDate(QDate.currentDate())
        page_by_date_dateedit_stop.setDate(QDate.currentDate())
        ###page_by_date_button_stop_to_start.setIconSize(QSize(20, 20))
        ###page_by_date_button_start_to_stop.setIconSize(QSize(20, 20))
        page_by_date_button_stop_to_start.setIconSize(get_default_size())
        page_by_date_button_start_to_stop.setIconSize(get_default_size())
        page_by_date_button_stop_to_start.widget_from = page_by_date_dateedit_stop
        page_by_date_button_stop_to_start.widget_to   = page_by_date_dateedit_start
        page_by_date_button_start_to_stop.widget_from = page_by_date_dateedit_start
        page_by_date_button_start_to_stop.widget_to   = page_by_date_dateedit_stop

        # pages stackées : by_acqid / by_date
        self.stack_period = QStackedWidget()
        self.stack_period.addWidget(page_by_acqid)
        self.stack_period.addWidget(page_by_date)


        # des radio boutons pour sélectionner le mode 'par acqid' ou 'par date'
        # -----------------
        button_by_acqid = QRadioButton('Par acqid')
        button_by_date  = QRadioButton('Par date')

        # son rangement
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(button_by_acqid)
        layout_buttons.addWidget(button_by_date )

        # son affinage
        button_by_acqid.name = 'by_acqid'
        button_by_date.name  = 'by_date'
        # - bouton par défaut
        button_by_acqid.setChecked(True)
        self.config['plage'] = button_by_acqid.name
        # - liaison button <-> page
        button_by_acqid.widget = page_by_acqid
        button_by_date.widget  = page_by_date

        # grouper les radio bouton
        # -------------------------
        self.button_period_group = QButtonGroup()
        self.button_period_group.addButton(button_by_acqid)
        self.button_period_group.addButton(button_by_date)

        # rangement de tout ça dans le layout de mode configuration
        layout = QVBoxLayout()
        layout.addLayout(layout_buttons)
        layout.addWidget(self.stack_period)
        box_period.setLayout(layout)

        # connexions
        self.button_period_group.buttonClicked.connect   (self.display_period_page)

        self.page_by_acqid_lineedit_start.textChanged.connect (self.acqid_changed_manualy)
        self.page_by_acqid_lineedit_stop.textChanged.connect  (self.acqid_changed_manualy)

        page_by_date_dateedit_start.dateChanged.connect  (self.date_changed)
        page_by_date_dateedit_stop.dateChanged.connect   (self.date_changed)

        page_by_acqid_button_stop_to_start.clicked.connect(self.copy_left_right)
        page_by_acqid_button_start_to_stop.clicked.connect(self.copy_left_right)

        page_by_date_button_stop_to_start.clicked.connect(self.copy_left_right)
        page_by_date_button_start_to_stop.clicked.connect(self.copy_left_right)

        return box_period


    def setup_destination_ihm(self):
        box_destination = QGroupBox("Destination")

        # répertoire de destination
        # -------------------------
        destination_dir_out                = QLabel('Répertoire de destination')
        self.destination_dir_out_lineedit  = QLineEdit(self.config['dir_out'])
        destination_button_browse          = QPushButton(icons['folder'], None)

        # son rangement
        layout_dir_out = QHBoxLayout()
        layout_dir_out.addWidget(destination_dir_out)
        layout_dir_out.addWidget(self.destination_dir_out_lineedit)
        layout_dir_out.addWidget(destination_button_browse)
        ###layout.addStretch()

        # son affinage
        destination_button_browse.setToolTip('sélectionner un répertoire de destination')
        ###destination_button_browse.setIconSize(QSize(20, 20))
        destination_button_browse.setIconSize(get_default_size())

        # rangement de tout ça dans le layout de mode configuration
        layout = QVBoxLayout()
        layout.addLayout(layout_dir_out)
        box_destination.setLayout(layout)

        # connexions
        self.destination_dir_out_lineedit.textChanged.connect(self.dir_out_changed)
        destination_button_browse.clicked.connect(self.get_destination_dir)

        return box_destination


    def setup_result_ihm(self):
        box_result = QGroupBox("Résultat")

        # afficheur du résultat
        # ---------------------
        self.result_plaintextedit = QPlainTextEdit()

        # bouton de visualisation du résultat
        self.result_button_see = QPushButton()
        ###self.result_button_see.setIconSize(QSize(20, 20))
        self.result_button_see.setIconSize(get_default_size())

        # son affinage
        self.result_button_see.setIcon(icons['eye_closed'])
        self.result_button_see.setEnabled(False)
        self.result_button_see.setToolTip("visualiser le fichier généré")
        self.result_plaintextedit.setFont (QFont ('Courier', 12))

        # rangement de tout ça dans le layout de mode configuration
        layout = QVBoxLayout()
        layout.addWidget(self.result_plaintextedit)
        layout.addWidget(self.result_button_see, alignment=Qt.AlignRight)

        box_result.setLayout(layout)

        # connexions
        self.result_button_see.clicked.connect(self.see_result)

        return box_result



    def display_configuration_page(self, button):
        """ Affiche la page 'configuration par fichier' ou
            'configuration manuelle' en fonction du bouton sélectionné.
            Met à jour le dictionnaire de la configuration.
        """
        # logger.log(logging.RUN, "Exportation::display_configuration_page")

        widget = button.widget
        self.stack_conf_mode.setCurrentWidget(widget)

        self.config['config_mode'] = button.text()

        return


    def configuration_file_changed(self, text):
        """ Met à jour le dictionnaire de la configuration.
        """
        # logger.log(logging.RUN, "Exportation::configuration_file_changed")

        self.config['config_file'] = text

        return


    def get_configuration_file(self):
        """ Affiche le dialogue de demande du nom du fichier de configuration
            Met à jour le dictionnaire de la configuration.
        """
        # logger.log(logging.RUN, "Exportation::get_configuration_file")

        filename = QFileDialog.getOpenFileName(self,
                            'Choisir le fichier de configuration',
                            filter="All(*);;config (*.config);;cfg (*.cfg)")
        self.file_lineedit.setText(filename[0])

        self.config['config_file'] = filename[0]

        return


    def period_selected(self, button):
        """ Met à jour le dictionnaire de la configuration.
        """
        # logger.log(logging.RUN, "Exportation::period_selected")

        self.config['prod_mode'] = button.text()

        return


    def version_changed(self, value):
        """ Met à jour le dictionnaire de la configuration.
        """
        self.config['version'] = value

        return


    def processing_level_changed(self, value):
        """ Met à jour le dictionnaire de la configuration.
        """
        self.config['processing_level'] = value

        return


    def display_period_page(self, button):
        """ Affiche la page 'période par date' ou 'période par acqid'
            en fonction du bouton sélectionné.
            Met à jour le dictionnaire de la configuration
        """
        # logger.log(logging.RUN, f"Exportation::display_period_page : " +\
        #                         f"button = {button}")

        widget = button.widget
        self.stack_period.setCurrentWidget(widget)

        self.config['plage'] = button.name

        return


    def date_changed(self, date):
        """ Met à jour le dictionnaire de la configuration en fonction du
            widget expéditeur (start/stop).
        """
        # logger.log(logging.RUN, f"Exportation::date_changed : " +\
        #                         f"date = {date}")

        sender = self.sender()
        key    = sender.name
        self.config[key] = f"{date.day():02d}{date.month():02d}{date.year()}"

        return


    def acqid_changed_manualy(self):
        """ L'utilisateur a saisi un acqid.
            Met à jour le dictionnaire de la configuration en fonction du
            widget expéditeur (start/stop).
        """
        sender = self.sender()
        key    = sender.name
        self.config[key] = sender.text()

        return


    def copy_left_right(self):
        """ Copie de gauche à droite et inversement en fonction du
            widget expéditeur (start_to_stop/stop_to_start).
        """
        sender = self.sender()
        widget_from    = sender.widget_from
        widget_to      = sender.widget_to

        if isinstance(widget_from, QDateEdit):
            widget_to.setDate(widget_from.date())
        else:
            widget_to.setText(widget_from.text())

        return


    def dir_out_changed(self, text):
        """ Met à jour le dictionnaire de la configuration avec le contenu
            du champ.
        """
        self.config['dir_out'] = text

        return


    def get_destination_dir(self):
        """ Affiche le dialogue de demande du répertoire de sortie
            Met à jour le dictionnaire de la configuration.
        """
        initial = self.destination_dir_out_lineedit.text()
        dir_out = QFileDialog.getExistingDirectory(self,
                            'Choisir le répertoire de destination',
                            directory=initial)

        if not dir_out:
            return

        self.destination_dir_out_lineedit.setText(dir_out)
        self.config['dir_out'] = dir_out

        return


    def prefix_changed(self, text):
        """ Met à jour le dictionnaire de la configuration avec le contenu
            du champ.
        """
        self.config['prefix'] = text

        return


    def view_selected_index(self, index):
        """ Positionne la vue sur l'index reçu.
        """
        logger.log(logging.RUN, f"Exportation::view_selected_index : " +\
                                f"index = {index}")

        self.selection.left_selector.highlight_index(index)

        return


    def clear_list(self):
        """ supprime de la liste les vecteurs sélectionnés.
        """
        logger.log(logging.RUN, "Exportation::clear_list")
        for item in reversed(self.manual_list_vectors.selectedItems()):
            row = self.manual_list_vectors.row(item)
            self.manual_list_vectors.takeItem(row)

        return


    def delete_name(self, item):
        """ Supprime de manual_list_vectors le nom sélectionné.
        """
        logger.log(logging.RUN, f"Exportation::delete_name : " + \
                                f"item = {item}")

        row = self.manual_list_vectors.currentRow()
        self.manual_list_vectors.takeItem(row)

        return


    def multi_vectors_selected(self, acqid, vector_names):
        """ Mettre à jour manual_list_vectors avec la liste des noms
            de vecteurs reçue.
        """
        logger.log(logging.RUN, f"Exportation::multi_vectors_selected : " + \
                                f"acqid = {acqid}, " +\
                                f"vector_names = {vector_names}")

        # afficher la page de configuration manuelle
        self.button_manual.setChecked(True)
        self.display_configuration_page(self.button_manual)

        already_present = [ i.text() for i in
                                self.manual_list_vectors.findItems('', Qt.MatchContains) ]

        for vector_name in vector_names:
            if not vector_name in already_present:
                self.manual_list_vectors.addItem(vector_name)

        self.acqid = acqid
        self.page_by_acqid_lineedit_start.setText(self.acqid)
        self.page_by_acqid_lineedit_stop.setText (self.acqid)

        return


    def vector_selected(self, acqid, vector_name):
        """ Mettre à jour manual_list_vectors avec le nom reçu.
        """
        logger.log(logging.RUN, f"Exportation::vector_selected : " + \
                                f"acqid = {acqid}, " +\
                                f"vector_name = {vector_name}")

        self.multi_vectors_selected(acqid, [ vector_name ])

        return


    def see_result(self):
        """ Lancer un termincal et ncview sur le résultat.
        """
        logger.log(logging.RUN, "Exportation::see_result")

        # rechercher le nom du fichier dernier .nc généré (avec ou sans le nom
        # de l'utilisateur
        prefix = self.config['prefix'] + '_' + os.getenv('USER')
        all_nc_files = [ os.path.join(self.config['dir_out'], x)
                            for x in glob.glob(prefix + '*.nc',
                                               root_dir=self.config['dir_out'])
                       ]
        if not all_nc_files:
            prefix = self.config['prefix']
            all_nc_files = [ os.path.join(self.config['dir_out'], x)
                                 for x in glob.glob(prefix + '*.nc',
                                                    root_dir=self.config['dir_out'])
                           ]

        last_nc_file = max(all_nc_files, key=os.path.getctime)

        # visualisation du résultat par ncview
        runstring = f"xterm -e ncview {last_nc_file}"
        logger.debug(f"runstring = {runstring}")
        subprocess.Popen(shlex.split(runstring))

        return


    def build_conf_file(self):
        """ Construire le fichier de configuration
            (cas une configuration manuelle)
        """
        logger.log(logging.RUN, "Exportation::build_conf_file")

        conf_file = os.path.join(os.sep, 'tmp',
                                 os.getenv('USER') + '.aito_export_prod_CDF' + '.config')

        # information à l'usage de l'utilisateur
        self.result_plaintextedit.appendHtml(
                            f"<b>Génération du fichier : {conf_file}</b><br />")

        # en mode 'plage' == 'by_date', on récupère les informations nécessaires
        # à partir de l'acqid courant (elles devraient être correctes...)
        if self.config['plage'] == 'by_date':
            # récupération du nom de la plateforme
            long_name, year, num = AIDA.ID_to_full(self.config['start'])
        else:
            # récupération du nom de la plateforme
            long_name, year, num = AIDA.ID_to_full(self.acqid)
        self.result_plaintextedit.appendPlainText(f" - plateforme    : {long_name}")

        # récupérer le ref_time du premier vecteur
        name = self.manual_list_vectors.item(0).text()
        vector = Vector(acqid=self.acqid, name=name)
        ref_time = vector.header['ref_time']
        self.result_plaintextedit.appendPlainText(f" - ref_time      : {ref_time}")


        if self.config['prod_mode'] == 'Un fichier pour la période':
            base_temps = 'periode'
        else:
            base_temps = 'jour'
        self.result_plaintextedit.appendPlainText(f" - base de temps : {base_temps}\n")

        # création d'un configparser
        config = configparser.ConfigParser(interpolation=None)
        # empêcher configparser de passer les noms d'option en minuscule
        config.optionxform = lambda option: option

        # remplissage du parser
        # - partie générale
        config['GENERAL'] = {
                'plateforme'             : long_name,
                'reftime'                : ref_time,
                'version'                : self.config['version'],
                'processing_level'       : self.config['processing_level'],
                'base_nom_fic_out'       : self.config['prefix'] + '_' + os.getenv('USER'),
                'base_temps_fic_out'     : base_temps,
                'remplace_vecteur_absent':'True',
                }

        # - partie vecteurs
        all_names = [ i.text() for i in
                        self.manual_list_vectors.findItems('', Qt.MatchContains) ]

        for name in all_names:
            # NOTE : on a déjà lu le premier vecteur => on pourrait se passer
            #      : de le relire
            vector = Vector(acqid=self.acqid, name=name)

            # attention : pou les vecteurs temps au moins, le champ 'name'
            # n'est pas toujours postionné...
            config[name] = { "nom"        : vector.header.get('name',
                                                              vector.header['#hdr_name']),
                             "nom_vecteur": name,
                           }

        # écrire le fihier de configuration
        with open(conf_file, 'w') as handler:
            config.write(handler)

        return conf_file


    def worker_throws_info(self, s):
        """ Traitement de la ligne d'output reçu du Worker.
            Met à jour le widget d'affichage du résultat.
        """
        self.result_plaintextedit.appendPlainText(s)

        return

    def worker_completed(self, ret_code):
        """ Traitement du code de retour du Worker.
            Met à jour le widget d'affichage du résultat et le bouton
            permettant de visualiser le généré.
        """
        # TODO : le ret_code est toujour à 0 (même si prod_CDF a fait un exit 1)
        #        voir le TODO dans Worker.
        #self.result_plaintextedit.appendHtml(f"<br /><b>Terminé avec le " +\
        #                                     f"code retour {ret_code}</b>")
        self.result_plaintextedit.appendHtml(f"<br /><b>Terminé</b>")

        # valider le bouton de visualisation du résultat
        self.result_button_see.setIcon(icons['eye_opened'])
        self.result_button_see.setEnabled(True)

        return


    def run_prod(self):
        """ Lancer l'exécution
        """
        logger.log(logging.RUN, "Exportation::run_prod")

        # vérifier si les acqids ont été sélectionnés
        if not 'start' in self.config.keys():
            self.message.setText("Pas d'acqids sélectionnés.")
            self.message.exec()
            return

        # en configuration Manuelle,
        # vérifier que des vecteurs ont été sélectionnés
        if self.config['config_mode'] == 'Manuelle':
            if self.manual_list_vectors.count() == 0:
                self.message.setText("Pas de vecteurs sélectionnés.")
                self.message.exec()
                return


        # ré-initialisation de la partie résultat
        self.result_plaintextedit.setPlainText('')
        self.result_button_see.setIcon(icons['eye_closed'])
        self.result_button_see.setEnabled(False)

        # pour une configuration manuelle,
        # construire le fichier de configuration
        if self.config['config_mode'] == 'Manuelle':
            conf_file = self.build_conf_file()
        else:
            conf_file = self.config['config_file']

        # exécution
        # - information à l'usage de l'utilisateur
        tool = os.path.basename(tool_CDF)
        self.result_plaintextedit.appendHtml(f"<b>Lancement de : {tool}</b>")

        # - préparation de la commande (python -u => ne pas bufferiser les
        #   output de prod_CDF.py)
        cmd = f"{PYTHON_X_Y} -u {tool_CDF} " +\
                           f"-o {self.config['dir_out']} " +\
                           f"-v {self.config['version']} " +\
                           f"-c {conf_file} " +\
                           f"{self.config['start']} {self.config['stop']}"
        # DBG print(f"=== RUN : {cmd}")

        self.result_plaintextedit.appendPlainText(f" - commande : {cmd}\n")

        # - lancement (avec lecture au fur et à mesure des output)
        # NOTE : C'EST LÀ QUE TOUT SE JOUE
        self.work_requested.emit(cmd)

        return


    def acqid_changed(self, acqid):
        """ La Selection avertie qu'un acqid a été sélectionné.
        """
        logger.log(logging.RUN, f"Exportation::acqid_changed : " +\
                                f"acqid = {acqid}")

        self.acqid = acqid
        self.page_by_acqid_lineedit_start.setText(self.acqid)
        self.page_by_acqid_lineedit_stop.setText (self.acqid)
        # on aurait envie de laisser les vecteurs déjà sélectionnés, mais
        # cela pourrait être problématique particulièrement si la plateforme
        # n'est plus la même
        self.manual_list_vectors.clear()
        self.button_by_file.setChecked(True)
        self.display_configuration_page(self.button_by_file)

        return


    def write_settings(self):
        """ Enregistrement des préférences utilisateur.
        """
        logger.log(logging.RUN, f"Exportation::write_settings")

        logger.debug("rien à faire ?")

        return


    def restore_context(self):
        """ Restauration du contexte de la dernière session de l'utilisateur.
        """
        logger.log(logging.RUN, f"Exportation::restore_context")

        logger.debug("rien à faire ?")

        return

