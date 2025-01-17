# -*- coding: utf-8 -*-
from os import path as os_path

from PyQt5.QtWidgets import QDialog
from qgis.PyQt import uic

from ..utils.functions import setCustomProjectVariable, getCustomProjectVariable


class DlgDrucklayout(QDialog):
    def __init__(self, iface, parent=None):
        super(DlgDrucklayout, self).__init__(parent)
        self.ui = uic.loadUi(os_path.join(os_path.dirname(__file__), "myDlgDrucklayout.ui"), self)
        self.iface = iface
        self.ui.txtLayGemarkung.textChanged.connect(self.stempel)
        self.ui.txtLayGemarkung.setToolTip("Gemarkung")
        self.ui.txtLayProjektname.textChanged.connect(self.stempel)
        self.ui.txtLayProjektname.setToolTip("Projektname")
        self.ui.txtLayGemarkung.textChanged.connect(self.stempel)
        self.ui.txtLayGemarkung.setToolTip("Gemarkung")
        self.ui.txtLayGemeinde.textChanged.connect(self.stempel)
        self.ui.txtLayGemeinde.setToolTip("Gemeinde")
        self.ui.cboLayKreis.currentIndexChanged.connect(self.stempel)
        self.ui.cboLayKreis.editTextChanged.connect(self.stempel)
        self.ui.cboLayKreis.setToolTip("Kreis")
        self.ui.txtLayGemeinde.textChanged.connect(self.stempel)
        self.ui.txtLayGemeinde.setToolTip("Gemeinde")
        self.ui.cboLayHoehenbezug.currentIndexChanged.connect(self.stempel)
        self.ui.cboLayHoehenbezug.editTextChanged.connect(self.stempel)
        self.ui.cboLayHoehenbezug.setToolTip("Höhenbezug")
        self.ui.cboLayLagebezug.currentIndexChanged.connect(self.stempel)
        self.ui.cboLayLagebezug.editTextChanged.connect(self.stempel)
        self.ui.cboLayLagebezug.setToolTip("Lagebezug")
        self.ui.txtLayGelaendeaufnahme.textChanged.connect(self.stempel)
        self.ui.txtLayGelaendeaufnahme.setToolTip("Name des Vermessenden")
        self.ui.txtLayGelaendeaufnahmeDatum.textChanged.connect(self.stempel)
        self.ui.txtLayGelaendeaufnahmeDatum.setToolTip("Datum der Vermessung von bis")
        self.ui.butOK.clicked.connect(self.OK)
        self.ui.butAbbruch.clicked.connect(self.Abbruch)
        self.ui.setup()

    def setup(self):
        self.getLayAttribute()
        # self.ui.txt6.setStyleSheet("""QLineEdit { background-color: green }""")

    def OK(self):
        self.setLayAttribute()
        self.ui.close()

    def Abbruch(self):
        self.ui.close()

    def stempel(self):
        self.ui.txt3.setText(self.ui.txtLayGemarkung.text())
        self.ui.txt2.setText(self.ui.txtLayProjektname.text())
        self.ui.txt5.setText(self.ui.cboLayKreis.currentText())
        self.ui.txt4.setText(self.ui.txtLayGemeinde.text())
        self.ui.txt9.setText(self.ui.cboLayHoehenbezug.currentText())
        self.ui.txt8.setText(self.ui.cboLayLagebezug.currentText())
        self.ui.txt12.setText(self.ui.txtLayGelaendeaufnahme.text())
        self.ui.txt13.setText(self.ui.txtLayGelaendeaufnahmeDatum.text())

    def setLayAttribute(self):
        setCustomProjectVariable("Gemarkung", self.ui.txtLayGemarkung.text())
        setCustomProjectVariable("Projektname", self.ui.txtLayProjektname.text())
        setCustomProjectVariable("Kreis", self.ui.cboLayKreis.currentText())
        setCustomProjectVariable("Gemeinde", self.ui.txtLayGemeinde.text())
        setCustomProjectVariable("Hoehenbezug", self.ui.cboLayHoehenbezug.currentText())
        setCustomProjectVariable("Lagebezug", self.ui.cboLayLagebezug.currentText())
        setCustomProjectVariable("Gelaendeaufnahme", self.ui.txtLayGelaendeaufnahme.text())
        setCustomProjectVariable("Gelaendeaufnahme_Datum", self.ui.txtLayGelaendeaufnahmeDatum.text())

    def getLayAttribute(self):
        self.ui.txt1.setText(getCustomProjectVariable("aktcode"))
        self.ui.txt10.setText(getCustomProjectVariable("project_filename"))
        self.ui.txtLayGemarkung.setText(getCustomProjectVariable("Gemarkung"))
        self.ui.txtLayProjektname.setText(getCustomProjectVariable("Projektname"))
        self.ui.cboLayKreis.setCurrentText(getCustomProjectVariable("Kreis"))
        self.ui.txtLayGemeinde.setText(getCustomProjectVariable("Gemeinde"))
        self.ui.cboLayHoehenbezug.setCurrentText(getCustomProjectVariable("Hoehenbezug"))
        self.ui.cboLayLagebezug.setCurrentText(getCustomProjectVariable("Lagebezug"))
        self.ui.txtLayGelaendeaufnahme.setText(getCustomProjectVariable("Gelaendeaufnahme"))
        self.ui.txtLayGelaendeaufnahmeDatum.setText(getCustomProjectVariable("Gelaendeaufnahme_Datum"))
