import os
import unittest
import logging
import numpy as np
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import time 
import vtkSegmentationCorePython as vtkSegmentationCore 

#
# AblationPlanner
#

class AblationPlanner(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "AblationPlanner"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = ["ModelToModelDistance"]  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Nathaniel Rex (Brown University)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
See  <a href="https://github.com/naterex23/SlicerAblationPlanner">documentation</a> for details.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
  """
  Add data sets to Sample Data module.
  """
  # It is always recommended to provide sample data for users to make it easy to try the module,
  # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # To ensure that the source code repository remains small (can be downloaded and installed quickly)
  # it is recommended to store data sets that are larger than a few MB in a Github release.

  # AblationPlanner1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='AblationPlanner',
    sampleName='AblationPlanner1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'AblationPlanner1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='AblationPlanner1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='AblationPlanner1'
  )


#
# AblationPlannerWidget
#

class AblationPlannerWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self.updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/AblationPlanner.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    #COMMENTED OUT

    self.nodeSelectors = [
            (self.ui.MRMLNodeComboBox_5, "InputSurface"),
            (self.ui.endPointsMarkupsSelector,"EndPoints"),
            (self.ui.MRMLNodeComboBox_3, "NativeFiducials"),
            (self.ui.MRMLNodeComboBox_4, "NewFiducials"),
            (self.ui.MRMLNodeComboBox_6, "InputTumor")
            ]

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    #COMMENTED OUT

     
	#self._addInputVolumeSection()


    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = AblationPlannerLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
  
    # Buttons
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton) 
    self.ui.PushButton.connect('clicked(bool)', self.onProbeButton)
    self.ui.PushButton_2.connect('clicked(bool)', self.onTumorButton)
    self.ui.PushButton_3.connect('clicked(bool)', self.onMarginButton)
    self.ui.PushButton_4.connect('clicked(bool)', self.onColorButton)
    self.ui.PushButton_5.connect('clicked(bool)', self.onReColorButton)

    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    for nodeSelector, roleName in self.nodeSelectors:
        nodeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    # Make sure parameter node is initialized (needed for module reload)
    #self.initializeParameterNode()
    self.updateGUIFromParameterNode()


  def cleanup(self):
    self.removeObservers()

  #def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    #self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.
    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user


  def setParameterNode(self, inputParameterNode):
    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    self._parameterNode = inputParameterNode
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    parameterNode = self._parameterNode
    if not slicer.mrmlScene.IsNodePresent(parameterNode):
        parameterNode = None

    if parameterNode is None:
        return

    
    if self.updatingGUIFromParameterNode:
        return
    self.updatingGUIFromParameterNode = True

    wasBlocked = self.ui.MRMLNodeComboBox_5.blockSignals(True)
    self.ui.MRMLNodeComboBox_5.setCurrentNode(self._parameterNode.GetNodeReference("InputSurface"))
    self.ui.MRMLNodeComboBox_5.blockSignals(wasBlocked)
 
    wasBlocked = self.ui.endPointsMarkupsSelector.blockSignals(True)
    self.ui.endPointsMarkupsSelector.setCurrentNode(self._parameterNode.GetNodeReference("EndPoints"))
    self.ui.endPointsMarkupsSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.MRMLNodeComboBox_3.blockSignals(True)
    self.ui.MRMLNodeComboBox_3.setCurrentNode(self._parameterNode.GetNodeReference("NativeFiducialsƒ"))
    self.ui.MRMLNodeComboBox_3.blockSignals(wasBlocked)

    wasBlocked = self.ui.MRMLNodeComboBox_4.blockSignals(True)
    self.ui.MRMLNodeComboBox_4.setCurrentNode(self._parameterNode.GetNodeReference("NewFiducials"))
    self.ui.MRMLNodeComboBox_4.blockSignals(wasBlocked)

    wasBlocked = self.ui.MRMLNodeComboBox_6.blockSignals(True)
    self.ui.MRMLNodeComboBox_6.setCurrentNode(self._parameterNode.GetNodeReference("InputTumor"))
    self.ui.MRMLNodeComboBox_6.blockSignals(wasBlocked)

    #consider adding enabled 
    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    #for nodeSelector, roleName in self.nodeSelectors:
    #    self._parameterNode.SetNodeReferenceID(roleName, nodeSelector.currentNodeID)

    #inputSurfaceNode = self._parameterNode.GetNodeReference("InputSurface")
    #if inputSurfaceNode and inputSurfaceNode.IsA("vtkMRMLSegmentationNode"):
    #    self._parameterNode.SetParameter("InputSurfaceID", self.ui.MRMLNodeComboBox_5.currentNodeID)
    #    self.ui.MRMLNodeComboBox_5.setCurrentNodeID(self._parameterNode.GetParameter("InputSurfaceID"))
    #    self.ui.MRMLNodeComboBox_5.setVisible(True)

    #inputTumorNode = self._parameterNode.GetNodeReference("InputTumor")
    #if inputTumorNode:
    #    if inputTumorNode.IsA("vtkMRMLSegmentationNode"):
    #        self._parameterNode.SetParameter("InputTumorID", self.ui.MRMLNodeComboBox_4.currentNodeID)
    #        self.ui.MRMLNodeComboBox_5.setCurrentNodeID(self._parameterNode.GetParameter("InputTumorID"))
    #        self.ui.MRMLNodeComboBox_5.setVisible(True)

    self.updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """
    if self._parameterNode is None:
            return

    for nodeSelector, roleName in self.nodeSelectors:
        self._parameterNode.SetNodeReferenceID(roleName, nodeSelector.currentNodeID)

    #inputSurfaceNode = self._parameterNode.GetNodeReference("InputSurface")
    #if inputSurfaceNode:
    #    if inputSurfaceNode.IsA("vtkMRMLSegmentationNode"):
    #        self._parameterNode.SetParameter("InputSurfaceID", self.ui.MRMLNodeComboBox_5.currentNodeID)

    #self.ui.MRMLNodeComboBox_5.setCurrentNodeID(self._parameterNode.GetParameter("InputSurfaceID"))
    #self.ui.MRMLNodeComboBox_5.setVisible(inputSurfaceNode and inputSurfaceNode.IsA("vtkMRMLSegmentationNode"))


    #inputTumorNode = self._parameterNode.GetNodeReference("InputTumor")
    #if inputTumorNode:
    #    if inputTumorNode.IsA("vtkMRMLSegmentationNode"):
    #        self._parameterNode.SetParameter("InputTumorID", self.ui.MRMLNodeComboBox_4.currentNodeID)
    #        self.ui.MRMLNodeComboBox_4.setCurrentNodeID(self._parameterNode.GetParameter("InputTumorID"))
    #        self.ui.MRMLNodeComboBox_4.setVisible(inputTumorNode and inputTumorNode.IsA("vtkMRMLSegmentationNode"))



  def onTumorButton(self):
     self.updateParameterNodeFromGUI()
     nativeFiducials = self._parameterNode.GetNodeReference("NativeFiducials")
     tableFiducials = self._parameterNode.GetNodeReference("NewFiducials")
     tumorNode = self._parameterNode.GetNodeReference("InputTumor")

     nativeTableTransform = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")

     parameters = {}
     parameters["fixedLandmarks"] = tableFiducials
     parameters["movingLandmarks"] = nativeFiducials
     parameters["saveTransform"] = nativeTableTransform
     parameters["transformType"] = "Rigid"

     FRcliNode = slicer.cli.runSync(slicer.modules.fiducialregistration, None, parameters)

     tumorNode.SetAndObserveTransformNodeID(nativeTableTransform.GetID())
     tumorNode.HardenTransform()
     self.logic.updateNodeColor(tumorNode)





  def onMarginButton(self):
    self.updateParameterNodeFromGUI()

    tumorNode = self._parameterNode.GetNodeReference("InputTumor")
    probeNode = self._parameterNode.GetNodeReference("InputSurface")

    print("You clicked the margin button!")
    outputMarginModel, resultTableNode, lowerMargin = self.logic.evaluateMargins(tumorNode, probeNode)
    
    thisDisplayNode = tumorNode.GetDisplayNode()
    thisDisplayNode.SetVisibility(False) # Hide all points

    #self._parameterNode.SetParameter("originalModelFieldArray", VTKDataArray)
    self._parameterNode.SetNodeReferenceID("outputMarginModel", outputMarginModel.GetID())
    #self._parameterNode.SetParameter("originalModelFieldData", VTKFieldData) #set original colors
    self._parameterNode.SetNodeReferenceID("resultTableNodeID", resultTableNode.GetID())
    #self._parameterNode.SetNodeReferenceID()
    VTKFieldData = outputMarginModel.GetMesh().GetAttributesAsFieldData(0)
    VTKFieldDataArray = VTKFieldData.GetArray("Absolute")

    originalColorArray = []

    for i in range(0, VTKFieldDataArray.GetSize()-1):
        thisArray = []
        thisArray.append(VTKFieldDataArray.GetValue(i))
        thisArray.append(i)
        originalColorArray.append(thisArray)


    self.originalColorArray = originalColorArray
    self.originalModelFieldData = VTKFieldData
    self.lowerMargin = lowerMargin



  def onColorButton(self):
    self.updateParameterNodeFromGUI()
    outputMarginModel = self._parameterNode.GetNodeReference("outputMarginModel")
    self.logic.changeColorsByMargin(outputMarginModel,5,10,15)
    self.logic.updateNodeColor(outputMarginModel)


  def onReColorButton(self): 
    self.updateParameterNodeFromGUI()
    outputMarginModel = self._parameterNode.GetNodeReference("outputMarginModel")
    self.logic.regenerateOriginalModelColors(outputMarginModel, self.originalColorArray)
    self.logic.updateNodeColor(outputMarginModel)


  def onApplyButton(self):
     print("You clicked the apply button!")
     self._parameterNode.SetParameter("dummy_parameter","dummy_parameter_value")
     print(self._parameterNode)


  def onProbeButton(self):
    self.updateParameterNodeFromGUI()
    try:
        slicer.util.showStatusMessage("Processing...")
        slicer.app.processEvents()  # force update
        #preprocessedPolyData = self.getPreprocessedPolyData()
        endPointsMarkupsNode = self._parameterNode.GetNodeReference("EndPoints")
        if not endPointsMarkupsNode:
            endPointsMarkupsNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode",
                slicer.mrmlScene.GetUniqueNameByString("Centerline endpoints"))
            endPointsMarkupsNode.CreateDefaultDisplayNodes()
            self._parameterNode.SetNodeReferenceID("EndPoints", endPointsMarkupsNode.GetID())
    except Exception as e:
        slicer.util.errorDisplay("Failed to detect end points: "+str(e))
    self.updateParameterNodeFromGUI()

    endPointsMarkupsNode = self._parameterNode.GetNodeReference("EndPoints")
    #print("Found endPointsMarkupsNode of length: ", num_fiducials)

    probeNode = self._parameterNode.GetNodeReference("InputSurface")
    #print("Found probe: ", probeNode)

    self.logic.process(endPointsMarkupsNode, probeNode)
    


	







#
# AblationPlannerLogic
#

class AblationPlannerLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    if not parameterNode:
        print("No parameter node entered!")

  def process(self, fiducialNode, probeNode):
    print("Processing...")
    
    if not fiducialNode:
        print("Entered fiducial node is null!")
        return

    fidCount = fiducialNode.GetNumberOfFiducials()
    print("Number of fiducials entered: ", fidCount)

    defaultPosition = [0,0,-1]
    xyz = [0,0,0]
    coordList = []
    

    if (fidCount%2 == 1):
        print("You entered an odd number of fiducials!")
    else:
        fidPairs = fidCount/2 
        nodeIds = duplicateProbeNode(int(fidPairs),probeNode)
        #print(nodeIds)
        
        for i in range(0, fidCount):
            xyz = [0,0,0]
            fiducialNode.GetNthFiducialPosition(i, xyz) #.GetNthFiducialPosition(0, [1,1,1])
            coordList.append(xyz)

    fidDistance = []
    fidVector = []
    fidUnitVector = []
    xyz1s = []

    for i in range(0, fidCount, 2):
        xyz1 = coordList[i]
        xyz1s.append(xyz1)
        xyz2 = coordList[i+1]

        #print("Calculating distance & vector for: ", xyz1, xyz2)

        fiducialDistance = (((abs(xyz2[0]-xyz1[0])) ** 2) + (abs(xyz2[1]-xyz1[1]) ** 2) + (abs(xyz2[2]-xyz1[2]) ** 2)) ** 0.5
        vector = [xyz2[0]-xyz1[0], xyz2[1]-xyz1[1], xyz2[2]- xyz1[2]]
        unitVector = [vector[0]/fiducialDistance, vector[1]/fiducialDistance, vector[2]/fiducialDistance]

        fidDistance.append(fiducialDistance)
        fidVector.append(vector)
        fidUnitVector.append(unitVector)
        
        slicer.app.processEvents()  # force update

        rigidRegistrationMatrix = rotationMatrixFromVectors(defaultPosition, unitVector)
        thisScene = probeNode.GetScene()
        probeReference = thisScene.GetNodeByID(nodeIds[int(i/2)])

        slicer.app.processEvents()  # force update

        applyTransformToProbe(rigidRegistrationMatrix, probeReference, xyz1)

    convertSegmentsToSegment(probeNode, nodeIds)


  def evaluateMargins(self, probeNode, tumorNode):
    modelNode1 = convertSegmentToModel(tumorNode)
    modelNode2 = convertSegmentToModel(probeNode)
    outputNode = findModelToModelDistance(modelNode1,modelNode2)
    VTKFieldData = outputNode.GetMesh().GetAttributesAsFieldData(0)
    #print("Number of arrays available in VTKFieldData: ", VTKFieldData.GetNumberOfArrays())
    #print("Number of tuples in VTKFieldData", VTKFieldData.GetNumberOfTuples())

    resultTableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "Points from surface distance")
    
    for j in range(0,VTKFieldData.GetNumberOfArrays()):
        resultTableNode.AddColumn(VTKFieldData.GetArray(j))


    tumorDisplayNode = tumorNode.GetDisplayNode()
    tumorDisplayNode.SetOpacity(0.2)
    probeDisplayNode = probeNode.GetDisplayNode()
    tumorDisplayNode.SetOpacity(0.2)
    thisDisplayNode = modelNode2.GetDisplayNode()
    thisDisplayNode.SetOpacity(0.2) # Hide all points
    

    distanceRange = VTKFieldData.GetArray("Absolute").GetRange()
    print("Evaluated model to model distance, found range: ", distanceRange)

    return outputNode, resultTableNode, distanceRange[0] #, array


  def updateNodeColor(self, node):
    #thisNode = slicer.util.getNode(node)
    thisDisplayNode = node.GetDisplayNode()
    thisDisplayNode.SetVisibility(False) # Hide all points
    thisDisplayNode.SetVisibility(True)
  

  def changeColorsByMargin(self, modelNode, low, med, high):

    VTKFieldData = modelNode.GetMesh().GetAttributesAsFieldData(0)

    VTKFieldDataArray = VTKFieldData.GetArray("Absolute")

    print("Size of entered array: ", VTKFieldDataArray.GetSize())
    for i in range(0,VTKFieldDataArray.GetSize()-1):
        colorval = VTKFieldDataArray.GetValue(i)
        #print(this_colorval)
        if (colorval < low):
            VTKFieldDataArray.SetValue(i,low)
        elif (colorval < med):
            VTKFieldDataArray.SetValue(i,med)
        else:
            VTKFieldDataArray.SetValue(i,high)




  def regenerateOriginalModelColors(self, modelNode, originalColorArray):

    VTKFieldData = modelNode.GetMesh().GetAttributesAsFieldData(0)
    VTKFieldDataArray = VTKFieldData.GetArray("Absolute")

    #importedData = originalModelFieldData.GetMesh().GetAttributesAsFieldData(0)
    
    for i in range(0, len(originalColorArray)-1):
        loopArray = originalColorArray[i]
        colorval = loopArray[0]
        VTKFieldDataArray.SetValue(i,colorval)


        
def convertSegmentsToSegment(probeNode, nodeIds):
    thisScene = probeNode.GetScene()

    if len(nodeIds)>0:
        print("Found multiple probe nodes, combining them into a single segment!: ", nodeIds)

    segmentationNode = slicer.vtkMRMLSegmentationNode()
    slicer.mrmlScene.AddNode(segmentationNode)
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    
    

    slicer.app.processEvents() 

    for probeNodeID in nodeIds:
        print("Processing copy of: ", probeNodeID)
        duplicateProbeNode = thisScene.GetNodeByID(probeNodeID)
        #duplicateProbeNode.GetSegmentation().SetMasterRepresentationName("Binary labelmap")
        segmentType = duplicateProbeNode.GetSegmentation().GetMasterRepresentationName()
        slicer.app.processEvents() 
        if (segmentType == "Closed surface"):
            print("Found a closed surface! ", probeNodeID)
            mergedImage = vtk.vtkPolyData()
            duplicateProbeNode.GetClosedSurfaceRepresentation(duplicateProbeNode.GetSegmentation().GetNthSegmentID(0), mergedImage)
            segmentationNode.AddSegmentFromClosedSurfaceRepresentation(mergedImage,probeNodeID,[0,1,0])
        else:
            print("Found a Binary labelmap! ", probeNodeID)
            #segmentationNode.AddSegmentFromBinaryLabelmapRepresentation(mergedImage,probeNodeID,[1,0,0])
            labelmapImage = vtkSegmentationCore.vtkOrientedImageData()
            duplicateProbeNode.GetBinaryLabelmapRepresentation(duplicateProbeNode.GetSegmentation().GetNthSegmentID(0),labelmapImage)
            segmentationNode.AddSegmentFromBinaryLabelmapRepresentation(labelmapImage,probeNodeID,[1,0,0])
        
        slicer.mrmlScene.RemoveNode(duplicateProbeNode)

    print("Number of segments found to add: ", segmentationNode.GetSegmentation().GetNumberOfSegments())

    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    #segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)


    #segmentEditorWidget.setActiveEffectByName("Logical operators")
    #effect = segmentEditorWidget.activeEffect()
    #effect.self().scriptedEffect.setParameter("Operation","UNION")
    #effect.self().scriptedEffect.setParameter("ModifierSegmentID",segmentationNode.GetSegmentation().GetNthSegmentID(1))
    #print("Found Nth segmentID: ", segmentationNode.GetSegmentation().GetNthSegmentID(1))
    #print(effect.self().modifierSegmentID())
    #effect.self().onApply()
    #segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(1))

    for i in range(1, segmentationNode.GetSegmentation().GetNumberOfSegments()):  #TWO ADDITIONAL PROBES
        segmentEditorWidget.setActiveEffectByName("Logical operators")
        effect = segmentEditorWidget.activeEffect()
        effect.self().scriptedEffect.setParameter("Operation","UNION")
        effect.self().scriptedEffect.setParameter("ModifierSegmentID",segmentationNode.GetSegmentation().GetNthSegmentID(i))
        print("Found Nth segmentID: ", segmentationNode.GetSegmentation().GetNthSegmentID(i))
        print(effect.self().modifierSegmentID())
        effect.self().onApply()
        #segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(i))

    for i in range(1, segmentationNode.GetSegmentation().GetNumberOfSegments()):  #TWO ADDITIONAL PROBES
        segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(i))

    segDisplayNode = segmentationNode.GetDisplayNode()
    segDisplayNode.SetOpacity(0.3)

    segmentationNode.GetSegmentation().CreateRepresentation("Closed surface")
    segmentationNode.GetSegmentation().SetMasterRepresentationName("Closed surface")
    segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(1))

    #segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(1))
    #segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(2))




    
    
    

def applyTransformToProbe(rm, probeNode, xyz1):
    transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")

    transformMatrixNP = np.array(
    [[rm[0,0],rm[0,1],rm[0,2], xyz1[0]],
    [rm[1,0],rm[1,1],rm[1,2], xyz1[1]],
    [rm[2,0],rm[2,1],rm[2,2], xyz1[2]],
    [0,0,0,1]])
    #SetMatrixTransformToParent
    #transformNode.SetAndObserveMatrixTransformToParent(slicer.util.vtkMatrixFromArray(transformMatrixNP))
    transformNode.SetMatrixTransformToParent(slicer.util.vtkMatrixFromArray(transformMatrixNP))
    print("Print location 4")
    slicer.app.processEvents()  # force update
    time.sleep(1)
    probeNode.SetAndObserveTransformNodeID(transformNode.GetID())
    print("Print location 5")
    slicer.app.processEvents()  # force update
    time.sleep(1)
    probeNode.HardenTransform()
    time.sleep(0.5)
    slicer.app.processEvents()


def rotationMatrixFromVectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotationMatrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotationMatrix

def duplicateProbeNode(fidPairs, probeNode):
    print("Duplicating Probes!")

    numDuplicates = int(fidPairs - 1)
    nodeIds = []
    nodeIds.append(probeNode.GetID())
    if (numDuplicates > 0):
        for i in range(0,numDuplicates):
            
            #labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
            #slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(probeNode, labelmapVolumeNode, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)
            #seg = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
            
            mergedImage = vtk.vtkPolyData()
            probeNode.GetClosedSurfaceRepresentation(probeNode.GetSegmentation().GetNthSegmentID(0), mergedImage)
            
            segmentationNode = slicer.vtkMRMLSegmentationNode()
            #segmentationNode.SetMasterRepresentationToClosedSurface()
            slicer.mrmlScene.AddNode(segmentationNode)
            
            slicer.app.processEvents()  # force update
            print("Print Location 1!")
            time.sleep(1)

            segmentationNode.CreateDefaultDisplayNodes() # only needed for display
            segmentationNode.AddSegmentFromClosedSurfaceRepresentation(mergedImage,"duplicate_node",[0,1,0])
            print(segmentationNode.GetSegmentation().GetMasterRepresentationName())
            segmentationNode.GetSegmentation().CreateRepresentation("Closed surface")
            #segmentationNode.GetSegmentation().SetMasterRepresentationName("Closed surface")
            segmentationNode.GetSegmentation().SetMasterRepresentationName("Binary labelmap")

            segDisplayNode = probeNode.GetDisplayNode()
            segDisplayNode.SetOpacity(0.1)
            segDisplayNode = segmentationNode.GetDisplayNode()
            segDisplayNode.SetOpacity(0.1)

            slicer.app.processEvents()  # force update
            print("Print Location 2!")
            time.sleep(1)
            #slicer.app.processEvents()  # force update
            #time.sleep(1)

            #slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapVolumeNode, seg)
            #seg.CreateClosedSurfaceRepresentation()

            nodeIds.append(segmentationNode.GetID())

    probeNode.GetSegmentation().CreateRepresentation("Binary labelmap")
    probeNode.GetSegmentation().SetMasterRepresentationName("Binary labelmap")
    return nodeIds




def convertSegmentToModel(segmentNode):

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    modelNode = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Folder")
    slicer.modules.segmentations.logic().ExportVisibleSegmentsToModels(segmentNode,modelNode)
    folder = shNode.GetItemDataNode(modelNode +1)
    displayNode = folder.GetDisplayNode()
    displayNode.SetOpacity(0.2)
    return folder

def findModelToModelDistance(modelNode1,modelNode2):
    print("Executing model to model distance!")

    vtkOutput = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")

    parameters = {}
    parameters["vtkFile1"] = modelNode2
    parameters["vtkFile2"] = modelNode1
    parameters['distanceType'] = "absolute_closest_point"
    parameters["vtkOutput"] = vtkOutput

    cliNode = slicer.cli.runSync(slicer.modules.modeltomodeldistance, None, parameters)
    return vtkOutput


    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputVolume: volume to be thresholded
    :param outputVolume: thresholding result
    :param imageThreshold: values above/below this threshold will be set to 0
    :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    :param showResult: show output volume in slice viewers
    """

    #if not inputVolume or not outputVolume:
    #  raise ValueError("Input or output volume is invalid")

    #import time
    #startTime = time.time()
    #logging.info('Processing started')

    # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    #cliParams = {
    #  'InputVolume': inputVolume.GetID(),
    #  'OutputVolume': outputVolume.GetID(),
    #  'ThresholdValue' : imageThreshold,
    #  'ThresholdType' : 'Above' if invert else 'Below'
    #  }
    #cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    #slicer.mrmlScene.RemoveNode(cliNode)

    #stopTime = time.time()
    #logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

#
# AblationPlannerTest
#

class AblationPlannerTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_AblationPlanner1()

  def test_AblationPlanner1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Get/create input data

    import SampleData
    registerSampleData()
    inputVolume = SampleData.downloadSample('AblationPlanner1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = AblationPlannerLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')