#!/usr/bin/env python3

"""
AIDA
    Gestion des graphes de d'aperçu.

    TODO : il faut peut-être rassembler avec Plot.py...
"""

import sys
import os
import numpy as np

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtGui     import QColor

import pyqtgraph as pg

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA
import AITO_lib

class Plot_overview(QWidget):
    """ Gestion des graphes de d'aperçu.
    """

    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__()

        self.min_width  = 300
        self.min_height = 200

        self.main_data_shape = None
        self.more_curve      = None

        self.setup_ihm()


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        self.setMinimumSize(self.min_width, self.min_height)

        # informations sur le vecteur
        self.label_vector_infos = QLabel()


        # configuration générale de pyqtgraph
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # plot des données
        axis = {'bottom': pg.DateAxisItem()
               }

        plot_curve = pg.PlotWidget(axisItems=axis)

        plot_curve.setTitle('Données')
        plot_curve.showGrid(x=True, y=True, alpha=0.1)

        plot_curve.getAxis('bottom').setLabel(' ')
        plot_curve.getAxis('bottom').enableAutoSIPrefix(False)

        plot_curve.getAxis('left').setLabel(' ', units="unit")
        plot_curve.getAxis('left').enableAutoSIPrefix(False)

        plot_curve.setMaximumHeight(350)

        self.plot_curve = plot_curve


        # plot de l'histogramme
        axis = {'left': PersentAxisItem(orientation='left')
               }

        plot_histo = pg.PlotWidget(axisItems=axis)

        plot_histo.setTitle('Distribution')
        plot_histo.showGrid(x=True, y=True, alpha=0.1)

        plot_histo.getAxis('bottom').setLabel(' ')
        plot_histo.getAxis('bottom').enableAutoSIPrefix(False)

        plot_histo.getAxis('left').setLabel(' ', units="percent")
        plot_histo.getAxis('left').enableAutoSIPrefix(False)

        plot_histo.setMaximumHeight(350)

        self.plot_histo = plot_histo


        # rangement du name dans son layout
        layout_name = QHBoxLayout()
        layout_name.addWidget(self.label_vector_infos)

        # rangement de tout ça dans le layout principal
        layout_plot = QHBoxLayout()
        layout_plot.addWidget(self.plot_curve)
        layout_plot.addWidget(self.plot_histo)

        # rangement de tout ça dans le layout principal
        layout = QVBoxLayout()
        layout.addLayout(layout_name)
        layout.addLayout(layout_plot)

        self.setLayout(layout)


        # messages "Graphique non disponible"
        self.warning_not_1D = pg.LabelItem(
                            "Graphique non disponible.<br>" +
                            "Pour les vecteurs multi-dimensionnels, <br>" +
                            "utilisez vista ou adp.",
                            color='r')
        self.warning_not_1D.setParentItem(self.plot_curve.graphicsItem())
        self.warning_not_1D.anchor(itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.warning_not_1D.hide()

        self.warning_bad_format = pg.LabelItem(
                            "Graphique non disponible.<br>" +
                            "Ne sait pas encore traiter ce format de vecteur.",
                            color='r')
        self.warning_bad_format.setParentItem(self.plot_curve.graphicsItem())
        self.warning_bad_format.anchor(itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.warning_bad_format.hide()

        self.warning_all_nan = pg.LabelItem(
                            "Graphique non disponible.<br>" +
                            "Toutes les valeurs sont à NaN.",
                            color='b')
        self.warning_all_nan.setParentItem(self.plot_curve.graphicsItem())
        self.warning_all_nan.anchor(itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.warning_all_nan.hide()

        return


    def clear(self):
        """ Nettoyage de la page
        """
        self.plot_curve.clear()
        self.plot_histo.clear()

        return


    def valid_data(self, data, invval, misval):
        """ Retourne les données reçues en remplaçant les données `invalides` par
            des nan
        """
        # TODO : il faut voir les data en float
        conditions  = [ data ==  invval,
                        data ==  misval,
                        data ==  np.inf,
                        data == -np.inf,
                      ]
        choices     = [ np.nan,
                        np.nan,
                        np.nan,
                        np.nan,
                      ]

        return np.select(conditions, choices, default=data)


    def update(self, vector):
        """ Mise à jour du graphe du vecteur.
        """
        # DBG print(f"=== Plot_overview::update()")
        acqid   = vector.acqid
        data    = vector.data
        time    = vector.time
        header  = vector.header
        name    = vector.name
        histo_X = vector.histo_X
        histo_Y = vector.histo_Y

        # affichage des données 1D seulement
        if int(header['dim_array']) > 1:
            self.warning_not_1D.show()
            print(f"!!! Plot_overview::update : TODO : plot multi-dimensionnel")

            return

        # format string32
        if header['format'] == 'string32':
            data, ticks = AITO_lib.string32_to_int(data)
            self.plot_curve.getAxis('left').setTicks( (ticks, []) )
        else:
            self.plot_curve.getAxis('left').setTicks( None )


        # clear des plots et warnings
        self.plot_curve.clear()
        self.plot_histo.clear()
        self.time = time    # ??? NO MORE USED
        self.warning_not_1D.hide()
        self.warning_bad_format.hide()

        # infos du vecteur
        freq = ""
        if 'freq_ech' in header.keys():
            freq = f"(fréquence : {header['freq_ech']} Hz)"

        self.label_vector_infos.setText(f"<b>{acqid} : {name}</b> " +\
                                        f"{freq}")

        # plot Données : unité
        self.plot_curve.getAxis('left').setLabel('', units=header.get('unit'))


        # affichage des données 1D
        if int(header['dim_array']) == 1:
            # quelques infos pour l'utilisateur
            nan_count = np.count_nonzero(np.isnan(data.data))
            if nan_count == len(data):
                self.warning_all_nan.show()
            else:
                self.warning_all_nan.hide()

            inf_count = np.count_nonzero(np.isinf(data.data))
            self.plot_curve.getAxis('bottom').setLabel(f"{len(data.data)} valeurs, " +
                                                       f"{nan_count} nan")

            # plot Données
            self.plot_curve.plot(time, data, pen='b')
            self.plot_curve.autoRange()

            # plot Histogramme
            if header['format'] == 'string32':
                self.plot_histo.hide()
            else:
                self.plot_histo.plot(histo_X, histo_Y,
                                     stepMode=True,
                                     fillLevel=0,
                                     brush=(0,0,255,150))
                self.plot_histo.autoRange()
                self.plot_histo.show()

        return


class PersentAxisItem (pg.AxisItem):
    """
    Définit l'axe des abscisses
    """
    def tickStrings(self, values, scale, spacing):

        return [str(value)[:4] for value in values]


class EmptyAxisItem (pg.AxisItem):
    """
    Définit l'axe des abscisses
    """
    def tickStrings(self, values, scale, spacing):

        return ['' for value in values]


