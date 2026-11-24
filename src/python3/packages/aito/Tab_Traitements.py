#!/usr/bin/env python3

"""
AITO
    Gestion de la page Traitements.
"""

import sys
import os
import logging
import numpy as np

from PyQt5.QtGui     import QIcon
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout,
                             QListWidget, QStackedWidget,
                             QPushButton, QCheckBox, QWidget, QLabel, QTextEdit,
                             QDialog,
                            )
from PyQt5.QtCore    import (Qt,
                             pyqtSignal,
                            )

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

_path_resources = os.path.join(AH, 'lib', PYTHON_X_Y, 'aito', 'resources')

import AIDA

from AITO_icons     import icons, get_default_size
from AITO_operators import operators   as operators
from Vector         import Vector
from Call_Oper      import Call_Oper
from Plot           import Plot
from Operator       import Operator

logger = logging.getLogger('aito')


class Documentation(QWidget):
    """ Gestion des documentations des opérateurs.
    """

    def __init__(self, app, parent=None):
        super().__init__()

        # logger.log(logging.RUN, "Tab_Traitements::Documentation::__init__")

        self.condition = None

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMinimumWidth (600)
        self.setMinimumHeight(650)
        self.move(200, 300)

        layout = QVBoxLayout()
        self.message = QTextEdit()
        self.message.setReadOnly(True)
        layout.addWidget(self.message)

        self.setLayout(layout)



