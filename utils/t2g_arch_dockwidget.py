# -*- coding: utf-8 -*-
"""
/***************************************************************************
 T2G_ArchDockWidget
                                 A QGIS plugin
 Archäologie-PlugIn für Tachy2Gis
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-03-17
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Daniel Timmel
        email                :
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from os import path as os_path

from PyQt5.QtWidgets import QDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os_path.join(os_path.dirname(__file__), "t2g_arch_dockwidget_base.ui"))


class T2GArchDockWidget(QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(T2GArchDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    @staticmethod
    def eLayerListe():
        return ["E_Line", "E_Polygon", "E_Point"]

    @staticmethod
    def eFeldListe():
        return ["Objekttyp", "Objektart", "Schnitt Nr", "Planum", "Material", "Befund Nr", "Fund Nr"]
