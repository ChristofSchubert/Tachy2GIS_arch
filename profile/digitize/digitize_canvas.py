# -*- coding: utf-8 -*-

import processing
from qgis.PyQt.QtGui import QFont
from qgis.core import (
    QgsRasterLayer,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsTextFormat,
    QgsVectorLayerSimpleLabeling,
    QgsMarkerLineSymbolLayer,
    QgsLineSymbol,
    QgsFillSymbol,
    QgsCategorizedSymbolRenderer,
    QgsRendererCategory,
    QgsRuleBasedLabeling,
    Qgis,
)
from qgis.gui import QgsMapCanvas, QgsMapToolPan, QgsMapToolZoom, QgsAttributeDialog

from ..publisher import Publisher


## @brief With the ProfileImageCanvas class a map canvas element is realized. It should be used in the profile dialog
#
# Inherits from QgsMapCanvas
#
# @author Mario Uhlig, VisDat geodatentechnologie GmbH, mario.uhlig@visdat.de
# @date 2021-05-26


class DigitizeCanvas(QgsMapCanvas):
    ## The constructor.
    # @param dialogInstance pointer to the dialogInstance

    def __init__(self, dialogInstance, iFace):
        super(DigitizeCanvas, self).__init__()

        self.pup = Publisher()

        self.dialogInstance = dialogInstance

        self.imageLayer = None

        self.digiPointLayer = None
        self.digiLineLayer = None
        self.digiPolygonLayer = None

        self.digiPolygonHoverLayer = None
        self.digiPointHoverLayer = None
        self.digiLineHoverLayer = None

        self.featForm = None

        self.createMapToolPan()
        self.createMapToolZoomIn()
        self.createMapToolZoomOut()

        self.createConnects()

    ## \brief Create a point layer from Point-Eingabelayer
    #
    # \param refData
    # @returns
    def createDigiPointLayer(self, refData):
        refData["pointLayer"].selectAll()
        self.digiPointLayer = processing.run(
            "native:saveselectedfeatures",
            {"INPUT": refData["pointLayer"], "OUTPUT": "memory:"},
        )["OUTPUT"]
        refData["pointLayer"].removeSelection()

        # Layer leeren
        pr = self.digiPointLayer.dataProvider()
        pr.truncate()

        # Renderer
        symbol_profile = QgsMarkerSymbol.createSimple(
            {
                "name": "circle",
                "color": "red",
                "color_border": "black",
                "width_border": "1",
                "size": "3.0",
            }
        )

        symbol_tachy = QgsMarkerSymbol.createSimple(
            {
                "name": "circle",
                "color": "grey",
                "color_border": "black",
                "width_border": "1",
                "size": "3.0",
            }
        )

        categorized_renderer = QgsCategorizedSymbolRenderer()
        categorized_renderer.setClassAttribute("geo_quelle")

        field = self.digiPointLayer.fields().lookupField("geo_quelle")
        unique_values = self.digiPointLayer.uniqueValues(field)
        # Add a few categories
        cat1 = QgsRendererCategory("profile_object", symbol_profile, "profile")
        cat2 = QgsRendererCategory(None, symbol_tachy, "tachy")
        categorized_renderer.addCategory(cat1)
        categorized_renderer.addCategory(cat2)

        self.digiPointLayer.setRenderer(categorized_renderer)

        # Projection
        crs = refData["pointLayer"].sourceCrs()
        self.digiPointLayer.setCrs(crs)

        # rule-based labeling
        root = QgsRuleBasedLabeling.Rule(QgsPalLayerSettings())
        rule_pt = QgsRuleBasedLabeling.Rule(
            self.createLabelSettings(
                """
                    'Punkt ' + "ptnr"
                """
            ).settings()
        )
        rule_pt.settings().isExpression = True
        rule_pt.setFilterExpression(
            """
                "obj_typ" = 'Fotoentzerrpunkt' OR "obj_typ" = 'Fund' OR "obj_typ" = 'Probe' 
            """
        )
        rule_bef = QgsRuleBasedLabeling.Rule(
            self.createLabelSettings(
                """
                    'Befund ' + "bef_nr"
                """
            ).settings()
        )
        rule_bef.settings().isExpression = True
        rule_bef.setFilterExpression(
            """
                "obj_typ" = 'Befund' 
            """
        )
        root.appendChild(rule_bef)
        root.appendChild(rule_pt)

        # Apply rule-based labeling to the layer
        self.digiPointLayer.setLabeling(QgsRuleBasedLabeling(root))
        self.digiPointLayer.setLabelsEnabled(True)

    ## \brief Create a hover point layer from Point-Eingabelayer
    #
    # \param refData
    # @returns
    def createDigiPointHoverLayer(self, refData):
        refData["pointLayer"].selectAll()
        self.digiPointHoverLayer = processing.run(
            "native:saveselectedfeatures",
            {"INPUT": refData["pointLayer"], "OUTPUT": "memory:"},
        )["OUTPUT"]
        refData["pointLayer"].removeSelection()

        # Layer leeren
        pr = self.digiPointHoverLayer.dataProvider()
        pr.truncate()

        # Renderer
        symbol_profile = QgsMarkerSymbol.createSimple(
            {
                "name": "circle",
                # "color": "red",
                "color_border": "yellow",
                "width_border": "1",
                "size": "3.0",
            }
        )

        symbol_tachy = QgsMarkerSymbol.createSimple(
            {
                "name": "circle",
                # "color": "grey",
                "color_border": "yellow",
                "width_border": "1",
                "size": "3.0",
            }
        )

        categorized_renderer = QgsCategorizedSymbolRenderer()

        categorized_renderer.setClassAttribute("geo_quelle")

        field = self.digiPointHoverLayer.fields().lookupField("geo_quelle")
        unique_values = self.digiPointHoverLayer.uniqueValues(field)
        # Add a few categories
        cat1 = QgsRendererCategory("profile_object", symbol_profile, "profile")
        cat2 = QgsRendererCategory(None, symbol_tachy, "tachy")
        categorized_renderer.addCategory(cat1)
        categorized_renderer.addCategory(cat2)

        self.digiPointHoverLayer.setRenderer(categorized_renderer)

        # Projection
        crs = refData["pointLayer"].sourceCrs()
        self.digiPointHoverLayer.setCrs(crs)

    ## \brief Create a line layer from Line-Eingabelayer
    #
    # \param refData
    # @returns
    def createDigiLineLayer(self, refData):
        refData["lineLayer"].selectAll()
        self.digiLineLayer = processing.run(
            "native:saveselectedfeatures",
            {"INPUT": refData["lineLayer"], "OUTPUT": "memory:"},
        )["OUTPUT"]
        refData["lineLayer"].removeSelection()

        # Layer leeren
        pr = self.digiLineLayer.dataProvider()
        pr.truncate()

        # Renderer
        symbol_profile = QgsLineSymbol.createSimple({"line_style": "solid", "color": "black", "width": "0.8"})

        symbol_tachy = QgsLineSymbol.createSimple({"line_style": "solid", "color": "grey", "width": "0.8"})

        symbol_profile_vertex = QgsMarkerLineSymbolLayer()
        symbol_profile_vertex.setSubSymbol(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    "color": "red",
                    "color_border": "black",
                    "width_border": "1",
                    "size": "3.0",
                }
            )
        )
        symbol_profile_vertex.setPlacements(Qgis.MarkerLinePlacement.Vertex)

        symbol_tachy_vertex = QgsMarkerLineSymbolLayer()
        symbol_tachy_vertex.setSubSymbol(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    "color": "grey",
                    "color_border": "black",
                    "width_border": "1",
                    "size": "3.0",
                }
            )
        )
        symbol_tachy_vertex.setPlacements(Qgis.MarkerLinePlacement.Vertex)

        symbol_profile.appendSymbolLayer(symbol_profile_vertex)
        symbol_tachy.appendSymbolLayer(symbol_tachy_vertex)

        # Add a few categories
        categorized_renderer = QgsCategorizedSymbolRenderer()
        categorized_renderer.setClassAttribute("geo_quelle")
        cat1 = QgsRendererCategory("profile_object", symbol_profile, "profile")
        cat2 = QgsRendererCategory(None, symbol_tachy, "tachy")
        categorized_renderer.addCategory(cat1)
        categorized_renderer.addCategory(cat2)

        self.digiLineLayer.renderer().setUsingSymbolLevels(True)
        self.digiLineLayer.setRenderer(categorized_renderer)

        crs = refData["lineLayer"].sourceCrs()
        self.digiLineLayer.setCrs(crs)

        # rule-based labeling
        root = QgsRuleBasedLabeling.Rule(QgsPalLayerSettings())
        rule_prof = QgsRuleBasedLabeling.Rule(
            self.createLabelSettings(
                """
                    'Profil ' + "prof_nr"
                """
            ).settings()
        )
        rule_prof.settings().isExpression = True
        rule_prof.setFilterExpression(
            """
                "obj_typ" = 'Profil'
            """
        )
        rule_bef = QgsRuleBasedLabeling.Rule(
            self.createLabelSettings(
                """
                    'Befund ' + "bef_nr"
                """
            ).settings()
        )
        rule_bef.settings().isExpression = True
        rule_bef.setFilterExpression(
            """
                "obj_typ" = 'Befund' 
            """
        )
        root.appendChild(rule_bef)
        root.appendChild(rule_prof)

        # Apply rule-based labeling to the layer
        self.digiLineLayer.setLabeling(QgsRuleBasedLabeling(root))
        self.digiLineLayer.setLabelsEnabled(True)

    ## \brief Create a hover line layer from Line-Eingabelayer
    #
    # \param refData
    # @returns
    def createDigiLineHoverLayer(self, refData):
        refData["lineLayer"].selectAll()
        self.digiLineHoverLayer = processing.run(
            "native:saveselectedfeatures",
            {"INPUT": refData["lineLayer"], "OUTPUT": "memory:"},
        )["OUTPUT"]
        refData["lineLayer"].removeSelection()

        # Layer leeren
        pr = self.digiLineHoverLayer.dataProvider()
        pr.truncate()

        # Renderer
        symbol_profile = QgsLineSymbol.createSimple(
            {
                "style": "solid",
                "color": "255, 255, 0, 50",
                "width": "2",
                "cap_style": "round",
                "join_style": "round",
            }
        )
        symbol_tachy = QgsLineSymbol.createSimple(
            {
                "style": "solid",
                "color": "255, 255, 0, 50",
                "width": "2",
                "cap_style": "round",
                "join_style": "round",
            }
        )

        symbol_profile_vertex = QgsMarkerLineSymbolLayer()
        symbol_profile_vertex.setSubSymbol(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    # "color": "red",
                    "color_border": "yellow",
                    "width_border": "1",
                    "size": "3.0",
                }
            )
        )
        symbol_profile_vertex.setPlacements(Qgis.MarkerLinePlacement.Vertex)

        symbol_tachy_vertex = QgsMarkerLineSymbolLayer()
        symbol_tachy_vertex.setSubSymbol(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    # "color": "grey",
                    "color_border": "yellow",
                    "width_border": "1",
                    "size": "3.0",
                }
            )
        )
        symbol_tachy_vertex.setPlacements(Qgis.MarkerLinePlacement.Vertex)

        symbol_profile.appendSymbolLayer(symbol_profile_vertex)
        symbol_tachy.appendSymbolLayer(symbol_tachy_vertex)

        # Add a few categories
        categorized_renderer = QgsCategorizedSymbolRenderer()
        categorized_renderer.setClassAttribute("geo_quelle")
        cat1 = QgsRendererCategory("profile_object", symbol_profile, "profile")
        cat2 = QgsRendererCategory(None, symbol_tachy, "tachy")
        categorized_renderer.addCategory(cat1)
        categorized_renderer.addCategory(cat2)

        self.digiLineHoverLayer.setRenderer(categorized_renderer)

        crs = refData["lineLayer"].sourceCrs()

        self.digiLineHoverLayer.setCrs(crs)

    ## \brief Create a polygon layer from Polygon-Eingabelayer
    #
    # \param refData
    # @returns
    def createDigiPolygonLayer(self, refData):
        refData["polygonLayer"].selectAll()
        self.digiPolygonLayer = processing.run(
            "native:saveselectedfeatures",
            {"INPUT": refData["polygonLayer"], "OUTPUT": "memory:"},
        )["OUTPUT"]
        refData["polygonLayer"].removeSelection()

        # Layer leeren
        pr = self.digiPolygonLayer.dataProvider()
        pr.truncate()

        # Renderer
        symbol_profile = QgsFillSymbol.createSimple(
            {
                "style": "no",
                "outline_style": "solid",
                "outline_color": "black",
                "outline_width": "0.8",
            }
        )

        symbol_tachy = QgsFillSymbol.createSimple(
            {
                "style": "no",
                "outline_style": "solid",
                "outline_color": "grey",
                "outline_width": "0.8",
            }
        )

        symbol_profile_vertex = QgsMarkerLineSymbolLayer()
        symbol_profile_vertex.setSubSymbol(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    "color": "red",
                    "color_border": "black",
                    "width_border": "1",
                    "size": "3.0",
                }
            )
        )
        symbol_profile_vertex.setPlacements(Qgis.MarkerLinePlacement.Vertex)

        symbol_tachy_vertex = QgsMarkerLineSymbolLayer()
        symbol_tachy_vertex.setSubSymbol(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    "color": "grey",
                    "color_border": "black",
                    "width_border": "1",
                    "size": "3.0",
                }
            )
        )
        symbol_tachy_vertex.setPlacements(Qgis.MarkerLinePlacement.Vertex)

        symbol_profile.appendSymbolLayer(symbol_profile_vertex)
        symbol_tachy.appendSymbolLayer(symbol_tachy_vertex)

        # Add a few categories
        categorized_renderer = QgsCategorizedSymbolRenderer()
        categorized_renderer.setClassAttribute("geo_quelle")
        cat1 = QgsRendererCategory("profile_object", symbol_profile, "profile")
        cat2 = QgsRendererCategory(None, symbol_tachy, "tachy")
        categorized_renderer.addCategory(cat1)
        categorized_renderer.addCategory(cat2)

        self.digiPolygonLayer.renderer().setUsingSymbolLevels(True)
        self.digiPolygonLayer.setRenderer(categorized_renderer)

        crs = refData["polygonLayer"].sourceCrs()
        self.digiPolygonLayer.setCrs(crs)

        # rule-based labeling
        root = QgsRuleBasedLabeling.Rule(QgsPalLayerSettings())
        rule_bef = QgsRuleBasedLabeling.Rule(
            self.createLabelSettings(
                """
                    'Befund ' + "bef_nr"
                """
            ).settings()
        )
        rule_bef.settings().isExpression = True
        rule_bef.setFilterExpression(
            """
                "obj_typ" = 'Befund' 
            """
        )
        root.appendChild(rule_bef)

        # Apply rule-based labeling to the layer
        self.digiPolygonLayer.setLabeling(QgsRuleBasedLabeling(root))
        self.digiPolygonLayer.setLabelsEnabled(True)

    ## \brief Create a hover polygon layer from Polygon-Eingabelayer
    #
    # \param refData
    # @returns

    def createDigiPolygonHoverLayer(self, refData):
        refData["polygonLayer"].selectAll()
        self.digiPolygonHoverLayer = processing.run(
            "native:saveselectedfeatures",
            {"INPUT": refData["polygonLayer"], "OUTPUT": "memory:"},
        )["OUTPUT"]
        refData["polygonLayer"].removeSelection()

        # Layer leeren
        pr = self.digiPolygonHoverLayer.dataProvider()
        pr.truncate()

        # Renderer
        symbol_profile = QgsFillSymbol.createSimple(
            {
                "style": "solid",
                "color": "255, 255, 0, 50",
                "outline_style": "solid",
                "outline_color": "255, 255, 0, 0",
                "outline_width": "2",
                "cap_style": "round",
                "join_style": "round",
            }
        )
        symbol_tachy = QgsFillSymbol.createSimple(
            {
                "style": "solid",
                "color": "255, 255, 0, 50",
                "outline_style": "solid",
                "outline_color": "255, 255, 0, 0",
                "outline_width": "2",
                "cap_style": "round",
                "join_style": "round",
            }
        )

        symbol_profile_vertex = QgsMarkerLineSymbolLayer()
        symbol_profile_vertex.setSubSymbol(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    # "color": "red",
                    "color_border": "yellow",
                    "width_border": "1",
                    "size": "3.0",
                }
            )
        )
        symbol_profile_vertex.setPlacements(Qgis.MarkerLinePlacement.Vertex)

        symbol_tachy_vertex = QgsMarkerLineSymbolLayer()
        symbol_tachy_vertex.setSubSymbol(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    # "color": "grey",
                    "color_border": "yellow",
                    "width_border": "1",
                    "size": "3.0",
                }
            )
        )
        symbol_tachy_vertex.setPlacements(Qgis.MarkerLinePlacement.Vertex)

        symbol_profile.appendSymbolLayer(symbol_profile_vertex)
        symbol_tachy.appendSymbolLayer(symbol_tachy_vertex)

        # Add a few categories
        categorized_renderer = QgsCategorizedSymbolRenderer()
        categorized_renderer.setClassAttribute("geo_quelle")
        cat1 = QgsRendererCategory("profile_object", symbol_profile, "profile")
        cat2 = QgsRendererCategory(None, symbol_tachy, "tachy")
        categorized_renderer.addCategory(cat1)
        categorized_renderer.addCategory(cat2)

        self.digiPolygonHoverLayer.setRenderer(categorized_renderer)

        crs = refData["polygonLayer"].sourceCrs()

        self.digiPolygonHoverLayer.setCrs(crs)

    ## \brief Add features to a hover layer
    #
    # \param linkObj
    # @returns

    def addHoverFeatures(self, linkObj):
        layer = linkObj["layer"]
        features = linkObj["features"]
        # print([(f.name(), linkObj["features"][0][f.name()]) for f in linkObj["features"][0].fields()])

        if layer == self.digiPolygonLayer:
            self.digiPolygonHoverLayer.startEditing()
            pr = self.digiPolygonHoverLayer.dataProvider()
            pr.addFeatures(features)
            self.digiPolygonHoverLayer.commitChanges()

        if layer == self.digiLineLayer:
            self.digiLineHoverLayer.startEditing()
            pr = self.digiLineHoverLayer.dataProvider()
            pr.addFeatures(features)
            self.digiLineHoverLayer.commitChanges()

        if layer == self.digiPointLayer:
            self.digiPointHoverLayer.startEditing()
            pr = self.digiPointHoverLayer.dataProvider()
            pr.addFeatures(features)
            self.digiPointHoverLayer.commitChanges()

        self.refresh()

    ## \brief Remove features from a hover layer
    #
    # \param linkObj
    # @returns

    def removeHoverFeatures(self, _):
        self.digiPolygonHoverLayer.startEditing()
        pr = self.digiPolygonHoverLayer.dataProvider()
        pr.truncate()
        self.digiPolygonHoverLayer.commitChanges()

        self.digiLineHoverLayer.startEditing()
        pr = self.digiLineHoverLayer.dataProvider()
        pr.truncate()
        self.digiLineHoverLayer.commitChanges()

        self.digiPointHoverLayer.startEditing()
        pr = self.digiPointHoverLayer.dataProvider()
        pr.truncate()
        self.digiPointHoverLayer.commitChanges()

        self.refresh()

    ## \brief Create settings for label
    #
    # \param label_field
    # @returns labelSettings

    def createLabelSettings(self, label_field):
        textFormat = QgsTextFormat()
        textFormat.setFont(QFont("Arial"))
        textFormat.setSizeUnit(Qgis.RenderUnit.RenderPixels)
        textFormat.setSize(10)

        palSettings = QgsPalLayerSettings()
        palSettings.setFormat(textFormat)
        palSettings.fieldName = label_field
        palSettings.enabled = True

        return QgsVectorLayerSimpleLabeling(palSettings)

    ## \brief Set coordinates on the statusbar in dialog instance TransformationDialog.setCoordinatesOnStatusBar() . Depends on mouse move on the map element
    #
    def canvasMoveEvent(self, event):
        x = event.x()
        y = event.y()
        self.pup.publish("moveCoordinate", {"x": x, "y": y})
        # self.dialogInstance.setCoordinatesOnStatusBar(x, y)

    ## \brief Event connections
    #
    def createConnects(self):
        # Koordinatenanzeige
        self.xyCoordinates.connect(self.canvasMoveEvent)

    ## \brief Create action to pan on the map
    #
    def createMapToolPan(self):
        self.toolPan = QgsMapToolPan(self)

    ## \brief Create action to zoom in on the map
    #
    def createMapToolZoomIn(self):
        self.toolZoomIn = QgsMapToolZoom(self, False)

    ## \brief Create action to zoom out on the map
    #
    def createMapToolZoomOut(self):
        self.toolZoomOut = QgsMapToolZoom(self, True)

    ## \brief Set extent of the map by extent of the source layer
    #
    def setExtentByImageLayer(self):
        self.setExtent(self.imageLayer.extent())
        self.refresh()

    ## \brief Edit Attributes of a feature
    #
    def editFeatureAttributes(self, uuid):
        if isinstance(self.featForm, QgsAttributeDialog):
            self.featForm.close()

        featuresPoly = self.digiPolygonLayer.getFeatures()

        for feature in featuresPoly:
            if feature["obj_uuid"] == uuid:
                self.digiPolygonLayer.startEditing()
                self.openAttributeDialog(self.digiPolygonLayer, feature)

        featuresLine = self.digiLineLayer.getFeatures()

        for feature in featuresLine:
            if feature["obj_uuid"] == uuid:
                self.digiLineLayer.startEditing()
                self.openAttributeDialog(self.digiLineLayer, feature)

        featuresPoint = self.digiPointLayer.getFeatures()

        for feature in featuresPoint:
            if feature["obj_uuid"] == uuid:
                self.digiPointLayer.startEditing()
                self.openAttributeDialog(self.digiPointLayer, feature)

    ## \brief Open attribute dialog for a feature
    #
    def openAttributeDialog(self, layer, feature):
        self.featForm = QgsAttributeDialog(
            vl=layer,
            thepFeature=feature,
            parent=self,
            featureOwner=False,
            showDialogButtons=True,
        )
        self.featForm.closeEvent = self.closeFeatForm
        self.featForm.setWindowTitle("Feature Eigenschaften")
        self.featForm.accepted.connect(self.acceptFeatForm)
        self.featForm.show()

    ## \brief Accept function on attribute dialog
    #
    def updateObjectTable(self, fields, feature):
        dataObj = {}

        for item in fields:
            if (
                item.name() == "obj_uuid"
                or item.name() == "fid"
                or item.name() == "obj_typ"
                or item.name() == "obj_art"
                or item.name() == "zeit"
                or item.name() == "material"
                or item.name() == "bemerkung"
                or item.name() == "bef_nr"
                or item.name() == "fund_nr"
                or item.name() == "probe_nr"
            ):
                dataObj[item.name()] = feature[item.name()]

        self.pup.publish("updateFeatureAttr", dataObj)

    ## \brief If the 'ok'-button of the self.featForm was clicked
    #
    def acceptFeatForm(self):
        fields = self.featForm.feature().fields()
        self.updateObjectTable(fields, self.featForm.feature())

    ## \brief Close function on attribute dialog
    #
    def closeFeatForm(self, event):
        self.digiPolygonLayer.commitChanges()
        self.digiLineLayer.commitChanges()
        self.digiPointLayer.commitChanges()

    def removeFeatureByUuid(self, uuid):
        featuresPoly = self.digiPolygonLayer.getFeatures()

        for feature in featuresPoly:
            if feature["obj_uuid"] == uuid:
                self.digiPolygonLayer.startEditing()
                self.digiPolygonLayer.deleteFeature(feature.id())
                print("commitChanges", self.digiPolygonLayer.commitChanges())

        featuresLine = self.digiLineLayer.getFeatures()

        for feature in featuresLine:
            if feature["obj_uuid"] == uuid:
                self.digiLineLayer.startEditing()
                self.digiLineLayer.deleteFeature(feature.id())
                print("commitChanges", self.digiLineLayer.commitChanges())

        featuresPoint = self.digiPointLayer.getFeatures()

        for feature in featuresPoint:
            if feature["obj_uuid"] == uuid:
                self.digiPointLayer.startEditing()
                self.digiPointLayer.deleteFeature(feature.id())
                print("commitChanges", self.digiPointLayer.commitChanges())

                # layer.dataProvider().deleteFeatures([5, 10])

    ## \brief Update canvas map element
    #
    # - Clear canvas element
    # - Validation of the source layer
    # - Show subset of the source layer - col obj_type = TransformationDialog.colNameGcpSource
    # - Marker symbol
    # - Label lyer with Id of the feature
    # - Additional display other input layers
    #
    # \param imageLayerPath

    def update(self, refData):
        # canvas leeren

        imageLayerPath = refData["profilePath"]

        self.clearCache()
        self.refresh()

        self.imageLayer = QgsRasterLayer(imageLayerPath, "Profile image")
        if not self.imageLayer.isValid():
            print("Layer failed to load!")

        sourceCrs = self.imageLayer.crs()

        # Sets canvas CRS
        self.setDestinationCrs(sourceCrs)

        # set extent to the extent of Layer E_Point
        self.setExtentByImageLayer()
        listLayers = []

        self.createDigiPointLayer(refData)
        self.createDigiLineLayer(refData)
        self.createDigiPolygonLayer(refData)

        self.createDigiPointHoverLayer(refData)
        self.createDigiLineHoverLayer(refData)
        self.createDigiPolygonHoverLayer(refData)

        listLayers.append(self.digiPointHoverLayer)
        listLayers.append(self.digiLineHoverLayer)
        listLayers.append(self.digiPolygonHoverLayer)

        listLayers.append(self.digiPointLayer)
        listLayers.append(self.digiLineLayer)
        listLayers.append(self.digiPolygonLayer)

        listLayers.append(self.imageLayer)

        self.setLayers(listLayers)

        self.pup.publish("setDigiPointLayer", self.digiPointLayer)
        self.pup.publish("setDigiLineLayer", self.digiLineLayer)
        self.pup.publish("setDigiPolygonLayer", self.digiPolygonLayer)