class Tab_Traitements(QWidget):
    """ Gestion de la page Traitements.
    """

    # signal de mise à jour de l'indicateur de progression
    in_progress_signal = pyqtSignal(int)

    def __init__(self, parent=None, app=None):
        super().__init__()
        logger.log(logging.RUN, "Tab_Traitements::__init__")

        self.call_oper = Call_Oper()

        self.my_opers       = list()
        self.vector         = None
        self.acqid          = None
        self.extra_rft_time = None

        self.setup_ihm(app, parent)


    def setup_ihm(self, app, parent):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Tab_Traitements::setup_ihm")

        # créer le presse-papier
        clipboard = app.clipboard()

        up_layout = QVBoxLayout()

        # graphe
        # ------
        self.plot = Plot()
        up_layout.addWidget(self.plot)

        # boutons du graphe
        button_layout = QHBoxLayout()

        # bouton prévu pour ajout un paramètre au graphe (surtout utile pour
        # l'opérateur 'Decale')
        button_add_param = QPushButton(icons['add'], None)
        button_add_param.setIconSize(get_default_size())
        button_add_param.setToolTip("Ajouter un paramètre au graphe... TO BE DONE")
        button_add_param.hide()


        button_clear = QPushButton(icons['clear'], None)
        button_clear.setIconSize(get_default_size())
        button_clear.setToolTip("Nettoyer le graphe")

        button_layout.addWidget(button_add_param)
        button_layout.addWidget(button_clear)

        up_layout.addLayout(button_layout)

        # connexions
        button_clear.clicked.connect(self.clean_up)

        # opérateurs
        # ----------
        opers_layout = QGridLayout()

        # sélection de l'opérateur
        oper_choice = QListWidget()

        # stack des pages d'opérateur
        self.pages = QStackedWidget()



        # traiter les informations de chaque opérateur
        for i, (oper_name, oper) in enumerate(operators.items()):
            oper_choice.insertItem (i, oper_name)

            # enrichir la description de l'opérateur
            oper['plot']      = self.plot
            oper['clipboard'] = clipboard

            # créer l'objet opérateur à partir de sa description
            operator = Operator(name=oper_name, parent=self, **oper)

            # mémoriser la condition de l'opérateur dans l'opérateur
            if 'condition' in oper.keys():
                operator.condition = oper['condition']
            else:
                operator.condition = None

            self.my_opers.append(operator)

            self.pages.addWidget (operator)

        # TODO : SIZE
        oper_choice.setMinimumWidth(oper_choice.sizeHintForColumn(0))

        # connexion
        oper_choice.currentRowChanged.connect(self.display)

        # boutons de documentation de l'opérateur sélectionné
        button_oper_doc = QPushButton(icons['documentation'], None)
        button_oper_doc.setIconSize(get_default_size())
        button_oper_doc.setToolTip("Documentation de l'opérateur")
        button_oper_doc.clicked.connect(self.show_doc)

        # fenêtre de la documentation
        self.documentation = Documentation(self)

        # Affichage du daignostique de l'opérateur
        self.diag_oper = QLabel()

        # ranger tout ça dans le QGridLayout
        opers_layout.addWidget(oper_choice     , 0, 0)
        opers_layout.addWidget(self.pages      , 0, 1)
        opers_layout.addWidget(button_oper_doc , 1, 0)
        opers_layout.addWidget(self.diag_oper  , 1, 1)
        opers_layout.setColumnStretch(0, 1)
        up_layout.addLayout(opers_layout)

        # positionnement du layout
        self.setLayout(up_layout)

        # sélectionner le premier opérateur
        oper_choice.setCurrentRow(0)

        self.oper_choice = oper_choice

        # préparer un Dialog bloquant (pour afficher des erreurs d'exécution)
        self.dialog = QDialog(self)
        self.dialog.resize(500, 70)
        self.dialog.setModal(True)

        dialog_layout = QVBoxLayout()
        self.message = QLabel("Erreur...")
        dialog_layout.addWidget(self.message)
        self.dialog.setLayout(dialog_layout)


    def display(self, i):
        """ Affichage de la page correspondante à l'opérateur sélectionné.
        """
        # logger.log(logging.RUN, f"Tab_Traitements::display : " +\
        #                         f"mise à jour de l'opérateur {i} : " +\
        #                         f"{self.my_opers[i].oper_name}")

        # reset des variables
        self.extra_rft_time = None

        self.pages.setCurrentIndex(i)

        if not self.vector:
            # aucun vecteur n'a été sélectionné
            return


        self.my_opers[i].update(self.vector.header,
                                self.vector.data,
                                self.vector.acqid_dir,
                                new_time_header=None)

        self.diag_oper.setText('')

        # nettoyer les données-résultat du graphe
        self.plot.clear_more_data()

        return


    def show_doc(self):
        """ Affichage de la documentation de l'opérateur sélectionné.
        """
        # logger.log(logging.RUN, "Tab_Traitements::show_doc")

        current   = self.oper_choice.currentRow()
        oper_name = self.my_opers[current].oper_name
        file = os.path.join(_path_resources, f"{oper_name}.html")

        with open(file, 'r') as handler:
            self.documentation.message.setText(handler.read())
        self.documentation.setWindowTitle(f"{oper_name}")

        # si la fenêtre est iconifiée, la désiconifier
        self.documentation.setWindowState(Qt.WindowNoState)
        self.documentation.show()

        return


    def update_buttons(self, button_clip, button_exec, condition_label):
        """ Valide/dévalide les boutons ClipBoard et Exec de l'opérateur en
            fonction de la conditions enregistrée.
        """
        # logger.log(logging.RUN, "Tab_Traitements::update_buttons")

        if not button_exec:
            return

        # numéro de l'opérateur courant
        i = self.oper_choice.currentRow()

        # commencer par (re)valider les boutons
        button_clip.setEnabled(True)
        button_exec.setEnabled(True)
        condition_label.setText('')

        # tester la condition
        if self.my_opers[i].condition:
            condition = self.my_opers[i].condition
            try:
                cond_value = eval(condition)
                if not cond_value:
                    button_clip.setEnabled(False)
                    button_exec.setEnabled(False)
                    condition_label.setText(f"(condition = '{condition}')")
            except Exception as e:
                raise Exception(f"Tab_Traitements.py::update_exec_button : " +\
                                f"erreur lors de l'évaluation de : " +\
                                f"'{condition}'")

        return


    def update_extra_rft_time(self, name_rft_time):
        """ Mise à jour du vecteur temps supplémentaire utilisé par
            l'opérateur (ex pour MoyEch_tps_impos)
            L'opérateur mettra à jour les widgets qui dépendent de
            ce ref_time.
        """
        logger.log(logging.RUN, f"Tab_Traitements::update_extra_rft_time : " +\
                                f">{name_rft_time}<)")

        self.in_progress_signal.emit(0)

        if name_rft_time is None:
            self.extra_rft_time = None
        else:
            # création de l'objet Vector pour le vecteur sélectionné
            try:
                self.extra_rft_time = Vector(acqid=self.acqid,
                                             name=name_rft_time,
                                             rft_time=True,
                                             get_histogram=False)
            except Exception as e:
                self.message.setText(f"{e}")
                self.dialog.show()

                self.in_progress_signal.emit(100)
                return

        self.in_progress_signal.emit(100)

        return


    def exec_oper(self, cmd, index_out_data):
        """ Appel de l'opérateur et ajoute les retours au graphe.
        """
        logger.log(logging.RUN, f"Tab_Traitements::exec_oper : " +\
                                f"cmd = {cmd}")

        self.in_progress_signal.emit(0)

        ret, diag, data = self.call_oper.exec(self.acqid, cmd)

        if ret != 0:
            self.message.setText(f"Erreur d'exécution <br>  {diag}")
            self.dialog.show()

            self.in_progress_signal.emit(100)
            return

        # afficher le diagnostique retournée par l'opérateur
        # par blocs de n caractères
        n = 80
        diag_chunks = [ diag[i:i+n] for i in range(0, len(diag), n)]
        self.diag_oper.setText(f"{'<br>'.join(diag_chunks)}")

        # ajouter au graphe, les données retournées par l'opérateur
        if self.extra_rft_time:
            self.plot.plot_more_data(data[index_out_data], self.extra_rft_time.time)
        else:
            self.plot.plot_more_data(data[index_out_data], self.vector.time)

        self.in_progress_signal.emit(100)

        return


    def clean_up(self):
        """ Remet le graphe dans son état initial.
        """
        # logger.log(logging.RUN, f"Tab_Traitements::clean_up")

        self.plot.clear_more_data()

        return


    def update(self, **kwargs):
        """ Mise à jour de la page.
        """
        logger.log(logging.RUN, f"Tab_Traitements::update : " +\
                                f"kwargs.items() = {kwargs.items()}")

        if 'vector' in kwargs.keys():
            self.in_progress_signal.emit(0)

            vector = kwargs['vector']
            logger.debug(f"acqid = {vector.acqid}, name = {vector.name}")

            self.acqid  = vector.acqid
            self.vector = vector

            # remise à jour l'opérateur courant
            i = self.oper_choice.currentRow()
            self.display(i)

            # mise à jour du graphe
            self.plot.update(self.vector.data,
                             self.vector.time,
                             self.vector.header,
                             self.vector.name)

            self.in_progress_signal.emit(100)

        return

