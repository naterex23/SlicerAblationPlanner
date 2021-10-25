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
    self.parent.categories = ["Quantification"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = ["ModelToModelDistance"]  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Nathaniel Rex (Brown University), Scott Collins (Rhode Island Hospital)"]  # TODO: replace with "Firstname Lastname (Organization)"
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
    # import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
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
            (self.ui.probeNodeSelector, "InputSurface"),
            (self.ui.endPointsMarkupsSelector,"EndPoints"),
            (self.ui.nativeFiducialsSelector, "NativeFiducials"),
            (self.ui.newFiducialSelector, "NewFiducials"),
            (self.ui.tumorSegmentSelector, "InputTumor")
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
    self.ui.PushButton_7.connect('clicked(bool)', self.onHardenButton) 
    self.ui.PushButton_6.connect('clicked(bool)', self.onTranslateButton) 
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
    self.endPoints_positions = []
    self.fromDrag = False
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

    wasBlocked = self.ui.probeNodeSelector.blockSignals(True)
    self.ui.probeNodeSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputSurface"))
    self.ui.probeNodeSelector.blockSignals(wasBlocked)
 
    wasBlocked = self.ui.endPointsMarkupsSelector.blockSignals(True)
    self.ui.endPointsMarkupsSelector.setCurrentNode(self._parameterNode.GetNodeReference("EndPoints"))
    self.ui.endPointsMarkupsSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.nativeFiducialsSelector.blockSignals(True)
    self.ui.nativeFiducialsSelector.setCurrentNode(self._parameterNode.GetNodeReference("NativeFiducialsƒ"))
    self.ui.nativeFiducialsSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.newFiducialSelector.blockSignals(True)
    self.ui.newFiducialSelector.setCurrentNode(self._parameterNode.GetNodeReference("NewFiducials"))
    self.ui.newFiducialSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.tumorSegmentSelector.blockSignals(True)
    self.ui.tumorSegmentSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputTumor"))
    self.ui.tumorSegmentSelector.blockSignals(wasBlocked)


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
     


  def onMarginButton(self):
    try: 
      self.updateParameterNodeFromGUI()

      tumorNode = self._parameterNode.GetNodeReference("InputTumor")
      probeNode = self._parameterNode.GetNodeReference("combinedProbeNode")


      outputMarginModel, resultTableNode, lowerMargin, signedVals = self.logic.evaluateMargins(tumorNode, probeNode)
      
      thisDisplayNode = tumorNode.GetDisplayNode()
      thisDisplayNode.SetVisibility(False) # Hide all points

      self._parameterNode.SetNodeReferenceID("outputMarginModel", outputMarginModel.GetID())
      self._parameterNode.SetNodeReferenceID("resultTableNodeID", resultTableNode.GetID())
      VTKFieldData = outputMarginModel.GetMesh().GetAttributesAsFieldData(0)
      VTKFieldDataArray = VTKFieldData.GetArray("Signed")
      originalColorArray = []

      for i in range(0, VTKFieldDataArray.GetSize()-1):
          thisArray = []
          thisArray.append(VTKFieldDataArray.GetValue(i))
          thisArray.append(i)
          originalColorArray.append(thisArray)

      self.originalColorArray = originalColorArray
      self.originalModelFieldData = VTKFieldData
      self.lowerMargin = lowerMargin
      self.signedVals = signedVals
    except Exception as e:
      slicer.util.errorDisplay("Did you enter a segmentation? The code found an error: "+str(e))


  def onColorButton(self):
    self.updateParameterNodeFromGUI()
    outputMarginModel = self._parameterNode.GetNodeReference("outputMarginModel")
    self.logic.changeColorsByMargin(outputMarginModel,-10,-5,-2)
    self.logic.updateNodeColor(outputMarginModel)


  def onReColorButton(self): 
    self.updateParameterNodeFromGUI()
    outputMarginModel = self._parameterNode.GetNodeReference("outputMarginModel")
    self.logic.regenerateOriginalModelColors(outputMarginModel, self.originalColorArray)
    self.logic.updateNodeColor(outputMarginModel)

  def onTranslateButton(self):
    probeNode = self._parameterNode.GetNodeReference("InputSurface")

    thisScene = probeNode.GetScene()
    markupReference = thisScene.GetNodeByID(self.formerMarkupID)
    markupReference.RemoveObserver(self.observerID)
    self.removeObservers()


    nodeIds = self.probeNodeIDs
    combinedProbeNode = self.logic.convertSegmentsToSegment(probeNode, nodeIds)
    self._parameterNode.SetNodeReferenceID("combinedProbeNode", combinedProbeNode.GetID())
     

  def onHardenButton(self):
     tumorNode = self._parameterNode.GetNodeReference("InputTumor")
     tumorNode.HardenTransform()
     self.logic.updateNodeColor(tumorNode)
     

  def onProbeButton(self):
    self.updateParameterNodeFromGUI()
    if True:
      xyz = []
      endPointsMarkupsNode = self._parameterNode.GetNodeReference("EndPoints")
      probeNode = self._parameterNode.GetNodeReference("InputSurface")
      #print("Found an input probe: ", probeNode)
      probeDisplayNode = probeNode.GetDisplayNode()
      probeDisplayNode.SetVisibility(False)

      for i in range(0, endPointsMarkupsNode.GetNumberOfFiducials()):
        xyz.append([0,0,0])

      print("Number of input fiducials found: ", endPointsMarkupsNode.GetNumberOfFiducials())

      if endPointsMarkupsNode.GetNumberOfFiducials() > 2:
        if (endPointsMarkupsNode.GetNumberOfFiducials()%2 == 1):
          print("You entered an odd number of fiducials. Please enter an even number of fiducials.")
        else:
          fidPairs = endPointsMarkupsNode.GetNumberOfFiducials()/2 
          probeNodeIDs = duplicateProbeNode(int(fidPairs),probeNode)
      self.probeNodeIDs = probeNodeIDs
      print("New probe IDs probes: ", self.probeNodeIDs)

      for i in range(0, endPointsMarkupsNode.GetNumberOfFiducials()):
        endPointsMarkupsNode.GetNthFiducialPosition(i, xyz[i])
        self.endPoints_positions.append(xyz) #.GetNthFiducialPosition(0, [1,1,1])
        #print("At positon: ", i, " found position: ", xyz[i])
        self.endPoints_positions = xyz
        
      #self.endPoints_positions = point_list
      for i in range(0, len(self.probeNodeIDs)):
        self.logic.updateProbePosition(self.probeNodeIDs[i], probeNode, [0,0,0], [0,0,-1], self.endPoints_positions[i*2], self.endPoints_positions[i*2+1])
        #logging.info("Moving probe {0} from {1} , {2} to position {3} , {4}".format(self.probeNodeIDs[i], [0,0,0],[0,0,-1], self.endPoints_positions[i*2], self.endPoints_positions[i*2+1]))

      #endPointsMarkupsNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointStartInteractionEvent, self.onMarkupStartInteraction)
      if self.fromDrag:
        #endPointsMarkupsNode.removeObservers()
        thisScene = probeNode.GetScene()
        markupReference = thisScene.GetNodeByID(self.formerMarkupID)
        endPointsMarkupsNode.RemoveObserver(self.observerID)
        self.removeObservers()
      self.observerID = endPointsMarkupsNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self.onMarkupEndInteraction)
      self.formerMarkupID = endPointsMarkupsNode.GetID()


  def onMarkupEndInteraction(self, caller, event):
    markupsNode = caller
    self.fromDrag = True
    thisScene = markupsNode.GetScene()
    existingMovedProbes = self.probeNodeIDs
    for probeID in existingMovedProbes:
      probeReference = thisScene.GetNodeByID(probeID)
      slicer.mrmlScene.RemoveNode(probeReference)
      print("Deleted: ", probeID)

    self.onProbeButton()




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


    #convertSegmentsToSegment(probeNode, nodeIds)
  def updateProbePosition(self, probeNodeID, probeNode, xyz1, xyz2, xyz3, xyz4):
     #print("Updating probe position!")
     #print(xyz1, " ", xyz2, " ", xyz3, " ", xyz4)
     

     fiducialDistance1 = (((abs(xyz2[0]-xyz1[0])) ** 2) + (abs(xyz2[1]-xyz1[1]) ** 2) + (abs(xyz2[2]-xyz1[2]) ** 2)) ** 0.5
     vector1 = [xyz2[0]-xyz1[0], xyz2[1]-xyz1[1], xyz2[2]- xyz1[2]]
     unitVector1 = [vector1[0]/fiducialDistance1, vector1[1]/fiducialDistance1, vector1[2]/fiducialDistance1]

     fiducialDistance2 = (((abs(xyz4[0]-xyz3[0])) ** 2) + (abs(xyz4[1]-xyz3[1]) ** 2) + (abs(xyz4[2]-xyz3[2]) ** 2)) ** 0.5
     vector2 = [xyz4[0]-xyz3[0], xyz4[1]-xyz3[1], xyz4[2]- xyz3[2]]
     unitVector2 = [vector2[0]/fiducialDistance2, vector2[1]/fiducialDistance2, vector2[2]/fiducialDistance2]

     rigidRegistrationMatrix = rotationMatrixFromVectors(unitVector1, unitVector2)
     slicer.app.processEvents()  # force update
     
     thisScene = probeNode.GetScene()
     probeReference = thisScene.GetNodeByID(probeNodeID)

     applyTransformToProbe(rigidRegistrationMatrix, probeReference, xyz3)



  def evaluateMargins(self, probeNode, tumorNode):
    modelNode1 = convertSegmentToModel(tumorNode)
    modelNode2 = convertSegmentToModel(probeNode)
    outputNode = findModelToModelDistance(modelNode1,modelNode2)
    VTKFieldData = outputNode.GetMesh().GetAttributesAsFieldData(0)

    resultTableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "surface_distances")
    
    for j in range(0,VTKFieldData.GetNumberOfArrays()):
        resultTableNode.AddColumn(VTKFieldData.GetArray(j))

    tumorDisplayNode = tumorNode.GetDisplayNode()
    #tumorDisplayNode.SetVisibility(False) # Hide all points
    tumorDisplayNode.SetOpacity(0.05)
    probeDisplayNode = probeNode.GetDisplayNode()
    #probeDisplayNode.SetVisibility(False)
    probeDisplayNode.SetOpacity(0.05)
    thisDisplayNode = modelNode2.GetDisplayNode()
    thisDisplayNode.SetVisibility(False)

    distanceRange = VTKFieldData.GetArray("Signed").GetRange()
    signedVals = []
    for i in range(0,VTKFieldData.GetArray('Signed').GetSize()-1):
        signedVals.append(VTKFieldData.GetArray('Signed').GetValue(i)) #value

    print("Evaluated model to model distance, found range: ", distanceRange)
    print("Mean: ", np.mean(signedVals))
    print("Median: ", np.median(signedVals))
    print("80th percentile: ", np.quantile(signedVals, 0.8))
    print("20th percentile: ", np.quantile(signedVals, 0.2))

    return outputNode, resultTableNode, distanceRange[0], signedVals #, array


  def updateNodeColor(self, node):
    thisDisplayNode = node.GetDisplayNode()
    thisDisplayNode.SetVisibility(False) # Hide all points
    thisDisplayNode.SetVisibility(True)

  def changeColorsByMargin(self, modelNode, low, med, high):

    VTKFieldData = modelNode.GetMesh().GetAttributesAsFieldData(0)
    VTKFieldDataArray = VTKFieldData.GetArray("Signed")

    for i in range(0,VTKFieldDataArray.GetSize()-1):
        colorval = VTKFieldDataArray.GetValue(i)
        if (colorval > high):
            VTKFieldDataArray.SetValue(i,high)
        elif (colorval > med):
            VTKFieldDataArray.SetValue(i,med)
        else:
            VTKFieldDataArray.SetValue(i,low)

  def regenerateOriginalModelColors(self, modelNode, originalColorArray):

    VTKFieldData = modelNode.GetMesh().GetAttributesAsFieldData(0)
    VTKFieldDataArray = VTKFieldData.GetArray("Signed")

    for i in range(0, len(originalColorArray)-1):
        loopArray = originalColorArray[i]
        colorval = loopArray[0]
        VTKFieldDataArray.SetValue(i,colorval)


        
  def convertSegmentsToSegment(self, probeNode, nodeIds):
    thisScene = probeNode.GetScene()

    
    #probeNode.GetSegmentation().CreateRepresentation("Binary labelmap") #added 2/22
    #probeNode.GetSegmentation().SetMasterRepresentationName("Binary labelmap") #added 2/22


    if len(nodeIds)>0:
        print("Found multiple probe nodes, combining them into a single segment!: ", nodeIds)

    segmentationNode = slicer.vtkMRMLSegmentationNode()
    slicer.mrmlScene.AddNode(segmentationNode)
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display

    slicer.app.processEvents() 

    for probeNodeID in nodeIds:
        duplicateProbeNode = thisScene.GetNodeByID(probeNodeID)
        #duplicateProbeNode.GetSegmentation().SetMasterRepresentationName("Binary labelmap") #ADDED 2/22
        segmentType = duplicateProbeNode.GetSegmentation().GetMasterRepresentationName()
        slicer.app.processEvents() 
        if (segmentType == "Closed surface"):
            mergedImage = vtk.vtkPolyData()
            duplicateProbeNode.GetClosedSurfaceRepresentation(duplicateProbeNode.GetSegmentation().GetNthSegmentID(0), mergedImage)
            segmentationNode.AddSegmentFromClosedSurfaceRepresentation(mergedImage,probeNodeID,[0,1,0])
        else:
            labelmapImage = vtkSegmentationCore.vtkOrientedImageData()
            duplicateProbeNode.GetBinaryLabelmapRepresentation(duplicateProbeNode.GetSegmentation().GetNthSegmentID(0),labelmapImage)
            segmentationNode.AddSegmentFromBinaryLabelmapRepresentation(labelmapImage,probeNodeID,[1,0,0])
            duplicateProbeNode.GetSegmentation().CreateRepresentation("Closed Surface")
            #segmentationNode.GetSegmentation().CreateRepresentation("Closed surface")
            #segmentationNode.GetSegmentation().SetMasterRepresentationName("Closed surface")
        #slicer.mrmlScene.RemoveNode(duplicateProbeNode)

    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)


    for i in range(1, segmentationNode.GetSegmentation().GetNumberOfSegments()+1):  #TWO ADDITIONAL PROBES
        segmentEditorWidget.setActiveEffectByName("Logical operators")
        effect = segmentEditorWidget.activeEffect()
        effect.self().scriptedEffect.setParameter("Operation","UNION")
        effect.self().scriptedEffect.setParameter("ModifierSegmentID",segmentationNode.GetSegmentation().GetNthSegmentID(i))
        effect.self().onApply()
        #segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(i))

    #for i in range(1, segmentationNode.GetSegmentation().GetNumberOfSegments()):  #TWO ADDITIONAL PROBES
    #    segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(i))

    segDisplayNode = segmentationNode.GetDisplayNode()
    segDisplayNode.SetOpacity(0.3)

    segmentationNode.GetSegmentation().CreateRepresentation("Closed surface")
    segmentationNode.GetSegmentation().SetMasterRepresentationName("Closed surface")
    
    segNum = segmentationNode.GetSegmentation().GetNumberOfSegments()
    for i in range(0,segNum):
      segmentationNode.GetSegmentation().RemoveSegment(segmentationNode.GetSegmentation().GetNthSegmentID(1))

    return segmentationNode


