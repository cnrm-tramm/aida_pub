#!/usr/bin/env python3

"""
AITO
    Selecteur de droite

    Il est lié au Selecteur de gauche (Left_selector.py) :
    - il affiche le contenu de l'index sélectionné dans le Selecteur de gauche.
    - il envoie au Selecteur de gauche, l'index selectionné si cet index n'est
      pas un vecteur.
    Les 2 Selcteurs utilisent le même model (Model_plateforme.py,
    Model_campagne.py)

    Notes de conception :
    -------------------
    Cet objet permet 2 modes d'affichages : par liste ou par icônes.
    - un QTreeView permet d'afficher plusieurs colonnes mais ne permet pas
      d'afficher en mode icône
    - un QListView ne permet pas d'afficher plusieurs colonnes mais permet
      d'afficher en mode icône
    De ce fait l'objet `Right_selector` définit un QTreeView *et* un QListView
    localisés tout les 2 à la même place, qui partagent le même model : un
    seul de ces 2 objets (QTreeView et QListView) est visible en fonction du
    bouton de sélection du mode de vue.


    NOTE : la gestion des tête de colonne (header) est pourrie : le model ne
           devrait pas le positionner. Il devrait être positionner par
           Left_selector et Right_selector (Left_selector ne veut affichier
           que la colonne 0 et ne devrait pas faire des pieds et des mains
           pour masquer les autres)
"""

import sys
import os
import logging

from PyQt5.QtWidgets import (QWidget,
                             QPushButton, QRadioButton,
                             QTreeView, QListView,
                             QLineEdit, QSlider,
                             QVBoxLayout, QHBoxLayout,
                             QSizePolicy,
                            )
from PyQt5.Qt        import (QAbstractItemView,
                             QHeaderView,
                            )
from PyQt5.QtCore    import (Qt, QSize,
                             QSortFilterProxyModel, QRegExp,
                             QSettings,
                            )


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from AITO_icons import icons, get_default_size

logger = logging.getLogger('aito')


