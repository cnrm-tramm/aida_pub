#!/usr/bin/env python3

"""
AIDA
    Gestion du graphe détaillé (onglet Traitement)
"""

import sys
import os
import numpy as np

from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtGui     import QColor

import pyqtgraph as pg

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA

class Plot(QWidget):
    """ Gestion du tracer des données d'un vecteur.
    """

    ORANGE     = QColor(255,173,0)
    pen_ORANGE = pg.mkPen(color=(255,173, 0), width=2)

    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__()

        self.min_width  = 400
        self.min_height = 300

        self.main_data_shape = None
        self.more_curve      = None

        self.setup_ihm()


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        self.setMinimumSize(self.min_width, self.min_height)

        layout = QVBoxLayout()

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        axis = {'bottom': pg.DateAxisItem()
               }
        plot = pg.PlotWidget(axisItems=axis)

        plot.setTitle('Données')
        plot.showGrid(x=True, y=True, alpha=0.1)

        plot.getAxis('bottom').setLabel('Données manquantes :    ')
        plot.getAxis('bottom').enableAutoSIPrefix(False)

        plot.getAxis('left').setLabel('', units="unit")
        plot.getAxis('left').enableAutoSIPrefix(False)

        # legende
        plot.addLegend(offset=(-1, 1))

        self.plot = plot

        # messages "Graphique non disponible"
        self.warning_not_1D = pg.LabelItem(
                            "Graphique non disponible.<br>" +
                            "Pour les vecteurs multi-dimensionnels, <br>" +
                            "utilisez vista ou adp.",
                            color='r')
        self.warning_not_1D.setParentItem(self.plot.graphicsItem())
        self.warning_not_1D.anchor(itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.warning_not_1D.hide()

        self.warning_bad_format = pg.LabelItem(
                            "Graphique non disponible.<br>" +
                            "Ne sait pas encore traiter ce format de vecteur.",
                            color='r')
        self.warning_bad_format.setParentItem(self.plot.graphicsItem())
        self.warning_bad_format.anchor(itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.warning_bad_format.hide()

        self.warning_all_nan = pg.LabelItem(
                            "Graphique non disponible.<br>" +
                            "Toutes les valeurs sont à NaN.",
                            color='b')
        self.warning_all_nan.setParentItem(self.plot.graphicsItem())
        self.warning_all_nan.anchor(itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.warning_all_nan.hide()

        self.warning_more_data = pg.LabelItem()
        self.warning_more_data.setParentItem(self.plot.graphicsItem())
        self.warning_more_data.anchor(itemPos=(0.5, 0.5), parentPos=(0.5, 0.5))
        self.warning_more_data.hide()

        layout.addWidget(self.plot)
        self.setLayout(layout)


    def valid_data(self, data, invval, misval):
        """ Retourne les données reçues en remplaçant les données `invalides`
            par des nan.
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


    def update(self, data, time, header, name):
        """ Mise à jour du graphe du vecteur.
        """
        # DBG print(f"=== Plot::update()")

        # clear du plot
        self.plot.clear()
        self.time = time    # ??? NO MORE USED

        # titre
        freq = ""
        if 'freq_ech' in header.keys():
            freq = f"(fréquence : {header['freq_ech']} Hz)"

        self.plot.setTitle(f"<b>{header['vol']} : {name}</b> " +\
                           f"{freq}")

        # unité
        self.plot.getAxis('left').setLabel('', units=header.get('unit'))

        if int(header['dim_array']) > 1:
            self.warning_not_1D.show()
            print("!!! Plot::update : TODO : plot multi-dimensionnel")
            return
        else:
            self.warning_not_1D.hide()

        if header['format'] == 'string32':
            self.warning_bad_format.show()
            print("!!! Plot::update : TODO : plot string32")
            return
        else:
            self.warning_bad_format.hide()

        # quelques infos pour l'utilisateur
        nan_count = np.count_nonzero(np.isnan(data.data))
        if nan_count == len(data):
            self.warning_all_nan.show()
        else:
            self.warning_all_nan.hide()

        inf_count = np.count_nonzero(np.isinf(data.data))
        self.plot.getAxis('bottom').setLabel(f"Nb values : {len(data.data)}, " +
                                             f"Nan : {nan_count}, " +
                                             f"Inf : {inf_count}")

        # calcul des obs_min et obs_max
        if int(header['dim_array']) == 1:
            s_obs_min, s_obs_max = AIDA.compute_obs_min_max(header, data)

            obs_min = None
            if s_obs_min:
                obs_min = float(s_obs_min)

            obs_max = None
            if s_obs_max:
                obs_max = float(s_obs_max)

            # calcul de la moyenne des valeurs hors nan, inf...
            invval = None
            if 'invval' in header.keys():
                invval = np.array([ header['invval'] ], data.dtype.char)[0]

            misval = None
            if 'misval' in header.keys() and header['misval'] != '' :
                misval = np.array([ header['misval'] ], data.dtype.char)[0]

            mean = np.nanmean(self.valid_data(data.data, invval, misval))

            # lignes obs_min, obs_max et mean
            for value in [obs_min, obs_max]:
                if value:
                    hLine = pg.InfiniteLine(angle=0, pen='r', pos=value)
                    self.plot.addItem(hLine, ignoreBounds=True)

            hLine = pg.InfiniteLine(angle=0, pen='g', pos=mean)
            self.plot.addItem(hLine, ignoreBounds=True)

            # label des obs_min, obs_max et mean sur l'axe droit
            axis = self.plot.getAxis('right')

            ticks = list()
            if obs_min:
                ticks.append( (obs_min, f"obs_min\n{obs_min:.2f}") )
            if mean:
                ticks.append( (mean   , f"mean\n{mean:.2f}") )
            if obs_max:
                ticks.append( (obs_max, f"obs_max\n{obs_max:.2f}") )

            axis.setTicks( [ ticks ] )
            axis.show()

            # mémoriser le shape des data principales (pyqtgraph peut lever une
            # exception "X and Y arrays must be the same shape")
            self.main_data_shape = data.shape

            # plot (plot.plot() fait le addItem)!
            self.main_curve = self.plot.plot(time, data, pen='b',
                                             name='initial')

        else:
            # mettre à jour les obs_min, obs_max du header (le vecteur n'est pas
            # écrit, mais les fonctions de mise à jour des widgets des arguments
            # des opérateurs ont besoin de ses variables)
            obs_min = None
            obs_max = None

        header['obs_min'] = str(obs_min)
        header['obs_max'] = str(obs_max)


        return


    def plot_more_data(self, data, time):
        """ Ajoute des data au graphe.
        """
        # DBG print(f"=== Plot::plot_more_data()")

        # si toutes les données sont à Nan
        nan_count = np.count_nonzero(np.isnan(data))
        if nan_count == len(data):
            self.warning_more_data.setText(
                            "Graphique non disponible.<br>" +
                            "Toutes les valeurs sont à NaN.",
                            color=self.ORANGE)
            self.warning_more_data.show()
            return

        # masquer le warning
        self.warning_more_data.hide()

        # tracer les données calculées
        if not self.more_curve:
            # plot (plot.plot() fait le addItem)!
            self.more_curve = self.plot.plot(time, data, pen=self.pen_ORANGE,
                                             name='result')
        else:
            self.more_curve.setData(time, data)

        return


    def clear_more_data(self):
        """ Nettoyer les données supplémentaires du graphe.
        """
        # DBG print(f"=== Plot::clear_more_data()")
        if self.more_curve:
            self.plot.removeItem(self.more_curve)
            self.more_curve = None
        self.warning_more_data.hide()

        return

