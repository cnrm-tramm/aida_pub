#!/usr/bin/env python3

"""
AITO
    Gestion des widgets d'appel des opérateurs (voir AITO_operators.py).

    Les paramètres de l'appel peuvent être du type
        - lineedit
        - combo

    Pour que les QDoubleValidator accèptent la 'virgule décimale' *et* le
    'point décimal', il faut postionner leur `locale` à QtCore.QLocale('en').
"""

import sys
import os
import numpy as np
import inspect


from PyQt5           import QtCore
from PyQt5.QtCore    import (QEvent, QLocale)
from PyQt5.QtWidgets import (QMessageBox,
                             QVBoxLayout, QGridLayout,
                             QWidget, QLabel,
                             QLineEdit, QComboBox, QSpinBox, QPushButton,
                             QSizePolicy,
                            )
from PyQt5.QtGui     import (QIntValidator, QDoubleValidator, QPalette, QColor,
                            QIcon)

import pyqtgraph as pg

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA

from   AITO_icons import icons, get_default_size


class Operator(QWidget):
    """ Gestion d'un traitement 'opérateur'.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

        # DBG print(f"=== Operator::__init__ : name = {kwargs.get('name')}")

        # récupération de la description reçue
        self.oper_name = kwargs.get('name')
        oper_params    = kwargs.get('args', None)

        # vérifier les outputs de l'opérateur
        self.oper_outs = kwargs.get('outs', ['data'])
        try:
            self.index_out_data = self.oper_outs.index('data')
        except Exception as e:
            raise Exception(f"IHMClasses/Operator.py::__init__ : " +\
                            f"operator : {self.oper_name} : " +\
                            f"'data' not found in " +\
                            f"'outs: {self.oper_outs}'")

        # liste des widget de l'opérateur
        self.my_widgets = list()

        # nom du vecteur courant
        self.vector_name = None

        # note : le parent doit posséder les méthodes :
        # - exec_oper(self, cmd, index_out_data)
        # - update_extra_rft_time(self, name_rft_time)
        # - update_buttons(self, button_clip, button_exec, condition_label)
        self.parent = kwargs.get('parent', None)

        self.special_lineedit_widget = list()
        self.special_combo_widgets   = list()
        self.special_min_widgets     = list()
        self.special_max_widgets     = list()

        # récupération du plot et du presse-papier
        self.plot      = kwargs.get('plot'     , None)
        self.clipboard = kwargs.get('clipboard', None)

        self.setup_ihm(oper_params)

        return


    def setup_ihm(self, oper_params):
        """ Mise en place des objets graphiques.
        """
        # DBG print(f"=== setup_ihm()")

        layout = QGridLayout()


        for i, param in enumerate(oper_params, start=1):
            param_name = QLabel(param['name'])

            if param['widget'] == 'lineedit':
                widget        = self.build_lineedit(param)
                widget.update = self.update_lineedit
            elif param['widget'] == 'combo':
                widget        = self.build_combo(param)
                widget.update = self.update_combo

            layout.addWidget(param_name        , i, 1)
            layout.addWidget(widget            , i, 2)
            layout.addWidget(widget.range_label, i, 3)

            self.my_widgets.append(widget)

        self.setLayout(layout)

        button_clipboard = QPushButton(icons['clipboard'], None)
        button_clipboard.setIconSize(get_default_size())
        button_clipboard.setToolTip("Copier la commande dans le presse-papier")
        button_clipboard.pressed.connect(self.button_clipboard_pressed)
        layout.addWidget(button_clipboard, i+1, 1)
        self.button_clipboard = button_clipboard

        button_exec = QPushButton('Execute')
        button_exec.oper_name = self.oper_name
        button_exec.pressed.connect(self.button_exec_pressed)
        self.button_exec     = button_exec
        self.condition_label = QLabel()
        self.condition_label.setStyleSheet("color:orange;")


        layout.addWidget(self.button_exec    , i+1, 2)
        layout.addWidget(self.condition_label, i+2, 2)

        layout.setRowStretch   (layout.rowCount()   , 1)
        layout.setColumnStretch(layout.columnCount(), 1)

        self.setLayout(layout)

        ## préparer un Dialog bloquant affiché lors d'un traitement
        #self.dialog = QDialog(self)
        #self.dialog.resize(500, 70)
        #self.dialog.setModal(True)

        #dialog_layout = QVBoxLayout()
        #dialog_layout.addWidget(QLabel("Merci de patienter..."))
        #self.dialog.setLayout(dialog_layout)

        # une fenêtre pour afficher des messages
        self.message = QMessageBox(self)

        return


    def build_lineedit(self, param):
        """ Construction des object graphique d'un widget de type LineEdit
            pour la gestion d'un paramètre en fonction des arguments reçus.
        """
        # DBG print(f"=== Operator.py::build_lineedit : {self.oper_name} : {param['name']}")

        # création des objets graphiques
        lineedit = QLineEdit()
        # TODO SIZE
        lineedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lineedit.setMinimumWidth(400)
        lineedit.range_label = QLabel()

        # enrichissement du widget
        lineedit.my_type               = 'lineedit'
        lineedit.name                  = param['name']
        lineedit.fct_get_default_value = None
        lineedit.fct_get_min_value     = None
        lineedit.fct_get_max_value     = None
        lineedit.fct_get_special_value = None
        lineedit.val_min               = None
        lineedit.val_max               = None
        lineedit.default               = None
        lineedit.type                  = None
        lineedit.show_range            = True
        lineedit.call_type             = None
        lineedit.outs                  = ['data']

        # étudier la description du paramètre
        # -----------------------------------
        editable = True
        # - editable
        if 'editable' in param.keys():
            lineedit.setEnabled(param['editable'])
            editable = param['editable']

        # - show_range
        if 'show_range' in param.keys():
            lineedit.show_range = param['show_range']

        # - valeur par défaut
        if 'default' in param.keys():
            if inspect.isfunction(param['default']):
                # forme : fonction
                lineedit.fct_get_default_value = param['default']
            else:
                # forme : value
                # la valeur par défault a été fournies => initialiser le lineedit
                lineedit.default = str(param['default'])
                lineedit.setText(lineedit.default)

        # - range
        if 'values' in param.keys():
            if isinstance(param['values'], list):
                # forme : [min, max] avec min et/ou max = fonction
                # param min
                if inspect.isfunction(param['values'][0]):
                    lineedit.fct_get_min_value = param['values'][0]
                else:
                    lineedit.val_min = param['values'][0]

                # param max
                if inspect.isfunction(param['values'][-1]):
                    lineedit.fct_get_max_value = param['values'][-1]
                else:
                    lineedit.val_max = param['values'][-1]

            elif inspect.isfunction(param['values']):
                # forme : fonction
                lineedit.fct_get_special_value = param['values']
            elif isinstance(param['values'], float):
                # forme : float
                if not lineedit.default:
                    lineedit.default = str(param['values'])
                lineedit.setText(str(param['values']))
            elif isinstance(param['values'], int):
                # forme : int
                if not lineedit.default:
                    lineedit.default = str(param['values'])
                lineedit.setText(str(param['values']))
            elif isinstance(param['values'], str):
                # forme : str
                if len(param['values']) == 0:
                    param['values'] = ' '
                if not lineedit.default:
                    lineedit.default = str(param['values'])
                lineedit.setText(str(param['values']))
            else:
                raise Exception(f"IHMClasses/Operator.py::build_lineedit : " +\
                                f"unexpected values field :'{param['values']}'")

        # les valeurs min/max ont été fournies => initialiser le range_label
        if lineedit.show_range:
            if 'type' in param.keys() and param['type'] in [int, float]:
                if lineedit.val_min and lineedit.val_max:
                    lineedit.range_label = QLabel(f'[{lineedit.val_min},' +\
                                                  f' {lineedit.val_max}]')


        # - type (=> le validator)
        # connexion seulement pour les int et float editables
        if 'type' in param.keys():
            if param['type'] is int:
                validator = QIntValidator()
                lineedit.setValidator(validator)
                if editable:
                    lineedit.textChanged.connect(self.lineedit_changed)
            elif param['type'] is float:
                validator = QDoubleValidator()
                validator.setLocale(QtCore.QLocale('en'))
                lineedit.setValidator(validator)
                if editable:
                    lineedit.textChanged.connect(self.lineedit_changed)

        lineedit.type      = param['type']
        lineedit.call_type = param.get('call_type', lineedit.type)


        return lineedit


    def build_combo(self, param):
        """ Construction des object graphique d'un widget de type Combo
            pour la gestion d'un paramètre en fonction des arguments reçus.
        """
        # DBG print(f"=== Operator.py::build_combo : {self.oper_name} : {param['name']}")

        # création des objets graphiques
        combo = QComboBox()
        combo.range_label = QLabel()    # inutilisé mais on sait jamais...

        # enrichissement du widget
        combo.my_type               = 'combo'
        combo.name                  = param['name']
        combo.fct_get_special_value = None
        combo.call_type             = None
        combo.changed               = None

        # étudier la description du paramètre
        # -----------------------------------
        # - editable
        if 'editable' in param.keys():
            combo.setEditable(param['editable'])

        # - values
        if 'values' in param.keys():
            if isinstance(param['values'], list):
                # forme : [v1, v2, v3...] avec vx = str()
                combo.addItems(param['values'])
            elif inspect.isfunction(param['values']):
                # forme : fonction
                combo.fct_get_special_value = param['values']
            else:
                raise Exception(f"IHMClasses/Operator.py::build_combo : " +\
                                f"unexpected values field :'{param['values']}'")

        # - call_type
        combo.call_type = param.get('call_type', str)

        # - changed
        combo.changed = param.get('changed', None)

        # connexions
        combo.currentIndexChanged.connect(self.combo_changed)

        return combo


    def update(self, header, data, acqid_path, new_time_header):
        """ Mise à jour de tous les widgets de paramètre de l'opérateur.
        """
        # DBG print(f"=== Operator.py::update : {header['#hdr_name']}, new_time_header = {new_time_header}")

        if int(header['dim_array']) > 1:
            # TODO
            print(f"!!! Operator.py::update() : TODO : traiter les vecteurs multi-dimensionnels !!!")
        ###    return

        # mémorisation du nom du vecteur (pour le clipboard)
        self.vector_name = header['#hdr_name']

        # mise à jour de chaque widget de l'opérateur
        for widget in self.my_widgets:
            widget.update(widget, header, data, acqid_path, new_time_header)

        # valider/dévalider le bouton Exec
        self.parent.update_buttons(self.button_clipboard,
                                   self.button_exec,
                                   self.condition_label)

        return


    def update_lineedit(self, widget, header, data, acqid_path, new_time_header):
        """ Mise à jour d'un widget de paramètre de type lineedit
            en fonction des arguments reçus
        """
        # DBG print(f"=== Operator.py::update_lineedit() : widget = {widget.name}")

        # valeur min/max du lineedit
        if widget.fct_get_min_value:
            min_value = widget.fct_get_min_value(header, data,
                                                 acqid_path, new_time_header)
        else:
            min_value = widget.val_min

        if widget.fct_get_max_value:
            max_value = widget.fct_get_max_value(header, data,
                                                 acqid_path, new_time_header)
        else:
            max_value = widget.val_max

        # valeur par défaut du lineedit
        if widget.fct_get_default_value:
            default_value = widget.fct_get_default_value(header, data,
                                                 acqid_path, new_time_header)
        else:
            default_value = widget.default

        # valeurs spéciales du lineedit
        special_value = None
        if widget.fct_get_special_value:
            special_value = widget.fct_get_special_value(header, data,
                                                 acqid_path, new_time_header)

        # mise à jour des widgets avec les valeurs trouvées
        if widget.validator():
            if widget.type is int:
                # si min_value = 0.0 alors "if min_value" est False
                # => tester min et max...
                if min_value or max_value:
                    widget.validator().setRange(int(min_value), int(max_value))
            elif widget.type is float:
                # si min_value = 0.0 alors "if min_value" est False
                # => tester min et max...
                if min_value or max_value:
                    widget.validator().setRange(float(min_value), float(max_value), decimals=10)

        # mise à jour du texte
        if special_value:
            val = special_value
        elif default_value:
            val = default_value
        else:
            val = min_value
        widget.setText(str(val))

        # mise à jour du range
        if widget.show_range:
            widget.range_label.setText(f'[{min_value},' +\
                                       f' {max_value}]')

        # TODO : SIZE
        widget.adjustSize()

        return


    def update_combo(self, widget, header, data, acqid_path, new_time_header):
        """ Mise à jour d'un widget de paramètre de type combo
            en fonction des arguments reçus
        """
        # DBG print(f"=== Operator.py::update_combo() : widget = {widget.name}, acqid_path = {acqid_path}")

        # valeurs spéciales du combo
        if widget.fct_get_special_value:
            # vider tous les items avant de les ré-initialiser
            # TODO : LUSTRE : il faudrait garder cette liste en mémoir +
            #      : ne réinitialiser que si on a changé d'acqid
            widget.clear()
            widget.addItems(widget.fct_get_special_value(header, data,
                                                 acqid_path, new_time_header))
            widget.setCurrentIndex(0)

        return


    def lineedit_changed(self, s):
        """ Action à mener si la valeur du combo a été changée.
        """
        sender = self.sender()
        # DBG print(f"=== Operator.py::lineedit_changed : pour {self.oper_name}::{sender.name} : s = {s}")

        if sender.hasAcceptableInput():
            sender.setStyleSheet("color:black;")
        else:
            sender.setStyleSheet("color:red;")


    def combo_changed(self, index):
        """ Action à mener si la valeur du combo a été changée.
            Si la valeur du champ contient '...' c'est que l'utilisateur n'a
            pas fait de choix (valeur mise à l'initialisation du widget)
        """
        sender = self.sender()
        ### print(f"=== combo_changed : pour {self.oper_name}::{sender.name} : index = {index} => texte = {self.sender().currentText()}")
        ### print(f"::: combo_changed : pour {self.oper_name}::{sender.name} : self.parent = {self.parent}")

        # cas où le combo est juste été vidé
        if index == -1:
            return

        sender_changed = self.sender().changed
        if sender_changed:
            for action, names in sender_changed.items():
                if action == 'read_vect':
                    if '...' in self.sender().currentText():
                        self.parent.update_extra_rft_time(None)
                    else:
                        self.parent.update_extra_rft_time(self.sender().currentText())

                    for name in names:
                        done = False
                        for widget in self.my_widgets:
                            if widget.name == name:
                                if '...' in self.sender().currentText():
                                    widget.update(widget, None, None, None,
                                                  None)
                                else:
                                    widget.update(widget, None, None, None,
                                                  self.parent.extra_rft_time.header)
                                done = True
                        if not done:
                            raise Exception(f"IHMClasses/Operator.py::combo_changed : " +\
                                            f"unexpected name field :'{name}'")
                else:
                    raise Exception(f"IHMClasses/Operator.py::combo_changed : " +\
                                    f"unexpected action field :'{action}'")


        # valider/dévalider le bouton Exec
        self.parent.update_buttons(self.button_clipboard,
                                   self.button_exec,
                                   self.condition_label)

        return


    #def set_timer(self, msec, button, dialog):
    #    """ Armement d'un timer (pour simuler le traitement de l'operateur).
    #    """
    #    def timer_end():
    #        """ traitement à l'expiration du timer
    #        """
    #        button.setEnabled(True)
    #        if dialog:
    #            dialog.hide()

    #        ## mise à jour du plot
    #        ##name, freq_ech = self.plot.update()
    #        # pour tester sur différents vecteurs, c'est tout l'IHM qu'il
    #        # faut mettre à jour
    #        self.parent.update()

    #        return


    #    # affichage d'une boite de message
    #    button.setEnabled(False)
    #    if dialog:
    #        dialog.show()

    #    # clear du plot
    #    self.plot.plot.clear()

    #    # armement du timer
    #    QTimer.singleShot(msec, timer_end)

    #    return


    def build_command(self):
        """ Retourne la commande de correspondante à la sélection faite par
            l'utilisateur.

            :return: "nom_oper (nom_vect, args, nom_sortie)"
            :rtype : str()
        """
        # DBG print(f"=== build_command()")

        # construire le début de la commande : "nom_oper ("
        cmd = f"{self.oper_name} ("

        # ajouter les arguments au format et valeur attendu par l'opérateur
        sep = ''
        for widget in self.my_widgets:
            if widget.my_type == 'lineedit':
                if widget.call_type == str:
                    # ajout de '' autour de la valeur
                    val = f"'{widget.call_type(widget.text())}'"
                elif widget.call_type == 'vector_name':
                    # ne pas ajouter de '' autour de la valeur
                    val = f"{widget.text()}"
                else:
                    val = f"{widget.call_type(widget.text())}"
                cmd = f"{cmd}{sep}{val}"

            elif widget.my_type == 'combo':
                if widget.call_type == int:
                    cmd = f"{cmd}{sep}{widget.currentIndex()}"
                elif widget.call_type == str:
                    # ajout de '' autour de la valeur
                    cmd = f"{cmd}{sep}'{widget.currentText()}'"
                elif widget.call_type == 'vector_name':
                    # ne pas ajouter de '' autour de la valeur
                    cmd = f"{cmd}{sep}{widget.currentText()}"
                else:
                    cmd = f"{cmd}{sep}{widget.currentText()}"
            sep = ', '

        # terminer la commande avec les 'noms' des vecteurs de sortie (ils ne
        # sont pas écrit => n'importe quels noms feront l'affaire.
        for out_part in self.oper_outs:
            out_name = self.vector_name.split('_')
            out_name.insert(-1, f'aito{out_part}')
            out_name = '_'.join(out_name)
            cmd = f"{cmd}, {out_name}"

        # la dernière ')'
        cmd = cmd + ')'

        return cmd


    def button_clipboard_pressed(self):
        """ Copie la commande (nom de l'opérateur et ses arguments) dans le
            presse_papier.
        """
        # DBG print(f"=== button_clipboard_pressed()")

        cmd = self.build_command()

        self.clipboard.setText(cmd)

        # message pour l'utilisateur
        text = self.clipboard.text()
        self.message.setText(f"{text} <br><br>copied to clipboard<br><br>")
        self.message.exec()

        return


    def button_exec_pressed(self):
        # DBG print(f"=== Operator.py::button_exec_pressed()")

        sender_name = self.sender().oper_name
        cmd = self.build_command()

        # lancer le traitement
        self.parent.exec_oper(cmd, self.index_out_data)

        return


if __name__ == '__main__':
    from PyQt5.QtWidgets     import QApplication, QWidget
    from AITO_operators import operators   as operators
    import AITO_icons

    app = QApplication(['Test'])

    # construire les QIcons à partir des icônes de AIDA
    AITO_icons.build_QIcons()

    #oper = operators['Filtre_RC_sdph']
    #oper = operators['Correc_pics_mnq']
    #oper = operators['Correc_hors_stat']
    #oper = operators['Comble_spline']
    #oper = operators['MoyEch_tps_impos']
    oper = operators['Decale']
    w    = Operator(**oper)

    w.show()
    sys.exit(app.exec_())