def applyTransformToProbe(rm, probeNode, xyz1):
    transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
  
    transformMatrixNP = np.array(
    [[rm[0,0],rm[0,1],rm[0,2], xyz1[0]],
    [rm[1,0],rm[1,1],rm[1,2], xyz1[1]],
    [rm[2,0],rm[2,1],rm[2,2], xyz1[2]],
    [0,0,0,1]])

    #print(transformMatrixNP)

    transformNode.SetMatrixTransformToParent(slicer.util.vtkMatrixFromArray(transformMatrixNP))
    
    slicer.app.processEvents()  
    time.sleep(0.05)
    probeNode.SetAndObserveTransformNodeID(transformNode.GetID())
    slicer.app.processEvents()  #harden transform would often cause slicer to crash before slowing the program down. 
    time.sleep(0.05)
    probeNode.HardenTransform()
    time.sleep(0.05)
    slicer.app.processEvents()
    slicer.mrmlScene.RemoveNode(transformNode)




def rotationMatrixFromVectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    print(vec1, " ", vec2)
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)

    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotationMatrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotationMatrix

def duplicateProbeNode(fidPairs, probeNode):
    #print("Copying: ", probeNode)
    numDuplicates = int(fidPairs)
    nodeIds = []
    #nodeIds.append(probeNode.GetID())
    if (numDuplicates > 0):
        for i in range(0,numDuplicates):
            
            mergedImage = vtk.vtkPolyData()
            probeNode.GetClosedSurfaceRepresentation(probeNode.GetSegmentation().GetNthSegmentID(0), mergedImage)
            
            segmentationNode = slicer.vtkMRMLSegmentationNode()
            slicer.mrmlScene.AddNode(segmentationNode)
            
            slicer.app.processEvents()  #force update as occasionally the follow steps cause slicer to crash
            time.sleep(0.1)

            segmentationNode.CreateDefaultDisplayNodes() # only needed for display
            segmentationNode.AddSegmentFromClosedSurfaceRepresentation(mergedImage,"duplicate_node",[0,1,0])
            segmentationNode.GetSegmentation().CreateRepresentation("Closed surface")
            segmentationNode.GetSegmentation().SetMasterRepresentationName("Binary labelmap")

            segDisplayNode = probeNode.GetDisplayNode()
            segDisplayNode.SetOpacity(0.3)
            segDisplayNode = segmentationNode.GetDisplayNode()
            segDisplayNode.SetOpacity(0.3)

            slicer.app.processEvents() 
            time.sleep(0.1)

            nodeIds.append(segmentationNode.GetID()) #CHANGED THIS
            seg_name = probeNode.GetName()
            new_seg_name = seg_name + "_" + str(i)
            segmentationNode.SetName(new_seg_name)

    #probeNode.GetSegmentation().CreateRepresentation("Binary labelmap")
    #probeNode.GetSegmentation().SetMasterRepresentationName("Binary labelmap")
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
    parameters['distanceType'] = "signed_closest_point"
    parameters["vtkOutput"] = vtkOutput

    cliNode = slicer.cli.runSync(slicer.modules.modeltomodeldistance, None, parameters)
    return vtkOutput

    
      



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

   
    self.delayDisplay('Loaded test data set')



    self.delayDisplay('Test passed')