class Right_selector(QWidget):
    """ Gestion de la sélection dans la partie droite.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Right_selector::__init__")

        self.parent      = kwargs.get('parent'     , None)
        self.name        = kwargs.get('name'       , None)
        self.models      = kwargs.get('models'     , None)
        self.select_mode = kwargs.get('select_mode', 'single')
        view_mode        = kwargs.get('view_mode', 'plateforme')

        if not self.models:
            raise Exception("Right_selector::__init : no models given")

        # raccourci d'accés au model acqid
        self.model_acqid = self.models['acqid']

        # préférences utilisateur
        self.settings = self.parent.settings

        # vue en icon/list : user préférences ou par default
        key = f'{self.settings.name}/icon_list'
        self.icon_list = self.settings.value(key, 'list')

        # mise en place de l'IHM
        self.setup_ihm(view_mode)

        return


    def setup_ihm(self, view_mode):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Right_selector::setup_ihm")

        # les widgets graphiques
        # - le bouton liste / icone
        self.button_mode = QPushButton()
        self.button_mode.setToolTip('mode liste/icône')
        if self.icon_list == 'list':
            self.button_mode.setIcon(icons['mode_list'])
        else:
            self.button_mode.setIcon(icons['mode_icon'])
        self.button_mode.setIconSize(get_default_size())


        # - un QLineEdit pour rechercher des vecteurs
        self.line_edit_filter = QLineEdit()
        self.line_edit_filter.setPlaceholderText('Rechercher')
        self.line_edit_filter.setToolTip('Rechercher les vecteurs dont le ' +\
                                         'nom contient le texte saisi')
        self.line_edit_filter.setInputMask('')
        self.line_edit_filter.setClearButtonEnabled(True)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.line_edit_filter.setSizePolicy(size_policy)

        # cacher les widgets de la recherche
        self.line_edit_filter.hide()

        # - un slider pour modifier la taille des icones
        self.slider_icon_size = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_icon_size.setToolTip("modifier la taille des icônes")
        self.slider_icon_size.setRange(8, 48)
        key = f'{self.settings.name}/icon_size'
        # -- taille des icones : user préférences ou par default
        self.slider_icon_size.setValue( int(self.settings.value(key, 16)) )

        # - un radiobutton permettant à l'utilisteur de sélectionner le mode
        #   de réglage de la taille des colonnes : User ou Auto
        self.column_mode = QRadioButton('auto')
        self.column_mode.setToolTip("taille des colonnes : automatique/manuelle")
        # -- user préférences ou par default
        key = f'{self.settings.name}/column_mode'
        self.column_mode.setChecked( int(self.settings.value(key, True)) )

        # - le model à utiliser
        model = self.models[view_mode]

        # - un proxy pour affiner les affichages
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        # -- associer le proxy et le model
        self.proxy_model.setSourceModel(model)

        # - le treeview
        self.treeview = QTreeView()
        self.treeview.sortByColumn(0, Qt.AscendingOrder)
        self.treeview.setSortingEnabled(True)
        self.treeview.setHeaderHidden(False)
        self.treeview.setRootIsDecorated(False)
        self.treeview.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        # -- associer le proxy/model au treeview
        self.treeview.setModel(self.proxy_model)

        # amélioration des performance d'affichage...
        self.treeview.setUniformRowHeights(True)


        # - le listview
        self.listview = QListView()
        # -- associer le proxy/model au listview
        self.listview.setModel(self.proxy_model)

        # affinage de treeview et du listview
        # - listview en mode icon
        self.listview.setViewMode(QListView.IconMode)
        self.listview.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listview.setResizeMode(QListView.Adjust)
        self.listview.setUniformItemSizes(True)

        # - mode de sélection
        if self.select_mode == 'single':
            self.treeview.setSelectionMode(QAbstractItemView.SingleSelection)
            self.listview.setSelectionMode(QAbstractItemView.SingleSelection)
        elif self.select_mode == 'multi':
            self.treeview.setSelectionMode(QAbstractItemView.MultiSelection)
            self.listview.setSelectionMode(QAbstractItemView.MultiSelection)
        else:
            self.treeview.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.listview.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # - visibilité du treeview et du listview selon le mode de visualisation
        if self.icon_list == 'list':
            self.treeview.setVisible(True)
            self.listview.setVisible(False)
        else:
            self.treeview.setVisible(False)
            self.listview.setVisible(True)


        # rangement de tout ça dans des layouts
        # - rangement des tools secondaires dans leur layout
        layout_tools2 = QHBoxLayout()
        layout_tools2.addWidget(self.column_mode)
        layout_tools2.addWidget(self.slider_icon_size)
        layout_tools2.addWidget(self.button_mode, stretch=0, alignment=Qt.AlignRight)

        # - rangement des tools dans leur layout
        layout_tools = QVBoxLayout()
        layout_tools.addLayout(layout_tools2)
        layout_tools.addWidget(self.line_edit_filter)

        # - rangement des widget dans leur layout
        layout_views = QHBoxLayout()
        layout_views.addWidget(self.treeview)
        layout_views.addWidget(self.listview)

        # rangement des layouts dans le layout principal
        layout = QVBoxLayout()
        layout.addLayout(layout_tools)
        layout.addLayout(layout_views)

        self.setLayout(layout)

        # connexions
        self.button_mode.clicked.connect(self.toggle_icon_list)
        self.treeview.clicked.connect(self.view_clicked)
        self.listview.clicked.connect(self.view_clicked)
        self.treeview.activated.connect(self.get_selected_vector_names)
        self.listview.activated.connect(self.get_selected_vector_names)
        self.column_mode.toggled.connect(self.toggle_column_mode)
        self.slider_icon_size.valueChanged.connect(self.change_icon_size)
        self.line_edit_filter.textChanged.connect(self.update_vectors_filtered)

        return


    def update_vectors_filtered(self, text):
        """ Met à jour l'affichage en fonction du 'text' reçu.
        """
        logger.log(logging.RUN, f"Right_selector::update_vectors_filtered : " +\
                                f"text = {text}")

        reg_expr = QRegExp(text, Qt.CaseSensitive)
        self.proxy_model.setFilterRegExp(reg_expr)

        return


    def toggle_column_mode(self, toggle):
        """ Bascule la gestion de la taille des colonnes (automatique/manuelle)
        """
        logger.log(logging.RUN, f"Right_selector::toggle_column_mode : " +\
                                f"toggle = {toggle}")

        if toggle:
            self.treeview.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        else:
            self.treeview.header().setSectionResizeMode(QHeaderView.Interactive)

        return


    def change_icon_size(self, value):
        """ Modifie la taille des icônes.
        """
        logger.log(logging.RUN, f"Right_selector::change_icon_size : " +\
                                f"value = {value}")

        # taille des icônes
        self.treeview.setIconSize(QSize(value, value))
        self.listview.setIconSize(QSize(value, value))

        return


    def toggle_icon_list(self):
        """ Bascule le mode d'affichage liste <-> icone.
        """
        logger.log(logging.RUN, f"Right_selector::toggle_icon_list : " +\
                                f"actual self.icon_list = {self.icon_list}")

        # basculer les visibilités du treeview et du listview
        if self.icon_list == 'list':
            self.icon_list = 'icon'

            self.button_mode.setIcon(icons['mode_icon'])

            self.treeview.setVisible(False)
            self.listview.setVisible(True)

        else:
            self.icon_list = 'list'

            self.button_mode.setIcon(icons['mode_list'])

            self.treeview.setVisible(True)
            self.listview.setVisible(False)

        return


    def use_view_mode(self, view_mode):
        """ Change le view_mode et le model utilisé
            ('plateforme', 'campagne', 'date')
        """
        logger.log(logging.RUN, f"Right_selector::use_view_mode : " +\
                                f"view_mode = {view_mode}")

        model = self.models[view_mode]
        self.proxy_model.setSourceModel(model)

        self.treeview.setModel(self.proxy_model)
        self.listview.setModel(self.proxy_model)

        if view_mode == 'by_date':
            # TODO : ça fini par être vraiment cochon les Head pour by_date
            model.setHorizontalHeaderLabels( [ 'Année' ] )

        # masquer la case de recherche
        self.line_edit_filter.hide()

        return


    def get_selected_vector_names(self, index):
        """ Transmet la liste des noms de vecteurs sélectionnés à son parent.

            Plusieurs vecteurs ont été sélectionnés puis la touche [ENTER]
            a été pressée (<=> sélection de plusieurs vecteurs)

            Cette méthode n'est effective que si self.select_mode n'est pas
            'single' (<=> si self.select_mode = 'multi' ou 'extended'.
        """
        logger.log(logging.RUN, f"Right_selector::get_selected_vector_names : " +\
                                f"index.data() = {index.data()}")

        # récupérer les noms des vecteurs sélectionnés
        if self.treeview.isVisible():
            indexes = self.treeview.selectionModel().selectedRows(column=0)
            vector_names = [ index.data() for index in indexes ]
        else:
            indexes = self.listview.selectedIndexes()
            vector_names = [ index.data() for index in indexes ]

        # récupérer l'aqid
        acqid = index.model().data(index, Qt.UserRole + 1)

        # remonter la liste au parent
        self.parent.multi_vectors_selected(acqid, vector_names)

        return


    def view_clicked(self, proxy_index):
        """ Gestion de la sélection d'une ligne du treeview.

            Voir le code des Model
            l'index est clickable même si l'item qui lui est lié a été
            "disablé" dans le model (QStandardItem.setEnabled(False)). Le test
                if not item.isEnabled():
                    return
            permet de ne rien faire si l'utilisateur à cliqué sur une
            "information complémentaire".
            On aurait pû aussi tester que le role était à None... mais un jour
            on donnera peut-être un rôle aux informations supplémentaires.


            # TODO ?
            # les appels à populate devrait être fait par le main...
            # et non pas dupliqué dans Left et Rigth
        """
        logger.log(logging.RUN, f"Right_selector::view_clicked : " +\
                                f"proxy_index.data() = {proxy_index.data()}")

        # récupérer l'index du modèle à partir de l'index du proxy
        index = self.proxy_model.mapToSource(proxy_index)

        # récupérer le model de l'index
        used_model      = index.model()
        used_model_name = used_model.name

        # récupérer le StandardItem lié à l'index
        item = used_model.itemFromIndex(index)

        # item sans données (voir here_doc de la méthode)
        if not item.isEnabled():
            return

        # récupérer le role dans l'arborescence de la ligne sélectionnée
        role = used_model.data(index, Qt.UserRole)

        if used_model_name == 'plateforme':
            if role == 'plateforme':
                used_model.populate_level_2(index)

            elif role == 'year':
                used_model.populate_level_3(index)

            elif role == 'num':
                # afficher les vecteurs de l'acqid
                acqid = used_model.data(index, Qt.UserRole + 1)
                self.parent.right_acqid_selected(acqid, index)

                return

        elif used_model_name == 'campagne':
            if role == 'campagne':
                used_model.populate_level_2(index)

            elif role == 'plateforme':
                used_model.populate_level_3(index)

            elif role == 'year':
                used_model.populate_level_4(index)

            elif role == 'num':
                # prévenir le parent qu'une acquisition a été cliquée
                acqid = used_model.data(index, Qt.UserRole + 1)
                self.parent.right_acqid_selected(acqid, index)

                return

        elif used_model_name == 'by_date':
            if role == 'acqid':
                # prévenir le parent qu'une acquisition a été cliquée
                acqid = index.data()
                self.parent.right_acqid_selected(acqid, index)

                return

            else:
                self.change_root(index, used_model_name)

        elif used_model_name == 'acqid':
            if role == 'vector':
                # les informations utiles sont dans la 1ière colonne, pas dans
                # les colonnes d'information
                index_at_0 = used_model.index(index.row(), 0)
                acqid = used_model.data(index_at_0, Qt.UserRole + 1)

                # prévenir le parent qu'un vecteur a été cliqué
                self.parent.vector_selected(acqid, index_at_0.data())

                return

        else:
            raise Exception(f"Right_selector::view_clicked : " +\
                            f"ne sait pas gérer le mode '{used_model_name}.")

        # prévenir le parent qu'un index a été sélectionné
        self.parent.right_selected(index)

        return


    def change_root(self, index, view_mode=None):
        """ Change la racine de l'affichage pour l'index du model reçu.

            Si le view_mode n'est pas précisé, utilise le nom du model de
            l'index reçu.
        """
        logger.log(logging.RUN, f"Right_selector::change_root : " +\
                                f"index.data() = {index.data()}, " +\
                                f"view_mode = {view_mode}")

        # model en cours (on peut être passé en model acqid)
        current_model = self.treeview.model().sourceModel().name

        # récupérer le model de l'index reçu
        used_model = index.model()

        # remettre le model de l'index aux views
        if current_model != used_model:
            self.proxy_model.setSourceModel(used_model)

        self.treeview.setModel(self.proxy_model)
        self.listview.setModel(self.proxy_model)

        if view_mode == None:
            view_mode = used_model.name

        # récupérer le proxy_index à partir de l'index
        proxy_index = self.proxy_model.mapFromSource(index)

        self.use_view_mode(view_mode)
        self.treeview.setRootIndex(proxy_index)
        self.listview.setRootIndex(proxy_index)

        # TODO : pas de meilleurs place pour faire ça ?
        if view_mode == 'by_date':
            # récupérer le role dans l'arborescence de la ligne sélectionnée
            role = used_model.data(index, Qt.UserRole)

            if role in ['year', 'month', 'day']:
                # TODO : ça fini par être vraiment cochon les Head pour by_date
                # le nom de la colonne est "ce qui est contenu dans role" =>
                # décalage d'un niveau.
                heads = {'year': 'Mois', 'month': 'Jour', 'day': 'Acqid'}
                used_model.setHorizontalHeaderLabels( [ heads[role] ] )

        return


    def display_acqid(self, acqid):
        """ Afficher la liste des vecteurs de l'acqid dans le treeview
            avec les colonnes "name | date | size".
        """
        logger.log(logging.RUN, f"Right_selector::display_acqid : " +\
                                f"acqid = {acqid}")

        # peupler la vue
        self.model_acqid.populate_acqid(acqid)

        # utiliser le model acqid et le proxy de visualisation
        model = self.model_acqid
        self.proxy_model.setSourceModel(model)

        self.treeview.setModel(self.proxy_model)
        self.listview.setModel(self.proxy_model)

        # afficher la case de recherche
        self.line_edit_filter.show()

        return


    def write_settings(self):
        """ Enregistrement des préférences utilisateur.
        """
        logger.log(logging.RUN, "Right_selector::write_settings")

        self.settings.setValue('icon_list'  , self.icon_list)
        self.settings.setValue('icon_size'  , self.slider_icon_size.value())
        self.settings.setValue('column_mode', int(self.column_mode.isChecked()))

        return

