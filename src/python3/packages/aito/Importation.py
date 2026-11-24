#!/usr/bin/env python3

"""
AITO
    Gestion de la partie Importation.

    Importation doit :
    1) lancer le producteur mtv.py
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

from PyQt5.QtWidgets import (QWidget,
                             QLabel, QComboBox, QListWidget, QPlainTextEdit,
                             QLineEdit,
                             QPushButton, QCheckBox, QRadioButton, QButtonGroup,
                             QHBoxLayout, QVBoxLayout,
                             QGridLayout,
                             QFileDialog, QMessageBox,
                            )
from PyQt5.Qt        import (QAbstractItemView,
                            )
from PyQt5.QtGui     import (QFont,
                            )
from PyQt5.QtCore    import (Qt,
                             QThread, QObject,
                             pyqtSignal, pyqtSlot,
                             QSettings,
                            )


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
import readers

from AITO_icons import icons, get_default_size

logger = logging.getLogger('aito')


class Worker(QObject):
    # signaux de  communication avec le "propriétaire"
    info      = pyqtSignal(str)
    completed = pyqtSignal(int)

    @pyqtSlot(str)
    def do_work(self, runstring):
        # logger.log(logging.RUN, f"Importation::Worker::do_work : " +\
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
        #        semble pas lire le code d'exit de mtv...)
        ret_code = process.returncode
        self.completed.emit(ret_code)

        return


class Importation(QWidget):
    """ Gestion de la page Importation
    """
    # signal de lancement d'un processus par la class Worker
    work_requested = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Importation::__init__")

        self.parent    = kwargs.get('parent'   , None)

        # récupérer les objets de l'application (models, gest_XXX...)
        self.models    = self.parent.models
        self.gest_pltf = self.models['plateforme'].gest_pltf
        self.gest_camp = self.models['campagne'].gest_camp

        # readers
        self.reader_names = list()
        for module in readers.__all__ :
            module_name = module.__name__.split('.')[1]
            if not module_name in ['abstract_reader', 'str2time']:
                self.reader_names.append(module_name)


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
        self.settings.name = 'Importation'

        # mise en place de l'IHM
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Importation::setup_ihm")

        # les widgets graphiques
        self.combo_import_type = QComboBox()
        self.button_group      = QButtonGroup(self)
        button_pltf            = QRadioButton("Plateforme")
        button_acqid           = QRadioButton("acqid")
        self.combo_pltf        = QComboBox()
        self.lineedit_acqid    = QLineEdit()
        self.combo_camp        = QComboBox()
        self.cfg_file          = QLineEdit()
        button_cfg_file        = QPushButton(icons['folder'], None)
        button_clear_list      = QPushButton(icons['clear'], None)
        self.src_files         = QListWidget()
        button_src_files       = QPushButton(icons['folder'], None)
        button_exec            = QPushButton(icons['run'], None)
        self.option_F          = QCheckBox("option force (-F)")
        self.result            = QPlainTextEdit()

        # affinage
        self.button_group.addButton(button_pltf)
        self.button_group.addButton(button_acqid)
        button_pltf.setChecked(True)
        self.combo_pltf.setEnabled(True)
        self.lineedit_acqid.setEnabled(False)

        self.combo_import_type.addItems(self.reader_names)
        index = self.combo_import_type.findText('csv_like')
        if index != -1:
            self.combo_import_type.setCurrentIndex(index)
        self.combo_pltf.addItems(self.gest_pltf.get_names())

        self.lineedit_acqid.setPlaceholderText("Saisir un acqid")

        self.combo_camp.setEditable(True)
        self.combo_camp.addItems(["..."] + list(self.gest_camp.get_names()))
        self.combo_camp.setToolTip("sélectionner ou saisir un nom de campagne")

        button_cfg_file.setIconSize(get_default_size())
        button_cfg_file.setToolTip("sélectionner un fichier de configuration")
        self.cfg_file.setPlaceholderText("sélectionner un fichier de configuration")

        ###self.src_files.setToolTip("sélectionner des fichiers source")
        ### TODO ce serait mieux avec la touche [SUPPR]...
        self.src_files.setToolTip("""
                    <b>pour remplir cette liste :</b>
                    <ol>
                      <li>sélectionner des fichiers sources à l'aide du bouton
                          <i>sélectionner...</i>
                          (autant de fois que nécessaires)</li>
                    </ol>
                    <p>
                    <b>pour supprimer des fichiers sources de cette liste :</b>
                    <ol>
                      <li>sélectionner ici les fichiers source à supprimer</li>
                      <li>clicker sur le bouton <i>supprimer...</i>
                    </ol>""")
        self.src_files.setSelectionMode(QAbstractItemView.ExtendedSelection)

        button_src_files.setIconSize(get_default_size())
        button_src_files.setToolTip("sélectionner des fichiers source")

        button_clear_list.setIconSize(get_default_size())
        button_clear_list.setToolTip("supprimer les fichiers source sélectionnés")

        button_exec.setIconSize(get_default_size())
        button_exec.setToolTip("exécuter")

        self.result.setFont (QFont ('Courier', 12))

        # rangement de tout ça dans le layout principal
        layout = QGridLayout()
        layout.addWidget(QLabel("Type de fichier"         ), 0, 0)
        layout.addWidget(self.combo_import_type            , 0, 1, 1, -1)

        layout.addWidget(button_pltf                       , 1, 0)
        layout.addWidget(self.combo_pltf                   , 1, 1, 1, -1)

        layout.addWidget(button_acqid                      , 2, 0)
        layout.addWidget(self.lineedit_acqid               , 2, 1, 1, -1)

        layout.addWidget(QLabel("Campagne"                ), 3, 0)
        layout.addWidget(self.combo_camp                   , 3, 1, 1, -1)

        layout.addWidget(QLabel("Fichier de configuration"), 4, 0)
        layout.addWidget(self.cfg_file                     , 4, 1)
        layout.addWidget(button_cfg_file                   , 4, 2, 1, -1)

        layout.addWidget(QLabel("Fichiers source"         ), 5, 0)
        layout.addWidget(self.src_files                    , 5, 1)
        layout_1 = QVBoxLayout()
        layout_1.addWidget(button_src_files)
        layout_1.addWidget(button_clear_list, alignment=Qt.AlignBottom)
        layout.addLayout(layout_1                          , 5, 2, 1, -1)

        layout.addWidget(button_exec                       , 6, 0)
        layout.addWidget(self.option_F                     , 6, 1, 1, -1)

        layout.addWidget(QLabel("Résultat"                ), 7, 0)

        layout.addWidget(self.result                       , 8, 0, 1, -1)

        # positionnement du layout
        self.setLayout(layout)

        # connexions
        button_cfg_file.clicked.connect(self.get_configuration_file)
        self.button_group.buttonClicked.connect(self.pltf_or_acqid_clickced)
        button_src_files.clicked.connect(self.get_source_files)
        button_clear_list.clicked.connect(self.clear_list)
        button_exec.clicked.connect(self.run_prod)

        # une fenêtre pour afficher des messages
        self.message = QMessageBox(self)

        return


    def get_configuration_file(self):
        """ Affiche le dialogue de demande du nom du fichier de configuration
            Met à jour le champ correspondant
        """
        logger.log(logging.RUN, "Importation::get_configuration_file")

        filename = QFileDialog.getOpenFileName(self,
                            'Choisir le fichier de configuration',
                            filter="All(*);;config (*.config);;cfg (*.cfg)")
        if filename:
            self.cfg_file.setText(filename[0])

        return


    def pltf_or_acqid_clickced(self, button):
        """ Gère les champs correspondant à la sélection
        """
        logger.log(logging.RUN, f"Importation::pltf_or_acqid_clickced : " +\
                                f"button.text() = {button.text()}")

        if button.text() == 'Plateforme':
            self.combo_pltf.setEnabled(True)
            self.lineedit_acqid.setEnabled(False)
        else:
            self.combo_pltf.setEnabled(False)
            self.lineedit_acqid.setEnabled(True)

        return




    def get_source_files(self):
        """ Affiche le dialogue de demande des noms des fichiers source.
            Met à jour le champ correspondant
        """
        logger.log(logging.RUN, f"Importation::get_source_files")

        filenames = QFileDialog.getOpenFileNames(self,
                            'Choisir les fichierssource ',
                            )
        if filenames:
            for filename in filenames[0]:
                self.src_files.addItem(filename)

        return


    ###def clear_list(self):
    ###    """ Vide la liste des fichiers sources
    ###    """
    ###    logger.log(logging.RUN, f"Importation::clear_list")

    ###    self.src_files.clear()

    ###    return


    def clear_list(self):
        """ supprime de la liste les lignes sélectionnées.
        """
        logger.log(logging.RUN, "Importation::clear_list")
        for item in reversed(self.src_files.selectedItems()):
            row = self.src_files.row(item)
            self.src_files.takeItem(row)

        return


    def worker_throws_info(self, s):
        """ Traitement de la ligne d'output reçu du Worker.
            Met à jour le widget d'affichage du résultat.
        """
        self.result.appendPlainText(s)

        return

    def worker_completed(self, ret_code):
        """ Traitement du code de retour du Worker.
            Met à jour le widget d'affichage du résultat.
        """
        # TODO : le ret_code est toujour à 0 (même si mtv a fait un exit 1)
        #        voir le TODO dans Worker.
        #self.result.appendHtml(f"<br /><b>Terminé avec le " +\
        #                       f"code retour {ret_code}</b>")
        self.result.appendHtml(f"<br /><b>Terminé</b>")

        return


    def run_prod(self):
        """ Lancer l'exécution
        """
        logger.log(logging.RUN, f"Importation::run_prod")

        options = dict()

        # récupération (et vérification) des input
        options['-t'] = self.combo_import_type.currentText()

        if self.button_group.checkedButton().text() == 'Plateforme':
            options['-p'] = self.combo_pltf.currentText()
        elif self.button_group.checkedButton().text() == 'acqid':
            acqid = self.lineedit_acqid.text()

            if not acqid[0:2] in AIDA.plt_by_abrev.keys():
                self.message.setText(f"l'acqid '{acqid}' ne correspond à " +\
                                       "aucune plateforme")
                self.message.exec()
                return

            options['-a'] = acqid

        if not self.combo_camp.currentText().startswith('...'):
            options['-c'] = self.combo_camp.currentText()

        options['-f'] = self.cfg_file.text()

        if self.option_F.isChecked():
            options['-F'] = ''

        # exécution
        tool = os.path.join(AIDA.AIDA_getenv('BIN'), 'mtv.py')
        self.result.appendHtml(f"<b>Lancement de : {os.path.basename(tool)}</b>")

        # - préparation de la commande (python -u => ne pas bufferiser les
        #   output de mtv.py)
        cmd = f"{PYTHON_X_Y} -u {tool} "

        # ajouter les options dans l'ordre suivant
        for key in ['-F', '-a', '-p', '-c', '-f', '-t']:
            if key in options.keys():
                cmd = f"{cmd} {key} {options[key]}"

        # ajouter les sources
        all_names = [ i.text() for i in
                        self.src_files.findItems('', Qt.MatchContains) ]
        cmd = cmd + ' ' + ' '.join(all_names)
        # DBG print(f"=== RUN : {cmd}")

        # - lancement (avec lecture au fur et à mesure des output)
        # NOTE : C'EST LÀ QUE TOUT SE JOUE
        self.work_requested.emit(cmd)

        return


    def view_selected_index(self, index):
        """ Positionne la vue sur l'index reçu.
        """
        logger.log(logging.RUN, f"Importation::view_selected_index")

        logger.debug(f"index = {index} : rien à faire")

        return


    def write_settings(self):
        """ Enregistrement des préférences utilisateur.
        """
        logger.log(logging.RUN, f"Importation::write_settings")

        logger.debug("rien à faire")

        return


    def restore_context(self):
        """ Restauration du contexte de la dernière session de l'utilisateur.
        """
        logger.log(logging.RUN, f"Importation::restore_context")

        logger.debug("rien à faire")

        return

