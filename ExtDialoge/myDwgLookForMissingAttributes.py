# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LfADockWidget
                                 A QGIS plugin
 Tool für das Landesamt für Archäologie Dresden
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-11-29
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Daniel Timmel
        email                : aaa@web.de
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

from PyQt5.QtCore import QCoreApplication, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDockWidget, QMessageBox, QTableWidgetItem
from qgis.PyQt import uic
from qgis.core import QgsProject, QgsFeatureRequest, QgsExpression, Qgis, QgsMessageLog

from ..Icons import ICON_PATHS
from ..utils.functions import isNumber, progressBar

FORM_CLASS, _ = uic.loadUiType(os_path.join(os_path.dirname(__file__), "myDwgLookForMissingAttributes.ui"))


class LookForMissingAttributesDockWidget(QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(LookForMissingAttributesDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.ui = self
        self.iface = iface
        # self.layer = self.iface.mapCanvas().currentLayer()
        self.txtDelimiter.setText(",")
        self.txtDelimiter.textChanged.connect(self.setDelimiter)
        self.ui.butGo.clicked.connect(self.go)
        self.ui.butGo.setIcon(QIcon(ICON_PATHS["go-next"]))
        self.ui.butGo.setToolTip("Fehlende Nummern finden.")
        self.ui.butBefundLabel.clicked.connect(self.findBefLabel)
        self.ui.butBefundLabel.setIcon(QIcon(ICON_PATHS["Befundnr"]))
        self.ui.butBefundLabel.setToolTip("Fehlende Befundlabel finden.")
        self.ui.butBefundnr.clicked.connect(self.findBefnr)
        self.ui.butBefundnr.setIcon(QIcon(ICON_PATHS["Befundnr2"]))
        self.ui.butBefundnr.setToolTip("Fehlende Befundnummern finden.")
        self.ui.butProfnr.clicked.connect(self.findProfnr)
        self.ui.butProfnr.setIcon(QIcon(ICON_PATHS["Profil"]))
        self.ui.butProfnr.setToolTip("Fehlende Profilnummern finden.")
        self.ui.butFundnr.clicked.connect(self.findFundnr)
        self.ui.butFundnr.setIcon(QIcon(ICON_PATHS["Fund"]))
        self.ui.butFundnr.setToolTip("Fehlende Fundnummern finden.")
        self.ui.butProbnr.clicked.connect(self.findProbnr)
        self.ui.butProbnr.setIcon(QIcon(ICON_PATHS["Probe"]))
        self.ui.butProbnr.setToolTip("Fehlende Probenummern finden.")
        # self.iface.addDockWidget(Qt.RightDockWidgetArea, self.ui)
        self.delimiter = None
        self.befNrCol = []
        self.fundNrCol = []
        self.profNrCol = []
        self.probNrCol = []
        self.setup()

    def setup(self):
        layer = self.iface.mapCanvas().currentLayer()
        self.cboFieldName.addItems(layer.fields().names())
        self.befNrCol = self.numCol(",", "bef_nr")
        self.fundNrCol = self.numCol(",", "fund_nr")
        self.profNrCol = self.numCol(",", "prof_nr")
        self.probNrCol = self.numCol(",", "prob_nr")
        self.ui.txtNextBef.setText(str(self.befNrCol[-1]))
        self.ui.txtNextFund.setText(str(self.fundNrCol[-1]))
        self.ui.txtNextProf.setText(str(self.profNrCol[-1]))
        self.ui.txtNextProb.setText(str(self.probNrCol[-1]))
        # self.setDelimiter()

    def closeEvent(self, QCloseEvent):
        pass

    def setDelimiter(self):
        self.delimiter = self.txtDelimiter.currentText()

    def go(self, max):
        layer = self.iface.activeLayer()
        if self.iface.activeLayer().selectedFeatureCount() == 0:
            QMessageBox.critical(None, "Meldung", "Es sind keine Objekte selektiert!", QMessageBox.Abort)
        else:
            self.tableWidget.setRowCount(0)

            fieldname = self.cboFieldName.currentText()
            delimiter = self.delimiter  # self.txtDelimiter.text()
            numFailCol = self.numFail(delimiter, layer, fieldname, max)

            columnCount = 1
            row = 0
            column = 0
            self.tableWidget.setColumnCount(columnCount)
            self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem())
            self.tableWidget.horizontalHeaderItem(0).setText(fieldname)

            for val in numFailCol:
                self.tableWidget.insertRow(row)
                item1 = QTableWidgetItem(str(val))
                # item2.setTextAlignment(Qt.AlignHCenter)
                self.tableWidget.setItem(row, column, item1)
                row = row + 1
                pass
            pass

    def findBefLabel(self):
        layer = QgsProject.instance().mapLayersByName("E_Point")[0]
        self.iface.setActiveLayer(layer)
        find = "\"obj_typ\"='Kartenbeschriftung'"

        it = layer.getFeatures(QgsFeatureRequest(QgsExpression(str(find))))
        ids = [i.id() for i in it]
        layer.selectByIds(ids)
        self.ui.cboFieldName.setCurrentText("bef_nr")
        self.go(self.befNrCol[-1])
        pass

    def findBefnr(self):
        # layer.selectAll()
        # numFailCol = self.numFail(self.delimiter, layer, fieldname)
        layerLine = QgsProject.instance().mapLayersByName("E_Line")[0]
        layerPoly = QgsProject.instance().mapLayersByName("E_Polygon")[0]
        layerPoint = QgsProject.instance().mapLayersByName("E_Point")[0]
        layerlist = [layerLine, layerPoly, layerPoint]
        for layer in layerlist:
            pass

    def findProfnr(self):
        layer = QgsProject.instance().mapLayersByName("E_Line")[0]
        self.iface.setActiveLayer(layer)
        find = "\"obj_typ\"='Profil'"

        it = layer.getFeatures(QgsFeatureRequest(QgsExpression(str(find))))
        ids = [i.id() for i in it]
        layer.selectByIds(ids)
        self.ui.cboFieldName.setCurrentText("prof_nr")
        self.go(self.befNrCol[-1])
        pass

    def findFundnr(self):
        # TODO document why this method is empty
        pass

    def findProbnr(self):
        # TODO document why this method is empty
        pass

    def numFail(self, delimiter, layer, fieldname, max):
        numCol = []
        idField = layer.dataProvider().fieldNameIndex(fieldname)
        for feat in layer.selectedFeatures():
            attrs = feat.attributes()
            if attrs[idField] != None:
                # QgsMessageLog.logMessage('dddd', 'T2G Archäologie', Qgis.Info)
                attr = str(attrs[idField]).split(delimiter)
                for item in attr:
                    item = item.strip(" ")
                    if isNumber(item):
                        item = int(item)
                        if item not in numCol:
                            numCol.append(item)
        numCol.sort()

        numFailCol = []
        count = 1
        # max = valMax(delimiter, fieldname)
        QgsMessageLog.logMessage("max " + str(max), "T2G Archäologie", Qgis.Info)
        try:
            for i in range(numCol[0], max):
                while numCol[i - 1] > count:
                    numFailCol.append(count)
                    count = count + 1
                pass
                count = count + 1
        except IndexError:
            pass
        return numFailCol

    def numCol(self, delimiter, fieldname):

        layerLine = QgsProject.instance().mapLayersByName("E_Line")[0]
        layerPoly = QgsProject.instance().mapLayersByName("E_Polygon")[0]
        layerPoint = QgsProject.instance().mapLayersByName("E_Point")[0]
        layerlist = [layerLine, layerPoly, layerPoint]

        numCol = []
        progress = progressBar("Fortschritt")
        QCoreApplication.processEvents()
        featuremax = 0
        for layer in layerlist:
            featuremax = featuremax + layer.featureCount()
        progress.setText(str(featuremax) + " Geometrien werden analysiert")
        progress.setMaximum(featuremax)
        i = 0
        for layer in layerlist:
            idField = layer.dataProvider().fieldNameIndex(fieldname)
            for feat in layer.getFeatures():
                progress.setValue(i)
                attrs = feat.attributes()
                i = i + 1
                if attrs[idField] != None:
                    # QgsMessageLog.logMessage('dddd', 'T2G Archäologie', Qgis.Info)
                    attr = str(attrs[idField]).split(delimiter)
                    for item in attr:
                        item = item.strip(" ")
                        if isNumber(item):
                            item = int(item)
                            if item not in numCol:
                                numCol.append(item)
        numCol.sort()

        return numCol
